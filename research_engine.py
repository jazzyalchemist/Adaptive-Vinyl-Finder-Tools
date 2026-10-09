#!/usr/bin/env python3
"""Audit, route, and batch catalog research without pretending it is verification."""
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path
import re
import urllib.parse as up
import vinyl_suite as v

ROOT=Path(__file__).resolve().parent
VALID_OVERLAP={'multiple major genres'}
BLOCKERS={'artist/title missing','catalog number missing','format missing','zero/nonpositive price','availability unknown','duplicate listing ID'}

def text_key(value):
    # Remove Discogs disambiguation suffix for grouping, but never treat it as resolved identity.
    return re.sub(r'\s*\(\d+\)\s*$','',str(value or '')).strip().casefold()

def stable_key(p):
    source=p.get('source') or ('https://'+up.urlsplit(p.get('url','')).netloc if up.urlsplit(p.get('url','')).hostname else 'unknown-source')
    return str(source).rstrip('/')+'|'+str(p.get('id') or p.get('url') or '')

def fingerprint(p):
    fields=['artist','title','name','price','currency','available','genre','styles','label','cat','country','released','format','media','sleeve','comments','tracklist','variant_id']
    return hashlib.sha256(json.dumps({k:p.get(k) for k in fields},sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def affordability(price):
    n=v.number(price)
    if n is None or n<=0:return None
    return 5 if n<=5 else 4 if n<=10 else 3 if n<=20 else 2 if n<=35 else 1

def normalize_ledger(pack):
    rows=[];seen=collections.Counter(stable_key(p) for p in pack['products'])
    for source in pack['products']:
        p=dict(source); p['listing_key']=stable_key(p)
        p['source']=p.get('source') or 'https://'+up.urlsplit(p.get('url','')).netloc
        if not p.get('currency') and p.get('price_usd_snapshot'):p['currency']='USD';p['currency_basis']='Prior report explicitly denominated snapshot in USD'
        original=[s.strip() for s in str(p.get('quality_flags','')).split(';') if s.strip()]
        annotations=[s for s in original if s in VALID_OVERLAP]
        issues=[s for s in original if s not in VALID_OVERLAP]
        for condition,flag in [(not p.get('artist') or not p.get('title'),'artist/title missing'),(not p.get('cat'),'catalog number missing'),(not p.get('format'),'format missing'),(p.get('price') is None or p['price']<=0,'zero/nonpositive price'),(p.get('available') is None,'availability unknown'),(seen[p['listing_key']]>1,'duplicate listing ID')]:
            if condition and flag not in issues:issues.append(flag)
        p.update(genre_annotations=annotations,data_issues=issues,source_snapshot_at=p.get('checked_at') or p.get('snapshot') or pack.get('checked_at') or pack.get('snapshot_date'),
                 source_check_claim=p.get('live_checked_at') or None,stock_verification='seller_snapshot_only',
                 metadata_fingerprint=fingerprint(p),research_stage='editorial_lead' if str(p.get('editorial_status','')).startswith('Batch') else 'mechanically_screened')
        p['legacy_scores']={k:p.get(k) for k in ['L','G','I','R','V','Q','U','C','A']}
        p['scores']={k:None for k in ['L','G','C','A','I','R','V','Q','U']}
        p['scores']['C']=v.grade_score(p.get('media')) or None
        p['scores']['A']=affordability(p.get('price')) if p.get('currency')=='USD' else None
        p['assessment_note']='Prior editorial scores preserved separately; no unbound recipient or unsourced market score promoted.'
        rows.append(p)
    return rows

def tier_candidates(rows,profile,per_tier=12):
    result=[];used=set()
    for tier in profile['tiers']:
        candidates=[]
        for p in rows:
            if p.get('available') is not True or p.get('price') is None or p['price']<=0 or any(x in BLOCKERS for x in p['data_issues']):continue
            if p['listing_key'] in used:continue
            styles=[x.strip() for x in str(p.get('styles','')).split(',')];hits=[pat for pat in tier['style_patterns'] if any(re.search(pat,style,re.I) for style in styles)]
            artist=text_key(p.get('artist'));artist_hit=artist in [text_key(x) for x in tier.get('artist_examples',[])]
            label_hit=any(re.search(pat,str(p.get('label','')),re.I) for pat in tier.get('label_patterns',[]))
            if not (hits or artist_hit or label_hit):continue
            priority=(6 if artist_hit else 0)+(4 if label_hit else 0)+min(3,len(hits))+v.grade_score(p.get('media'))+((affordability(p.get('price')) or 0) if p.get('currency')=='USD' else 0)
            candidates.append((priority,p,{'style_rule_matches':hits,'artist_example_match':artist_hit,'label_rule_match':label_hit}))
        candidates.sort(key=lambda x:(-x[0],str(x[1].get('artist')),str(x[1].get('title')),x[1]['listing_key']))
        selected=[];artists=collections.Counter()
        for priority,p,basis in candidates:
            a=text_key(p.get('artist'))
            if artists[a]>=profile.get('max_per_artist',2):continue
            selected.append({'listing_key':p['listing_key'],'id':p.get('id'),'artist':p.get('artist'),'title':p.get('title'),'price':p['price'],'currency':p.get('currency'),'media':p.get('media'),'sleeve':p.get('sleeve'),'url':p.get('url'),'source_snapshot_at':p['source_snapshot_at'],
                             'routing_basis':basis,'queue_priority':priority,'status':'metadata_candidate_not_a_buy_recommendation','next_action':'Audition and verify exact edition/current stock before recommending.'})
            used.add(p['listing_key']);artists[a]+=1
            if len(selected)>=per_tier:break
        result.append({'tier':tier['id'],'name':tier['name'],'connection':tier['connection'],'difference':tier['difference'],
                       'target_releases':per_tier,'eligible_before_diversification':len(candidates),'selected':selected,'unfilled_slots':max(0,per_tier-len(selected))})
    return result

def audit_catalog(pack,profile,per_tier=12,previous=None):
    rows=normalize_ledger(pack);previous_map={p['listing_key']:p for p in (previous or {}).get('products',[])}
    changes=collections.Counter();issues=collections.Counter();annotations=collections.Counter();genres=collections.Counter()
    for p in rows:
        old=previous_map.get(p['listing_key']);change='new' if not old else 'unchanged' if old.get('metadata_fingerprint')==p['metadata_fingerprint'] else 'changed'
        p['metadata_change']=change;changes[change]+=1
        if old and change=='unchanged':
            # Carry analyst evidence only when it actually exists. A stage is never verification by itself.
            p['cached_assessments']=old.get('cached_assessments',[])
        issues.update(p['data_issues']);annotations.update(p['genre_annotations'])
        # Preserve an existing named taxonomy; changing classifiers does not improve the underlying data.
        declared=[x.strip() for x in str(p.get('major_categories','')).split(';') if x.strip()]
        genres.update(declared or v.categories(p))
    tiers=tier_candidates(rows,profile,per_tier)
    issue_rows=[p for p in rows if p['data_issues']]
    issue_rows.sort(key=lambda p:(-sum(x in BLOCKERS for x in p['data_issues']),-int(p['research_stage']=='editorial_lead'),p['listing_key']))
    return {'schema_version':2,'engine_version':'2.1.0','created_at':v.now(),'source':pack.get('source'),'source_checked_at':pack.get('checked_at'),
            'coverage':pack.get('coverage',{}),'profile_basis':profile.get('basis'),'profile_hash':hashlib.sha256(json.dumps(profile,sort_keys=True).encode()).hexdigest(),
            'summary':{'rows':len(rows),'unique_listing_keys':len({p['listing_key'] for p in rows}),'editorial_leads':sum(p['research_stage']=='editorial_lead' for p in rows),
             'snapshot_available':sum(p.get('available') is True for p in rows),'data_issue_rows':len(issue_rows),'annotation_only_rows':sum(bool(p['genre_annotations']) and not p['data_issues'] for p in rows),
             'issue_counts':dict(issues),'annotation_counts':dict(annotations),'overlapping_genre_counts':dict(genres),'metadata_changes':dict(changes),
             'retired_since_prior_snapshot':len(set(previous_map)-{p['listing_key'] for p in rows}),
             'verification_scope':'Only source observations and mechanical screening; this engine does not listen, browse, or verify sales.'},
            'exploration_tiers':tiers,'issue_queue_keys':[p['listing_key'] for p in issue_rows],'products':rows}

def write_outputs(report,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);v.atomic(out/'research-ledger.json',report)
    fields=['listing_key','id','artist','title','price','currency','available','media','sleeve','source_snapshot_at','stock_verification','research_stage','metadata_change','data_issues','genre_annotations','C','A','L','G','I','R','V','Q','U','url']
    def write(name,rows):
        with (out/name).open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader()
            for p in rows:
                row={**p,**p['scores']}
                safe={k:json.dumps(row.get(k),ensure_ascii=False) if isinstance(row.get(k),(list,dict)) else row.get(k) for k in fields}
                for k,val in safe.items():
                    if isinstance(val,str) and val.lstrip().startswith(('=','+','-','@')):safe[k]="'"+val
                w.writerow(safe)
    write('coverage-ledger.csv',report['products']);keys=set(report['issue_queue_keys']);write('data-issues.csv',[p for p in report['products'] if p['listing_key'] in keys])
    v.atomic(out/'exploration-candidates.json',{'profile_basis':report['profile_basis'],'tiers':report['exploration_tiers']})
    v.atomic(out/'audit-summary.json',report['summary'])

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--catalog',required=True);parser.add_argument('--profile',default=str(ROOT/'templates/discovery-profile.json'));parser.add_argument('--previous');parser.add_argument('--per-tier',type=int,default=12);parser.add_argument('--out',default='private/research')
    a=parser.parse_args()
    if not 1<=a.per_tier<=100:parser.error('--per-tier must be 1–100')
    report=audit_catalog(v.load_catalog(a.catalog),v.read_json(a.profile),a.per_tier,v.read_json(a.previous) if a.previous else None)
    write_outputs(report,a.out);print(json.dumps(report['summary'],indent=2))

if __name__=='__main__':main()
