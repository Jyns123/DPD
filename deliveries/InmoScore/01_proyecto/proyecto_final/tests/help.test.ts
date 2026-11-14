import assert from "node:assert/strict";
import test from "node:test";
import { answerQuestion, answerTopic, followUpTopics, suggestedTopics, HELP_TOPICS } from "../lib/help.ts";

test("every quick topic has a useful grounded answer", () => {
  for (const topic of HELP_TOPICS) {
    const answer = answerTopic(topic.id);
    assert.equal(answer.topic, topic.id);
    assert.ok(answer.title && answer.paragraphs.length >= 2);
  }
});

test("accents and casing do not prevent topic detection", () => {
  assert.equal(answerQuestion("¿POR QUÉ EL CRÉDITO tiene un tope?").topic, "budget");
  assert.equal(answerQuestion("¿Qué significa la PREDICCIÓN?").topic, "model");
  assert.equal(answerQuestion("¿Dónde están mis fotografías?").topic, "map");
});

test("empty results take precedence over budget words", () => {
  assert.equal(answerQuestion("No hay resultados con mi presupuesto").topic, "no_results");
});

test("privacy questions are not misclassified as save actions", () => {
  assert.equal(answerQuestion("¿Cómo guardar mis datos personales?").topic, "privacy");
});

test("unknown questions do not invent property details or transactions", () => {
  const answer = answerQuestion("Quiero comprar el departamento 123 mañana");
  assert.equal(answer.topic, "unknown");
  assert.match(answer.paragraphs.join(" "), /No tiene información adicional/);
});

test("budget context only includes finite values from a completed search", () => {
  const answer = answerTopic("budget", { cap: 390676, effectiveBudget: 390676 });
  assert.match(answer.paragraphs[1], /390/);
  assert.match(answer.paragraphs[1], /última búsqueda/);
  assert.match(answerTopic("budget", { cap: NaN, effectiveBudget: Infinity }).paragraphs[1], /No conocemos/);
  assert.match(answerTopic("budget").paragraphs[1], /No conocemos/);
});

test("negative outcomes and model uncertainty remain explicit", () => {
  assert.match(answerTopic("no_results", { matchedTotal: 0 }).paragraphs[0], /no encontró/);
  assert.match(answerTopic("model").paragraphs.join(" "), /No son una garantía/);
  assert.match(answerTopic("favorites").paragraphs.join(" "), /no genera una compra/);
});

test("favorite action respects whether a session exists", () => {
  assert.equal(answerTopic("favorites", { signedIn: false }).action?.href, "/ingresar");
  assert.equal(answerTopic("favorites", { signedIn: true }).action?.href, "/guardados");
});

test("help prioritizes the current page without changing profile values", () => {
  assert.deepEqual(suggestedTopics({ path: "/explorar", matchedTotal: 0 }), ["no_results", "budget", "quality"]);
  assert.deepEqual(suggestedTopics({ path: "/inmueble/123" }), ["model", "quality", "compare"]);
  assert.deepEqual(suggestedTopics({ path: "/perfil" }), ["budget", "ranking", "privacy"]);
  assert.equal(suggestedTopics({ path: "/explorar", comparedCount: 2 })[0], "compare");
});

test("unanswered questions and negative feedback offer distinct supported follow-ups", () => {
  const allowed = new Set(HELP_TOPICS.map(topic => topic.id));
  for (const topic of [...allowed, "unknown"] as const) {
    const options = followUpTopics(topic);
    assert.ok(options.length >= 2);
    assert.ok(options.every(option => allowed.has(option) && option !== topic));
    assert.equal(new Set(options).size, options.length);
  }
});
