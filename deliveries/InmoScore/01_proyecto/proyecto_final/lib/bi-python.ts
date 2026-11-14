import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { jsonError } from "../app/api/_shared";

const cache = new Map<string, string>();
const pending = new Map<string, Promise<string>>();

function renderCharts(input: string): Promise<string> {
  const projectPython = resolve(process.platform === "win32" ? ".venv/Scripts/python.exe" : ".venv/bin/python");
  const executable = process.env.PYTHON_EXECUTABLE ||
    (existsSync(projectPython) ? projectPython : process.platform === "win32" ? "python" : "python3");
  return new Promise((success, failure) => {
    const child = spawn(executable, ["-I", "-X", "utf8", resolve("analytics/render_bi.py")], {
      stdio: ["pipe", "pipe", "ignore"],
      windowsHide: true,
    });
    const chunks: Buffer[] = [];
    let bytes = 0;
    const deadline = setTimeout(() => {
      child.kill();
      failure(new Error("Se agotó el tiempo de generación."));
    }, 5_000);
    child.on("error", error => { clearTimeout(deadline); failure(error); });
    child.stdin.on("error", () => { /* El cierre del proceso informa el fallo. */ });
    child.stdout.on("data", (chunk: Buffer) => {
      bytes += chunk.length;
      if (bytes > 700_000) {
        child.kill();
        failure(new Error("La figura excede el tamaño esperado."));
        return;
      }
      chunks.push(chunk);
    });
    child.on("close", code => {
      clearTimeout(deadline);
      try {
        if (code !== 0 || bytes > 700_000) throw new Error("No se pudo generar la figura.");
        const result = Buffer.concat(chunks).toString("utf8");
        JSON.parse(result);
        success(result);
      } catch (error) { failure(error); }
    });
    child.stdin.end(input);
  });
}

export async function renderBiResponse(input: object) {
  const payload = JSON.stringify(input);
  const key = createHash("sha256").update(payload).digest("hex");
  const headers = { "Cache-Control": "no-store", "Content-Type": "application/json" };
  const cached = cache.get(key);
  if (cached) return new Response(cached, { headers });

  let rendering = pending.get(key);
  if (!rendering) {
    if (pending.size >= 2) {
      return jsonError(503, "chart_busy", "Hay gráficos en preparación. Reintenta en unos segundos.");
    }
    rendering = renderCharts(payload).then(charts => {
      if (cache.size >= 32) {
        const oldest = cache.keys().next().value;
        if (oldest) cache.delete(oldest);
      }
      cache.set(key, charts);
      return charts;
    }).finally(() => pending.delete(key));
    pending.set(key, rendering);
  }
  try {
    return new Response(await rendering, { headers });
  } catch {
    return jsonError(503, "python_chart_unavailable", "El gráfico de Python no está disponible. Puedes consultar los gráficos interactivos.");
  }
}
