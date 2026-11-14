import assert from "node:assert/strict";
import test from "node:test";
import {
  affordableCap,
  rankListings,
  validateProfile,
  toPublicListing,
  type BuyerProfile,
  type CatalogListing,
} from "../lib/recommendation.ts";

const profile: BuyerProfile = {
  name: "Ari",
  income: 8_000,
  savings: 70_000,
  budget: 500_000,
  minRooms: 2,
  minArea: 60,
  districts: [],
  weights: { price: 0.5, safety: 0.3, convenience: 0.2 },
};

function listing(id: string, district: string, price: number, rooms = 2, area = 65): CatalogListing {
  return {
    id,
    district,
    address: `${id} address`,
    price,
    area,
    rooms,
    bathrooms: 1,
    parking: 0,
    maintenance: null,
    predictedPrice: price * 1.1,
    scores: { price: 80, safety: 70, convenience: 60 },
    location: null,
    dataPartial: false,
    flags: [],
    url: null,
    availability: "unverified",
    duplicateGroupId: null,
  };
}

test("validates bounded, finite profile values and rejects malformed weights", () => {
  assert.equal(validateProfile(profile).valid, true);
  const invalid = validateProfile({ ...profile, income: Number.POSITIVE_INFINITY });
  assert.equal(invalid.valid, false);
  const invalidWeights = validateProfile({ ...profile, weights: { ...profile.weights, safety: -1 } });
  assert.equal(invalidWeights.valid, false);
});

test("affordability cap uses both mortgage capacity and minimum down payment savings", () => {
  assert.ok(affordableCap(profile) > 0);
  assert.equal(affordableCap({ income: profile.income, savings: 0 }), 0);
});

test("ranking keeps every eligible home when matches are in one district", () => {
  const listings = [
    listing("1", "A", 200_000),
    listing("2", "A", 210_000),
    listing("3", "A", 220_000),
    listing("4", "A", 230_000),
    listing("5", "B", 240_000, 1),
    listing("6", "C", 510_000),
  ];
  const result = rankListings(listings, profile);
  assert.deepEqual(result.listings.map((item) => item.id), ["1", "2", "3", "4"]);
  assert.equal(result.total, 4);
  assert.equal(result.matchedTotal, 4);
  assert.equal(result.diversityLimited, false);
  assert.equal(result.effectiveBudget, Math.min(profile.budget, affordableCap(profile)));
  assert.ok(result.listings[0]?.score >= 0 && result.listings[0]?.score <= 100);
  assert.ok(result.listings[0]?.reasons.length);
});

test("affinity ordering diversifies only when more than one district matches", () => {
  const listings = [
    listing("a1", "A", 200_000), listing("a2", "A", 210_000),
    listing("a3", "A", 220_000), listing("a4", "A", 230_000),
    listing("b1", "B", 240_000),
  ];
  const result = rankListings(listings, profile);
  assert.deepEqual(result.listings.map((item) => item.id), ["a1", "a2", "a3", "b1"]);
  assert.equal(result.matchedTotal, 5);
  assert.equal(result.total, 4);
  assert.equal(result.diversityLimited, true);
});

test("recommendation reasons describe measured criteria and do not present a model estimate as a sale price", () => {
  const result = rankListings([listing("one", "A", 200_000)], profile);
  assert.match(result.listings[0].reasons[0], /Precio frente al modelo: índice 80\/100/);
  assert.match(result.listings[0].reasons[1], /Seguridad distrital: índice 70\/100/);
  assert.ok(result.listings[0].reasons.some(reason => reason.includes("referencia del modelo")));
});

test("duplicate capture groups retain distinct units", () => {
  const first = { ...listing("one", "A", 200_000), duplicateGroupId: "same-group" };
  const exactCopy = { ...listing("two", "A", 200_000), duplicateGroupId: "same-group" };
  const anotherUnit = { ...listing("three", "A", 200_000, 3), duplicateGroupId: "same-group" };
  const result = rankListings([first, exactCopy, anotherUnit], profile);
  assert.deepEqual(result.listings.map(item => item.id), ["one", "three"]);
  assert.equal(result.total, 2);
});

test("price sorting keeps district diversity uncapped and supports pagination", () => {
  const listings = [listing("1", "A", 200_000), listing("2", "A", 210_000), listing("3", "A", 220_000), listing("4", "A", 230_000)];
  const result = rankListings(listings, profile, { sort: "price_desc", limit: 2, offset: 1 });
  assert.deepEqual(result.listings.map((item) => item.id), ["3", "2"]);
  assert.equal(result.total, 4);
  assert.equal(result.matchedTotal, 4);
  assert.equal(result.diversityLimited, false);
});

test("location-only filter excludes listings without coordinates", () => {
  const listings = [listing("1", "A", 200_000), { ...listing("2", "B", 210_000), location: { lat: -12, lng: -77, precision: "approximate" } }];
  const result = rankListings(listings, profile, { onlyLocated: true });
  assert.deepEqual(result.listings.map((item) => item.id), ["2"]);
});

test("zero preference weights are rejected", () => {
  assert.throws(() => rankListings([], { ...profile, weights: { price: 0, safety: 0, convenience: 0 } }));
});


test("TEA is converted to a monthly effective rate and savings are added to loan capacity", () => {
  const p={income:15000,savings:150000};
  const r=(1.09 ** (1/12))-1;
  const expected=Math.floor(Math.min(p.savings/.1,p.income*.3*(1-(1+r)**-240)/r+p.savings));
  assert.equal(affordableCap(p),expected);
});
test("known retired listings do not enter recommendations", () => {
  const item={...listing("retired","A",200000),flags:["retired_at_last_check"]};
  assert.equal(rankListings([item],profile).total,0);
});
test("listings outside the model area range remain excluded from recommendations", () => {
  const item = { ...listing("review-area", "A", 200000), area: 84580, flags: ["model_outside_area_range"] };
  const result = rankListings([item, listing("valid", "A", 210000)], profile);
  assert.deepEqual(result.listings.map(row => row.id), ["valid"]);
  assert.equal(result.matchedTotal, 1);
});
test("price gap is measured against model reference, not asking price", () => {
  const item={...listing("discount","A",200000),predictedPrice:250000};
  assert.equal(rankListings([item],profile).listings[0].opportunity,20);
});

test("district conflicts are excluded and public details do not expose unsupported references", () => {
  for (const flag of ["capture_district_conflict", "model_outside_area_range"]) {
    const original = { ...listing("review", "A", 200000), flags: [flag] };
    const published = toPublicListing(original);
    assert.equal(published.predictedPrice, null);
    assert.equal(published.scores.price, null);
    assert.equal(published.price, original.price);
    assert.equal(published.area, original.area);
    assert.notEqual(original.predictedPrice, null);
    assert.notEqual(original.scores.price, null);
    if (flag === "capture_district_conflict") {
      assert.equal(published.scores.safety, null);
      assert.equal(published.scores.convenience, null);
    }
    assert.equal(rankListings([original], profile).total, 0);
  }
  const valid = listing("valid", "A", 200000);
  assert.equal(toPublicListing(valid).predictedPrice, valid.predictedPrice);
});
