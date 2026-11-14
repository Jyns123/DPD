export const RANKING_ASSUMPTIONS = {
  tea: 0.09,
  years: 20,
  maxIncomeShare: 0.3,
  minDown: 0.1,
} as const;

export type PreferenceWeights = {
  price: number;
  safety: number;
  convenience: number;
};

export type BuyerProfile = {
  name?: string;
  income: number;
  savings: number;
  budget: number;
  minRooms: number;
  minArea: number;
  districts: string[];
  weights: PreferenceWeights;
};

export type CatalogListing = {
  id: string;
  district: string;
  address: string;
  price: number;
  area: number;
  rooms: number;
  bathrooms: number;
  parking: number | null;
  maintenance: number | null;
  predictedPrice: number | null;
  scores: { price: number | null; safety: number | null; convenience: number | null };
  location: { lat: number; lng: number; precision: string } | null;
  dataPartial: boolean;
  flags: string[];
  url: string | null;
  availability: "unverified";
  duplicateGroupId: string | null;
  // Present only for listings seen by the own Urbania capture (urbania/).
  source?: "urbania_fase1";
  observedAt?: string;
};

export type RankedListing = CatalogListing & {
  score: number;
  reasons: string[];
  opportunity: number | null;
};

export function needsInputReview(listing: CatalogListing): boolean {
  return listing.flags.some(flag =>
    flag === "model_outside_area_range" || flag === "capture_district_conflict");
}

// El archivo analítico conserva la predicción para auditoría. La API no la
// ofrece como referencia utilizable si la entrada necesita revisión.
export function toPublicListing(listing: CatalogListing): CatalogListing {
  if (listing.flags.includes("capture_district_conflict")) {
    return { ...listing, predictedPrice: null, scores: { price: null, safety: null, convenience: null } };
  }
  return needsInputReview(listing)
    ? { ...listing, predictedPrice: null, scores: { ...listing.scores, price: null } }
    : listing;
}

export type RankingOptions = {
  limit?: number;
  offset?: number;
  sort?: "match" | "price_asc" | "price_desc";
  onlyLocated?: boolean;
};

export type ValidationResult =
  | { valid: true; value: BuyerProfile }
  | { valid: false; error: string };

const MAX_MONEY = 1_000_000_000;

function finiteNumber(value: unknown, min: number, max: number): value is number {
  return typeof value === "number" && Number.isFinite(value) && value >= min && value <= max;
}

export function validateProfile(value: unknown): ValidationResult {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return { valid: false, error: "El perfil debe ser un objeto válido" };
  }
  const input = value as Record<string, unknown>;
  const fieldLabels: Record<string, string> = {income:"ingreso",savings:"ahorro",budget:"presupuesto",minRooms:"dormitorios",minArea:"área mínima"};
  const numericFields: Array<[keyof BuyerProfile, number, number]> = [
    ["income", 0, MAX_MONEY],
    ["savings", 0, MAX_MONEY],
    ["budget", 0, MAX_MONEY],
    ["minRooms", 0, 20],
    ["minArea", 0, 100_000],
  ];
  for (const [field, min, max] of numericFields) {
    if (!finiteNumber(input[field], min, max)) {
      return { valid: false, error: `Revisa el valor de ${fieldLabels[field] ?? field}: debe estar entre ${min} y ${max}` };
    }
  }
  if (!Number.isInteger(input.minRooms)) {
    return { valid: false, error: "El número de dormitorios debe ser entero" };
  }
  if (!Array.isArray(input.districts) || input.districts.length > 100 ||
      input.districts.some((district) => typeof district !== "string" || district.trim().length === 0 || district.length > 100)) {
    return { valid: false, error: "Revisa los distritos seleccionados" };
  }
  const weights = input.weights;
  if (!weights || typeof weights !== "object" || Array.isArray(weights)) {
    return { valid: false, error: "Define tus prioridades de precio, seguridad y servicios" };
  }
  const parsedWeights = weights as Record<string, unknown>;
  for (const key of ["price", "safety", "convenience"] as const) {
    if (!finiteNumber(parsedWeights[key], 0, 1)) {
      return { valid: false, error: "Cada prioridad debe estar entre 0 y 100 en el control" };
    }
  }
  if ((parsedWeights.price as number) + (parsedWeights.safety as number) + (parsedWeights.convenience as number) <= 0) {
    return { valid: false, error: "Asigna una prioridad mayor que cero a al menos un criterio." };
  }
  if (typeof input.name !== "undefined" && (typeof input.name !== "string" || input.name.length > 120)) {
    return { valid: false, error: "El nombre debe tener como máximo 120 caracteres" };
  }

  return {
    valid: true,
    value: {
      ...(typeof input.name === "string" ? { name: input.name.trim() } : {}),
      income: input.income as number,
      savings: input.savings as number,
      budget: input.budget as number,
      minRooms: input.minRooms as number,
      minArea: input.minArea as number,
      districts: [...new Set((input.districts as string[]).map((district) => district.trim()))],
      weights: {
        price: parsedWeights.price as number,
        safety: parsedWeights.safety as number,
        convenience: parsedWeights.convenience as number,
      },
    },
  };
}

