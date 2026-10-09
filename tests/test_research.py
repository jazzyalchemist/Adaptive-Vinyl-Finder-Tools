import copy
import json
from pathlib import Path
import tempfile
import unittest
import vinyl_suite as v
import research_engine as r
import listening_history as h

class ResearchTests(unittest.TestCase):
    def setUp(self):
        self.profile=v.read_json(r.ROOT/'templates/discovery-profile.json')
        self.p={'id':'1','artist':'One','title':'Alpha','source':'https://a.test','url':'https://a.test/products/a','available':True,'price':10,'currency':'USD','cat':'A1','format':'LP','styles':'Deep House','genre':'Electronic','media':'VG+','quality_flags':'multiple major genres','L':5,'G':5}
    def test_overlap_is_annotation_not_exception(self):
        report=r.audit_catalog({'products':[self.p]},self.profile)
        self.assertEqual(report['summary']['data_issue_rows'],0)
        self.assertEqual(report['summary']['annotation_only_rows'],1)
        p=report['products'][0];self.assertIsNone(p['scores']['L']);self.assertIsNone(p['scores']['G']);self.assertEqual(p['legacy_scores']['L'],5)
        self.assertIsNone(p['source_snapshot_at']);self.assertEqual(p['stock_verification'],'seller_snapshot_only')
    def test_incremental_reuse_and_changed_price(self):
        first=r.audit_catalog({'products':[self.p]},self.profile);first['products'][0]['cached_assessments']=[{'claim':'evidence'}]
        second=r.audit_catalog({'products':[self.p]},self.profile,previous=first)
        self.assertEqual(second['summary']['metadata_changes'],{'unchanged':1});self.assertEqual(second['products'][0]['cached_assessments'],[{'claim':'evidence'}])
        p=dict(self.p,price=11);third=r.audit_catalog({'products':[p]},self.profile,previous=first)
        self.assertEqual(third['summary']['metadata_changes'],{'changed':1});self.assertNotIn('cached_assessments',third['products'][0])
    def test_routing_never_forces_quota_or_genre_collision(self):
        p=dict(self.p,styles='Contemporary R&B',artist='Marshall');report=r.audit_catalog({'products':[p]},self.profile)
        self.assertTrue(all(not t['selected'] for t in report['exploration_tiers']))
        p=dict(self.p,price=0,artist='Guy J');report=r.audit_catalog({'products':[p]},self.profile)
        self.assertTrue(all(not t['selected'] for t in report['exploration_tiers']))
    def test_progressive_house_not_prog_rock(self):
        self.assertNotIn('Rock',v.categories(self.p|{'styles':'Progressive House'}))
    def test_no_false_offline_freshness(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'catalog.json';v.atomic(path,{'source':'https://a.test','products':[{'id':1,'body_html':'','variants':[{'price':'3','available':True}]}]})
            self.assertIsNone(v.load_catalog(path)['products'][0]['checked_at'])
    def test_interested_is_weaker_than_auditioned(self):
        s=v.blank_state();s['feedback']=[{'rating':1,'tags':['spacious'],'stage':'interested'}]
        self.assertEqual(v.learned(s)['spacious']['weight'],.077)
        s['feedback'][0]['stage']='auditioned';self.assertEqual(v.learned(s)['spacious']['weight'],.25)

class HistoryTests(unittest.TestCase):
    def run_history(self,rows,**kwargs):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'history.json';v.atomic(p,rows)
            return h.summarize([p],'2023-10-09','2026-10-09','America/Denver',**kwargs)
    def event(self,**kw):
        return {'ts':'2025-10-01T12:00:00Z','ms_played':60000,'master_metadata_track_name':'Song','master_metadata_album_artist_name':'Artist','spotify_track_uri':'spotify:track:x','ip_addr':'SECRET_IP','username':'SECRET_NAME','platform':'SECRET_DEVICE',**kw}
    def test_dedupe_privacy_and_counts(self):
        e=self.event();r=self.run_history([e,e,self.event(ts='2025-10-02T12:00:00Z',ms_played=5000,skipped=True)])
        self.assertEqual(r['coverage']['included_unique_music_events'],2);self.assertEqual(r['tracks'][0]['meaningful_events'],1)
        self.assertEqual(r['tracks'][0]['recorded_events'],2);self.assertNotIn('SECRET',json.dumps(r));self.assertEqual(r['genre_coverage_fraction'],0)
    def test_fractional_genre_minutes_and_unmapped(self):
        r=self.run_history([self.event(),self.event(spotify_track_uri='spotify:track:y')],genre_map={'spotify:track:x':{'genres':['deep house','ambient'],'source':'artist/label source'}})
        self.assertEqual(r['genre_coverage_fraction'],.5);self.assertEqual(r['genre_listening_minutes_fractional'],{'ambient':.5,'deep house':.5})
        self.assertEqual(r['unmapped_listening_minutes'],1)
    def test_basic_export_rejected(self):
        with self.assertRaisesRegex(ValueError,'Extended'):self.run_history([{'endTime':'2025','msPlayed':60000}])
    def test_window_uses_local_day_and_podcasts_excluded(self):
        r=self.run_history([self.event(ts='2023-10-09T00:00:00Z'),self.event(master_metadata_track_name=None)])
        self.assertEqual(r['coverage']['included_unique_music_events'],0)
        self.assertEqual(r['coverage']['excluded']['outside_requested_window'],1)

class WatchObservationTests(unittest.TestCase):
    def setUp(self):
        self.s=v.blank_state();self.s['watchlist']=[{'id':'w','artist':'A','title':'T','cat':'X','currency':'USD','ceiling':20,'basis':'item','enabled':True}]
        self.p={'id':'1','artist':'A','title':'T','cat':'X','currency':'USD','price':10,'available':True,'checked_at':v.now(),'source':'https://a.test'}
    def check(self,products,complete=True,stamp=None,errors=None):
        return v.evaluate_watch(self.s,[{'source':'https://a.test','checked_at':stamp or v.now(),'products':products,'coverage':{'complete':complete,'errors':errors or []}}])
    def test_failed_partial_source_does_not_create_fake_restock(self):
        self.assertEqual(len(self.check([self.p])['alerts']),1)
        self.check([],False,errors=['timeout'])
        self.assertEqual(len(self.check([self.p])['alerts']),0)
    def test_stale_absence_does_not_clear_but_fresh_complete_absence_does(self):
        self.check([self.p]);self.check([],stamp='2020-01-01T00:00:00Z')
        self.assertEqual(len(self.check([self.p])['alerts']),0)
        self.check([]);self.assertEqual(len(self.check([self.p])['alerts']),1)
    def test_v2_signature_survives_failed_migration_check(self):
        self.check([self.p]);del self.s['watchlist'][0]['last_observations']
        self.check([],False,errors=['timeout'])
        self.assertEqual(len(self.check([self.p])['alerts']),0)
