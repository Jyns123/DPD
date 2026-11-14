import type { EventInput } from './analytics-validation';
const CONSENT = 'inmoscore:analytics-consent';
const SESSION = 'inmoscore:analytics-session';
let lastPage = '';
export function analyticsEnabled() {
  try { return typeof window !== 'undefined' && localStorage.getItem(CONSENT)==='yes'; }
  catch { return false; }
}
export function setAnalyticsConsent(enabled: boolean) {
  try {
    localStorage.setItem(CONSENT,enabled?'yes':'no');
    if (!enabled) { sessionStorage.removeItem(SESSION); lastPage=''; }
    window.dispatchEvent(new Event('inmoscore:consent'));
  } catch { /* Una restricción del navegador no debe impedir usar la web. */ }
}
export function trackPageView() {
  if(!analyticsEnabled() || window.location.pathname.startsWith('/tablero')) return;
  try {
    const key = `${sessionStorage.getItem(SESSION)||''}|${window.location.pathname}`;
    if(key===lastPage) return;
    trackInteraction('page_view');
    lastPage=`${sessionStorage.getItem(SESSION)||''}|${window.location.pathname}`;
  } catch { /* La navegación sigue disponible sin almacenamiento local. */ }
}
export function trackInteraction(type: EventInput['type'], details: Omit<Partial<EventInput>, 'id'|'visitorId'|'type'> = {}) {
  if (!analyticsEnabled()) return;
  try {
    let visitorId = sessionStorage.getItem(SESSION);
    if (!visitorId) { visitorId = crypto.randomUUID(); sessionStorage.setItem(SESSION,visitorId); }
    const payload = {id:crypto.randomUUID(),visitorId,type,...details};
    void fetch('/api/analytics',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload),keepalive:true})
      .then(response=>{ if(!response.ok) window.dispatchEvent(new Event('inmoscore:analytics-error')); })
      .catch(()=>window.dispatchEvent(new Event('inmoscore:analytics-error')));
  } catch { /* Las métricas son opcionales; nunca bloquean una búsqueda. */ }
}
