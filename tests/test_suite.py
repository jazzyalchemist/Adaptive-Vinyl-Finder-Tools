import copy
import csv
import datetime as dt
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
import vinyl_suite as v

class CatalogTests(unittest.TestCase):
    def test_variant_unknowns_and_metadata(self):
        p=v.normalize({'id':1,'title':'=bad','handle':'a','body_html':'ARTIST: One TITLE: Alpha LABEL: Label CAT: A GENRE: Electronic STYLES: Ambient MEDIA: VG+ SLEEVE: VG','variants':[{'id':2,'price':'0','available':False},{'id':3,'price':'4.99','available':True}]},'https://a.test','USD')
        self.assertEqual(p['artist'],'One'); self.assertTrue(p['available']); self.assertEqual(p['variant_id'],'3')
        self.assertIn('multiple_variants_verify_exact_copy',p['flags']); self.assertIn('Electronic',v.categories(p))
        self.assertIsNone(v.normalize({'id':2,'variants':[{'price':'NaN'}]},'https://a.test')['available'])
    def test_partition_manifest_and_formula_safety(self):
        pack={'checked_at':'old','coverage':{'complete':False},'products':[{'id':1,'title':'=HYPERLINK()','available':True},{'id':2,'available':False},{'id':3,'available':None}]}
        with tempfile.TemporaryDirectory() as d:
            counts=v.export_catalog(pack,d); self.assertEqual(list(counts.values()),[1,1,1])
            with open(Path(d)/'active.csv',encoding='utf-8-sig') as f: rows=list(csv.DictReader(f))
            self.assertTrue(rows[0]['title'].startswith("'=")); self.assertEqual(v.read_json(Path(d)/'full-catalog.json')['products'][0]['title'],'=HYPERLINK()')
            self.assertEqual(v.read_json(Path(d)/'manifest.json')['source_checked_at'],'old')
            self.assertEqual(v.load_catalog(Path(d)/'active.csv')['products'][0]['available'],True)
    def test_scan_short_page(self):
        with patch.object(v,'fetch',return_value=json.dumps({'products':[{'id':1,'variants':[]}]}).encode()):
            result=v.scan('https://a.test')
        self.assertTrue(result['coverage']['complete']); self.assertEqual(result['coverage']['unknown_availability'],1)
    def test_scan_failed_page_is_partial(self):
        batch={'products':[{'id':i+1,'variants':[]} for i in range(250)]}
        with patch.object(v,'fetch',side_effect=[json.dumps(batch).encode(),urllib.error.HTTPError('url',400,'limit',{},None)]):
            result=v.scan('https://a.test',pause=0)
        self.assertEqual(result['coverage']['retrieved'],250); self.assertFalse(result['coverage']['complete']); self.assertTrue(result['coverage']['errors'])
    def test_repeated_page_stops(self):
        batch=json.dumps({'products':[{'id':i+1,'variants':[]} for i in range(250)]}).encode()
        with patch.object(v,'fetch',return_value=batch): result=v.scan('https://a.test',pause=0)
        self.assertIn('repeated_page',result['coverage']['flags'])
    def test_sitemap_reconciles_missing_but_not_exhaustion(self):
        batch=json.dumps({'products':[{'id':i+1,'handle':str(i),'variants':[]} for i in range(250)]}).encode()
        missing=json.dumps({'product':{'id':251,'handle':'missing','variants':[]}}).encode()
        with patch.object(v,'fetch',side_effect=[batch,missing]),patch.object(v,'sitemap_urls',return_value=['https://a.test/products/missing']):
            result=v.scan('https://a.test',max_pages=1,pause=0,sitemap=True)
        self.assertEqual(result['coverage']['retrieved'],251); self.assertFalse(result['coverage']['complete'])
    def test_https_and_redirect_guard(self):
        for url in ['http://a.test','javascript:alert(1)','https://user:pass@a.test']:
            with self.assertRaises(ValueError): v.https(url)
        with self.assertRaises(ValueError): v.HTTPSOnly().redirect_request(None,None,302,'',{},'http://a.test')
    def test_missing_stock_and_zero_not_falsely_buyable(self):
        self.assertIsNone(v.truth('')); self.assertIsNone(v.number('NaN')); self.assertFalse(v.truth('false'))
        self.assertIn('price_needs_verification',v.normalize({'id':1,'variants':[{'price':'0','available':True}]},'https://a.test')['flags'])

