// Integración local con eventos ficticios. Usar una base desechable de demostración.
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { mkdirSync, writeFileSync } from 'node:fs';

const base = process.env.TEST_BASE_URL || 'http://127.0.0.1:5173';
const address = new URL(base);
if (!['localhost', '127.0.0.1', '[::1]'].includes(address.hostname) ||
    address.protocol !== 'http:' || address.username || address.password ||
    address.pathname !== '/' || address.search || address.hash) {
  throw new Error('Usa la dirección HTTP de un servidor local con una base de prueba desechable.');
}
const origin = address.origin;
const token = process.env.TEST_ANALYTICS_TOKEN || '';
const checks = [];
const zeroHeatmap = () => Array.from({ length: 7 }, () => Array(6).fill(0));
const sample = {
  mode: 'sim',
  daily: [
    { date: '2026-11-10', searches: 3, referrals: 1 },
    { date: '2026-11-11', searches: 7, referrals: 2 },
  ],
  heatmap: zeroHeatmap(),
};
sample.heatmap[1][2] = 4;
sample.heatmap[2][3] = 9;

function authHeaders() {
  return token ? { 'X-Analytics-Token': token } : {};
}
function post(path, body, requestOrigin = origin) {
  return fetch(origin + path, {
    method: 'POST',
    headers: { Origin: requestOrigin, 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(15_000),
  });
}
async function readAnalytics() {
  const response = await fetch(origin + '/api/analytics', {
    headers: authHeaders(), cache: 'no-store', signal: AbortSignal.timeout(15_000),
  });
  assert.equal(response.status, 200, 'La lectura local de analítica debe estar autorizada.');
  const data = await response.json();
  assert.ok(Array.isArray(data.events));
  return data.events;
}
function assertSvg(svg) {
  assert.equal(typeof svg, 'string');
  assert.match(svg, /^<svg\s[^>]*xmlns=["']http:\/\/www\.w3\.org\/2000\/svg["']/);
  assert.match(svg, /<\/svg>\s*$/);
  assert.doesNotMatch(svg, /<script\b|<foreignObject\b|\bon\w+\s*=|javascript:/i);
}
async function chartsFor(body) {
  const response = await post('/api/bi-chart', body);
  assert.equal(response.status, 200, `No se generó el gráfico: HTTP ${response.status}.`);
  assert.match(response.headers.get('cache-control'), /no-store/);
  const charts = await response.json();
  assertSvg(charts.trend);
  assertSvg(charts.heatmap);
  return charts;
}
async function check(name, run) {
  await run();
  checks.push(name);
}

// Reproduce la agregación existente: fechas de Lima, búsqueda por evento,
// salidas únicas por sesión y día, y todos los eventos para el mapa de calor.
function chartInput(events) {
  const days = new Map();
  const seen = new Set();
  const heatmap = zeroHeatmap();
  for (const event of events) {
    if (seen.has(event.id)) continue;
    const timestamp = Date.parse(event.timestamp);
    assert.ok(Number.isFinite(timestamp), 'La fecha registrada debe ser válida.');
    seen.add(event.id);
    const lima = new Date(timestamp - 5 * 60 * 60 * 1000);
    const date = lima.toISOString().slice(0, 10);
    const day = days.get(date) || { searches: 0, referrals: new Set() };
    if (event.type === 'search') day.searches++;
    if (event.type === 'outbound') day.referrals.add(event.visitorId);
    days.set(date, day);
    heatmap[(lima.getUTCDay() + 6) % 7][Math.floor(lima.getUTCHours() / 4)]++;
  }
  return {
    mode: 'live',
    daily: [...days.entries()].sort(([left], [right]) => left.localeCompare(right))
      .map(([date, day]) => ({ date, searches: day.searches, referrals: day.referrals.size })),
    heatmap,
  };
}

let originalCharts;
await check('Python devuelve dos SVG completos y privados', async () => {
  originalCharts = await chartsFor(sample);
});
await check('la misma selección produce gráficos estables', async () => {
  assert.deepEqual(await chartsFor(sample), originalCharts);
});
await check('una selección vacía genera una respuesta válida sin datos inventados', async () => {
  await chartsFor({ mode: 'sim', daily: [], heatmap: zeroHeatmap() });
});

const invalid = [
  ['modo desconocido', { ...sample, mode: 'private' }],
  ['serie diaria con forma incorrecta', { ...sample, daily: {} }],
  ['mapa de calor con seis días', { ...sample, heatmap: zeroHeatmap().slice(0, 6) }],
  ['mapa de calor con cinco franjas', { ...sample, heatmap: zeroHeatmap().map(row => row.slice(0, 5)) }],
  ['conteo negativo', { ...sample, daily: [{ date: '2026-11-10', searches: -1, referrals: 0 }] }],
  ['conteo fraccionario', { ...sample, heatmap: zeroHeatmap().map((row, index) => index ? row : [0.5, 0, 0, 0, 0, 0]) }],
  ['fecha inexistente', { ...sample, daily: [{ date: '2026-02-30', searches: 1, referrals: 0 }] }],
  ['fecha fuera de formato', { ...sample, daily: [{ date: '2026-11-10T00:00:00Z', searches: 1, referrals: 0 }] }],
  ['fechas duplicadas', { ...sample, daily: [sample.daily[0], sample.daily[0]] }],
  ['fechas desordenadas', { ...sample, daily: [...sample.daily].reverse() }],
  ['periodo superior al límite', { ...sample, daily: [{ date: '2026-01-01', searches: 0, referrals: 0 }, { date: '2026-11-11', searches: 1, referrals: 0 }] }],
];
for (const [label, payload] of invalid) {
  await check(`se rechaza ${label}`, async () => {
    assert.equal((await post('/api/bi-chart', payload)).status, 400);
  });
}
await check('un origen externo no puede generar gráficos', async () => {
  assert.equal((await post('/api/bi-chart', sample, 'https://example.test')).status, 403);
});

await check('Python puede devolver un lote de treinta indicadores con huecos y valores negativos', async () => {
  const charts = Array.from({ length: 30 }, (_, index) => ({
    id: `indicador-${index}`, kind: 'daily', values: [1, null, index + 2],
  }));
  charts[28] = { id: 'saldo', kind: 'signed', values: [-42] };
  charts[29] = { id: 'cobertura', kind: 'level', values: [84], max: 100 };
  const response = await post('/api/bi-indicators', { mode: 'sim', charts });
  assert.equal(response.status, 200);
  const { charts: rendered } = await response.json();
  assert.deepEqual(Object.keys(rendered), charts.map(chart => chart.id));
  assert.ok(Object.values(rendered).every(svg => svg.startsWith('<svg ') && svg.endsWith('</svg>')));
  assert.match(rendered.saldo, /#ad5541/);
});

await check('el lote rechaza identificadores duplicados', async () => {
  const entry = { id: 'repetido', kind: 'daily', values: [1, 2] };
  assert.equal((await post('/api/bi-indicators', { mode: 'sim', charts: [entry, entry] })).status, 400);
});

await check('una búsqueda registrada actualiza la tendencia y el mapa de Python', async () => {
  const beforeEvents = await readAnalytics();
  const beforeInput = chartInput(beforeEvents);
  const beforeCharts = await chartsFor(beforeInput);
  // Este evento simula la acción que envía el cliente tras aceptar las métricas.
  // La API recibe solo acciones anónimas; el consentimiento se controla en la web.
  const event = {
    id: randomUUID(), visitorId: randomUUID(), type: 'search',
    success: true, resultCount: 9, durationMs: 123,
  };
  assert.equal((await post('/api/analytics', event)).status, 201);
  const afterEvents = await readAnalytics();
  assert.equal(afterEvents.filter(row => row.id === event.id).length, 1);
  const afterInput = chartInput(afterEvents);
  assert.ok(afterInput.daily.reduce((sum, row) => sum + row.searches, 0) >
    beforeInput.daily.reduce((sum, row) => sum + row.searches, 0));
  assert.ok(afterInput.heatmap.flat().reduce((sum, count) => sum + count, 0) >
    beforeInput.heatmap.flat().reduce((sum, count) => sum + count, 0));
  const afterCharts = await chartsFor(afterInput);
  assert.notEqual(afterCharts.trend, beforeCharts.trend, 'La tendencia debe cambiar al agregarse la búsqueda.');
  assert.notEqual(afterCharts.heatmap, beforeCharts.heatmap, 'El mapa de calor debe cambiar al agregarse la búsqueda.');
  assert.deepEqual(await chartsFor(afterInput), afterCharts, 'El nuevo resultado también debe permanecer estable.');
});

mkdirSync('tests/results', { recursive: true });
writeFileSync('tests/results/bi-chart-api.json', JSON.stringify({
  executedAt: new Date().toISOString(), base: origin, status: 'passed',
  checks: checks.length, results: checks,
  scope: 'Generación de SVG por API local y actualización tras una búsqueda ficticia persistida. Sin usuarios reales ni prueba de carga. El evento sintético queda en la base desechable.',
}, null, 2));
console.log(`${checks.length} comprobaciones de gráficos Python aprobadas.`);
