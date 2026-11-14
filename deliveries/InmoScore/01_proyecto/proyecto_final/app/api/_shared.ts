import { currentUser } from '../../lib/auth/session';
import { PasswordWorkBusyError } from '../../lib/auth/passwords';
import { readLimitedJson } from '../../lib/http-body';
export { parseStoredProfile } from '../../lib/stored-profile';

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
export const readJson = readLimitedJson;
export function databaseError(error?: unknown) {
  if (error instanceof PasswordWorkBusyError) {
    return Response.json({ error: 'authentication_busy', message: 'Estamos atendiendo varios ingresos. Espera unos segundos y vuelve a intentarlo.' },
      { status: 503, headers: { 'Cache-Control': 'no-store', 'Retry-After': '3' } });
  }
  return jsonError(500, 'database_error', 'No se pudo completar la operación con la base de datos.');
}
