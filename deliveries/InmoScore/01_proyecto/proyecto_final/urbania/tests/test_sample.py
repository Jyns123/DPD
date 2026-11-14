import unittest, tempfile, json
from pathlib import Path
from urbania_phase1 import Search, Store, rows_from_sample

SAMPLE=json.loads((Path(__file__).resolve().parents[1]/'evidence'/'browser_sample.json').read_text(encoding='utf-8'))

class Sample(unittest.TestCase):
 def test_rows_keep_published_data(self):
  search=Search.from_url(SAMPLE['query_url']);rows=rows_from_sample(SAMPLE,search);main=[r for r in rows if not r['recommendation']]
  self.assertEqual(len(rows),8);self.assertEqual(len(main),6);self.assertTrue(all(r['district']==search.district for r in main))
  self.assertEqual(sum(r['listing_kind']=='unit' and r['bedrooms'] is None for r in main),2)
 def test_ingest_keeps_observation_date(self):
  search=Search.from_url(SAMPLE['query_url'])
  with tempfile.TemporaryDirectory() as folder:
   db=Store(str(Path(folder)/'s.sqlite'))
   try:
    stats=db.ingest(db.start(),search,rows_from_sample(SAMPLE,search),observed_at=SAMPLE['observed_date'])
    self.assertEqual(stats,{'new':6,'changed':0,'unchanged':0,'excluded':2})
    self.assertEqual({r[0] for r in db.db.execute('SELECT last_observed_at FROM listings')},{SAMPLE['observed_date']})
   finally:db.close()

if __name__=='__main__':unittest.main()
