import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';

const base = process.env.TEST_BASE_URL || 'http://127.0.0.1:5173';
if (!['localhost', '127.0.0.1'].includes(new URL(base).hostname)) throw new Error('Usa un servidor local de demostración.');
const checks = [];
const post = (path, body) => fetch(base + path, { method: 'POST', headers: { 'Content-Type': 'application/json', Origin: base }, body: JSON.stringify(body) });
async function check(name, run) { await run(); checks.push(name); }

await check('un cuerpo excesivo se rechaza y el servidor sigue disponible', async () => {
  assert.equal((await post('/api/ranking', { text: 'x'.repeat(100000) })).status, 400);
  assert.equal((await fetch(base + '/api/health')).status, 200);
});
await check('el límite también se aplica cuando no llega Content-Length', async () => {
  const body = new ReadableStream({ start(controller) { controller.enqueue(new TextEncoder().encode('{"x":"' + 'x'.repeat(50000) + '"}')); controller.close(); } });
  const response = await fetch(base + '/api/ranking', { method: 'POST', duplex: 'half', body, headers: { Origin: base, 'Content-Type': 'application/json' } });
  assert.equal(response.status, 400);
});
await check('la respuesta de recomendaciones personales no se almacena en caché', async () => {
  const profiles = JSON.parse(readFileSync('data/demo_profiles.json', 'utf8'));
  const response = await post('/api/ranking', { profile: profiles[0] });
  assert.equal(response.status, 200);
  assert.match(response.headers.get('cache-control'), /private.*no-store/);
  const data = await response.json(); assert.equal(data.matchedTotal, 180); assert.equal(data.cap, 390676);
});
await check('una ráfaga de ingresos recibe reintento controlado sin cola criptográfica ilimitada', async () => {
  // Calienta la ruta sin verificar ninguna contraseña ni crear una cuenta.
  await post('/api/auth/login', {});
  const outcomes = await Promise.all(Array.from({ length: 8 }, () => post('/api/auth/login', {
    email: `control-${randomUUID()}@example.test`, password: 'Clave de prueba sin cuenta 2026',
  })));
  assert.ok(outcomes.every(response => response.status === 401 || response.status === 503));
  const busy = outcomes.filter(response => response.status === 503);
  assert.ok(busy.length > 0, 'La ráfaga debe superar los dos trabajos de contraseña simultáneos.');
  for (const response of busy) assert.equal(response.headers.get('retry-after'), '3');
});
mkdirSync('tests/results', { recursive: true });
writeFileSync('tests/results/backend-hardening-api.json', JSON.stringify({ executedAt: new Date().toISOString(), status: 'passed', checks: checks.length, results: checks,
  scope: 'Pruebas funcionales locales con intentos ficticios; no es una prueba de miles de usuarios ni se crean cuentas.' }, null, 2));
console.log(`${checks.length} comprobaciones de protección del backend aprobadas.`);
