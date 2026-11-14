import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { generateSimulation, SIMULATION_END, SIMULATION_SEED } from "../lib/business-simulation.ts";
import { DEFAULT_ASSUMPTIONS, metricsCsv, summarize, type CatalogQuality } from "../lib/business-metrics.ts";
import type { CatalogListing } from "../lib/recommendation.ts";

const directory = join(process.cwd(), "data", "simulation");
mkdirSync(directory, { recursive: true });
const catalogFile = JSON.parse(readFileSync(join(process.cwd(), "data", "catalog.json"), "utf8")) as { listings: CatalogListing[]; districts: string[] };
const listings = catalogFile.listings;
const catalog: CatalogQuality = {
  total: listings.length,
  withModel: listings.filter(item => item.predictedPrice && !item.flags.some(flag => flag === "model_outside_area_range" || flag === "capture_district_conflict")).length,
  preciseLocation: listings.filter(item => item.location && ["calle", "exacta"].includes(item.location.precision)).length,
  withWarnings: listings.filter(item => item.flags.length > 0).length,
  districts: catalogFile.districts.length,
};
const events = generateSimulation();
const metadata = { source: "simulacion", seed: SIMULATION_SEED, fictionalVisitors: 300, sessionsPerVisitor: 1, startDateLima: "2026-10-13", endDateLima: "2026-11-11", timezone: "America/Lima", eventCount: events.length, note: "Datos ficticios para aprender a usar el tablero. No representan personas, compras, pagos ni ingresos reales. El catálogo de viviendas se conserva separado y procede del proyecto recibido." };
writeFileSync(join(directory, "eventos_300.json"), JSON.stringify({ metadata, events }, null, 2) + "\n");
const columns = ["source", "id", "visitorId", "type", "timestamp", "district", "channel", "resultCount", "durationMs", "success", "topic", "helpful"] as const;
const escape = (value: unknown) => `"${String(value ?? "").replaceAll('"', '""')}"`;
const rows = events.map(event => columns.map(column => escape(column === "source" ? "simulacion" : event[column])).join(","));
writeFileSync(join(directory, "eventos_300.csv"), "\uFEFF" + columns.map(escape).join(",") + "\r\n" + rows.join("\r\n") + "\r\n");
const summary = summarize(events, catalog, true, DEFAULT_ASSUMPTIONS, SIMULATION_END);
writeFileSync(join(directory, "indicadores_escenario.csv"), metricsCsv(summary.metrics));
writeFileSync(join(directory, "diccionario_indicadores.json"), JSON.stringify({ metadata, assumptions: DEFAULT_ASSUMPTIONS, catalogScope: "Catálogo global real del proyecto, independiente de la simulación y sus filtros", catalog, indicators: summary.metrics }, null, 2) + "\n");
writeFileSync(join(directory, "LEEME.md"), `# Datos para practicar con el tablero\n\nEstos archivos contienen **300 visitantes ficticios**, con una sesión por visitante y **${events.length} eventos**. No son usuarios registrados ni ventas reales. No deben mezclarse con la base de actividad de la web.\n\n- eventos_300.json: eventos y procedencia.\n- eventos_300.csv: los mismos eventos, para Excel o Power BI.\n- indicadores_escenario.csv: los 30 indicadores del escenario inicial.\n- diccionario_indicadores.json: fórmulas, unidades, límites y supuestos económicos.\n\nEl tablero se abre en /tablero al iniciar InmoScore. La pestaña Simulación calcula el escenario en el navegador; Actividad registrada consulta el servidor cada 5 segundos. Las cifras financieras solo se calculan en Simulación. No se ejecutan pagos ni se confirman compras.\n\n## Repetir el ejercicio\n\nEjecutar desde proyecto_final: node --experimental-strip-types scripts/export-business-simulation.ts. La semilla fija ${SIMULATION_SEED} reproduce los mismos eventos. Cambiar los filtros no modifica los archivos originales.\n\nLas fechas están guardadas en UTC y agrupadas en hora de Lima. Los porcentajes de calidad describen el catálogo completo; no son simulados ni se recalculan por distrito de actividad. Los costos financieros se asignan al segmento que se está observando; no se prorratean automáticamente.\n\n## Qué puede completar el equipo\n\nElegir un distrito, anotar tres indicadores antes y después de aplicar el filtro y explicar sus denominadores. Después, cambiar un único supuesto de negocio y describir cómo cambia el saldo. No necesitan agregar código para demostrar este aprendizaje.\n`);
console.log(JSON.stringify({ directory, visitors: 300, events: events.length, indicators: summary.metrics.length, files: ["eventos_300.json", "eventos_300.csv", "indicadores_escenario.csv", "diccionario_indicadores.json", "LEEME.md"] }, null, 2));
