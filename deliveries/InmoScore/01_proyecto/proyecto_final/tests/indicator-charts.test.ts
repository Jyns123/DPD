import assert from "node:assert/strict";
import test from "node:test";
import { catalogProportion, dailyMetricSeries, isDailyMetric, monetaryChartScale } from "../lib/indicator-charts.ts";
import { DEFAULT_ASSUMPTIONS, summarize, type AnalyticsEvent, type CatalogQuality } from "../lib/business-metrics.ts";
import { generateSimulation, SIMULATION_END } from "../lib/business-simulation.ts";
const catalog: CatalogQuality = { total: 100, withModel: 90, preciseLocation: 20, withWarnings: 70, districts: 4 };
function event(id: string, timestamp: string, extra: Partial<AnalyticsEvent> = {}): AnalyticsEvent {
  return { id, visitorId: "session-a", timestamp, type: "search", success: true, resultCount: 0, durationMs: 100, ...extra };
}
test("los 30 gráficos se separan en21diarios,3catálogo,5financieros y1instantánea", () => {
  const summary = summarize(generateSimulation(), catalog, true, DEFAULT_ASSUMPTIONS, SIMULATION_END);
  assert.equal(summary.metrics.length, 30);
  assert.equal(summary.metrics.filter(isDailyMetric).length, 21);
  assert.equal(summary.metrics.filter(metric => catalogProportion(metric.id, catalog)).length, 3);
  assert.equal(summary.metrics.filter(metric => metric.group === "Finanzas").length, 5);
  assert.equal(summary.metrics.filter(metric => metric.id === "freshness").length, 1);
});
test("una sesión en dos fechas conserva conteosdiarios sininventarhistoria delcatálogo", () => {
  const events = [event("a", "2026-11-10T15:00:00Z"), event("b", "2026-11-12T15:00:00Z"), event("c", "2026-11-12T16:00:00Z", { resultCount: 2 })];
  const series = dailyMetricSeries(events, catalog);
  assert.deepEqual(series.sessions, [{ date: "2026-11-10", value: 1 }, { date: "2026-11-12", value: 1 }]);
  assert.deepEqual(series.searches, [{ date: "2026-11-10", value: 1 }, { date: "2026-11-12", value: 2 }]);
  assert.deepEqual(series.empty, [{ date: "2026-11-10", value: 100 }, { date: "2026-11-12", value: 50 }]);
  assert.equal(series["model-coverage"], undefined);
  assert.equal(series.income, undefined);
  assert.equal(series.freshness, undefined);
});
test("una tasa sin denominador queda nula y nunca se dibuja como cero", () => {
  const series = dailyMetricSeries([event("a", "2026-11-11T15:00:00Z", { type: "page_view" })], catalog);
  assert.deepEqual(series.helpful, [{ date: "2026-11-11", value: null }]);
  assert.deepEqual(series.results, [{ date: "2026-11-11", value: null }]);
  assert.deepEqual(dailyMetricSeries([], catalog), {});
});
test("las proporciones salen del catálogo real y las finanzas registradas siguen sin datos", () => {
  assert.deepEqual(catalogProportion("location-coverage", catalog), { amount: 20, total: 100, label: "Ubicación precisa", remainder: "Aproximada o sin ubicación" });
  const real = summarize(generateSimulation(), catalog, false);
  assert(real.metrics.filter(metric => metric.group === "Finanzas").every(metric => metric.value === null));
  const simulated = summarize(generateSimulation(), catalog, true);
  const scale = monetaryChartScale(simulated.metrics);
  assert(simulated.metrics.filter(metric => metric.unit === "money").every(metric => Math.abs(metric.value ?? 0) <= scale));
});
