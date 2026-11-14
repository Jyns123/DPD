import { CHANNEL_LABELS, TOPIC_LABELS, ratio, type AnalyticsEvent } from "./business-metrics.ts";

type Session = { id: string; events: AnalyticsEvent[] };
export type Action = "Solo actividad" | "Búsqueda" | "Ficha" | "Salida";

/** Cada gráfico usa los eventos ya filtrados por el tablero. */
export function businessVisuals(events: AnalyticsEvent[]) {
  const groups = new Map<string, AnalyticsEvent[]>();
  for (const event of events) {
    const session = groups.get(event.visitorId) ?? [];
    session.push(event);
    groups.set(event.visitorId, session);
  }
  const sessions: Session[] = [...groups].map(([id, items]) => ({
    id, events: [...items].sort((a, b) => a.timestamp.localeCompare(b.timestamp) || a.id.localeCompare(b.id)),
  }));
  const stages = [
    { name: "Actividad", count: sessions.length },
    { name: "Búsqueda", count: 0 },
    { name: "Ficha", count: 0 },
    { name: "Salida al aviso", count: 0 },
  ];
  const channels = new Map<string, Record<Action, number>>();
  for (const session of sessions) {
    let reached = 0;
    for (const event of session.events) {
      if (reached === 0 && event.type === "search") reached = 1;
      else if (reached === 1 && event.type === "detail") reached = 2;
      else if (reached === 2 && event.type === "outbound") reached = 3;
    }
    for (let step = 1; step <= reached; step++) stages[step].count++;
    const channel = session.events[0].channel || "desconocido";
    const record = channels.get(channel) ?? { "Solo actividad": 0, "Búsqueda": 0, "Ficha": 0, "Salida": 0 };
    const types = new Set(session.events.map(item => item.type));
    const action: Action = types.has("outbound") ? "Salida" : types.has("detail") ? "Ficha" : types.has("search") ? "Búsqueda" : "Solo actividad";
    record[action]++;
    channels.set(channel, record);
  }
  const journey = stages.map((stage, index) => ({
    ...stage,
    percentOfStart: ratio(stage.count, stages[0].count),
    percentOfPrevious: index ? ratio(stage.count, stages[index - 1].count) : null,
  }));
  const channelActions = [...channels].map(([key, counts]) => ({
    name: CHANNEL_LABELS[key] || key, ...counts,
    total: Object.values(counts).reduce((sum, count) => sum + count, 0),
  })).sort((a, b) => b.total - a.total);

  const searchOutcomes = [
    { name: "Con resultados", value: 0 },
    { name: "Sin coincidencias", value: 0 },
    { name: "Error", value: 0 },
    { name: "Sin medición", value: 0 },
  ];
  const latencies = [
    { name: "< 250 ms", count: 0 },
    { name: "250–499 ms", count: 0 },
    { name: "500–999 ms", count: 0 },
    { name: "1–1,9 s", count: 0 },
    { name: "≥ 2 s", count: 0 },
  ];
  let searchesWithoutDuration = 0;
  const topics = new Map<string, number>();
  const pairSessions = new Map<string, Set<string>>();
  for (const event of events) {
    if (event.type === "search") {
      const bucket = event.success === false ? 2
        : typeof event.resultCount === "number" && event.resultCount > 0 ? 0
        : event.resultCount === 0 ? 1 : 3;
      searchOutcomes[bucket].value++;
      const duration = event.durationMs;
      if (typeof duration === "number" && Number.isFinite(duration) && duration >= 0) {
        const bin = duration < 250 ? 0 : duration < 500 ? 1 : duration < 1000 ? 2 : duration < 2000 ? 3 : 4;
        latencies[bin].count++;
      } else searchesWithoutDuration++;
    }
    if (event.type === "chat_question") {
      const key = event.topic || "Sin categoría";
      topics.set(key, (topics.get(key) ?? 0) + 1);
    }
    const key = `${event.channel || "desconocido"}\u0000${event.district || "Sin distrito"}`;
    const set = pairSessions.get(key) ?? new Set<string>();
    set.add(event.visitorId);
    pairSessions.set(key, set);
  }
  const topicAreas = [...topics].map(([name, size]) => ({
    name: TOPIC_LABELS[name] || name, size,
  })).sort((a, b) => b.size - a.size);
  const districts = new Map<string, number>();
  const matrixChannelCodes = new Set<string>();
  for (const [key, ids] of pairSessions) {
    const [channel, district] = key.split("\u0000");
    matrixChannelCodes.add(channel);
    districts.set(district, (districts.get(district) ?? 0) + ids.size);
  }
  const matrixChannels = [...matrixChannelCodes].sort().map(code => ({ code, name: CHANNEL_LABELS[code] || code }));
  const topDistricts = [...districts].sort((a, b) => b[1] - a[1]).slice(0, 8).map(([name]) => name);
  const matrix = topDistricts.map(name => ({
    district: name,
    cells: matrixChannels.map(channel => {
      return { channel: channel.name, count: pairSessions.get(`${channel.code}\u0000${name}`)?.size ?? 0 };
    }),
  }));
  const maxMatrix = Math.max(0, ...matrix.flatMap(row => row.cells.map(cell => cell.count)));
  return { journey, channelActions, searchOutcomes, latencies, searchesWithoutDuration, topicAreas, matrixChannels, matrix, maxMatrix };
}
