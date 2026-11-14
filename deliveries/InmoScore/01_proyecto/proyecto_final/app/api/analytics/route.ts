import { createHash } from 'node:crypto';
import { AnalyticsStore, MAX_EVENTS } from '../../../db/analytics';
import { getDistricts, getListings, getListing } from '../../../lib/catalog';
import { parseEvent } from '../../../lib/analytics-validation';
import { canReadAnalytics } from '../../../lib/analytics-access';
import { jsonError, mutationOriginIsSame, readJson } from '../_shared';
export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

let lastListings: ReturnType<typeof getListings> | undefined;
let lastSummary: { total: number; withModel: number; preciseLocation: number; withWarnings: number; districts: number; capturedAt?: string };
function catalogSummary() {
  const listings = getListings();
  if (listings !== lastListings) {
    let withModel=0, preciseLocation=0, withWarnings=0, capturedAt: string | undefined;
    for (const row of listings) {
      if (row.predictedPrice !== null && row.predictedPrice > 0) withModel++;
      if (row.location && ['calle','exacta'].includes(row.location.precision)) preciseLocation++;
      if (row.flags.length > 0) withWarnings++;
      if (row.observedAt && (!capturedAt || row.observedAt > capturedAt)) capturedAt=row.observedAt;
    }
    lastSummary={total:listings.length,withModel,preciseLocation,withWarnings,districts:getDistricts().length,capturedAt};
    lastListings=listings;
  }
  return lastSummary;
}
export async function GET(request: Request) {
  if (!canReadAnalytics(request,{token:process.env.ANALYTICS_ADMIN_TOKEN,localOnly:process.env.ANALYTICS_LOCAL_ONLY==='1'})) return jsonError(403,'private_dashboard','El tablero real requiere una clave de administración fuera de la demostración local.');
  let store: AnalyticsStore | undefined;
  try {
    store = new AnalyticsStore();
    const catalog = catalogSummary();
    const etag = '"'+createHash('sha256').update(store.revision()+JSON.stringify(catalog)).digest('hex')+'"';
    const headers={'Cache-Control':'no-store','ETag':etag,'Vary':'x-analytics-token'};
    if (request.headers.get('if-none-match') === etag) return new Response(null,{status:304,headers});
    return Response.json({events:store.list(),catalog,updatedAt:new Date().toISOString(),retention:{days:90,maxEvents:MAX_EVENTS}}, {headers});
  } catch { return jsonError(500,'analytics_unavailable','No se pudo leer el tablero. Reintenta en un momento.'); }
  finally { store?.close(); }
}
export async function POST(request: Request) {
  if (!mutationOriginIsSame(request)) return jsonError(403,'invalid_origin','La interacción debe originarse en esta aplicación.');
  const input = parseEvent(await readJson(request),getDistricts());
  if (!input) return jsonError(400,'invalid_event','La interacción no tiene el formato esperado.');
  if(input.listingId) {
    const listing=getListing(input.listingId);
    if(!listing)return jsonError(400,'unknown_listing','El aviso asociado no existe en el catálogo.');
    // El distrito se obtiene del catálogo, incluido al guardar un favorito.
    input.district=listing.district;
  }
  let store: AnalyticsStore | undefined;
  try {
    store = new AnalyticsStore();
    const status = store.record(input);
    if(status==='limited') return jsonError(429,'event_limit','Espera un momento antes de registrar más interacciones.');
    return Response.json({status},{status:status==='saved'?201:200,headers:{'Cache-Control':'no-store'}});
  } catch { return jsonError(500,'analytics_unavailable','No se pudo registrar esta interacción.'); }
  finally { store?.close(); }
}
