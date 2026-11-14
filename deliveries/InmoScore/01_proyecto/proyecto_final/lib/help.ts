import { RANKING_ASSUMPTIONS, type BuyerProfile } from "./recommendation.ts";

export const HELP_TOPICS = [
  { id: "start", label: "Por dónde empezar" },
  { id: "budget", label: "Mi presupuesto y mi tope" },
  { id: "ranking", label: "Cómo se ordenan las viviendas" },
  { id: "no_results", label: "No encuentro resultados" },
  { id: "model", label: "Qué estima el modelo" },
  { id: "quality", label: "Avisos que necesitan revisión" },
  { id: "map", label: "Ubicación y fotografías" },
  { id: "favorites", label: "Guardar mis opciones" },
  { id: "compare", label: "Comparar viviendas" },
  { id: "privacy", label: "Mi cuenta y mis datos" },
] as const;

export type HelpTopic = (typeof HELP_TOPICS)[number]["id"];
export type HelpContext = {
  path?: string;
  comparedCount?: number;
  effectiveBudget?: number;
  cap?: number;
  matchedTotal?: number;
  signedIn?: boolean;
  profile?: BuyerProfile;
  districts?: string[];
};

// Sugiere la ayuda que corresponde a la pantalla, sin cambiar los datos del usuario.
export function suggestedTopics(context: HelpContext = {}): HelpTopic[] {
  if (context.path === "/explorar" && context.matchedTotal === 0) return ["no_results", "budget", "quality"];
  if (context.path?.startsWith("/inmueble/")) return ["model", "quality", "compare"];
  if (context.path === "/perfil" || (context.path === "/registro" && context.signedIn)) return ["budget", "ranking", "privacy"];
  if (context.path === "/guardados") return ["favorites", "compare", "quality"];
  if (context.path === "/cuenta" || context.path === "/ingresar" || context.path === "/registro") return ["privacy", "favorites", "start"];
  if ((context.comparedCount ?? 0) > 0) return ["compare", "model", "quality"];
  if (context.path === "/explorar") return ["ranking", "budget", "map"];
  return ["start", "budget", "model"];
}

export function followUpTopics(topic: HelpAnswer["topic"]): HelpTopic[] {
  const followUps: Record<HelpAnswer["topic"], HelpTopic[]> = {
    start: ["budget", "ranking"], budget: ["no_results", "ranking"],
    ranking: ["budget", "model"], no_results: ["budget", "quality", "map"],
    model: ["quality", "ranking"], quality: ["model", "map"],
    map: ["quality", "no_results"], favorites: ["privacy", "compare"],
    compare: ["model", "favorites"], privacy: ["favorites", "start"],
    unknown: ["budget", "no_results", "model"],
  };
  return followUps[topic];
}
export type HelpAnswer = {
  topic: HelpTopic | "unknown";
  title: string;
  paragraphs: string[];
  action?: { label: string; href: string };
  recommendations?: {
    id: string;
    address: string;
    district: string;
    price: number;
    rooms: number;
    area: number;
    score: number;
    reasons: string[];
  }[];
};

const money = (amount: number) => new Intl.NumberFormat("es-PE", {
  style: "currency", currency: "PEN", maximumFractionDigits: 0,
}).format(amount);

function finiteMoney(value: number | undefined): value is number {
  return typeof value === "number" && Number.isFinite(value) && value >= 0;
}

