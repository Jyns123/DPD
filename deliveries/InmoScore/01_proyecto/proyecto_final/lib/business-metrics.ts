export const EVENT_TYPES = ["page_view", "search", "detail", "favorite", "compare", "outbound", "chat_question", "chat_feedback", "support_message", "api_error"] as const;
export type EventType = (typeof EVENT_TYPES)[number];
export type AnalyticsEvent = {
  id: string;
  visitorId: string;
  type: EventType;
  timestamp: string;
  district?: string;
  channel?: "directo" | "organico" | "referido" | "campana";
  resultCount?: number;
  durationMs?: number;
  success?: boolean;
  topic?: string;
  helpful?: boolean;
  listingId?: string;
};
export type CatalogQuality = {
  total: number;
  withModel: number;
  preciseLocation: number;
  withWarnings: number;
  districts: number;
  capturedAt?: string;
};
export type AnalyticsResponse = { events: AnalyticsEvent[]; catalog: CatalogQuality; updatedAt: string; retention?: unknown };
export type EventFilters = { from: string; to: string; district: string; channel: string };
export type FinancialAssumptions = { referralValue: number; marketingCost: number; fixedCost: number; costPerSession: number };
export const DEFAULT_ASSUMPTIONS: FinancialAssumptions = { referralValue: 25, marketingCost: 300, fixedCost: 150, costPerSession: 0.2 };
export type Metric = { id: string; title: string; value: number | null; unit: "count" | "percent" | "money" | "ms" | "minutes" | "decimal"; group: "Negocio" | "Finanzas" | "Calidad" | "Soporte" | "TI"; formula: string; note: string };
export type DailyRow = { date: string; sessions: number; searches: number; referrals: number; errors: number; latency: number | null };
export type FunnelRow = { stage: string; count: number; percent: number | null };
export type BreakdownRow = { name: string; sessions: number; referrals: number; rate: number | null };
export const CHANNEL_LABELS: Record<string, string> = { directo: "Directo", organico: "Orgánico", referido: "Referido", campana: "Campaña", desconocido: "Sin canal" };
export const TOPIC_LABELS: Record<string, string> = { start: "Primeros pasos", budget: "Tope de compra", ranking: "Puntaje", no_results: "Sin coincidencias", model: "Modelo de precio", quality: "Calidad de avisos", map: "Ubicación", favorites: "Favoritos", compare: "Comparación", privacy: "Privacidad", sin_respuesta: "Consulta no cubierta" };