export function affordableCap(profile: Pick<BuyerProfile, "income" | "savings">): number {
  const monthlyRate = (1 + RANKING_ASSUMPTIONS.tea) ** (1 / 12) - 1;
  const payments = RANKING_ASSUMPTIONS.years * 12;
  const factor = (1 - (1 + monthlyRate) ** -payments) / monthlyRate;
  const loanCapacity = (profile.income * RANKING_ASSUMPTIONS.maxIncomeShare) * factor;
  const byLoan = loanCapacity + profile.savings;
  const bySavings = profile.savings / RANKING_ASSUMPTIONS.minDown;
  return Math.max(0, Math.floor(Math.min(byLoan, bySavings)));
}

function listingOpportunity(listing: CatalogListing): number | null {
  if (!finiteNumber(listing.predictedPrice, 0, MAX_MONEY) || listing.price <= 0) return null;
  if (listing.predictedPrice <= 0) return null;
  return Math.round(((listing.predictedPrice - listing.price) / listing.predictedPrice) * 1000) / 10;
}

function normalizedScore(value: number | null): number | null {
  if (value === null || !Number.isFinite(value)) return null;
  const percentage = Math.abs(value) <= 1 ? value * 100 : value;
  return Math.min(100, Math.max(0, percentage));
}

function scoreListing(listing: CatalogListing, weights: PreferenceWeights): number {
  const total = weights.price + weights.safety + weights.convenience;
  const score = (value: number | null) => normalizedScore(value) ?? 0;
  return Math.round((
    score(listing.scores.price) * weights.price +
    score(listing.scores.safety) * weights.safety +
    score(listing.scores.convenience) * weights.convenience
  ) / total);
}

function reasonsFor(listing: CatalogListing, profile: BuyerProfile, opportunity: number | null): string[] {
  const reasons: string[] = [];
  const criteria = ([
    { key: "price", label: "Precio frente al modelo" },
    { key: "safety", label: "Seguridad distrital" },
    { key: "convenience", label: "Servicios del distrito" },
  ] as const).filter(({ key }) => profile.weights[key] > 0)
    .sort((a, b) => profile.weights[b.key] - profile.weights[a.key]);
  for (const { key, label } of criteria.slice(0, 2)) {
    const index = normalizedScore(listing.scores[key]);
    if (index !== null) reasons.push(`${label}: índice ${Math.round(index)}/100 según tu prioridad`);
  }
  if (opportunity !== null && opportunity > 0) {
    reasons.push(`Precio publicado ${opportunity}% menor que la referencia del modelo`);
  }
  reasons.push("Cumple tu tope, área y dormitorios indicados");
  if (listing.flags.length > 0) reasons.push("Revisa las alertas de esta publicación");
  if (listing.dataPartial) reasons.push("Publicación con datos incompletos");
  return reasons;
}

