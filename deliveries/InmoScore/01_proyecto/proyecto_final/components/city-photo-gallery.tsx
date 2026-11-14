import Image from "next/image";
import "./city-photo-gallery.css";

const photos = [
  {
    place: "Barranco",
    title: "Puente de los Suspiros",
    year: "2007",
    src: "/imagenes/barranco-puente.jpg",
    alt: "Puente de los Suspiros y una casona roja en Barranco, Lima",
    author: "Manuel González Olaechea y Franco",
    source: "https://commons.wikimedia.org/wiki/File:Puente_de_los_Suspiros.JPG",
    license: "CC BY 3.0",
    licenseUrl: "https://creativecommons.org/licenses/by/3.0/",
  },
  {
    place: "Miraflores",
    title: "Parque Kennedy",
    year: "2011",
    src: "/imagenes/miraflores-kennedy.jpg",
    alt: "Parque Kennedy con jardines, palmeras y edificios de Miraflores",
    author: "Municipalidad de Miraflores",
    source: "https://commons.wikimedia.org/wiki/File:Parque_Kennedy.jpg",
    license: "CC BY 2.0",
    licenseUrl: "https://creativecommons.org/licenses/by/2.0/",
  },
  {
    place: "Cercado de Lima",
    title: "Plaza San Martín",
    year: "2020",
    src: "/imagenes/cercado-plaza.jpg",
    alt: "Vista aérea de la Plaza San Martín y sus edificios en el centro de Lima",
    author: "Ministerio de Defensa del Perú",
    source: "https://commons.wikimedia.org/wiki/File:Plaza_San_Mart%C3%ADn%2C_Lima_Peru.jpg",
    license: "CC BY 2.0",
    licenseUrl: "https://creativecommons.org/licenses/by/2.0/",
  },
  {
    place: "Costa Verde",
    title: "Acantilados de Miraflores",
    year: "2013",
    src: "/imagenes/miraflores-costa.jpg",
    alt: "Acantilados de Miraflores, edificios y vía costera junto al océano",
    author: "David Bush",
    source: "https://commons.wikimedia.org/wiki/File:Cliffs_at_Miraflores%2C_Lima.jpg",
    license: "CC BY 2.0",
    licenseUrl: "https://creativecommons.org/licenses/by/2.0/",
  },
] as const;

export default function CityPhotoGallery() {
  return (
    <section className="city-gallery wrap" aria-labelledby="city-gallery-title">
      <div className="city-gallery-heading">
        <div>
          <span>LA CIUDAD EN FOTOGRAFÍAS</span>
          <h2 id="city-gallery-title">Cuatro miradas de Lima.</h2>
        </div>
        <p>Espacios públicos de distintas fechas para conocer la ciudad. Estas fotos no corresponden a los inmuebles del catálogo.</p>
      </div>
      <p className="city-gallery-swipe-hint">Desliza para ver las cuatro fotografías →</p>
      <div className="city-gallery-grid">
        {photos.map((photo) => (
          <figure className="city-gallery-card" key={photo.src}>
            <div className="city-gallery-image">
              <Image
                src={photo.src}
                alt={photo.alt}
                fill
                sizes="(max-width: 640px) 82vw, (max-width: 1100px) 48vw, 24vw"
                loading="lazy"
              />
            </div>
            <figcaption>
              <span>{photo.place} · {photo.year}</span>
              <strong>{photo.title}</strong>
              <small>
                Foto: <a href={photo.source} target="_blank" rel="noopener noreferrer">{photo.author}</a>
                {" · "}<a href={photo.licenseUrl} target="_blank" rel="noopener noreferrer">{photo.license}</a>
                {" · "}encuadre para la web
              </small>
            </figcaption>
          </figure>
        ))}
      </div>
    </section>
  );
}
