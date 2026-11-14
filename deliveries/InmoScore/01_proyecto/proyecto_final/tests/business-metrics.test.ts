import assert from "node:assert/strict";
import test from "node:test";
import { boardReadings, correlation, dateInLima, DEFAULT_ASSUMPTIONS, filterEvents, metricsCsv, percentile, summarize, type AnalyticsEvent, type CatalogQuality } from "../lib/business-metrics.ts";
import { generateSimulation, SIMULATION_END } from "../lib/business-simulation.ts";
const catalog: CatalogQuality = { total: 100, withModel: 90, preciseLocation: 20, withWarnings: 70, districts: 4 };
const event = (id: string, type: AnalyticsEvent["type"], extra: Partial<AnalyticsEvent> = {}): AnalyticsEvent => ({ id, visitorId: "session-a", type, timestamp: "2026-11-11T15:00:00Z", district: "San Miguel", channel: "directo", ...extra });
const value = (events: AnalyticsEvent[], id: string, simulated = false) => summarize(events, catalog, simulated, DEFAULT_ASSUMPTIONS, SIMULATION_END).metrics.find(metric => metric.id === id)!.value;

test("la simulación es reproducible y contiene exactamente 300 sesiones ficticias", () => {
  const first = generateSimulation();
  assert.deepEqual(first, generateSimulation());
  assert.equal(new Set(first.map(item => item.visitorId)).size, 300);
  assert.equal(first.filter(item => item.type === "page_view").length, 300);
  assert.equal(new Set(first.map(item => item.id)).size, first.length);
  assert(first.every(item => item.visitorId.startsWith("sim-")));
  assert(first.every(item => item.timestamp <= SIMULATION_END));
  assert.notDeepEqual(first, generateSimulation(300, 42));
});
test("cada salida simulada tiene una ficha previa en la misma sesión", () => {
  const events = generateSimulation();
  for (const outgoing of events.filter(item => item.type === "outbound")) assert(events.some(item => item.visitorId === outgoing.visitorId && item.type === "detail" && item.timestamp < outgoing.timestamp));
});
test("la simulación rechaza tamaños inválidos y admite cero", () => {
  assert.deepEqual(generateSimulation(0), []);
  for (const count of [-1, 1.5, 10001, NaN]) assert.throws(() => generateSimulation(count));
});
test("hay 30 indicadores únicos con unidades, fórmulas y límites", () => {
  const metrics = summarize(generateSimulation(), catalog, true).metrics;
  assert.equal(metrics.length, 30);
  assert.equal(new Set(metrics.map(metric => metric.id)).size, 30);
  assert(metrics.every(metric => metric.formula && metric.note && metric.unit));
  assert.equal(metrics.filter(metric => metric.group === "Finanzas").length, 5);
});
test("el modo registrado no inventa ingreso, costos ni retorno", () => {
  const metrics = summarize(generateSimulation(), catalog, false).metrics;
  assert(metrics.filter(metric => metric.group === "Finanzas").every(metric => metric.value === null));
});
test("sin eventos los conteos son cero y tasas y latencia quedan sin datos", () => {
  assert.equal(value([], "sessions"), 0);
  for (const id of ["activation", "conversion", "results", "empty", "mean-results", "helpful", "success", "latency", "freshness"]) assert.equal(value([], id), null, id);
});
test("sesiones y salidas se deduplican por sesión, búsquedas se cuentan por evento", () => {
  const events = [event("1", "page_view"), event("2", "search", { success: true, resultCount: 2 }), event("3", "search", { success: true, resultCount: 0 }), event("4", "outbound"), event("5", "outbound")];
  assert.equal(value(events, "sessions"), 1);
  assert.equal(value(events, "searches"), 2);
  assert.equal(value(events, "referrals"), 1);
  assert.equal(value(events, "results"), 50);
  assert.equal(value(events, "mean-results"), 1);
});
test("búsqueda sin coincidencias es una operación válida, error no contamina tasa de coincidencias", () => {
  const events = [event("1", "search", { success: true, resultCount: 0 }), event("2", "search", { success: false }), event("3", "api_error")];
  assert.equal(value(events, "empty"), 100);
  assert.equal(value(events, "results"), 0);
  assert.equal(value(events, "success"), 50);
  assert.equal(value(events, "errors"), 2);
});
test("la fecha local se calcula en Lima incluso alrededor de medianoche UTC", () => {
  assert.equal(dateInLima("2026-11-11T04:59:59Z"), "2026-11-10");
  assert.equal(dateInLima("2026-11-11T05:00:00Z"), "2026-11-11");
  assert.equal(dateInLima("invalid"), "");
});
test("los filtros son inclusivos, combinables y no duplican IDs de evento", () => {
  const a = event("1", "page_view", { timestamp: "2026-11-11T04:59:59Z" });
  const b = event("2", "page_view", { timestamp: "2026-11-11T05:00:00Z" });
  const c = event("3", "page_view", { district: "Ate" });
  const filtered = filterEvents([a, b, b, c], { from: "2026-11-11", to: "2026-11-11", district: "San Miguel", channel: "directo" });
  assert.deepEqual(filtered, [b]);
});
test("la calidad del catálogo no cambia por los filtros de actividad", () => {
  const summaryA = summarize(generateSimulation(), catalog, true);
  const summaryB = summarize([], catalog, true);
  for (const id of ["model-coverage", "location-coverage", "warning-rate"]) assert.equal(summaryA.metrics.find(item => item.id === id)!.value, summaryB.metrics.find(item => item.id === id)!.value);
  assert.equal(summaryA.metrics.find(item => item.id === "model-coverage")!.value, 90);
});
test("el escenario económico usa supuestos editables y respeta costo cero", () => {
  const events = [event("1", "outbound"), event("2", "outbound", { visitorId: "session-b" })];
  const result = summarize(events, catalog, true, { referralValue: 20, marketingCost: 10, fixedCost: 5, costPerSession: 1 });
  const get = (id: string) => result.metrics.find(item => item.id === id)!.value;
  assert.equal(get("income"), 40);
  assert.equal(get("operating"), 7);
  assert.equal(get("balance"), 23);
  assert.equal(get("roi"), 100 * 23 / 17);
  const zero = summarize(events, catalog, true, { referralValue: 0, marketingCost: 0, fixedCost: 0, costPerSession: 0 });
  assert.equal(zero.metrics.find(item => item.id === "roi")!.value, null);
});
test("un saldo negativo se conserva", () => {
  const result = summarize([], catalog, true, DEFAULT_ASSUMPTIONS);
  assert.equal(result.metrics.find(item => item.id === "balance")!.value, -450);
});
test("la valoración útil usa solo respuestas recibidas, no todas las consultas", () => {
  const events = [event("1", "chat_question", { topic: "budget" }), event("2", "chat_question", { topic: "sin_respuesta" }), event("3", "chat_feedback", { helpful: true }), event("4", "chat_feedback", { helpful: false })];
  assert.equal(value(events, "helpful"), 50);
  assert.equal(value(events, "feedback"), 2);
  assert.equal(value(events, "unanswered"), 50);
});
test("el Pareto termina en 100% y ordena frecuencias", () => {
  const summary = summarize(generateSimulation(), catalog, true);
  assert.equal(summary.pareto.at(-1)!.cumulative, 100);
  summary.pareto.slice(1).forEach((row, index) => assert(row.count <= summary.pareto[index].count));
  assert.equal(summary.pareto.reduce((sum, row) => sum + row.count, 0), summary.metrics.find(item => item.id === "questions")!.value);
});
test("el mapa de calor conserva el total de eventos seleccionados", () => {
  const events = generateSimulation();
  assert.equal(summarize(events, catalog, true).heatmap.flat().reduce((sum, cell) => sum + cell.count, 0), events.length);
});
test("P95 usa rango más cercano y correlación exige variación y tres puntos", () => {
  assert.equal(percentile(Array.from({ length: 100 }, (_, index) => index + 1), .95), 95);
  assert.equal(percentile([], .95), null);
  assert.equal(correlation([1, 2, 3], [2, 4, 6]), 1);
  assert.equal(correlation([1, 2, 3], [3, 2, 1]), -1);
  assert.equal(correlation([1, 1, 1], [2, 4, 6]), null);
  assert.equal(correlation([1, 2], [2, 4]), null);
});
test("el CSV incluye fórmulas y todas las filas sin convertir vacíos en cero", () => {
  const csv = metricsCsv(summarize([], catalog, false).metrics);
  assert.equal(csv.split("\r\n").length, 31);
  assert(csv.includes('"Finanzas","Ingreso hipotético","","money"'));
  assert(csv.includes("Fórmula"));
});

