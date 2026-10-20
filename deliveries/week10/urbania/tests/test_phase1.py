import unittest, tempfile, json
from pathlib import Path
from unittest.mock import Mock,patch
from urbania_phase1 import *
from capture import Client,Robots

S=Search('san-juan-de-lurigancho')
def row(pid='123',price=200000):
 return dict(posting_id=pid,url=BASE+'/inmueble/clasificado/fixture-'+pid,operation='venta',property_type='departamento',listing_kind='unit',price_pen=price,bedrooms=2,area_m2=60,price_raw='S/ '+str(price),features_raw='60 m² tot. 2 dorm.',location='San Juan de Lurigancho, Lima',in_requested_district=True,recommendation=False,filter_match='match',quality_flags=[])
def card(pid,price='S/ 200,000',features='60 m² tot. 2 dorm.',location='San Juan de Lurigancho, Lima'):
 # None omite el bloque, como una card que no lo publica.
 blocks=[('h2','POSTING_CARD_PRICE',price),('h3','POSTING_CARD_FEATURES',features),('h4','POSTING_CARD_LOCATION',location)]
 return f'<div data-qa="posting PROPERTY" data-to-posting="{row(pid)["url"]}" data-id="{pid}">'+''.join(f'<{t} data-qa="{qa}">{v}</{t}>' for t,qa,v in blocks if v is not None)+'</div>'

class Filters(unittest.TestCase):
 def test_verified_range(self):
  self.assertEqual(Search(S.district,bedrooms_min=0,bedrooms_max=1,price_min=100000,price_max=300000,currency='PEN').url(),BASE+'/buscar/venta-de-departamentos-en-san-juan-de-lurigancho--lima--lima?bedroomMin=0&bedroomMax=1&priceMin=100000&priceMax=300000&currencyId=6')
 def test_verified_usd(self):self.assertIn('currencyId=2',Search(S.district,price_min=50000,price_max=100000,currency='USD').url())
 def test_verified_exact(self):self.assertTrue(Search(S.district,bedrooms_exact=2).url().endswith('?bedroomsNumber=2'))
 def test_pagination(self):self.assertTrue(S.url(2).endswith('?page=2'))
 def test_search_from_url(self):
  q=Search(S.district,bedrooms_min=0,bedrooms_max=1,price_min=100000,price_max=300000,currency='PEN');self.assertEqual(Search.from_url(q.url()),q)
  for url in [S.url(2),BASE+'/buscar/venta-de-casas-en-lima',S.url()+'?sort=low_price']:
   with self.assertRaises(ValueError):Search.from_url(url)
 def test_district_confirmed_by_location(self):
  rows=parse_listing(card('1')+card('2',location=None),S)
  self.assertEqual(rows[0]['district'],S.district);self.assertIsNone(rows[1]['district']);self.assertEqual(stable_payload(rows[0])['district'],S.district)
 def test_invalid(self):
  for kwargs in [dict(bedrooms_min=3,bedrooms_max=1),dict(price_min=10),dict(bedrooms_exact=2,bedrooms_min=1),dict(price_min=100,price_max=10,currency='PEN')]:
   with self.assertRaises(ValueError):Search(S.district,**kwargs)
 def test_url_tracking_removed(self):self.assertEqual(canonical_posting(row()['url']+'?n_src=Listado'),row()['url'])
 def test_numbers(self):
  for raw,value in [('114.17',114.17),('2,500.50',2500.5),('2.500,50',2500.5),('1,200',1200)]:self.assertEqual(number(raw),value)
 def test_unknown_not_one(self):self.assertEqual(bounds('86 m² tot. 1 baño',r'dorm\.?'),(None,None,None))
 def test_range_preserved(self):self.assertEqual(bounds('1 a 3 dorm.',r'dorm\.?'),(None,1,3))
 def test_project_review(self):r=row();r['listing_kind']='project';self.assertEqual(filter_match(r,Search(S.district,bedrooms_exact=1)),'project_review')
 def test_mismatch(self):self.assertEqual(filter_match(row(),Search(S.district,bedrooms_exact=1)),'mismatch')
 def test_unknown_currency(self):r=row();self.assertEqual(filter_match(r,Search(S.district,price_max=100000,currency='USD')),'unknown')
 def test_recommendations(self):
  rows=parse_listing(card('1')+'<h2>Encontramos otros inmuebles que podrían interesarte</h2><div class="thin-postings-container">'+card('2')+'</div>',S)
  self.assertFalse(rows[0]['recommendation']);self.assertTrue(rows[1]['recommendation'])
 def test_incomplete_card_kept(self):
  rows=parse_listing(card('1')+card('2',features=None)+card('3',price=None),S)
  self.assertEqual(len(rows),3);self.assertIsNone(rows[1]['bedrooms']);self.assertIn('caracteristicas_no_informadas',rows[1]['quality_flags']);self.assertEqual(rows[1]['price_pen'],200000)
  self.assertIsNone(rows[2]['price_pen']);self.assertFalse(rows[2]['price_is_from']);self.assertIn('precio_no_informado',rows[2]['quality_flags'])
 def test_missing_location_unknown_not_excluded(self):
  r=parse_listing(card('1')+card('2',location=None),S)[1]
  self.assertIsNone(r['in_requested_district']);self.assertIn('ubicacion_no_informada',r['quality_flags']);self.assertTrue(is_main(r));self.assertEqual(r['filter_match'],'unknown')
 def test_majority_missing_is_html_change(self):
  with self.assertRaises(ParseError):parse_listing(card('1',price=None)+card('2',price=None)+card('3'),S)
 def test_single_incomplete_card_page(self):self.assertEqual(len(parse_listing(card('1',features=None),S)),1)
 def test_robots(self):
  r=Robots('User-agent: *\nDisallow: /avisos-api/\nAllow: *page=2\nDisallow: *page=*')
  self.assertTrue(r.allows(S.url(2)));self.assertFalse(r.allows(S.url(6)))
 def test_robots_observed_page_limit(self):
  # Reglas de paginación de robots.txt observadas el 20-10-2026.
  r=Robots('User-agent: *\n'+''.join(f'Allow: *page={n}\n' for n in range(2,6))+'Disallow: *page=*')
  self.assertTrue(r.allows(S.url()));self.assertTrue(r.allows(S.url(5)));self.assertFalse(r.allows(S.url(6)))
 def test_http403_stops(self):
  session=Mock();session.headers={};session.get.return_value=Mock(status_code=403)
  c=Client(session=session)
  with patch('time.sleep'):
   for _ in range(2):
    with self.assertRaises(CaptureStopped):c.fetch(S.url())
  self.assertEqual(session.get.call_count,1)

