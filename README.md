# Hospital Analytics — Integrated Data Project (Real Data Edition)

A complete data analytics project with **four connected pieces**, all
working on the exact same dataset:

| # | Piece | Tool | Folder |
|---|-------|------|--------|
| 1 | The data | CSV (source of truth for import) | `data/` |
| 2 | The database | SQL Server | `sql/` |
| 3 | The code | Python (open in VS Code) | `python/` |
| 4 | The dashboard | Power BI | `powerbi/` + `dashboard_preview/` |

## About the data — this is REAL, not simulated

This version replaces the original mock/simulated dataset with a genuine,
real, publicly available hospital dataset:

> **"Diabetes 130-US Hospitals for Years 1999–2008"** (Strack, DeShazo,
> Gennings, et al., 2014) — UCI Machine Learning Repository, licensed
> **CC BY 4.0**. 101,766 real, de-identified inpatient encounters from
> **130 real US hospitals and integrated delivery networks**.
> Source: <https://archive.ics.uci.edu/dataset/296>

`data/Hospital_Raw_Data.csv` contains an **8,281-row reproducible random
sample** of that dataset (`random_state=42`), kept at roughly the same
scale as the original mock version so every downstream script, SQL table,
and dashboard still works the same way.

### Why the columns changed

The original mock version had `Patient_Name`, `Doctor_Name`, `Bill_Amount`,
`Room_Type`, `Bed_Number`, `City`, and `Insurance_Provider`. **No real,
legally published hospital dataset contains these** — patient names,
physician identities, exact billing, and room/bed assignments are
Protected Health Information (PHI). Publishing them openly would violate
patient privacy law in every country that regulates health data (HIPAA in
the US, and equivalents elsewhere). Any dataset that *does* claim to have
"real" data with those fields is either not actually real, or not
legally shared.

What real open hospital data *does* publish — and what this project now
uses — is de-identified clinical/administrative detail: demographics
(race, gender, age bracket), admission type/source, discharge
disposition, medical specialty, length of stay, lab/procedure/medication
counts, diagnosis codes, and readmission outcome. See the column mapping
below.

