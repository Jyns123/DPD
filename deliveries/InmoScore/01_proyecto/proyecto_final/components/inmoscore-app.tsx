"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import type {
  BuyerProfile,
  CatalogListing,
  RankedListing,
} from "../lib/recommendation";
import { affordableCap, needsInputReview, validateProfile } from "../lib/recommendation";
import { trackInteraction } from "../lib/track-interaction";
import InmoScoreHelp from "./inmoscore-help";
import CityPhotoGallery from "./city-photo-gallery";
import PriorityGraphic from "./priority-graphic";
import NextLink from "next/link";
import Image from "next/image";
import {
  ArrowRight,
  ArrowUpRight,
  ArrowLeft,
  BedDouble,
  Bath,
  CarFront,
  Check,
  ChevronDown,
  ChevronRight,
  Heart,
  House,
  LayoutGrid,
  MapPin,
  Menu,
  Search,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Trees,
  UserRound,
  X,
  Scale,
  Info,
  LogOut,
  CheckCircle2,
  Bookmark,
  Building2,
  LoaderCircle,
  Eye,
  EyeOff,
} from "lucide-react";
import "./inmoscore-experience.css";

type Me = {
  user: { id: string; name: string; email: string } | null;
  profile: BuyerProfile | null;
  favorites: string[];
};
type Ranking = {
  listings: RankedListing[];
  total: number;
  matchedTotal: number;
  cap: number;
  effectiveBudget: number;
  diversityLimited: boolean;
  warnings: string[];
};
const DEFAULT: BuyerProfile = {
  name: "",
  income: 15000,
  savings: 150000,
  budget: 700000,
  minRooms: 2,
  minArea: 55,
  districts: [],
  weights: { price: 0.35, safety: 0.35, convenience: 0.3 },
};
const MONEY = new Intl.NumberFormat("es-PE", { maximumFractionDigits: 0 });
const soles = (n: number) => `S/ ${MONEY.format(n)}`;
const day = (iso?: string | null) =>
  iso ? iso.slice(0, 10).split("-").reverse().join("/") : "fecha desconocida";
const PHOTOS = ["/interior.jpg", "/interior-2.jpg", "/interior-3.jpg"];
// IDs can contain letters; every listing still needs a valid reference image.
const photo = (id: string) =>
  PHOTOS[
    Array.from(id).reduce((sum, char) => sum + char.charCodeAt(0), 0) %
      PHOTOS.length
  ];
const photoDimensions = (id: string) => photo(id) === "/interior.jpg"
  ? { width: 1600, height: 1200 }
  : { width: 900, height: 600 };
