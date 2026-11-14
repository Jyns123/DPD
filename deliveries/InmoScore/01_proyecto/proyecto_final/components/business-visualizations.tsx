"use client";

import { useMemo } from "react";
import {
  Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Funnel, FunnelChart,
  Legend, Pie, PieChart, ResponsiveContainer, Scatter, ScatterChart,
  Tooltip, Treemap, XAxis, YAxis, ZAxis,
} from "recharts";
import { businessVisuals } from "../lib/business-visuals";
import { metricValue, type AnalyticsEvent, type FinancialAssumptions, type Metric, type BreakdownRow, type DailyRow } from "../lib/business-metrics";

const COLORS = ["#315f48", "#86a85e", "#d6815e", "#abc3bc", "#c3a462", "#879ba4"];
const ACTIONS = [
  { key: "Solo actividad", color: "#cbdacf" },
  { key: "Búsqueda", color: "#87a861" },
  { key: "Ficha", color: "#446f53" },
  { key: "Salida", color: "#d6815e" },
] as const;
type Summary = { daily: DailyRow[]; districts: BreakdownRow[]; metrics: Metric[] };

function ChartTable({ caption, headers, rows }: { caption: string; headers: string[]; rows: (string | number)[][] }) {
  return <details className="bi-visual-data"><summary>Ver datos del gráfico</summary><div className="board-table-scroll"><table><caption>{caption}</caption><thead><tr>{headers.map(header => <th scope="col" key={header}>{header}</th>)}</tr></thead><tbody>{rows.length ? rows.map((row, index) => <tr key={index}>{row.map((value, column) => <td key={column}>{value}</td>)}</tr>) : <tr><td colSpan={headers.length}>Sin observaciones en esta selección.</td></tr>}</tbody></table></div></details>;
}
function Card({ title, tag, note, children, wide = false }: { title: string; tag: string; note: string; children: React.ReactNode; wide?: boolean }) {
  return <article className={`bi-visual-card ${wide ? "bi-visual-wide" : ""}`}><header><div><small>{tag}</small><h3>{title}</h3></div></header><p>{note}</p>{children}</article>;
}
function EmptyChart({ label }: { label: string }) {
  return <div className="bi-visual-empty">{label}</div>;
}
function Waterfall({ metrics }: { metrics: Metric[] }) {
  const value = (id: string) => metrics.find(metric => metric.id === id)?.value ?? 0;
  const income = value("income"), marketing = value("marketing"), operating = value("operating"), balance = value("balance");
  const bars = [
    { name: "Valor supuesto", from: 0, to: income, color: COLORS[0], label: income },
    { name: "Captación", from: income, to: income - marketing, color: COLORS[2], label: -marketing },
    { name: "Operación", from: income - marketing, to: balance, color: COLORS[2], label: -operating },
    { name: "Saldo", from: 0, to: balance, color: balance < 0 ? COLORS[2] : COLORS[1], label: balance },
  ];
  const maximum = Math.max(1, ...bars.flatMap(bar => [bar.from, bar.to]));
  const minimum = Math.min(0, ...bars.flatMap(bar => [bar.from, bar.to]));
  const span = maximum - minimum || 1;
  const y = (number: number) => 20 + (maximum - number) / span * 185;
  return <div className="bi-waterfall" role="img" aria-label="Puente del escenario hipotético: valor de referidos menos captación y operación igual saldo"><svg viewBox="0 0 690 268" preserveAspectRatio="xMidYMid meet">
    <line x1="36" x2="660" y1={y(0)} y2={y(0)} stroke="#9aa99a" strokeWidth="1.2" />
    {bars.slice(0, 2).map((bar, index) => <line key={bar.name} x1={180 + index * 155} x2={220 + index * 155} y1={y(bar.to)} y2={y(bar.to)} stroke="#aebcaf" strokeDasharray="4 3" />)}
    {bars.map((bar, index) => {
      const x = 65 + index * 155;
      const top = Math.min(y(bar.from), y(bar.to));
      const height = Math.max(3, Math.abs(y(bar.from) - y(bar.to)));
      return <g key={bar.name}><rect x={x} y={top} width="115" height={height} rx="5" fill={bar.color}><title>{bar.name}: {metricValue({ value: bar.label, unit: "money" })}</title></rect><text x={x + 57} y="233" textAnchor="middle" fontSize="11" fill="#526855">{bar.name}</text><text x={x + 57} y={Math.max(14, top - 6)} textAnchor="middle" fontSize="10" fill="#345343">{metricValue({ value: bar.label, unit: "money" })}</text></g>;
    })}
  </svg></div>;
}

