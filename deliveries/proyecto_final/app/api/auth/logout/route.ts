import { endSession } from '../../../../lib/auth/session';
import { mutationOriginIsSame, jsonError, databaseError } from '../../_shared';
export async function POST(request: Request) {
  if (!mutationOriginIsSame(request)) return jsonError(403, 'forbidden_origin', 'La solicitud debe venir del mismo sitio.');
  try { await endSession(); return Response.json({ loggedOut: true }, { headers: { 'Cache-Control': 'no-store' } }); } catch { return databaseError(); }
}
