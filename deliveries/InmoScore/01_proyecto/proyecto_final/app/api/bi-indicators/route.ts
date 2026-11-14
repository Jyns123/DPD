import { canReadAnalytics } from "../../../lib/analytics-access";
import { renderBiResponse } from "../../../lib/bi-python";
import { jsonError, mutationOriginIsSame, readJson } from "../_shared";

export const runtime = "nodejs";

type Indicator = { id: string; kind: "daily" | "level" | "signed"; values: (number | null)[]; max?: number };

function numberInRange(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value) && Math.abs(value) <= 1e15;
}

function parseIndicators(value: unknown) {
  if (!value || typeof value !== "object") return null;
  const { mode, charts } = value as { mode?: unknown; charts?: unknown };
  if ((mode !== "sim" && mode !== "live") || !Array.isArray(charts) || charts.length > 30) return null;
  const normalized: Indicator[] = [];
  const ids = new Set<string>();
  for (const chart of charts) {
    if (!chart || typeof chart.id !== "string" || !/^[a-z][a-z0-9_-]{0,31}$/.test(chart.id) ||
        ids.has(chart.id) || !["daily", "level", "signed"].includes(chart.kind) ||
        !Array.isArray(chart.values) || chart.values.length > 92 ||
        (chart.kind !== "daily" && chart.values.length !== 1) ||
        chart.values.some((point: unknown) => point !== null && !numberInRange(point)) ||
        (chart.max !== undefined && (!numberInRange(chart.max) || chart.max <= 0))) return null;
    ids.add(chart.id);
    normalized.push({ id: chart.id, kind: chart.kind, values: chart.values, max: chart.max });
  }
  return { mode, charts: normalized };
}

export async function POST(request: Request) {
  if (!mutationOriginIsSame(request)) {
    return jsonError(403, "invalid_origin", "La gráfica debe solicitarse desde el tablero.");
  }
  const input = parseIndicators(await readJson(request, 64 * 1024));
  if (!input) return jsonError(400, "invalid_chart_data", "La selección de indicadores no tiene el formato esperado.");
  if (input.mode === "live" && !canReadAnalytics(request, {
    token: process.env.ANALYTICS_ADMIN_TOKEN,
    localOnly: process.env.ANALYTICS_LOCAL_ONLY === "1",
  })) {
    return jsonError(403, "private_dashboard", "La gráfica registrada requiere acceso al tablero.");
  }
  return renderBiResponse(input);
}
