"""Build the Week 6 feature store from the real acquired listing source."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WEEK06_RAW = ROOT / "deliveries" / "week06" / "data" / "raw"
WEEK06_PROCESSED = ROOT / "deliveries" / "week06" / "data" / "processed"


def main():
    from week06_features import crime_index, district_baseline, convenience as build_convenience, zone_composite, feature_store

    source = WEEK06_RAW / "listings_urbania.csv"
    if not source.exists():
        raise FileNotFoundError(
            f"Missing {source}. Run acquire_real_sources.py first."
        )
    WEEK06_PROCESSED.mkdir(parents=True, exist_ok=True)
    crime_path = WEEK06_PROCESSED / "crime_index_distrito.csv"
    crime = crime_index(str(WEEK06_RAW / "denuncias_lima.csv"), str(WEEK06_RAW / "distritos_lima_socioec.csv"))
    crime.to_csv(crime_path, index=False)
    baseline_path = WEEK06_PROCESSED / "baseline_precio_m2_distrito.csv"
    baseline, _ = district_baseline(str(source), str(crime_path))
    baseline.to_csv(baseline_path, index=False)
    convenience_path = WEEK06_PROCESSED / "zone_convenience_index.csv"
    convenience_data = build_convenience(str(WEEK06_RAW / "pois_lima.csv"), str(WEEK06_RAW / "distritos_lima_geo.geojson"), str(WEEK06_RAW / "distritos_lima_socioec.csv"))
    convenience_data.to_csv(convenience_path, index=False)
    composite_path = WEEK06_PROCESSED / "zone_index_distrito.csv"
    composite = zone_composite(str(crime_path), str(convenience_path), str(baseline_path), str(WEEK06_RAW / "distritos_lima_socioec.csv"))
    composite.to_csv(composite_path, index=False)
    output = WEEK06_PROCESSED / "listings_feature_store.csv"
    data = feature_store(str(source), str(composite_path), str(baseline_path), str(WEEK06_RAW / "bcrp_precios.csv"), str(WEEK06_RAW / "proyectos_mivivienda.csv"))
    data.to_csv(output, index=False, encoding="utf-8")
    print(f"{len(data)} listings -> {output}")


if __name__ == "__main__":
    main()