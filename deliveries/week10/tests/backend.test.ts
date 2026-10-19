import assert from "node:assert/strict";
import test from "node:test";
import {
  affordableCap,
  rankListings,
  validateProfile,
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

test("ranking filters by budget and home requirements, then limits matching diversity", () => {
  const listings = [
    listing("1", "A", 200_000),
    listing("2", "A", 210_000),
    listing("3", "A", 220_000),
    listing("4", "A", 230_000),
    listing("5", "B", 240_000, 1),
    listing("6", "C", 510_000),
  ];
  const result = rankListings(listings, profile);
  assert.deepEqual(result.listings.map((item) => item.id), ["1", "2", "3"]);
  assert.equal(result.total, 3);
  assert.ok(result.listings[0]?.score >= 0 && result.listings[0]?.score <= 100);
  assert.ok(result.listings[0]?.reasons.length);
});

test("price sorting keeps district diversity uncapped and supports pagination", () => {
  const listings = [listing("1", "A", 200_000), listing("2", "A", 210_000), listing("3", "A", 220_000), listing("4", "A", 230_000)];
  const result = rankListings(listings, profile, { sort: "price_desc", limit: 2, offset: 1 });
  assert.deepEqual(result.listings.map((item) => item.id), ["3", "2"]);
  assert.equal(result.total, 4);
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
test("price gap is measured against model reference, not asking price", () => {
  const item={...listing("discount","A",200000),predictedPrice:250000};
  assert.equal(rankListings([item],profile).listings[0].opportunity,20);
});
