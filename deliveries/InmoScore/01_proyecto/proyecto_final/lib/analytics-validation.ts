export const EVENT_TYPES = ['page_view', 'search', 'detail', 'favorite', 'compare', 'outbound', 'chat_question', 'chat_feedback', 'support_message', 'api_error'] as const;
export const HELP_TOPICS = ['start', 'budget', 'ranking', 'no_results', 'model', 'quality', 'map', 'favorites', 'compare', 'privacy', 'sin_respuesta'] as const;
const OPERATION_TOPICS = ['districts','detail','favorite'];
const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
export type EventInput = {
  id: string; visitorId: string; type: typeof EVENT_TYPES[number];
  district?: string; resultCount?: number; durationMs?: number;
  success?: boolean; helpful?: boolean; topic?: string; listingId?: string;
};

// Solo se admite información necesaria para medir uso. Nombres, correos,
// presupuesto y texto del chat no tienen lugar en este registro.
export function parseEvent(value: unknown, districts: string[]): EventInput | null {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return null;
  const row = value as Record<string, unknown>;
  const allowed = new Set(['id','visitorId','type','district','resultCount','durationMs','success','helpful','topic','listingId']);
  if (Object.keys(row).some(key => !allowed.has(key))) return null;
  if (typeof row.id !== 'string' || !uuid.test(row.id) || typeof row.visitorId !== 'string' || !uuid.test(row.visitorId)) return null;
  if (!EVENT_TYPES.includes(row.type as typeof EVENT_TYPES[number])) return null;
  if (row.district !== undefined && (typeof row.district !== 'string' || !districts.includes(row.district))) return null;
  if (row.topic !== undefined && (typeof row.topic !== 'string' || !(row.type === 'api_error' ? OPERATION_TOPICS.includes(row.topic) : HELP_TOPICS.includes(row.topic as typeof HELP_TOPICS[number])))) return null;
  if (row.listingId !== undefined && (typeof row.listingId !== 'string' || !/^[a-zA-Z0-9_-]{1,50}$/.test(row.listingId))) return null;
  for (const key of ['success','helpful']) if (row[key] !== undefined && typeof row[key] !== 'boolean') return null;
  for (const [key, max] of [['resultCount',100000],['durationMs',120000]] as const) {
    if (row[key] !== undefined && (typeof row[key] !== 'number' || !Number.isFinite(row[key]) || row[key] < 0 || row[key] > max)) return null;
  }
  if(row.resultCount !== undefined && !Number.isInteger(row.resultCount)) return null;
  if (row.type === 'search' && (typeof row.success !== 'boolean' || typeof row.durationMs !== 'number' || (row.success && typeof row.resultCount !== 'number'))) return null;
  if (row.type === 'chat_feedback' && typeof row.helpful !== 'boolean') return null;
  return row as EventInput;
}

export function localAnalyticsRequest(request: Request) {
  const url = new URL(request.url);
  const loopback = (hostname: string) => ['localhost','127.0.0.1','[::1]'].includes(hostname);
  try { return loopback(url.hostname) && loopback(new URL(`${url.protocol}//${request.headers.get('host') || url.host}`).hostname); }
  catch { return false; }
}
