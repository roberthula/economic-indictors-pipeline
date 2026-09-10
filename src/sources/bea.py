import os

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

BEA_API_KEY = os.getenv("BEA_API_KEY")
BEA_API_URL = "https://apps.bea.gov/api/data/"

def fetch_bea_table(table_name, year, frequency="Q"):
    """Fetch a table from BEA's National Income and Product Accounts (NIPA) dataset."""

    if frequency != "Q":
        raise ValueError("This function currently supports quarterly data only.")

    params = {
        "UserID": BEA_API_KEY,
        "method": "GetData",
        "datasetname": "NIPA",
        "TableName": table_name,
        "Frequency": frequency,
        "Year": str(year),
        "ResultFormat": "json"
    }
    response = requests.get(
        BEA_API_URL,
        params=params,
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()

    results = data["BEAAPI"]["Results"]

    if "Error" in results:
        error = results["Error"]
        raise ValueError(
            f"BEA API request failed: {error.get('APIErrorDescription', error)}"
        )



    observations = results["Data"]
    df = pd.DataFrame(observations)

    df["value"] = pd.to_numeric(
        df["DataValue"].str.replace(",", "", regex=False),
        errors="coerce",
    )

    df["date"] = pd.PeriodIndex(
        df["TimePeriod"], freq="Q"
    ).to_timestamp()

    df = df.rename(columns={
        "SeriesCode": "series_id",
        "LineDescription": "description",
        "CL_UNIT": "unit",
        "UNIT_MULT": "unit_multiplier",
        "TableName": "table_name",
    })

    df = df[[
        "date", "value", "series_id", "description",
        "unit", "unit_multiplier", "table_name",
    ]]

    df = df.sort_values(
        ["series_id", "date"]
    ).reset_index(drop=True)

    return df

if __name__ == "__main__":
    df = fetch_bea_table("T10101", 2025)
    print(df.head().to_string(index=False))