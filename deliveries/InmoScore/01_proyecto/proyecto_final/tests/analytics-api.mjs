import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { mkdirSync, writeFileSync } from 'node:fs';
const base=process.env.TEST_BASE_URL || 'http://127.0.0.1:5173';
if(!['localhost','127.0.0.1'].includes(new URL(base).hostname))throw new Error('Usa un servidor local de prueba.');
const checks=[];
const visitorId=randomUUID();
const event={id:randomUUID(),visitorId,type:'search',success:true,resultCount:9,durationMs:420};
async function post(body,origin=base){return fetch(base+'/api/analytics',{method:'POST',headers:{Origin:origin,'Content-Type':'application/json'},body:JSON.stringify(body)});}
async function check(name,action){await action();checks.push(name);}
await check('evento consentido sintético se guarda',async()=>assert.equal((await post(event)).status,201));
await check('reenvío no duplica evento',async()=>assert.equal((await post(event)).status,200));
await check('origen externo rechazado',async()=>assert.equal((await post({...event,id:randomUUID()},'https://example.test')).status,403));
await check('texto libre privado rechazado',async()=>assert.equal((await post({...event,id:randomUUID(),question:'No almacenar esto'})).status,400));
await check('importe personal rechazado',async()=>assert.equal((await post({...event,id:randomUUID(),income:5000})).status,400));
await check('fecha del cliente no altera periodo real',async()=>assert.equal((await post({...event,id:randomUUID(),timestamp:'2030-01-01'})).status,400));
await check('evento falso no autorizado',async()=>assert.equal((await post({...event,id:randomUUID(),type:'sale'})).status,400));
await check('favorito recibe el distrito de su aviso',async()=>{
  const id=randomUUID();
  assert.equal((await post({id,visitorId:randomUUID(),type:'favorite',listingId:'149756570'})).status,201);
  const data=await (await fetch(base+'/api/analytics')).json();
  assert.equal(data.events.find(row=>row.id===id).district,'San Martin De Porres');
});
await check('aviso inexistente no genera métricas',async()=>assert.equal((await post({id:randomUUID(),visitorId:randomUUID(),type:'detail',listingId:'inexistente'})).status,400));
await check('lectura local reconcilia evento y catálogo',async()=>{
  const response=await fetch(base+'/api/analytics');assert.equal(response.status,200);
  assert.match(response.headers.get('cache-control'),/no-store/);
  const data=await response.json();const own=data.events.filter(row=>row.visitorId===visitorId);
  assert.equal(own.length,1);assert.equal(own[0].resultCount,9);assert.ok(own[0].timestamp);
  assert.equal(own[0].channel,undefined,'No atribuir un canal sin evidencia');
  assert.equal(data.catalog.total,6332);assert.equal(data.catalog.preciseLocation,133);
  assert.equal(data.retention.maxEvents,20000);assert.equal(data.retention.days,90);
});
mkdirSync('tests/results',{recursive:true});
writeFileSync('tests/results/analytics-api.json',JSON.stringify({status:'passed',executedAt:new Date().toISOString(),checks:checks.length,results:checks,note:'Solo eventos sintéticos en base desechable de pruebas.'},null,2));
console.log(`${checks.length} comprobaciones de analítica aprobadas.`);
