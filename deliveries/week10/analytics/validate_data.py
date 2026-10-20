"""Verify the delivered catalogue against its included sklearn artifact."""
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits
BASE=Path(__file__).resolve().parents[1]
data=json.loads((BASE/'data/catalog.json').read_text())
items=data['listings']
frame=pd.read_csv(BASE/'data/listings_clean.csv',dtype={'listing_id':str})
# Listings seen by the own capture (urbania/): updated historical IDs plus new IDs.
live=[r for r in items if r.get('source')=='urbania_fase1']
live_ids={r['id'] for r in live}
new_live=live_ids-set(frame.listing_id)
assert len(frame)==3896 and set(frame.listing_id)<={r['id'] for r in items}
assert len(items)==3896+len(new_live)
assert len({r['id'] for r in items})==len(items)
assert len(data['districts'])==20
assert data['metadata']['live']['liveListings']==len(live)
assert all(r['url'].startswith('https://urbania.pe/inmueble/') and len(r['observedAt'])==10 for r in live)
assert all(r['price']>0 and r['area']>0 and r['predictedPrice']>0 for r in items)
assert all(all(np.isfinite(v) and 0<=v<=1 for v in r['scores'].values()) for r in items)
located=[r for r in items if r['location']]
assert len(located)==133
assert all(-13<r['location']['lat']<-11 and -78<r['location']['lng']<-76 for r in located)
assert all(r['location']['precision'] in ['calle','exacta'] for r in located)
# New listings come from cards, which do not publish maintenance.
assert sum(r['maintenance'] is None for r in items)==2009+len(new_live)
assert sum('possible_duplicate' in r['flags'] for r in items)==24
model=joblib.load(BASE/'models/valuation_model.joblib')
assert not {'price_soles','price_per_m2','baseline_price_soles'} & set(model['feature_columns'])
# Updated listings were valued with their newer card, not with the historical row.
head=frame.head(100)
head=head[~head.listing_id.isin(live_ids)]
with threadpool_limits(limits=1):
    predicted=np.exp(model['pipeline'].predict(head[model['feature_columns']]))
byid={r['id']:r for r in items}
assert all(abs(byid[id]['predictedPrice']-float(p))<=.51 for id,p in zip(head.listing_id,predicted))
result={'status':'passed','listings':len(items),'districts':len(data['districts']),'geocoded_street_or_building':len(located),'unknown_maintenance':2009+len(new_live),'possible_duplicate_rows':24,'model_prediction_rows_checked':len(head),'live_listings':len(live),'live_new_listings':len(new_live)}
(BASE/'tests/results').mkdir(exist_ok=True,parents=True)
(BASE/'tests/results/data-validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