const FLAGS: Record<string, string> = {
  maintenance_unknown: "Mantenimiento por confirmar",
  possible_duplicate: "Posible publicación repetida",
  missing_geocode: "Sin ubicación precisa",
  geocode_context_only: "Ubicación aproximada",
  missing_context: "Datos de zona incompletos",
  retired_at_last_check: "Anuncio retirado en la última revisión",
  model_historical_only:
    "Referencia de un modelo evaluado con avisos históricos; falta validarla en esta captura",
  model_outside_area_range:
    "Área fuera del rango observado por el modelo; revisar el aviso",
  capture_district_conflict:
    "El distrito histórico no coincide con la captura; revisar el aviso",
};
function modelReference(item: CatalogListing) {
  if (item.flags.includes("capture_district_conflict"))
    return "Distrito por revisar";
  if (item.flags.includes("model_outside_area_range"))
    return "Área por revisar";
  return item.predictedPrice ? soles(item.predictedPrice) : "Sin referencia";
}
function pricePerSquareMeter(item: CatalogListing) {
  if (needsInputReview(item)) {
    return "Precio por m² pendiente de revisar";
  }
  return `${soles(Math.round(item.price / item.area))} por m²`;
}
function changePage(update: () => void) {
  update();
}
function districtIndicator(
  item: CatalogListing,
  key: "safety" | "convenience",
) {
  if (item.flags.includes("capture_district_conflict"))
    return "Distrito por revisar";
  const value = item.scores[key];
  return value === null ? "Sin datos" : `${Math.round(value * 100)}/100`;
}
async function api<T = Record<string, unknown>>(
  path: string,
  options?: RequestInit,
) {
  let r: Response;
  try {
    r = await fetch(path, {
      cache: "no-store",
      ...options,
      headers: { "Content-Type": "application/json", ...options?.headers },
    });
  } catch (cause) {
    if (options?.signal?.aborted) throw cause;
    throw Error("No pudimos conectarnos. Revisa tu conexión y vuelve a intentarlo; tus filtros siguen aquí.");
  }
  const body = await r.json().catch(() => null) as (T & { message?: string }) | null;
  if (!r.ok) throw Error(body?.message || "El servicio no pudo responder. Espera un momento y vuelve a intentarlo.");
  if (!body) throw Error("La respuesta no llegó completa. Vuelve a intentar la consulta.");
  return body;
}
function Link({
  href,
  children,
  className = "",
}: {
  href: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <a
      href={href}
      className={className}
      onClick={(e) => {
        if (
          e.button === 0 &&
          !e.ctrlKey &&
          !e.metaKey &&
          !e.shiftKey &&
          !e.altKey
        ) {
          e.preventDefault();
          changePage(() => {
            window.history.pushState({}, "", href);
            window.dispatchEvent(new PopStateEvent("popstate"));
            const hash = href.split("#")[1];
            if (hash) {
              window.requestAnimationFrame(() => document.getElementById(hash)?.scrollIntoView());
            } else {
              const root = document.documentElement;
              const previousScroll = root.style.scrollBehavior;
              root.style.scrollBehavior = "auto";
              window.scrollTo(0, 0);
              root.style.scrollBehavior = previousScroll;
            }
          });
        }
      }}
    >
      {children}
    </a>
  );
}
export default function InmoScoreApp() {
  const [path, setPath] = useState("/"),
    [me, setMe] = useState<Me>({ user: null, profile: null, favorites: [] });
  const [profile, setProfile] = useState<BuyerProfile>({
      ...DEFAULT,
      weights: { ...DEFAULT.weights },
    }),
    [districts, setDistricts] = useState<string[]>([]);
  const [result, setResult] = useState<Ranking | null>(null),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [toast, setToast] = useState("");
  const [menu, setMenu] = useState(false),
    [filters, setFilters] = useState(false),
    [sort, setSort] = useState("match"),
    [onlyLocated, setOnlyLocated] = useState(false);
  const [detail, setDetail] = useState<CatalogListing | null>(null),
    [saved, setSaved] = useState<CatalogListing[]>([]),
    [compare, setCompare] = useState<CatalogListing[]>([]);
  const [compareOpen, setCompareOpen] = useState(false),
    [consent, setConsent] = useState(false),
    [authPrompt, setAuthPrompt] = useState(false),
    [deleteOpen, setDeleteOpen] = useState(false);
  const [page, setPage] = useState(0),
    [view, setView] = useState("grid"),
    [mapListing, setMapListing] = useState<CatalogListing | null>(null),
    [savingId, setSavingId] = useState("");
  const [authName, setAuthName] = useState(""),
    [authEmail, setAuthEmail] = useState(""),
    [authPassword, setAuthPassword] = useState(""),
    [authConfirm, setAuthConfirm] = useState(""),
    [deletePassword, setDeletePassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [confirmTouched, setConfirmTouched] = useState(false);
  const [districtQuery, setDistrictQuery] = useState("");
  const [rankingBusy, setRankingBusy] = useState(false);
  const [districtsError, setDistrictsError] = useState(false);
  const [districtsBusy, setDistrictsBusy] = useState(false);
  const [sessionLoaded, setSessionLoaded] = useState(false);
  const [emptyFinancialFields, setEmptyFinancialFields] = useState<string[]>([]);
  const [pendingFavorite, setPendingFavorite] = useState<{
    id: string;
    returnPath: string;
  } | null>(null);
  const requestId = useRef(0);
  const rankingRequest = useRef<AbortController | null>(null);
  const navigation = useRef<HTMLElement>(null);
  const menuToggle = useRef<HTMLButtonElement>(null);
  const districtInput = useRef<HTMLInputElement>(null);
  const previousPath = useRef("/");
  const filterPanel = useRef<HTMLElement>(null);
  useDialogFocus(filterPanel, filters);
  const reloadDistricts = async () => {
    setDistrictsBusy(true);
    try {
      const data = await api<{ districts: string[] }>("/api/districts");
      setDistricts(data.districts ?? []);
      setDistrictsError(false);
    } catch {
      setDistrictsError(true);
      trackInteraction("api_error", { topic: "districts" });
    } finally { setDistrictsBusy(false); }
  };
  useEffect(() => {
    if (path === previousPath.current) return;
    previousPath.current = path;
    const frame = requestAnimationFrame(() => document.getElementById("main")?.focus({ preventScroll: true }));
    return () => cancelAnimationFrame(frame);
  }, [path]);
  useEffect(() => {
    const screen = window.matchMedia("(max-width: 760px)");
    const closeDesktopFilters = () => {
      if (!screen.matches) setFilters(false);
    };
    screen.addEventListener("change", closeDesktopFilters);
    return () => screen.removeEventListener("change", closeDesktopFilters);
  }, []);
  const go = useCallback((next: string) => {
    changePage(() => {
      window.history.pushState({}, "", next);
      window.dispatchEvent(new Event('inmoscore:navigate'));
      setPath(next);
      setMenu(false);
      setError("");
      setDetail(null);
      setBusy(false);
      setFilters(false);
      setShowPassword(false);
      setConfirmTouched(false);
      setPage(0);
      if (next !== "/ingresar" && next !== "/registro") setPendingFavorite(null);
      const root = document.documentElement;
      const previousScroll = root.style.scrollBehavior;
      root.style.scrollBehavior = "auto";
      window.scrollTo(0, 0);
      root.style.scrollBehavior = previousScroll;
    });
  }, []);
  useEffect(() => {
    let active = true;
    const pop = () => {
      setPath(window.location.pathname);
      setMenu(false);
      setError("");
      setDetail(null);
      setBusy(false);
      setFilters(false);
      setShowPassword(false);
      setConfirmTouched(false);
      setPage(0);
      if (!["/ingresar", "/registro"].includes(window.location.pathname))
        setPendingFavorite(null);
    };
    window.addEventListener("popstate", pop);
    // Read the browser location after hydration; cancel if this view unmounts.
    queueMicrotask(() => {
      if (active) pop();
    });
    fetch("/api/me")
      .then(async (r) => {
        if (r.ok) {
          const m = (await r.json()) as Me;
          if (!active) return;
          setMe(m);
          if (m.profile) { setProfile(m.profile); setEmptyFinancialFields([]); }
          else if (m.user) {
            setProfile((p) => ({ ...p, name: m.user!.name, income: 0, savings: 0, budget: 0 }));
            setEmptyFinancialFields(["income", "savings", "budget"]);
          }
        } else if (r.status !== 401)
          setToast(
            "No se pudo recuperar la cuenta. Puedes explorar como visitante.",
          );
      })
      .catch(() => {
        if (active) setToast("No se pudo recuperar la cuenta. Puedes explorar como visitante.");
      })
      .finally(() => { if (active) setSessionLoaded(true); });
    api<{ districts: string[] }>("/api/districts")
      .then((d) => { if (active) setDistricts(d.districts ?? []); })
      .catch(() => { if (active) setDistrictsError(true); });
    return () => {
      active = false;
      window.removeEventListener("popstate", pop);
    };
  }, []);
  useEffect(() => {
    if (!sessionLoaded || !me.user || path !== "/") return;
    const destination = me.profile ? "/explorar" : "/registro";
    let active = true;
    queueMicrotask(() => {
      if (!active) return;
      window.history.replaceState({}, "", destination);
      window.dispatchEvent(new Event('inmoscore:navigate'));
      setPath(destination);
    });
    return () => { active = false; };
  }, [sessionLoaded, me.user, me.profile, path]);
  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(""), 5000);
    return () => clearTimeout(t);
  }, [toast]);
  useEffect(() => {
    if (!menu) return;
    const frame = requestAnimationFrame(() => navigation.current?.querySelector<HTMLAnchorElement>("a")?.focus());
    const outside = (event: PointerEvent) => {
      const target = event.target as Node;
      if (!navigation.current?.contains(target) && !menuToggle.current?.contains(target)) setMenu(false);
    };
    document.addEventListener("pointerdown", outside);
    return () => { cancelAnimationFrame(frame); document.removeEventListener("pointerdown", outside); };
  }, [menu]);
  useEffect(() => {
    const f = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setCompareOpen(false);
        setAuthPrompt(false);
        if (authPrompt) setPendingFavorite(null);
        setDeleteOpen(false);
        setFilters(false);
        setMenu(false);
        if (menu) menuToggle.current?.focus();
      }
    };
    document.addEventListener("keydown", f);
    return () => document.removeEventListener("keydown", f);
  }, [authPrompt, menu]);
  const loadRanking = useCallback(async () => {
    const id = ++requestId.current;
    rankingRequest.current?.abort();
    const controller = new AbortController();
    rankingRequest.current = controller;
    let timedOut = false;
    const timeout = setTimeout(() => { timedOut = true; controller.abort(); }, 15000);
    const startedAt = performance.now();
    setRankingBusy(true);
    setError("");
    try {
      const data = await api<Ranking>("/api/ranking", {
        method: "POST",
        signal: controller.signal,
        body: JSON.stringify({
          profile,
          sort,
          onlyLocated,
          offset: page * 12,
          limit: 12,
        }),
      });
      if (id === requestId.current) {
        setResult(data);
        trackInteraction("search", {
          resultCount: data.matchedTotal,
          durationMs: Math.round(performance.now() - startedAt),
          success: true,
          district: profile.districts.length === 1 ? profile.districts[0] : undefined,
        });
      }
    } catch (cause) {
      if (id === requestId.current && (!controller.signal.aborted || timedOut)) {
        setError(timedOut ? "La búsqueda está tardando más de lo esperado. Tus filtros siguen aquí; puedes reintentar." : (cause as Error).message);
        setResult(null);
        trackInteraction("search", { durationMs: Math.round(performance.now() - startedAt), success: false });
      }
    } finally {
      clearTimeout(timeout);
      if (id === requestId.current) setRankingBusy(false);
    }
  }, [profile, sort, onlyLocated, page]);
  useEffect(() => {
    if (path !== "/explorar") return;
    // Cancel stale responses immediately, including during the debounce interval.
    const pendingId = ++requestId.current;
    queueMicrotask(() => {
      if (pendingId === requestId.current) setRankingBusy(true);
    });
    const timer = setTimeout(loadRanking, 220);
    return () => {
      clearTimeout(timer);
      requestId.current += 1;
      rankingRequest.current?.abort();
    };
  }, [path, loadRanking]);
  useEffect(() => {
    if (!path.startsWith("/inmueble/")) return;
    let active = true;
    const controller = new AbortController();
    queueMicrotask(async () => {
      if (!active) return;
      setBusy(true);
      setError("");
      try {
        const data = await api<{ listing: CatalogListing }>(
          `/api/listings/${encodeURIComponent(path.split("/").pop()!)}`,
          { signal: controller.signal },
        );
        if (active) {
          setDetail(data.listing);
          trackInteraction("detail", { listingId: data.listing.id, district: data.listing.district });
        }
      } catch (cause) {
        if (active) {
          setError((cause as Error).message);
          trackInteraction("api_error", { topic: "detail" });
        }
      } finally {
        if (active) setBusy(false);
      }
    });
    return () => {
      active = false;
      controller.abort();
    };
  }, [path]);
  useEffect(() => {
    if (path !== "/guardados" || !me.user) return;
    let active = true;
    queueMicrotask(async () => {
      if (!active) return;
      setBusy(true);
      setError("");
      try {
        const results = await Promise.allSettled(
          me.favorites.map((id) =>
            api<{ listing: CatalogListing }>(`/api/listings/${id}`).then(
              (data) => data.listing,
            ),
          ),
        );
        if (active) {
          const successful = results
            .filter((r) => r.status === "fulfilled")
            .map((r) => (r as PromiseFulfilledResult<CatalogListing>).value);
          setSaved(successful);
          if (results.some((r) => r.status === "rejected"))
            setError(
              "Algunas viviendas guardadas no pudieron cargarse, pero el resto sigue disponible.",
            );
        }
      } catch (cause) {
        if (active) setError((cause as Error).message);
      } finally {
        if (active) setBusy(false);
      }
    });
    return () => {
      active = false;
    };
  }, [path, me.user, me.favorites]);
  const change = (key: keyof BuyerProfile, value: unknown) => {
    setProfile((p) => ({ ...p, [key]: value }));
    setPage(0);
  };
  const toggleFavorite = async (id: string) => {
    if (!me.user) {
      setPendingFavorite({ id, returnPath: path });
      setAuthPrompt(true);
      return;
    }
    if (savingId) return;
    setSavingId(id);
    try {
      const d = await api<{ favorites: string[] }>("/api/favorites", {
        method: "POST",
        body: JSON.stringify({ id }),
      });
      const was = me.favorites.includes(id);
      setMe((m) => ({ ...m, favorites: d.favorites }));
      if (!was) trackInteraction("favorite", { listingId: id });
      setToast(
        was
          ? "Vivienda retirada de tus guardados"
          : "Vivienda guardada en tu cuenta",
      );
    } catch (e) {
      setToast((e as Error).message);
      trackInteraction("api_error", { topic: "favorite" });
    } finally {
      setSavingId("");
    }
  };
  const toggleCompare = (item: CatalogListing) => {
    if (compare.some((x) => x.id === item.id))
      setCompare((c) => c.filter((x) => x.id !== item.id));
    else if (compare.length < 3) setCompare((c) => [...c, item]);
    else setToast("Puedes comparar hasta 3 viviendas a la vez.");
  };
  const saveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!me.user) {
      setAuthPrompt(true);
      return;
    }
    if (path === "/registro" && !consent) {
      setError("Acepta guardar tu perfil para continuar.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const d = await api<{ user: Me["user"]; profile: BuyerProfile }>(
        "/api/profile",
        { method: "PUT", body: JSON.stringify(profile) },
      );
      setMe((m) => ({ ...m, user: d.user, profile: d.profile }));
      go("/explorar");
      setToast("Tu perfil está guardado. Ya podemos buscar contigo.");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };
  const exploreWithProfile = () => {
    const validation = validateProfile(profile);
    if (!validation.valid) {
      setError(validation.error);
      return;
    }
    go("/explorar");
  };
  const submitAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (path === "/registro" && authPassword !== authConfirm) {
      setError("Las contraseñas no coinciden.");
      return;
    }
    setBusy(true);
    try {
      const m = await api<Me>(
        path === "/registro" ? "/api/auth/register" : "/api/auth/login",
        {
          method: "POST",
          body: JSON.stringify({
            name: authName,
            email: authEmail,
            password: authPassword,
          }),
        },
      );
      setMe(m);
      setAuthPassword("");
      setAuthConfirm("");
      if (m.profile) { setProfile(m.profile); setEmptyFinancialFields([]); }
      else {
        setProfile((p) => ({ ...p, name: m.user?.name || p.name, income: 0, savings: 0, budget: 0 }));
        setEmptyFinancialFields(["income", "savings", "budget"]);
      }
      let nextPath = m.profile ? "/explorar" : "/registro";
      let message =
        path === "/registro"
          ? "Tu cuenta está lista. Completa tu perfil."
          : "Bienvenido de vuelta.";
      if (pendingFavorite) {
        // Continue the requested save without toggling an existing favorite off.
        nextPath = pendingFavorite.returnPath;
        try {
          if (!m.favorites.includes(pendingFavorite.id)) {
            const saved = await api<{ favorites: string[] }>("/api/favorites", {
              method: "POST",
              body: JSON.stringify({ id: pendingFavorite.id }),
            });
            setMe({ ...m, favorites: saved.favorites });
            trackInteraction("favorite", { listingId: pendingFavorite.id });
          }
          message =
            "Sesión iniciada. La vivienda que elegiste está en tus guardados.";
        } catch (cause) {
          nextPath = `/inmueble/${pendingFavorite.id}`;
          message = `Tu sesión está abierta, pero no se pudo guardar la vivienda: ${(cause as Error).message}`;
        }
      }
      setPendingFavorite(null);
      go(nextPath);
      setToast(message);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };
  const logout = async () => {
    setBusy(true);
    try {
      await api("/api/auth/logout", { method: "POST" });
      setMe({ user: null, profile: null, favorites: [] });
      setSaved([]);
      setCompare([]);
      setAuthPassword("");
      setAuthEmail("");
      setAuthName("");
      setAuthConfirm("");
      setEmptyFinancialFields([]);
      reset();
      go("/");
      setToast("Sesión cerrada.");
    } catch (e) {
      setToast((e as Error).message);
    } finally {
      setBusy(false);
    }
  };
  const weightsUI = () => (
    <div className="weights">
      {(
        [
          {
            key: "price",
            title: "Oportunidad de precio",
            text: "Precio frente a la referencia del modelo",
            icon: <Scale size={17} />,
          },
          {
            key: "safety",
            title: "Seguridad",
            text: "Indicador de denuncias a nivel distrital",
            icon: <ShieldCheck size={17} />,
          },
          {
            key: "convenience",
            title: "Colegios y servicios",
            text: "Oferta de servicios del distrito",
            icon: <Trees size={17} />,
          },
        ] as const
      ).map((w) => (
        <label className="weight-row" key={w.key}>
          <span className="weight-heading">
            {w.icon}
            <strong>{w.title}</strong>
            <b>{Math.round(profile.weights[w.key] * 100)}</b>
          </span>
          <span className="weight-description">{w.text}</span>
          <input
            type="range"
            min="0"
            max="100"
            step="5"
            value={Math.round(profile.weights[w.key] * 100)}
            onChange={(e) => {
              setProfile((p) => ({
                ...p,
                weights: {
                  ...p.weights,
                  [w.key]: Number(e.target.value) / 100,
                },
              }));
              setPage(0);
            }}
            aria-label={`Prioridad de ${w.title}`}
          />
          <span className="range-labels">
            <span>Menos importante</span>
            <span>Más importante</span>
          </span>
        </label>
      ))}
    </div>
  );
  const card = (item: CatalogListing | RankedListing) => {
    const ranked = item as RankedListing;
    const selected = compare.some((x) => x.id === item.id);
    return (
      <article className="property-card" key={item.id}>
        <div className="property-image">
          <Link href={`/inmueble/${item.id}`} className="photo-link">
            <Image
              src={photo(item.id)}
              {...photoDimensions(item.id)}
              sizes="(max-width: 760px) 100vw, (max-width: 1000px) 65vw, 32vw"
              alt="Interior de vivienda, fotografía referencial"
              loading="lazy"
            />
          </Link>
          <span className="image-caption">Imagen ilustrativa · no corresponde al aviso</span>
          {typeof ranked.score === "number" && (
            <span className="match-badge">
              <Sparkles size={12} />
              {ranked.score}% de afinidad
            </span>
          )}
          <button
            className={`heart-button ${me.favorites.includes(item.id) ? "hearted" : ""}`}
            onClick={() => toggleFavorite(item.id)}
            disabled={savingId === item.id}
            aria-label={`${me.favorites.includes(item.id) ? "Quitar de guardados" : "Guardar vivienda"}: ${item.address || item.district}`}
            aria-pressed={me.favorites.includes(item.id)}
          >
            <Heart
              size={19}
              fill={me.favorites.includes(item.id) ? "currentColor" : "none"}
            />
          </button>
        </div>
        <div className="property-body">
          <div className="property-location">
            <MapPin size={13} />
            {item.district}
            <span>VENTA</span>
          </div>
          <Link href={`/inmueble/${item.id}`} className="property-title">
            {item.address || `Vivienda en ${item.district}`}
          </Link>
          <div className="property-specs">
            <span>
              <BedDouble size={15} />
              {item.rooms} dorm.
            </span>
            <span>
              <Bath size={15} />
              {item.bathrooms} baños
            </span>
            <span>{item.area} m²</span>
          </div>
          <div className="property-price">
            {soles(item.price)}
            <span>{pricePerSquareMeter(item)}</span>
          </div>
          <div className="property-reference">
            <span>Referencia del modelo</span>
            <strong>{modelReference(item)}</strong>
          </div>
          {typeof ranked.score === "number" && (
            <div className="match-reason">
              <span className="match-reason-title">Por qué aparece en tu búsqueda</span>
              <ul>
                {(ranked.reasons?.slice(0, 3) || ["Coincide con tus filtros"]).map((reason) => (
                  <li key={reason}><Check size={14} aria-hidden="true" />{reason}</li>
                ))}
              </ul>
            </div>
          )}
          <div className="card-foot">
            <button
              className={`compare-select ${selected ? "selected" : ""}`}
              onClick={() => toggleCompare(item)}
              aria-pressed={selected}
              aria-label={`${selected ? "Quitar de comparación" : "Comparar"}: ${item.address || item.district}`}
            >
              <span className="checkbox-icon" aria-hidden="true">
                {selected && <Check size={10} />}
              </span>
              Comparar
            </button>
            <Link href={`/inmueble/${item.id}`}>
              Ver detalle <ArrowUpRight size={14} />
            </Link>
          </div>
        </div>
      </article>
    );
  };
  const reset = () => {
    setProfile({ ...DEFAULT, weights: { ...DEFAULT.weights } });
    setEmptyFinancialFields([]);
    setOnlyLocated(false);
    setView("grid");
    setPage(0);
    setSort("match");
  };
  const currentMapListing =
    result?.listings.find((item) => item.id === mapListing?.id) ||
    result?.listings[0];
  const completeBudget = emptyFinancialFields.length === 0 && [profile.income, profile.savings, profile.budget].every(value => Number.isFinite(value) && value >= 0);
  const profileCap = completeBudget ? affordableCap(profile) : null;
  const profileBudget = profileCap === null ? null : Math.min(profile.budget, profileCap);
  const districtNeedle = districtQuery.trim().normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  const visibleDistricts = districts.filter(district => district.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().includes(districtNeedle));
  const confirmMismatch = confirmTouched && authConfirm.length > 0 && authConfirm !== authPassword;
  return (
    <div className="site-shell">
      <a href="#main" className="skip-link">
        Saltar al contenido
      </a>
      <header className="header">
        <div className="header-inner">
          <Link href={me.user ? (me.profile ? "/explorar" : "/registro") : "/"} className="brand">
            <Image src="/logo.png" alt="InmoScore Logo" width={1254} height={1254} sizes="(max-width: 760px) 64px, 75px" className="brand-logo" />
            Inmo<span className="brand-light">Score</span>
            <span className="brand-dot"></span>
          </Link>
          <nav
            ref={navigation}
            id="main-navigation"
            className={menu ? "nav nav-open" : "nav"}
            aria-label="Navegación principal"
          >
            <Link
              href="/explorar"
              className={path === "/explorar" ? "active" : ""}
            >
              Explorar viviendas
            </Link>
            {!me.user && <Link href="/#como-funciona">Cómo funciona</Link>}
            <Link
              href="/guardados"
              className={path === "/guardados" ? "active" : ""}
            >
              Guardados
              {me.favorites.length > 0 && (
                <span className="nav-count">{me.favorites.length}</span>
              )}
            </Link>
            <NextLink href="/tablero" prefetch={false}>Tablero</NextLink>
            <div className="nav-account-links">
              {me.user ? (
                <>
                  <Link href="/cuenta">Mi cuenta</Link>
                  <Link href="/perfil">Mi perfil</Link>
                </>
              ) : (
                <>
                  <Link href="/ingresar">Ingresar</Link>
                  <Link href="/registro">Crear cuenta</Link>
                </>
              )}
            </div>
          </nav>
          <div className="header-actions">
            {me.user ? (
              <>
                <Link href="/cuenta" className="account-pill">
                  <span className="avatar">
                    {me.user.name.slice(0, 1).toUpperCase()}
                  </span>
                  {me.user.name.split(" ")[0]}
                  <ChevronDown size={14} />
                </Link>
                <Link
                  href="/perfil"
                  className="button button-dark button-small"
                >
                  Mi perfil <SlidersHorizontal size={14} />
                </Link>
              </>
            ) : (
              <>
                <Link href="/ingresar" className="login-link">
                  Ingresar
                </Link>
                <Link
                  href="/registro"
                  className="button button-dark button-small"
                >
                  Crear mi perfil <ArrowUpRight size={15} />
                </Link>
              </>
            )}
            <button
              ref={menuToggle}
              className="mobile-menu icon-button"
              aria-label={menu ? "Cerrar navegación" : "Abrir navegación"}
              aria-expanded={menu}
              aria-controls="main-navigation"
              onClick={() => setMenu(!menu)}
            >
              {menu ? <X /> : <Menu />}
            </button>
          </div>
        </div>
      </header>
      <main id="main" key={path} className="route-enter" tabIndex={-1}>
        {path === "/" && !sessionLoaded && <div className="wrap initial-loading" role="status"><LoaderCircle className="spin" size={20} /> Preparando tu espacio de búsqueda…</div>}
        {districtsError && (
          <div className="wrap"><div className="district-load-warning" role="status">
            No se pudieron cargar los distritos. Puedes explorar todos mientras reintentamos.
            <button type="button" disabled={districtsBusy} onClick={reloadDistricts}>{districtsBusy ? "Cargando…" : "Cargar distritos"}</button>
          </div></div>
        )}
        {path === "/" && sessionLoaded && !me.user && (
          <>
            <section className="hero wrap">
              <div className="hero-copy">
                <h1>
                  Encuentra un lugar<br />
                  <em>para llamar hogar.</em>
                </h1>
                <p className="hero-sub">
                  Busca, compara y descubre viviendas en Lima que se ajusten a lo que buscas.
                </p>
                <div className="hero-actions">
                  <Link
                    href="/explorar"
                    className="button button-dark button-large"
                  >
                    Explorar viviendas <ArrowUpRight size={19} />
                  </Link>
                </div>
              </div>
              <div className="hero-visual">
                <Image
                  src="/imagenes/hero-lima-parque-edificios.jpg"
                  width={1600}
                  height={902}
                  sizes="100vw"
                  preload
                  className="hero-photo"
                  alt="Edificios residenciales y un parque urbano de Lima"
                />
                <div className="hero-photo-shade" />
                <span className="hero-image-note">Foto de contexto, no de un aviso · <a href="https://commons.wikimedia.org/wiki/File:Buildings_and_parks_in_Lima,_Peru_-_skyline.jpg" target="_blank" rel="noopener noreferrer">Tremoro0</a> · <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank" rel="noopener noreferrer">CC BY-SA 3.0</a></span>
              </div>
            </section>
            <section className="search-section wrap">
              <form
                className="quick-search"
                onSubmit={(e) => {
                  e.preventDefault();
                  go("/explorar");
                }}
              >
                <label>
                  <span>
                    <MapPin size={15} />
                    ¿Dónde te gustaría vivir?
                  </span>
                  <select
                    aria-label="Distrito para explorar"
                    value={profile.districts[0] || ""}
                    onChange={(e) =>
                      change(
                        "districts",
                        e.target.value ? [e.target.value] : [],
                      )
                    }
                  >
                    <option value="">Todos los distritos de Lima</option>
                    {districts.map((d) => (
                      <option key={d}>{d}</option>
                    ))}
                  </select>
                </label>
                <label>
                  <span>
                    <BedDouble size={15} />
                    Dormitorios
                  </span>
                  <select
                    value={profile.minRooms}
                    onChange={(e) => change("minRooms", Number(e.target.value))}
                  >
                    {[1, 2, 3, 4].map((n) => (
                      <option key={n} value={n}>
                        {n} o más dormitorios
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  <span>
                    <Scale size={15} />
                    Tu presupuesto
                  </span>
                  <select
                    value={profile.budget}
                    onChange={(e) => change("budget", Number(e.target.value))}
                  >
                    {[300000, 400000, 500000, 700000, 1000000, 2000000].map(
                      (n) => (
                        <option key={n} value={n}>
                          Hasta {soles(n)}
                        </option>
                      ),
                    )}
                  </select>
                </label>
                <button className="button button-dark" type="submit">
                  <Search size={18} />
                  Explorar viviendas
                </button>
              </form>
              <p className="landing-notice">El catálogo incluye avisos históricos. Confirma la disponibilidad con el anunciante.</p>
            </section>
            <section id="como-funciona" className="landing-discover wrap">
              <div className="landing-discover-image">
                <Image src="/imagenes/lima-interior-dia.webp" width={1672} height={941} sizes="(max-width: 760px) 100vw, 50vw" alt="Interior ilustrativo de una vivienda" loading="lazy" />
                <span>Imagen ilustrativa</span>
              </div>
              <div className="landing-discover-copy">
                <span className="landing-discover-label">UNA BÚSQUEDA MÁS CLARA</span>
                <h2>Encuentra más que una dirección.</h2>
                <p>Tu próximo hogar es una decisión importante. Encuentra opciones que encajen contigo y compáralas con información a la vista.</p>
                <div className="landing-benefits">
                  <div><span><SlidersHorizontal size={20} /></span><div><h3>Busca a tu manera</h3><p>Elige tus distritos, presupuesto y espacio ideal.</p></div></div>
                  <div><span><Scale size={20} /></span><div><h3>Compara con confianza</h3><p>Revisa precios, características e indicadores del entorno.</p></div></div>
                  <div><span><Heart size={20} /></span><div><h3>Guarda tus favoritos</h3><p>Ten tus opciones a mano para volver a ellas cuando quieras.</p></div></div>
                </div>
                <Link href="/explorar" className="text-link">Explorar viviendas <ArrowRight size={17} /></Link>
              </div>
            </section>
            <PriorityGraphic weights={profile.weights} />
            <section className="visual-diptych wrap" aria-label="Explora la búsqueda a tu manera">
              <figure className="visual-tile visual-tile-city">
                <Image src="/imagenes/miraflores-apartamentos.jpg" fill sizes="(max-width: 760px) 100vw, 50vw" alt="Edificios residenciales frente al acantilado de Miraflores, Lima" loading="lazy" />
                <figcaption>
                  <span>EXPLORA</span>
                  <strong>Compara lugares con calma.</strong>
                  <small>Fotografía del distrito. No corresponde a un aviso del catálogo.</small>
                  <Link href="/explorar" className="visual-tile-link">Ver viviendas <ArrowRight size={16} /></Link>
                  <small className="visual-credit">Foto: <a href="https://commons.wikimedia.org/wiki/File:Lima,_Peru_Miraflores_Apartments.jpg" target="_blank" rel="noopener noreferrer">Christian Córdova</a> · <a href="https://creativecommons.org/licenses/by/2.0/" target="_blank" rel="noopener noreferrer">CC BY 2.0</a></small>
                </figcaption>
              </figure>
              <figure className="visual-tile visual-tile-home">
                <Image src="/imagenes/san-borja-sur.jpg" fill sizes="(max-width: 760px) 100vw, 50vw" alt="Bulevar arbolado de la avenida San Borja Sur en Lima" loading="lazy" />
                <figcaption>
                  <span>PERSONALIZA</span>
                  <strong>Haz que la búsqueda parta de ti.</strong>
                  <small>Elige presupuesto, espacio y distritos antes de comparar.</small>
                  <Link href="/perfil" className="visual-tile-link">Crear mi búsqueda <ArrowRight size={16} /></Link>
                  <small className="visual-credit">Foto: <a href="https://commons.wikimedia.org/wiki/File:Avenida_San_Borja_Sur,_Lima,_2023.jpg" target="_blank" rel="noopener noreferrer">Daniell Veramendi</a> · <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener noreferrer">CC BY 4.0</a></small>
                </figcaption>
              </figure>
            </section>
            <CityPhotoGallery />
            <section className="closing wrap">
              <h2>
                Hay muchas viviendas.
                <br />
                Encuentra la que tiene sentido para ti.
              </h2>
              <Link
                href="/registro"
                className="button button-dark button-large"
              >
                Crear mi perfil <ArrowUpRight size={18} />
              </Link>
            </section>
          </>
        )}
        {((path === "/ingresar" && !me.user) ||
          (path === "/registro" && !me.user)) && (
          <section className="auth-layout wrap">
            <div className="auth-panel">
              <span className="eyebrow">
                {path === "/registro"
                  ? "TU BÚSQUEDA, A TU MANERA"
                  : "QUÉ BUENO TENERTE DE VUELTA"}
              </span>
              <h1>
                {path === "/registro" ? (
                  <>
                    Crea tu cuenta.
                    <br />
                    Encuentra tu hogar.
                  </>
                ) : (
                  <>
                    Continúa donde
                    <br />
                    lo dejaste.
                  </>
                )}
              </h1>
              <p>
                Guarda tus viviendas favoritas y recupera tus prioridades desde
                tu cuenta.
              </p>
              <form className="auth-form" onSubmit={submitAuth} aria-busy={busy}>
                {path === "/registro" && (
                  <label className="field">
                    Tu nombre
                    <input
                      required
                      autoComplete="name"
                      name="name"
                      maxLength={120}
                      value={authName}
                      onChange={(e) => setAuthName(e.target.value)}
                    />
                  </label>
                )}
                <label className="field">
                  Correo electrónico
                  <input
                    required
                    type="email"
                    name="email"
                    inputMode="email"
                    autoCapitalize="none"
                    spellCheck={false}
                    autoComplete="email"
                    maxLength={254}
                    value={authEmail}
                    onChange={(e) => setAuthEmail(e.target.value)}
                  />
                </label>
                <div className="field">
                  <label htmlFor="auth-password">Contraseña</label>
                  <div className="password-field">
                  <input
                    id="auth-password"
                    required
                    name="password"
                    type={showPassword ? "text" : "password"}
                    autoComplete={
                      path === "/registro" ? "new-password" : "current-password"
                    }
                    minLength={10}
                    maxLength={128}
                    aria-describedby="password-help"
                    value={authPassword}
                    onChange={(e) => setAuthPassword(e.target.value)}
                  />
                  <button type="button" className="password-toggle" onClick={() => setShowPassword(value => !value)} aria-label={showPassword ? "Ocultar contraseñas" : "Mostrar contraseñas"} aria-pressed={showPassword}>{showPassword ? <EyeOff size={19} /> : <Eye size={19} />}</button>
                  </div>
                  <span id="password-help" className="small muted">
                    {path === "/registro"
                      ? "Entre 10 y 128 caracteres. Puedes usar una frase larga."
                      : "La contraseña que elegiste al crear tu cuenta."}
                  </span>
                </div>
                {path === "/registro" && (
                  <div className="field">
                    <label htmlFor="auth-password-confirmation">Confirmar contraseña</label>
                    <input
                      id="auth-password-confirmation"
                      required
                      name="passwordConfirmation"
                      type={showPassword ? "text" : "password"}
                      autoComplete="new-password"
                      minLength={10}
                      maxLength={128}
                      value={authConfirm}
                      aria-invalid={confirmMismatch || undefined}
                      aria-describedby={confirmMismatch ? "confirm-password-help" : undefined}
                      onBlur={() => setConfirmTouched(true)}
                      onChange={(e) => setAuthConfirm(e.target.value)}
                    />
                    {confirmMismatch && <span id="confirm-password-help" className="field-error">Todavía no coinciden. Revisa ambas contraseñas antes de continuar.</span>}
                  </div>
                )}
                {error && (
                  <div className="error-banner" role="alert">
                    {error}
                  </div>
                )}
                <button
                  className="button button-dark button-large auth-button"
                  type="submit"
                  disabled={busy}
                >
                  {busy ? (
                    <LoaderCircle size={19} className="spin" />
                  ) : (
                    <UserRound size={19} />
                  )}{" "}
                  {busy ? (path === "/registro" ? "Creando tu cuenta…" : "Iniciando sesión…") : (path === "/registro" ? "Crear cuenta" : "Iniciar sesión")}
                  <ArrowRight size={18} />
                </button>
              </form>
              <p className="auth-switch">
                {path === "/registro"
                  ? "¿Ya tienes una cuenta?"
                  : "¿Primera vez por aquí?"}{" "}
                <Link
                  href={path === "/registro" ? "/ingresar" : "/registro"}
                  className="text-link"
                >
                  {path === "/registro" ? "Inicia sesión" : "Crea tu cuenta"}
                </Link>
              </p>
              <div className="auth-benefits">
                <span>
                  <CheckCircle2 size={18} />
                  Tu perfil y tus favoritos, en un solo lugar
                </span>
                <span>
                  <ShieldCheck size={18} />
                  Tú controlas los datos de tu cuenta
                </span>
              </div>
              <Link href="/explorar" className="text-link">
                Explorar como visitante <ArrowRight size={16} />
              </Link>
            </div>
            <div className="auth-photo">
              <Image
                src="/interior-3.jpg"
                width={900}
                height={600}
                sizes="(max-width: 760px) 100vw, 50vw"
                alt="Espacio interior, imagen referencial"
              />
              <div>
                <span className="eyebrow">MÁS QUE METROS CUADRADOS</span>
                <h2>
                  Un lugar para
                  <br />
                  lo que viene.
                </h2>
                <p>Imagen referencial</p>
              </div>
            </div>
          </section>
        )}
        {path === "/ingresar" && me.user && (
          <section className="empty-state wrap">
            <UserRound size={36} />
            <h1>Ya tienes una sesión abierta.</h1>
            <p>{me.user.name}</p>
            <Link href="/cuenta" className="button button-dark">
              Ir a mi cuenta <ArrowRight size={18} />
            </Link>
          </section>
        )}
        {(path === "/perfil" || (path === "/registro" && me.user)) && (
          <section className="profile-page wrap">
            <div className="page-heading">
              <div>
                <span className="eyebrow">
                  {path === "/registro"
                    ? "COMPLETA TU REGISTRO"
                    : "LO IMPORTANTE EMPIEZA CONTIGO"}
                </span>
                <h1>Tu perfil de búsqueda</h1>
                <p>{me.user ? "Ajusta tus preferencias y guárdalas cuando estés listo." : "Prueba tus preferencias sin crear una cuenta. Puedes cambiarlas cuando quieras."}</p>
              </div>
              <span className="step-pill">
                Perfil <ChevronRight size={14} />
                Recomendaciones
              </span>
            </div>
            <form className="profile-layout" aria-busy={busy} onSubmit={event => {
              if (me.user) void saveProfile(event);
              else { event.preventDefault(); exploreWithProfile(); }
            }}>
              <div className="profile-main">
                <section className="form-section">
                  <div className="form-section-title">
                    <span>01</span>
                    <div>
                      <h2>Conozcámonos</h2>
                      <p>Así personalizamos tu búsqueda.</p>
                    </div>
                  </div>
                  <label className="field">
                    ¿Cómo te llamas? {!me.user && <span className="optional">Opcional si exploras sin cuenta</span>}
                    <input
                      autoComplete="given-name"
                      required={Boolean(me.user)}
                      maxLength={120}
                      value={profile.name || ""}
                      onChange={(e) => change("name", e.target.value)}
                      placeholder="Tu nombre"
                    />
                  </label>
                  {me.user && (
                    <p className="small muted">Cuenta: {me.user.email}</p>
                  )}
                </section>
                <section className="form-section">
                  <div className="form-section-title">
                    <span>02</span>
                    <div>
                      <h2>Un presupuesto que encaje contigo</h2>
                    </div>
                  </div>
                  <div className="field-grid">
                    {(
                      [
                        { key: "income", label: "Ingreso mensual neto" },
                        {
                          key: "savings",
                          label: "Ahorro para la cuota inicial",
                        },
                        { key: "budget", label: "Presupuesto máximo" },
                      ] as const
                    ).map((f) => (
                      <label key={f.key} className="field">
                        {f.label}
                        <div className="input-prefix">
                          <span>S/</span>
                          <input
                            required
                            type="number"
                            inputMode="decimal"
                            step="any"
                            min="0"
                            max="1000000000"
                            value={emptyFinancialFields.includes(f.key) ? "" : profile[f.key]}
                            onChange={(e) => {
                              setEmptyFinancialFields((fields) => e.target.value === ""
                                ? [...new Set([...fields, f.key])]
                                : fields.filter((key) => key !== f.key));
                              change(f.key, Number(e.target.value));
                            }}
                          />
                        </div>
                      </label>
                    ))}
                  </div>
                  <div className="inline-note">
                    <Info size={16} />
                    <span>
                      TEA de 9 %, plazo de 20 años, cuota de hasta 30 % del
                      ingreso e inicial mínima de 10 %. No incluye seguros ni
                      gastos.
                    </span>
                  </div>
                </section>
                <section className="form-section">
                  <div className="form-section-title">
                    <span>03</span>
                    <div>
                      <h2>El espacio que necesitas</h2>
                      <p>Requisitos mínimos para filtrar las viviendas.</p>
                    </div>
                  </div>
                  <div className="field-grid">
                    <label className="field">
                      Dormitorios
                      <select
                        value={profile.minRooms}
                        onChange={(e) =>
                          change("minRooms", Number(e.target.value))
                        }
                      >
                        {[1, 2, 3, 4, 5].map((n) => (
                          <option key={n} value={n}>
                            {n} o más
                          </option>
                        ))}
                      </select>
                    </label>
                    <label className="field">
                      Área mínima
                      <div className="input-suffix">
                        <input
                          required
                          type="number"
                          min="0"
                          max="10000"
                          value={profile.minArea}
                          onChange={(e) =>
                            change("minArea", Number(e.target.value))
                          }
                        />
                        <span>m²</span>
                      </div>
                    </label>
                  </div>
                  <label className="field">
                    Distritos de interés
                    <span className="optional">
                      Opcional · sin selección se incluyen todos
                    </span>
                  </label>
                  <div className="field district-search">
                    <label htmlFor="district-query">Buscar un distrito</label>
                    <div className="district-search-input"><Search size={17} aria-hidden="true" /><input ref={districtInput} id="district-query" type="search" value={districtQuery} onChange={event => setDistrictQuery(event.target.value)} placeholder="Por ejemplo, San Miguel" autoComplete="off" aria-describedby="district-search-count" />{districtQuery && <button type="button" onClick={() => { setDistrictQuery(""); districtInput.current?.focus(); }} aria-label="Borrar búsqueda de distrito"><X size={17} /></button>}</div>
                  </div>
                  <p className="district-search-count" id="district-search-count" role="status">{visibleDistricts.length} {visibleDistricts.length === 1 ? "distrito disponible" : "distritos disponibles"} · {profile.districts.length} elegidos</p>
                  <div className="district-chips">
                    {visibleDistricts.map((d) => (
                      <button
                        type="button"
                        className={
                          profile.districts.includes(d)
                            ? "district-chip chosen"
                            : "district-chip"
                        }
                        aria-pressed={profile.districts.includes(d)}
                        key={d}
                        onClick={() =>
                          change(
                            "districts",
                            profile.districts.includes(d)
                              ? profile.districts.filter((x) => x !== d)
                              : [...profile.districts, d],
                          )
                        }
                      >
                        {profile.districts.includes(d) && <Check size={12} />}{" "}
                        {d}
                      </button>
                    ))}
                  </div>
                  {visibleDistricts.length === 0 && districts.length > 0 && <p className="small muted">No hay distritos con ese nombre. Prueba una parte del nombre; tus selecciones se conservan.</p>}
                  {districtQuery && profile.districts.some(district => !visibleDistricts.includes(district)) && <p className="small muted">También elegiste: {profile.districts.filter(district => !visibleDistricts.includes(district)).join(", ")}.</p>}
                </section>
                <section className="form-section">
                  <div className="form-section-title">
                    <span>04</span>
                    <div>
                      <h2>¿Qué pesa más para ti?</h2>
                    </div>
                  </div>
                  {weightsUI()}
                </section>
                {error && (
                  <div className="error-banner" role="alert">
                    {error}
                  </div>
                )}
                {path === "/registro" && (
                  <label className="consent">
                    <input
                      required
                      type="checkbox"
                      checked={consent}
                      onChange={(e) => setConsent(e.target.checked)}
                    />
                    <span>
                      Quiero guardar estos datos para personalizar mi búsqueda.
                      Puedo editarlos o eliminarlos desde mi cuenta.
                    </span>
                  </label>
                )}
                <div className="form-actions">
                  {me.user ? (
                    <button
                      className="button button-dark button-large"
                      disabled={busy}
                      type="submit"
                    >
                      {busy ? (
                        <LoaderCircle size={18} className="spin" />
                      ) : (
                        <Check size={18} />
                      )}
                      {busy ? "Guardando tu perfil…" : "Guardar y ver viviendas"} <ArrowRight size={17} />
                    </button>
                  ) : (
                    <>
                      <button
                        className="button button-dark button-large"
                        type="submit"
                      >
                        Ver recomendaciones <ArrowRight size={18} />
                      </button>
                      <p className="small muted">
                        Exploras como visitante.{" "}
                        <Link href="/registro">
                          Crea tu cuenta para guardar el perfil.
                        </Link>
                      </p>
                    </>
                  )}
                </div>
              </div>
              <aside className="profile-aside">
                <figure className="section-photo profile-photo">
                  <Image src="/imagenes/web-perfil.webp" fill sizes="(max-width: 760px) 100vw, 33vw" alt="Patio residencial limeño, escena ilustrativa" loading="lazy" />
                  <figcaption>Imagen ilustrativa</figcaption>
                </figure>
                <div className="profile-summary">
                  <span className="summary-symbol">
                    <House size={28} />
                  </span>
                  <span className="eyebrow">TU BÚSQUEDA VA TOMANDO FORMA</span>
                  <h2>Un hogar a tu medida.</h2>
                  <p>Presupuesto deseado <strong>{emptyFinancialFields.includes("budget") ? "Por completar" : soles(profile.budget)}</strong></p>
                  <div className="budget-preview">
                    <span>Presupuesto que aplicaría la búsqueda</span>
                    <strong>{profileBudget === null ? "Completa tus importes" : soles(profileBudget)}</strong>
                    <p>{profileCap === null ? "Ingresa tus ingresos, ahorro y presupuesto para revisar el tope." : `Tope calculado: ${soles(profileCap)}. Usamos el menor valor entre ese tope y tu presupuesto.`}</p>
                    <small>Simulación con los supuestos indicados. No representa una aprobación de crédito.</small>
                  </div>
                  <div className="summary-facts">
                    <span>
                      <BedDouble size={17} />
                      {profile.minRooms}+ dormitorios
                    </span>
                    <span>
                      <Building2 size={17} />
                      Desde {profile.minArea} m²
                    </span>
                    <span>
                      <MapPin size={17} />
                      {profile.districts.length
                        ? `${profile.districts.length} distritos elegidos`
                        : "Todos los distritos disponibles"}
                    </span>
                  </div>
                  <div className="summary-bottom">
                    <ShieldCheck size={20} />
                    <p>
                      Puedes actualizar tus preferencias cuando quieras.
                    </p>
                  </div>
                </div>
              </aside>
            </form>
          </section>
        )}
        {path === "/explorar" && (
          <section className="explore-page">
            <div className="wrap">
              <figure className="explore-banner">
                <Image src="/imagenes/magdalena-atardecer.jpg" width={1280} height={588} sizes="100vw" alt="Vista panorámica de Magdalena del Mar al atardecer" loading="eager" />
                <figcaption>Magdalena del Mar · foto: <a href="https://commons.wikimedia.org/wiki/File:Atardecer_en_Magdalena_del_Mar_%28Lima%2C_Per%C3%BA%29.jpg" target="_blank" rel="noopener noreferrer">Miguel A. Vera León</a> · <a href="https://creativecommons.org/licenses/by/2.0/" target="_blank" rel="noopener noreferrer">CC BY 2.0</a> · no corresponde a un aviso</figcaption>
              </figure>
              <div className="page-heading">
                <div>
                  <span className="eyebrow">EXPLORAR EL CATÁLOGO</span>
                  <h1>
                    Viviendas en Lima
                    <span className="heading-dot">.</span>
                  </h1>
                  <p>Filtra los avisos históricos y compara lo que muestran los datos disponibles.</p>
                </div>
                <Link href="/perfil" className="button button-white">
                  <SlidersHorizontal size={16} />
                  Editar mi perfil
                </Link>
              </div>
              <div className="explore-layout">
                <aside
                  ref={filterPanel}
                  id="search-filters"
                  className={`filter-panel ${filters ? "filter-panel-open" : ""}`}
                  role={filters ? "dialog" : undefined}
                  aria-modal={filters || undefined}
                  aria-label="Filtros de búsqueda"
                  tabIndex={filters ? -1 : undefined}
                >
                  <div className="filter-title">
                    <strong>
                      <SlidersHorizontal size={17} />
                      Tu búsqueda
                    </strong>
                    <div className="filter-title-actions">
                      <button className="text-button" onClick={reset}>
                        Restablecer
                      </button>
                      <button
                        className="icon-button mobile-filter-dismiss"
                        onClick={() => setFilters(false)}
                        aria-label="Cerrar filtros"
                      >
                        <X size={22} />
                      </button>
                    </div>
                  </div>
                  <label className="field">
                    Presupuesto máximo
                    <strong className="budget-display">
                      {soles(profile.budget)}
                    </strong>
                    <input
                      type="range"
                      min="0"
                      max={Math.max(2000000, profile.budget)}
                      step="10000"
                      value={profile.budget}
                      onChange={(e) => change("budget", Number(e.target.value))}
                    />
                    <span className="range-labels">
                      <span>S/ 0</span>
                      <span>{soles(Math.max(2000000, profile.budget))}</span>
                    </span>
                  </label>
                  {result && (
                    <div className="affordable">
                      <span>Tope estimado por ingreso y ahorro</span>
                      <strong>{soles(result.cap)}</strong>
                      <p>
                        La búsqueda usa el menor valor entre tu presupuesto y
                        este tope: <b>{soles(result.effectiveBudget)}</b>.
                      </p>
                      <Link href="/perfil">
                        Ajustar situación financiera <ArrowUpRight size={12} />
                      </Link>
                    </div>
                  )}
                  <label className="field">
                    Distrito
                    <select
                      value={
                        profile.districts.length === 1
                          ? profile.districts[0]
                          : ""
                      }
                      onChange={(e) =>
                        change(
                          "districts",
                          e.target.value ? [e.target.value] : [],
                        )
                      }
                    >
                      <option value="">
                        {profile.districts.length > 1
                          ? `${profile.districts.length} elegidos en mi perfil`
                          : "Todos los distritos"}
                      </option>
                      {districts.map((d) => (
                        <option key={d}>{d}</option>
                      ))}
                    </select>
                  </label>
                  <fieldset className="field bedroom-filter">
                    <legend>Dormitorios mínimos</legend>
                    <div className="room-buttons">
                      {[1, 2, 3, 4].map((n) => (
                        <button
                          type="button"
                          className={profile.minRooms === n ? "selected" : ""}
                          aria-pressed={profile.minRooms === n}
                          aria-label={`${n} o más dormitorios`}
                          key={n}
                          onClick={() => change("minRooms", n)}
                        >
                          {n}+
                        </button>
                      ))}
                    </div>
                  </fieldset>
                  <label className="field">
                    Área mínima
                    <div className="input-suffix">
                      <input
                        type="number"
                        min="0"
                        max="10000"
                        value={profile.minArea}
                        onChange={(e) =>
                          change("minArea", Number(e.target.value))
                        }
                      />
                      <span>m²</span>
                    </div>
                  </label>
                  <div className="filter-divider" />
                  <h3 className="filter-subtitle">Tus prioridades</h3>
                  <p className="small muted">
                    Mueve los controles y compara el resultado.
                  </p>
                  {weightsUI()}
                  <label className="located-filter">
                    <input
                      type="checkbox"
                      checked={onlyLocated}
                      onChange={(e) => {
                        setOnlyLocated(e.target.checked);
                        if (!e.target.checked) setView("grid");
                        setPage(0);
                      }}
                    />
                    Solo con ubicación geocodificada
                  </label>
                  <p className="tiny muted">
                    Seguridad y conveniencia son distritales. Las coordenadas
                    son aproximadas.
                  </p>
                  <button
                    className="button button-dark mobile-filter-close"
                    onClick={() => setFilters(false)}
                  >
                    Ver resultados <Check size={16} />
                  </button>
                </aside>
                <div className="results" aria-busy={rankingBusy}>
                  <div className="results-toolbar">
                    <div role="status" aria-live="polite" aria-atomic="true">
                      <strong>
                        {rankingBusy || (!result && !error)
                          ? "Buscando…"
                          : error
                            ? "Revisa la búsqueda"
                            : `${result?.total ?? 0} opciones en la selección`}
                      </strong>
                      <span>
                        {!rankingBusy && result?.diversityLimited
                          ? `${result.matchedTotal} cumplen tus filtros. Mostramos hasta 3 por distrito para diversificar.`
                          : "Coincidencias con tus filtros"}
                      </span>
                      {!rankingBusy && result?.diversityLimited && (
                        <button
                          className="text-button all-matches"
                          onClick={() => {
                            setSort("price_asc");
                            setPage(0);
                          }}
                        >
                          Ver todas por menor precio
                        </button>
                      )}
                    </div>
                    <div className="toolbar-controls">
                      <button
                        className="button button-white mobile-filters"
                        aria-expanded={filters}
                        aria-controls="search-filters"
                        onClick={() => setFilters(!filters)}
                      >
                        <SlidersHorizontal size={15} />
                        Filtros
                      </button>
                      <label className="sort-label">
                        <span className="sr-only">Ordenar viviendas</span>
                        <select
                          value={sort}
                          onChange={(e) => {
                            setSort(e.target.value);
                            setPage(0);
                          }}
                        >
                          <option value="match">Mayor afinidad</option>
                          <option value="price_asc">Menor precio</option>
                          <option value="price_desc">Mayor precio</option>
                        </select>
                      </label>
                      <div className="view-switch">
                        <button
                          className={view === "grid" ? "selected" : ""}
                          aria-label="Ver tarjetas"
                          aria-pressed={view === "grid"}
                          onClick={() => setView("grid")}
                        >
                          <LayoutGrid size={17} />
                        </button>
                        <button
                          className={view === "map" ? "selected" : ""}
                          aria-label="Ver mapa"
                          aria-pressed={view === "map"}
                          onClick={() => {
                            setView("map");
                            setOnlyLocated(true);
                            setPage(0);
                          }}
                        >
                          <MapPin size={17} />
                        </button>
                      </div>
                    </div>
                  </div>
                  <div
                    className="active-filters"
                    aria-label="Filtros aplicados"
                  >
                    <strong>Tu búsqueda:</strong>
                    <span>Hasta {soles(profile.budget)}</span>
                    <span>{profile.minRooms}+ dormitorios</span>
                    <span>Desde {profile.minArea} m²</span>
                    {profile.districts.length === 0 ? (
                      <span>Todos los distritos</span>
                    ) : (
                      profile.districts.map((district) => (
                        <button
                          key={district}
                          onClick={() =>
                            change(
                              "districts",
                              profile.districts.filter(
                                (value) => value !== district,
                              ),
                            )
                          }
                          aria-label={`Quitar filtro de ${district}`}
                        >
                          {district}
                          <X size={13} aria-hidden="true" />
                        </button>
                      ))
                    )}
                    {onlyLocated && (
                      <button
                        onClick={() => {
                          setOnlyLocated(false);
                          setView("grid");
                          setPage(0);
                        }}
                        aria-label="Quitar filtro de ubicación y volver a tarjetas"
                      >
                        Con ubicación
                        <X size={13} aria-hidden="true" />
                      </button>
                    )}
                  </div>
                  {view === "map" && (
                    <p className="map-scope-note">
                      El mapa incluye solo avisos con coordenadas. Quita el
                      filtro «Con ubicación» para volver a ver también los demás
                      avisos.
                    </p>
                  )}
                  {error && (
                    <div className="error-banner" role="alert">
                      {error}
                      <button onClick={loadRanking}>Reintentar</button>
                    </div>
                  )}
                  {rankingBusy && !result && (
                    <div className="loading-state">
                      <LoaderCircle className="spin" />
                      Buscando viviendas para ti…
                    </div>
                  )}
                  {result && result.total > 0 && view === "grid" && (
                    <div
                      className={`property-grid ${rankingBusy ? "updating" : ""}`}
                    >
                      {result.listings.map(card)}
                    </div>
                  )}
                  {result && result.total > 0 && view === "map" && (
                    <div className="map-layout">
                      <div className="map-list">
                        {result.listings.map((item) => (
                          <button
                            key={item.id}
                            className={
                              currentMapListing?.id === item.id
                                ? "map-list-row selected"
                                : "map-list-row"
                            }
                            aria-pressed={currentMapListing?.id === item.id}
                            onClick={() => setMapListing(item)}
                          >
                            <MapPin size={18} />
                            <span>
                              <strong>{soles(item.price)}</strong>
                              <small>
                                {item.district} · {item.area} m²
                              </small>
                            </span>
                            <ChevronRight size={16} />
                          </button>
                        ))}
                      </div>
                      {currentMapListing && (
                        <div className="map-selection-panel">
                          <MapPanel item={currentMapListing} />
                          <Link
                            href={`/inmueble/${currentMapListing.id}`}
                            className="button button-white map-detail-link"
                          >
                            Ver detalle de esta vivienda{" "}
                            <ArrowUpRight size={16} />
                          </Link>
                        </div>
                      )}
                    </div>
                  )}
                  {!rankingBusy && result?.total === 0 && (
                    <div className="empty-state search-empty">
                      <span className="search-empty-icon"><Search size={27} /></span>
                      <h2>No encontramos viviendas con estos filtros.</h2>
                      <p>Revisa primero el tope aplicado y luego los requisitos que podrías flexibilizar.</p>
                      <p className="empty-budget">Presupuesto aplicado: <strong>{soles(result.effectiveBudget)}</strong>. El presupuesto deseado puede ser mayor que el tope calculado con tus ingresos y ahorro.</p>
                      <div className="search-empty-actions">
                        {profile.districts.length > 0 && (
                          <button className="button button-white" onClick={() => change("districts", [])}>
                            Ver todos los distritos
                          </button>
                        )}
                        {profile.minRooms > 1 && (
                          <button className="button button-white" onClick={() => change("minRooms", profile.minRooms - 1)}>
                            Reducir dormitorios a {profile.minRooms - 1}+
                          </button>
                        )}
                        {onlyLocated && (
                          <button className="button button-white" onClick={() => { setOnlyLocated(false); setView("grid"); setPage(0); }}>
                            Incluir viviendas sin ubicación
                          </button>
                        )}
                        <Link href="/perfil" className="button button-dark">Revisar mi presupuesto <ArrowRight size={16} /></Link>
                        <button className="button button-white" onClick={() => window.dispatchEvent(new CustomEvent("inmoscore:open-help", { detail: "no_results" }))}>Entender este resultado</button>
                      </div>
                    </div>
                  )}
                  {result && result.total > 12 && (
                    <div className="pagination">
                      <button
                        disabled={page === 0 || rankingBusy}
                        onClick={() => {
                          setPage((p) => p - 1);
                          window.scrollTo(0, 240);
                        }}
                      >
                        <ArrowLeft size={15} />
                        Anterior
                      </button>
                      <span>
                        Página {page + 1} de {Math.ceil(result.total / 12)}
                      </span>
                      <button
                        disabled={
                          (page + 1) * 12 >= result.total || rankingBusy
                        }
                        onClick={() => {
                          setPage((p) => p + 1);
                          window.scrollTo(0, 240);
                        }}
                      >
                        Siguiente
                        <ArrowRight size={15} />
                      </button>
                    </div>
                  )}
                  <div className="result-note">
                    <Info size={15} />
                    <span>
                      La afinidad resume tus prioridades; no es una probabilidad
                      de satisfacción ni garantía de precio. Fotografías
                      referenciales.
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </section>
        )}
        {path.startsWith("/inmueble/") && (
          <section className="detail-page wrap">
            <Link href="/explorar" className="back-link">
              <ArrowLeft size={15} />
              Volver a la búsqueda
            </Link>
            {busy && (
              <div className="loading-state">
                <LoaderCircle className="spin" />
                Cargando vivienda…
              </div>
            )}
            {error && (
              <div className="empty-state">
                <h1>No pudimos encontrar este aviso</h1>
                <p>{error}</p>
                <Link href="/explorar" className="button button-dark">
                  Explorar viviendas
                </Link>
              </div>
            )}
            {detail && (
              <>
                <div className="detail-heading">
                  <div>
                    <div className="property-location">
                      <MapPin size={15} />
                      {detail.district} · Lima
                    </div>
                    <h1>
                      {detail.address || `Vivienda en ${detail.district}`}
                    </h1>
                    <p>Referencia del catálogo · ID {detail.id}</p>
                  </div>
                  <button
                    className="button button-white"
                    onClick={() => toggleFavorite(detail.id)}
                  >
                    <Heart
                      size={17}
                      fill={
                        me.favorites.includes(detail.id)
                          ? "currentColor"
                          : "none"
                      }
                    />
                    {me.favorites.includes(detail.id) ? "Guardado" : "Guardar"}
                  </button>
                </div>
                <div className="detail-gallery">
                  <Image
                    src={photo(detail.id)}
                    {...photoDimensions(detail.id)}
                    sizes="(max-width: 760px) 100vw, 65vw"
                    alt="Interior ilustrativo, no corresponde al anuncio"
                  />
                  <div>
                    <Image src="/interior-2.jpg" width={900} height={600} sizes="(max-width: 760px) 50vw, 35vw" alt="Fotografía referencial" />
                    <Image src="/interior-3.jpg" width={900} height={600} sizes="(max-width: 760px) 50vw, 35vw" alt="Fotografía referencial" />
                  </div>
                  <span>
                    Fotografías referenciales · no son imágenes del inmueble
                  </span>
                </div>
                <div className="detail-layout">
                  <div>
                    <div className="detail-specs">
                      <span>
                        <BedDouble size={23} />
                        <strong>{detail.rooms}</strong>Dormitorios
                      </span>
                      <span>
                        <Bath size={23} />
                        <strong>{detail.bathrooms}</strong>Baños
                      </span>
                      <span>
                        <Building2 size={23} />
                        <strong>{detail.area} m²</strong>Área total
                      </span>
                      <span>
                        <CarFront size={23} />
                        <strong>{detail.parking ?? "—"}</strong>Cocheras
                      </span>
                    </div>
                    <section className="detail-section">
                      <h2>Una referencia para comparar</h2>
                      <p>
                        El modelo estima un precio de oferta con atributos del
                        aviso y su distrito. Una diferencia no confirma una
                        oportunidad de compra.
                      </p>
                      <div className="valuation">
                        <div>
                          <span>Precio del aviso</span>
                          <strong>{soles(detail.price)}</strong>
                        </div>
                        <div>
                          <span>Referencia del modelo</span>
                          <strong>{modelReference(detail)}</strong>
                        </div>
                      </div>
                      {needsInputReview(detail) && (
                        <div className="inline-note" role="note">
                          <Info size={16} />
                          <span>
                            {detail.flags.includes("capture_district_conflict")
                              ? "El distrito histórico no coincide con el de la captura."
                              : "El área publicada queda fuera del rango observado por el modelo."}{" "}
                            Conservamos los datos originales, pero no mostramos
                            una estimación ni un puntaje de precio hasta revisar
                            el aviso.
                          </span>
                        </div>
                      )}
                      <p className="small muted">
                        La evaluación usó 779 avisos históricos reservados para
                        prueba: error porcentual absoluto mediano de 12,2 %. No
                        mide el error de este inmueble ni valida la captura de
                        octubre; tampoco es un intervalo de confianza.
                      </p>
                    </section>
                    <section className="detail-section">
                      <h2>¿Cómo encaja con tus prioridades?</h2>
                      <p>
                        Los indicadores del entorno corresponden al distrito
                        completo.
                      </p>
                      {(
                        [
                          {
                            key: "price",
                            title: "Oportunidad de precio",
                            icon: <Scale size={19} />,
                          },
                          {
                            key: "safety",
                            title: "Seguridad distrital",
                            icon: <ShieldCheck size={19} />,
                          },
                          {
                            key: "convenience",
                            title: "Colegios y servicios",
                            icon: <Trees size={19} />,
                          },
                        ] as const
                      )
                        .filter((c) =>
                          c.key === "price"
                            ? !needsInputReview(detail)
                            : !detail.flags.includes(
                                "capture_district_conflict",
                              ),
                        )
                        .map((c) => {
                          const value = detail.scores[c.key];
                          if (value === null) return null;
                          return (
                            <div className="component-row" key={c.key}>
                              <span>
                                {c.icon}
                                {c.title}
                              </span>
                              <div>
                                <i
                                  style={{
                                    width: `${value * 100}%`,
                                  }}
                                />
                              </div>
                              <strong>{Math.round(value * 100)}/100</strong>
                            </div>
                          );
                        })}
                      {detail.flags.includes("capture_district_conflict") && (
                        <p className="inline-note">
                          Los indicadores del entorno quedan pendientes hasta
                          confirmar el distrito del aviso.
                        </p>
                      )}
                      <div className="inline-note">
                        <Info size={16} />
                        <span>
                          Denuncias por residente no equivalen a seguridad del
                          entorno inmediato. Las zonas comerciales pueden
                          registrar más denuncias por población flotante.
                        </span>
                      </div>
                    </section>
                    <section className="detail-section">
                      <h2>Información para tener en cuenta</h2>
                      <div className="facts-table">
                        <div>
                          <span>Mantenimiento declarado</span>
                          <strong>
                            {detail.maintenance === null
                              ? "No confirmado"
                              : soles(detail.maintenance)}
                          </strong>
                        </div>
                        <div>
                          <span>Disponibilidad</span>
                          <strong>No verificada</strong>
                        </div>
                        <div>
                          <span>Constructora y conservación</span>
                          <strong>Sin datos suficientes</strong>
                        </div>
                        <div>
                          <span>Origen del aviso</span>
                          <strong>
                            {detail.source === "urbania_fase1"
                              ? "Captura propia en Urbania"
                              : "Dataset público de Urbania"}
                          </strong>
                        </div>
                      </div>
                      <ul className="quality-list">
                        {detail.flags.map((f) => (
                          <li key={f}>
                            <Info size={15} />
                            {FLAGS[f] || "Dato pendiente de verificación"}
                          </li>
                        ))}
                      </ul>
                    </section>
                    <section className="detail-section">
                      <h2>Ubicación y entorno</h2>
                      {detail.location ? (
                        <MapPanel item={detail} />
                      ) : (
                        <div className="map-unavailable">
                          <MapPin size={28} />
                          <strong>{detail.district}, Lima</strong>
                          <p>
                            No hay coordenadas suficientemente precisas. No
                            mostramos un punto inventado.
                          </p>
                        </div>
                      )}
                    </section>
                  </div>
                  <aside>
                    <div className="detail-summary">
                      <span className="eyebrow">PRECIO PUBLICADO</span>
                      <h2>{soles(detail.price)}</h2>
                      <p>{pricePerSquareMeter(detail)}</p>
                      <div className="historical-badge">
                        <Info size={15} />
                        {detail.source === "urbania_fase1"
                          ? `Visto en Urbania el ${day(detail.observedAt)} · no verificado`
                          : "Aviso histórico · no verificado"}
                      </div>
                      <button
                        className="button button-dark"
                        onClick={() => toggleFavorite(detail.id)}
                      >
                        <Heart size={17} />
                        {me.favorites.includes(detail.id)
                          ? "Retirar de guardados"
                          : "Guardar esta vivienda"}
                      </button>
                      <button
                        className="button button-white"
                        onClick={() => toggleCompare(detail)}
                      >
                        <Scale size={17} />
                        {compare.some((x) => x.id === detail.id)
                          ? "Quitar de comparación"
                          : "Añadir a comparación"}
                      </button>
                      {detail.url ? (
                        <a
                          className="source-link"
                          href={detail.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          onClick={() => trackInteraction("outbound", { listingId: detail.id, district: detail.district })}
                        >
                          Consultar anuncio de origen <ArrowUpRight size={15} />
                        </a>
                      ) : (
                        <p className="small muted">
                          No contamos con un enlace de origen verificable para
                          este aviso.
                        </p>
                      )}
                      <p className="tiny muted">
                        El anuncio puede haber cambiado o estar retirado.
                        Confirma la disponibilidad con el anunciante antes de
                        tomar una decisión.
                      </p>
                    </div>
                  </aside>
                </div>
              </>
            )}
          </section>
        )}
        {path === "/guardados" && (
          <section className="saved-page wrap">
            <div className="page-heading">
              <div>
                <span className="eyebrow">
                  TUS POSIBILIDADES, EN UN MISMO LUGAR
                </span>
                <h1>
                  Los que te hicieron imaginar
                  <span className="heading-dot">.</span>
                </h1>
                <p>Vuelve a tus favoritos y compara con calma.</p>
              </div>
              <Link href="/explorar" className="button button-white">
                Seguir explorando <ArrowUpRight size={16} />
              </Link>
            </div>
            <figure className="section-photo section-photo-wide">
              <Image src="/imagenes/web-guardados.webp" fill sizes="100vw" alt="Calle residencial limeña, escena ilustrativa" loading="lazy" />
              <figcaption>Imagen ilustrativa · las fotografías de avisos son referenciales</figcaption>
            </figure>
            {!me.user ? (
              <div className="empty-state">
                <Heart size={36} />
                <h2>Dale un lugar a tus favoritos.</h2>
                <p>
                  Inicia sesión para guardarlos y encontrarlos desde tu cuenta.
                </p>
                <Link href="/ingresar" className="button button-dark">
                  Ingresar <ArrowRight size={16} />
                </Link>
              </div>
            ) : busy ? (
              <div className="loading-state">
                <LoaderCircle className="spin" />
                Recuperando tus guardados…
              </div>
            ) : saved.length ? (
              <>
                <div className="saved-count">
                  {saved.length} viviendas guardadas
                </div>
                <div className="property-grid saved-grid">
                  {saved.map(card)}
                </div>
              </>
            ) : (
              <div className="empty-state">
                <Bookmark size={36} />
                <h2>Tu próxima opción está por descubrir.</h2>
                <p>Toca el corazón de una vivienda y aparecerá aquí.</p>
                <Link href="/explorar" className="button button-dark">
                  Explorar viviendas <ArrowRight size={16} />
                </Link>
              </div>
            )}
            {error && (
              <div className="error-banner" role="alert">
                {error}
              </div>
            )}
          </section>
        )}
        {path === "/cuenta" && (
          <section className="account-page wrap">
            <span className="eyebrow">TU ESPACIO EN INMOSCORE</span>
            <h1>Mi cuenta</h1>
            <figure className="section-photo section-photo-wide account-photo">
              <Image src="/imagenes/pueblo-libre-plaza.jpg" fill sizes="100vw" alt="Plaza Bolívar de Pueblo Libre con una bandera peruana" loading="lazy" />
              <figcaption>Pueblo Libre · foto: <a href="https://commons.wikimedia.org/wiki/File:Plaza_Principal_de_Pueblo_Libre.JPG" target="_blank" rel="noopener noreferrer">Rafajs77</a> · <a href="https://commons.wikimedia.org/wiki/File:Plaza_Principal_de_Pueblo_Libre.JPG#Licensing" target="_blank" rel="noopener noreferrer">dominio público</a> · contexto, no aviso</figcaption>
            </figure>
            {me.user ? (
              <div className="account-layout">
                <div className="account-profile">
                  <span className="avatar avatar-large">
                    {me.user.name.slice(0, 1)}
                  </span>
                  <h2>{me.user.name}</h2>
                  <p>{me.user.email}</p>
                </div>
                <div className="account-options">
                  <Link href="/perfil">
                    <span>
                      <SlidersHorizontal size={21} />
                      <strong>
                        Mi perfil de búsqueda
                        <small>Actualiza presupuesto y prioridades</small>
                      </strong>
                    </span>
                    <ArrowUpRight size={18} />
                  </Link>
                  <Link href="/guardados">
                    <span>
                      <Heart size={21} />
                      <strong>
                        Mis viviendas guardadas
                        <small>
                          {me.favorites.length} opciones para seguir comparando
                        </small>
                      </strong>
                    </span>
                    <ArrowUpRight size={18} />
                  </Link>
                  <button
                    type="button"
                    className="account-logout"
                    disabled={busy}
                    onClick={logout}
                  >
                    <span>
                      <LogOut size={21} />
                      <strong>
                        Cerrar sesión
                        <small>Tu perfil seguirá guardado en InmoScore</small>
                      </strong>
                    </span>
                    <ArrowUpRight size={18} />
                  </button>
                  <button
                    className="danger-account"
                    onClick={() => setDeleteOpen(true)}
                  >
                    Eliminar mi cuenta
                  </button>
                  <p className="small muted">
                    La eliminación borra tu cuenta, perfil, sesiones y viviendas
                    guardadas de esta instalación.
                  </p>
                </div>
              </div>
            ) : (
              <div className="empty-state">
                <UserRound size={36} />
                <h2>Tu búsqueda te está esperando.</h2>
                <Link href="/ingresar" className="button button-dark">
                  Iniciar sesión <ArrowRight size={16} />
                </Link>
              </div>
            )}
          </section>
        )}
        {![
          "/",
          "/explorar",
          "/registro",
          "/ingresar",
          "/perfil",
          "/guardados",
          "/cuenta",
        ].includes(path) &&
          !path.startsWith("/inmueble/") && (
            <section className="empty-state wrap">
              <h1>Esta página no está disponible.</h1>
              <Link href="/" className="button button-dark">
                Volver al inicio
              </Link>
            </section>
          )}
      </main>
      <footer className="footer">
        <div className="wrap footer-main">
          <div className="footer-brand">
            <Link href={me.user ? (me.profile ? "/explorar" : "/registro") : "/"} className="brand">
              <Image
                src="/logo.png"
                width={1254}
                height={1254}
                sizes="90px"
                alt="InmoScore Logo"
                className="brand-logo-footer"
              />
              Inmo<span className="brand-light">Score</span>
              <span className="brand-dot"></span>
            </Link>
            <p>
              Encuentra un hogar que encaje contigo. Compara viviendas según tu
              presupuesto y lo que más te importa.
            </p>
          </div>
          <nav className="footer-links" aria-label="Explora InmoScore">
            <strong>Encuentra tu hogar</strong>
            <Link href="/explorar">Explorar viviendas</Link>
            {!me.user && <Link href="/#como-funciona">Cómo funciona</Link>}
          </nav>
          <nav className="footer-links" aria-label="Tu espacio en InmoScore">
            <strong>Tu espacio</strong>
            <Link href="/perfil">Mi perfil</Link>
            <Link href="/guardados">Viviendas guardadas</Link>
            <Link href="/cuenta">Mi cuenta</Link>
            <NextLink href="/tablero" prefetch={false}>Tablero de actividad</NextLink>
          </nav>
        </div>
        <div className="wrap footer-bottom">
          <span>© InmoScore</span>
          <span>Tu próximo hogar, con más claridad.</span>
        </div>
      </footer>
      {compare.length > 0 && (
        <div className="compare-tray">
          <span>
            <Scale size={20} />
            <strong>{compare.length} viviendas para comparar</strong>
          </span>
          <div>
            {compare.map((x) => (
              <button key={x.id} onClick={() => toggleCompare(x)}>
                {x.district}
                <X size={12} />
              </button>
            ))}
          </div>
          <button
            className="button button-dark"
            disabled={compare.length < 2}
            onClick={() => { setCompareOpen(true); trackInteraction("compare"); }}
          >
            Comparar <ArrowRight size={15} />
          </button>
          <button
            className="icon-button"
            aria-label="Vaciar comparación"
            onClick={() => setCompare([])}
          >
            <X size={18} />
          </button>
        </div>
      )}
      {compareOpen && (
        <Modal
          title="Compara tus opciones"
          close={() => setCompareOpen(false)}
          wide
        >
          <p className="comparison-intro">
            Revisa las características de cada vivienda lado a lado.
          </p>
          <p className="comparison-hint">Desliza horizontalmente para ver todas las opciones.</p>
          <div className="comparison-scroll">
            <table className="comparison-table">
              <thead>
                <tr>
                  <th>Vivienda</th>
                  {compare.map((x) => (
                    <th key={x.id}>
                      <Image src={photo(x.id)} {...photoDimensions(x.id)} sizes="(max-width: 760px) 180px, 250px" alt="Imagen referencial" />
                      <span>{x.district}</span>
                      <small>{x.address || `Vivienda en ${x.district}`}</small>
                      <button type="button" className="comparison-detail" onClick={() => { setCompareOpen(false); go(`/inmueble/${x.id}`); }}>Ver detalle <ArrowUpRight size={13} /></button>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {[
                  {
                    label: "Precio publicado",
                    fn: (x: CatalogListing) => soles(x.price),
                  },
                  {
                    label: "Referencia del modelo",
                    fn: modelReference,
                  },
                  { label: "Área", fn: (x: CatalogListing) => `${x.area} m²` },
                  {
                    label: "Dormitorios / baños",
                    fn: (x: CatalogListing) => `${x.rooms} / ${x.bathrooms}`,
                  },
                  {
                    label: "Cocheras",
                    fn: (x: CatalogListing) => String(x.parking ?? "Sin datos"),
                  },
                  {
                    label: "Mantenimiento",
                    fn: (x: CatalogListing) =>
                      x.maintenance === null
                        ? "Por confirmar"
                        : soles(x.maintenance),
                  },
                  {
                    label: "Seguridad distrital",
                    fn: (x: CatalogListing) => districtIndicator(x, "safety"),
                  },
                  {
                    label: "Conveniencia distrital",
                    fn: (x: CatalogListing) =>
                      districtIndicator(x, "convenience"),
                  },
                  { label: "Disponibilidad", fn: () => "No verificada" },
                ].map((row) => (
                  <tr key={row.label}>
                    <th scope="row">{row.label}</th>
                    {compare.map((x) => {
                      const value = row.fn(x);
                      return <td key={x.id} className={value === "Sin datos" || value === "Por confirmar" || value === "No verificada" || value === "Sin referencia" ? "comparison-missing" : ""}>{value}</td>;
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Modal>
      )}
      {authPrompt && (
        <Modal
          title="Guarda lo que te importa"
          close={() => {
            setAuthPrompt(false);
            setPendingFavorite(null);
          }}
        >
          <p>
            Inicia sesión para conservar tus viviendas favoritas y tu perfil en
            InmoScore.
            {pendingFavorite &&
              " Al ingresar retomaremos la vivienda que elegiste guardar."}
          </p>
          <button
            className="button button-dark"
            onClick={() => {
              setAuthPrompt(false);
              go("/ingresar");
            }}
          >
            Iniciar sesión <ArrowRight size={18} />
          </button>
          <button
            className="text-button"
            onClick={() => {
              setAuthPrompt(false);
              go("/registro");
            }}
          >
            Crear una cuenta
          </button>
          <button
            className="text-button"
            onClick={() => {
              setAuthPrompt(false);
              setPendingFavorite(null);
            }}
          >
            Seguir explorando
          </button>
        </Modal>
      )}
      {deleteOpen && (
        <Modal
          title="¿Eliminar tu cuenta de InmoScore?"
          close={() => {
            setDeleteOpen(false);
            setDeletePassword("");
          }}
        >
          <p>
            Se eliminarán tu cuenta, tu perfil, tus guardados y todas tus
            sesiones. No se puede deshacer.
          </p>
          <label className="field">
            Confirma tu contraseña
            <input
              type="password"
              autoComplete="current-password"
              minLength={10}
              maxLength={128}
              value={deletePassword}
              onChange={(e) => setDeletePassword(e.target.value)}
            />
          </label>
          <button
            className="button button-danger"
            disabled={busy || deletePassword.length < 10}
            onClick={async () => {
              setBusy(true);
              try {
                await api("/api/account", {
                  method: "DELETE",
                  body: JSON.stringify({ password: deletePassword }),
                });
                setMe({ user: null, profile: null, favorites: [] });
                setSaved([]);
                setCompare([]);
                reset();
                setDeleteOpen(false);
                setDeletePassword("");
                go("/");
                setToast("Tu cuenta y tus datos se eliminaron.");
              } catch (e) {
                setToast((e as Error).message);
              } finally {
                setBusy(false);
              }
            }}
          >
            Eliminar mi cuenta
          </button>
          <button
            className="button button-white"
            onClick={() => {
              setDeleteOpen(false);
              setDeletePassword("");
            }}
          >
            Conservar mi cuenta
          </button>
        </Modal>
      )}
      {toast && (
        <div className="toast" role="status">
          <CheckCircle2 size={18} />
          <span>{toast}</span>
          <button aria-label="Cerrar aviso" onClick={() => setToast("")}>
            <X size={15} />
          </button>
        </div>
      )}
      <InmoScoreHelp
        context={{
          signedIn: Boolean(me.user),
          path,
          comparedCount: compare.length,
          profile,
          districts,
          ...(path === "/explorar" && result && !rankingBusy ? {
            effectiveBudget: result.effectiveBudget,
            cap: result.cap,
            matchedTotal: result.matchedTotal,
          } : {}),
        }}
        onNavigate={go}
        hidden={compareOpen || authPrompt || deleteOpen || filters}
      />
    </div>
  );
}

function useDialogFocus(
  ref: React.RefObject<HTMLElement | null>,
  active: boolean,
) {
  useEffect(() => {
    if (!active) return;
    const previous = document.activeElement as HTMLElement | null;
    const oldOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    ref.current?.focus();
    const trap = (event: KeyboardEvent) => {
      if (event.key !== "Tab") return;
      const nodes = Array.from(
        ref.current?.querySelectorAll<HTMLElement>(
          'button:not([disabled]),a[href],input:not([disabled]),select:not([disabled]),textarea:not([disabled]),[tabindex="0"]',
        ) ?? [],
      ).filter((node) => node.getClientRects().length > 0);
      if (!nodes.length) {
        event.preventDefault();
        return;
      }
      const first = nodes[0],
        last = nodes[nodes.length - 1];
      if (
        event.shiftKey &&
        (document.activeElement === first ||
          document.activeElement === ref.current)
      ) {
        event.preventDefault();
        last.focus();
      } else if (
        !event.shiftKey &&
        (document.activeElement === last ||
          document.activeElement === ref.current)
      ) {
        event.preventDefault();
        first.focus();
      }
    };
    document.addEventListener("keydown", trap);
    return () => {
      document.body.style.overflow = oldOverflow;
      document.removeEventListener("keydown", trap);
      if (previous?.isConnected) previous.focus();
    };
  }, [ref, active]);
}

function Modal({
  title,
  close,
  children,
  wide = false,
}: {
  title: string;
  close: () => void;
  children: React.ReactNode;
  wide?: boolean;
}) {
  const ref = useRef<HTMLDivElement>(null);
  useDialogFocus(ref, true);
  return (
    <div
      className="modal-overlay"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) close();
      }}
    >
      <div
        ref={ref}
        role="dialog"
        aria-modal="true"
        aria-label={title}
        tabIndex={-1}
        className={`modal ${wide ? "modal-wide" : ""}`}
      >
        <div className="modal-heading">
          <h2>{title}</h2>
          <button
            className="icon-button"
            aria-label="Cerrar diálogo"
            onClick={close}
          >
            <X size={22} />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}

type GeoFeature = {
  properties: Record<string, string>;
  geometry: { type: string; coordinates: number[][][] | number[][][][] };
};
function MapPanel({ item }: { item: CatalogListing }) {
  const [features, setFeatures] = useState<GeoFeature[]>([]),
    [zoom, setZoom] = useState(1),
    [mapError, setMapError] = useState(false);
  useEffect(() => {
    let active = true;
    fetch("/districts.geojson")
      .then((r) => {
        // The optional file is absent in this delivery; Next may return HTML with status 200.
        if (!r.ok || !r.headers.get("content-type")?.includes("json"))
          throw Error();
        return r.json();
      })
      .then((d) => {
        if (!Array.isArray(d.features) || d.features.length === 0)
          throw Error();
        if (active) setFeatures((d as { features: GeoFeature[] }).features);
      })
      .catch(() => {
        if (active) setMapError(true);
      });
    return () => {
      active = false;
    };
  }, []);
  const location = item?.location;
  if (!location)
    return (
      <div className="map-unavailable">
        <MapPin size={28} />
        <strong>Ubicación pendiente de geocodificación</strong>
        <p>No contamos con un punto suficientemente preciso.</p>
      </div>
    );
  const { lat, lng } = location;
  const radius = [0.07, 0.035, 0.018, 0.009][zoom];
  const height = 430,
    width = 740,
    latRadius = (radius * height) / width;
  const project = (point: number[]) => [
    ((point[0] - lng + radius) / (2 * radius)) * width,
    ((lat + latRadius - point[1]) / (2 * latRadius)) * height,
  ];
  const normalize = (v: string) =>
    (v || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toUpperCase();
  const shapes = features.flatMap((f, index) => {
    if (!f.geometry) return [];
    const polygons =
      f.geometry.type === "Polygon"
        ? [f.geometry.coordinates as number[][][]]
        : (f.geometry.coordinates as number[][][][]);
    return polygons.map((poly, j) => {
      const ring = poly[0];
      if (!ring?.length) return null;
      const d = poly
        .map(
          (r) =>
            r
              .map((p, k) => {
                const [x, y] = project(p);
                return `${k ? "L" : "M"}${x.toFixed(2)},${y.toFixed(2)}`;
              })
              .join(" ") + " Z",
        )
        .join(" ");
      const name = f.properties.NOMBDIST || "";
      let district = normalize(name);
      if (district === "MAGDALENA VIEJA") district = "PUEBLO LIBRE";
      const selected = district === normalize(item.district);
      const xs = ring.map((p) => p[0]),
        ys = ring.map((p) => p[1]);
      const center = project([
        (Math.min(...xs) + Math.max(...xs)) / 2,
        (Math.min(...ys) + Math.max(...ys)) / 2,
      ]);
      return (
        <g key={`${index}-${j}`}>
          <path
            d={d}
            fill={selected ? "#d6e7b6" : "#f3f5eb"}
            stroke="#b8c7a5"
            strokeWidth="1.3"
            fillRule="evenodd"
          />
          {center[0] > 30 &&
            center[0] < width - 30 &&
            center[1] > 20 &&
            center[1] < height - 20 && (
              <text
                x={center[0]}
                y={center[1]}
                className="map-district-label"
                textAnchor="middle"
                fill="#52634c"
                fontSize="16"
                letterSpacing="1"
              >
                {district}
              </text>
            )}
        </g>
      );
    });
  });
  return (
    <div className="map-panel">
      <div className="local-map">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          role="img"
          aria-label={
            features.length > 0
              ? `Mapa de límites distritales con ubicación aproximada en ${item.district}`
              : `Referencia de ubicación en ${item.district}; cartografía local no incluida`
          }
        >
          <rect width={width} height={height} fill="#e7eedc" />
          {shapes}
          <circle cx="370" cy="215" r="42" fill="#7d9f4930" />
          <circle
            cx="370"
            cy="215"
            r="22"
            fill="#173d31"
            stroke="#fff"
            strokeWidth="4"
          />
          <path
            d="m360 216 10-9 10 9v11h-20z"
            fill="none"
            stroke="#def492"
            strokeWidth="2"
          />
        </svg>
        <span className="map-price-label">{soles(item.price)}</span>
        <span className="local-map-note">
          {features.length > 0
            ? "Límites distritales · No incluye calles"
            : "Ubicación aproximada · Sin cartografía local"}
        </span>
        {features.length > 0 && (
          <div className="map-controls">
            <button
              aria-label="Acercar mapa"
              disabled={zoom === 3}
              onClick={() => setZoom((z) => z + 1)}
            >
              +
            </button>
            <button
              aria-label="Alejar mapa"
              disabled={zoom === 0}
              onClick={() => setZoom((z) => z - 1)}
            >
              −
            </button>
          </div>
        )}
        {mapError && (
          <p className="map-error">
            Cartografía local no incluida. Consulta esta ubicación en
            OpenStreetMap.
          </p>
        )}
      </div>
      <div>
        <MapPin size={16} />
        <span>
          {item.district} · precisión:{" "}
          {location.precision === "exacta" ? "edificio" : "calle"}
          <small>
            Coordenadas: {lat.toFixed(5)}, {lng.toFixed(5)} · Aproximadas,
            sujetas a error.
          </small>
        </span>
        <a
          href={`https://www.openstreetmap.org/?mlat=${lat}&mlon=${lng}#map=16/${lat}/${lng}`}
          target="_blank"
          rel="noopener noreferrer"
          className="external-map-link"
        >
          Abrir en OpenStreetMap <ArrowUpRight size={12} />
        </a>
      </div>
    </div>
  );
}
