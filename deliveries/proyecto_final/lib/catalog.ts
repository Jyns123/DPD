import catalogData from "../data/catalog.json";
import { toPublicListing, type CatalogListing } from "./recommendation";

type Catalog = {
  metadata: Record<string, unknown>;
  listings: CatalogListing[];
  districts: string[];
};

const catalog = catalogData as Catalog;
const publicListings = catalog.listings.map(toPublicListing);
const listingsById = new Map(publicListings.map((listing) => [listing.id, listing]));

export function getListings(): CatalogListing[] {
  return publicListings;
}

export function getListing(id: string): CatalogListing | undefined {
  return listingsById.get(id);
}

export function getDistricts(): string[] {
  return catalog.districts;
}

export function isKnownListing(id: unknown): id is string {
  return typeof id === "string" && listingsById.has(id);
}
