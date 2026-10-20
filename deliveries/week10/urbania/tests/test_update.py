import unittest, tempfile, fcntl
from pathlib import Path
from urbania_phase1 import BASE, DISTRICTS, CaptureStopped, Store
from update import EXIT_CODES, update

class FakeClient:
 # Simula el sitio: cada distrito responde una página con sus cards y el recuento visible.
 def __init__(self,cards=2,block_at=None,price=True):self.stopped=False;self.calls=[];self.cards=cards;self.block_at=block_at;self.price=price
 def fetch(self,url):
  self.calls.append(url)
  if len(self.calls)==self.block_at:self.stopped=True;raise CaptureStopped('HTTP 403; no reintentar ni marcar avisos retirados')
  slug=url.split('venta-de-departamentos-en-')[1].split('--')[0];name=DISTRICTS[slug];first=1000*(list(DISTRICTS).index(slug)+1)
  price='<h2 data-qa="POSTING_CARD_PRICE">S/ 200,000</h2>' if self.price else ''
  cards=''.join(f'<div data-qa="posting PROPERTY" data-to-posting="{BASE}/inmueble/clasificado/fixture-{first+i}">{price}<h3 data-qa="POSTING_CARD_FEATURES">60 m² tot. 2 dorm.</h3><h4 data-qa="POSTING_CARD_LOCATION">{name}, Lima</h4></div>' for i in range(self.cards))
  return f'<h1>{self.cards} Departamentos en venta en {name}</h1>{cards}','2026-10-20T10:00:00+00:00'

class Update(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.dir=Path(self.tmp.name);self.db=str(self.dir/'u.sqlite')
 def tearDown(self):self.tmp.cleanup()
 def run_update(self,client,districts=None):return update(self.db,districts,5,str(self.dir/'captures'),str(self.dir/'actual.csv'),client)
 def states(self):
  db=Store(self.db)
  try:return dict(db.db.execute('SELECT posting_id,state FROM listings').fetchall())
  finally:db.close()
 def test_all_districts_one_client(self):
  client=FakeClient();summary=self.run_update(client)
  self.assertEqual(summary['status'],'ok');self.assertEqual(len(client.calls),len(DISTRICTS));self.assertEqual(summary['complete_districts'],len(DISTRICTS))
  self.assertEqual(summary['exported'],2*len(DISTRICTS));self.assertTrue((self.dir/'actual.csv').exists());self.assertFalse((self.dir/'actual.csv.tmp').exists())
  self.assertEqual(len(list((self.dir/'captures'/'updates').glob('*.json'))),1)
 def test_block_stops_remaining_districts(self):
  client=FakeClient(block_at=2);summary=self.run_update(client,['miraflores','barranco','lince'])
  self.assertEqual(summary['status'],'blocked');self.assertEqual(EXIT_CODES[summary['status']],2);self.assertEqual(len(client.calls),2)
  self.assertTrue(summary['results'][0]['complete']);self.assertIn('403',summary['results'][1]['reason']);self.assertTrue(summary['results'][2]['reason'].startswith('Omitido'))
  self.assertEqual(set(self.states().values()),{'active'})
 def test_concurrent_run_skipped(self):
  client=FakeClient()
  with open(self.db+'.lock','w') as lock:
   fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);summary=self.run_update(client)
  self.assertEqual(summary['status'],'skipped');self.assertEqual(client.calls,[])
 def test_html_change_is_error(self):
  summary=self.run_update(FakeClient(price=False),['miraflores'])
  self.assertEqual(summary['status'],'error');self.assertEqual(EXIT_CODES[summary['status']],1);self.assertEqual(summary['results'][0]['error'],'ParseError');self.assertEqual(self.states(),{})
 def test_next_run_marks_missing_listing(self):
  self.run_update(FakeClient(cards=2),['miraflores']);summary=self.run_update(FakeClient(cards=1),['miraflores'])
  self.assertEqual(summary['status'],'ok');self.assertEqual(summary['results'][0]['stats']['unchanged'],1);self.assertEqual(self.states(),{'1000':'active','1001':'not_observed'})

if __name__=='__main__':unittest.main()
