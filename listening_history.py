#!/usr/bin/env python3
"""Summarize Spotify Extended Streaming History without exposing IP/device data."""
import argparse
import collections
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo
import vinyl_suite as v

def parse_time(value):
    stamp=dt.datetime.fromisoformat(str(value).replace('Z','+00:00'))
    if stamp.tzinfo is None:raise ValueError('Timestamp must have a timezone')
    return stamp.astimezone(dt.timezone.utc)

def summarize(paths,start,through,timezone='UTC',min_ms=30000,genre_map=None):
    tz=ZoneInfo(timezone);begin=dt.datetime.combine(dt.date.fromisoformat(start),dt.time.min,tzinfo=tz)
    end=dt.datetime.combine(dt.date.fromisoformat(through)+dt.timedelta(days=1),dt.time.min,tzinfo=tz)
    if end<=begin:raise ValueError('End date precedes start date')
    if min_ms<0:raise ValueError('Meaningful-play threshold must be nonnegative')
    tracks={};artists={};monthly=collections.Counter();excluded=collections.Counter();seen=set();input_rows=0;first=None;last=None;source_files=[]
    for path in paths:
        data=v.read_json(path)
        if not isinstance(data,list):raise ValueError('History files must contain event arrays')
        source_files.append({'name':Path(path).name,'sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),'rows':len(data)})
        for e in data:
            input_rows+=1
            if not isinstance(e,dict):excluded['invalid_row']+=1;continue
            if 'ts' not in e or 'ms_played' not in e:excluded['unsupported_basic_history_schema']+=1;continue
            title=e.get('master_metadata_track_name');artist=e.get('master_metadata_album_artist_name')
            if not title or not artist:excluded['non_music_or_missing_music_metadata']+=1;continue
            ms=v.number(e.get('ms_played'))
            if ms is None or ms<0:excluded['invalid_duration']+=1;continue
            try:stamp=parse_time(e['ts'])
            except (ValueError,TypeError):excluded['invalid_timestamp']+=1;continue
            if not begin<=stamp<end:excluded['outside_requested_window']+=1;continue
            uri=e.get('spotify_track_uri') or 'local:'+hashlib.sha256((artist+'|'+title).encode()).hexdigest()[:20]
            signature=(stamp.isoformat(),uri,ms,e.get('reason_start'),e.get('reason_end'),e.get('platform'))
            if signature in seen:excluded['duplicate_event']+=1;continue
            seen.add(signature);first=min(first,stamp) if first else stamp;last=max(last,stamp) if last else stamp
            t=tracks.setdefault(uri,{'uri':uri,'artist':artist,'title':title,'album':e.get('master_metadata_album_album_name'),'recorded_events':0,'meaningful_events':0,'ms_played':0,'skipped_events':0,'first_seen':stamp.isoformat(),'last_seen':stamp.isoformat()})
            t['recorded_events']+=1;t['meaningful_events']+=int(ms>=min_ms);t['ms_played']+=ms;t['skipped_events']+=int(e.get('skipped') is True)
            t['first_seen']=min(t['first_seen'],stamp.isoformat());t['last_seen']=max(t['last_seen'],stamp.isoformat())
            a=artists.setdefault(artist,{'artist':artist,'recorded_events':0,'meaningful_events':0,'ms_played':0})
            a['recorded_events']+=1;a['meaningful_events']+=int(ms>=min_ms);a['ms_played']+=ms
            monthly[stamp.astimezone(tz).strftime('%Y-%m')]+=ms
    ranked=sorted(tracks.values(),key=lambda x:(-x['ms_played'],-x['meaningful_events'],x['uri']))
    ranked_artists=sorted(artists.values(),key=lambda x:(-x['ms_played'],x['artist']))
    for rows in [ranked,ranked_artists]:
        for row in rows:row['listening_minutes']=round(row['ms_played']/60000,3)
    mapping=genre_map or {};genres=collections.Counter();classified_ms=0;total_ms=sum(t['ms_played'] for t in ranked)
    for t in ranked:
        meta=mapping.get(t['uri']) or mapping.get('artist:'+t['artist'])
        if not meta or not meta.get('genres') or not meta.get('source'):continue
        if not isinstance(meta['genres'],list) or not all(isinstance(x,str) and x for x in meta['genres']):raise ValueError('Genre mapping needs a nonempty list of genre strings')
        # Fractional allocation prevents a multi-tagged track from inflating total measured minutes.
        tags=sorted(set(meta['genres']));classified_ms+=t['ms_played']
        for tag in tags:genres[tag]+=t['ms_played']/len(tags)
        t['genre_mapping']=dict(meta,classification_level=meta.get('classification_level') or ('artist_proxy' if 'artist:'+t['artist'] in mapping and t['uri'] not in mapping else 'track_manual'))
    if input_rows and excluded['unsupported_basic_history_schema']==input_rows:raise ValueError('Use Extended Streaming History, not basic one-year history')
    return {'schema_version':1,'created_at':v.now(),'requested_window':{'from':start,'through':through,'timezone':timezone},
            'coverage':{'input_rows':input_rows,'included_unique_music_events':len(seen),'unique_tracks':len(ranked),'unique_artists':len(ranked_artists),
             'observed_first_event':first.isoformat() if first else None,'observed_last_event':last.isoformat() if last else None,'excluded':dict(excluded),
             'completeness':'Unknown: file/event coverage is reported; event gaps do not prove inactivity or missing data.'},
            'method':{'rank_by':'Total observed listening milliseconds; meaningful-event counts shown separately','meaningful_event_min_ms':min_ms,'warning':'Counts are export events, not official Spotify play counts. Skipping is not automatically dislike. No audio inference or ML training.',
             'genre_method':'Optional source-backed track mapping or clearly marked artist proxy, with fractional allocation for overlapping genres'},
            'total_listening_minutes':round(total_ms/60000,3),'genre_coverage_fraction':classified_ms/total_ms if total_ms else None,
            'genre_listening_minutes_fractional':{k:round(ms/60000,3) for k,ms in genres.items()},'unmapped_listening_minutes':round((total_ms-classified_ms)/60000,3),
            'monthly_listening_minutes':{k:round(ms/60000,3) for k,ms in sorted(monthly.items())},'source_files':source_files,'tracks':ranked,'artists':ranked_artists}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',nargs='+',required=True);p.add_argument('--from',dest='start',required=True);p.add_argument('--through',required=True);p.add_argument('--timezone',default='UTC');p.add_argument('--min-ms',type=int,default=30000);p.add_argument('--genre-map');p.add_argument('--out',default='private/listening')
    a=p.parse_args();paths=[]
    for name in a.input:
        path=Path(name)
        paths+=sorted(path.glob('*.json')) if path.is_dir() else [path]
    if not paths:raise ValueError('No history files found')
    result=summarize(paths,a.start,a.through,a.timezone,a.min_ms,v.read_json(a.genre_map) if a.genre_map else None)
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True);v.atomic(out/'listening-profile.json',result)
    for name,rows,fields in [('top-tracks.csv',result['tracks'],['uri','artist','title','album','recorded_events','meaningful_events','listening_minutes','skipped_events','first_seen','last_seen']),('top-artists.csv',result['artists'],['artist','recorded_events','meaningful_events','listening_minutes'])]:
        with (out/name).open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader()
            for row in rows:
                safe={k:row.get(k) for k in fields}
                for k,value in safe.items():
                    if isinstance(value,str) and value.lstrip().startswith(('=','+','-','@')):safe[k]="'"+value
                w.writerow(safe)
    print(json.dumps(result['coverage'],indent=2))

if __name__=='__main__':main()
