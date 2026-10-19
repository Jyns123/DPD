import { randomUUID } from 'node:crypto';
import { getRepository } from '../../../../db';
import { hashPassword, normalizedEmail, tokenHash, validPassword } from '../../../../lib/auth/passwords';
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
    const repository = getRepository();
    // Loopback clients share the local server. This also bounds registration work.
    if (!await repository.takeAuthAttempt(tokenHash('register:local'), 30, 60 * 60 * 1000)) return jsonError(429, 'too_many_attempts', 'Demasiados registros. Vuelve a intentarlo más tarde.');
    const user = await repository.createUser({ id: randomUUID(), name: name.trim(), email, passwordHash: await hashPassword(password) });
    if (!user) return jsonError(409, 'email_in_use', 'Ese correo ya tiene una cuenta. Inicia sesión.');
    await startSession(user.id);
    return Response.json({ user: publicUser(user), profile: null, favorites: [] }, { status: 201, headers: { 'Cache-Control': 'no-store' } });
  } catch { return databaseError(); }
}
