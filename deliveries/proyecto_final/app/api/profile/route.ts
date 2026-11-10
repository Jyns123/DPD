import { getRepository } from '../../../db';
import { publicUser } from '../../../lib/auth/session';
import { authenticatedUser, databaseError, jsonError, mutationOriginIsSame, readJson } from '../_shared';
import { validateProfile } from '../../../lib/recommendation';
export async function PUT(request: Request) {
  if (!mutationOriginIsSame(request)) return jsonError(403, 'forbidden_origin', 'La solicitud debe venir del mismo sitio.');
  try {
    const user = await authenticatedUser();
    if (!user) return jsonError(401, 'unauthorized', 'Inicia sesión para guardar tu perfil.');
    const result = validateProfile(await readJson(request));
    if (!result.valid) return jsonError(400, 'invalid_profile', result.error);
    const profile = result.value;
    if (!profile.name) return jsonError(400, 'invalid_profile', 'El nombre es obligatorio.');
    await getRepository().saveProfile(user.id, profile.name, JSON.stringify(profile));
    return Response.json({ user: { ...publicUser(user), name: profile.name }, profile }, { headers: { 'Cache-Control': 'no-store' } });
  } catch { return databaseError(); }
}
