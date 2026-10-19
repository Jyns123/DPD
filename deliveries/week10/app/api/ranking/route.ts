import { getListings } from "../../../lib/catalog";
import { rankListings, validateProfile } from "../../../lib/recommendation";
import { jsonError, readJson } from "../_shared";

export async function POST(request: Request) {
  const payload = await readJson(request);
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    return jsonError(400, "invalid_json", "El cuerpo debe ser un objeto JSON válido.");
  }
  const input = payload as Record<string, unknown>;
  const profileInput = input.profile ?? input;
  const validation = validateProfile(profileInput);
  if (!validation.valid) return jsonError(400, "invalid_profile", validation.error);
  const weightTotal = validation.value.weights.price + validation.value.weights.safety + validation.value.weights.convenience;
  if (weightTotal <= 0) return jsonError(400, "invalid_weights", "Al menos una ponderación debe ser mayor que cero.");

  const limit = input.limit ?? 24;
  const offset = input.offset ?? 0;
  const sort = input.sort ?? "match";
  const onlyLocated = input.onlyLocated ?? false;
  if (typeof limit !== "number" || !Number.isFinite(limit) || limit < 1 ||
      typeof offset !== "number" || !Number.isFinite(offset) || offset < 0 ||
      typeof onlyLocated !== "boolean" ||
      !["match", "price_asc", "price_desc"].includes(String(sort))) {
    return jsonError(400, "invalid_options", "limit, offset o sort no son válidos.");
  }
  try {
    return Response.json(rankListings(getListings(), validation.value, {
      limit: Math.min(100, Math.floor(limit)),
      offset: Math.floor(offset),
      sort: sort as "match" | "price_asc" | "price_desc",
      onlyLocated,
    }));
  } catch {
    return jsonError(400, "invalid_weights", "Al menos una ponderación debe ser mayor que cero.");
  }
}
