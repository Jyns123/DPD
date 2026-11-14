export const JSON_BODY_LIMIT = 16 * 1024;
export const JSON_BODY_TIMEOUT_MS = 8000;

/** Lee una entrada pequeña sin acumular un cuerpo ilimitado en memoria. */
export async function readLimitedJson(request: Request, maximumBytes = JSON_BODY_LIMIT, timeoutMs = JSON_BODY_TIMEOUT_MS): Promise<unknown | null> {
  const declared = request.headers.get('content-length');
  if (declared !== null && (!/^\d+$/.test(declared) || Number(declared) > maximumBytes)) return null;
  if (!request.body) return null;
  let reader: ReadableStreamDefaultReader<Uint8Array> | undefined;
  let timer: ReturnType<typeof setTimeout> | undefined;
  try {
    reader = request.body.getReader();
    const deadline = new Promise<never>((_, reject) => {
      timer = setTimeout(() => reject(new Error('body_timeout')), timeoutMs);
    });
    const chunks: Uint8Array[] = [];
    let size = 0;
    while (true) {
      const part = await Promise.race([reader.read(), deadline]);
      if (part.done) break;
      size += part.value.byteLength;
      if (size > maximumBytes) { void reader.cancel().catch(() => {}); return null; }
      chunks.push(part.value);
    }
    const bytes = new Uint8Array(size);
    let offset = 0;
    for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
    return JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(bytes));
  } catch {
    if (reader) void reader.cancel().catch(() => {});
    return null;
  } finally {
    if (timer) clearTimeout(timer);
    reader?.releaseLock();
  }
}
