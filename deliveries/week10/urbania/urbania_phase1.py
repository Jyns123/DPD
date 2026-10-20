"""Urbania fase 1: venta/departamentos, filtros y estado incremental. Python 3.10+."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import re
import sqlite3
import time
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlencode, urljoin, urlsplit, urlunsplit, parse_qsl
from bs4 import BeautifulSoup

BASE = 'https://urbania.pe'
VERSION = '1.0-phase1'
CURRENCY_IDS = {'PEN': 6, 'USD': 2}
# Estos slugs se observaron en los enlaces de distrito del sitio. SJL se abrió directamente.
DISTRICTS = {
 'miraflores':'Miraflores', 'santiago-de-surco':'Santiago de Surco',
 'san-isidro':'San Isidro', 'san-miguel':'San Miguel', 'san-borja':'San Borja',
 'surquillo':'Surquillo', 'jesus-maria':'Jesús María', 'magdalena':'Magdalena',
 'barranco':'Barranco', 'lima-cercado':'Lima Cercado', 'chorrillos':'Chorrillos',
 'pueblo-libre':'Pueblo Libre', 'lince':'Lince', 'la-victoria':'La Victoria',
 'la-molina':'La Molina', 'brena':'Breña', 'ate-vitarte':'Ate Vitarte',
 'los-olivos':'Los Olivos', 'san-martin-de-porres':'San Martín de Porres',
 'san-juan-de-lurigancho':'San Juan de Lurigancho',
}

def utcnow():
 return datetime.now(timezone.utc).isoformat()

def normalized(s):
 return re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',s or '').encode('ascii','ignore').decode().lower()).strip()

@dataclass(frozen=True)
class Search:
 district: str
 bedrooms_min: int | None = None
 bedrooms_max: int | None = None
 bedrooms_exact: int | None = None
 price_min: int | None = None
 price_max: int | None = None
 currency: str | None = None

 def __post_init__(self):
  if self.district not in DISTRICTS: raise ValueError('Distrito fuera del catálogo de fase 1')
  if self.bedrooms_exact is not None and (self.bedrooms_min is not None or self.bedrooms_max is not None):
   raise ValueError('Usar dormitorios exactos o rango, no ambos')
  for value in [self.bedrooms_min,self.bedrooms_max,self.bedrooms_exact]:
   if value is not None and (isinstance(value,bool) or not isinstance(value,int) or not 0 <= value <= 5):
    raise ValueError('Dormitorios entre 0 y 5; 5+ requiere verificar otra semántica')
  for value in [self.price_min,self.price_max]:
   if value is not None and (isinstance(value,bool) or not isinstance(value,int) or value < 0):
    raise ValueError('Precios enteros no negativos')
  if self.bedrooms_min is not None and self.bedrooms_max is not None and self.bedrooms_min > self.bedrooms_max:
   raise ValueError('Rango de dormitorios invertido')
  if self.price_min is not None and self.price_max is not None and self.price_min > self.price_max:
   raise ValueError('Rango de precios invertido')
  if (self.price_min is not None or self.price_max is not None) and self.currency not in CURRENCY_IDS:
   raise ValueError('Especificar PEN o USD para filtrar precios')
  if self.currency is not None and self.currency not in CURRENCY_IDS: raise ValueError('Moneda no soportada')

 @property
 def unfiltered(self):
  return all(v is None for v in [self.bedrooms_min,self.bedrooms_max,self.bedrooms_exact,self.price_min,self.price_max,self.currency])

 def url(self, page=1):
  if isinstance(page,bool) or not isinstance(page,int) or page < 1: raise ValueError('Página >= 1')
  query={}
  if self.bedrooms_exact is not None: query['bedroomsNumber']=self.bedrooms_exact
  elif self.bedrooms_min is not None or self.bedrooms_max is not None:
   query['bedroomMin']=self.bedrooms_min if self.bedrooms_min is not None else 0
   if self.bedrooms_max is not None: query['bedroomMax']=self.bedrooms_max
  for key,value in [('priceMin',self.price_min),('priceMax',self.price_max)]:
   if value is not None: query[key]=value
  if self.currency: query['currencyId']=CURRENCY_IDS[self.currency]
  if page > 1: query['page']=page
  path=f'{BASE}/buscar/venta-de-departamentos-en-{self.district}--lima--lima'
  return path + ('?'+urlencode(query) if query else '')

 @property
 def key(self):
  return hashlib.sha256(self.url().encode()).hexdigest()

 @classmethod
 def from_url(cls,url):
  # Solo acepta URLs que el propio generador reproduce exactamente.
  parts=urlsplit(url);m=re.fullmatch(r'/buscar/venta-de-departamentos-en-(.+)--lima--lima',parts.path)
  if not m:raise ValueError('URL de búsqueda no reconocida')
  q={k:int(v) for k,v in parse_qsl(parts.query)}
  currency={v:k for k,v in CURRENCY_IDS.items()}.get(q.get('currencyId'))
  search=cls(m[1],q.get('bedroomMin'),q.get('bedroomMax'),q.get('bedroomsNumber'),q.get('priceMin'),q.get('priceMax'),currency)
  if search.url()!=url:raise ValueError('URL con parámetros fuera del contrato verificado')
  return search


def canonical_posting(url):
 parts=urlsplit(urljoin(BASE,url or ''))
 if parts.hostname not in {'urbania.pe','www.urbania.pe'} or not parts.path.startswith('/inmueble/'):
  raise ValueError('Enlace de ficha de Urbania requerido')
 if not re.search(r'-\d+$',parts.path.rstrip('/')): raise ValueError('Ficha sin ID reconocible')
 return urlunsplit(('https','urbania.pe',parts.path.rstrip('/'),'',''))

NUMBER=r'\d+(?:[.,]\d+)*'
def number(s):
 if s is None:return None
 s=re.sub(r'\s+','',str(s))
 if not re.fullmatch(NUMBER,s):return None
 if '.' in s and ',' in s:
  dec='.' if s.rfind('.')>s.rfind(',') else ','
  s=s.replace(',' if dec=='.' else '.','').replace(dec,'.')
 elif '.' in s or ',' in s:
  sep='.' if '.' in s else ','; chunks=s.split(sep)
  if len(chunks)>2:
   if not all(len(c)==3 for c in chunks[1:]):return None
   s=''.join(chunks)
  elif len(chunks[-1])==3:s=''.join(chunks)
  else:s=s.replace(sep,'.')
 try:return float(s)
 except ValueError:return None

def bounds(text,unit):
 match=re.search(rf'({NUMBER})(?:\s*(?:a|hasta|[-–])\s*({NUMBER}))?\s*{unit}',text,re.I)
 if not match:return None,None,None
 lo=number(match[1]);hi=number(match[2]) if match[2] else lo
 return (lo if lo==hi else None),lo,hi

def text(node):return re.sub(r'\s+',' ',node.get_text(' ',strip=True)).strip() if node else None

class ParseError(RuntimeError):pass
class CaptureStopped(RuntimeError):pass

# Si un bloque falta en una card, queda nulo con bandera. Si falta en la mayoría de la
# página, lo probable es un cambio de HTML: se rechaza para no grabar nulos masivos.
CARD_BLOCKS={'price_raw':('POSTING_CARD_PRICE','precio_no_informado'),
 'features_raw':('POSTING_CARD_FEATURES','caracteristicas_no_informadas'),
 'location':('POSTING_CARD_LOCATION','ubicacion_no_informada')}

def parse_listing(html,search:Search):
 soup=BeautifulSoup(html,'lxml')
 title=text(soup.title) or ''
 if any(w in title.lower() for w in ['just a moment','access denied','verify you are human']):
  raise ParseError('Página de verificación, no listado')
 cards=soup.select('[data-qa="posting PROPERTY"], [data-qa="posting DEVELOPMENT"]')
 if not cards:raise ParseError('Sin cards reconocibles; no asumir oferta vacía')
 boundary=next((h for h in soup.find_all(re.compile('^h[1-6]$')) if 'otros inmuebles que podr' in normalized(text(h))),None)
 rows=[]; seen=set()
 for card in cards:
  recommended=bool(card.find_parent(class_='thin-postings-container'))
  if boundary and boundary in card.find_all_previous():recommended=True
  href=card.get('data-to-posting')
  if not href:
   a=card.select_one('a[href*="/inmueble/"]');href=a.get('href') if a else None
  try:url=canonical_posting(href)
  except (ValueError,TypeError):continue
  pid=re.search(r'-(\d+)$',url)[1]
  # Identidad canónica: ruta/ID; data-id discrepante se registra como bandera.
  flags=[]
  if card.get('data-id') and card['data-id']!=pid:flags.append('card_id_discrepante')
  block={}
  for field,(qa,flag) in CARD_BLOCKS.items():
   block[field]=text(card.select_one(f'[data-qa="{qa}"]')) or None
   if block[field] is None:flags.append(flag)
  price_raw,features,location=block['price_raw'],block['features_raw'],block['location']
  # Sin ubicación no se puede comprobar el distrito: queda desconocido, no excluido.
  in_district=normalized(DISTRICTS[search.district]) in normalized(location) if location else None
  if in_district is False:flags.append('ubicacion_fuera_distrito_consultado')
  # El distrito consultado solo se asigna cuando la ubicación de la card lo confirma.
  row={'posting_id':pid,'url':url,'operation':'venta','property_type':'departamento',
       'district':search.district if in_district else None,
       'listing_kind':'project' if '/proyecto/' in url else 'unit','price_raw':price_raw,
       'features_raw':features,'location':location,'address':text(card.select_one('[class*="location-address"]')),
       'price_is_from':bool(re.search('desde',price_raw or '',re.I)),
       'recommendation':recommended,'in_requested_district':in_district,'quality_flags':flags}
  for cur,pattern in [('pen',r'S/\.?'),('usd',r'USD|US\$')]:
   m=re.search(rf'(?:{pattern})\s*({NUMBER})',price_raw or '',re.I);row[f'price_{cur}']=number(m[1]) if m else None
  for key,unit in [('bedrooms',r'dorm\.?'),('area_m2',r'm(?:²|2)\s*tot\.?'),('bathrooms',r'baños?')]:
   val,lo,hi=bounds(features or '',unit);row[key]=val;row[key+'_min']=lo;row[key+'_max']=hi
  if row['bedrooms'] is None and row['listing_kind']=='unit':flags.append('dormitorios_no_informados')
  if re.search(r'\bha\b',features or '',re.I):flags.append('superficie_en_hectareas_revisar')
  row['filter_match']=filter_match(row,search)
  if pid not in seen:rows.append(row);seen.add(pid)
 main=[r for r in rows if not r['recommendation']]
 for field,(qa,_) in CARD_BLOCKS.items():
  missing=sum(r[field] is None for r in main)
  if len(main)>1 and missing*2>len(main):raise ParseError(f'{qa} ausente en {missing} de {len(main)} cards; posible cambio de HTML')
 return rows

def is_main(row):
 # Resultado principal: ni recomendación ni card de otro distrito. Una card sin ubicación
 # apareció entre los resultados del distrito y cuenta como principal.
 return not row.get('recommendation') and row.get('in_requested_district') is not False

def filter_match(row,search):
 if row.get('recommendation'):return 'recommendation'
 if row.get('in_requested_district') is False:return 'different_district'
 # El rango de un proyecto no prueba una combinación precio/área/dormitorio de una unidad.
 if row['listing_kind']=='project':return 'project_review'
 unknown=row.get('in_requested_district',True) is None
 n=row.get('bedrooms')
 lo=search.bedrooms_exact if search.bedrooms_exact is not None else search.bedrooms_min
 hi=search.bedrooms_exact if search.bedrooms_exact is not None else search.bedrooms_max
 if lo is not None or hi is not None:
  if n is None:unknown=True
  elif (lo is not None and n<lo) or (hi is not None and n>hi):return 'mismatch'
 if search.price_min is not None or search.price_max is not None:
  amount=row.get('price_'+search.currency.lower())
  if amount is None or row.get('price_is_from'):unknown=True
  elif (search.price_min is not None and amount<search.price_min) or (search.price_max is not None and amount>search.price_max):return 'mismatch'
 return 'unknown' if unknown else 'match'

def rows_from_sample(sample,search:Search):
 # Filas de evidence/browser_sample.json con el formato de parse_listing.
 rows=[]
 for original in sample['rows']:
  row=dict(original);row['url']=BASE+row.pop('path')
  row.update(operation='venta',property_type='departamento')
  in_district=normalized(DISTRICTS[search.district]) in normalized(row['location'])
  row.update(in_requested_district=in_district,district=search.district if in_district else None)
  row.setdefault('price_is_from',row['listing_kind']=='project')
  row['quality_flags']=['dormitorios_no_informados'] if row['listing_kind']=='unit' and row.get('bedrooms') is None else []
  row['filter_match']=filter_match(row,search)
  rows.append(row)
 return rows

# Persistir solo datos propios de la ficha, sin filtros, posición ni tracking.
CONTENT_FIELDS=['url','operation','property_type','district','listing_kind','price_raw','features_raw','location','address',
 'price_is_from','price_pen','price_usd','bedrooms','bedrooms_min','bedrooms_max','area_m2','area_m2_min','area_m2_max',
 'bathrooms','bathrooms_min','bathrooms_max','quality_flags']

def stable_payload(row):
 payload={k:row.get(k) for k in CONTENT_FIELDS}
 payload['url']=canonical_posting(row['url'])
 return payload

class Store:
 def __init__(self,path='urbania.sqlite'):
  self.db=sqlite3.connect(path,isolation_level=None)
  self.db.row_factory=sqlite3.Row
  self.db.execute('PRAGMA foreign_keys=ON')
  self.db.execute('PRAGMA journal_mode=WAL')
  self.db.execute('PRAGMA busy_timeout=5000')
  self.db.executescript('''
   CREATE TABLE IF NOT EXISTS runs(id INTEGER PRIMARY KEY, started_at TEXT NOT NULL, finished_at TEXT, state TEXT NOT NULL);
   CREATE TABLE IF NOT EXISTS listings(source TEXT NOT NULL DEFAULT 'urbania', posting_id TEXT NOT NULL,
    first_ingested_at TEXT NOT NULL,last_ingested_at TEXT NOT NULL,last_observed_at TEXT,
    payload TEXT NOT NULL,content_hash TEXT NOT NULL,state TEXT NOT NULL DEFAULT 'active',last_seen_run INTEGER,
    PRIMARY KEY(source,posting_id));
   CREATE TABLE IF NOT EXISTS versions(source TEXT NOT NULL,posting_id TEXT NOT NULL,hash TEXT NOT NULL,
    observed_at TEXT NOT NULL,payload TEXT NOT NULL,id INTEGER PRIMARY KEY,
    FOREIGN KEY(source,posting_id) REFERENCES listings(source,posting_id));
   CREATE TABLE IF NOT EXISTS sightings(run_id INTEGER NOT NULL,posting_id TEXT NOT NULL,scope TEXT NOT NULL,
    filter_match TEXT NOT NULL,PRIMARY KEY(run_id,posting_id,scope),FOREIGN KEY(run_id) REFERENCES runs(id));
   CREATE TABLE IF NOT EXISTS members(scope TEXT NOT NULL,posting_id TEXT NOT NULL,last_run INTEGER NOT NULL,
    missing_complete_runs INTEGER NOT NULL DEFAULT 0,PRIMARY KEY(scope,posting_id));
   CREATE TABLE IF NOT EXISTS scopes(run_id INTEGER NOT NULL,scope TEXT NOT NULL,complete INTEGER NOT NULL,
    reason TEXT,PRIMARY KEY(run_id,scope));
   CREATE TABLE IF NOT EXISTS checks(id INTEGER PRIMARY KEY,posting_id TEXT NOT NULL,checked_at TEXT NOT NULL,
    http_status INTEGER NOT NULL,evidence TEXT NOT NULL);
  ''')
 def close(self):self.db.close()
 def start(self,now=None):
  return self.db.execute("INSERT INTO runs(started_at,state) VALUES(?,'running')",(now or utcnow(),)).lastrowid
 def ingest(self,run_id,search:Search,rows,observed_at=None,now=None):
  now=now or utcnow();stats={'new':0,'changed':0,'unchanged':0,'excluded':0}
  run=self.db.execute('SELECT * FROM runs WHERE id=?',(run_id,)).fetchone()
  if not run or run['state']!='running':raise ValueError('Ejecución no abierta')
  self.db.execute('BEGIN IMMEDIATE')
  try:
   for row in rows:
    if not is_main(row):stats['excluded']+=1;continue
    url=canonical_posting(row['url']);pid=re.search(r'-(\d+)$',url)[1]
    if str(row['posting_id'])!=pid:raise ValueError('posting_id no corresponde a URL')
    payload=stable_payload(row);serialized=json.dumps(payload,sort_keys=True,ensure_ascii=False)
    digest=hashlib.sha256(serialized.encode()).hexdigest()
    old=self.db.execute("SELECT * FROM listings WHERE source='urbania' AND posting_id=?",(pid,)).fetchone()
    if old and old['last_observed_at'] and (observed_at is None or observed_at<old['last_observed_at']):
     # Importar una captura antigua no debe restaurar un precio anterior ni reactivar un aviso.
     stats['excluded']+=1;continue
    if old is None:
     self.db.execute('INSERT INTO listings(source,posting_id,first_ingested_at,last_ingested_at,last_observed_at,payload,content_hash,state,last_seen_run) VALUES(?,?,?,?,?,?,?, ?,?)',
       ('urbania',pid,now,now,observed_at,serialized,digest,'active',run_id))
     stats['new']+=1;changed=True
    else:
     changed=digest!=old['content_hash'];stats['changed' if changed else 'unchanged']+=1
     self.db.execute("UPDATE listings SET last_ingested_at=?,last_observed_at=COALESCE(?,last_observed_at),payload=?,content_hash=?,state='active',last_seen_run=? WHERE source='urbania' AND posting_id=?",
       (now,observed_at,serialized,digest,run_id,pid))
    if changed:self.db.execute('INSERT INTO versions(source,posting_id,hash,observed_at,payload) VALUES(?,?,?,?,?)',('urbania',pid,digest,observed_at or now,serialized))
    self.db.execute('INSERT OR REPLACE INTO sightings VALUES(?,?,?,?)',(run_id,pid,search.key,row.get('filter_match','unknown')))
    self.db.execute('INSERT INTO members VALUES(?,?,?,0) ON CONFLICT(scope,posting_id) DO UPDATE SET last_run=excluded.last_run,missing_complete_runs=0',(search.key,pid,run_id))
   self.db.execute('COMMIT')
  except Exception:self.db.execute('ROLLBACK');raise
  return stats
 def finish_scope(self,run_id,search:Search,complete=False,reason=''):
  # Una ejecución limitada, fallida o repetida no crea evidencia de ausencia.
  old=self.db.execute('SELECT 1 FROM scopes WHERE run_id=? AND scope=?',(run_id,search.key)).fetchone()
  if old:return
  self.db.execute('BEGIN IMMEDIATE')
  try:
   self.db.execute('INSERT INTO scopes VALUES(?,?,?,?)',(run_id,search.key,int(complete),reason))
   if complete:
    self.db.execute('UPDATE members SET missing_complete_runs=missing_complete_runs+1 WHERE scope=? AND last_run<>?',(search.key,run_id))
    if search.unfiltered:
     self.db.execute("UPDATE listings SET state='not_observed' WHERE source='urbania' AND state='active' AND (last_seen_run IS NULL OR last_seen_run<>?) AND posting_id IN (SELECT posting_id FROM members WHERE scope=? AND last_run<>?)",(run_id,search.key,run_id))
   self.db.execute('COMMIT')
  except Exception:self.db.execute('ROLLBACK');raise
 def finish(self,run_id,state='finished',now=None):
  self.db.execute('UPDATE runs SET finished_at=?,state=? WHERE id=?',(now or utcnow(),state,run_id))
 def verify(self,pid,http_status,evidence='',checked_at=None,min_hours=6):
  """No realiza requests. Registra el resultado de una verificación de ficha externa."""
  checked_at=checked_at or utcnow();t=datetime.fromisoformat(checked_at)
  old=self.db.execute("SELECT * FROM listings WHERE source='urbania' AND posting_id=?",(str(pid),)).fetchone()
  if old is None:raise ValueError('Aviso desconocido')
  # Un 200 genérico, un bloqueo o un redirect no prueba actividad ni retirada.
  if http_status==200 and evidence=='valid_listing':new_state='active'
  elif http_status in {404,410} or (http_status==200 and evidence=='explicit_unavailable'):
   previous=self.db.execute('SELECT * FROM checks WHERE posting_id=? ORDER BY checked_at DESC,id DESC LIMIT 1',(str(pid),)).fetchone()
   unavailable=previous and (previous['http_status'] in {404,410} or previous['evidence']=='explicit_unavailable')
   distant=unavailable and (t-datetime.fromisoformat(previous['checked_at'])).total_seconds()>=min_hours*3600
   new_state='withdrawn' if distant else ('withdrawn' if old['state']=='withdrawn' else 'withdrawal_pending')
  else:new_state=old['state']
  self.db.execute('BEGIN IMMEDIATE')
  try:
   self.db.execute('INSERT INTO checks(posting_id,checked_at,http_status,evidence) VALUES(?,?,?,?)',(str(pid),checked_at,http_status,evidence))
   self.db.execute("UPDATE listings SET state=? WHERE source='urbania' AND posting_id=?",(new_state,str(pid)))
   self.db.execute('COMMIT')
  except Exception:self.db.execute('ROLLBACK');raise
  return new_state
 def export(self,path):
  records=[]
  for entry in self.db.execute('SELECT * FROM listings ORDER BY posting_id'):
   row=dict(entry);payload=json.loads(row.pop('payload'));row.update(payload)
   row['quality_flags']=' | '.join(row.get('quality_flags') or []);records.append(row)
  if records:
   with open(path,'w',newline='',encoding='utf-8-sig') as f:
    writer=csv.DictWriter(f,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
  return len(records)

# CLI begins

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 sub=parser.add_subparsers(dest='command',required=True)
 p=sub.add_parser('url');p.add_argument('--district',required=True,choices=DISTRICTS)
 p.add_argument('--bedrooms-min',type=int);p.add_argument('--bedrooms-max',type=int);p.add_argument('--bedrooms-exact',type=int)
 p.add_argument('--price-min',type=int);p.add_argument('--price-max',type=int);p.add_argument('--currency',choices=CURRENCY_IDS);p.add_argument('--page',type=int,default=1)
 p=sub.add_parser('ingest');p.add_argument('html');p.add_argument('--district',required=True,choices=DISTRICTS)
 p.add_argument('--db',default='urbania.sqlite');p.add_argument('--observed-at',required=True,help='Fecha UTC ISO real de la captura HTML')
 # Importar HTML no se declara barrido completo y no modifica ausencias.
 p=sub.add_parser('sample');p.add_argument('json');p.add_argument('--db',default='urbania.sqlite')
 p=sub.add_parser('export');p.add_argument('--db',default='urbania.sqlite');p.add_argument('--out',default='urbania_actual.csv')
 args=parser.parse_args()
 if args.command=='url':
  print(Search(args.district,args.bedrooms_min,args.bedrooms_max,args.bedrooms_exact,args.price_min,args.price_max,args.currency).url(args.page))
 elif args.command=='ingest':
  datetime.fromisoformat(args.observed_at)
  search=Search(args.district);rows=parse_listing(Path(args.html).read_text(encoding='utf-8'),search)
  db=Store(args.db);run=db.start()
  try:
   print(json.dumps(db.ingest(run,search,rows,observed_at=args.observed_at),ensure_ascii=False))
   db.finish_scope(run,search,False,'Importación de una página; cobertura parcial');db.finish(run)
  except Exception:db.finish(run,'failed');raise
  finally:db.close()
 elif args.command=='sample':
  # Transcripción del DOM: se conoce la fecha de observación, no la hora; cobertura parcial.
  sample=json.loads(Path(args.json).read_text(encoding='utf-8'));search=Search.from_url(sample['query_url'])
  db=Store(args.db);run=db.start()
  try:
   print(json.dumps(db.ingest(run,search,rows_from_sample(sample,search),observed_at=sample['observed_date']),ensure_ascii=False))
   db.finish_scope(run,search,False,'Muestra transcrita del navegador; cobertura parcial');db.finish(run)
  except Exception:db.finish(run,'failed');raise
  finally:db.close()
 else:
  db=Store(args.db)
  try:print(f'{db.export(args.out)} registros exportados')
  finally:db.close()

if __name__=='__main__':main()