// Respuestas verificables sobre el funcionamiento del proyecto. No consulta un LLM.
export function answerTopic(topic: HelpTopic, context: HelpContext = {}): HelpAnswer {
  const assumptions = RANKING_ASSUMPTIONS;
  switch (topic) {
    case "start": return {
      topic, title: "Empieza con una búsqueda sencilla",
      paragraphs: [
        "Puedes explorar sin crear una cuenta. Revisa ingresos, ahorro, presupuesto y requisitos: los valores iniciales son un ejemplo, no tus datos.",
        "Después elige distritos y prioridades. Abre un detalle para revisar el precio anunciado, su referencia y las advertencias. La cuenta sirve para conservar tu perfil y tus favoritos.",
      ], action: { label: "Revisar mi perfil", href: "/perfil" },
    };
    case "budget": return {
      topic, title: "El presupuesto deseado no siempre es el tope",
      paragraphs: [
        `La búsqueda utiliza el menor valor entre tu presupuesto deseado y el tope estimado según ingresos y ahorro. El cálculo usa supuestos: TEA de ${assumptions.tea * 100}%, ${assumptions.years} años, cuota máxima de ${assumptions.maxIncomeShare * 100}% del ingreso e inicial mínima de ${assumptions.minDown * 100}%.`,
        finiteMoney(context.effectiveBudget) && finiteMoney(context.cap)
          ? `En tu última búsqueda, el tope calculado fue ${money(context.cap)} y el presupuesto aplicado fue ${money(context.effectiveBudget)}. Si cambiaste los datos, espera a que termine la búsqueda para revisar los nuevos valores.`
          : "Abre una búsqueda para ver el tope calculado con tu perfil. No conocemos ese resultado hasta que la aplicación lo calcule.",
        "Es una simulación para comparar opciones. No es una aprobación de crédito ni una oferta de un banco; revisa condiciones y gastos adicionales antes de una decisión real.",
      ], action: { label: "Revisar presupuesto", href: "/perfil" },
    };
    case "ranking": return {
      topic, title: "Tú eliges qué pesa más",
      paragraphs: [
        "Primero se aplican presupuesto y requisitos. Después el puntaje combina precio, seguridad y conveniencia según los pesos que elegiste. Cambiar esos pesos puede cambiar el orden; también puede dejarlo igual.",
        "El puntaje es una ayuda para comparar. No es la probabilidad de comprar ni la precisión del modelo. Los indicadores de seguridad y conveniencia describen el distrito, no la seguridad de una vivienda concreta.",
      ], action: { label: "Ajustar mi búsqueda", href: "/explorar" },
    };
    case "no_results": return {
      topic, title: "Una búsqueda sin coincidencias también es útil",
      paragraphs: [
        context.matchedTotal === 0
          ? "La última búsqueda no encontró coincidencias con los requisitos y el presupuesto aplicados. Esto no significa que la aplicación haya fallado."
          : "Si no ves opciones, revisa primero el presupuesto aplicado y los requisitos. Un aviso puede quedar fuera por precio, área, dormitorios, distrito o datos pendientes de revisar.",
        "Comprueba el tope antes de subir el presupuesto deseado. Puedes ampliar distritos, revisar el mínimo de área o quitar el filtro de ubicación, únicamente si esos cambios se ajustan a lo que buscas. No hace falta cambiar tus ingresos para conseguir resultados.",
      ], action: { label: "Volver a los filtros", href: "/explorar" },
    };
    case "model": return {
      topic, title: "Una referencia de precio anunciado",
      paragraphs: [
        "El modelo HistGradientBoosting usa características del departamento y su distrito para estimar el precio anunciado. Esas referencias se preparan por lotes en Python y la web las lee del catálogo; no entrena un modelo nuevo con cada consulta.",
        "La evaluación histórica incluida informa un error absoluto medio cercano a S/119,801 y un error porcentual absoluto mediano de 12.2% en 779 casos. No son una garantía por inmueble ni una validación de disponibilidad o de la captura más reciente.",
        "El modelo no estima una venta cerrada, una rentabilidad ni una hipoteca aprobada. Revisa las advertencias y contrasta el aviso antes de recomendar una compra.",
      ],
    };
    case "quality": return {
      topic, title: "Las advertencias ayudan a revisar",
      paragraphs: [
        "Un mantenimiento desconocido no equivale a cero. Una ubicación aproximada no representa la puerta del inmueble. Los anuncios son históricos y su disponibilidad no está confirmada.",
        "Si el área está fuera del rango utilizado por el modelo o hay un conflicto de distrito, la aplicación no muestra una referencia de precio utilizable y excluye ese aviso del ranking. Conserva el dato original para poder revisarlo.",
        "Una diferencia grande entre precio anunciado y referencia necesita revisión: por sí sola no demuestra que exista una ganga ni que el dato sea falso.",
      ],
    };
    case "map": return {
      topic, title: "Mira también el alcance de cada imagen",
      paragraphs: [
        "Las fotografías de referencia de la interfaz son ilustrativas; no verifican el estado de la vivienda anunciada. El detalle indica cuándo una ubicación es aproximada o no tiene coordenadas suficientes.",
        "El mapa incluye únicamente los avisos con ubicación. Si al activarlo aparecen menos opciones, quita el filtro «Con ubicación» para volver a ver el resto. No se inventan coordenadas para completar el mapa.",
      ], action: { label: "Explorar viviendas", href: "/explorar" },
    };
    case "favorites": return {
      topic, title: "Conserva las opciones que te interesan",
      paragraphs: [
        context.signedIn
          ? "Pulsa el corazón de una vivienda para guardarla en tu cuenta. Puedes encontrarla en «Guardados» y retirarla pulsando de nuevo el corazón."
          : "Puedes explorar sin cuenta. Para conservar favoritos entre visitas, ingresa o crea una cuenta; la aplicación te ayudará a continuar el guardado que solicitaste.",
        "Guardar una vivienda no contacta al anunciante, no reserva el inmueble y no genera una compra.",
      ], action: { label: context.signedIn ? "Ver guardados" : "Ingresar", href: context.signedIn ? "/guardados" : "/ingresar" },
    };
    case "compare": return {
      topic, title: "Dos o tres opciones, lado a lado",
      paragraphs: [
        "Marca «Comparar» en dos o tres tarjetas y abre la comparación en la barra inferior. Revisa precio, área, dormitorios, referencia y datos de zona.",
        "Puedes quitar una opción para añadir otra. Las diferencias te ayudan a explicar tu elección; no sustituyen la verificación de los avisos.",
      ], action: { label: "Elegir viviendas", href: "/explorar" },
    };
    case "privacy": return {
      topic, title: "Elige qué quieres conservar",
      paragraphs: [
        "La cuenta conserva tu perfil y tus favoritos en la base del proyecto. Puedes cerrar sesión o eliminar tu cuenta desde «Mi cuenta», confirmando tu contraseña.",
        "Esta conversación funciona con respuestas locales sobre la aplicación. No se envía a una persona ni a un servicio de inteligencia artificial. Se borra al recargar la página o al pulsar «Nueva consulta». No escribas contraseñas ni datos personales aquí.",
      ], action: { label: "Ver mi cuenta", href: "/cuenta" },
    };
  }
}

