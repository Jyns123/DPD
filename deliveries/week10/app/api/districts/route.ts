import { getDistricts } from "../../../lib/catalog";

export async function GET() {
  return Response.json({ districts: getDistricts() });
}
