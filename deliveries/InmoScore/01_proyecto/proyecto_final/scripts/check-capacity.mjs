// Prueba local reproducible. Solicitudes concurrentes no equivalen a usuarios reales.
import {readFileSync,mkdirSync,writeFileSync} from 'node:fs';
import {performance} from 'node:perf_hooks';
const base=process.env.TEST_BASE_URL || 'http://127.0.0.1:5173';
if(!['127.0.0.1','localhost'].includes(new URL(base).hostname))throw new Error('Esta prueba solo admite un servidor local de demostración.');
const total=Number(process.env.LOAD_REQUESTS || 1000);
const concurrency=Number(process.env.LOAD_CONCURRENCY || 25);
if(!Number.isInteger(total)||total<1||total>5000||!Number.isInteger(concurrency)||concurrency<1||concurrency>50)throw new Error('Usa de1a5000 solicitudes y de1a50 conexiones.');
const profiles=JSON.parse(readFileSync('data/demo_profiles.json','utf8')).map(profile=>{
  const values={...profile};delete values.name;return values;
});
const measurements=[];const errors=[];const statuses={};
async function call(index,record) {
  const start=performance.now();
  try {
    const response=await fetch(base+'/api/ranking',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({profile:profiles[index%profiles.length],limit:24}),signal:AbortSignal.timeout(15000)});
    const data=await response.json();
    if(record)statuses[response.status]=(statuses[response.status]||0)+1;
    if(!response.ok)throw new Error(`HTTP ${response.status}`);
    if(!Array.isArray(data.listings) || !data.listings.length || typeof data.effectiveBudget!=='number')throw new Error('La respuesta no contiene el ranking esperado.');
  } catch(error) {if(record)errors.push({request:index,message:String(error.message)});else throw error;}
  finally {if(record)measurements.push(performance.now()-start);}
}
for(let i=0;i<10;i++)await call(i,false);
let cursor=0;const start=performance.now();
await Promise.all(Array.from({length:concurrency},async()=>{while(cursor<total){const current=cursor++;await call(current,true);}}));
const elapsed=performance.now()-start;measurements.sort((a,b)=>a-b);
const percentile=q=>Number(measurements[Math.max(0,Math.ceil(q*measurements.length)-1)].toFixed(2));
const report={testedAt:new Date().toISOString(),base,totalRequests:total,maxConcurrentRequests:concurrency,durationSeconds:Number((elapsed/1000).toFixed(2)),requestsPerSecond:Number((total*1000/elapsed).toFixed(2)),latencyMs:{p50:percentile(.5),p95:percentile(.95),p99:percentile(.99),max:measurements.at(-1)},errors:errors.length,statuses,errorExamples:errors.slice(0,5),scope:'API de ranking en un equipo local, perfiles ficticios incluidos. No mide navegador, internet, escrituras, usuarios únicos ni capacidad de producción.'};
mkdirSync('tests/results',{recursive:true});
const name=process.env.LOAD_LABEL==='before'?'capacity-before.json':'capacity-after.json';
writeFileSync('tests/results/'+name,JSON.stringify(report,null,2));
console.log(JSON.stringify(report,null,2));
if(errors.length)process.exitCode=1;
