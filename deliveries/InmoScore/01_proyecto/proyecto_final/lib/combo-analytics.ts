import {
  CHANNEL_LABELS, TOPIC_LABELS, dateInLima, percentile, ratio,
  type AnalyticsEvent, type DailyRow, type BreakdownRow,
} from "./business-metrics.ts";
import { businessVisuals } from "./business-visuals.ts";

/** Lecturas descriptivas de los eventos que ya pasó el filtro del tablero. */
export function comboAnalytics(events: AnalyticsEvent[], daily: DailyRow[], districts: BreakdownRow[]) {
  const qualityByDay = new Map<string, {
    withResults: number; empty: number; failed: number; unmeasured: number; durations: number[];
  }>();
  const topicByName = new Map<string, { questions: number; positive: number; votes: number }>();

  for (const event of events) {
    if (event.type === "search") {
      const day = dateInLima(event.timestamp);
      if (!day) continue;
      const row = qualityByDay.get(day) ?? { withResults: 0, empty: 0, failed: 0, unmeasured: 0, durations: [] };
      if (event.success === false) row.failed++;
      else if (typeof event.resultCount === "number" && event.resultCount > 0) row.withResults++;
      else if (event.resultCount === 0) row.empty++;
      else row.unmeasured++;
      if (typeof event.durationMs === "number" && Number.isFinite(event.durationMs) && event.durationMs >= 0) row.durations.push(event.durationMs);
      qualityByDay.set(day, row);
    }
    if (event.type === "chat_question" || event.type === "chat_feedback") {
      const key = event.topic || "sin_categoria";
      const row = topicByName.get(key) ?? { questions: 0, positive: 0, votes: 0 };
      if (event.type === "chat_question") row.questions++;
      else if (typeof event.helpful === "boolean") {
        row.votes++;
        if (event.helpful) row.positive++;
      }
      topicByName.set(key, row);
    }
  }

  const activity = daily.map(day => ({
    date: day.date,
    searches: day.searches,
    sessions: day.sessions,
    referrals: day.referrals,
    outboundRate: ratio(day.referrals, day.sessions),
  }));
  const quality = [...qualityByDay].sort(([a], [b]) => a.localeCompare(b)).map(([date, row]) => ({
    date,
    withResults: row.withResults,
    empty: row.empty,
    failed: row.failed,
    unmeasured: row.unmeasured,
    measured: row.durations.length,
    p95: percentile(row.durations, .95),
  }));
  const channels = businessVisuals(events).channelActions.map(row => ({
    ...row,
    outboundRate: ratio(row["Salida"], row.total),
  }));
  const districtRows = districts.slice(0, 8).map(row => ({
    ...row,
    label: row.name,
    outboundRate: row.rate,
  }));
  const support = [...topicByName].filter(([, row]) => row.questions > 0)
    .map(([key, row]) => ({
      key, name: TOPIC_LABELS[key] || (key === "sin_categoria" ? "Sin categoría" : key),
      questions: row.questions, votes: row.votes,
      helpfulRate: ratio(row.positive, row.votes),
    }))
    .sort((a, b) => b.questions - a.questions)
    .slice(0, 9);

  return { activity, quality, channels, districts: districtRows, support };
}

/** El desglose conserva los filtros globales y solo separa un distrito ya seleccionado. */
export function districtDrilldown(events: AnalyticsEvent[], district: string) {
  const days = new Map<string, { sessions: Set<string>; outbound: Set<string>; searches: number }>();
  for (const event of events) {
    if ((event.district || "Sin distrito") !== district) continue;
    const date = dateInLima(event.timestamp);
    if (!date) continue;
    const row = days.get(date) ?? { sessions: new Set<string>(), outbound: new Set<string>(), searches: 0 };
    row.sessions.add(event.visitorId);
    if (event.type === "outbound") row.outbound.add(event.visitorId);
    if (event.type === "search") row.searches++;
    days.set(date, row);
  }
  return [...days].sort(([a], [b]) => a.localeCompare(b)).map(([date, row]) => ({
    date,
    sessions: row.sessions.size,
    searches: row.searches,
    outbound: row.outbound.size,
    outboundRate: ratio(row.outbound.size, row.sessions.size),
  }));
}

export function channelName(code: string) { return CHANNEL_LABELS[code] || code; }
