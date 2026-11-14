import { randomUUID } from 'node:crypto';
import { getRepository } from '../../../../db';
import { hashPassword, normalizedEmail, tokenHash, validPassword, passwordWorkAvailable, PasswordWorkBusyError } from '../../../../lib/auth/passwords';
import { startSession, publicUser } from '../../../../lib/auth/session';
import { jsonError, mutationOriginIsSame, readJson, databaseError } from '../../_shared';

export const runtime = 'nodejs';
export async function POST(request: Request) {
  if (!mutationOriginIsSame(request)) return jsonError(403, 'forbidden_origin', 'La solicitud debe venir del mismo sitio.');
  const payload = await readJson(request);
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) return jsonError(400, 'invalid_credentials', 'Revisa los datos de tu cuenta.');
  const { name, email: rawEmail, password } = payload as Record<string, unknown>;
  const email = normalizedEmail(rawEmail);
  if (!email || !validPassword(password) || typeof name !== 'string' || !name.trim() || name.trim().length > 120)
    return jsonError(400, 'invalid_credentials', 'Ingresa nombre, correo válido y una contraseña de 10 a 128 caracteres.');
  try {
    if (!passwordWorkAvailable()) throw new PasswordWorkBusyError();
    const repository = getRepository();
    // Un grupo que crea sus cuentas no debe agotar un cupo global de toda la hora.
    if (!await repository.takeAuthAttempt(tokenHash('register:' + email), 5, 15 * 60 * 1000)) return jsonError(429, 'too_many_attempts', 'Se intentó registrar este correo varias veces. Espera 15 minutos o inicia sesión.');
    if (!await repository.takeAuthAttempt(tokenHash('register:burst'), 60, 60 * 1000)) return Response.json({ error: 'too_many_attempts', message: 'Hay muchos registros en este momento. Espera un minuto e inténtalo de nuevo.' }, { status: 429, headers: { 'Cache-Control': 'no-store', 'Retry-After': '60' } });
    const user = await repository.createUser({ id: randomUUID(), name: name.trim(), email, passwordHash: await hashPassword(password) });
    if (!user) return jsonError(409, 'email_in_use', 'Ese correo ya tiene una cuenta. Inicia sesión.');
    await startSession(user.id);
    return Response.json({ user: publicUser(user), profile: null, favorites: [] }, { status: 201, headers: { 'Cache-Control': 'no-store' } });
  } catch (error) { return databaseError(error); }
}
