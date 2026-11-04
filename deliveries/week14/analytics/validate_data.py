"""Verifica el catálogo; --catalog-only evita abrir el modelo serializado."""
import argparse
import json
import math
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--catalog-only',action='store_true',help='verificar solo el JSON sin abrir el modelo')
args=parser.parse_args()
data=json.loads((BASE/'data/catalog.json').read_text(encoding='utf-8'))
items=data['listings']
assert len(items)==3896
assert len({r['id'] for r in items})==len(items)
assert len(data['districts'])==20
assert all(r['price']>0 and r['area']>0 and r['predictedPrice']>0 for r in items)
assert all(all(math.isfinite(v) and 0<=v<=1 for v in r['scores'].values()) for r in items)
located=[r for r in items if r['location']]
assert len(located)==133
assert all(-13<r['location']['lat']<-11 and -78<r['location']['lng']<-76 for r in located)
assert all(r['location']['precision'] in ['calle','exacta'] for r in located)
assert sum(r['maintenance'] is None for r in items)==2009
assert sum('possible_duplicate' in r['flags'] for r in items)==24
result={'status':'passed','listings':len(items),'districts':len(data['districts']),'geocoded_street_or_building':len(located),'unknown_maintenance':2009,'possible_duplicate_rows':24}
if args.catalog_only:
    result['model_check']='not_run'
    print(json.dumps(result,indent=2))
    raise SystemExit(0)

import joblib
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits
model=joblib.load(BASE/'models/valuation_model.joblib')
assert not {'price_soles','price_per_m2','baseline_price_soles'} & set(model['feature_columns'])
frame=pd.read_csv(BASE/'data/listings_clean.csv',dtype={'listing_id':str})
with threadpool_limits(limits=1):
    predicted=np.exp(model['pipeline'].predict(frame.head(100)[model['feature_columns']]))
byid={r['id']:r for r in items}
assert all(abs(byid[id]['predictedPrice']-float(p))<=.51 for id,p in zip(frame.head(100).listing_id,predicted))
result['model_prediction_rows_checked']=100
(BASE/'tests/results').mkdir(exist_ok=True,parents=True)
(BASE/'tests/results/data-validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
