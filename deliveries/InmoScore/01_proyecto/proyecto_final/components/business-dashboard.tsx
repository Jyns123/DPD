"use client";
import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import PythonCharts from "./bi-python-charts";
import IndicatorCharts from "./bi-indicator-charts";
import BusinessVisualizations from "./business-visualizations";
import BusinessComboCharts from "./business-combo-charts";
import {
  Bar, BarChart, CartesianGrid, Cell, ComposedChart, Legend, Line,
  Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { ArrowLeft, ArrowUpRight, BarChart3, Check, CircleHelp, Download, Filter, LockKeyhole, RefreshCw, Wifi } from "lucide-react";
import {
  CHANNEL_LABELS, DEFAULT_ASSUMPTIONS, boardReadings, dateInLima, filterEvents, metricValue, metricsCsv, summarize,
  type AnalyticsEvent, type AnalyticsResponse, type CatalogQuality, type EventFilters, type FinancialAssumptions, type Metric,
} from "../lib/business-metrics";
import { generateSimulation, SIMULATION_END, SIMULATION_SEED } from "../lib/business-simulation";

const COLORS = ["#173d31", "#86a85e", "#d6815e", "#abc3bc", "#667354", "#c3a462", "#879ba4"];
const GROUPS = ["Todos", "Negocio", "Finanzas", "Calidad", "Soporte", "TI"] as const;
const REPORT_TABS = [
  ["#board-charts", "Vista general"],
  ["#board-business-visuals", "Análisis del negocio"],
  ["#board-combo-charts", "Gráficos combinados"],
  ["#board-finances", "Escenario económico"],
  ["#board-indicator-charts", "30 gráficos de indicadores"],
  ["#board-indicators", "Fórmulas"],
  ["#board-catalog", "Calidad del catálogo"],
] as const;
const EVENT_NAMES: Record<string, string> = { page_view: "Entrada a la web", search: "Búsqueda", detail: "Consulta de ficha", favorite: "Favorito añadido", compare: "Comparación", outbound: "Salida al anuncio", chat_question: "Consulta de ayuda", chat_feedback: "Valoración de ayuda", support_message: "Mensaje de soporte", api_error: "Error de operación" };
function formatDate(value: string) { return new Date(value).toLocaleString("es-PE", { timeZone: "America/Lima", dateStyle: "short", timeStyle: "medium" }); }
function downloadFile(content: string, filename: string, mime = "text/csv;charset=utf-8") {
  const url = URL.createObjectURL(new Blob([content], { type: mime }));
  const link = document.createElement("a"); link.href = url; link.download = filename; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
function MetricCard({ metric }: { metric: Metric }) {
  return <article className={`board-metric ${metric.value !== null && metric.value < 0 ? "is-negative" : ""}`}>
    <span className="board-metric-group">{metric.group}</span><h3>{metric.title}</h3>
    <strong>{metricValue(metric)}</strong>
    <details><summary><CircleHelp size={13} /> Cómo se calcula</summary><p><b>Fórmula:</b> {metric.formula}.</p><p>{metric.note}</p></details>
  </article>;
}
function DataTable({ caption, headers, rows }: { caption: string; headers: string[]; rows: (string | number | null)[][] }) {
  return <details className="board-data-table"><summary>Ver datos de este gráfico</summary><div className="board-table-scroll"><table><caption>{caption}</caption><thead><tr>{headers.map(header => <th key={header} scope="col">{header}</th>)}</tr></thead><tbody>{rows.length ? rows.map((row, index) => <tr key={index}>{row.map((cell, column) => <td key={column}>{cell ?? "Sin datos"}</td>)}</tr>) : <tr><td colSpan={headers.length}>No hay eventos en esta selección.</td></tr>}</tbody></table></div></details>;
}
export default function BusinessDashboard({ initialCatalog }: { initialCatalog: CatalogQuality }) {
  const [mode, setMode] = useState<"simulation" | "live">("simulation");
  const [liveEvents, setLiveEvents] = useState<AnalyticsEvent[]>([]);
  const [catalog, setCatalog] = useState(initialCatalog);
  const [filters, setFilters] = useState<EventFilters>({ from: "", to: "", district: "", channel: "" });
  const [assumptions, setAssumptions] = useState<FinancialAssumptions>(DEFAULT_ASSUMPTIONS);
  const [group, setGroup] = useState<(typeof GROUPS)[number]>("Todos");
  const [updatedAt, setUpdatedAt] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [token, setToken] = useState("");
  const [activeToken, setActiveToken] = useState("");
  const [revision, setRevision] = useState(0);
  const [paused, setPaused] = useState(false);
  const [metricQuery, setMetricQuery] = useState("");
  const [activeSection, setActiveSection] = useState("#board-charts");
  const simulation = useMemo(() => generateSimulation(), []);
  const allEvents = mode === "simulation" ? simulation : liveEvents;
  const filtered = useMemo(() => filterEvents(allEvents, filters), [allEvents, filters]);
  const referenceTime = mode === "simulation" ? SIMULATION_END : updatedAt || new Date().toISOString();
  const summary = useMemo(() => summarize(filtered, catalog, mode === "simulation", assumptions, referenceTime), [filtered, catalog, mode, assumptions, referenceTime]);
  const dates = useMemo(() => [...new Set(allEvents.map(event => dateInLima(event.timestamp)).filter(Boolean))].sort(), [allEvents]);
  const districts = useMemo(() => [...new Set(allEvents.map(event => event.district || "Sin distrito"))].sort(), [allEvents]);
  const channels = useMemo(() => [...new Set(allEvents.map(event => event.channel || "desconocido"))].sort(), [allEvents]);
  const invalidRange = Boolean(filters.from && filters.to && filters.from > filters.to);
  const normalize = (text: string) => text.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  const availableMetrics = summary.metrics.filter(metric => (group === "Todos" || metric.group === group) && normalize(`${metric.title} ${metric.formula}`).includes(normalize(metricQuery)));
  const readings = boardReadings(summary, catalog);
  const selectedFrom = filters.from || dates[0] || "";
  const selectedTo = filters.to || dates.at(-1) || "";
  const recentEvents = useMemo(() => [...filtered].sort((a, b) => b.timestamp.localeCompare(a.timestamp)).slice(0, 6), [filtered]);
  const clearFilters = useCallback(() => setFilters({ from: "", to: "", district: "", channel: "" }), []);
  function switchMode(next: "simulation" | "live") {
    if (next === mode) return;
    setMode(next); clearFilters(); setError(""); setLiveEvents([]); setUpdatedAt(null); setPaused(false);
  }
  function recentDays(days: number) {
    const end = dates.at(-1);
    if (!end) return;
    const start = new Date(`${end}T12:00:00Z`);
    start.setUTCDate(start.getUTCDate() - days + 1);
    const from = start.toISOString().slice(0, 10);
    setFilters(current => ({ ...current, from: from < dates[0] ? dates[0] : from, to: end }));
  }

  useEffect(() => {
    const syncSection = () => setActiveSection(window.location.hash || "#board-charts");
    syncSection();
    window.addEventListener("hashchange", syncSection);
    return () => window.removeEventListener("hashchange", syncSection);
  }, []);

  useEffect(() => {
    if (mode !== "live" || paused) return;
    let active = true, running = false, accessDenied = false;
    let etag: string | null = null;
    const controller = new AbortController();
    async function refresh() {
      if (running || accessDenied || document.hidden) return;
      running = true; setLoading(true);
      const requestController = new AbortController();
      const abortRequest = () => requestController.abort();
      controller.signal.addEventListener("abort", abortRequest, { once: true });
      const timeout = window.setTimeout(abortRequest, 10000);
      try {
        const headers: Record<string, string> = {};
        if (activeToken) headers["X-Analytics-Token"] = activeToken;
        if (etag) headers["If-None-Match"] = etag;
        const response = await fetch("/api/analytics", { cache: "no-store", signal: requestController.signal, headers });
        if (response.status === 304) {
          if (active) { setUpdatedAt(new Date().toISOString()); setError(""); }
          return;
        }
        const payload = await response.json();
        if (!response.ok) {
          if (response.status === 401 || response.status === 403) {
            etag = null; accessDenied = true;
            if (active) { setLiveEvents([]); setUpdatedAt(null); }
          }
          throw new Error(payload.message || payload.error || `No se pudo consultar el tablero (${response.status}).`);
        }
        const data = payload as AnalyticsResponse;
        if (!Array.isArray(data.events) || !data.catalog) throw new Error("La respuesta del servidor no contiene eventos válidos.");
        etag = response.headers.get("ETag");
        if (active) { setLiveEvents(data.events); setCatalog(data.catalog); setUpdatedAt(data.updatedAt); setError(""); }
      } catch (failure) {
        if (active) setError(requestController.signal.aborted ? "La consulta tardó más de diez segundos. Volveremos a intentar; también puedes actualizar manualmente." : failure instanceof Error ? failure.message : "No se pudo actualizar. Conservamos la última lectura.");
      } finally {
        window.clearTimeout(timeout);
        controller.signal.removeEventListener("abort", abortRequest);
        running = false; if (active) setLoading(false);
      }
    }
    void refresh();
    const timer = window.setInterval(() => void refresh(), 5000);
    const onVisible = () => { if (!document.hidden) void refresh(); };
    document.addEventListener("visibilitychange", onVisible);
    return () => { active = false; controller.abort(); clearInterval(timer); document.removeEventListener("visibilitychange", onVisible); };
  }, [mode, paused, activeToken, revision]);

  const mainIds = ["sessions", "activation", "referrals", "results"];
  const topics = summary.pareto;
  return <main className="business-board bi-workspace">
    <a className="board-skip" href="#board-charts">Ir a los gráficos</a>
    <header className="board-topbar">
      <Link href="/" className="board-logo"><span>InmoScore<span className="board-logo-dot">.</span></span><small>INTELIGENCIA DE NEGOCIO</small></Link>
      <span className="bi-workspace-label"><BarChart3 size={15} /> Panel interno</span>
      <Link href="/" className="board-back"><ArrowLeft size={15} /> Volver a la web</Link>
    </header>
    <section className="bi-titlebar">
      <div><h1>Panorama del negocio</h1></div>
      <div className="board-mode" role="group" aria-label="Fuente del tablero">
        <button aria-pressed={mode === "simulation"} onClick={() => switchMode("simulation")}>Simulación · 300 visitantes</button>
        <button aria-pressed={mode === "live"} onClick={() => switchMode("live")}><Wifi size={13} /> Actividad registrada</button>
      </div>
    </section>
    <div className={`board-source-note ${mode === "live" ? "is-live" : ""}`}><span className="board-status-dot" /><p>{mode === "simulation" ? <><b>Datos de práctica.</b> 300 visitantes ficticios · 13 oct.–11 nov. 2026. Los importes son supuestos; no hay compras ni pagos.</> : <><b>Eventos consentidos.</b> Sesiones anónimas, no personas. Actualización cada 5 segundos · hasta 90 días y 20,000 eventos.</>}</p></div>
    {mode === "live" && <section className="board-live-controls" aria-label="Conexión al tablero"><div><span className="board-sync"><span className={`board-status-dot ${error ? "has-error" : ""}`} />{loading ? "Consultando…" : paused ? "Actualización pausada" : updatedAt ? `Última lectura: ${formatDate(updatedAt)}` : "Esperando conexión"}</span><small>Esta página no genera visitas para no alterar los resultados.</small></div><button className="board-button" onClick={() => { setPaused(false); setRevision(value => value + 1); }}><RefreshCw size={15} /> Actualizar</button><button className="board-button" aria-pressed={paused} onClick={() => setPaused(value => !value)}>{paused ? "Reanudar" : "Pausar"}</button><details className="board-access"><summary><LockKeyhole size={14} /> Acceso remoto</summary><form onSubmit={event => { event.preventDefault(); setLiveEvents([]); setUpdatedAt(null); setError(""); setActiveToken(token); setRevision(value => value + 1); }}><label htmlFor="board-token">Clave del tablero configurada por el responsable</label><input id="board-token" type="password" value={token} autoComplete="off" onChange={event => setToken(event.target.value)} /><button className="board-button" type="submit">Conectar</button><small>Solo queda en memoria de esta pestaña. En localhost no hace falta si el responsable no configuró una clave.</small></form></details></section>}
    {error && <div role="alert" className="board-error">{error} {updatedAt ? "Se conserva la última lectura; puede estar desactualizada." : "La simulación sigue disponible sin conexión."}</div>}
    <nav className="bi-report-tabs" aria-label="Secciones del informe">{REPORT_TABS.map(([href, label]) => <a key={href} className={activeSection === href ? "is-current" : undefined} aria-current={activeSection === href ? "location" : undefined} href={href}>{label}</a>)}</nav>
    <section className="board-filterbar" aria-label="Filtros de actividad"><span className="board-filter-title"><Filter size={16} /> Explorar datos</span><label>Desde<input type="date" value={filters.from} min={dates[0]} max={filters.to || dates.at(-1)} onChange={event => setFilters(current => ({ ...current, from: event.target.value }))} /></label><label>Hasta<input type="date" value={filters.to} min={filters.from || dates[0]} max={dates.at(-1)} onChange={event => setFilters(current => ({ ...current, to: event.target.value }))} /></label><label>Distrito del evento<select value={filters.district} onChange={event => setFilters(current => ({ ...current, district: event.target.value }))}><option value="">Todos</option>{districts.map(value => <option key={value}>{value}</option>)}</select></label><label>Canal declarado<select value={filters.channel} onChange={event => setFilters(current => ({ ...current, channel: event.target.value }))}><option value="">Todos</option>{channels.map(value => <option key={value} value={value}>{CHANNEL_LABELS[value] || value}</option>)}</select></label><button className="board-button" onClick={clearFilters}>Limpiar</button></section>
    <div className="board-periods"><span>Periodo rápido</span><button disabled={!dates.length} onClick={() => setFilters(current => ({ ...current, from: "", to: "" }))}>Todo el historial</button><button disabled={!dates.length} onClick={() => recentDays(7)}>Últimos 7 días disponibles</button><button disabled={!dates.length} onClick={() => recentDays(30)}>Últimos 30 días disponibles</button></div><div className="board-selection"><p role="status">{invalidRange ? "La fecha inicial debe ser anterior a la final." : `${filtered.length.toLocaleString("es-PE")} eventos seleccionados · ${selectedFrom && selectedTo ? `${selectedFrom} a ${selectedTo}` : "Sin actividad disponible"} · hora de Lima`}</p><button disabled={invalidRange} className="board-export" onClick={() => downloadFile(metricsCsv(summary.metrics, { source: mode, filters: { ...filters, from: selectedFrom, to: selectedTo }, assumptions }), `inmoscore_indicadores_${mode}.csv`)}><Download size={15} /> Descargar indicadores</button></div>
    <details className="bi-scope"><summary>Qué representan los filtros y los datos</summary><p>Los filtros seleccionan eventos, no recorridos completos. Los tres indicadores de cobertura del modelo, ubicación y advertencias describen el catálogo completo. El CSV incluye la fuente, el periodo y los supuestos utilizados. Una salida al portal original no confirma un contacto ni una compra.</p></details>
    {!filtered.length && <div className="board-empty"><h2>{mode === "live" && !liveEvents.length ? "El primer recorrido empieza en la web" : "Esta selección todavía no tiene actividad"}</h2><p>{mode === "live" && !liveEvents.length ? "Abre InmoScore en otra pestaña, acepta el registro de uso y realiza una búsqueda. Los indicadores se actualizarán en unos segundos. No hace falta crear cuentas ficticias." : "Amplía el periodo o limpia los filtros. No reemplazamos los datos que faltan con ceros inventados en porcentajes."}</p><Link href="/" target="_blank" rel="noreferrer" className="board-button">Abrir InmoScore <ArrowUpRight size={15} /></Link></div>}
    <section id="board-charts" className="bi-primary-charts" aria-label="Vista general del comportamiento">
      <PythonCharts mode={mode} daily={summary.daily} heatmap={summary.heatmap} token={activeToken} />
    </section>
    <section className="board-summary" aria-label="Resumen de actividad">{mainIds.map(id => { const metric = summary.metrics.find(item => item.id === id)!; return <div key={id}><span>{metric.title}</span><strong>{metricValue(metric)}</strong><small>{id === "sessions" ? "IDs de sesión distintos" : id === "activation" ? "Sesiones que hicieron una búsqueda" : id === "referrals" ? "No equivalen a compras" : "Entre consultas sin error técnico"}</small></div>; })}</section>
    <div className="bi-section-context"><div><h2>El recorrido dentro de la web</h2><p>Estas vistas relacionan las acciones registradas: buscar, consultar una ficha, guardar, comparar y abrir el anuncio original.</p></div><figure className="bi-section-photo"><Image src="/imagenes/bi-miraflores.png" alt="Escena ilustrativa de Miraflores" fill sizes="(max-width: 680px) 35vw, 240px" /><figcaption>Escena ilustrativa de Miraflores</figcaption></figure></div>
    <section className="board-chart-grid" aria-label="Exploración interactiva de los datos">
      <article className="board-chart-card"><div className="board-card-title"><h3>Del interés a la exploración</h3><span>Sesiones por acción</span></div><p>No exige una secuencia. Una sesión puede aparecer en varias etapas.</p><div className="board-chart" role="img" aria-label="Barras de sesiones por actividad"><ResponsiveContainer width="100%" height="100%" minWidth={0} initialDimension={{ width: 480, height: 258 }} debounce={80}><BarChart data={summary.funnel} layout="vertical" margin={{ left: 0, right: 30 }}><CartesianGrid strokeDasharray="3 3" horizontal={false} /><XAxis type="number" allowDecimals={false} /><YAxis type="category" dataKey="stage" width={80} tick={{ fontSize: 12 }} /><Tooltip /><Bar isAnimationActive={false} name="Sesiones" dataKey="count" fill="#173d31" radius={[0, 7, 7, 0]}>{summary.funnel.map((row, index) => <Cell key={row.stage} fill={COLORS[index]} />)}</Bar></BarChart></ResponsiveContainer></div><DataTable caption="Sesiones por acción" headers={["Acción", "Sesiones", "% de sesiones"]} rows={summary.funnel.map(row => [row.stage, row.count, row.percent === null ? null : `${row.percent.toFixed(1)}%`])} /></article>
      <article className="board-chart-card"><div className="board-card-title"><h3>De dónde viene el interés</h3><span>Canales</span></div><p>Canal declarado en el escenario; en uso real se muestra solo el canal registrado.</p><div className="board-chart" role="img" aria-label="Distribución circular de sesiones por canal"><ResponsiveContainer width="100%" height="100%" minWidth={0} initialDimension={{ width: 480, height: 258 }} debounce={80}><PieChart><Pie isAnimationActive={false} data={summary.channels.map(row => ({ ...row, label: CHANNEL_LABELS[row.name] || row.name }))} dataKey="sessions" nameKey="label" innerRadius={68} outerRadius={104} paddingAngle={3}>{summary.channels.map((row, index) => <Cell key={row.name} fill={COLORS[index % COLORS.length]} />)}</Pie><Tooltip /><Legend /></PieChart></ResponsiveContainer></div><DataTable caption="Actividad por canal" headers={["Canal", "Sesiones", "Sesiones con salida", "Tasa de salida"]} rows={summary.channels.map(row => [CHANNEL_LABELS[row.name] || row.name, row.sessions, row.referrals, row.rate === null ? null : `${row.rate.toFixed(1)}%`])} /></article>
      <article className="board-chart-card"><div className="board-card-title"><h3>Consultas que conviene aclarar</h3><span>Pareto de temas</span></div><p>Frecuencia y porcentaje acumulado. Son temas de consulta, no causas confirmadas de un problema.</p><div className="board-chart" role="img" aria-label="Pareto de consultas y porcentaje acumulado"><ResponsiveContainer width="100%" height="100%" minWidth={0} initialDimension={{ width: 480, height: 258 }} debounce={80}><ComposedChart data={topics} margin={{ left: -20, right: -15, bottom: 40 }}><CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey="name" tick={{ fontSize: 10 }} angle={-25} textAnchor="end" interval={0} /><YAxis yAxisId="count" allowDecimals={false} /><YAxis yAxisId="percent" orientation="right" domain={[0, 100]} unit="%" tick={{ fontSize: 11 }} /><Tooltip /><Bar isAnimationActive={false} yAxisId="count" dataKey="count" name="Consultas" fill="#86a85e" radius={[4, 4, 0, 0]} /><Line isAnimationActive={false} yAxisId="percent" dataKey="cumulative" name="Acumulado (%)" stroke="#173d31" strokeWidth={2} /></ComposedChart></ResponsiveContainer></div><DataTable caption="Consultas por tema" headers={["Tema", "Consultas", "% acumulado"]} rows={topics.map(row => [row.name, row.count, `${row.cumulative.toFixed(1)}%`])} /></article>
      <article className="board-chart-card"><div className="board-card-title"><h3>Distritos que se exploran</h3><span>Hasta 10 distritos</span></div><p>Sesiones con eventos asociados al distrito. Una sesión puede explorar varios.</p><div className="board-chart" role="img" aria-label="Sesiones por distrito"><ResponsiveContainer width="100%" height="100%" minWidth={0} initialDimension={{ width: 480, height: 258 }} debounce={80}><BarChart data={summary.districts.slice(0, 10)} layout="vertical" margin={{ left: 5, right: 10 }}><CartesianGrid strokeDasharray="3 3" horizontal={false} /><XAxis type="number" allowDecimals={false} /><YAxis type="category" dataKey="name" width={113} tick={{ fontSize: 10 }} /><Tooltip /><Bar isAnimationActive={false} dataKey="sessions" name="Sesiones" fill="#173d31" radius={[0, 5, 5, 0]} /><Bar isAnimationActive={false} dataKey="referrals" name="Sesiones con salida" fill="#d6815e" radius={[0, 5, 5, 0]} /></BarChart></ResponsiveContainer></div><DataTable caption="Actividad por distrito" headers={["Distrito", "Sesiones", "Sesiones con salida", "Tasa de salida"]} rows={summary.districts.map(row => [row.name, row.sessions, row.referrals, row.rate === null ? null : `${row.rate.toFixed(1)}%`])} /></article>
    </section>
    <BusinessVisualizations events={filtered} summary={summary} assumptions={assumptions} simulation={mode === "simulation"} />
    <BusinessComboCharts events={filtered} daily={summary.daily} districts={summary.districts} mode={mode} />
    <IndicatorCharts events={filtered} metrics={summary.metrics} catalog={catalog} mode={mode} token={activeToken} referenceTime={referenceTime} />
    <section id="board-finances" className="board-financial"><div className="board-section-heading"><div><span className="board-eyebrow">HIPÓTESIS DE NEGOCIO</span><h2>Probar números sin confundirlos con ventas</h2></div><span className="board-pill">{mode === "simulation" ? "Supuestos editables" : "Sin transacciones registradas"}</span><figure className="bi-section-photo bi-finance-photo"><Image src="/imagenes/bi-pueblo-libre.png" alt="Escena ilustrativa de Pueblo Libre" fill sizes="(max-width: 680px) 35vw, 180px" /><figcaption>Escena ilustrativa de Pueblo Libre</figcaption></figure></div><p>InmoScore no cobra ni registra compras. Este ejercicio asigna un valor ficticio a cada sesión que abre un anuncio. Los importes no representan el precio de los inmuebles ni una comisión real.</p>{mode === "simulation" ? <><details className="bi-finance-settings"><summary>Ajustar el valor del referido y los costos</summary><div className="board-assumptions">{([{ key: "referralValue", label: "Valor por referido (S/)" }, { key: "marketingCost", label: "Captación del segmento (S/)" }, { key: "fixedCost", label: "Costo fijo del segmento (S/)" }, { key: "costPerSession", label: "Costo por sesión (S/)" }] as const).map(field => <label key={field.key}>{field.label}<input type="number" min="0" max="1000000" step="0.1" value={assumptions[field.key]} onChange={event => { const value = Number(event.target.value); if (Number.isFinite(value) && value >= 0 && value <= 1000000) setAssumptions(current => ({ ...current, [field.key]: value })); }} /></label>)}</div><p className="board-chart-note">Los costos fijos y de captación se asignan al segmento seleccionado; al filtrar no se prorratean. Puedes modificarlos para comparar hipótesis.</p><button className="board-reset-assumptions" onClick={() => setAssumptions(DEFAULT_ASSUMPTIONS)}>Restablecer supuestos iniciales</button></details><p className="bi-finance-chart-link"><a href="#board-indicator-charts">Ver los gráficos del escenario</a> y seleccionar <b>Finanzas</b>. Los cinco gráficos se actualizan al modificar estos supuestos.</p></> : <div className="board-finance-empty">Los cinco indicadores financieros quedan <b>sin datos</b> en actividad registrada. Usa la simulación para explorar el escenario económico. Para obtener ingresos reales haría falta un proceso comercial validado y datos de transacciones.</div>}</section>
    <section className="bi-city-stories bi-catalog-scene" aria-label="Contexto visual de Lima"><figure><div className="bi-city-image"><Image src="/imagenes/bi-barranco.png" alt="Escena ilustrativa de Barranco, no corresponde a un aviso del catálogo" fill sizes="90vw" /></div><figcaption>Escena ilustrativa de Barranco</figcaption></figure></section>
    <details id="board-indicators" className="bi-expander"><summary><span>Consultar los 30 indicadores</span><small>Definiciones, fórmulas y resultados por área</small></summary><div className="bi-expander-content"><div className="board-metric-search"><label htmlFor="board-metric-search">Buscar un indicador</label><input id="board-metric-search" type="search" value={metricQuery} placeholder="Por ejemplo: búsquedas, costo o ubicación" onChange={event => setMetricQuery(event.target.value)} /><span role="status">{availableMetrics.length} de 30 indicadores</span></div><div className="board-groups" role="group" aria-label="Filtrar indicadores por área">{GROUPS.map(value => <button key={value} aria-pressed={group === value} onClick={() => setGroup(value)}>{value}{value !== "Todos" && <small>{summary.metrics.filter(item => item.group === value).length}</small>}</button>)}</div>{!availableMetrics.length && <p className="board-no-metrics">No hay indicadores con ese texto en esta área. Prueba otro término o selecciona Todos.</p>}<div className="board-metric-grid">{availableMetrics.map(metric => <MetricCard key={metric.id} metric={metric} />)}</div></div></details>
    <details id="board-readings" className="bi-expander"><summary><span>Notas para revisar con el equipo</span><small>Observaciones y siguientes pasos a partir de esta selección</small></summary>
    <section className="board-readings" aria-label="Lecturas para el equipo"><div className="board-readings-heading"><div><span className="board-eyebrow">DE LOS DATOS A LA REVISIÓN</span><h2>Qué pueden revisar ahora</h2></div><span>{mode === "simulation" ? "Ejercicio con actividad ficticia" : "Lectura de la actividad seleccionada"}</span></div><div className="board-readings-grid">{readings.map((reading, index) => <article key={reading.id}><span className="board-reading-number">0{index + 1}</span><small>{reading.scope}</small><h3>{reading.title}</h3><p><b>{reading.observation}</b></p><p>{reading.nextStep}</p></article>)}</div>{!readings.length && <p>Cuando haya actividad o datos del catálogo, verán observaciones concretas para revisar.</p>}<p className="board-reading-note">Son observaciones de los datos disponibles. No identifican causas, no predicen ventas y no sustituyen una prueba con usuarios.</p></section>
    </details>
    <details id="board-catalog" className="bi-expander"><summary><span>Calidad del catálogo y últimas interacciones</span><small>Datos de origen y evidencia detrás de los gráficos</small></summary><div className="bi-expander-content">
    <section className="board-bottom-grid"><article className="board-chart-card"><div className="board-card-title"><h3>Catálogo que sostiene las recomendaciones</h3><span>Datos del proyecto</span></div><div className="board-catalog-count"><b>{catalog.total.toLocaleString("es-PE")}</b><span>avisos · {catalog.districts} distritos</span></div><p>Este bloque utiliza el catálogo completo y no cambia al filtrar actividad. {catalog.capturedAt ? `Última fecha de observación incluida: ${dateInLima(catalog.capturedAt.includes("T") ? catalog.capturedAt : `${catalog.capturedAt}T12:00:00Z`)}.` : "Fecha de observación no informada."} La disponibilidad de los avisos debe verificarse.</p><ul className="board-check-list"><li><Check size={16} /> {catalog.withModel.toLocaleString("es-PE")} con referencia de precio utilizable</li><li><Check size={16} /> {catalog.preciseLocation.toLocaleString("es-PE")} con ubicación precisa</li><li><CircleHelp size={16} /> {catalog.withWarnings.toLocaleString("es-PE")} con al menos una advertencia</li></ul><p className="board-chart-note">Tener una predicción no garantiza su exactitud. Los indicadores de la zona son distritales, no atributos verificados de cada vivienda.</p></article><article className="board-chart-card"><div className="board-card-title"><h3>Últimas interacciones de la selección</h3><span>{mode === "simulation" ? "Ficticias" : "Registradas"}</span></div><ol className="board-event-list">{recentEvents.map(event => <li key={event.id}><span className="board-event-dot" /><div><b>{EVENT_NAMES[event.type] || event.type}</b><small>{event.district || "Sin distrito asociado"}</small></div><time dateTime={event.timestamp}>{new Date(event.timestamp).toLocaleTimeString("es-PE", { timeZone: "America/Lima", hour: "2-digit", minute: "2-digit" })}</time></li>)}</ol>{!filtered.length && <p>Las interacciones aparecerán aquí cuando haya datos.</p>}<p className="board-chart-note">No se muestran nombres, correos, ingresos ni mensajes de los visitantes.</p></article></section>
    </div></details>
    <footer className="board-footer"><span>InmoScore · Lecturas claras para decisiones mejor informadas.</span><span>{mode === "simulation" ? `Simulación reproducible · semilla ${SIMULATION_SEED}` : "Actualización por consulta periódica · 5 s"}</span></footer>
  </main>;
}