export function ratio(numerator: number, denominator: number): number | null {
  return denominator > 0 ? 100 * numerator / denominator : null;
}
export function percentile(values: number[], fraction: number): number | null {
  if (!values.length) return null;
  const sorted = values.filter(Number.isFinite).sort((a, b) => a - b);
  if (!sorted.length) return null;
  return sorted[Math.max(0, Math.min(sorted.length - 1, Math.ceil(fraction * sorted.length) - 1))];
}
export function dateInLima(timestamp: string): string {
  const value = Date.parse(timestamp);
  return Number.isFinite(value) ? new Date(value - 5 * 60 * 60 * 1000).toISOString().slice(0, 10) : "";
}
export function uniqueSessions(events: AnalyticsEvent[]): number {
  return new Set(events.map(event => event.visitorId)).size;
}
export function deduplicateEvents(events: AnalyticsEvent[]): AnalyticsEvent[] {
  const seen = new Set<string>();
  return events.filter(event => {
    if (seen.has(event.id) || !dateInLima(event.timestamp)) return false;
    seen.add(event.id);
    return true;
  });
}
export function filterEvents(events: AnalyticsEvent[], filters: EventFilters): AnalyticsEvent[] {
  return deduplicateEvents(events).filter(event => {
    const date = dateInLima(event.timestamp);
    return (!filters.from || date >= filters.from) && (!filters.to || date <= filters.to)
      && (!filters.district || (event.district || "Sin distrito") === filters.district)
      && (!filters.channel || (event.channel || "desconocido") === filters.channel);
  });
}
export function correlation(x: number[], y: number[]): number | null {
  if (x.length !== y.length || x.length < 3 || !x.every(Number.isFinite) || !y.every(Number.isFinite)) return null;
  const mx = x.reduce((a, b) => a + b, 0) / x.length;
  const my = y.reduce((a, b) => a + b, 0) / y.length;
  let covariance = 0, vx = 0, vy = 0;
  x.forEach((value, index) => { covariance += (value - mx) * (y[index] - my); vx += (value - mx) ** 2; vy += (y[index] - my) ** 2; });
  return vx > 0 && vy > 0 ? Math.max(-1, Math.min(1, covariance / Math.sqrt(vx * vy))) : null;
}
export function summarize(eventsInput: AnalyticsEvent[], catalog: CatalogQuality, simulation: boolean, assumptions: FinancialAssumptions = DEFAULT_ASSUMPTIONS, now: string = new Date().toISOString()) {
  const events = deduplicateEvents(eventsInput);
  // Agrupar una sola vez evita recorrer el historial por cada día y celda.
  const byType = new Map<EventType, AnalyticsEvent[]>();
  type ActivityGroup = { sessions: Set<string>; referrals: Set<string> };
  type DayGroup = ActivityGroup & { searches: number; errors: number; latencies: number[] };
  const days = new Map<string, DayGroup>();
  const byDistrict = new Map<string, ActivityGroup>();
  const byChannel = new Map<string, ActivityGroup>();
  const topicCounts = new Map<string, number>();
  const heatmap = Array.from({ length: 7 }, (_, weekday) =>
    Array.from({ length: 6 }, (_, band) => ({ weekday, band, count: 0 })));
  let latest: number | null = null;
  for (const event of events) {
    const items = byType.get(event.type) ?? [];
    items.push(event);
    byType.set(event.type, items);
    const timestamp = Date.parse(event.timestamp);
    latest = latest === null ? timestamp : Math.max(latest, timestamp);
    const lima = new Date(timestamp - 5 * 3600000);
    const date = lima.toISOString().slice(0, 10);
    const day = days.get(date) ?? { sessions: new Set<string>(), referrals: new Set<string>(), searches: 0, errors: 0, latencies: [] };
    day.sessions.add(event.visitorId);
    if (event.type === "outbound") day.referrals.add(event.visitorId);
    if (event.type === "api_error" || event.type === "search" && event.success === false) day.errors++;
    if (event.type === "search") {
      day.searches++;
      if (typeof event.durationMs === "number" && Number.isFinite(event.durationMs) && event.durationMs >= 0) day.latencies.push(event.durationMs);
    }
    days.set(date, day);
    for (const [map, key] of [[byDistrict, event.district || "Sin distrito"], [byChannel, event.channel || "desconocido"]] as const) {
      const segment = map.get(key) ?? { sessions: new Set<string>(), referrals: new Set<string>() };
      segment.sessions.add(event.visitorId);
      if (event.type === "outbound") segment.referrals.add(event.visitorId);
      map.set(key, segment);
    }
    if (event.type === "chat_question") {
      const topic = event.topic || "Sin categoría";
      topicCounts.set(topic, (topicCounts.get(topic) ?? 0) + 1);
    }
    heatmap[(lima.getUTCDay() + 6) % 7][Math.floor(lima.getUTCHours() / 4)].count++;
  }
  const of = (type: EventType) => byType.get(type) ?? [];
  const sessions = uniqueSessions(events);
  const searches = of("search");
  const completed = searches.filter(event => event.success !== false && typeof event.resultCount === "number");
  const successful = completed.filter(event => (event.resultCount ?? 0) > 0);
  const empty = completed.filter(event => event.resultCount === 0);
  const searchers = uniqueSessions(searches);
  const details = of("detail");
  const favorites = uniqueSessions(of("favorite"));
  const comparers = uniqueSessions(of("compare"));
  const referrals = uniqueSessions(of("outbound"));
  const questions = of("chat_question");
  const feedback = of("chat_feedback").filter(event => typeof event.helpful === "boolean");

  const failures = of("api_error").length + searches.filter(event => event.success === false).length;

  const latencies = searches.map(event => event.durationMs).filter((value): value is number => typeof value === "number" && Number.isFinite(value) && value >= 0);
  const income = referrals * assumptions.referralValue;
  const operational = assumptions.fixedCost + sessions * assumptions.costPerSession;
  const totalCost = assumptions.marketingCost + operational;
  const metrics: Metric[] = [
    { id: "sessions", title: "Sesiones observadas", value: sessions, unit: "count", group: "Negocio", formula: "IDs de sesión distintos en la selección", note: "Una persona puede abrir más de una sesión. No es un conteo de personas identificadas." },
    { id: "searchers", title: "Sesiones que buscan", value: searchers, unit: "count", group: "Negocio", formula: "Sesiones con al menos una búsqueda", note: "Incluye búsquedas fallidas para medir intención de uso." },
    { id: "activation", title: "Activación de búsqueda", value: ratio(searchers, sessions), unit: "percent", group: "Negocio", formula: "Sesiones que buscan / sesiones observadas × 100", note: "Mide uso del recomendador, no ventas." },
    { id: "searches", title: "Búsquedas realizadas", value: searches.length, unit: "count", group: "Negocio", formula: "Eventos search", note: "Cada consulta completada o fallida cuenta una vez." },
    { id: "details", title: "Fichas consultadas", value: details.length, unit: "count", group: "Negocio", formula: "Eventos detail", note: "Una misma ficha puede consultarse varias veces." },
    { id: "favorites", title: "Sesiones que guardan", value: favorites, unit: "count", group: "Negocio", formula: "Sesiones con una adición a favoritos", note: "Mide intención histórica; no es el inventario actual de favoritos." },
    { id: "comparers", title: "Sesiones que comparan", value: comparers, unit: "count", group: "Negocio", formula: "Sesiones con evento compare", note: "Usar el comparador ayuda a explorar alternativas." },
    { id: "referrals", title: "Salidas al anuncio", value: referrals, unit: "count", group: "Negocio", formula: "Sesiones con evento outbound", note: "Abrir el portal original no confirma un contacto ni una compra." },
    { id: "conversion", title: "Tasa de salida al anuncio", value: ratio(referrals, sessions), unit: "percent", group: "Negocio", formula: "Sesiones con salida / sesiones observadas × 100", note: "Conversión de navegación. No se registran ventas inmobiliarias." },
    { id: "income", title: "Ingreso hipotético", value: simulation ? income : null, unit: "money", group: "Finanzas", formula: "Sesiones con salida × valor supuesto por referido", note: "Escenario académico. No existe facturación ni comisión contratada." },
    { id: "marketing", title: "Gasto de captación supuesto", value: simulation ? assumptions.marketingCost : null, unit: "money", group: "Finanzas", formula: "Presupuesto de marketing ingresado", note: "Costo total asignado manualmente al segmento filtrado; no se prorratea." },
    { id: "operating", title: "Costo operativo supuesto", value: simulation ? operational : null, unit: "money", group: "Finanzas", formula: "Costo fijo + sesiones × costo unitario supuesto", note: "No proviene de una factura de infraestructura." },
    { id: "balance", title: "Saldo del escenario", value: simulation ? income - totalCost : null, unit: "money", group: "Finanzas", formula: "Ingreso hipotético − captación − operación", note: "Saldo antes de impuestos y otros costos no modelados. No es utilidad real." },
    { id: "roi", title: "Retorno del escenario", value: simulation ? ratio(income - totalCost, totalCost) : null, unit: "percent", group: "Finanzas", formula: "Saldo del escenario / costo total × 100", note: "Sin dato si el costo total es cero. Es una hipótesis, no una predicción." },
    { id: "results", title: "Búsquedas con resultados", value: ratio(successful.length, completed.length), unit: "percent", group: "Calidad", formula: "Búsquedas con ≥1 resultado / búsquedas completadas × 100", note: "No incluye errores técnicos en el denominador." },
    { id: "empty", title: "Búsquedas sin coincidencias", value: ratio(empty.length, completed.length), unit: "percent", group: "Calidad", formula: "Búsquedas con 0 resultados / búsquedas completadas × 100", note: "Cero coincidencias puede ser correcto por presupuesto y filtros; no equivale a error." },
    { id: "mean-results", title: "Coincidencias por búsqueda", value: completed.length ? completed.reduce((sum, event) => sum + (event.resultCount ?? 0), 0) / completed.length : null, unit: "decimal", group: "Calidad", formula: "Suma de coincidencias / búsquedas completadas", note: "Se refiere al total comunicado por el motor, no al tamaño de la página." },
    { id: "model-coverage", title: "Avisos con referencia de precio", value: ratio(catalog.withModel, catalog.total), unit: "percent", group: "Calidad", formula: "Avisos con predicción utilizable / catálogo completo × 100", note: "Catálogo global, independiente de filtros de actividad. Cobertura no equivale a precisión." },
    { id: "location-coverage", title: "Ubicación precisa disponible", value: ratio(catalog.preciseLocation, catalog.total), unit: "percent", group: "Calidad", formula: "Avisos con coordenadas precisas / catálogo completo × 100", note: "No convierte los índices distritales en seguridad específica de la vivienda." },
    { id: "warning-rate", title: "Avisos con advertencias", value: ratio(catalog.withWarnings, catalog.total), unit: "percent", group: "Calidad", formula: "Avisos con ≥1 bandera de calidad / catálogo completo × 100", note: "Incluye faltantes y limitaciones conocidas; no significa que todos sean anuncios inválidos." },
    { id: "chat-sessions", title: "Sesiones con consultas", value: uniqueSessions(questions), unit: "count", group: "Soporte", formula: "Sesiones con evento chat_question", note: "Consultas al asistente guiado de la web." },
    { id: "questions", title: "Consultas recibidas", value: questions.length, unit: "count", group: "Soporte", formula: "Eventos chat_question", note: "Se guarda la categoría, nunca el texto libre en analítica." },
    { id: "helpful", title: "Respuestas valoradas útiles", value: ratio(feedback.filter(event => event.helpful).length, feedback.length), unit: "percent", group: "Soporte", formula: "Valoraciones positivas / valoraciones recibidas × 100", note: "Respuesta voluntaria; puede tener sesgo y no mide resolución de tickets." },
    { id: "feedback", title: "Valoraciones recibidas", value: feedback.length, unit: "count", group: "Soporte", formula: "Eventos chat_feedback con respuesta válida", note: "El tamaño de esta muestra ayuda a interpretar la proporción de respuestas útiles." },
    { id: "unanswered", title: "Consultas no cubiertas", value: ratio(questions.filter(event => event.topic === "sin_respuesta").length, questions.length), unit: "percent", group: "Soporte", formula: "Consultas sin respuesta de la guía / consultas × 100", note: "Permite priorizar nuevos temas, sin inventar respuestas." },
    { id: "errors", title: "Errores registrados", value: failures, unit: "count", group: "TI", formula: "Búsquedas fallidas + errores de otras operaciones registrados", note: "No cubre fallas que impiden enviar el evento ni reemplaza monitoreo de servidor." },
    { id: "success", title: "Búsquedas sin error", value: ratio(searches.filter(event => event.success !== false).length, searches.length), unit: "percent", group: "TI", formula: "Búsquedas sin error / búsquedas registradas × 100", note: "Incluye consultas con cero coincidencias. No es disponibilidad global del servicio." },
    { id: "latency", title: "Tiempo de búsqueda P95", value: percentile(latencies, .95), unit: "ms", group: "TI", formula: "Percentil 95 por rango más cercano de durationMs", note: "Tiempo observado en el cliente. Con pocas consultas es poco representativo." },
    { id: "events", title: "Eventos disponibles", value: events.length, unit: "count", group: "TI", formula: "IDs de evento distintos en la selección", note: "Solo eventos consentidos y dentro de la retención; no todos los visitantes de la web." },
    { id: "freshness", title: "Edad del último evento", value: latest === null ? null : Math.max(0, (Date.parse(now) - latest) / 60000), unit: "minutes", group: "TI", formula: "Hora de referencia − último evento seleccionado", note: simulation ? "Se usa el cierre del escenario ficticio, no la hora actual." : "La última consulta al servidor puede ser reciente aunque no haya actividad nueva." },
  ];
  const stages: [EventType | null, string][] = [[null, "Actividad"], ["search", "Búsqueda"], ["detail", "Ficha"], ["favorite", "Favorito"], ["outbound", "Anuncio"]];
  const funnel: FunnelRow[] = stages.map(([type, stage]) => { const count = type ? uniqueSessions(of(type)) : sessions; return { stage, count, percent: ratio(count, sessions) }; });
  const daily: DailyRow[] = [...days.entries()].sort(([a], [b]) => a.localeCompare(b)).map(([date, day]) => ({
    date, sessions: day.sessions.size, searches: day.searches,
    referrals: day.referrals.size, errors: day.errors, latency: percentile(day.latencies, .95),
  }));
  const breakdown = (map: Map<string, ActivityGroup>): BreakdownRow[] => [...map.entries()].map(([name, group]) => ({
    name, sessions: group.sessions.size, referrals: group.referrals.size,
    rate: ratio(group.referrals.size, group.sessions.size),
  })).sort((a, b) => b.sessions - a.sessions);
  const topics = [...topicCounts.entries()].map(([topic, count]) => ({ topic, name: TOPIC_LABELS[topic] || topic, count })).sort((a, b) => b.count - a.count);
  let cumulative = 0;
  const pareto = topics.map(row => { cumulative += row.count; return { ...row, cumulative: ratio(cumulative, questions.length) ?? 0 }; });
  return { metrics, funnel, daily, districts: breakdown(byDistrict), channels: breakdown(byChannel), pareto, heatmap, correlation: correlation(daily.map(row => row.searches), daily.map(row => row.referrals)), feedbackCount: feedback.length, completedSearches: completed.length };
}
export function metricValue(metric: Pick<Metric, "value" | "unit">): string {
  if (metric.value === null || !Number.isFinite(metric.value)) return "Sin datos";
  const value = new Intl.NumberFormat("es-PE", { maximumFractionDigits: metric.unit === "count" ? 0 : 1 }).format(metric.value);
  if (metric.unit === "money") return `S/ ${value}`;
  if (metric.unit === "percent") return `${value}%`;
  if (metric.unit === "ms") return `${value} ms`;
  if (metric.unit === "minutes") return `${value} min`;
  return value;
}
export type MetricExportContext = {
  source: "simulation" | "live";
  filters: EventFilters;
  assumptions?: FinancialAssumptions;
};
export function metricsCsv(metrics: Metric[], context?: MetricExportContext): string {
  const escape = (value: string | number | null) => `"${String(value ?? "").replaceAll('"', '""')}"`;
  const headers = ["Grupo", "Indicador", "Valor", "Unidad", "Fórmula", "Alcance"];
  const metadataHeaders = ["Fuente de actividad", "Desde (Lima)", "Hasta (Lima)", "Distrito de actividad", "Canal de actividad", "Valor supuesto por referido", "Captación supuesta", "Costo fijo supuesto", "Costo supuesto por sesión"];
  const metadata = context ? [context.source === "simulation" ? "Simulación ficticia" : "Actividad registrada", context.filters.from || "Todo el periodo disponible", context.filters.to || "Todo el periodo disponible", context.filters.district || "Todos", context.filters.channel || "Todos", context.source === "simulation" ? context.assumptions?.referralValue ?? "" : "", context.source === "simulation" ? context.assumptions?.marketingCost ?? "" : "", context.source === "simulation" ? context.assumptions?.fixedCost ?? "" : "", context.source === "simulation" ? context.assumptions?.costPerSession ?? "" : ""] : [];
  return "\uFEFF" + [[...headers, ...(context ? metadataHeaders : [])], ...metrics.map(metric => [metric.group, metric.title, metric.value, metric.unit, metric.formula, metric.note, ...metadata])].map(row => row.map(escape).join(",")).join("\r\n");
}

