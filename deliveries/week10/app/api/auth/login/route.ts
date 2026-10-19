import { getRepository } from '../../../../db';
import { DUMMY_PASSWORD_HASH, normalizedEmail, tokenHash, validPassword, verifyPassword } from '../../../../lib/auth/passwords';
import { startSession, publicUser } from '../../../../lib/auth/session';
import { databaseError, jsonError, mutationOriginIsSame, parseStoredProfile, readJson } from '../../_shared';

export const runtime = 'nodejs';
export async function POST(request: Request) {
  if (!mutationOriginIsSame(request)) return jsonError(403, 'forbidden_origin', 'La solicitud debe venir del mismo sitio.');
  const payload = await readJson(request);
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) return jsonError(400, 'invalid_credentials', 'Revisa tu correo y contraseña.');
  const { email: rawEmail, password } = payload as Record<string, unknown>;
  const email = normalizedEmail(rawEmail);
  if (!email || !validPassword(password)) return jsonError(400, 'invalid_credentials', 'Revisa tu correo y contraseña.');
  try {
    const repository = getRepository();
    const attemptKey = tokenHash('login:' + email);
    if (!await repository.takeAuthAttempt(attemptKey, 10, 15 * 60 * 1000)) return jsonError(429, 'too_many_attempts', 'Demasiados intentos. Espera 15 minutos e inténtalo de nuevo.');
    const user = await repository.findUserByEmail(email);
    const valid = await verifyPassword(password, user?.passwordHash || DUMMY_PASSWORD_HASH);
    if (!user || !valid) return jsonError(401, 'invalid_credentials', 'Correo o contraseña incorrectos.');
    await repository.clearAuthAttempts(attemptKey);
    await startSession(user.id);
    return Response.json({ user: publicUser(user), profile: parseStoredProfile(user.profileJson), favorites: await repository.listFavorites(user.id) }, { headers: { 'Cache-Control': 'no-store' } });
  } catch { return databaseError(); }
}
