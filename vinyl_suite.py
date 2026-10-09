#!/usr/bin/env python3
"""Adaptive Vinyl Finder 2.1 — portable, standard-library research tools."""
import argparse
import contextlib
import csv
import datetime as dt
import hashlib
import html
import json
import os
from pathlib import Path
import re
import tempfile
import time
import urllib.error
import urllib.parse as up
import urllib.request as ur
import uuid
import xml.etree.ElementTree as ET

VERSION = '2.1.0'
FIELDS = ['id','variant_id','artist','title','name','price','currency','available','genre','styles','label','cat','country','released','format','media','sleeve','comments','tracklist','url','checked_at','source','flags']
KEYS = ['ARTIST','TITLE','LABEL','CAT','TYPE','FORMAT','COUNTRY','RELEASED','GENRE','STYLES','MEDIA','SLEEVE','TRACKLIST','COMMENTS']
GENRES = {
 'Electronic': 'electronic|house|techno|trance|ambient|downtempo|dubstep|drum & bass|jungle|idm|electro|breakbeat',
 'Jazz': 'jazz|bebop|fusion|free improvisation', 'Rock': r'rock|\bprog\b|psychedelic|punk|grunge',
 'Metal': 'metal|doom|thrash|black metal|death metal', 'Hip-hop': 'hip.hop|rap|boom bap',
 'Soul / R&B / Funk': 'soul|r&b|funk|rhythm & blues|neo.soul', 'Pop': 'pop|synthpop',
 'Country': 'country|bluegrass|honky.tonk', 'Folk / Americana': 'folk|americana|singer.songwriter',
 'Blues': 'blues', 'Reggae / Dub / Ska': 'reggae|dub(?!step)|ska|dancehall',
 'Classical': 'classical|baroque|orchestral|opera|chamber', 'Gospel / Christian': 'gospel|christian|praise|worship',
 'World / International': 'world|afrobeat|highlife|soukous|latin|salsa|bossa|cumbia|raga|gamelan|flamenco',
 'Soundtracks / Library': 'soundtrack|library|score|stage & screen',
 'Odd / Experimental': 'experimental|avant.garde|noise|concr.te|field recording|spoken|outsider|sound collage|free improvisation'}
STYLES = {
 'ambient / drone': ['quiet','immersive','spacious','meditative','slow','minimal'],
 'downtempo / trip-hop': ['warm','cinematic','reflective','slow','groove','melancholy'],
 'trance / progressive': ['euphoric','uplifting','journey','emotional','energetic'],
 'deep / melodic house': ['warm','groove','journey','uplifting','dance'],
 'IDM / electro / experimental bass': ['strange','exploratory','textural','complex','futuristic'],
 'drum & bass / jungle': ['energetic','kinetic','complex','dance'],
 'spiritual / modal jazz': ['immersive','organic','meditative','journey','spacious'],
 'jazz fusion / progressive rock': ['complex','energetic','musicianship','journey'],
 'soul / funk / disco': ['warm','groove','joyful','organic','dance'],
 'folk / singer-songwriter': ['intimate','organic','reflective','lyrics'],
 'country / Americana': ['story','organic','lyrics','warm'],
 'blues': ['raw','organic','emotional','groove'],
 'reggae / dub': ['spacious','groove','warm','textural'],
 'classical / minimalism': ['complex','spacious','meditative','journey'],
 'metal / noise / free improvisation': ['intense','raw','strange','complex','cathartic'],
 'pop / R&B': ['melodic','intimate','joyful','lyrics'],
 'world / regional traditions': ['exploratory','organic','rhythm','dance'],
 'soundtracks / library music': ['cinematic','journey','textural','exploratory']}

def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def uid(): return uuid.uuid4().hex[:12]
def read_json(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def atomic(path, data):
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=p.parent, delete=False) as f:
        tmp = f.name; json.dump(data, f, ensure_ascii=False, indent=2); f.write('\n')
    try: os.replace(tmp, p)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def https(url):
    u = up.urlsplit(url)
    if u.scheme != 'https' or not u.hostname or u.username or u.password:
        raise ValueError('Use an HTTPS URL without embedded credentials')
    return url

