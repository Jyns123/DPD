import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import { readLimitedJson } from '../lib/http-body.ts';
import { parseStoredProfile } from '../lib/stored-profile.ts';
import { hashPassword, verifyPassword, MAX_PASSWORD_WORK, PasswordWorkBusyError } from '../lib/auth/passwords.ts';
import { SqliteRepository } from '../db/sqlite.ts';

function streamRequest(chunks: Uint8Array[], headers?: Record<string, string>, onCancel?: () => void) {
  let offset = 0;
  const body = new ReadableStream<Uint8Array>({
    pull(controller) { if (offset < chunks.length) controller.enqueue(chunks[offset++]); else controller.close(); },
    cancel() { onCancel?.(); },
  });
  return new Request('http://localhost/api/test', { method: 'POST', body, headers, duplex: 'half' } as RequestInit & { duplex: string });
}
const encode = (text: string) => new TextEncoder().encode(text);

test('JSON se lee por fragmentos y respeta el límite real de bytes', async () => {
  assert.deepEqual(await readLimitedJson(streamRequest([encode('{"name":'), encode('"María"}')]), 100), { name: 'María' });
  // "é" ocupa cuatro bytes, aunque su representación JSON tenga tres caracteres.
  assert.equal(await readLimitedJson(streamRequest([encode('"é"')]), 3), null);
  assert.equal(await readLimitedJson(streamRequest([encode('{"x":"'), encode('a'.repeat(1000))], { 'content-length': '2' }), 16), null);
});

test('cuerpo declarado excesivo y UTF-8 inválido se rechazan', async () => {
  assert.equal(await readLimitedJson(streamRequest([encode('{}')], { 'content-length': '9999999' })), null);
  assert.equal(await readLimitedJson(streamRequest([new Uint8Array([0x7b, 0xff, 0x7d])])), null);
  assert.equal(await readLimitedJson(streamRequest([encode('{incompleto')])), null);
});

test('un cuerpo que no termina se cancela al vencer la lectura', async () => {
  let cancelled = false;
  const body = new ReadableStream<Uint8Array>({ cancel() { cancelled = true; } });
  const request = new Request('http://localhost', { method: 'POST', body, duplex: 'half' } as RequestInit & { duplex: string });
  assert.equal(await readLimitedJson(request, 100, 25), null);
  assert.equal(cancelled, true);
});

test('los perfiles guardados se revalidan y se descartan esquemas incompletos', () => {
  const profile = { income: 8500, savings: 100000, budget: 550000, minRooms: 2, minArea: 55,
    districts: ['Ate'], weights: { price: .55, safety: .2, convenience: .25 } };
  assert.deepEqual(parseStoredProfile(JSON.stringify(profile)), profile);
  for (const value of [null, '{', '[]', '{"budget":20}', JSON.stringify({ ...profile, weights: { price: 0, safety: 0, convenience: 0 } })]) {
    assert.equal(parseStoredProfile(value), null);
  }
});

test('la criptografía limita trabajo simultáneo y libera los cupos al terminar', async () => {
  const password = 'Una clave de demostración 2026';
  const pending = Array.from({ length: MAX_PASSWORD_WORK }, () => hashPassword(password));
  await assert.rejects(hashPassword(password), PasswordWorkBusyError);
  const hashes = await Promise.all(pending);
  assert.equal(await verifyPassword(password, hashes[0]), true);
  assert.equal(await verifyPassword('otra clave demostrativa', hashes[0]), false);
});

test('la migración de índices conserva la cuenta de una base versión uno', async () => {
  const folder = mkdtempSync(join(tmpdir(), 'inmoscore-migration-'));
  const path = join(folder, 'accounts.sqlite');
  const original = new DatabaseSync(path);
  original.exec(readFileSync(new URL('../db/migrations/sqlite/001-initial.sql', import.meta.url), 'utf8'));
  original.prepare('INSERT INTO users(id,email,name,password_hash) VALUES (?,?,?,?)').run('demo', 'demo@example.test', 'Perfil de prueba', 'fixture-hash');
  original.close();
  const repository = new SqliteRepository(path);
  try {
    assert.equal((await repository.findUserByEmail('demo@example.test'))?.name, 'Perfil de prueba');
    const inspect = new DatabaseSync(path, { readOnly: true });
    try {
      assert.equal(Number(inspect.prepare('PRAGMA user_version').get()?.user_version), 2);
      const names = inspect.prepare("SELECT name FROM sqlite_master WHERE type='index'").all().map(row => row.name);
      assert.ok(names.includes('sessions_expiry_idx')); assert.ok(names.includes('auth_attempts_expiry_idx'));
    } finally { inspect.close(); }
  } finally { repository.close(); rmSync(folder, { recursive: true, force: true, maxRetries: 5, retryDelay: 100 }); }
});

test('el límite de intentos se reinicia sin esperar a la limpieza periódica', async (context) => {
  let now = 1_000_000;
  context.mock.method(Date, 'now', () => now);
  const folder = mkdtempSync(join(tmpdir(), 'inmoscore-attempts-'));
  const repository = new SqliteRepository(join(folder, 'accounts.sqlite'));
  try {
    assert.equal(await repository.takeAuthAttempt('fixture', 2, 1000), true);
    assert.equal(await repository.takeAuthAttempt('fixture', 2, 1000), true);
    assert.equal(await repository.takeAuthAttempt('fixture', 2, 1000), false);
    now += 1001;
    assert.equal(await repository.takeAuthAttempt('fixture', 2, 1000), true);
  } finally { repository.close(); rmSync(folder, { recursive: true, force: true, maxRetries: 5, retryDelay: 100 }); }
});
