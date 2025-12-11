import io
import os
import zipfile
from pathlib import Path

import pandas as pd
import requests


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

#set NREL_API_KEY and CENSUS_API_KEY before running
NREL_API_KEY = os.getenv("NREL_API_KEY", "")
CENSUS_API_KEY = os.getenv("CENSUS_API_KEY", "")


def ensure_dirs() -> None:
    for folder in (DATA_DIR, RAW_DIR, PROCESSED_DIR):
        folder.mkdir(parents=True, exist_ok=True)


def fetch_nrel_chargers() -> Path:
    """
    Download current NREL electric charger data for NJ (public only) as CSV.
    NREL does not expose a year filter. This pulls the latest live dataset.
    """
    if not NREL_API_KEY:
        raise RuntimeError("Set NREL_API_KEY in env before fetching chargers")
    #Command I run if doing this manually:
    #curl -L "https://developer.nrel.gov/api/alt-fuel-stations/v1.csv?api_key=YOUR_KEY&fuel_type=ELEC&state=NJ&access=public" -o data/raw/alt_fuel_stations_nj_raw.csv
    ensure_dirs()
    url = (
        "https://developer.nrel.gov/api/alt-fuel-stations/v1.csv"
        f"?api_key={NREL_API_KEY}&fuel_type=ELEC&state=NJ&access=public"
    )
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    out_path = RAW_DIR / "alt_fuel_stations_nj_raw.csv"
    out_path.write_bytes(resp.content)
    df = pd.read_csv(out_path)
    print(f"Saved chargers CSV to {out_path} rows={len(df)} cols={len(df.columns)}")
    return out_path


def fetch_census_subject_tables(year: int = 2021) -> Path:
    """
    Download ACS 5-year subject table slice for NJ counties.
    Pulls population, median income, renter percent, commute time.
    """
    if not CENSUS_API_KEY:
        raise RuntimeError("Set CENSUS_API_KEY in env before fetching ACS data")
    #Command I run if doing this manually:
    #curl -L "https://api.census.gov/data/2022/acs/acs5/subject?get=NAME,S0101_C01_001E,S1901_C01_001E,S2502_C03_001E,S0801_C01_049E&for=county:*&in=state:34&key=YOUR_KEY" -o data/raw/acs_nj_2022_subject_raw.csv
    ensure_dirs()
    url = (
        f"https://api.census.gov/data/{year}/acs/acs5/subject"
        "?get=NAME,S0101_C01_001E,S1901_C01_001E,S2502_C03_001E,S0801_C01_049E"
        "&for=county:*&in=state:34"
        f"&key={CENSUS_API_KEY}"
    )
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    payload = resp.json()
    header, rows = payload[0], payload[1:]
    df = pd.DataFrame(rows, columns=header)
    out_path = RAW_DIR / f"acs_nj_{year}_subject_raw.csv"
    df.to_csv(out_path, index=False)
    print(f"Saved ACS subject slice to {out_path} rows={len(df)} cols={len(df.columns)}")
    return out_path


def fetch_gazetteer(year: int = 2021) -> Path:
    """
    Download county Gazetteer to get land area for density calculations.
    """
    ensure_dirs()
    urls = [
        f"https://www2.census.gov/geo/docs/maps-data/data/gazetteer/{year}_Gazetteer/{year}_Gaz_counties_national.zip",
        f"https://www2.census.gov/geo/docs/maps-data/data/gazetteer/{year}_Gaz_counties_national.zip",
    ]
    resp = None
    for candidate in urls:
        try:
            resp = requests.get(candidate, timeout=60)
            resp.raise_for_status()
            break
        except Exception:
            resp = None
            continue
    if resp is None:
        raise RuntimeError("Could not download Gazetteer from known URLs")
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        raw_bytes = zf.read(f"{year}_Gaz_counties_national.txt")
    out_path = RAW_DIR / f"{year}_Gaz_counties_national.txt"
    out_path.write_bytes(raw_bytes)
    print(f"Saved Gazetteer to {out_path}")
    return out_path


def process_census_features(year: int = 2021) -> Path:
    """
    Merge ACS subject data with land area and compute population density.
    Saves a tidy county feature file for NJ.
    """
    ensure_dirs()
    raw_subject = RAW_DIR / f"acs_nj_{year}_subject_raw.csv"
    gaz_txt = RAW_DIR / f"{year}_Gaz_counties_national.txt"
    if not raw_subject.exists():
        raise FileNotFoundError("Run fetch_census_subject_tables first")
    if not gaz_txt.exists():
        raise FileNotFoundError("Run fetch_gazetteer first")

    acs = pd.read_csv(raw_subject, dtype={"state": str, "county": str})
    acs["GEOID"] = acs["state"].str.zfill(2) + acs["county"].str.zfill(3)
    acs = acs.rename(
        columns={
            "NAME": "name",
            "S0101_C01_001E": "population",
            "S1901_C01_001E": "median_household_income",
            "S2502_C03_001E": "renter_occupied_pct",
            "S0801_C01_049E": "mean_travel_time_to_work_minutes",
        }
    )
    numeric_cols = [
        "population",
        "median_household_income",
        "renter_occupied_pct",
        "mean_travel_time_to_work_minutes",
    ]
    for col in numeric_cols:
        acs[col] = pd.to_numeric(acs[col], errors="coerce")

    gaz = pd.read_csv(
        gaz_txt,
        sep="\t",
        dtype={"GEOID": str},
        usecols=["GEOID", "USPS", "ALAND_SQMI"],
    )
    gaz = gaz[gaz["USPS"] == "NJ"].rename(columns={"ALAND_SQMI": "land_area_sqmi"})
    merged = acs.merge(gaz[["GEOID", "land_area_sqmi"]], on="GEOID", how="left")
    merged["pop_density_per_sqmi"] = merged["population"] / merged["land_area_sqmi"]

    keep_cols = [
        "GEOID",
        "name",
        "population",
        "median_household_income",
        "renter_occupied_pct",
        "mean_travel_time_to_work_minutes",
        "land_area_sqmi",
        "pop_density_per_sqmi",
    ]
    merged = merged[keep_cols]

    out_path = PROCESSED_DIR / "acs_nj_counties.csv"
    merged.to_csv(out_path, index=False)
    print(f"Saved cleaned ACS county features to {out_path} rows={len(merged)}")
    return out_path


def main() -> None:
    print("Fetching NREL chargers for NJ...")
    fetch_nrel_chargers()
    year = 2022
    print(f"Fetching ACS {year} subject tables for NJ...")
    fetch_census_subject_tables(year=year)
    print(f"Fetching county Gazetteer {year}...")
    fetch_gazetteer(year=year)
    print("Processing ACS features...")
    process_census_features(year=year)


if __name__ == "__main__":
    main()
