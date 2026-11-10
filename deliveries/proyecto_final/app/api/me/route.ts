import { getRepository } from '../../../db';
import { publicUser } from '../../../lib/auth/session';
import { authenticatedUser, databaseError, jsonError, parseStoredProfile } from '../_shared';
export async function GET() {
  try {
    const user = await authenticatedUser();
    if (!user) return jsonError(401, 'unauthorized', 'Inicia sesión para consultar tu perfil.');
    return Response.json({ user: publicUser(user), profile: parseStoredProfile(user.profileJson), favorites: await getRepository().listFavorites(user.id) }, { headers: { 'Cache-Control': 'no-store' } });
  } catch { return databaseError(); }
}
