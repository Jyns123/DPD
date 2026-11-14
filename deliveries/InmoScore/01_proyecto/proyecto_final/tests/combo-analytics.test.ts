import test from "node:test";
import assert from "node:assert/strict";
import { comboAnalytics, districtDrilldown } from "../lib/combo-analytics.ts";
import { filterEvents, summarize, type AnalyticsEvent, type CatalogQuality } from "../lib/business-metrics.ts";
import { generateSimulation } from "../lib/business-simulation.ts";

const catalog: CatalogQuality = { total: 0, withModel: 0, preciseLocation: 0, withWarnings: 0, districts: 0 };
function event(id: string, visitorId: string, type: AnalyticsEvent["type"], minute: number, extra: Partial<AnalyticsEvent> = {}): AnalyticsEvent {
  return { id, visitorId, type, timestamp: new Date(Date.UTC(2026, 10, 11, 15, minute)).toISOString(), district: "Miraflores", channel: "directo", ...extra };
}

test("combined charts retain separate count, rate and time denominators", () => {
  const events = [
    event("1", "a", "page_view", 0),
    event("2", "a", "search", 1, { success: true, resultCount: 5, durationMs: 100 }),
    event("3", "a", "outbound", 2),
    event("4", "b", "search", 3, { success: true, resultCount: 0, durationMs: 300 }),
    event("5", "c", "search", 4, { success: false, durationMs: 600 }),
    event("6", "d", "search", 5, { success: true }),
  ];
  const summary = summarize(events, catalog, true);
  const result = comboAnalytics(events, summary.daily, summary.districts);
  assert.equal(result.activity[0].searches, 4);
  assert.equal(result.activity[0].sessions, 4);
  assert.equal(result.activity[0].outboundRate, 25);
  assert.deepEqual(result.quality.map(row => [row.withResults, row.empty, row.failed, row.unmeasured, row.measured, row.p95]), [[1, 1, 1, 1, 3, 600]]);
  assert.equal(result.channels[0].total, 4);
  assert.equal(result.channels[0].Salida, 1);
  assert.equal(result.channels[0].outboundRate, 25);
  assert.equal(result.districts[0].outboundRate, 25);
  assert.deepEqual(districtDrilldown(events, "Miraflores").map(row => [row.sessions, row.searches, row.outbound, row.outboundRate]), [[4, 4, 1, 25]]);
});

test("support rate uses only votes received for the same topic", () => {
  const events = [
    event("1", "a", "chat_question", 0, { topic: "model" }),
    event("2", "a", "chat_feedback", 1, { topic: "model", helpful: true }),
    event("3", "b", "chat_question", 2, { topic: "model" }),
    event("4", "b", "chat_feedback", 3, { topic: "model", helpful: false }),
    event("5", "c", "chat_question", 4, { topic: "budget" }),
  ];
  const summary = summarize(events, catalog, true);
  const support = comboAnalytics(events, summary.daily, summary.districts).support;
  assert.deepEqual(support.map(row => [row.key, row.questions, row.votes, row.helpfulRate]), [["model", 2, 2, 50], ["budget", 1, 0, null]]);
});

test("filtered simulation recomputes combinations without importing unrelated districts", () => {
  const events = filterEvents(generateSimulation(), { from: "", to: "", district: "Miraflores", channel: "" });
  const summary = summarize(events, catalog, true);
  const result = comboAnalytics(events, summary.daily, summary.districts);
  assert.equal(result.quality.reduce((total, row) => total + row.withResults + row.empty + row.failed + row.unmeasured, 0), events.filter(item => item.type === "search").length);
  assert.equal(result.channels.reduce((total, row) => total + row.total, 0), new Set(events.map(item => item.visitorId)).size);
  assert.deepEqual(result.districts.map(row => row.name), ["Miraflores"]);
  assert.equal(districtDrilldown(events, "Miraflores").reduce((total, row) => total + row.searches, 0), events.filter(item => item.type === "search").length);
});
