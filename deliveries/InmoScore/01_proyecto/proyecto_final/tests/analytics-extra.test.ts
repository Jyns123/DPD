import test from 'node:test';
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import { AnalyticsStore } from '../db/analytics.ts';
import { parseEvent } from '../lib/analytics-validation.ts';
import { dateInLima, filterEvents, summarize, type AnalyticsEvent } from '../lib/business-metrics.ts';
import { setAnalyticsConsent, trackInteraction, trackPageView } from '../lib/track-interaction.ts';

const catalog = { total: 6332, withModel: 6313, preciseLocation: 133, withWarnings: 5000, districts: 20 };
const baseEvent = (): AnalyticsEvent => ({ id: randomUUID(), visitorId: randomUUID(), type: 'page_view', timestamp: '2026-11-11T12:00:00Z' });

test('los errores instrumentados llegan con categorías cerradas, sin texto ni arrays', () => {
  const base = { id: randomUUID(), visitorId: randomUUID(), type: 'api_error' };
  for (const topic of ['districts', 'detail', 'favorite']) assert.ok(parseEvent({ ...base, topic }, []));
  for (const topic of [['detail'], { value: 'detail' }, 'mensaje libre', null]) {
    assert.equal(parseEvent({ ...base, topic }, []), null);
  }
  assert.equal(parseEvent({ ...base, message: 'Una consulta privada' }, []), null);
});

test('consultar el tablero elimina físicamente eventos vencidos aunque no haya escrituras nuevas', () => {
  const folder = mkdtempSync(join(tmpdir(), 'inmoscore-retention-'));
  const path = join(folder, 'events.sqlite');
  const store = new AnalyticsStore(path);
  try {
    const old = new Date(Date.now() - 91 * 86400000);
    store.record({ id: randomUUID(), visitorId: randomUUID(), type: 'page_view' }, old);
    assert.equal(store.list().length, 0);
    const inspect = new DatabaseSync(path, { readOnly: true });
    try { assert.equal(Number(inspect.prepare('SELECT COUNT(*) AS n FROM events').get()?.n), 0); }
    finally { inspect.close(); }
  } finally { store.close(); rmSync(folder, { recursive: true, force: true }); }
});

test('la tasa de búsquedas usa el mismo universo de éxitos y fallas', () => {
  const events: AnalyticsEvent[] = [
    { ...baseEvent(), type: 'search', success: true, resultCount: 9, durationMs: 100 },
    { ...baseEvent(), type: 'search', success: true, resultCount: 0, durationMs: 120 },
    { ...baseEvent(), type: 'search', success: false, durationMs: 150 },
    { ...baseEvent(), type: 'api_error', topic: 'detail' },
  ];
  const metrics = summarize(events, catalog, false).metrics;
  assert.equal(metrics.find(metric => metric.id === 'success')?.value, 200 / 3);
  assert.equal(metrics.find(metric => metric.id === 'errors')?.value, 2);
});

test('la actividad registrada nunca se presenta como facturación', () => {
  const events: AnalyticsEvent[] = [{ ...baseEvent(), type: 'outbound' }];
  const real = summarize(events, catalog, false).metrics;
  const simulated = summarize(events, catalog, true).metrics;
  for (const metric of real.filter(item => item.group === 'Finanzas')) assert.equal(metric.value, null);
  assert.equal(simulated.find(metric => metric.id === 'income')?.value, 25);
  assert.equal(real.find(metric => metric.id === 'referrals')?.value, 1);
});

test('el límite de fechas usa el día de Lima y no corta a medianoche UTC', () => {
  assert.equal(dateInLima('2026-11-12T04:59:59Z'), '2026-11-11');
  assert.equal(dateInLima('2026-11-12T05:00:00Z'), '2026-11-12');
  const before = { ...baseEvent(), timestamp: '2026-11-12T04:59:59Z' };
  const after = { ...baseEvent(), timestamp: '2026-11-12T05:00:00Z' };
  const selected = filterEvents([before, after], { from: '2026-11-11', to: '2026-11-11', district: '', channel: '' });
  assert.deepEqual(selected.map(event => event.id), [before.id]);
});

test('el registro requiere consentimiento y no duplica la misma navegación', () => {
  const names = ['window', 'localStorage', 'sessionStorage', 'fetch'] as const;
  const descriptors = new Map(names.map(name => [name, Object.getOwnPropertyDescriptor(globalThis, name)]));
  const makeStorage = () => {
    const values = new Map<string, string>();
    return { getItem: (key: string) => values.get(key) ?? null, setItem: (key: string, value: string) => values.set(key, value), removeItem: (key: string) => values.delete(key) };
  };
  const location = { pathname: '/' };
  const calls: Record<string, unknown>[] = [];
  const mocks = {
    window: { location, dispatchEvent: () => true }, localStorage: makeStorage(), sessionStorage: makeStorage(),
    fetch: async (_input: RequestInfo | URL, init?: RequestInit) => { calls.push(JSON.parse(String(init?.body))); return new Response('{}'); },
  };
  for (const name of names) Object.defineProperty(globalThis, name, { configurable: true, writable: true, value: mocks[name] });
  try {
    setAnalyticsConsent(false);
    trackInteraction('page_view');
    assert.equal(calls.length, 0);
    setAnalyticsConsent(true);
    trackPageView(); trackPageView();
    assert.equal(calls.length, 1);
    location.pathname = '/explorar'; trackPageView();
    assert.equal(calls.length, 2);
    location.pathname = '/tablero'; trackPageView();
    assert.equal(calls.length, 2);
    setAnalyticsConsent(false);
    location.pathname = '/perfil'; trackPageView();
    assert.equal(calls.length, 2);
  } finally {
    setAnalyticsConsent(false);
    for (const name of names) {
      const original = descriptors.get(name);
      if (original) Object.defineProperty(globalThis, name, original);
      else Reflect.deleteProperty(globalThis, name);
    }
  }
});
