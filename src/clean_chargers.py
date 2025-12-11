from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_PATH = BASE_DIR / "data" / "raw" / "alt_fuel_stations_nj_raw.csv"
COUNTY_SHP = BASE_DIR / "data" / "raw" / "cb_2022_us_county_500k" / "cb_2022_us_county_500k.shp"
OUT_PATH = BASE_DIR / "data" / "processed" / "chargers_nj_2022_by_county.csv"


def clean_chargers_2022() -> None:
    df = pd.read_csv(RAW_PATH)
    df["Date Last Confirmed"] = pd.to_datetime(df["Date Last Confirmed"], errors="coerce")
    df["Open Date"] = pd.to_datetime(df["Open Date"], errors="coerce")
    cutoff = pd.Timestamp("2022-12-31")
    df = df[df["Date Last Confirmed"] <= cutoff]
    df = df[df["Status Code"].isin(["E"])]
    df = df[df["State"] == "NJ"]
    df = df.dropna(subset=["Latitude", "Longitude"])
    gdf = gpd.GeoDataFrame(
        df,
        geometry=[Point(xy) for xy in zip(df["Longitude"], df["Latitude"])],
        crs="EPSG:4326",
    )
    counties = gpd.read_file(COUNTY_SHP).to_crs(epsg=4326)
    counties = counties[counties["STATEFP"] == "34"]
    gdf = gpd.sjoin(gdf, counties[["NAME", "GEOID", "geometry"]], how="left", predicate="within")
    gdf = gdf.rename(columns={"NAME": "county"})
    agg = (
        gdf.groupby("county")
        .agg(
            stations=("Station Name", "count"),
            level1_ports=("EV Level1 EVSE Num", "sum"),
            level2_ports=("EV Level2 EVSE Num", "sum"),
            dcfc_ports=("EV DC Fast Count", "sum"),
            last_confirmed_max=("Date Last Confirmed", "max"),
        )
        .reset_index()
    )
    agg.to_csv(OUT_PATH, index=False)
    print(f"Saved cleaned chargers to {OUT_PATH} rows={len(agg)}")


if __name__ == "__main__":
    clean_chargers_2022()