export default function BusinessVisualizations({ events, summary, assumptions, simulation }: {
  events: AnalyticsEvent[]; summary: Summary; assumptions: FinancialAssumptions; simulation: boolean;
}) {
  const visuals = useMemo(() => businessVisuals(events), [events]);
  const totalSearches = visuals.searchOutcomes.reduce((sum, item) => sum + item.value, 0);
  const maxMatrix = visuals.maxMatrix || 1;
  const scatter = summary.districts.slice(0, 12).filter(item => item.rate !== null).map(item => ({ name: item.name, sessions: item.sessions, rate: item.rate, size: item.sessions }));
  const measured = visuals.latencies.reduce((sum, item) => sum + item.count, 0);
  const daily = summary.daily.map(item => ({ ...item, label: item.date.slice(5) }));
  const countText = (value: number) => value.toLocaleString("es-PE");
  return <section id="board-business-visuals" className="bi-deep-dive" aria-labelledby="bi-deep-dive-heading">
    <div className="bi-deep-dive-heading"><div><span className="board-eyebrow">EXPLORACIÓN DEL NEGOCIO</span><h2 id="bi-deep-dive-heading">Del uso de la web a las decisiones</h2><p>Nueve vistas amplias para leer el recorrido, los canales, la calidad de búsqueda, el soporte y el escenario económico. Todas siguen el periodo, el distrito y el canal elegidos arriba.</p></div><span className="bi-deep-dive-count">9 vistas de análisis</span></div>
    <div className="bi-visual-chapter"><span>01</span><div><h3>Recorrido y captación</h3><p>Primero comprobamos si una sesión avanza hacia una búsqueda, una ficha y el enlace al aviso.</p></div></div>
    <div className="bi-visual-grid">
      <Card title="Embudo secuencial" tag="RECORRIDO" note="Cada etapa exige que la acción anterior haya ocurrido antes, dentro de la selección. «Salida» significa abrir el aviso externo; no registra una compra." wide>
        {visuals.journey[0].count ? <><div className="bi-large-chart bi-funnel-chart" role="img" aria-label="Embudo de sesiones desde actividad hasta salida al aviso"><ResponsiveContainer width="100%" height="100%" minWidth={0} initialDimension={{ width: 600, height: 305 }} debounce={80}><FunnelChart><Tooltip formatter={(value) => [countText(Number(value)), "Sesiones"]} /><Funnel dataKey="count" data={visuals.journey.map((row, index) => ({ ...row, fill: COLORS[index] }))} isAnimationActive={false} /></FunnelChart></ResponsiveContainer></div><div className="bi-funnel-legend" aria-label="Etapas del embudo">{visuals.journey.map((row, index) => <div key={row.name}><i style={{ background: COLORS[index] }} /><span>{row.name}</span><strong>{countText(row.count)}</strong><small>{row.percentOfStart === null ? "—" : `${row.percentOfStart.toFixed(1)}%`}</small></div>)}</div></> : <EmptyChart label="Aún no hay sesiones para formar el embudo." />}
        <div className="bi-visual-callout">De {countText(visuals.journey[0].count)} sesiones seleccionadas, {countText(visuals.journey[3].count)} llegaron al enlace externo después de buscar y abrir una ficha.</div>
        <ChartTable caption="Etapas del embudo secuencial" headers={["Etapa", "Sesiones", "% del inicio", "% de la etapa anterior"]} rows={visuals.journey.map(row => [row.name, row.count, row.percentOfStart === null ? "—" : `${row.percentOfStart.toFixed(1)}%`, row.percentOfPrevious === null ? "—" : `${row.percentOfPrevious.toFixed(1)}%`])} />
      </Card>
      <Card title="Cómo terminan las sesiones" tag="CANALES" note="Cada sesión se cuenta una vez, en su acción más avanzada. El canal corresponde al primer evento seleccionado." wide>
        {visuals.channelActions.length ? <div className="bi-large-chart" role="img" aria-label="Barras apiladas de sesiones por canal y acción máxima"><ResponsiveContainer width="100%" height="100%" minWidth={0} initialDimension={{ width: 600, height: 305 }} debounce={80}><BarChart data={visuals.channelActions} margin={{ left: 0, right: 12, bottom: 2 }}><CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey="name" tick={{ fontSize: 11 }} /><YAxis allowDecimals={false} /><Tooltip /><Legend />{ACTIONS.map(action => <Bar key={action.key} dataKey={action.key} name={action.key} stackId="actions" fill={action.color} isAnimationActive={false} />)}</BarChart></ResponsiveContainer></div> : <EmptyChart label="Aún no hay sesiones con canal en esta selección." />}
        <ChartTable caption="Sesiones por canal y acción máxima" headers={["Canal", "Solo actividad", "Búsqueda", "Ficha", "Salida", "Total"]} rows={visuals.channelActions.map(row => [row.name, row["Solo actividad"], row["Búsqueda"], row["Ficha"], row["Salida"], row.total])} />
      </Card>
    </div>
    <div className="bi-visual-chapter"><span>02</span><div><h3>Calidad de la búsqueda</h3><p>Distinguimos los resultados encontrados, los filtros sin coincidencias y los errores técnicos.</p></div></div>
    <div className="bi-visual-grid">
      <Card title="Resultado de cada búsqueda" tag="CALIDAD" note="El anillo cuenta búsquedas, no visitantes. «Sin coincidencias» es una respuesta válida del buscador.">
        {totalSearches ? <div className="bi-large-chart" role="img" aria-label="Distribución de resultados, búsquedas vacías, errores y búsquedas sin medición"><ResponsiveContainer width="100%" height="100%" minWidth={0} initialDimension={{ width: 480, height: 300 }} debounce={80}><PieChart><Pie data={visuals.searchOutcomes.filter(row => row.value)} dataKey="value" nameKey="name" innerRadius={67} outerRadius={111} paddingAngle={3} isAnimationActive={false}>{visuals.searchOutcomes.filter(row => row.value).map((row, index) => <Cell key={row.name} fill={COLORS[index]} />)}</Pie><Tooltip /><Legend /></PieChart></ResponsiveContainer></div> : <EmptyChart label="Aún no hay búsquedas registradas." />}
        <ChartTable caption="Resultado de las búsquedas" headers={["Resultado", "Búsquedas"]} rows={visuals.searchOutcomes.map(row => [row.name, row.value])} />
      </Card>
      <Card title="Tiempo observado de respuesta" tag="RENDIMIENTO" note={`Histograma de ${countText(measured)} búsquedas con tiempo medido. ${countText(visuals.searchesWithoutDuration)} quedaron sin duración; no se colocan en un intervalo ficticio.`}>
        {measured ? <div className="bi-large-chart" role="img" aria-label="Histograma de duración observada de búsqueda"><ResponsiveContainer width="100%" height="100%" minWidth={0} initialDimension={{ width: 480, height: 300 }} debounce={80}><BarChart data={visuals.latencies} margin={{ left: 0, right: 10, bottom: 0 }}><CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey="name" tick={{ fontSize: 10 }} /><YAxis allowDecimals={false} /><Tooltip /><Bar name="Búsquedas" dataKey="count" fill="#315f48" radius={[4, 4, 0, 0]} isAnimationActive={false} /></BarChart></ResponsiveContainer></div> : <EmptyChart label="Aún no se han medido tiempos de búsqueda." />}
        <ChartTable caption="Duración de búsquedas" headers={["Intervalo", "Búsquedas"]} rows={visuals.latencies.map(row => [row.name, row.count])} />
      </Card>
      <Card title="Actividad a lo largo del periodo" tag="TENDENCIA" note="Áreas superpuestas por día de Lima. Las búsquedas pueden superar las sesiones porque una sesión puede buscar varias veces." wide>
        {daily.length ? <div className="bi-large-chart" role="img" aria-label="Áreas por día de sesiones, búsquedas y sesiones con salida"><ResponsiveContainer width="100%" height="100%" minWidth={0} initialDimension={{ width: 600, height: 300 }} debounce={80}><AreaChart data={daily} margin={{ left: 0, right: 15, bottom: 0 }}><CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey="label" tick={{ fontSize: 10 }} minTickGap={20} /><YAxis allowDecimals={false} /><Tooltip labelFormatter={(_, payload) => payload?.[0]?.payload?.date || ""} /><Legend /><Area name="Sesiones" type="monotone" dataKey="sessions" stroke="#315f48" fill="#315f48" fillOpacity={.15} isAnimationActive={false} /><Area name="Búsquedas" type="monotone" dataKey="searches" stroke="#86a85e" fill="#86a85e" fillOpacity={.14} isAnimationActive={false} /><Area name="Sesiones con salida" type="monotone" dataKey="referrals" stroke="#d6815e" fill="#d6815e" fillOpacity={.13} isAnimationActive={false} /></AreaChart></ResponsiveContainer></div> : <EmptyChart label="Aún no hay actividad diaria." />}
        <ChartTable caption="Actividad diaria" headers={["Día (Lima)", "Sesiones", "Búsquedas", "Sesiones con salida"]} rows={daily.map(row => [row.date, row.sessions, row.searches, row.referrals])} />
      </Card>
    </div>
    <div className="bi-visual-chapter"><span>03</span><div><h3>Segmentos y consultas</h3><p>Vemos dónde se concentra el interés y qué preguntas aparecen en la ayuda.</p></div></div>
    <div className="bi-visual-grid">
      <Card title="Interés y salidas por distrito" tag="SEGMENTOS" note="Cada punto es un distrito del evento. Eje horizontal: sesiones; eje vertical: porcentaje de sesiones con salida. El tamaño también representa sesiones.">
        {scatter.length ? <div className="bi-large-chart" role="img" aria-label="Diagrama de dispersión de sesiones y tasa de salida por distrito"><ResponsiveContainer width="100%" height="100%" minWidth={0} initialDimension={{ width: 480, height: 300 }} debounce={80}><ScatterChart margin={{ top: 8, right: 23, bottom: 12, left: 3 }}><CartesianGrid strokeDasharray="3 3" /><XAxis type="number" dataKey="sessions" name="Sesiones" allowDecimals={false} label={{ value: "Sesiones", position: "insideBottom", offset: -9, fontSize: 10 }} /><YAxis type="number" dataKey="rate" name="Salida" unit="%" domain={[0, 100]} label={{ value: "% salida", angle: -90, position: "insideLeft", fontSize: 10 }} /><ZAxis type="number" dataKey="size" range={[70, 420]} /><Tooltip cursor={{ strokeDasharray: "3 3" }} /><Scatter name="Distritos" data={scatter} fill="#315f48" isAnimationActive={false} /></ScatterChart></ResponsiveContainer></div> : <EmptyChart label="Aún no hay distritos con sesiones para comparar." />}
        <ChartTable caption="Sesiones y salidas por distrito" headers={["Distrito", "Sesiones", "Sesiones con salida", "Tasa de salida"]} rows={summary.districts.map(row => [row.name, row.sessions, row.referrals, row.rate === null ? "—" : `${row.rate.toFixed(1)}%`])} />
      </Card>
      <Card title="Cruce entre distrito y canal" tag="MATRIZ" note="Cada celda cuenta sesiones con eventos de ese canal y distrito. Una misma sesión puede aparecer en más de una celda si exploró varios distritos.">
        {visuals.matrix.length ? <div className="bi-matrix-scroll"><table className="bi-channel-matrix"><caption>Sesiones observadas por distrito y canal</caption><thead><tr><th scope="col">Distrito</th>{visuals.matrixChannels.map(channel => <th key={channel.code} scope="col">{channel.name}</th>)}</tr></thead><tbody>{visuals.matrix.map(row => <tr key={row.district}><th scope="row">{row.district}</th>{row.cells.map(cell => <td key={cell.channel} style={{ backgroundColor: `rgba(49,95,72,${.08 + .78 * cell.count / maxMatrix})`, color: cell.count > maxMatrix * .56 ? "#fff" : "#254b36" }} title={`${row.district} · ${cell.channel}: ${cell.count} sesiones`}>{cell.count}</td>)}</tr>)}</tbody></table></div> : <EmptyChart label="Aún no hay datos cruzados por canal y distrito." />}
      </Card>
      <Card title="Temas consultados al asistente" tag="SOPORTE" note="El mosaico refleja categorías de preguntas recibidas. No guarda el texto libre y no equivale a tickets resueltos." wide>
        {visuals.topicAreas.length ? <><div className="bi-large-chart bi-treemap" role="img" aria-label="Mosaico de frecuencia de temas consultados"><ResponsiveContainer width="100%" height="100%" minWidth={0} initialDimension={{ width: 600, height: 300 }} debounce={80}><Treemap data={visuals.topicAreas} dataKey="size" nameKey="name" stroke="#fff" fill="#315f48" isAnimationActive={false}><Tooltip /></Treemap></ResponsiveContainer></div><div className="bi-topic-legend">{visuals.topicAreas.slice(0, 8).map(topic => <span key={topic.name}><i style={{ background: COLORS[0] }} />{topic.name} <b>{topic.size}</b></span>)}</div></> : <EmptyChart label="Aún no hay consultas al asistente en la selección." />}
        <ChartTable caption="Consultas al asistente por tema" headers={["Tema", "Preguntas"]} rows={visuals.topicAreas.map(row => [row.name, row.size])} />
      </Card>
    </div>
    <div className="bi-visual-chapter"><span>04</span><div><h3>Escenario económico</h3><p>El puente permite probar supuestos sin atribuir ingresos reales al proyecto.</p></div></div>
    <div className="bi-visual-grid">
      <Card title="Puente de valor, costos y saldo" tag="FINANZAS · SIMULACIÓN" note={simulation ? `Escenario editable: S/ ${assumptions.referralValue} por salida, S/ ${assumptions.marketingCost} de captación, S/ ${assumptions.fixedCost} fijo y S/ ${assumptions.costPerSession} por sesión. No son ventas ni gastos comprobados.` : "La web no registra transacciones, comisiones ni costos reales. Este gráfico permanece sin datos en actividad registrada."} wide>
        {simulation ? <><Waterfall metrics={summary.metrics} /><ChartTable caption="Puente de resultados hipotéticos" headers={["Concepto", "Importe"]} rows={["income", "marketing", "operating", "balance"].map(id => { const metric = summary.metrics.find(item => item.id === id)!; return [metric.title, metricValue(metric)]; })} /></> : <EmptyChart label="Sin transacciones registradas. Cambia a Simulación para explorar supuestos." />}
      </Card>
    </div>
    <p className="bi-deep-dive-note">Los gráficos describen eventos consentidos o el escenario ficticio de 300 sesiones. Los filtros recortan eventos, por lo que un embudo filtrado puede comenzar después de la primera visita. Ningún gráfico acredita ventas, ganancias o el comportamiento de personas identificadas.</p>
  </section>;
}