class HTTPSOnly(ur.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        https(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def fetch(url, retries=2, max_bytes=20_000_000):
    https(url)
    for attempt in range(retries+1):
        try:
            req = ur.Request(url, headers={'User-Agent':'AdaptiveVinylFinder/2.0 public read-only catalog research'})
            with ur.build_opener(HTTPSOnly()).open(req, timeout=30) as r:
                body = r.read(max_bytes+1)
                if len(body)>max_bytes: raise ValueError('Response exceeds size limit; use a seller export')
                return body
        except (urllib.error.URLError, TimeoutError) as e:
            retry = not isinstance(e, urllib.error.HTTPError) or e.code in (429,500,502,503,504)
            if not retry or attempt == retries: raise
            delay = min(30, 2**attempt)
            if isinstance(e, urllib.error.HTTPError):
                try: delay = min(30, max(delay, int(e.headers.get('Retry-After','0'))))
                except ValueError: pass
            time.sleep(delay)

def truth(v):
    if v is True or str(v).lower() == 'true': return True
    if v is False or str(v).lower() == 'false': return False
    return None
def number(v):
    try:
        n = float(v)
        return n if n == n and abs(n) != float('inf') else None
    except (ValueError, TypeError): return None
def grade_score(value):
    codes=re.findall(r'(?<![A-Z])(?:NM|M-|VG\+|VG|G\+|M|G|F|P)(?![A-Z])',str(value or '').upper())
    grades={'M':5,'NM':5,'M-':5,'VG+':4,'VG':3,'G+':2,'G':1,'F':1,'P':1}
    return grades.get(codes[0],0) if codes else 0
def normalize(p, base, currency=None, checked=None):
    s = html.unescape(re.sub('<[^>]*>', ' ', p.get('body_html') or ''))
    s = re.sub(r'\s+', ' ', s); d = {}
    for k in KEYS:
        m = re.search(r'\b'+k+r':\s*(.*?)(?=\b(?:'+'|'.join(KEYS)+r'):|$)', s)
        d[k.lower()] = m.group(1).strip() if m else ''
    vs = p.get('variants') or []
    v = next((v for v in vs if truth(v.get('available')) is True), vs[0] if vs else {})
    stock = [truth(v.get('available')) for v in vs]
    available = True if True in stock else False if stock and all(x is False for x in stock) else None
    price = number(v.get('price')); flags = []
    if available is None: flags.append('availability_unknown')
    if not price or price<0: flags.append('price_needs_verification')
    if len(vs)>1: flags.append('multiple_variants_verify_exact_copy')
    url = base.rstrip('/')+'/products/'+p.get('handle','')
    if v.get('id'): url += '?variant='+str(v['id'])
    d.update(id=str(p.get('id','')), variant_id=str(v.get('id','')), name=p.get('title',''), price=price,
             currency=currency, available=available, url=url, tags=p.get('tags',[]), flags=flags,
             checked_at=checked or now(), source=base, variants=vs, scores={}, evidence={})
    return d

def categories(p):
    tags = p.get('tags',[])
    s = ' '.join(str(p.get(k,'')) for k in ['genre','styles'])+' '+(' '.join(tags) if isinstance(tags,list) else str(tags))
    return [g for g, pattern in GENRES.items() if re.search(pattern, s, re.I)] or ['Unmapped / ambiguous']

def sitemap_urls(base, limit=100):
    """Read public product sitemaps only; no invented pagination bypass."""
    pending = [base+'/sitemap.xml']; seen = set(); products = set()
    while pending:
        if len(seen)>=limit: raise ValueError('Sitemap traversal cap reached')
        url = pending.pop(0)
        if url in seen: continue
        seen.add(url); root = ET.fromstring(fetch(url))
        locs = [x.text for x in root.iter() if x.tag.split('}')[-1]=='loc' and x.text]
        if root.tag.split('}')[-1]=='sitemapindex':
            pending += [u for u in locs if up.urlsplit(u).netloc == up.urlsplit(base).netloc and 'product' in u.lower() and u not in seen]
        else:
            products.update(u.split('?')[0] for u in locs if up.urlsplit(u).netloc == up.urlsplit(base).netloc and '/products/' in up.urlsplit(u).path)
    return sorted(products)

def scan(url, max_pages=100, pause=.3, currency=None, sitemap=False, max_products=5000):
    u = up.urlsplit(https(url)); base = 'https://'+u.netloc; seen = {}; errors=[]; flags=[]; pages=0; exhausted=False
    started=now()
    for page in range(1,max_pages+1):
        try:
            payload=json.loads(fetch(base+f'/products.json?limit=250&page={page}'))
            batch=payload['products']
            if not isinstance(batch,list): raise ValueError('products must be an array')
            new=0
            for p in batch:
                if not isinstance(p,dict) or not p.get('id'): raise ValueError('Product lacks stable ID')
                key=str(p['id'])
                if key not in seen: new+=1
                seen[key]=normalize(p,base,currency,now())
            pages+=1
            if batch and new == 0: flags.append('repeated_page'); break
            if len(batch)<250: exhausted=True; break
            time.sleep(pause)
        except (ValueError, KeyError, urllib.error.URLError, TimeoutError) as e:
            errors.append(f'Page {page}: {type(e).__name__}: {e}'); break
    sm = {'attempted':False,'listed':None,'fetched_missing':0,'complete':None}
    if sitemap:
        sm['attempted']=True
        try:
            urls=sitemap_urls(base); sm['listed']=len(urls)
            present={x['url'].split('?')[0] for x in seen.values()}
            missing=[x for x in urls if x not in present]; sm['complete']=len(missing)<=max_products
            if len(missing)>max_products: flags.append('sitemap_product_cap')
            for target in missing[:max_products]:
                try:
                    p=json.loads(fetch(target+'.json'))['product']
                    seen[str(p['id'])]=normalize(p,base,currency,now()); sm['fetched_missing']+=1
                except (ValueError,KeyError,urllib.error.URLError,TimeoutError) as e:
                    errors.append(f'Sitemap product {target}: {type(e).__name__}: {e}'); sm['complete']=False
                time.sleep(pause)
            if not urls: sm['complete']=False; flags.append('empty_sitemap_not_proof_of_empty_catalog')
        except (ValueError,ET.ParseError,urllib.error.URLError,TimeoutError) as e:
            errors.append('Sitemap: '+str(e)); sm['complete']=False
    if not exhausted: flags.append('pagination_not_exhausted')
    complete=exhausted and not flags
    if sitemap: complete=complete and sm['complete'] is True
    products=list(seen.values())
    return {'schema_version':2,'source':base,'currency':currency,'started_at':started,'checked_at':now(),
            'coverage':{'retrieved':len(products),'available':sum(p['available'] is True for p in products),
             'sold_out':sum(p['available'] is False for p in products),'unknown_availability':sum(p['available'] is None for p in products),
             'pages':pages,'complete':complete,'scope':'Publicly exposed listings only; hidden/deleted/private inventory cannot be enumerated.',
             'pagination_exhausted':exhausted,'sitemap':sm,'errors':errors,'flags':flags},'products':products}

def load_catalog(path):
    p=Path(path)
    if p.suffix.lower()=='.csv':
        with p.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
        pack={'schema_version':2,'source':str(p),'checked_at':None,'coverage':{'complete':False,'note':'CSV alone does not prove full coverage'},'products':rows}
    else:
        raw=read_json(p)
        if isinstance(raw,list): pack={'products':raw,'coverage':{'complete':False},'checked_at':None}
        elif isinstance(raw,dict) and isinstance(raw.get('products'),list): pack=raw
        else: raise ValueError('Expected catalog object with products array, product array, or CSV')
    for row in pack['products']:
        if 'body_html' in row:
            observed=row.get('checked_at') or pack.get('checked_at')
            row.update(normalize(row,pack.get('source','https://unknown.invalid'),pack.get('currency'),observed))
            row['checked_at']=observed  # Offline import must never invent a fresh observation.
        row['available']=truth(row.get('available')); row['price']=number(row.get('price'))
        row.setdefault('currency',pack.get('currency')); row.setdefault('checked_at',pack.get('checked_at'))
        row.setdefault('flags',[])
    return pack

def export_catalog(pack, out):
    out=Path(out); out.mkdir(parents=True,exist_ok=True)
    atomic(out/'full-catalog.json', pack)
    groups={'active.csv':lambda p:p['available'] is True,'sold-out.csv':lambda p:p['available'] is False,'unknown-availability.csv':lambda p:p['available'] is None}
    counts={}
    for name,predicate in groups.items():
        rows=[p for p in pack['products'] if predicate(p)]; counts[name]=len(rows)
        with (out/name).open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=FIELDS,extrasaction='ignore'); w.writeheader()
            for row in rows:
                safe={k:json.dumps(row[k],ensure_ascii=False) if isinstance(row.get(k),(dict,list)) else row.get(k) for k in FIELDS}
                # Spreadsheet formula injection protection; JSON retains untouched text.
                for k,v in safe.items():
                    if isinstance(v,str) and v.lstrip().startswith(('=','+','-','@')): safe[k]="'"+v
                w.writerow(safe)
    atomic(out/'manifest.json',{'schema_version':2,'exported_at':now(),'source_checked_at':pack.get('checked_at'),
         'coverage':pack.get('coverage',{}),'counts':counts,'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.name in ['full-catalog.json',*groups]}})
    return counts

def blank_state():
    return {'schema_version':2,'revision':0,'updated_at':now(),'preferences':[], 'feedback':[], 'sessions':[],
            'collection':[],'assessments':[],'watchlist':[],'sites':[],'events':[]}
def state_read(path):
    s=read_json(path)
    if s.get('schema_version')!=2: raise ValueError('Unsupported state schema: migrate a copy; do not overwrite')
    if type(s.get('revision'))!=int or s['revision']<0: raise ValueError('Invalid state revision')
    for key in ['preferences','feedback','sessions','collection','assessments','watchlist','sites','events']:
        if not isinstance(s.get(key),list): raise ValueError('Invalid state list: '+key)
    return s

@contextlib.contextmanager
def edit_state(path, action):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True); lock=Path(str(p)+'.lock')
    try: fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    except FileExistsError: raise ValueError('State locked. Close the other process; remove stale .lock only after verifying it stopped.')
    os.write(fd,str(os.getpid()).encode()); os.close(fd)
    try:
        old=state_read(p); s=json.loads(json.dumps(old)); yield s
        backups=p.parent/(p.name+'.backups'); backups.mkdir(exist_ok=True)
        atomic(backups/(f"revision-{old['revision']}-{uid()}.json"),old)
        s['revision']=old['revision']+1; s['updated_at']=now()
        s['events'].append({'id':uid(),'at':now(),'action':action,'previous_revision':old['revision']})
        atomic(p,s)
    finally: lock.unlink(missing_ok=True)

def learned(s, subject='self'):
    scores={}
    for f in s['feedback']:
        if not f.get('active',True) or f.get('subject','self')!=subject: continue
        for tag in f['tags']:
            entry=scores.setdefault(tag,{'positive':0,'negative':0,'positive_mass':0,'negative_mass':0,'weight':0,'status':'hypothesis'})
            entry['positive' if f['rating']>0 else 'negative']+=1
            entry['positive_mass' if f['rating']>0 else 'negative_mass']+=.25 if f.get('stage')=='interested' else 1
    for v in scores.values():
        mass=v['positive_mass']+v['negative_mass']; v['weight']=round((v['positive_mass']-v['negative_mass'])/(mass+3),3)
        v['status']='provisional pattern' if mass>=3 else 'hypothesis'
    return scores

def memory_view(s):
    return {'revision':s['revision'],'confirmed_preferences':[p for p in s['preferences'] if p.get('active') and p.get('status')=='confirmed'],
            'other_preferences':[p for p in s['preferences'] if p.get('active') and p.get('status')!='confirmed'],
            'learned_hypotheses':learned(s),'counts':{k:len(s[k]) for k in ['feedback','collection','assessments','sessions','watchlist','sites']}}

def explore_plan(s,mood,experience,energy,lyrics,novelty):
    tokens=set(re.findall(r'[\w-]+',(mood+' '+experience).lower()))
    if energy=='low': tokens.add('slow')
    if energy=='high': tokens.add('energetic')
    if lyrics=='yes': tokens.add('lyrics')
    weights=learned(s)
    ranked=[]
    for style,hints in STYLES.items():
        hits=sorted(tokens.intersection(hints)); inferred=sum(v['weight'] for t,v in weights.items() if t in hints or t in style)
        ranked.append({'style':style,'session_matches':hits,'session_match_count':len(hits),
                       'learned_modifier':round(inferred,3),'basis':'Heuristic descriptors; listening fit requires audition. Not genre truth or a trained model.'})
    ranked.sort(key=lambda x:(x['session_match_count'],x['learned_modifier']),reverse=True)
    picked=ranked[:4]
    if novelty=='high':
        unseen=next((x for x in ranked[4:] if x['style'] not in {p['style'] for p in picked}),None)
        if unseen: picked.append(dict(unseen,role='wildcard; deliberately weak prior'))
    profile=read_json(Path(__file__).resolve().parent/'templates/discovery-profile.json')
    return {'id':uid(),'at':now(),'mood':mood,'experience':experience,'energy':energy,'lyrics':lyrics,'novelty':novelty,
            'shortlist':picked,'scope':'Session only; permanent preferences change only through explicit statements or feedback.',
            'exploration_tiers':[dict(t,target_releases=12) for t in profile['tiers']],
            'tier_policy':'At least 12 release leads per tier by default; report shortfalls rather than force unrelated stock. Metadata routes are provisional; actual history can customize the profile.',
            'confirmed_context':[p for p in s['preferences'] if p.get('active') and p.get('status')=='confirmed' and p.get('subject')=='self'],
            'queries':[f'"{p["style"]}" vinyl record label albums {experience}' for p in picked]}

def watch_match(w,p):
    if w.get('product_id') and str(p.get('id'))!=str(w['product_id']): return False
    if w.get('variant_id') and str(p.get('variant_id'))!=str(w['variant_id']): return False
    for key in ['artist','title','cat','label','format','released']:
        want=w.get(key)
        if not want: continue
        actual=str(p.get(key) or (p.get('name','') if key=='title' else ''))
        if key in ['artist','title']:
            if not all(re.search(r'\b'+re.escape(t)+r'\b',actual,re.I) for t in re.findall(r'\w+',want)): return False
        elif key=='format':
            if str(want).casefold().strip() not in {actual.casefold().strip(),str(p.get('type','')).casefold().strip()}: return False
        elif actual.casefold().strip()!=str(want).casefold().strip(): return False
    return True

def fresh_observation(stamp):
    try:
        return 0 <= (dt.datetime.now(dt.timezone.utc)-dt.datetime.fromisoformat(stamp.replace('Z','+00:00'))).total_seconds() <= 86400 if stamp else False
    except (ValueError,TypeError,AttributeError):
        return False

def evaluate_watch(s,packs):
    report={'checked_at':now(),'alerts':[],'results':[],'coverage':[{'source':p.get('source'),'checked_at':p.get('checked_at'),'coverage':p.get('coverage')} for p in packs]}
    for w in s['watchlist']:
        if not w.get('enabled'): continue
        matches=[]; current_qualified=[]; observed_keys=set(); observations={x['offer_key']:x for x in w.get('last_observations',[])}
        legacy_signatures=set(w.get('last_qualified',[])) if not observations else set()
        for pack in packs:
            for p in pack['products']:
                if not watch_match(w,p): continue
                reasons=[]; price=p.get('price'); stock=p.get('available'); stamp=p.get('checked_at') or pack.get('checked_at')
                fresh=fresh_observation(stamp)
                if not fresh: reasons.append('stale_or_missing_timestamp')
                if stock is not True: reasons.append('sold_out' if stock is False else 'availability_unknown')
                if price is None or price<=0: reasons.append('invalid_price')
                if p.get('currency')!=w['currency']: reasons.append('currency_unknown_or_mismatch')
                if not w.get('cat') and not w.get('product_id'): reasons.append('edition_needs_verification')
                if len(p.get('variants') or [])>1 and not w.get('variant_id'): reasons.append('variant_needs_verification')
                if w.get('media_min') and grade_score(p.get('media'))<grade_score(w['media_min']): reasons.append('condition_below_minimum_or_unknown')
                if w.get('basis')=='landed':
                    price=price+w['shipping']+w['tax'] if price is not None else None
                if price is not None and price>w['ceiling']: reasons.append('over_ceiling')
                match={'watch_id':w['id'],'record':p,'comparison_price':price,'basis':w['basis'],
                       'status':'qualifying_seller_claim' if not reasons else 'research_lead','reasons':reasons}
                matches.append(match)
                offer_key=json.dumps([p.get('source') or pack.get('source'),p.get('id'),p.get('variant_id')])
                observed_keys.add(offer_key)
                if not reasons:
                    signature=hashlib.sha256(json.dumps([w['id'],p.get('source'),p.get('id'),p.get('variant_id'),price],sort_keys=True).encode()).hexdigest()
                    current_qualified.append(signature)
                    if signature!=observations.get(offer_key,{}).get('signature') and signature not in legacy_signatures:
                        report['alerts'].append(match)
                    observations[offer_key]={'offer_key':offer_key,'source':p.get('source') or pack.get('source'),'signature':signature,'last_seen':stamp,'status':'qualified'}
                elif fresh and stock is not None and p.get('currency')==w['currency'] and price is not None and price>0:
                    observations[offer_key]={'offer_key':offer_key,'source':p.get('source') or pack.get('source'),'signature':None,'last_seen':stamp,'status':'observed_not_qualified'}
        w['last_checked']=report['checked_at']
        # Absence in partial/failed sources is unknown, not sold out. Clear only after complete observation.
        complete_sources={pack.get('source') for pack in packs if fresh_observation(pack.get('checked_at')) and pack.get('coverage',{}).get('complete') is True and not pack.get('coverage',{}).get('errors')}
        for key,old in observations.items():
            if key not in observed_keys and old.get('source') in complete_sources:old['signature']=None;old['status']='not_in_complete_snapshot'
        w['last_observations']=list(observations.values())
        w['last_qualified']=list({x['signature'] for x in observations.values() if x.get('signature')} or legacy_signatures)
        report['results'].append({'watch_id':w['id'],'matches':matches,'status':'matches_found' if matches else 'not_found_in_checked_sources',
                                  'search_queries':[f'"{w["artist"]}" "{w["title"]}" "{w.get("cat", "")}" vinyl buy',f'"{w["artist"]}" "{w["title"]}" record shop -site:ebay.com']})
    return report

def site_queries(genre,region):
    g=genre or 'all genres'; r=region or 'worldwide'
    return [f'{g} specialist vinyl record shop {r}',f'{g} independent record store online shipping {r}',
            f'{g} record label mailorder vinyl',f'{g} vinyl distro rare used records {r}',
            f'{g} record shop directory {r}',f'{g} vinyl label Bandcamp',
            f'{g} vinyl records tienda discos disques Schallplatten mailorder']

def text_out(path,value):
    Path(path).parent.mkdir(parents=True,exist_ok=True); Path(path).write_text(value,encoding='utf-8')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state',default='private/memory.json')
    cmds=parser.add_subparsers(dest='command',required=True)
    ex=cmds.add_parser('export',help='Active CSV, full JSON, sold-out CSV, unknown CSV, manifest')
    source=ex.add_mutually_exclusive_group(required=True); source.add_argument('--url'); source.add_argument('--input')
    ex.add_argument('--out',default='private/catalog'); ex.add_argument('--currency'); ex.add_argument('--max-pages',type=int,default=100)
    ex.add_argument('--sitemap',action='store_true'); ex.add_argument('--max-products',type=int,default=5000)
    mem=cmds.add_parser('memory'); ms=mem.add_subparsers(dest='action',required=True)
    ms.add_parser('init'); ms.add_parser('view')
    put=ms.add_parser('set'); put.add_argument('key'); put.add_argument('value'); put.add_argument('--subject',default='self'); put.add_argument('--source',required=True); put.add_argument('--inferred',action='store_true')
    fb=ms.add_parser('feedback'); fb.add_argument('record'); fb.add_argument('--rating',type=int,choices=[-1,1],required=True); fb.add_argument('--tags',required=True); fb.add_argument('--subject',default='self'); fb.add_argument('--reason',default='')
    fb.add_argument('--stage',choices=['interested','auditioned','owned'],default='auditioned')
    forget=ms.add_parser('forget'); forget.add_argument('id')
    undo=ms.add_parser('restore'); undo.add_argument('backup')
    imp=ms.add_parser('import-items'); imp.add_argument('kind',choices=['collection','assessments']); imp.add_argument('file')
    ev=cmds.add_parser('explore'); ev.add_argument('--mood',default=''); ev.add_argument('--experience',default='')
    ev.add_argument('--energy',choices=['low','medium','high'],default='medium'); ev.add_argument('--lyrics',choices=['yes','no','either'],default='either')
    ev.add_argument('--novelty',choices=['low','medium','high'],default='medium'); ev.add_argument('--out',default='private/exploration.json')
    wa=cmds.add_parser('watch'); ws=wa.add_subparsers(dest='action',required=True)
    add=ws.add_parser('add'); add.add_argument('--artist',required=True); add.add_argument('--title',required=True); add.add_argument('--ceiling',type=float,required=True); add.add_argument('--currency',default='USD')
    for field in ['cat','label','format','released','product-id','variant-id']: add.add_argument('--'+field,default='')
    add.add_argument('--basis',choices=['item','landed'],default='item'); add.add_argument('--shipping',type=float); add.add_argument('--tax',type=float)
    add.add_argument('--media-min',choices=['M','NM','VG+','VG','G+','G','F','P'])
    stop=ws.add_parser('pause'); stop.add_argument('id'); resume=ws.add_parser('resume'); resume.add_argument('id')
    ws.add_parser('list')
    check=ws.add_parser('check'); check.add_argument('--catalog',action='append',default=[]); check.add_argument('--refresh',action='store_true'); check.add_argument('--max-pages',type=int,default=100); check.add_argument('--out',default='private/watch-report.json')
    sites=cmds.add_parser('sites'); ss=sites.add_subparsers(dest='action',required=True)
    sq=ss.add_parser('queries'); sq.add_argument('--genre',default=''); sq.add_argument('--region',default=''); sq.add_argument('--out',default='private/site-queries.json')
    sa=ss.add_parser('add'); sa.add_argument('url'); sa.add_argument('--name',required=True); sa.add_argument('--genres',default=''); sa.add_argument('--adapter',choices=['manual','shopify'],default='manual'); sa.add_argument('--currency'); sa.add_argument('--evidence',default='')
    ss.add_parser('list')
    pr=ss.add_parser('probe'); pr.add_argument('url'); pr.add_argument('--out',default='private/site-probe.json')
    args=parser.parse_args()
    if args.command=='export':
        if not 1<=args.max_pages<=1000 or args.max_products<0: parser.error('Invalid scan limits')
        pack=load_catalog(args.input) if args.input else scan(args.url,args.max_pages,currency=args.currency,sitemap=args.sitemap,max_products=args.max_products)
        if args.input and args.currency:
            for row in pack['products']: row['currency']=args.currency
            pack['currency']=args.currency; pack['currency_note']='User supplied; independently verify seller denomination'
        result=export_catalog(pack,args.out); print(json.dumps({'counts':result,'coverage':pack.get('coverage')},indent=2)); return
    if args.command=='memory' and args.action=='init':
        p=Path(args.state)
        p.parent.mkdir(parents=True,exist_ok=True)
        # Exclusive creation protects existing state, even under concurrent startup.
        with p.open('x',encoding='utf-8') as f: json.dump(blank_state(),f,indent=2)
        print('Created',args.state); return
    s=state_read(args.state)
    if args.command=='memory':
        if args.action=='view': print(json.dumps(memory_view(s),ensure_ascii=False,indent=2)); return
        with edit_state(args.state,'memory '+args.action) as s:
            if args.action=='set':
                for p in s['preferences']:
                    if p['subject']==args.subject and p['key']==args.key: p['active']=False
                row={'id':uid(),'subject':args.subject,'key':args.key,'value':args.value,'source':args.source,'status':'inferred' if args.inferred else 'confirmed','at':now(),'active':True}
                s['preferences'].append(row); print(row['id'])
            elif args.action=='feedback':
                tags=sorted(set(t.strip().lower() for t in args.tags.split(',') if t.strip()))
                if not tags: raise ValueError('Supply at least one feedback tag')
                row={'id':uid(),'subject':args.subject,'record':args.record,'rating':args.rating,'tags':tags,'reason':args.reason,'stage':args.stage,'at':now(),'active':True}
                s['feedback'].append(row); print(row['id'])
            elif args.action=='forget':
                found=False
                for key in ['preferences','feedback']:
                    for row in s[key]:
                        if row['id']==args.id: row['active']=False; found=True
                if not found: raise ValueError('Preference or feedback ID not found')
            elif args.action=='restore':
                restored=state_read(args.backup)
                for key in ['preferences','feedback','sessions','collection','assessments','watchlist','sites']: s[key]=restored[key]
            elif args.action=='import-items':
                rows=read_json(args.file)
                if not isinstance(rows,list): raise ValueError('Import requires a JSON array')
                for row in rows:
                    if not isinstance(row,dict) or not row.get('id'): raise ValueError('Each item needs stable id')
                    if args.kind=='collection' and row.get('status') not in ['owned','ordered','wanted','rejected','sold']: raise ValueError('Invalid collection status')
                    if args.kind=='assessments':
                        for key,value in row.get('scores',{}).items():
                            if key not in ['L','G','C','A','R','U','I','V','Q'] or value is not None and (type(value)!=int or not 1<=value<=5): raise ValueError('Invalid assessment score')
                        if any(row.get('scores',{}).get(k) for k in ['R','U','I','V','Q']) and not row.get('evidence'): raise ValueError('Objective/market scores require evidence')
                    previous=next((x for x in s[args.kind] if x['id']==row['id']),None)
                    if previous: s[args.kind].remove(previous)
                    s[args.kind].append(dict(row,updated_at=now()))
    elif args.command=='explore':
        if not args.mood and not args.experience:
            print('Ask: What mood? What experience? Low/medium/high energy? Lyrics or instrumental? Familiar or adventurous? Budget and format?'); return
        plan=explore_plan(s,args.mood,args.experience,args.energy,args.lyrics,args.novelty)
        with edit_state(args.state,'exploration session') as s: s['sessions'].append(plan)
        atomic(args.out,plan); print(json.dumps(plan,ensure_ascii=False,indent=2))
    elif args.command=='watch':
        if args.action=='list': print(json.dumps(s['watchlist'],indent=2)); return
        if args.action=='add':
            if number(args.ceiling) is None or args.ceiling<=0: raise ValueError('Ceiling must be finite and positive')
            if args.basis=='landed' and (args.shipping is None or args.tax is None): raise ValueError('Landed ceiling requires explicit shipping and tax estimates')
            if any(x is not None and (number(x) is None or x<0) for x in [args.shipping,args.tax]): raise ValueError('Shipping/tax must be finite and nonnegative')
            with edit_state(args.state,'watch add') as s:
                w={k:getattr(args,k) for k in ['artist','title','ceiling','currency','cat','label','format','released','product_id','variant_id','basis','shipping','tax','media_min']}
                w.update(id=uid(),enabled=True,at=now(),alert_signatures=[]); s['watchlist'].append(w); print(w['id'])
        elif args.action in ['pause','resume']:
            with edit_state(args.state,'watch '+args.action) as s:
                w=next((w for w in s['watchlist'] if w['id']==args.id),None)
                if not w: raise ValueError('Watch ID not found')
                w['enabled']=args.action=='resume'
        else:
            packs=[load_catalog(p) for p in args.catalog]
            if args.refresh:
                if not 1<=args.max_pages<=1000: raise ValueError('Invalid max-pages')
                for site in s['sites']:
                    if site['adapter']=='shopify': packs.append(scan(site['url'],args.max_pages,currency=site.get('currency')))
            if not packs: raise ValueError('No checked sources: supply --catalog or register Shopify sites and --refresh')
            with edit_state(args.state,'watch check') as s:
                report=evaluate_watch(s,packs); atomic(args.out,report)
            print(json.dumps({'new_alerts':len(report['alerts']),'report':args.out,'coverage':report['coverage']},indent=2))
    elif args.command=='sites':
        if args.action=='list': print(json.dumps(s['sites'],indent=2))
        elif args.action=='queries':
            result={'at':now(),'genre':args.genre,'region':args.region,'queries':site_queries(args.genre,args.region),'status':'Queries prepared; run with an AI web-search tool or search provider. No search performed by this command.'}
            atomic(args.out,result); print(json.dumps(result,indent=2))
        elif args.action=='add':
            https(args.url)
            with edit_state(args.state,'site add') as s:
                canonical=args.url.rstrip('/')
                if any(x['url']==canonical for x in s['sites']): raise ValueError('Site already registered')
                s['sites'].append({'id':uid(),'url':canonical,'name':args.name,'genres':args.genres,'adapter':args.adapter,'currency':args.currency,'evidence':args.evidence,'verification':'unverified until research','at':now()})
        else:
            url=https(args.url); results={}
            for name,path in [('homepage',url),('robots',url.rstrip('/')+'/robots.txt')]:
                try:
                    content=fetch(path,max_bytes=2_000_000).decode('utf-8',errors='replace')
                    results[name]={'reachable':True,'title':re.search(r'<title[^>]*>(.*?)</title>',content,re.I|re.S).group(1).strip() if re.search(r'<title[^>]*>(.*?)</title>',content,re.I|re.S) else None}
                    if name=='robots': results[name]['text']=content
                except (ValueError,urllib.error.URLError,TimeoutError) as e: results[name]={'reachable':False,'error':str(e)}
            atomic(args.out,{'url':url,'checked_at':now(),'results':results,'note':'Reachability is not legitimacy, stock verification, or a review of robots rules. AI/operator must review policies before extraction.'}); print(args.out)

if __name__=='__main__':
    try: main()
    except (ValueError,KeyError,FileNotFoundError,FileExistsError,json.JSONDecodeError,urllib.error.URLError) as e:
        print('ERROR:',e); raise SystemExit(2)