class Persistence(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.db=Store(str(Path(self.tmp.name)/'test.sqlite'))
 def tearDown(self):self.db.close();self.tmp.cleanup()
 def add(self,r=None,scope=S,observed='2026-10-20T10:00:00+00:00'):
  run=self.db.start();stats=self.db.ingest(run,scope,[r or row()],observed);return run,stats
 def count(self,table):return self.db.db.execute('SELECT COUNT(*) FROM '+table).fetchone()[0]
 def test_idempotent(self):
  run,_=self.add();stats=self.db.ingest(run,S,[row(),row()]);self.assertEqual(self.count('listings'),1);self.assertEqual(self.count('versions'),1);self.assertEqual(self.count('sightings'),1)
 def test_changed_price_versions(self):
  self.add();_,stats=self.add(row(price=210000));self.assertEqual(stats['changed'],1);self.assertEqual(self.count('versions'),2)
 def test_change_then_revert_preserved(self):
  self.add();self.add(row(price=210000));self.add();self.assertEqual(self.count('versions'),3)
 def test_cross_query_no_duplicate(self):
  self.add();self.add(scope=Search(S.district,bedrooms_exact=2));self.assertEqual(self.count('listings'),1);self.assertEqual(self.count('versions'),1)
 def test_recommendation_excluded(self):
  r=row();r['recommendation']=True;self.add(r);self.assertEqual(self.count('listings'),0)
 def test_card_without_location_ingested(self):
  r=row();r.update(location=None,in_requested_district=None);self.add(r);self.assertEqual(self.count('listings'),1)
 def test_partial_not_absent(self):
  self.add();run=self.db.start();self.db.finish_scope(run,S,False,'403');self.assertEqual(self.db.db.execute('SELECT state FROM listings').fetchone()[0],'active')
 def test_filtered_absence_not_withdrawn(self):
  filtered=Search(S.district,price_max=250000,currency='PEN');self.add(scope=filtered);run=self.db.start();self.db.finish_scope(run,filtered,True);self.assertEqual(self.db.db.execute('SELECT state FROM listings').fetchone()[0],'active')
 def test_full_absence_only_not_observed(self):
  self.add();run=self.db.start();self.db.finish_scope(run,S,True);self.assertEqual(self.db.db.execute('SELECT state FROM listings').fetchone()[0],'not_observed')
 def test_404_confirmations_and_reactivation(self):
  self.add();self.assertEqual(self.db.verify('123',404,checked_at='2026-10-20T10:00:00+00:00'),'withdrawal_pending')
  self.assertEqual(self.db.verify('123',404,checked_at='2026-10-20T10:01:00+00:00'),'withdrawal_pending')
  self.assertEqual(self.db.verify('123',410,checked_at='2026-10-21T10:00:00+00:00'),'withdrawn')
  self.assertEqual(self.db.verify('123',200,'valid_listing',checked_at='2026-10-21T11:00:00+00:00'),'active')
 def test_block_not_withdrawn(self):
  self.add()
  for status in [403,429,500,302]:self.assertEqual(self.db.verify('123',status),'active')
 def test_invalid200_not_reactivate(self):
  self.add();self.db.db.execute("UPDATE listings SET state='withdrawn'");self.assertEqual(self.db.verify('123',200,'generic_page'),'withdrawn')
 def test_stale_capture_does_not_restore(self):
  self.add(row(price=210000),observed='2026-10-21T10:00:00+00:00');self.add(row(price=200000));self.assertEqual(json.loads(self.db.db.execute('SELECT payload FROM listings').fetchone()[0])['price_pen'],210000)
 def test_transaction_rollback(self):
  run=self.db.start();bad=row('124');bad['posting_id']='wrong'
  with self.assertRaises(ValueError):self.db.ingest(run,S,[row(),bad])
  self.assertEqual(self.count('listings'),0)
 def test_closed_run_rejected(self):
  run,_=self.add();self.db.finish(run)
  with self.assertRaises(ValueError):self.db.ingest(run,S,[row()])
 def test_export(self):
  self.add();p=Path(self.tmp.name)/'out.csv';self.assertEqual(self.db.export(p),1);self.assertIn('price_pen',p.read_text(encoding='utf-8-sig'))

class CaptureIntegration(unittest.TestCase):
 def fixture(self,pid,total=2,next_page=False):
  r=row(pid)
  return f'<h1>{total} Departamentos en venta en San Juan de Lurigancho</h1><div data-qa="posting PROPERTY" data-id="{pid}" data-to-posting="{r["url"]}"><h2 data-qa="POSTING_CARD_PRICE">S/ 200,000</h2><h3 data-qa="POSTING_CARD_FEATURES">60 m² tot. 2 dorm.</h3><h4 data-qa="POSTING_CARD_LOCATION">San Juan de Lurigancho, Lima</h4></div>'+('<a href="'+S.url()+'">2</a>' if next_page else '')
 def test_two_pages_complete(self):
  from capture import capture
  fake=Mock();fake.fetch.side_effect=[(self.fixture('1',next_page=True),'2026-10-20T10:00:00+00:00'),(self.fixture('2'),'2026-10-20T10:01:00+00:00')]
  with tempfile.TemporaryDirectory() as folder:
   result=capture(S,str(Path(folder)/'db'),3,fake,str(Path(folder)/'html'))
   self.assertTrue(result['complete']);self.assertEqual(result['unique_ids'],2);self.assertEqual(result['pages'],2)
 def test_limit_incomplete(self):
  from capture import capture
  fake=Mock();fake.fetch.return_value=(self.fixture('1',next_page=True),'2026-10-20T10:00:00+00:00')
  with tempfile.TemporaryDirectory() as folder:
   result=capture(S,str(Path(folder)/'db'),1,fake,str(Path(folder)/'html'))
   self.assertFalse(result['complete'])
 def test_block_does_not_mark_empty_complete(self):
  from capture import capture
  fake=Mock();fake.fetch.side_effect=CaptureStopped('403')
  with tempfile.TemporaryDirectory() as folder:
   result=capture(S,str(Path(folder)/'db'),3,fake,str(Path(folder)/'html'))
   self.assertFalse(result['complete']);self.assertEqual(result['unique_ids'],0)
 def test_repeated_pages_incomplete(self):
  from capture import capture
  fake=Mock();fake.fetch.return_value=(self.fixture('1',next_page=True),'2026-10-20T10:00:00+00:00')
  with tempfile.TemporaryDirectory() as folder:
   result=capture(S,str(Path(folder)/'db'),3,fake,str(Path(folder)/'html'))
   self.assertFalse(result['complete']);self.assertEqual(result['unique_ids'],1)
 def test_incomplete_card_does_not_stop(self):
  from capture import capture
  fake=Mock();fake.fetch.return_value=('<h1>2 Departamentos en venta en San Juan de Lurigancho</h1>'+card('1')+card('2',features=None),'2026-10-20T10:00:00+00:00')
  with tempfile.TemporaryDirectory() as folder:
   result=capture(S,str(Path(folder)/'db'),3,fake,str(Path(folder)/'html'))
   self.assertTrue(result['complete']);self.assertEqual(result['unique_ids'],2);self.assertIsNone(result['error'])

if __name__=='__main__':unittest.main()
