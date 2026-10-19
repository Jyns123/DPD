import test from 'node:test';
import assert from 'node:assert/strict';
import { hashPassword, verifyPassword, validPassword, normalizedEmail, sessionToken, tokenHash } from '../lib/auth/passwords.ts';

test('scrypt uses a unique random salt and verifies only the correct password', async () => {
 const password = 'Una frase de prueba 2026';
 const one = await hashPassword(password), two = await hashPassword(password);
 assert.notEqual(one, two); assert.ok(one.startsWith('scrypt$32768$8$3$'));
 assert.ok(!one.includes(password)); assert.equal(await verifyPassword(password,one),true);
 assert.equal(await verifyPassword('otra frase de prueba',one),false);
 assert.equal(await verifyPassword(password,'malformed'),false);
});
test('password hashing preserves Unicode and intentional whitespace', async () => {
 const password = '  Casa nueva 🏠 2026  ';
 const hashed = await hashPassword(password);
 assert.equal(await verifyPassword(password,hashed),true);
 assert.equal(await verifyPassword(password.trim(),hashed),false);
});
test('sessions use random opaque tokens and store only their digest', () => {
 const first = sessionToken(), second = sessionToken();
 assert.match(first,/^[A-Za-z0-9_-]{43}$/); assert.notEqual(first,second);
 assert.match(tokenHash(first),/^[0-9a-f]{64}$/); assert.notEqual(tokenHash(first),first);
});
test('credential bounds and normalized email reject invalid input', () => {
 assert.equal(normalizedEmail('  Demo@Example.Test '),'demo@example.test');
 assert.equal(normalizedEmail('correo invalido'),null);
 assert.equal(validPassword('short'),false); assert.equal(validPassword('x'.repeat(129)),false);
 assert.equal(validPassword('x'.repeat(10)),true);
});
