"use client";

import { useMemo, useState } from "react";
import {
  Bar, CartesianGrid, ComposedChart, Legend, Line, ResponsiveContainer,
  Tooltip, XAxis, YAxis,
} from "recharts";
import { comboAnalytics, districtDrilldown } from "../lib/combo-analytics";
import type { AnalyticsEvent, BreakdownRow, DailyRow } from "../lib/business-metrics";

const INK = "#173d31";
const LIME = "#86a85e";
const CLAY = "#d6815e";
const SAGE = "#abc3bc";
const GRID = "#e7ede8";
const fmt = (value: number) => value.toLocaleString("es-PE");
const pct = (value: number | null) => value === null ? "Sin dato" : `${value.toFixed(1)}%`;
const shortDate = (date: string) => date.slice(5);
const shortLabel = (value: string) => value.length > 13 ? `${value.slice(0, 12)}…` : value;
const tooltipValue = (value: unknown, name: unknown): [string, string] => {
  const label = String(name);
  const number = Number(value);
  if (!Number.isFinite(number)) return ["Sin dato", label];
  if (label.includes("(%)")) return [`${number.toFixed(1)}%`, label];
  if (label.includes("(ms)")) return [`${fmt(number)} ms`, label];
  return [fmt(number), label];
};

function Card({ title, eyebrow, description, children, wide = false }: {
  title: string; eyebrow: string; description: string; children: React.ReactNode; wide?: boolean;
}) {
  return <article className={`combo-card ${wide ? "combo-wide" : ""}`}>
    <div className="combo-card-intro"><span>{eyebrow}</span><h3>{title}</h3><p>{description}</p></div>
    {children}
  </article>;
}
function Empty({ children }: { children: React.ReactNode }) {
  return <div className="combo-empty">{children}</div>;
}
function Table({ caption, headings, rows }: { caption: string; headings: string[]; rows: (string | number)[][] }) {
  return <details className="combo-table"><summary>Consultar los valores exactos</summary><div className="combo-table-scroll"><table><caption>{caption}</caption><thead><tr>{headings.map(item => <th key={item} scope="col">{item}</th>)}</tr></thead><tbody>{rows.length ? rows.map((row, index) => <tr key={index}>{row.map((value, column) => <td key={column}>{value}</td>)}</tr>) : <tr><td colSpan={headings.length}>Sin eventos en esta selección.</td></tr>}</tbody></table></div></details>;
}
function CountAxis() { return <YAxis yAxisId="count" allowDecimals={false} tick={{ fontSize: 12, fill: "#57705d" }} width={42} />; }
function PercentAxis() { return <YAxis yAxisId="rate" orientation="right" domain={[0, 100]} unit="%" tick={{ fontSize: 12, fill: "#57705d" }} width={49} />; }
function DateAxis() { return <XAxis dataKey="date" tickFormatter={shortDate} minTickGap={22} tick={{ fontSize: 12, fill: "#57705d" }} />; }
function Chart({ children, label, leftAxis, rightAxis, tall = false }: { children: React.ReactNode; label: string; leftAxis: string; rightAxis: string; tall?: boolean }) {
  return <div className={`combo-chart ${tall ? "combo-chart-tall" : ""}`} role="img" aria-label={`${label}. Los valores exactos están en la tabla inferior.`}>
    <div className="combo-axis-key"><span>Izquierda · {leftAxis}</span><span>Derecha · {rightAxis}</span></div>
    <div className="combo-chart-plot"><ResponsiveContainer width="100%" height="100%" minWidth={0} initialDimension={{ width: 620, height: 320 }} debounce={80}>{children}</ResponsiveContainer></div>
  </div>;
}

