import pandas as pd
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
PROC = BASE / "data" / "processed"


STATE_ABBR = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "Puerto Rico": "PR",
}


def build_state_features() -> None:
    chargers = pd.read_csv(PROC / "chargers_us_2022_by_state.csv")
    acs = pd.read_csv(PROC / "acs_us_states_2022.csv")
    acs["State"] = acs["state_name"].map(STATE_ABBR)
    acs = acs.dropna(subset=["State"])
    merged = chargers.merge(acs, on="State", how="inner")
    merged["chargers_per_100k"] = merged["stations"] / (merged["population"] / 100000)
    out = PROC / "state_features_2022.csv"
    merged.to_csv(out, index=False)
    print(f"Saved {len(merged)} rows to {out}")


if __name__ == "__main__":
    build_state_features()
