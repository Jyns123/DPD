import { canReadAnalytics } from "../../../lib/analytics-access";
import { jsonError, mutationOriginIsSame, readJson } from "../_shared";

import { renderBiResponse } from "../../../lib/bi-python";

export const runtime = "nodejs";

type DailyPoint = { date: string; searches: number; referrals: number };
type ChartInput = { mode: "sim" | "live"; daily: DailyPoint[]; heatmap: number[][] };

function isCount(value: unknown): value is number {
  return typeof value === "number" && Number.isInteger(value) && value >= 0 && value <= 20_000;
}

function parseChartInput(value: unknown): ChartInput | null {
  if (!value || typeof value !== "object") return null;
  const { mode, daily, heatmap } = value as Partial<ChartInput>;
  if ((mode !== "sim" && mode !== "live") || !Array.isArray(daily) || daily.length > 92) return null;
  if (!Array.isArray(heatmap) || heatmap.length !== 7 ||
      heatmap.some(row => !Array.isArray(row) || row.length !== 6 || !row.every(isCount))) return null;

  const points: DailyPoint[] = [];
  let first = 0;
  let previous = -Infinity;
  for (const point of daily) {
    if (!point || typeof point.date !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(point.date) ||
        !isCount(point.searches) || !isCount(point.referrals)) return null;
    const time = Date.parse(point.date);
    if (!Number.isFinite(time) || new Date(time).toISOString().slice(0, 10) !== point.date ||
        time <= previous) return null;
    if (!points.length) first = time;
    if (time - first > 91 * 86_400_000) return null;
    points.push({ date: point.date, searches: point.searches, referrals: point.referrals });
    previous = time;
  }
  return { mode, daily: points, heatmap };
}

export async function POST(request: Request) {
  if (!mutationOriginIsSame(request)) {
    return jsonError(403, "invalid_origin", "La gráfica debe solicitarse desde el tablero.");
  }
  const input = parseChartInput(await readJson(request));
  if (!input) return jsonError(400, "invalid_chart_data", "La selección de datos no tiene el formato esperado.");
  if (input.mode === "live" && !canReadAnalytics(request, {
    token: process.env.ANALYTICS_ADMIN_TOKEN,
    localOnly: process.env.ANALYTICS_LOCAL_ONLY === "1",
  })) {
    return jsonError(403, "private_dashboard", "La gráfica registrada requiere acceso al tablero.");
  }

  return renderBiResponse(input);
}
