import type { HelpAnswer, HelpContext } from "./help.ts";
import type { BuyerProfile, RankedListing } from "./recommendation.ts";

export type HelpSearch = {
  district?: string;
  budget?: number;
  minRooms?: number;
  minArea?: number;
};

type RankingReply = {
  listings: RankedListing[];
  matchedTotal: number;
  effectiveBudget: number;
  cap: number;
};

const soles = (value: number) => `S/ ${new Intl.NumberFormat("es-PE", { maximumFractionDigits: 0 }).format(value)}`;
const plain = (value: string) => value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();

function amountIn(question: string): number | undefined {
  const amount = "(\\d{1,3}(?:[.,]\\d{3})+|\\d{4,9}|\\d{1,3})";
  const expressions = [
    new RegExp(`s\\/\\s*${amount}\\s*(mil|k)?`, "i"),
    new RegExp(`\\b(?:presupuesto(?: de| hasta)?|hasta|por)\\s+${amount}\\s*(mil|k|soles)?`, "i"),
    new RegExp(`\\b${amount}\\s*(mil|k|soles)\\b`, "i"),
  ];
  for (const expression of expressions) {
    const match = question.match(expression);
    if (!match) continue;
    const base = Number(match[1].replace(/[.,]/g, ""));
    const value = /^(mil|k)$/i.test(match[2] ?? "") ? base * 1000 : base;
    if (Number.isFinite(value) && value >= 10_000 && value <= 1_000_000_000) return value;
  }
  return undefined;
}

// Reconoce preferencias explícitas. Los nombres de distrito vienen del catálogo.
export function parseHelpSearch(question: string, districts: string[] = []): HelpSearch | null {
  const text = plain(question.trim().slice(0, 400));
  const searchIntent = /\b(busco|buscando|recomiend\w*|recomend\w*|sugier\w*|muestr\w*|encuentr\w*|quiero ver|quiero encontrar|opciones para mi)\b/.test(text);
  if (!searchIntent) return null;

  const district = [...districts]
    .sort((a, b) => b.length - a.length)
    .find(item => {
      const name = plain(item).replace(/[-\s]+/g, "\\s+");
      return new RegExp(`(?:^|[^a-z])${name}(?:$|[^a-z])`).test(text);
    });
  const rooms = text.match(/\b(\d{1,2}|un|una|uno|dos|tres|cuatro|cinco)\s*(?:o\s+mas|\+)?\s*(?:dormitorios?|habitaciones?|cuartos?)\b/);
  const roomWords: Record<string, number> = { un: 1, una: 1, uno: 1, dos: 2, tres: 3, cuatro: 4, cinco: 5 };
  const minRooms = rooms ? (roomWords[rooms[1]] ?? Number(rooms[1])) : undefined;
  const area = text.match(/\b(\d{2,4})\s*(?:m2|m²|metros cuadrados)\b/);
  return {
    ...(district ? { district } : {}),
    ...(amountIn(text) !== undefined ? { budget: amountIn(text) } : {}),
    ...(minRooms !== undefined && minRooms <= 20 ? { minRooms } : {}),
    ...(area ? { minArea: Number(area[1]) } : {}),
  };
}

function queryProfile(profile: BuyerProfile, search: HelpSearch): BuyerProfile {
  return {
    ...profile,
    ...(search.budget !== undefined ? { budget: search.budget } : {}),
    ...(search.minRooms !== undefined ? { minRooms: search.minRooms } : {}),
    ...(search.minArea !== undefined ? { minArea: search.minArea } : {}),
    ...(search.district ? { districts: [search.district] } : {}),
  };
}

export async function answerHelpSearch(search: HelpSearch, context: HelpContext, signal?: AbortSignal): Promise<HelpAnswer> {
  if (!context.profile) return {
    topic: "ranking", title: "Primero definamos tu búsqueda",
    paragraphs: ["Necesito los filtros de tu perfil para mostrar viviendas concretas del catálogo."],
    action: { label: "Revisar mi perfil", href: "/perfil" },
  };

  const profile = queryProfile(context.profile, search);
  const response = await fetch("/api/ranking", {
    method: "POST",
    cache: "no-store",
    signal,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ profile, sort: "match", limit: 3, offset: 0 }),
  });
  if (!response.ok) throw new Error("ranking_unavailable");
  const ranking = await response.json() as RankingReply;
  if (!Array.isArray(ranking.listings) || !Number.isFinite(ranking.matchedTotal) || !Number.isFinite(ranking.effectiveBudget)) {
    throw new Error("invalid_ranking");
  }

  const places = profile.districts.length ? profile.districts.join(", ") : "todos los distritos disponibles";
  const criteria = `Busqué en ${places}, con al menos ${profile.minRooms} dormitorio${profile.minRooms === 1 ? "" : "s"}, ${profile.minArea} m² y un presupuesto deseado de ${soles(profile.budget)}. El tope aplicado por el cálculo de esta web es ${soles(ranking.effectiveBudget)}.`;
  if (!ranking.listings.length) return {
    topic: "ranking", title: "No encontré viviendas con estos filtros",
    paragraphs: [criteria, "Puedes revisar el presupuesto, el área o los distritos. Mantengo tus datos actuales; no cambio los filtros sin que tú lo decidas."],
    action: { label: "Revisar mis filtros", href: "/explorar" },
  };

  return {
    topic: "ranking",
    title: `${ranking.matchedTotal} ${ranking.matchedTotal === 1 ? "opción coincide" : "opciones coinciden"} con tu búsqueda`,
    paragraphs: [
      criteria,
      "Estas son las primeras opciones ordenadas por el puntaje del proyecto. El precio es el publicado en un aviso histórico; confirma su disponibilidad y los datos antes de tomar una decisión. Esta pregunta no cambia los filtros de la búsqueda principal.",
    ],
    recommendations: ranking.listings.slice(0, 3).map(item => ({
      id: item.id, address: item.address, district: item.district,
      price: item.price, rooms: item.rooms, area: item.area, score: item.score,
      reasons: item.reasons.slice(0, 2),
    })),
    action: { label: "Abrir catálogo con mis filtros actuales", href: "/explorar" },
  };
}

export function unavailableSearchAnswer(): HelpAnswer {
  return {
    topic: "ranking", title: "No pude consultar el catálogo ahora",
    paragraphs: ["Tu pregunta sigue aquí. Intenta de nuevo o abre la búsqueda para revisar las viviendas disponibles."],
    action: { label: "Explorar viviendas", href: "/explorar" },
  };
}
