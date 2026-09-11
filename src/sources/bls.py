import os

import requests
import pandas as pd
from dotenv import load_dotenv

import json
from pathlib import Path

load_dotenv()

BLS_API_KEY = os.getenv("BLS_API_KEY")
BLS_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

def fetch_bls_series(series_id, start_year, end_year):
    """Fetch a BLS series for the requested range of years."""

    payload = {
        "seriesid": [series_id],
        "startyear": str(start_year),
        "endyear": str(end_year),
        "registrationkey": BLS_API_KEY,
    }

    response = requests.post(
        BLS_URL,
        json=payload,
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()

    # Create the raw BLS folder.
    raw_dir = Path(__file__).resolve().parents[2] / "data" / "raw" / "bls"
    raw_dir.mkdir(parents=True, exist_ok=True)

    # Include the series and requested years in the filename.
    raw_path = raw_dir / f"{series_id}_{start_year}_{end_year}.json"

    with raw_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    if data.get("status") != "REQUEST_SUCCEEDED":
        raise ValueError(f"BLS API request failed: {data.get('message')}")

    series = data["Results"]["series"][0]
    observations = series["data"]

    df = pd.DataFrame(observations)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    df = df[df["period"].isin([f"M{i:02d}" for i in range(1, 13)])].copy()

    df["date"] = pd.to_datetime(
        df["year"] + "-" + df["period"].str[1:] + "-01"
    )
    df["series_id"] = series_id

    df = df[["date", "value", "series_id"]]
    df = df.sort_values("date").reset_index(drop=True)

    return df


if __name__ == "__main__":
    df = fetch_bls_series("CUUR0000SA0", 2023, 2025)
    print(df.head().to_string(index=False))