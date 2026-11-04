"""Actualización periódica: recorre sin filtros los distritos del catálogo con un solo cliente HTTP.
Respeta robots y 10 s entre solicitudes; ante 403/429/verificación detiene toda la ejecución, sin bypass."""
import argparse
import fcntl
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from capture import Client, capture
from urbania_phase1 import DISTRICTS, Search, Store

# robots.txt (consultado el 20-10-2026) permite page=2..5 y excluye las páginas siguientes.
MAX_PAGES=5
EXIT_CODES={'ok':0,'skipped':0,'error':1,'blocked':2}

def update(db_path='urbania.sqlite',districts=None,max_pages=MAX_PAGES,evidence_dir='captures',out='urbania_actual.csv',client=None):
 with open(db_path+'.lock','w') as lock:
  # Un único proceso por base: si otra actualización la está usando, esta no hace nada.
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:return {'status':'skipped','reason':'Otra actualización usa la misma base'}
  client=client or Client();started=datetime.now(timezone.utc);results=[]
  for district in districts or list(DISTRICTS):
   # Tras un bloqueo no se consulta nada más: los distritos pendientes quedan sin evidencia.
   if client.stopped:results.append({'district':district,'complete':False,'reason':'Omitido: el sitio bloqueó la ejecución','error':None});continue
   results.append({'district':district,**capture(Search(district),db_path,max_pages,client,evidence_dir)})
  exported=0
  if out:
   db=Store(db_path)
   try:exported=db.export(out+'.tmp')
   finally:db.close()
   # Reemplazo atómico: quien lea el CSV nunca ve un archivo a medio escribir.
   if exported:os.replace(out+'.tmp',out)
  status='blocked' if client.stopped else 'error' if any(r['error'] for r in results) else 'ok'
  summary={'started_at':started.isoformat(),'finished_at':datetime.now(timezone.utc).isoformat(),'status':status,
   'complete_districts':sum(r['complete'] for r in results),'districts':len(results),'exported':exported,'results':results}
  folder=Path(evidence_dir)/'updates';folder.mkdir(parents=True,exist_ok=True)
  (folder/f'{started:%Y%m%dT%H%M%SZ}.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
  return summary

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--db',default='urbania.sqlite');p.add_argument('--district',action='append',choices=DISTRICTS,help='Repetible; por defecto, todo el catálogo')
 p.add_argument('--max-pages',type=int,default=MAX_PAGES);p.add_argument('--evidence-dir',default='captures')
 p.add_argument('--out',default='urbania_actual.csv',help="CSV que se regenera al terminar; '' para no exportar")
 a=p.parse_args()
 if a.max_pages<1:raise SystemExit('--max-pages debe ser positivo')
 summary=update(a.db,a.district,a.max_pages,a.evidence_dir,a.out)
 print(json.dumps(summary,ensure_ascii=False))
 raise SystemExit(EXIT_CODES[summary['status']])

if __name__=='__main__':main()
