from src.sources.fred import fetch_fred_series
from src.sources.bls import fetch_bls_series
from src.sources.bea import fetch_bea_table

import pandas as pd
from pathlib import Path
 

def main():
    # Fetch the federal funds rate from FRED.
    fred_df = fetch_fred_series("DFF")

    # Display the first five rows.
    print(fred_df.head())

        # Fetch the U.S. unemployment rate from BLS.
    bls_df = fetch_bls_series("LNS14000000", 2024, 2025)

    print(bls_df.head())

    # Fetch quarterly GDP growth data from BEA.
    bea_df = fetch_bea_table("T10101", "2024", frequency="Q")

    print(bea_df.head())

        # Stack the observations from all three sources.
    combined_df = pd.concat(
        [
            fred_df.assign(source="FRED"),
            bls_df.assign(source="BLS"),
            bea_df.assign(source="BEA"),
        ],
        ignore_index=True,
    )

    print(combined_df.groupby("source").size())

    # Create the processed output folder.
    processed_dir = Path(__file__).resolve().parent / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Save the cleaned, combined data from all three sources.
    output_path = processed_dir / "economic_indicators.csv"
    combined_df.to_csv(output_path, index=False)

    print(f"Saved processed data to {output_path}")


if __name__ == "__main__":
    main()