test("las agregaciones diarias respetan sesiones repetidas y medianoche en Lima", () => {
  const events = [
    event("1", "search", { timestamp: "2026-11-11T04:59:00Z", resultCount: 0, success: true, durationMs: 100 }),
    event("2", "search", { timestamp: "2026-11-11T05:01:00Z", resultCount: 3, success: true, durationMs: 300 }),
    event("3", "outbound", { timestamp: "2026-11-11T05:02:00Z" }),
    event("4", "outbound", { timestamp: "2026-11-11T05:03:00Z" }),
    event("5", "api_error", { timestamp: "2026-11-11T05:04:00Z" }),
  ];
  const result = summarize(events, catalog, false);
  assert.equal(result.metrics.find(metric => metric.id === "sessions")!.value, 1);
  assert.deepEqual(result.daily, [
    { date: "2026-11-10", sessions: 1, searches: 1, referrals: 0, errors: 0, latency: 100 },
    { date: "2026-11-11", sessions: 1, searches: 1, referrals: 1, errors: 1, latency: 300 },
  ]);
  assert.deepEqual(result.districts, [{ name: "San Miguel", sessions: 1, referrals: 1, rate: 100 }]);
});
test("20 mil eventos conservan conteos y el mapa de calor sin multiplicar sesiones", () => {
  const events = Array.from({ length: 20000 }, (_, index) => event(String(index), index % 4 === 0 ? "outbound" : "page_view", { visitorId: `session-${index % 300}`, timestamp: new Date(Date.UTC(2026, 8, 1 + index % 60, 12)).toISOString() }));
  const result = summarize(events, catalog, false);
  assert.equal(result.metrics.find(metric => metric.id === "events")!.value, 20000);
  assert.equal(result.metrics.find(metric => metric.id === "sessions")!.value, 300);
  assert.equal(result.metrics.find(metric => metric.id === "referrals")!.value, 75);
  assert.equal(result.heatmap.flat().reduce((sum, cell) => sum + cell.count, 0), 20000);
  assert.equal(result.daily.length, 60);
});
test("las lecturas distinguen evidencia seleccionada y alcance del catálogo", () => {
  const summary = summarize([
    event("1", "search", { success: true, resultCount: 0 }),
    event("2", "search", { success: true, resultCount: 2 }),
    event("3", "chat_question", { topic: "budget" }),
  ], catalog, false);
  const readings = boardReadings(summary, catalog);
  assert.equal(readings.length, 3);
  assert.match(readings[0].observation, /50% de 2/);
  assert.match(readings[1].observation, /Tope de compra.*1 consulta de 1/);
  assert.equal(readings[2].scope, "Catálogo completo");
  assert.match(readings[2].observation, /20 de 100/);
  assert(readings.every(reading => reading.nextStep));
});
test("sin actividad no se generan observaciones falsas de búsquedas o consultas", () => {
  const emptyCatalog: CatalogQuality = { total: 0, withModel: 0, preciseLocation: 0, withWarnings: 0, districts: 0 };
  assert.deepEqual(boardReadings(summarize([], emptyCatalog, false), emptyCatalog), []);
  assert.deepEqual(boardReadings(summarize([], catalog, false), catalog).map(reading => reading.id), ["location-limit"]);
});
test("CSV contextual conserva fuente, selección y supuestos sin mezclar finanzas reales", () => {
  const filters = { from: "2026-11-01", to: "2026-11-11", district: "Ate", channel: "directo" };
  const metrics = summarize([], catalog, false).metrics;
  const real = metricsCsv(metrics, { source: "live", filters, assumptions: DEFAULT_ASSUMPTIONS });
  assert.equal(real.split("\r\n").length, 31);
  assert(real.includes('"Actividad registrada","2026-11-01","2026-11-11","Ate","directo","","","",""'));
  const simulation = metricsCsv(metrics, { source: "simulation", filters, assumptions: DEFAULT_ASSUMPTIONS });
  assert(simulation.includes('"Simulación ficticia","2026-11-01","2026-11-11","Ate","directo","25","300","150","0.2"'));
});
test("correlación descarta entradas no numéricas en lugar de mostrar NaN", () => {
  assert.equal(correlation([1, NaN, 3], [1, 2, 3]), null);
  assert.equal(correlation([1, 2, 3], [1, Infinity, 3]), null);
});
