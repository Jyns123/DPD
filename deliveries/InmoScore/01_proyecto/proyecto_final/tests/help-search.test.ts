import assert from "node:assert/strict";
import test from "node:test";
import { answerHelpSearch, parseHelpSearch } from "../lib/help-search.ts";
import type { BuyerProfile } from "../lib/recommendation.ts";

const districts = ["Miraflores", "Barranco", "San Miguel"];
const profile: BuyerProfile = {
  income: 15000, savings: 150000, budget: 700000, minRooms: 1,
  minArea: 55, districts: [], weights: { price: .35, safety: .35, convenience: .3 },
};

test("a concrete question reads only catalog districts and explicit preferences", () => {
  assert.deepEqual(
    parseHelpSearch("Busco dos dormitorios en Miraflores por S/ 400,000. ¿Qué me recomiendas?", districts),
    { district: "Miraflores", minRooms: 2, budget: 400000 },
  );
  assert.equal(parseHelpSearch("¿Por qué no hay resultados con mi presupuesto?", districts), null);
});

test("a recommendation uses the existing ranking result and links to its real listing", async () => {
  const previousFetch = globalThis.fetch;
  let submitted: Record<string, unknown> | null = null;
  globalThis.fetch = async (_input, init) => {
    submitted = JSON.parse(String(init?.body));
    return Response.json({
      matchedTotal: 1, effectiveBudget: 400000, cap: 900000,
      listings: [{ id: "aviso_1", district: "Miraflores", address: "Calle de prueba", price: 390000,
        rooms: 2, area: 62, score: 82, reasons: ["Precio frente al modelo: índice 80/100"] }],
    });
  };
  try {
    const search = parseHelpSearch("Busco 2 dormitorios en Miraflores por S/ 400,000", districts)!;
    const answer = await answerHelpSearch(search, { profile, districts });
    assert.deepEqual((submitted as {profile: BuyerProfile} | null)?.profile.districts, ["Miraflores"]);
    assert.equal((submitted as {profile: BuyerProfile} | null)?.profile.budget, 400000);
    assert.equal(answer.recommendations?.[0].id, "aviso_1");
    assert.match(answer.paragraphs.join(" "), /aviso histórico/);
  } finally {
    globalThis.fetch = previousFetch;
  }
});

test("no matching listings does not invent an offer", async () => {
  const previousFetch = globalThis.fetch;
  globalThis.fetch = async () => Response.json({ matchedTotal: 0, effectiveBudget: 300000, cap: 300000, listings: [] });
  try {
    const answer = await answerHelpSearch({ district: "Miraflores", budget: 400000 }, { profile, districts });
    assert.equal(answer.recommendations, undefined);
    assert.match(answer.title, /No encontré viviendas/);
    assert.match(answer.paragraphs[0], /300,000/);
  } finally {
    globalThis.fetch = previousFetch;
  }
});
