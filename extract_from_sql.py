"""
extract_from_sql.py
--------------------
Step 1 of the pipeline: pull the raw (dirty) hospital data from the
SQL Server database built by sql/setup_hospital_database.sql.

Run from VS Code:
    python extract_from_sql.py

If SQL Server isn't reachable (e.g. you haven't set it up yet), this
script automatically falls back to reading data/Hospital_Raw_Data.csv
directly, so the rest of the pipeline still works end-to-end.
"""

import pandas as pd
import config


def extract() -> pd.DataFrame:
    config.print_active_config()
    try:
        from sqlalchemy import create_engine
        engine = create_engine(config.get_sqlalchemy_url())
        query = "SELECT * FROM dbo.Hospital_Raw"
        df = pd.read_sql(query, engine)
        print(f"[OK] Pulled {len(df)} rows from SQL Server "
              f"({config.SQL_SERVER}/{config.SQL_DATABASE}.dbo.Hospital_Raw)")
        return df
    except Exception as e:
        print(f"[WARN] Could not connect to SQL Server ({e}).")
        print(f"[INFO] Falling back to local file: {config.FALLBACK_CSV_PATH}")
        df = pd.read_csv(config.FALLBACK_CSV_PATH)
        print(f"[OK] Loaded {len(df)} rows from CSV fallback")
        return df


if __name__ == "__main__":
    df = extract()
    df.to_csv("hospital_extracted.csv", index=False)
    print("[OK] Saved -> python/hospital_extracted.csv")
    print(df.head())
