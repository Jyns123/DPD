"use client";
import Image from "next/image";
import { useEffect, useMemo, useRef, useState } from "react";
import { RefreshCw } from "lucide-react";
import { metricValue, type AnalyticsEvent, type CatalogQuality, type Metric } from "../lib/business-metrics";
import { catalogProportion, dailyMetricSeries, isDailyMetric, monetaryChartScale, type DailyMetricPoint } from "../lib/indicator-charts";

const AREAS = ["Todos", "Negocio", "Finanzas", "Calidad", "Soporte", "TI"] as const;
type PythonRequest = { id: string; kind: "daily" | "level" | "signed"; values: (number | null)[]; max?: number };
type FigureResult = { request: object; charts: Record<string, string>; error?: boolean };
const compact = (value: number) => new Intl.NumberFormat("es-PE", { notation: "compact", maximumFractionDigits: 1 }).format(value);
const shortDate = (date: string) => date.slice(5).split("-").reverse().join("/");
function scaleFor(metric: Metric, values: (number | null)[]) {
  if (metric.unit === "percent") return 100;
  const maximum = Math.max(0, ...values.map(value => value ?? 0));
  if (metric.unit === "count" && maximum < 5) return 5;
  if (!maximum) return 1;
  const magnitude = 10 ** Math.floor(Math.log10(maximum));
  return [1, 2, 5, 10].map(multiplier => multiplier * magnitude)
    .find(candidate => candidate > maximum) ?? maximum;
}
function calendarPoints(points: DailyMetricPoint[]) {
  if (!points.length) return [];
  const byDate = new Map(points.map(point => [point.date, point.value]));
  const cursor = new Date(`${points[0].date}T12:00:00Z`);
  const last = points.at(-1)!.date;
  const result: DailyMetricPoint[] = [];
  while (cursor.toISOString().slice(0, 10) <= last) {
    const date = cursor.toISOString().slice(0, 10);
    result.push({ date, value: byDate.get(date) ?? null });
    cursor.setUTCDate(cursor.getUTCDate() + 1);
  }
  return result;
}
function DailyPlot({ metric, points, max }: { metric: Metric; points: DailyMetricPoint[]; max: number }) {
  const x = (index: number) => points.length > 1 ? 5 + 310 * index / (points.length - 1) : 160;
  const y = (value: number) => 89 - 80 * value / max;
  let path = "", connected = false;
  points.forEach((point, index) => {
    if (point.value === null) { connected = false; return; }
    path += `${connected ? "L" : "M"}${x(index).toFixed(2)},${y(point.value).toFixed(2)} `;
    connected = true;
  });
  return <svg viewBox="0 0 320 96" role="img" aria-label={`Evolución diaria de ${metric.title}`}>
    {[9, 49, 89].map(height => <line key={height} x1="5" x2="315" y1={height} y2={height} stroke="#e6ede8" strokeDasharray="3 3" />)}
    <path d={path} fill="none" stroke="#315f48" strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
    {points.map((point, index) => point.value === null ? null : <circle key={point.date} cx={x(index)} cy={y(point.value)} r={points.length === 1 ? 3.5 : 2} fill="#315f48"><title>{point.date}: {metricValue({ value: point.value, unit: metric.unit })}</title></circle>)}
  </svg>;
}
function LevelPlot({ amount, total, warning = false }: { amount: number; total: number; warning?: boolean }) {
  const width = total > 0 ? 310 * Math.max(0, Math.min(1, amount / total)) : 0;
  return <svg viewBox="0 0 320 96" role="img" aria-label={`${amount} de ${total}`}><rect x="5" y="36" width="310" height="25" rx="4" fill="#e8eee8" /><rect x="5" y="36" width={width} height="25" rx="4" fill={warning ? "#b88058" : "#315f48"} /></svg>;
}
function SignedPlot({ value, max }: { value: number; max: number }) {
  const width = 150 * Math.min(1, Math.abs(value) / max);
  return <svg viewBox="0 0 320 96" role="img" aria-label={`Valor del escenario: ${value}`}><line x1="10" x2="310" y1="49" y2="49" stroke="#e1e9e2" strokeWidth="25" /><line x1="160" x2="160" y1="23" y2="74" stroke="#8ca58e" /><rect x={value < 0 ? 160 - width : 160} y="37" width={width} height="24" rx="3" fill={value < 0 ? "#b88058" : "#315f48"} /></svg>;
}
function AgePlot({ metric, referenceTime }: { metric: Metric; referenceTime: string }) {
  if (metric.value === null) return <div className="bi-kpi-empty">Aún no hay eventos para calcular esta distancia temporal.</div>;
  const latest = new Date(Date.parse(referenceTime) - metric.value * 60000);
  const displayTime = (value: Date) => value.toLocaleString("es-PE", { timeZone: "America/Lima", day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
  return <><svg viewBox="0 0 320 96" role="img" aria-label={`${metricValue(metric)} desde el último evento seleccionado`}><line x1="22" x2="298" y1="47" y2="47" stroke="#b9ccbc" strokeWidth="3" /><circle cx="22" cy="47" r="6" fill="#315f48" /><circle cx="298" cy="47" r="6" fill="#fff" stroke="#315f48" strokeWidth="2" /><path d="M146 41 L157 47 L146 53" stroke="#7b987f" fill="none" strokeWidth="2" /><text x="160" y="27" textAnchor="middle" fill="#47644c" fontSize="12">{metricValue(metric)}</text></svg><div className="bi-kpi-axis"><span>Último: {displayTime(latest)}</span><span>Referencia: {displayTime(new Date(referenceTime))}</span></div></>;
}

export default function IndicatorCharts({ events, metrics, catalog, mode, token, referenceTime }: {
  events: AnalyticsEvent[]; metrics: Metric[]; catalog: CatalogQuality;
  mode: "simulation" | "live"; token: string; referenceTime: string;
}) {
  const [area, setArea] = useState<(typeof AREAS)[number]>("Todos");
  const [visible, setVisible] = useState(false);
  const [attempt, setAttempt] = useState(0);
  const [figures, setFigures] = useState<FigureResult | null>(null);
  const section = useRef<HTMLElement>(null);
  const daily = useMemo(() => {
    const observed = dailyMetricSeries(events, catalog);
    return Object.fromEntries(Object.entries(observed).map(([id, points]) => [id, calendarPoints(points)]));
  }, [events, catalog]);
  const moneyMax = monetaryChartScale(metrics);
  const visibleMetrics = metrics.filter(metric => area === "Todos" || metric.group === area);
  const requests: PythonRequest[] = metrics.flatMap((metric): PythonRequest[] => {
    if (metric.value === null || metric.id === "freshness") return [];
    if (isDailyMetric(metric)) {
      const values = (daily[metric.id] ?? []).map(point => point.value);
      if (!values.length || values.length > 92 || values.every(value => value === null)) return [];
      return [{ id: metric.id, kind: "daily" as const, values, max: scaleFor(metric, values) }];
    }
    const proportion = catalogProportion(metric.id, catalog);
    if (proportion && proportion.total) return [{ id: metric.id, kind: "level" as const, values: [proportion.amount], max: proportion.total }];
    if (metric.group === "Finanzas") return [{ id: metric.id, kind: "signed" as const, values: [metric.value], max: metric.unit === "money" ? moneyMax : Math.max(25, Math.ceil(Math.abs(metric.value) / 25) * 25) }];
    return [];
  });
  const requestBody = JSON.stringify({ mode: mode === "simulation" ? "sim" : "live", charts: requests });
  const accessToken = mode === "live" ? token : "";
  const request = useMemo(() => ({ body: requestBody, authenticated: Boolean(accessToken), attempt }), [requestBody, accessToken, attempt]);
  const current = figures?.request === request ? figures : null;

  useEffect(() => {
    const element = section.current;
    if (!element) return;
    const observer = new IntersectionObserver(entries => { if (entries.some(entry => entry.isIntersecting)) { setVisible(true); observer.disconnect(); } }, { rootMargin: "500px" });
    observer.observe(element);
    return () => observer.disconnect();
  }, []);
  useEffect(() => {
    if (!visible) return;
    let active = true;
    const controller = new AbortController();
    let timeout: ReturnType<typeof setTimeout> | undefined;
    const debounce = setTimeout(async () => {
      timeout = setTimeout(() => controller.abort(), 25000);
      try {
        const headers: Record<string, string> = { "Content-Type": "application/json" };
        if (accessToken) headers["X-Analytics-Token"] = accessToken;
        const response = await fetch("/api/bi-indicators", { method: "POST", body: request.body, headers, cache: "no-store", signal: controller.signal });
        const data = await response.json();
        if (!response.ok || !data.charts || typeof data.charts !== "object") throw new Error("No se generaron las figuras.");
        const charts: Record<string, string> = {};
        for (const [id, svg] of Object.entries(data.charts)) {
          if (typeof svg === "string" && svg.includes("<svg")) charts[id] = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
        }
        if (active) setFigures({ request, charts });
      } catch { if (active) setFigures({ request, charts: {}, error: true }); }
      finally { clearTimeout(timeout); }
    }, 600);
    return () => { active = false; clearTimeout(debounce); clearTimeout(timeout); controller.abort(); };
  }, [visible, request, accessToken]);

  return <section id="board-indicator-charts" className="bi-indicator-section" ref={section} aria-labelledby="bi-indicator-heading">
    <div className="bi-indicator-heading"><div><h2 id="bi-indicator-heading">30 gráficos de indicadores</h2><p>Negocio, finanzas, calidad, soporte y tecnología. Cada gráfico usa la selección actual o indica expresamente que corresponde al catálogo completo.</p><span className="bi-chart-count">{visibleMetrics.length} de 30 gráficos · {mode === "simulation" ? "Actividad ficticia" : "Actividad registrada"}</span></div><figure className="bi-section-photo"><Image src="/imagenes/bi-san-isidro.png" alt="Escena ilustrativa de San Isidro" fill sizes="(max-width: 680px) 35vw, 240px" /><figcaption>Escena ilustrativa de San Isidro</figcaption></figure></div>
    <div className="bi-chart-area-tabs" role="group" aria-label="Elegir área de indicadores">{AREAS.map(value => <button key={value} aria-pressed={area === value} onClick={() => setArea(value)}>{value}<small>{value === "Todos" ? 30 : metrics.filter(metric => metric.group === value).length}</small></button>)}</div>
    <div className="bi-chart-generation" role="status"><span>{!visible ? "Las figuras se preparan al acercarte a esta sección." : !current ? "Actualizando las figuras de Python; ya puedes explorar la representación local de los mismos datos." : current.error ? "Vista local de los datos. Las figuras de Python no están disponibles en este momento." : "Figuras de Python actualizadas. La edad del último evento se representa como una instantánea temporal."}</span>{current?.error && <button onClick={() => setAttempt(value => value + 1)}><RefreshCw size={12} /> Reintentar figuras</button>}</div>
    <div className="bi-indicator-grid">{visibleMetrics.map((metric) => {
      const points = daily[metric.id] ?? [];
      const dailyValues = points.map(point => point.value);
      const dailyMax = scaleFor(metric, dailyValues);
      const proportion = catalogProportion(metric.id, catalog);
      const signedMax = metric.unit === "money" ? moneyMax : Math.max(25, Math.ceil(Math.abs(metric.value ?? 0) / 25) * 25);
      const plot = current?.charts[metric.id];
      const hasDaily = isDailyMetric(metric) && points.some(point => point.value !== null);
      return <article key={metric.id} className={`bi-indicator-card bi-area-${metric.group.toLowerCase()}`}>
        <header><div><small>{metric.group}</small><h3>{metric.title}</h3></div></header>
        <span className="bi-indicator-scope">{isDailyMetric(metric) ? "Por día · hora de Lima" : proportion ? "Proporción del catálogo completo" : metric.id === "freshness" ? "Instantánea de la selección" : "Escenario económico de la selección"}</span>
        {isDailyMetric(metric) ? <>{hasDaily ? <><div className="bi-kpi-daily"><div className="bi-kpi-yaxis"><span>{metric.unit === "percent" ? `${dailyMax}%` : compact(dailyMax)}</span><span>0</span></div><div>{plot ? <Image src={plot} width={320} height={96} unoptimized alt={`Serie diaria de ${metric.title}; tabla disponible debajo`} /> : <DailyPlot metric={metric} points={points} max={dailyMax} />}</div></div><div className="bi-kpi-axis bi-kpi-date-axis"><span>{shortDate(points[0].date)}</span><span>{shortDate(points.at(-1)!.date)}</span></div></> : <div className="bi-kpi-empty">Sin observaciones suficientes para dibujar esta serie.</div>}</> : proportion ? <>{proportion.total ? <><div className="bi-kpi-level">{plot ? <Image src={plot} width={320} height={96} unoptimized alt={`${proportion.label}: ${proportion.amount} de ${proportion.total}`} /> : <LevelPlot amount={proportion.amount} total={proportion.total} warning={metric.id === "warning-rate"} />}</div><div className="bi-kpi-axis"><span>0 avisos</span><span>{compact(proportion.total)} avisos</span></div><div className="bi-kpi-legend"><span>{proportion.label}: {proportion.amount.toLocaleString("es-PE")}</span><span>{proportion.remainder}: {(proportion.total - proportion.amount).toLocaleString("es-PE")}</span></div></> : <div className="bi-kpi-empty">No hay un catálogo disponible para calcular esta proporción.</div>}</> : metric.id === "freshness" ? <AgePlot metric={metric} referenceTime={referenceTime} /> : metric.value === null ? <div className="bi-kpi-empty">Sin transacciones registradas.<br />Este gráfico solo usa supuestos en la simulación.</div> : <><div className="bi-kpi-level">{plot ? <Image src={plot} width={320} height={96} unoptimized alt={`${metric.title}: ${metricValue(metric)}`} /> : <SignedPlot value={metric.value} max={signedMax} />}</div><div className="bi-kpi-axis"><span>−{compact(signedMax)}{metric.unit === "percent" ? "%" : ""}</span><span>0</span><span>{compact(signedMax)}{metric.unit === "percent" ? "%" : ""}</span></div><p className="bi-kpi-unit">{metric.unit === "money" ? "Soles supuestos · escala compartida entre los cuatro importes" : "Retorno supuesto · escala porcentual propia"}</p></>}
        <div className="bi-kpi-caption"><span>{proportion ? "Catálogo" : metric.id === "freshness" ? "Distancia temporal" : metric.group === "Finanzas" ? "Escenario" : "Selección completa"}</span><b>{metricValue(metric)}</b></div>
        <details className="bi-kpi-explain"><summary>Ver datos, fórmula y alcance</summary><p><b>Fórmula:</b> {metric.formula}.</p><p>{metric.note}</p>{isDailyMetric(metric) && <><p>La serie muestra valores diarios; el resumen usa toda la selección. Los días sin observaciones quedan vacíos, no se inventan mediciones. No es un pronóstico.</p><div className="board-table-scroll"><table><caption>{metric.title} por día</caption><thead><tr><th scope="col">Fecha</th><th scope="col">Valor</th></tr></thead><tbody>{points.map(point => <tr key={point.date}><td>{point.date}</td><td>{metricValue({ value: point.value, unit: metric.unit })}</td></tr>)}</tbody></table></div></>}</details>
      </article>;
    })}</div>
  </section>;
}
