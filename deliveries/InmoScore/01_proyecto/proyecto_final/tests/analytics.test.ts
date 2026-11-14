import test from 'node:test';
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { AnalyticsStore } from '../db/analytics.ts';
import { parseEvent, localAnalyticsRequest, type EventInput } from '../lib/analytics-validation.ts';

function event(): EventInput { return {id:randomUUID(),visitorId:randomUUID(),type:'search',success:true,resultCount:9,durationMs:320}; }
test('eventos excluyen texto privado y campos no previstos',()=>{
  const row=event(); assert.deepEqual(parseEvent(row,[]),row);
  for (const extra of [{email:'x@example.test'},{income:5000},{question:'texto privado'},{timestamp:'2040-01-01'},{channel:'campana'}]) assert.equal(parseEvent({...row,...extra},[]),null);
  assert.equal(parseEvent({...row,durationMs:NaN},[]),null);
  assert.equal(parseEvent({...row,resultCount:-1},[]),null);
  assert.equal(parseEvent({...row,visitorId:'correo-personal'},[]),null);
  assert.equal(parseEvent({...row,district:'inventado'},['Ate']),null);
  assert.equal(parseEvent({...row,topic:'correo'},[]),null);
  assert.ok(parseEvent({id:randomUUID(),visitorId:randomUUID(),type:'api_error',topic:'favorite'},[]));
  assert.equal(parseEvent({id:randomUUID(),visitorId:randomUUID(),type:'chat_question',topic:'favorite'},[]),null);
});
test('lectura local no acepta host externo',()=>{
  assert.equal(localAnalyticsRequest(new Request('http://127.0.0.1:5173/api/analytics')),true);
  assert.equal(localAnalyticsRequest(new Request('http://localhost/api/analytics',{headers:{host:'example.test'}})),false);
  assert.equal(localAnalyticsRequest(new Request('https://example.test/api/analytics',{headers:{host:'localhost'}})),false);
});
test('persistencia separada, deduplicación, límite y conservación',()=>{
  const dir=mkdtempSync(join(tmpdir(),'inmoscore-analytics-')); const file=join(dir,'events.sqlite');
  let store=new AnalyticsStore(file);
  try {
    const row=event(); const now=new Date();
    assert.equal(store.record(row,now),'saved'); assert.equal(store.record(row,now),'duplicate');
    assert.equal(store.list().length,1);
    store.close(); store=new AnalyticsStore(file);
    assert.equal(store.list()[0].visitorId,row.visitorId);
    for(let i=1;i<100;i++)store.record({...row,id:randomUUID()},now);
    assert.equal(store.record({...row,id:randomUUID()},now),'limited');
    store.record(event(),new Date(now.getTime()+91*86400000));
    assert.equal(store.list().length,1);
  } finally {store.close();rmSync(dir,{recursive:true,force:true});}
});
