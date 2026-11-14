import test from "node:test";
import assert from "node:assert/strict";
import { businessVisuals } from "../lib/business-visuals.ts";
import { generateSimulation } from "../lib/business-simulation.ts";
import type { AnalyticsEvent } from "../lib/business-metrics.ts";

function event(id: string, visitorId: string, type: AnalyticsEvent["type"], minute: number, extra: Partial<AnalyticsEvent> = {}): AnalyticsEvent {
  return { id, visitorId, type, timestamp: new Date(Date.UTC(2026, 10, 11, 15, minute)).toISOString(), channel: "directo", district: "Miraflores", ...extra };
}

test("the sequential funnel does not count actions out of order", () => {
  const result = businessVisuals([
    event("1", "a", "page_view", 0), event("2", "a", "detail", 1),
    event("3", "a", "search", 2), event("4", "a", "outbound", 3),
    event("5", "b", "page_view", 0), event("6", "b", "search", 1),
    event("7", "b", "detail", 2), event("8", "b", "outbound", 3),
  ]);
  assert.deepEqual(result.journey.map(row => row.count), [2, 2, 1, 1]);
  assert.equal(result.channelActions[0].total, 2);
  assert.equal(result.channelActions[0].Salida, 2);
});

test("search outcome and latency charts preserve missing measurements", () => {
  const result = businessVisuals([
    event("1", "a", "search", 0, { success: true, resultCount: 4, durationMs: 120 }),
    event("2", "a", "search", 1, { success: true, resultCount: 0, durationMs: 500 }),
    event("3", "b", "search", 0, { success: false }),
    event("4", "c", "search", 0, { success: true, durationMs: 2300 }),
  ]);
  assert.deepEqual(result.searchOutcomes.map(row => row.value), [1, 1, 1, 1]);
  assert.deepEqual(result.latencies.map(row => row.count), [1, 0, 1, 0, 1]);
  assert.equal(result.searchesWithoutDuration, 1);
});

test("simulation totals agree across journey, channels and search outcomes", () => {
  const source = generateSimulation();
  const result = businessVisuals(source);
  assert.equal(result.journey[0].count, 300);
  assert.equal(result.channelActions.reduce((sum, row) => sum + row.total, 0), 300);
  assert.equal(result.searchOutcomes.reduce((sum, row) => sum + row.value, 0), source.filter(item => item.type === "search").length);
  assert.ok(result.journey.every((row, index) => !index || row.count <= result.journey[index - 1].count));
});
