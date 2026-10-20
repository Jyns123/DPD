"""Captura HTTP acotada: sin evasión de controles. No activa ninguna tarea periódica."""
import argparse
import json
import re
import time
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
import requests
from bs4 import BeautifulSoup
from urbania_phase1 import BASE, Search, Store, CaptureStopped, ParseError, is_main, parse_listing, utcnow

AGENT='UrbaniaResearchComparator/1.0'
class Robots:
 def __init__(self,body):
  groups=[];agents=[];rules=[]
  for raw in body.splitlines()+['User-agent: __end__']:
   line=raw.split('#',1)[0].strip()
   if ':' not in line:continue
   k,v=[x.strip() for x in line.split(':',1)];k=k.lower()
   if k=='user-agent':
    if rules:groups.append((agents,rules));agents=[];rules=[]
    agents.append(v.lower())
   elif k in {'allow','disallow'} and agents and v:rules.append((k=='allow',v))
  specific=[(a,r) for a,r in groups if any(x!='*' and x in AGENT.lower() for x in a)]
  if specific:
   longest=max(len(x) for a,_ in specific for x in a if x!='*' and x in AGENT.lower())
   selected=[r for a,r in specific if any(len(x)==longest and x in AGENT.lower() for x in a)]
  else:selected=[r for a,r in groups if '*' in a]
  self.rules=[v for r in selected for v in r]
 def allows(self,url):
  u=urlsplit(url);target=u.path+('?' + u.query if u.query else '');hits=[]
  for allow,rule in self.rules:
   pattern='^'+re.escape(rule).replace(r'\*','.*')
   if rule.endswith('$'):pattern=pattern[:-2]+'$'
   if re.search(pattern,target):hits.append((len(rule.replace('*','').rstrip('$')),allow))
  return max(hits)[1] if hits else True

class Client:
 def __init__(self,interval=10,session=None):
  self.session=session or requests.Session();self.session.headers.update({'User-Agent':AGENT})
  self.interval=max(10,interval);self.last=0;self.stopped=False;self.robots=None
 def _request(self,url):
  if self.stopped:raise CaptureStopped('Cliente detenido')
  time.sleep(max(0,self.interval-(time.monotonic()-self.last)));self.last=time.monotonic()
  r=self.session.get(url,timeout=30,allow_redirects=False)
  if r.status_code in {401,403,429}:self.stopped=True;raise CaptureStopped(f'HTTP {r.status_code}; no reintentar ni marcar avisos retirados')
  if r.status_code!=200:raise CaptureStopped(f'HTTP {r.status_code}; cobertura incompleta')
  return r
 def fetch(self,url):
  parts=urlsplit(url)
  if parts.hostname!='urbania.pe' or not parts.path.startswith('/buscar/venta-de-departamentos'):
   raise ValueError('Solo listados de venta de departamentos')
  if self.robots is None:
   response=self._request(BASE+'/robots.txt');self.robots=Robots(response.text)
  if not self.robots.allows(url):raise CaptureStopped('Ruta excluida por robots.txt; cobertura incompleta')
  r=self._request(url)
  if 'html' not in r.headers.get('content-type','').lower():raise ParseError('Respuesta no HTML')
  if any(x in r.text[:200000].lower() for x in ['cf-chl-','just a moment...','verify you are human','error code: 1010']):
   self.stopped=True;raise CaptureStopped('Respuesta de verificación')
  return r.text,utcnow()

def continuation(html,search,page,main_count):
 soup=BeautifulSoup(html,'lxml');higher=[]
 for a in soup.select('a[href]'):
  label=a.get_text(strip=True)
  if label.isdigit() and urlsplit(a['href']).path==urlsplit(search.url()).path:
   if int(label)>page:higher.append(int(label))
 if higher:return min(higher),False
 # Ausencia de paginación no basta para asumir que un listado quedó completo.
 h=soup.find('h1');m=re.match(r'\s*([\d.,]+)\s+Departamentos',h.get_text(' ',strip=True) if h else '',re.I)
 expected=int(re.sub(r'\D','',m[1])) if m else None
 # Para una única página se verifica el recuento. En páginas finales >1, el
 # recuento global se valida al terminar el barrido mediante IDs únicos.
 return None,(expected is not None)

def capture(search,db_path='urbania.sqlite',max_pages=5,client=None,evidence_dir='captures'):
 client=client or Client();db=Store(db_path);run=db.start();events=[];fingerprints=set();ids=set();page=1;complete=False;reason='Límite de páginas';expected=None;error=None
 totals={'new':0,'changed':0,'unchanged':0,'excluded':0}
 folder=Path(evidence_dir)/str(run);folder.mkdir(parents=True,exist_ok=True)
 try:
  for index in range(max_pages):
   url=search.url(page);html,observed=client.fetch(url)
   (folder/f'page_{page}.html').write_text(html,encoding='utf-8')
   rows=parse_listing(html,search);main=[r for r in rows if is_main(r)]
   fp=tuple(sorted(r['posting_id'] for r in main))
   if fp in fingerprints:reason='Página repetida';break
   fingerprints.add(fp);ids.update(fp)
   h=BeautifulSoup(html,'lxml').find('h1');m=re.match(r'\s*([\d.,]+)\s+Departamentos',h.get_text(' ',strip=True) if h else '',re.I)
   current_expected=int(re.sub(r'\D','',m[1])) if m else None
   if expected is None:expected=current_expected
   elif current_expected!=expected:reason='Recuento cambió durante barrido';expected=-1
   stats=db.ingest(run,search,rows,observed_at=observed)
   for key in totals:totals[key]+=stats[key]
   events.append({'url':url,'observed_at':observed,'main_cards':len(main),'stats':stats})
   next_page,has_count=continuation(html,search,page,len(main))
   if next_page is None:
    complete=has_count and expected is not None and expected>=0 and len(ids)==expected
    reason='Recuento y final de paginación verificados' if complete else 'Cobertura sin reconciliar con recuento'
    break
   page=next_page
 except (requests.RequestException,CaptureStopped,ParseError) as exc:
  reason=str(exc);complete=False;error=type(exc).__name__
 finally:
  db.finish_scope(run,search,complete,reason);db.finish(run,'finished' if complete else 'partial');db.close()
  (folder/'run.json').write_text(json.dumps({'run_id':run,'search_url':search.url(),'complete':complete,'reason':reason,'error':error,'stats':totals,'events':events},ensure_ascii=False,indent=2))
 return {'run_id':run,'complete':complete,'reason':reason,'error':error,'unique_ids':len(ids),'pages':len(events),'stats':totals}

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--district',required=True);p.add_argument('--db',default='urbania.sqlite');p.add_argument('--max-pages',type=int,default=5)
 p.add_argument('--bedrooms-exact',type=int);p.add_argument('--bedrooms-min',type=int);p.add_argument('--bedrooms-max',type=int);p.add_argument('--price-min',type=int);p.add_argument('--price-max',type=int);p.add_argument('--currency',choices=['PEN','USD'])
 a=p.parse_args()
 if a.max_pages<1:raise SystemExit('--max-pages debe ser positivo')
 s=Search(a.district,a.bedrooms_min,a.bedrooms_max,a.bedrooms_exact,a.price_min,a.price_max,a.currency)
 print(json.dumps(capture(s,a.db,a.max_pages),ensure_ascii=False))