class MemoryTests(unittest.TestCase):
    def test_atomic_backup_revision_and_lock(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'memory.json'; v.atomic(p,v.blank_state())
            with v.edit_state(p,'test') as s: s['preferences'].append({'id':'a'})
            self.assertEqual(v.state_read(p)['revision'],1); self.assertEqual(len(list((Path(d)/'memory.json.backups').iterdir())),1)
            self.assertFalse(Path(str(p)+'.lock').exists())
            Path(str(p)+'.lock').write_text('0')
            with self.assertRaises(ValueError):
                with v.edit_state(p,'blocked'): pass
    def test_failed_mutation_does_not_commit(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'memory.json'; v.atomic(p,v.blank_state())
            with self.assertRaises(ValueError):
                with v.edit_state(p,'fail') as s: s['revision']=99; raise ValueError('stop')
            self.assertEqual(v.state_read(p)['revision'],0); self.assertFalse(Path(str(p)+'.lock').exists())
    def test_adaptation_is_reversible_and_subject_specific(self):
        s=v.blank_state(); s['feedback']=[{'rating':1,'tags':['warm'],'subject':'self','active':True},{'rating':-1,'tags':['warm'],'subject':'dad','active':True}]
        self.assertEqual(v.learned(s)['warm']['weight'],.25); s['feedback'][0]['active']=False
        self.assertEqual(v.learned(s),{})
    def test_schema_guard(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.json'; v.atomic(p,{'schema_version':99})
            with self.assertRaises(ValueError): v.state_read(p)
    def test_exploration_separates_context(self):
        s=v.blank_state(); s['preferences']=[{'active':True,'status':'confirmed','subject':'self','key':'avoid','value':'noise'}]
        plan=v.explore_plan(s,'reflective','immersive journey','low','no','high')
        self.assertEqual(len(plan['shortlist']),5); self.assertEqual(plan['confirmed_context'][0]['value'],'noise')
        self.assertEqual(s['sessions'],[])

class WatchTests(unittest.TestCase):
    def setUp(self):
        self.s=v.blank_state(); self.s['watchlist']=[{'id':'w','artist':'Artist','title':'Album','cat':'X1','currency':'USD','ceiling':20,'basis':'item','enabled':True}]
        self.p={'id':1,'artist':'Artist','title':'Album','cat':'X1','currency':'USD','price':10,'available':True,'checked_at':v.now(),'source':'https://a.test'}
    def report(self,p=None): return v.evaluate_watch(self.s,[{'products':[self.p if p is None else p],'coverage':{'complete':True}}])
    def test_exact_constraints_price_stock_and_dedupe(self):
        self.assertEqual(len(self.report()['alerts']),1); self.assertEqual(len(self.report()['alerts']),0)
        self.p['price']=9; self.assertEqual(len(self.report()['alerts']),1)
        self.p['available']=False; self.assertEqual(len(self.report()['alerts']),0)
        self.p['available']=True; self.assertEqual(len(self.report()['alerts']),1)
        self.p['cat']='other'; self.assertEqual(self.report()['results'][0]['matches'],[])
    def test_stale_currency_and_unknown_edition_gates(self):
        self.p['checked_at']='2020-01-01T00:00:00+00:00'; self.assertEqual(len(self.report()['alerts']),0)
        self.p['checked_at']=v.now(); self.p['currency']=None; self.assertEqual(len(self.report()['alerts']),0)
        self.p['currency']='USD'; self.s['watchlist'][0]['cat']=''; self.assertEqual(len(self.report()['alerts']),0)
    def test_future_timestamp_not_fresh(self):
        self.p['checked_at']=(dt.datetime.now(dt.timezone.utc)+dt.timedelta(days=2)).isoformat()
        self.assertEqual(len(self.report()['alerts']),0)
    def test_landed_basis_and_grade(self):
        self.s['watchlist'][0].update(basis='landed',shipping=8,tax=3,media_min='VG+')
        self.p['media']='VG+'; self.assertEqual(len(self.report()['alerts']),0)
        self.s['watchlist'][0]['ceiling']=22; self.assertEqual(len(self.report()['alerts']),1)
        self.p['media']='VG'; self.assertEqual(len(self.report()['alerts']),0)
    def test_full_grade_names_and_record_type(self):
        self.s['watchlist'][0].update(media_min='VG+',format='LP')
        self.p.update(media='Very Good Plus (VG+)',format='Vinyl',type='LP')
        self.assertEqual(len(self.report()['alerts']),1)
        self.assertEqual(v.grade_score('Near Mint (NM or M-)'),5)
        self.assertEqual(v.grade_score('Unknown'),0)

class SitesTests(unittest.TestCase):
    def test_broad_and_niche_queries(self):
        q=v.site_queries('free jazz','Europe'); self.assertGreaterEqual(len(q),7)
        self.assertTrue(any('label' in x for x in q)); self.assertTrue(any('Schallplatten' in x for x in q))

class PackageTests(unittest.TestCase):
    def test_allowlist_never_includes_private(self):
        import build_packages as b
        paths=b.public_files()
        self.assertFalse(any('private' in p.relative_to(b.ROOT).parts for p in paths))
        self.assertFalse(any('dist' in p.relative_to(b.ROOT).parts for p in paths))

if __name__=='__main__': unittest.main()
