#!/usr/bin/env python3
"""Read-only Shopify catalog extractor; Python 3 standard library only."""
import argparse,datetime,html,json,re,time,urllib.request,urllib.parse,pathlib
KEYS=['ARTIST','TITLE','LABEL','CAT','TYPE','FORMAT','COUNTRY','RELEASED','GENRE','STYLES','MEDIA','SLEEVE','TRACKLIST','COMMENTS']
def normalize(p,base):
 s=html.unescape(re.sub('<[^>]*>',' ',p.get('body_html','')));s=re.sub(r'\s+',' ',s)
 d={}
 for i,k in enumerate(KEYS):
  m=re.search(r'\b'+k+r':\s*(.*?)(?=\b(?:'+'|'.join(KEYS[i+1:])+r'):|$)',s)
  d[k.lower()]=m.group(1).strip() if m else ''
 vs=p.get('variants',[]);v=next((x for x in vs if x.get('available')),vs[0] if vs else {})
 d.update(id=p.get('id'),name=p.get('title',''),price=float(v['price']) if v.get('price') is not None else None,available=any(x.get('available') for x in vs),url=base+'/products/'+p.get('handle',''),tags=p.get('tags',[]),scores={},evidence={})
 return d
def scan(url,max_pages=100,pause=.15):
 u=urllib.parse.urlsplit(url)
 if u.scheme!='https' or not u.hostname:raise ValueError('Supply an HTTPS store URL')
 base=f'https://{u.netloc}'; products={};pages=0;complete=False;errors=[]
 for page in range(1,max_pages+1):
  try:
   req=urllib.request.Request(base+f'/products.json?limit=250&page={page}',headers={'User-Agent':'VinylScout/1.0 read-only research'})
   payload=json.load(urllib.request.urlopen(req,timeout=45));batch=payload['products']
   if not isinstance(batch,list):raise ValueError('Invalid products array')
   for p in batch: products[p['id']]=normalize(p,base)
   pages+=1
   if len(batch)<250:complete=True;break
   time.sleep(pause)
  except Exception as e:errors.append(f'Page {page}: {type(e).__name__}: {e}');break
 return {'source':base,'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'coverage':{'retrieved':len(products),'available':sum(p['available'] for p in products.values()),'pages':pages,'complete':complete,'limit_reached':not complete and not errors,'errors':errors,'note':'Availability is a seller feed claim, not a reservation; missing listing counts require comparison with the store catalog.'},'products':list(products.values())}
def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('url');a.add_argument('--output',default='catalog-scan.json');a.add_argument('--max-pages',type=int,default=100);opts=a.parse_args()
 if not 1<=opts.max_pages<=1000:a.error('--max-pages must be 1–1000')
 payload=scan(opts.url,opts.max_pages);pathlib.Path(opts.output).write_text(json.dumps(payload,ensure_ascii=False,indent=2));print(json.dumps(payload['coverage'],indent=2));print('Saved',opts.output)
if __name__=='__main__':main()
