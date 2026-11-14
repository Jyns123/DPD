'use client';
import { useEffect, useState } from 'react';
import { analyticsEnabled, setAnalyticsConsent, trackPageView } from '../lib/track-interaction';
import './analytics-consent.css';
export default function AnalyticsConsent() {
  const [enabled,setEnabled]=useState(false);
  const [ready,setReady]=useState(false);
  const [failed,setFailed]=useState(false);
  useEffect(()=>{
    let active=true;
    const refresh=()=>setEnabled(analyticsEnabled());
    const page=()=>trackPageView();
    const error=()=>setFailed(true);
    queueMicrotask(()=>{if(active){refresh();setReady(true);page();}});
    window.addEventListener('inmoscore:consent',refresh);
    window.addEventListener('popstate',page);
    window.addEventListener('inmoscore:navigate',page);
    window.addEventListener('inmoscore:analytics-error',error);
    return ()=>{active=false;window.removeEventListener('inmoscore:consent',refresh);window.removeEventListener('popstate',page);window.removeEventListener('inmoscore:navigate',page);window.removeEventListener('inmoscore:analytics-error',error);};
  },[]);
  if(!ready) return null;
  return <aside className="analytics-consent" aria-label="Participación en las métricas">
    <details><summary>Métricas de la demostración · {enabled?'activadas':'desactivadas'}</summary>
      <p>Puedes compartir interacciones sin tu nombre: búsquedas, favoritos y uso de la ayuda. No enviamos ingresos, correos ni el texto del chat al tablero. Se guardan hasta 90 días o 20 000 eventos en el servidor de esta aplicación. Cada sesión se cuenta por separado.</p>
      <label><input type="checkbox" checked={enabled} onChange={event=>{setAnalyticsConsent(event.target.checked);setFailed(false);if(event.target.checked)trackPageView();}}/> Participar en las métricas</label>
      <p>Puedes desactivar el registro cuando quieras. Las interacciones anteriores siguen contándose hasta que vence su conservación. La limpieza se ejecuta al registrar o consultar datos en la aplicación.</p>
      {failed&&<p role="status">La web sigue funcionando, pero alguna interacción no pudo guardarse en el tablero.</p>}
    </details>
  </aside>;
}