export function rankListings(
  listings: CatalogListing[],
  profile: BuyerProfile,
  options: RankingOptions = {},
) {
  const weightTotal = profile.weights.price + profile.weights.safety + profile.weights.convenience;
  if (!Number.isFinite(weightTotal) || weightTotal <= 0) {
    throw new Error("At least one preference weight must be greater than zero");
  }
  const limit = Math.min(100, Math.max(1, Math.floor(options.limit ?? 24)));
  const offset = Math.max(0, Math.floor(options.offset ?? 0));
  const sort = options.sort ?? "match";
  const cap = affordableCap(profile);
  const effectiveBudget = Math.min(profile.budget, cap);

  let ranked = listings
    .filter((listing) => !listing.flags.includes("retired_at_last_check"))
    // Conservamos los avisos para revisarlos, sin recomendar referencias con
    // un área fuera del rango observado o con un distrito contradictorio.
    .filter((listing) => !needsInputReview(listing))
    .filter((listing) => listing.price <= effectiveBudget)
    .filter((listing) => listing.rooms >= profile.minRooms && listing.area >= profile.minArea)
    .filter((listing) => profile.districts.length === 0 || profile.districts.includes(listing.district))
    .filter((listing) => !options.onlyLocated || listing.location !== null)
    .map((listing) => ({ listing, score: sort === "match" ? scoreListing(listing, profile.weights) : 0 }));

  if (sort === "price_asc") ranked.sort((a, b) => a.listing.price - b.listing.price || a.listing.id.localeCompare(b.listing.id));
  else if (sort === "price_desc") ranked.sort((a, b) => b.listing.price - a.listing.price || a.listing.id.localeCompare(b.listing.id));
  else ranked.sort((a, b) => b.score - a.score || a.listing.price - b.listing.price || a.listing.id.localeCompare(b.listing.id));

  // Los grupos de captura pueden contener unidades distintas. Quitamos solo
  // avisos con el mismo grupo y los mismos atributos principales.
  const seen = new Set<string>();
  ranked = ranked.filter(({ listing }) => {
    if (!listing.duplicateGroupId) return true;
    const key = [listing.duplicateGroupId, listing.district, listing.price,
      listing.area, listing.rooms].join("|");
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });

  const matchedTotal = ranked.length;
  const hasDistrictAlternatives = new Set(ranked.map(({ listing }) => listing.district)).size > 1;
  if (sort === "match" && hasDistrictAlternatives) {
    const counts = new Map<string, number>();
    ranked = ranked.filter(({ listing }) => {
      const count = counts.get(listing.district) ?? 0;
      if (count >= 3) return false;
      counts.set(listing.district, count + 1);
      return true;
    });
  }

  const total = ranked.length;
  // Las explicaciones solo se materializan para la página que el usuario verá.
  const page = ranked.slice(offset, offset + limit).map(({ listing, score }) => {
    const opportunity = listingOpportunity(listing);
    return { ...listing, score: sort === "match" ? score : scoreListing(listing, profile.weights),
      reasons: reasonsFor(listing, profile, opportunity), opportunity };
  });
  const warnings = new Set<string>();
  for (const listing of page) {
    if (listing.dataPartial) warnings.add("Algunas publicaciones tienen datos incompletos.");
    if (listing.flags.length) warnings.add("Revisa las alertas de cada publicación antes de contactarla.");
    warnings.add("La disponibilidad de las publicaciones no está verificada.");
  }

  return {
    listings: page,
    total,
    matchedTotal,
    diversityLimited: matchedTotal > total,
    effectiveBudget,
    cap,
    assumptions: RANKING_ASSUMPTIONS,
    warnings: [...warnings],
  };
}
