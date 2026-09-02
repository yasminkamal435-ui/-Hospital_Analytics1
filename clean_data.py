"""
clean_data.py
-------------
Step 2 of the pipeline: clean the raw hospital encounter data.
Same cleaning philosophy as the original project (mirrors the Power
Query steps in Power BI so the SQL -> Python -> Power BI stack all
agree on the same definition of "clean data") — but rewritten for the
REAL dataset's actual quality issues instead of invented ones:

  - missing values are coded as "?" / "Not Recorded" / "Not Available"
    / "Not Mapped" / "Unknown/Invalid" in the source, not blank
  - a handful of rows have physiologically invalid stay lengths
  - Medical_Specialty and Payer_Code are unrecorded for a large share
    of real encounters (this is a genuine property of the source data,
    not a data-quality bug to "fix")

Run from VS Code:
    python clean_data.py
(uses hospital_extracted.csv produced by extract_from_sql.py; falls
back to the raw data file directly if that hasn't been run yet)
"""

import os
import numpy as np
import pandas as pd
import config

MISSING_TOKENS = {"?", "not recorded", "not available", "not mapped", "unknown/invalid", "null", "nan", ""}

VALID_READMITTED = {"NO", "<30", ">30"}


def _norm_missing(x):
    if pd.isna(x):
        return np.nan
    s = str(x).strip()
    if s.lower() in MISSING_TOKENS:
        return np.nan
    return s


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    text_cols = [
        "Race", "Gender", "Age_Group", "Admission_Type", "Admission_Source",
        "Discharge_Status", "Medical_Specialty", "Payer_Code",
        "Primary_Diagnosis_Code", "Max_Glucose_Serum_Test", "A1C_Test_Result",
        "Diabetes_Medication_Prescribed", "Medication_Changed", "Readmitted",
    ]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].apply(_norm_missing)

    numeric_cols = [
        "Length_of_Stay_Days", "Num_Lab_Procedures", "Num_Procedures",
        "Num_Medications", "Prior_Outpatient_Visits", "Prior_Emergency_Visits",
        "Prior_Inpatient_Visits", "Number_of_Diagnoses",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # rule-based filters (mirrors Power Query steps)
    df = df[df["Length_of_Stay_Days"].between(1, 14)]              # dataset's own inclusion criteria
    df = df[df["Num_Medications"].between(0, 100)]
    df = df[df["Readmitted"].isin(VALID_READMITTED)]
    df = df.dropna(subset=["Gender", "Age_Group", "Admission_Type", "Readmitted"])
    df = df[df["Gender"].isin(["Male", "Female"])]                  # drop rare 'Unknown/Invalid' gender codes
    df = df.drop_duplicates(subset=["Encounter_ID"])

    # fields that are genuinely unrecorded for many real encounters —
    # keep them explicit rather than dropping the row
    for col in ["Medical_Specialty", "Payer_Code"]:
        if col in df.columns:
            df[col] = df[col].fillna("Not Recorded")

    return df.reset_index(drop=True)


if __name__ == "__main__":
    src = "hospital_extracted.csv" if os.path.exists("hospital_extracted.csv") else config.FALLBACK_CSV_PATH
    print(f"[INFO] Reading raw data from {src}")
    raw = pd.read_csv(src)
    print(f"[INFO] Raw rows: {len(raw)}")

    cleaned = clean(raw)
    print(f"[OK] Clean rows: {len(cleaned)} "
          f"({len(raw) - len(cleaned)} rows removed by cleaning rules)")

    cleaned.to_csv("hospital_clean.csv", index=False)
    print("[OK] Saved -> python/hospital_clean.csv")