export default function BusinessComboCharts({ events, daily, districts, mode }: {
  events: AnalyticsEvent[]; daily: DailyRow[]; districts: BreakdownRow[]; mode: "simulation" | "live";
}) {
  const data = useMemo(() => comboAnalytics(events, daily, districts), [events, daily, districts]);
  const [chosenDistrict, setChosenDistrict] = useState("");
  const district = data.districts.some(row => row.name === chosenDistrict) ? chosenDistrict : data.districts[0]?.name || "";
  const districtDays = useMemo(() => districtDrilldown(events, district), [events, district]);
  const totalSearches = data.quality.reduce((sum, row) => sum + row.withResults + row.empty + row.failed + row.unmeasured, 0);
  const totalVotes = data.support.reduce((sum, row) => sum + row.votes, 0);

  return <section id="board-combo-charts" className="combo-report" aria-labelledby="combo-report-title">
    <header className="combo-report-header"><div><span className="board-eyebrow">LECTURA CRUZADA</span><h2 id="combo-report-title">Seis gráficos para entender el recorrido completo</h2><p>Combinamos volumen, proporciones y tiempo de respuesta en la misma vista. Cada gráfico responde a los filtros superiores y muestra sus valores en una tabla.</p></div><span className="combo-count">6 vistas combinadas · {mode === "simulation" ? "simulación" : "actividad registrada"}</span></header>
    <div className="combo-grid">
      <Card eyebrow="NEGOCIO · EVOLUCIÓN" title="Búsquedas y salidas por día" description="Las columnas cuentan búsquedas. La línea usa sesiones con salida al aviso divididas por sesiones de ese día. Abrir un aviso externo no confirma una compra." wide>
        {data.activity.length ? <Chart label="Búsquedas en columnas y tasa diaria de salida al aviso en línea" leftAxis="búsquedas" rightAxis="% de sesiones con salida"><ComposedChart data={data.activity} margin={{ top: 12, right: 5, bottom: 4, left: 2 }}><CartesianGrid stroke={GRID} strokeDasharray="3 3" vertical={false} /><DateAxis /><CountAxis /><PercentAxis /><Tooltip formatter={tooltipValue} /><Legend verticalAlign="top" height={35} /><Bar yAxisId="count" dataKey="searches" name="Búsquedas" fill={LIME} radius={[3, 3, 0, 0]} isAnimationActive={false} /><Line yAxisId="rate" dataKey="outboundRate" name="Sesiones con salida (%)" stroke={INK} strokeWidth={2.8} dot={{ r: 2 }} activeDot={{ r: 5 }} connectNulls={false} isAnimationActive={false} /></ComposedChart></Chart> : <Empty>Registra una búsqueda para ver la evolución diaria.</Empty>}
        <Table caption="Búsquedas y salidas por día" headings={["Día de Lima", "Sesiones", "Búsquedas", "Sesiones con salida", "Tasa de salida"]} rows={data.activity.map(row => [row.date, row.sessions, row.searches, row.referrals, pct(row.outboundRate)])} />
      </Card>

      <Card eyebrow="CALIDAD + TI" title="Resultado de búsqueda y rapidez" description="Las columnas apiladas separan resultados, cero coincidencias, fallas y búsquedas sin resultado informado. La línea es el P95 de búsquedas con tiempo medido; los tiempos faltantes no se convierten en cero." wide>
        {data.quality.length ? <Chart label="Resultados de búsqueda apilados por día y tiempo P95 en una línea" leftAxis="búsquedas" rightAxis="P95 en ms" tall><ComposedChart data={data.quality} margin={{ top: 12, right: 5, bottom: 4, left: 2 }}><CartesianGrid stroke={GRID} strokeDasharray="3 3" vertical={false} /><DateAxis /><CountAxis /><YAxis yAxisId="ms" orientation="right" unit=" ms" tick={{ fontSize: 12, fill: "#57705d" }} width={65} /><Tooltip formatter={tooltipValue} /><Legend verticalAlign="top" height={55} /><Bar yAxisId="count" stackId="searches" dataKey="withResults" name="Con resultados" fill={INK} isAnimationActive={false} /><Bar yAxisId="count" stackId="searches" dataKey="empty" name="Sin coincidencias" fill={LIME} isAnimationActive={false} /><Bar yAxisId="count" stackId="searches" dataKey="failed" name="Error" fill={CLAY} isAnimationActive={false} /><Bar yAxisId="count" stackId="searches" dataKey="unmeasured" name="Resultado no informado" fill={SAGE} isAnimationActive={false} /><Line yAxisId="ms" dataKey="p95" name="Tiempo P95 (ms)" stroke="#ad714e" strokeWidth={2.6} dot={{ r: 2 }} connectNulls={false} isAnimationActive={false} /></ComposedChart></Chart> : <Empty>Aún no hay búsquedas registradas para este cruce.</Empty>}
        <p className="combo-footnote">{fmt(totalSearches)} búsquedas en el periodo. El P95 solo usa las que informaron duración.</p>
        <Table caption="Resultado y duración de búsquedas por día" headings={["Día", "Con resultados", "Sin coincidencias", "Error", "Resultado no informado", "Con tiempo", "P95"]} rows={data.quality.map(row => [row.date, row.withResults, row.empty, row.failed, row.unmeasured, row.measured, row.p95 === null ? "Sin dato" : `${fmt(row.p95)} ms`])} />
      </Card>

      <Card eyebrow="CAPTACIÓN · CANALES" title="Canales, exploración y salidas" description="Las barras apiladas asignan cada sesión a su acción más avanzada. La línea divide las sesiones con salida entre todas las sesiones de ese canal. En uso real, «Sin canal» indica que no se conoce la procedencia." wide>
        {data.channels.length ? <Chart label="Sesiones apiladas por acción máxima y tasa de salida por canal" leftAxis="sesiones" rightAxis="% con salida"><ComposedChart data={data.channels} margin={{ top: 12, right: 5, bottom: 4, left: 2 }}><CartesianGrid stroke={GRID} strokeDasharray="3 3" vertical={false} /><XAxis dataKey="name" tick={{ fontSize: 12, fill: "#57705d" }} /><CountAxis /><PercentAxis /><Tooltip formatter={tooltipValue} /><Legend verticalAlign="top" height={55} /><Bar yAxisId="count" stackId="actions" dataKey="Solo actividad" fill={SAGE} isAnimationActive={false} /><Bar yAxisId="count" stackId="actions" dataKey="Búsqueda" fill={LIME} isAnimationActive={false} /><Bar yAxisId="count" stackId="actions" dataKey="Ficha" fill={INK} isAnimationActive={false} /><Bar yAxisId="count" stackId="actions" dataKey="Salida" fill={CLAY} isAnimationActive={false} /><Line yAxisId="rate" dataKey="outboundRate" name="Salida (%)" stroke="#a4583f" strokeWidth={2.8} dot={{ r: 4 }} connectNulls={false} isAnimationActive={false} /></ComposedChart></Chart> : <Empty>Aún no hay sesiones con canal registrado.</Empty>}
        <Table caption="Sesiones por canal y acción máxima" headings={["Canal", "Solo actividad", "Búsqueda", "Ficha", "Salida", "Tasa de salida"]} rows={data.channels.map(row => [row.name, row["Solo actividad"], row.Búsqueda, row.Ficha, row.Salida, pct(row.outboundRate)])} />
      </Card>

      <Card eyebrow="INTERÉS · DISTRITOS" title="Interés frente a salidas por distrito" description="Las columnas muestran sesiones con actividad del distrito. La línea muestra qué porcentaje de esas sesiones abrió un aviso externo. Un mismo recorrido puede explorar más de un distrito." wide>
        {data.districts.length ? <Chart label="Sesiones en columnas y tasa de salida por distrito" leftAxis="sesiones" rightAxis="% con salida" tall><ComposedChart data={data.districts} margin={{ top: 10, right: 4, bottom: 48, left: 2 }}><CartesianGrid stroke={GRID} strokeDasharray="3 3" vertical={false} /><XAxis dataKey="name" tickFormatter={shortLabel} interval={0} angle={-27} textAnchor="end" tick={{ fontSize: 12, fill: "#57705d" }} /><CountAxis /><PercentAxis /><Tooltip formatter={tooltipValue} /><Legend verticalAlign="top" height={35} /><Bar yAxisId="count" dataKey="sessions" name="Sesiones" fill={LIME} radius={[3, 3, 0, 0]} isAnimationActive={false} /><Line yAxisId="rate" dataKey="outboundRate" name="Salida (%)" stroke={INK} strokeWidth={2.8} dot={{ r: 4 }} connectNulls={false} isAnimationActive={false} /></ComposedChart></Chart> : <Empty>No hay distritos asociados a los eventos seleccionados.</Empty>}
        <Table caption="Sesiones y tasa de salida por distrito" headings={["Distrito", "Sesiones", "Sesiones con salida", "Tasa de salida"]} rows={data.districts.map(row => [row.name, row.sessions, row.referrals, pct(row.outboundRate)])} />
      </Card>

      <Card eyebrow="DESGLOSE DEL DISTRITO" title="Cómo cambió el distrito elegido" description="Selecciona un distrito para ver sus búsquedas diarias y la tasa de sesiones que abrieron un aviso. Este desglose conserva los filtros globales y no suma personas únicas de todo el periodo." wide>
        <div className="combo-district-buttons" role="group" aria-label="Elegir distrito para el desglose">{data.districts.map(row => <button key={row.name} aria-pressed={district === row.name} onClick={() => setChosenDistrict(row.name)}>{row.name}</button>)}</div>
        {districtDays.length ? <Chart label={`Búsquedas por día y tasa de salida en ${district}`} leftAxis="búsquedas" rightAxis="% con salida"><ComposedChart data={districtDays} margin={{ top: 12, right: 5, bottom: 4, left: 2 }}><CartesianGrid stroke={GRID} strokeDasharray="3 3" vertical={false} /><DateAxis /><CountAxis /><PercentAxis /><Tooltip formatter={tooltipValue} /><Legend verticalAlign="top" height={35} /><Bar yAxisId="count" dataKey="searches" name="Búsquedas" fill={LIME} radius={[3, 3, 0, 0]} isAnimationActive={false} /><Line yAxisId="rate" dataKey="outboundRate" name="Salida (%)" stroke={INK} strokeWidth={2.8} dot={{ r: 3 }} connectNulls={false} isAnimationActive={false} /></ComposedChart></Chart> : <Empty>Elige un distrito con actividad para ver su evolución.</Empty>}
        <p className="combo-footnote">Distrito seleccionado: <b>{district || "ninguno"}</b>.</p>
        <Table caption={`Evolución de ${district || "distrito sin datos"}`} headings={["Día", "Sesiones", "Búsquedas", "Sesiones con salida", "Tasa de salida"]} rows={districtDays.map(row => [row.date, row.sessions, row.searches, row.outbound, pct(row.outboundRate)])} />
      </Card>

      <Card eyebrow="SOPORTE · CALIDAD DE AYUDA" title="Preguntas y utilidad valorada" description="Las columnas cuentan preguntas por tema. La línea usa solo los votos recibidos sobre respuestas de ese tema. Si nadie votó, no se dibuja una utilidad ficticia." wide>
        {data.support.length ? <Chart label="Preguntas por tema en columnas y porcentaje de votos útiles en línea" leftAxis="preguntas" rightAxis="% de votos útiles" tall><ComposedChart data={data.support} margin={{ top: 12, right: 5, bottom: 55, left: 2 }}><CartesianGrid stroke={GRID} strokeDasharray="3 3" vertical={false} /><XAxis dataKey="name" tickFormatter={shortLabel} interval={0} angle={-27} textAnchor="end" tick={{ fontSize: 12, fill: "#57705d" }} /><CountAxis /><PercentAxis /><Tooltip formatter={tooltipValue} /><Legend verticalAlign="top" height={35} /><Bar yAxisId="count" dataKey="questions" name="Preguntas" fill={LIME} radius={[3, 3, 0, 0]} isAnimationActive={false} /><Line yAxisId="rate" dataKey="helpfulRate" name="Votos útiles (%)" stroke={INK} strokeWidth={2.8} dot={{ r: 3 }} connectNulls={false} isAnimationActive={false} /></ComposedChart></Chart> : <Empty>Aún no hay consultas al asistente en esta selección.</Empty>}
        <p className="combo-footnote">{fmt(totalVotes)} valoraciones en los temas mostrados. Una respuesta útil declarada no demuestra que se haya resuelto un caso.</p>
        <Table caption="Preguntas y valoraciones por tema" headings={["Tema", "Preguntas", "Valoraciones", "Votos útiles"]} rows={data.support.map(row => [row.name, row.questions, row.votes, pct(row.helpfulRate)])} />
      </Card>
    </div>
    <p className="combo-scope">Las vistas describen eventos del modo elegido. Los filtros seleccionan eventos y pueden dejar parte de un recorrido fuera; las sesiones no identifican personas. Los enlaces externos no prueban contactos, compras ni ingresos.</p>
  </section>;
}
