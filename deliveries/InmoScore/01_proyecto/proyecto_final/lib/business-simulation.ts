import type { AnalyticsEvent, EventType } from "./business-metrics.ts";
export const SIMULATION_END = "2026-11-12T04:59:59.000Z";
export const SIMULATION_SEED = 20261111;
export const SIMULATION_DAYS = 30;
const DISTRICTS = ["Santiago de Surco", "Miraflores", "San Miguel", "Ate", "Jesús María", "Los Olivos"];
const CHANNELS = ["directo", "organico", "referido", "campana"] as const;
const TOPICS = ["budget", "budget", "no_results", "model", "ranking", "favorites", "privacy", "sin_respuesta"];
function randomGenerator(seed: number) {
  let state = seed >>> 0;
  return () => { state = (Math.imul(state, 1664525) + 1013904223) >>> 0; return state / 4294967296; };
}
/** Datos ficticios: una sesión por visitante, sin correos, nombres ni ingresos personales. */
export function generateSimulation(count = 300, seed = SIMULATION_SEED): AnalyticsEvent[] {
  if (!Number.isInteger(count) || count < 0 || count > 10000) throw new Error("La simulación admite entre 0 y 10000 sesiones.");
  const random = randomGenerator(seed);
  const events: AnalyticsEvent[] = [];
  for (let user = 0; user < count; user++) {
    const visitorId = `sim-${String(user + 1).padStart(4, "0")}`;
    const district = DISTRICTS[Math.floor(random() * DISTRICTS.length)];
    const channel = CHANNELS[Math.floor(random() * CHANNELS.length)];
    const day = Math.floor(random() * SIMULATION_DAYS);
    const hour = 7 + Math.floor(random() * 16);
    let timestamp = Date.UTC(2026, 9, 13 + day, hour + 5, Math.floor(random() * 60));
    const emit = (type: EventType, extra: Partial<AnalyticsEvent> = {}) => { events.push({ id: `${visitorId}-${events.length + 1}`, visitorId, timestamp: new Date(timestamp).toISOString(), type, district, channel, ...extra }); timestamp += 1000 + Math.floor(random() * 10000); };
    emit("page_view");
    if (random() < .79) {
      const searches = 1 + Math.floor(random() * 3);
      let hasResults = false;
      for (let step = 0; step < searches; step++) {
        const success = random() > .045;
        const resultCount = success ? (random() < .22 ? 0 : 1 + Math.floor(random() * 56)) : undefined;
        hasResults ||= (resultCount ?? 0) > 0;
        emit("search", { success, resultCount, durationMs: 140 + Math.round(random() * 1500 + (channel === "campana" ? 160 : 0)) });
      }
      if (hasResults && random() < .87) {
        const views = 1 + Math.floor(random() * 4);
        for (let view = 0; view < views; view++) emit("detail");
        if (random() < .53) emit("favorite");
        if (random() < .45) emit("compare");
        if (random() < (channel === "referido" ? .56 : .35)) emit("outbound");
      }
    }
    if (random() < .41) {
      const questions = 1 + Math.floor(random() * 3);
      for (let question = 0; question < questions; question++) {
        const topic = TOPICS[Math.floor(random() * TOPICS.length)];
        emit("chat_question", { topic });
        if (random() < .53) emit("chat_feedback", { topic, helpful: topic !== "sin_respuesta" && random() < .84 });

      }
    }
    if (random() < .035) emit("api_error");
  }
  return events.sort((a, b) => a.timestamp.localeCompare(b.timestamp));
}

