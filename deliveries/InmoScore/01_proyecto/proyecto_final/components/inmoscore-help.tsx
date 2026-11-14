"use client";

import { useEffect, useRef, useState } from "react";
import { ArrowRight, MessageCircle, RotateCcw, Send, ThumbsDown, ThumbsUp, X } from "lucide-react";
import Image from "next/image";
import { answerQuestion, answerTopic, followUpTopics, suggestedTopics, HELP_TOPICS, type HelpAnswer, type HelpContext, type HelpTopic } from "../lib/help";
import { answerHelpSearch, parseHelpSearch, unavailableSearchAnswer } from "../lib/help-search";
import { trackInteraction } from "../lib/track-interaction";
import "./inmoscore-help.css";

type Exchange = { id: number; question: string; answer: HelpAnswer; feedback?: boolean };

function currentStep(context: HelpContext): string {
  if (context.path === "/explorar") {
    if (typeof context.matchedTotal === "number") return context.matchedTotal === 0
      ? "Tu búsqueda no tiene coincidencias. Podemos revisar filtros y presupuesto."
      : `Tu búsqueda tiene ${context.matchedTotal} ${context.matchedTotal === 1 ? "coincidencia" : "coincidencias"}. Puedes preguntar cómo se ordenan.`;
    return "Estás explorando viviendas. Podemos revisar filtros, puntajes o fotografías.";
  }
  if (context.path === "/perfil") return "Estás definiendo tu perfil. Podemos revisar el tope y tus prioridades.";
  if (context.path?.startsWith("/inmueble/")) return "Estás revisando un aviso. Podemos aclarar la referencia de precio y sus advertencias.";
  if (context.path === "/guardados") return "Estás en tus guardados. Podemos ayudarte a comparar tus opciones.";
  return "Podemos ayudarte a empezar, comparar y entender los resultados.";
}

