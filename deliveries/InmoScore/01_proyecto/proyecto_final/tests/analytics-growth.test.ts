import test from 'node:test';
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { canReadAnalytics } from '../lib/analytics-access.ts';
import { AnalyticsStore } from '../db/analytics.ts';

test('un Host local no concede acceso si el servidor no se inició en loopback',()=>{
  const request=new Request('http://localhost/api/analytics',{headers:{host:'localhost'}});
  assert.equal(canReadAnalytics(request,{}),false);
  assert.equal(canReadAnalytics(request,{localOnly:false}),false);
  assert.equal(canReadAnalytics(request,{localOnly:true}),true);
});
test('la clave se exige también localmente y una autorización ajena se rechaza',()=>{
  const request=(token:string)=>new Request('http://localhost/api/analytics',{headers:{'x-analytics-token':token}});
  assert.equal(canReadAnalytics(request(''),{localOnly:true,token:'test-admin-token'}),false);
  assert.equal(canReadAnalytics(request('incorrect-token'),{localOnly:true,token:'test-admin-token'}),false);
  assert.equal(canReadAnalytics(request('test-admin-token'),{token:'test-admin-token'}),true);
});
test('la revisión de eventos permanece estable y cambia al insertar o limpiar',()=>{
  const dir=mkdtempSync(join(tmpdir(),'inmoscore-revision-'));
  const store=new AnalyticsStore(join(dir,'events.sqlite'));
  try {
    const empty=store.revision();
    const row={id:randomUUID(),visitorId:randomUUID(),type:'page_view' as const};
    store.record(row);
    const active=store.revision();assert.notEqual(active,empty);
    assert.equal(store.revision(),active);
    store.record(row);assert.equal(store.revision(),active);
    store.record({...row,id:randomUUID()},new Date(Date.now()-91*86400000));
    assert.equal(store.revision(),active);
  } finally {store.close();rmSync(dir,{recursive:true,force:true});}
});
