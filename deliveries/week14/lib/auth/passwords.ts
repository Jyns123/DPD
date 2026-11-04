import { randomBytes, scrypt, timingSafeEqual, createHash } from 'node:crypto';

const COST = { N: 32768, r: 8, p: 3, maxmem: 64 * 1024 * 1024 };
export const DUMMY_PASSWORD_HASH = 'scrypt$32768$8$3$' + '0'.repeat(32) + '$' + '0'.repeat(128);
function derive(password: string, salt: Buffer): Promise<Buffer> {
  return new Promise((resolve, reject) => scrypt(password, salt, 64, COST, (error, key) => error ? reject(error) : resolve(key)));
}
export async function hashPassword(password: string): Promise<string> {
  const salt = randomBytes(16);
  const key = await derive(password, salt);
  return ['scrypt', COST.N, COST.r, COST.p, salt.toString('hex'), key.toString('hex')].join('$');
}
export async function verifyPassword(password: string, encoded: string): Promise<boolean> {
  const parts = encoded.split('$');
  if (parts.length !== 6 || parts.slice(0,4).join('$') !== 'scrypt$32768$8$3' || !/^[0-9a-f]{32}$/.test(parts[4]) || !/^[0-9a-f]{128}$/.test(parts[5])) return false;
  const key = await derive(password, Buffer.from(parts[4], 'hex'));
  return timingSafeEqual(key, Buffer.from(parts[5], 'hex'));
}
export function sessionToken() { return randomBytes(32).toString('base64url'); }
export function tokenHash(token: string) { return createHash('sha256').update(token).digest('hex'); }
export function validPassword(value: unknown): value is string { return typeof value === 'string' && value.length >= 10 && value.length <= 128; }
export function normalizedEmail(value: unknown): string | null {
  if (typeof value !== 'string') return null;
  const email = value.trim().toLowerCase();
  return email.length <= 254 && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) ? email : null;
}
