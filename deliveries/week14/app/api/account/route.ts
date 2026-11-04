import { getRepository } from '../../../db';
import { endSession } from '../../../lib/auth/session';
import { validPassword, verifyPassword, tokenHash } from '../../../lib/auth/passwords';
import { authenticatedUser, databaseError, jsonError, mutationOriginIsSame, readJson } from '../_shared';
export async function DELETE(request: Request) {
  if (!mutationOriginIsSame(request)) return jsonError(403, 'forbidden_origin', 'La solicitud debe venir del mismo sitio.');
  try {
    const user = await authenticatedUser();
    if (!user) return jsonError(401, 'unauthorized', 'Inicia sesión para eliminar tu cuenta.');
    const payload = await readJson(request);
    const password = payload && typeof payload === 'object' ? (payload as Record<string, unknown>).password : null;
    if (!await getRepository().takeAuthAttempt(tokenHash('delete:' + user.id), 10, 15 * 60 * 1000)) return jsonError(429, 'too_many_attempts', 'Demasiados intentos. Espera 15 minutos.');
    if (!validPassword(password) || !await verifyPassword(password, user.passwordHash)) return jsonError(403, 'invalid_password', 'Confirma la contraseña de tu cuenta.');
    await getRepository().deleteAccount(user.id);
    await endSession();
    return Response.json({ deleted: true }, { headers: { 'Cache-Control': 'no-store' } });
  } catch { return databaseError(); }
}
