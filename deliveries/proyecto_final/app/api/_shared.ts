import { currentUser } from '../../lib/auth/session';

export function jsonError(status: number, error: string, message: string) {
  return Response.json({ error, message }, { status, headers: { 'Cache-Control': 'no-store' } });
}
export function mutationOriginIsSame(request: Request): boolean {
  const origin = request.headers.get('origin');
  if (!origin) return request.headers.get('sec-fetch-site') === 'same-origin';
  try {
    // Next may normalize request.url to localhost even when bound to 127.0.0.1.
    // Host is the browser's actual destination; forwarded headers are ignored.
    const destination = new URL(request.url);
    const host = request.headers.get('host');
    if (host) destination.host = host;
    return new URL(origin).origin === destination.origin;
  } catch { return false; }
}
export const authenticatedUser = currentUser;
export async function readJson(request: Request): Promise<unknown | null> {
  try {
    if (Number(request.headers.get('content-length')) > 16384) return null;
    const value = await request.text();
    return value.length <= 16384 ? JSON.parse(value) : null;
  } catch { return null; }
}
export function databaseError() { return jsonError(500, 'database_error', 'No se pudo completar la operación con la base de datos.'); }
export function parseStoredProfile(value: string | null): object | null {
  if (!value) return null;
  try { const parsed: unknown = JSON.parse(value); return parsed && typeof parsed === 'object' && !Array.isArray(parsed) ? parsed : null; } catch { return null; }
}
