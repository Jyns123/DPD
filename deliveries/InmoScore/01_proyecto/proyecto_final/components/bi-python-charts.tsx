"use client";
import Image from "next/image";
import { useEffect, useMemo, useState } from "react";
import { Bar, CartesianGrid, ComposedChart, Legend, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { RefreshCw } from "lucide-react";
import type { DailyRow } from "../lib/business-metrics";

type Heatmap = Array<Array<{ weekday: number; band: number; count: number }>>;
type RequestIdentity = { body: string; authenticated: boolean; attempt: number };
type Figures = { request: RequestIdentity; trend?: string; heatmap?: string; error?: string };
const DAYS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"];
const EMPTY_IMAGE = "data:image/svg+xml;charset=utf-8,";
function svgImage(svg: string) { return EMPTY_IMAGE + encodeURIComponent(svg); }

/** El servidor dibuja con Python; solo recibe series agregadas, nunca mensajes o perfiles. */
export default function PythonCharts({ mode, daily, heatmap, token }: {
  mode: "simulation" | "live";
  daily: DailyRow[];
  heatmap: Heatmap;
  token: string;
}) {
  const [figures, setFigures] = useState<Figures | null>(null);
  const [attempt, setAttempt] = useState(0);
  const accessToken = mode === "live" ? token : "";
  // El JSON será idéntico en una lectura 304: no volvemos a ejecutar Python.
  const requestBody = JSON.stringify({
    mode: mode === "simulation" ? "sim" : "live",
    daily: daily.map(({ date, searches, referrals }) => ({ date, searches, referrals })),
    heatmap: heatmap.map(day => day.map(cell => cell.count)),
  });
  const request = useMemo(() => ({ body: requestBody, authenticated: Boolean(accessToken), attempt }), [requestBody, accessToken, attempt]);
  const current = figures?.request === request ? figures : null;
  const pending = !current;
  const peak = Math.max(1, ...heatmap.flat().map(cell => cell.count));

  useEffect(() => {
    let active = true;
    const controller = new AbortController();
    let timeout: ReturnType<typeof setTimeout> | undefined;
    const debounce = window.setTimeout(async () => {
      timeout = setTimeout(() => controller.abort(), 15000);
      try {
        const headers: Record<string, string> = { "Content-Type": "application/json" };
        if (accessToken) headers["X-Analytics-Token"] = accessToken;
        const response = await fetch("/api/bi-chart", { method: "POST", cache: "no-store", headers, body: request.body, signal: controller.signal });
        const result = await response.json();
        if (!response.ok) throw new Error(result.message || "No se pudo generar la figura de Python.");
        if (typeof result.trend !== "string" || typeof result.heatmap !== "string" || !result.trend.includes("<svg") || !result.heatmap.includes("<svg")) throw new Error("La figura recibida no tiene un formato válido.");
        if (active) setFigures({ request, trend: svgImage(result.trend), heatmap: svgImage(result.heatmap) });
      } catch {
        if (active) setFigures({ request, error: "La vista de Python no está disponible. Mostramos los mismos datos con los gráficos interactivos de la web." });
      } finally { clearTimeout(timeout); }
    }, 300);
    return () => { active = false; clearTimeout(debounce); clearTimeout(timeout); controller.abort(); };
  }, [request, accessToken]);

  return <>
    <div className="bi-chart-status" role="status">
      <span className={`bi-render-status ${pending ? "is-updating" : current?.error ? "is-fallback" : ""}`} />
      <span>{pending ? "Actualizando las figuras con la selección actual…" : current?.error ? current.error : "Figuras actualizadas con los datos seleccionados · Python"}</span>
      {current?.error && <button onClick={() => setAttempt(value => value + 1)}><RefreshCw size={12} /> Reintentar</button>}
    </div>
    <section className="bi-python-grid" aria-label="Visualizaciones principales">
      <article className="board-chart-card bi-trend-panel">
        <div className="board-card-title"><div><h3>Búsquedas y salidas al anuncio</h3></div><span>Por día · Lima</span></div>
        <p>Cómo cambia la actividad y cuántas sesiones llegan al portal original. Una salida no confirma una compra.</p>
        <div className={`bi-python-figure ${pending ? "is-pending" : ""}`} aria-busy={pending}>
          {current?.trend ? <Image src={current.trend} alt="Gráfico combinado de búsquedas y sesiones con salida al anuncio por fecha. Los valores exactos están disponibles en la tabla inferior." width={960} height={390} unoptimized /> : <div className="bi-native-trend"><ResponsiveContainer width="100%" height="100%" minWidth={0} initialDimension={{ width: 720, height: 280 }} debounce={80}><ComposedChart data={daily} margin={{ left: -15, right: 12, top: 12 }}><CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e7ede9" /><XAxis dataKey="date" tickFormatter={value => String(value).slice(5)} tick={{ fontSize: 11 }} minTickGap={25} /><YAxis allowDecimals={false} tick={{ fontSize: 11 }} /><Tooltip /><Legend /><Bar dataKey="searches" name="Búsquedas" fill="#b1c9be" radius={[4, 4, 0, 0]} isAnimationActive={false} /><Line type="monotone" dataKey="referrals" name="Sesiones con salida" stroke="#173d31" strokeWidth={2.5} dot={false} isAnimationActive={false} /></ComposedChart></ResponsiveContainer></div>}
        </div>
        <details className="board-data-table"><summary>Consultar datos y alcance</summary><p>El gráfico de Python completa con cero los días intermedios sin eventos seleccionados. La tabla solo incluye fechas observadas. La relación entre las series es descriptiva: no demuestra causalidad ni predice ventas.</p><div className="board-table-scroll"><table><caption>Actividad diaria en hora de Lima</caption><thead><tr><th scope="col">Fecha</th><th scope="col">Búsquedas</th><th scope="col">Sesiones con salida</th></tr></thead><tbody>{daily.length ? daily.map(row => <tr key={row.date}><td>{row.date}</td><td>{row.searches}</td><td>{row.referrals}</td></tr>) : <tr><td colSpan={3}>No hay actividad en esta selección.</td></tr>}</tbody></table></div></details>
      </article>
      <article className="board-chart-card bi-heat-panel">
        <div className="board-card-title"><div><h3>¿Cuándo interactúan?</h3></div><span>Hora de Lima</span></div>
        <p>Eventos por día de la semana y franja horaria. Un tono más intenso indica más actividad.</p>
        <div className={`bi-python-figure bi-python-heat ${pending ? "is-pending" : ""}`} aria-busy={pending}>
          {current?.heatmap ? <Image src={current.heatmap} alt="Mapa de calor de eventos por día de la semana y franja horaria. La tabla inferior contiene los valores exactos." width={560} height={390} unoptimized /> : <div className="bi-heat-skeleton" aria-hidden="true">{heatmap.map((day, dayIndex) => <div key={dayIndex}>{day.map(cell => <i key={cell.band} style={{ opacity: .12 + .88 * cell.count / peak }} />)}</div>)}</div>}
        </div>
        <details className="board-data-table" open={Boolean(current?.error)}><summary>Consultar valores por horario</summary><div className="board-heatmap"><table><caption className="board-sr-only">Eventos por día y franja horaria</caption><thead><tr><th scope="col">Hora</th>{DAYS.map(day => <th scope="col" key={day}>{day}</th>)}</tr></thead><tbody>{Array.from({ length: 6 }, (_, band) => <tr key={band}><th scope="row">{String(band * 4).padStart(2, "0")}–{String(band * 4 + 3).padStart(2, "0")}h</th>{heatmap.map((day, dayIndex) => <td key={dayIndex} style={{ background: day[band].count ? `rgba(23,61,49,${.12 + .88 * day[band].count / peak})` : "#f0f2ec", color: day[band].count / peak > .5 ? "#fff" : "#213b31" }}>{day[band].count}</td>)}</tr>)}</tbody></table></div></details>
      </article>
    </section>
  </>;
}
