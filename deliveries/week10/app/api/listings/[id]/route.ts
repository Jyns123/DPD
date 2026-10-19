import { getListing } from "../../../../lib/catalog";
import { jsonError } from "../../_shared";

export async function GET(_request: Request, context: { params: Promise<{ id: string }> }) {
  const { id } = await context.params;
  const listing = getListing(id);
  if (!listing) return jsonError(404, "listing_not_found", "No se encontró esa publicación.");
  return Response.json({ listing });
}
