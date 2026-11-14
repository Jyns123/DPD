import { readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import catalogData from "../data/catalog.json";
import { toPublicListing, type CatalogListing } from "./recommendation";

type Catalog = { metadata: Record<string, unknown>; listings: CatalogListing[]; districts: string[] };
type Loaded = { key: string; districts: string[]; listings: CatalogListing[]; byId: Map<string, CatalogListing> };

function load(data: Catalog, key: string): Loaded {
  const listings = data.listings.map(toPublicListing);
  return { key, districts: data.districts, listings, byId: new Map(listings.map(item => [item.id, item])) };
}
const bundled = load(catalogData as Catalog, "bundled");
let current = bundled;

// La actualización publica este archivo por reemplazo atómico solo tras validarlo.
function catalog(): Loaded {
  const path = join(process.cwd(), "data/catalog-published.json");
  let stat;
  try { stat = statSync(path); }
  catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return (current = bundled);
    throw error;
  }
  const key = `${stat.ino}:${stat.mtimeMs}:${stat.size}`;
  if (current.key !== key) current = load(JSON.parse(readFileSync(path, "utf8")) as Catalog, key);
  return current;
}

export function getListings(): CatalogListing[] { return catalog().listings; }
export function getListing(id: string): CatalogListing | undefined { return catalog().byId.get(id); }
export function getDistricts(): string[] { return catalog().districts; }
export function isKnownListing(id: unknown): id is string { return typeof id === "string" && catalog().byId.has(id); }
