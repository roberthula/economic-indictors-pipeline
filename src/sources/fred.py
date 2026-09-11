import os

import pandas as pd
import requests
from dotenv import load_dotenv
import json
from pathlib import Path


load_dotenv()

FRED_API_KEY = os.getenv("FRED_API_KEY")
if not FRED_API_KEY:
    raise RuntimeError("FRED_API_KEY is not set")
FRED_URL = "https://api.stlouisfed.org/fred/series/observations"


def fetch_fred_series(series_id):
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json"
    }

    try:
        response = requests.get(FRED_URL, params=params, timeout=60)
        response.raise_for_status()

    except requests.exceptions.Timeout:
        raise RuntimeError("FRED request timed out")

    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"FRED returned an HTTP error: {e}")

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to retrieve FRED data: {e}")

    data = response.json()

    # Locate the project's data/raw/fred folder.
    raw_dir = Path(__file__).resolve().parents[2] / "data" / "raw" / "fred"
    raw_dir.mkdir(parents=True, exist_ok=True)

    # Save the original response before transforming it.
    raw_path = raw_dir / f"{series_id}.json"

    with raw_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    df = pd.DataFrame(data["observations"])
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    df["series_id"] = series_id
    df = df[["date", "series_id", "value"]]

    return df

def fetch_fred_series_list(series_ids):
    if not series_ids:
        raise ValueError("series_ids cannot be empty")

    dataframes = []

    for series_id in series_ids:
        df = fetch_fred_series(series_id)
        dataframes.append(df)

    combined_df = pd.concat(dataframes, ignore_index=True)

    return combined_df


 

 