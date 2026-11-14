import Link from "next/link";
import type { PreferenceWeights } from "../lib/recommendation";
import "./priority-graphic.css";

type PriorityGraphicProps = {
  weights: PreferenceWeights;
};

export default function PriorityGraphic({ weights }: PriorityGraphicProps) {
  const total = weights.price + weights.safety + weights.convenience;
  const price = total > 0 ? Math.round((weights.price / total) * 100) : 0;
  const safety = total > 0 ? Math.min(100 - price, Math.round((weights.safety / total) * 100)) : 0;
  const services = total > 0 ? Math.max(0, 100 - price - safety) : 0;
  const activeCount = [weights.price, weights.safety, weights.convenience].filter(value => value > 0).length;
  const segments = [
    { label: "Precio", value: price, className: "price" },
    { label: "Seguridad distrital", value: safety, className: "safety" },
    { label: "Servicios del distrito", value: services, className: "services" },
  ];

  const chartBackground = total > 0
    ? `conic-gradient(var(--forest) 0 ${price}%, var(--orange) ${price}% ${price + safety}%, var(--lime) ${price + safety}% 100%)`
    : "#dfe7dd";

  return (
    <section className="priority-story wrap" aria-labelledby="priority-story-title">
      <div className="priority-story-copy">
        <span className="priority-story-kicker">EL ORDEN DE TUS RESULTADOS</span>
        <h2 id="priority-story-title">Mira qué pesa en tu búsqueda.</h2>
        <p>
          Elige la importancia del precio, la seguridad distrital y los servicios.
          El gráfico muestra el peso relativo de tus prioridades actuales al ordenar viviendas.
        </p>
        <Link href="/perfil">Ajustar mis prioridades <span aria-hidden="true">↗</span></Link>
      </div>
      <div className="priority-graphic-panel">
        <div className="priority-graphic-heading">
          <span>PRIORIDADES ACTUALES</span>
          <strong>{total > 0 ? `100% repartido entre ${activeCount} ${activeCount === 1 ? "criterio activo" : "criterios activos"}` : "Elige al menos un criterio"}</strong>
        </div>
        <div className="priority-graphic-body">
          <div className="priority-ring" style={{ background: chartBackground }} aria-hidden="true">
            <div><strong>{activeCount}</strong><span>{activeCount === 1 ? "criterio" : "criterios"}</span></div>
          </div>
          <ul aria-label="Peso relativo de las prioridades">
            {segments.map((segment) => (
              <li key={segment.className}>
                <span className={`priority-swatch ${segment.className}`} aria-hidden="true" />
                <span>{segment.label}</span>
                <strong>{segment.value}%</strong>
              </li>
            ))}
          </ul>
        </div>
        <p>Estas prioridades ordenan los avisos. La estimación del precio se calcula por separado.</p>
      </div>
    </section>
  );
}
