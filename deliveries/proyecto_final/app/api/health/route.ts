import { getRepository } from '../../../db';
export const dynamic = 'force-dynamic';
export async function GET() {
  try { await getRepository().health(); return Response.json({ status: 'ok', database: 'sqlite' }); }
  catch { return Response.json({ status: 'error', database: 'unavailable' }, { status: 503 }); }
}
