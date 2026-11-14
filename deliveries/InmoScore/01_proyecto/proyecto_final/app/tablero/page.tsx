import type { Metadata } from "next";
import BusinessDashboard from "../../components/business-dashboard";
import { getListings, getDistricts } from "../../lib/catalog";
import type { CatalogQuality } from "../../lib/business-metrics";
import "./dashboard.css";
export const dynamic = "force-dynamic";
export const metadata: Metadata = {
  title: "Tablero de control | InmoScore",
  robots: { index: false, follow: false },
};
export default function DashboardPage() {
  const listings = getListings();
  const dates = listings.map(item => item.observedAt).filter((value): value is string => Boolean(value)).sort();
  const catalog: CatalogQuality = {
    total: listings.length,
    withModel: listings.filter(item => typeof item.predictedPrice === "number" && item.predictedPrice > 0).length,
    preciseLocation: listings.filter(item => item.location && ["calle", "exacta"].includes(item.location.precision)).length,
    withWarnings: listings.filter(item => item.flags.length > 0).length,
    districts: getDistricts().length,
    capturedAt: dates.at(-1),
  };
  return <BusinessDashboard initialCatalog={catalog} />;
}