const patterns: { topic: HelpTopic; terms: RegExp }[] = [
  { topic: "privacy", terms: /\b(privacidad|contrasena|datos personales|eliminar cuenta|borrar cuenta|cerrar sesion)\b/ },
  { topic: "no_results", terms: /\b(no encuentro|sin resultados|no hay|cero|0 resultados|no aparecen|sin coincidencias)\b/ },
  { topic: "budget", terms: /\b(presupuesto|tope|credito|hipoteca|ahorro|ingreso|ingresos|cuota|tea)\b/ },
  { topic: "model", terms: /\b(modelo|prediccion|estima|estimacion|precision|mae|error|inteligencia)\b/ },
  { topic: "ranking", terms: /\b(puntaje|score|ranking|pesos|prioridades|orden|seguridad|conveniencia)\b/ },
  { topic: "quality", terms: /\b(advertencia|advertencias|calidad|mantenimiento|disponible|disponibilidad|conflicto|fuera de rango|ganga)\b/ },
  { topic: "map", terms: /\b(mapa|ubicacion|coordenadas|fotos|fotografias|imagenes)\b/ },
  { topic: "favorites", terms: /\b(favoritos|guardar|guardados|corazon)\b/ },
  { topic: "compare", terms: /\b(comparar|comparacion)\b/ },
  { topic: "start", terms: /\b(empezar|inicio|comenzar|como funciona|ayuda|hola)\b/ },
];

export function answerQuestion(question: string, context: HelpContext = {}): HelpAnswer {
  const normalized = question.trim().slice(0, 400).normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  const match = patterns.find(({ terms }) => terms.test(normalized));
  if (match) return answerTopic(match.topic, context);
  return {
    topic: "unknown", title: "Revisemos una duda concreta",
    paragraphs: [
      "Esta guía responde sobre el presupuesto, los filtros, el modelo, los favoritos y la comparación. No tiene información adicional de los anuncios ni atiende consultas con una persona.",
      "Elige uno de los temas de arriba o pregunta, por ejemplo: «¿Por qué mi tope es menor que mi presupuesto?». Si necesitas confirmar un dato del inmueble, revisa el aviso original.",
    ],
  };
}