| Original (mock) column | Real-data replacement | Notes |
|---|---|---|
| Patient_ID | `Encounter_ID`, `Patient_Number` | Real system-generated IDs |
| Patient_Name | *(removed)* | PHI — never published |
| City | *(removed)* | Not published at patient level |
| Department | `Medical_Specialty` | Specialty of the admitting physician |
| Doctor_Name | *(removed)* | PHI — never published |
| Diagnosis | `Primary_Diagnosis_Code` | Real ICD-9 code |
| Admission_Type / Date | `Admission_Type`, `Admission_Source` | Real categorical codes |
| Discharge_Date | *(removed — not published)* | Only `Length_of_Stay_Days` is available |
| Length_of_Stay_Days | `Length_of_Stay_Days` | Same concept, real values (1–14 days) |
| Room_Type / Bed_Number | *(removed)* | PHI-adjacent, never published |
| Insurance_Provider | `Payer_Code` | Real payer code, often unrecorded (`Not Recorded`) |
| Bill_Amount | *(removed)* | PHI — never published in open data |
| Discharge_Status | `Discharge_Status`, `Readmitted` | Real discharge disposition + 30/>30-day readmission flag |
| Patient_Rating | *(removed — doesn't exist in real records)* | |

## Architecture — how they connect

```
data/Hospital_Raw_Data.csv
        │
        │  sql/setup_all.ps1  (ONE command, auto-detects your SQL Server
        │  instance, creates the DB + table, imports the CSV)
        ▼
SQL Server: HospitalAnalyticsDB.dbo.Hospital_Raw   <-- single source of truth
        │
        │  setup_all.ps1 also writes connection.txt
        ▼
connection.txt   <-- the ONE file that links everything together
        │
        ├─────────────────────┐
        ▼                      ▼
python/config.py         Power BI Desktop
(reads it automatically,   (paste Server/Database
 zero manual editing)       shown at the end of
        │                    setup_all.ps1 — the
        ▼                    only manual step left,
python/main.py               since it's a GUI app)
```

`connection.txt` is the single link between all three tools: run
`sql/setup_all.ps1` once and it writes the correct server name into that
file automatically. Every Python script reads it with no editing needed.
Power BI Desktop is a GUI application with no command line, so pasting the
server/database into `Get Data → SQL Server database` is the one manual
step that genuinely can't be scripted away — `setup_all.ps1` prints those
exact two values at the end so it's a copy-paste, not something you type
from memory.

## Quick start

### 1. One-command SQL setup (Windows PowerShell)
```powershell
cd sql
powershell -ExecutionPolicy Bypass -File setup_all.ps1
```
This detects your local SQL Server instance, creates `HospitalAnalyticsDB`
+ `dbo.Hospital_Raw`, imports `data/Hospital_Raw_Data.csv`, and writes
`connection.txt` — wiring up the Python side automatically. At the end it
prints the Server/Database values you'll paste into Power BI.

*(Prefer doing it by hand instead? `sql/setup_hospital_database.sql` +
SSMS's Import Flat File wizard works too — see that file's comments.)*

### 2. Run the Python pipeline (open `python/` in VS Code)
```bash
cd python
pip install -r requirements.txt
python main.py
```
No config editing needed — `config.py` reads `connection.txt` automatically.
This pulls the data from SQL Server, cleans it, prints KPIs + insights, and
saves charts to `python/charts/`.

### 3. Build the Power BI report
Open Power BI Desktop → `Get Data` → `SQL Server database` → paste the
Server and Database values printed by `setup_all.ps1`. Then follow
`powerbi/PowerBI_Setup_Guide.md` for the Power Query cleaning steps, DAX
measures, and the included black/sky-blue theme.

### 4. Preview the target design
`dashboard_preview/Hospital_Overview_Dashboard.html` — open it in any
browser for an interactive preview of what the finished Power BI report
should look like (same KPIs, same charts, same color palette, now driven
by the real sampled data). This is a visual reference, not a substitute
for the real Power BI file.

## Folder structure

```
Hospital_Analytics_Project/
├── README.md                          <- you are here
├── connection.txt                     <- the link file (auto-written by setup_all.ps1)
├── data/
│   └── Hospital_Raw_Data.csv          <- real, de-identified patient encounter data (sampled)
├── sql/
│   ├── setup_all.ps1                  <- ONE command: detects SQL Server,
│   │                                      creates DB, imports data, writes
│   │                                      connection.txt automatically
│   └── setup_hospital_database.sql    <- manual/SSMS alternative
├── python/                            <- open this folder in VS Code
│   ├── config.py                      <- auto-reads ../connection.txt
│   ├── extract_from_sql.py            <- step 1: pull data from SQL
│   ├── clean_data.py                  <- step 2: clean (mirrors Power Query)
│   ├── analyze.py                     <- step 3: KPIs, insights, charts
│   ├── main.py                        <- runs steps 1-3 in order
│   └── requirements.txt
├── powerbi/
│   ├── PowerBI_Setup_Guide.md         <- connection + DAX + theme steps
│   └── Black_SkyBlue_PowerBI_Theme.json
└── dashboard_preview/
    └── Hospital_Overview_Dashboard.html
```

## Why this matters for a portfolio / graduation project

This mirrors how real analytics teams work: one governed data source
(SQL Server), multiple tools reading from it (Python for ad-hoc analysis
and automation, Power BI for the polished stakeholder-facing dashboard),
instead of scattered spreadsheet copies that drift out of sync. Being able
to explain *why* the pieces connect this way — not just that they exist —
is exactly what stands out in interviews. Working with a real published
dataset (and being able to explain honestly what real open health data
can and can't contain) is itself a talking point worth having ready.

**Data source & license:** Strack B, DeShazo JP, Gennings C, et al.
(2014), *"Impact of HbA1c Measurement on Hospital Readmission Rates"*,
BioMed Research International. Dataset hosted at the UCI Machine Learning
Repository, CC BY 4.0. This project uses a random 8,281-row sample of the
original 101,766-row release; full column definitions are in the paper
and repository page linked above.