export default function InmoScoreHelp({ context, onNavigate, hidden = false }: {
  context: HelpContext;
  onNavigate: (href: string) => void;
  hidden?: boolean;
}) {
  const [open, setOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [exchanges, setExchanges] = useState<Exchange[]>([]);
  const [feedbackMessage, setFeedbackMessage] = useState("");
  const [topicsOpen, setTopicsOpen] = useState(false);
  const [replyBusy, setReplyBusy] = useState(false);
  const dialog = useRef<HTMLElement>(null);
  const input = useRef<HTMLInputElement>(null);
  const log = useRef<HTMLDivElement>(null);
  const launcher = useRef<HTMLButtonElement>(null);
  const nextId = useRef(0);
  const requestSequence = useRef(0);
  const requestController = useRef<AbortController | null>(null);
  const contextRef = useRef(context);
  useEffect(() => { contextRef.current = context; }, [context]);

  const addAnswer = (text: string, answer: HelpAnswer) => {
    setExchanges(previous => [...previous.slice(-11), { id: ++nextId.current, question: text, answer }]);
    setQuestion("");
    setFeedbackMessage("");
    setTopicsOpen(false);
    trackInteraction("chat_question", { topic: answer.topic === "unknown" ? "sin_respuesta" : answer.topic });
  };

  const chooseTopic = (topic: HelpTopic) => {
    ++requestSequence.current;
    requestController.current?.abort();
    setReplyBusy(false);
    const label = HELP_TOPICS.find(item => item.id === topic)!.label;
    addAnswer(label, answerTopic(topic, contextRef.current));
  };

  async function submitQuestion(text: string) {
    const clean = text.trim().slice(0, 400);
    if (!clean || replyBusy) return;
    const search = parseHelpSearch(clean, contextRef.current.districts);
    if (!search) { addAnswer(clean, answerQuestion(clean, contextRef.current)); return; }
    const sequence = ++requestSequence.current;
    requestController.current?.abort();
    const controller = new AbortController();
    requestController.current = controller;
    const timeout = setTimeout(() => controller.abort(), 15000);
    setReplyBusy(true);
    try {
      const answer = await answerHelpSearch(search, contextRef.current, controller.signal);
      if (sequence === requestSequence.current) addAnswer(clean, answer);
    } catch {
      if (sequence === requestSequence.current) addAnswer(clean, unavailableSearchAnswer());
    } finally {
      clearTimeout(timeout);
      if (sequence === requestSequence.current) setReplyBusy(false);
    }
  }

  useEffect(() => {
    const handleOpen = (event: Event) => {
      if (hidden) return;
      setOpen(true);
      const requested = (event as CustomEvent<HelpTopic>).detail;
      if (HELP_TOPICS.some(topic => topic.id === requested)) {
        const label = HELP_TOPICS.find(topic => topic.id === requested)!.label;
        const answer = answerTopic(requested, contextRef.current);
        setExchanges(previous => [...previous.slice(-11), { id: ++nextId.current, question: label, answer }]);
        trackInteraction("chat_question", { topic: requested });
      }
    };
    window.addEventListener("inmoscore:open-help", handleOpen);
    return () => window.removeEventListener("inmoscore:open-help", handleOpen);
  }, [hidden]);

  useEffect(() => {
    if (!open || hidden) return;
    const previous = document.activeElement as HTMLElement | null;
    const launchButton = launcher.current;
    const oldOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    dialog.current?.focus();
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") { event.preventDefault(); setOpen(false); }
      if (event.key !== "Tab") return;
      const controls = Array.from(dialog.current?.querySelectorAll<HTMLElement>(
        'button:not([disabled]),a[href],input:not([disabled]),[tabindex="0"]',
      ) ?? []).filter(node => node.getClientRects().length > 0);
      const first = controls[0], last = controls[controls.length - 1];
      if (!first) { event.preventDefault(); return; }
      if (event.shiftKey && (document.activeElement === first || document.activeElement === dialog.current)) {
        event.preventDefault(); last.focus();
      } else if (!event.shiftKey && (document.activeElement === last || document.activeElement === dialog.current)) {
        event.preventDefault(); first.focus();
      }
    };
    document.addEventListener("keydown", onKey);
    return () => {
      document.body.style.overflow = oldOverflow;
      document.removeEventListener("keydown", onKey);
      if (previous?.isConnected) previous.focus();
      else launchButton?.focus();
    };
  }, [open, hidden]);

  useEffect(() => {
    if (open) log.current?.scrollTo({ top: log.current.scrollHeight, behavior: "instant" });
  }, [exchanges, open]);
  const lastExchangeId = exchanges.at(-1)?.id;
  useEffect(() => {
    // El tema se pliega al responder; el foco sigue dentro de la conversación.
    if (open && lastExchangeId !== undefined) input.current?.focus();
  }, [lastExchangeId, open]);

  function markFeedback(id: number, helpful: boolean) {
    const exchange = exchanges.find(item => item.id === id);
    if (!exchange || exchange.feedback !== undefined) return;
    setExchanges(previous => previous.map(item => item.id === id ? { ...item, feedback: helpful } : item));
    setFeedbackMessage(helpful ? "Gracias. Puedes continuar con otra consulta." : "Vamos por partes. Debajo de la respuesta tienes otras preguntas que pueden ayudarte.");
    trackInteraction("chat_feedback", { helpful, topic: exchange.answer.topic === "unknown" ? "sin_respuesta" : exchange.answer.topic });
    requestAnimationFrame(() => {
      const nextQuestion = dialog.current?.querySelector<HTMLButtonElement>(`[data-help-exchange="${id}"] .help-followups button`);
      if (!helpful && nextQuestion) nextQuestion.focus();
      else input.current?.focus();
    });
  }

  if (hidden) return null;
  return <>
    <button ref={launcher} className="help-launcher" onClick={() => setOpen(true)} aria-haspopup="dialog" aria-expanded={open} aria-controls="inmoscore-help">
      <MessageCircle size={20} aria-hidden="true" /><span>Pregunta al asistente</span>
    </button>
    {open && <div className="help-overlay" onMouseDown={event => { if (event.target === event.currentTarget) setOpen(false); }}>
      <section ref={dialog} id="inmoscore-help" className="help-dialog" role="dialog" aria-modal="true" aria-labelledby="help-title" aria-describedby="help-description" tabIndex={-1}>
        <header className="help-heading">
          <span className="help-avatar"><Image src="/logo.png" width={1254} height={1254} sizes="30px" alt="" /></span>
          <div><h2 id="help-title">Conversemos sobre tu búsqueda</h2><p>Asistente de InmoScore · respuestas de esta web</p></div>
          <button className="help-close" onClick={() => setOpen(false)} aria-label="Cerrar guía"><X size={22} /></button>
        </header>
        <p id="help-description" className="help-intro">Puedes elegir un tema o escribir una pregunta. Para recomendar viviendas, consulta el catálogo y el modelo de esta web con los filtros que indiques. No consulta un servicio externo de chat.</p>
        <p className="help-current-step" aria-live="polite"><strong>En esta pantalla</strong>{currentStep(context)}</p>
        <button className="help-recommend-trigger" disabled={replyBusy} onClick={() => { void submitQuestion("Recomiéndame viviendas con mis filtros actuales"); }}><span><strong>Ver viviendas para mí</strong><small>Con los filtros y prioridades de tu perfil actual</small></span><ArrowRight size={17} aria-hidden="true" /></button>
        {exchanges.length === 0 && <div className="help-suggestions"><strong>Para este momento de tu búsqueda</strong><div>{suggestedTopics(context).map(topic => <button key={topic} onClick={() => chooseTopic(topic)}>{HELP_TOPICS.find(item => item.id === topic)!.label}<ArrowRight size={14} aria-hidden="true" /></button>)}</div></div>}
        <details className="help-topics" open={topicsOpen} onToggle={event => setTopicsOpen(event.currentTarget.open)}>
          <summary>Ver todos los temas</summary>
          <div>{HELP_TOPICS.map(topic => <button key={topic.id} onClick={() => chooseTopic(topic.id)}>{topic.label}</button>)}</div>
        </details>
        <div className="help-conversation" ref={log} role="log" aria-label="Conversación de ayuda" aria-live="polite" aria-relevant="additions">
          {exchanges.length === 0 && <div className="help-welcome"><strong>Una decisión se entiende mejor paso a paso.</strong><p>Podemos revisar por qué cambia tu tope, cómo se ordenan las opciones o qué significa una advertencia del modelo.</p></div>}
          {exchanges.map(exchange => <article className="help-exchange" key={exchange.id} data-help-exchange={exchange.id}>
            <p className="help-question"><span className="help-speaker">Tu consulta</span>{exchange.question}</p>
            <div className="help-answer"><span className="help-speaker">Guía InmoScore</span><h3>{exchange.answer.title}</h3>
              {exchange.answer.paragraphs.map((paragraph, index) => <p key={index}>{paragraph}</p>)}
              {exchange.answer.recommendations && <div className="help-recommendations" aria-label="Viviendas recomendadas">
                {exchange.answer.recommendations.map(item => <button key={item.id} className="help-property" onClick={() => { setOpen(false); onNavigate(`/inmueble/${encodeURIComponent(item.id)}`); }}>
                  <span className="help-property-location">{item.district} · {item.rooms} dorm. · {item.area} m²</span>
                  <strong>{item.address}</strong>
                  <span className="help-property-price">S/ {new Intl.NumberFormat("es-PE").format(item.price)} <small>· afinidad {item.score}/100</small></span>
                  <span className="help-property-reason">{item.reasons[0] ?? "Cumple los filtros indicados"}</span>
                  <span className="help-property-open">Ver ficha <ArrowRight size={14} aria-hidden="true" /></span>
                </button>)}
              </div>}
              {exchange.answer.action && <button className="help-action" onClick={() => { setOpen(false); onNavigate(exchange.answer.action!.href); }}>{exchange.answer.action.label}<ArrowRight size={16} /></button>}
              <div className="help-feedback"><span>¿Te orientó?</span>
                <button disabled={exchange.feedback !== undefined} aria-label="Esta respuesta me orientó" aria-pressed={exchange.feedback === true} onClick={() => markFeedback(exchange.id, true)}><ThumbsUp size={15} /> Sí</button>
                <button disabled={exchange.feedback !== undefined} aria-label="Esta respuesta no resolvió mi duda" aria-pressed={exchange.feedback === false} onClick={() => markFeedback(exchange.id, false)}><ThumbsDown size={15} /> Aún no</button>
              </div>
              <div className="help-followups"><strong>{exchange.feedback === false || exchange.answer.topic === "unknown" ? "Probemos con una pregunta más concreta" : "También puedes preguntar"}</strong>{followUpTopics(exchange.answer.topic).map(topic => <button key={topic} onClick={() => chooseTopic(topic)}>{HELP_TOPICS.find(item => item.id === topic)!.label}<ArrowRight size={14} /></button>)}</div>
            </div>
          </article>)}
        </div>
        <p className="help-feedback-status" role="status">{feedbackMessage}</p>
        <form className="help-compose" onSubmit={event => { event.preventDefault(); void submitQuestion(question); }}>
          <label htmlFor="help-question">Tu pregunta sobre InmoScore</label>
          <div><input ref={input} id="help-question" value={question} onChange={event => setQuestion(event.target.value)} maxLength={400} autoComplete="off" aria-describedby="help-question-length" placeholder="Busco 2 dormitorios en Miraflores por S/ 400,000" /><button type="submit" disabled={!question.trim() || replyBusy} aria-label="Consultar"><Send size={19} /></button></div>
          <span id="help-question-length" className="help-question-length">{question.length}/400 caracteres</span>
          {replyBusy && <span className="help-searching" role="status">Buscando viviendas que cumplan tus filtros…</span>}
        </form>
        <div className="help-bottom"><small>No escribas datos personales. La conversación se borra al recargar.</small><button onClick={() => { ++requestSequence.current; requestController.current?.abort(); setReplyBusy(false); setExchanges([]); setQuestion(""); setFeedbackMessage("Listo. Puedes empezar una nueva consulta."); setTopicsOpen(false); input.current?.focus(); }}><RotateCcw size={14} /> Nueva consulta</button></div>
      </section>
    </div>}
  </>;
}
