import { dateInLima, summarize, type AnalyticsEvent, type CatalogQuality, type Metric } from "./business-metrics.ts";

export type DailyMetricPoint = { date: string; value: number | null };
export const CATALOG_METRICS = ["model-coverage", "location-coverage", "warning-rate"] as const;

export function isDailyMetric(metric: Metric) {
  return metric.group !== "Finanzas" && metric.id !== "freshness"
    && !(CATALOG_METRICS as readonly string[]).includes(metric.id);
}

/** Una agregación por día alimenta todos los gráficos; no se repite por indicador. */
export function dailyMetricSeries(events: AnalyticsEvent[], catalog: CatalogQuality): Record<string, DailyMetricPoint[]> {
  const groups = new Map<string, AnalyticsEvent[]>();
  for (const event of events) {
    const date = dateInLima(event.timestamp);
    if (!date) continue;
    const items = groups.get(date) ?? [];
    items.push(event);
    groups.set(date, items);
  }
  const series: Record<string, DailyMetricPoint[]> = {};
  for (const [date, items] of [...groups.entries()].sort(([a], [b]) => a.localeCompare(b))) {
    // Los costos no se distribuyen entre días. Sus cinco gráficos usan el escenario completo.
    const day = summarize(items, catalog, false, undefined, `${date}T23:59:59-05:00`);
    for (const metric of day.metrics.filter(isDailyMetric)) {
      (series[metric.id] ??= []).push({ date, value: metric.value });
    }
  }
  return series;
}

export function catalogProportion(id: string, catalog: CatalogQuality) {
  if (id === "model-coverage") return { amount: catalog.withModel, total: catalog.total, label: "Con referencia", remainder: "Sin referencia utilizable" };
  if (id === "location-coverage") return { amount: catalog.preciseLocation, total: catalog.total, label: "Ubicación precisa", remainder: "Aproximada o sin ubicación" };
  if (id === "warning-rate") return { amount: catalog.withWarnings, total: catalog.total, label: "Con advertencia", remainder: "Sin advertencias registradas" };
  return null;
}

export function monetaryChartScale(metrics: Metric[]): number {
  const maximum = Math.max(0, ...metrics.filter(metric => metric.group === "Finanzas" && metric.unit === "money").map(metric => Math.abs(metric.value ?? 0)));
  if (!maximum) return 1;
  const unit = 10 ** Math.floor(Math.log10(maximum));
  return Math.ceil(maximum / unit) * unit;
}
