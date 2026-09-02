# Power BI Setup Guide — Hospital Analytics (Real Data Edition)

This project's Power BI report connects to the **same** `HospitalAnalyticsDB`
database that the Python scripts (`../python/`) also read from — not to a
separate copy of the data. The data itself is a real, de-identified sample
of the UCI "Diabetes 130-US Hospitals 1999-2008" dataset — see `../README.md`
for the full explanation and column mapping.

## 1. Connect to the data source

1. Open Power BI Desktop.
2. `Get Data` → `SQL Server database`.
3. Server: `localhost` (or your machine name)
4. Database: `HospitalAnalyticsDB`
5. Select `dbo.Hospital_Raw` → **Transform Data**.

## 2. Clean the data in Power Query

Apply the same rules implemented in `../python/clean_data.py`, so both the
Python analysis and the Power BI report always agree on the same numbers:

- Treat `"?"`, `"Not Recorded"`, `"Not Available"`, `"Not Mapped"`, and
  `"Unknown/Invalid"` as null across the text columns (these are the
  source system's own missing-value codes)
- Convert `Length_of_Stay_Days`, `Num_Medications`, `Num_Procedures`,
  `Num_Lab_Procedures`, `Number_of_Diagnoses`, and the visit-count columns
  to whole numbers
- Filter: `Length_of_Stay_Days` between 1–14 (the dataset's own inclusion
  criteria), `Num_Medications` between 0–100, `Readmitted` in {NO, <30, >30}
- Keep only `Gender` = Male/Female (drop the rare "Unknown/Invalid" code)
- Remove duplicate `Encounter_ID` values
- Replace blank `Medical_Specialty` / `Payer_Code` with `"Not Recorded"`
  rather than dropping the row — a large share of real encounters
  genuinely don't have these recorded, which is itself worth showing

## 3. Data model

A single flat table is enough for this project size, but you can split into
a Fact table (`Encounters`: Length_of_Stay_Days, Num_Medications,
Number_of_Diagnoses, Readmitted) and Dimension tables (`Patients`,
`Medical_Specialty`, `Admission_Type`, `Age_Group`) if you want to
demonstrate star-schema modeling.

## 4. DAX measures

```DAX
Total Encounters = DISTINCTCOUNT(Hospital_Raw[Encounter_ID])
Avg Length of Stay = AVERAGE(Hospital_Raw[Length_of_Stay_Days])
Avg Medications = AVERAGE(Hospital_Raw[Num_Medications])
Avg Diagnoses = AVERAGE(Hospital_Raw[Number_of_Diagnoses])
Readmitted <30 Rate =
DIVIDE(
    CALCULATE(COUNTROWS(Hospital_Raw), Hospital_Raw[Readmitted] = "<30"),
    [Total Encounters]
)
```

These match exactly what `../python/analyze.py` prints, so you can
cross-check the Power BI card values against the Python console output.

## 5. Apply the theme

`View` → `Themes` → `Browse for themes...` → select
`Black_SkyBlue_PowerBI_Theme.json` in this folder.

## 6. Build the visuals

Match the layout in `../dashboard_preview/Hospital_Overview_Dashboard.html`:
- KPI cards: Total Encounters, Avg. Length of Stay, Avg. Medications,
  Avg. Diagnoses, Readmitted <30 Days Rate
- Slicer: Age Group
- Column chart: Patients by Gender
- Bar chart: Encounters by Medical Specialty (Top 8)
- Line chart: Encounters by Age Group
- Donut chart: Readmission breakdown (Not Readmitted / <30 days / >30 days)
- Bar chart: Encounters by Admission Type

## 7. Refresh

Any time new rows are added to `dbo.Hospital_Raw` in SQL Server, click
**Refresh** in Power BI — no need to re-import anything manually.