export type BoardReading = { id: string; title: string; observation: string; nextStep: string; scope: "Actividad seleccionada" | "Catálogo completo" };
/** Lecturas descriptivas; no atribuyen causas ni predicen resultados. */
export function boardReadings(summary: ReturnType<typeof summarize>, catalog: CatalogQuality): BoardReading[] {
  const readings: BoardReading[] = [];
  const metric = (id: string) => summary.metrics.find(item => item.id === id)!;
  const empty = metric("empty");
  if (summary.completedSearches) readings.push({
    id: "search-fit", title: "Revisar las búsquedas sin coincidencias",
    observation: `${metricValue(empty)} de ${summary.completedSearches} ${summary.completedSearches === 1 ? "búsqueda completada no obtuvo" : "búsquedas completadas no obtuvieron"} coincidencias.`,
    nextStep: "Prueben un caso con el mismo presupuesto y revisen qué filtro deja fuera los avisos. Cero resultados puede ser una respuesta correcta.",
    scope: "Actividad seleccionada",
  });
  const topTopic = summary.pareto[0];
  if (topTopic) readings.push({
    id: "help-topic", title: "Dar claridad al tema más consultado",
    observation: `«${topTopic.name}» reúne ${topTopic.count} ${topTopic.count === 1 ? "consulta" : "consultas"} de ${metric("questions").value ?? 0}.`,
    nextStep: "Lean esa respuesta de la guía y comprueben si el equipo puede explicarla con un ejemplo. La frecuencia no demuestra que la respuesta sea incorrecta.",
    scope: "Actividad seleccionada",
  });
  if (catalog.total) readings.push({
    id: "location-limit", title: "Explicar el alcance del mapa",
    observation: `${catalog.preciseLocation} de ${catalog.total} avisos tienen coordenadas precisas.`,
    nextStep: "Mantengan visible la diferencia entre una ubicación precisa y una referencia del distrito. Verifiquen la dirección antes de recomendar una visita.",
    scope: "Catálogo completo",
  });
  return readings;
}
