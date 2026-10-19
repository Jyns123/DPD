import { getRepository } from '../../../db';
import { isKnownListing } from '../../../lib/catalog';
import { authenticatedUser, databaseError, jsonError, mutationOriginIsSame, readJson } from '../_shared';
export async function POST(request: Request) {
  if (!mutationOriginIsSame(request)) return jsonError(403, 'forbidden_origin', 'La solicitud debe venir del mismo sitio.');
  try {
    const user = await authenticatedUser();
    if (!user) return jsonError(401, 'unauthorized', 'Inicia sesión para guardar favoritos.');
    const payload = await readJson(request);
    const id = payload && typeof payload === 'object' && !Array.isArray(payload) ? (payload as Record<string, unknown>).id : null;
    if (!isKnownListing(id)) return jsonError(400, 'invalid_listing', 'id debe identificar una publicación del catálogo.');
    return Response.json({ favorites: await getRepository().toggleFavorite(user.id, id) }, { headers: { 'Cache-Control': 'no-store' } });
  } catch { return databaseError(); }
}
