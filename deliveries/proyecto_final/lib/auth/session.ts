import { cookies } from 'next/headers';
import { getRepository } from '../../db';
import { sessionToken, tokenHash } from './passwords';
import type { UserRecord } from '../../db/repository';

export const COOKIE_NAME = 'inmoscore_session';
const SESSION_SECONDS = 60 * 60 * 24 * 7;
const cookieOptions = () => ({ httpOnly: true, sameSite: 'lax' as const, path: '/', secure: process.env.SESSION_COOKIE_SECURE === 'true' });
export async function currentUser(): Promise<UserRecord | null> {
  const token = (await cookies()).get(COOKIE_NAME)?.value;
  if (!token || !/^[A-Za-z0-9_-]{43}$/.test(token)) return null;
  return getRepository().findSessionUser(tokenHash(token), Date.now());
}
export async function startSession(userId: string) {
  const jar = await cookies();
  const previous = jar.get(COOKIE_NAME)?.value;
  if (previous) await getRepository().deleteSession(tokenHash(previous));
  const token = sessionToken();
  await getRepository().createSession(tokenHash(token), userId, Date.now() + SESSION_SECONDS * 1000);
  jar.set(COOKIE_NAME, token, { ...cookieOptions(), maxAge: SESSION_SECONDS });
}
export async function endSession() {
  const jar = await cookies();
  const token = jar.get(COOKIE_NAME)?.value;
  if (token) await getRepository().deleteSession(tokenHash(token));
  jar.set(COOKIE_NAME, '', { ...cookieOptions(), maxAge: 0 });
}
export function publicUser(user: UserRecord) { return { id: user.id, name: user.name, email: user.email }; }
