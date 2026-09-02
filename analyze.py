"""
analyze.py
----------
Step 3 of the pipeline: compute the same KPIs and breakdowns shown in
the Power BI dashboard, and save matplotlib charts as PNG files. Useful
for quick analysis directly in VS Code without opening Power BI at all,
and for validating that the Power BI numbers are correct.

Run from VS Code:
    python analyze.py
(uses hospital_clean.csv produced by clean_data.py)
"""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Black + sky-blue theme, matching the Power BI theme and HTML dashboard
BG = "#05070c"
PANEL = "#0b0f16"
SKY = "#38bdf8"
SKY_DARK = "#0ea5e9"
TEXT = "#f1f7fb"
GRID = "#16202c"

plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": PANEL,
    "axes.edgecolor": GRID, "axes.labelcolor": TEXT,
    "xtick.color": TEXT, "ytick.color": TEXT,
    "text.color": TEXT, "grid.color": GRID,
    "font.size": 10,
})

OUT_DIR = "charts"

AGE_ORDER = ["[0-10)", "[10-20)", "[20-30)", "[30-40)", "[40-50)",
             "[50-60)", "[60-70)", "[70-80)", "[80-90)", "[90-100)"]


def load_clean_data() -> pd.DataFrame:
    return pd.read_csv("hospital_clean.csv")


def print_kpis(df: pd.DataFrame):
    total_encounters = df["Encounter_ID"].nunique()
    avg_los = df["Length_of_Stay_Days"].mean()
    avg_meds = df["Num_Medications"].mean()
    avg_diag = df["Number_of_Diagnoses"].mean()
    readmit_30 = (df["Readmitted"] == "<30").sum() / len(df) * 100

    print("\n=== Hospital KPIs (real de-identified patient data) ===")
    print(f"Total Encounters     : {total_encounters:,}")
    print(f"Avg. Length of Stay  : {avg_los:.1f} days")
    print(f"Avg. Medications     : {avg_meds:.1f}")
    print(f"Avg. Diagnoses       : {avg_diag:.1f}")
    print(f"Readmitted <30 Days  : {readmit_30:.1f}%")


def chart_specialty_encounters(df: pd.DataFrame):
    spec = (df[df["Medical_Specialty"] != "Not Recorded"]
            ["Medical_Specialty"].value_counts().head(8))
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(spec.index[::-1], spec.values[::-1], color=SKY_DARK)
    ax.set_title("Encounters by Medical Specialty (Top 8)", color=TEXT)
    ax.set_xlabel("Encounters")
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/encounters_by_specialty.png", dpi=150, facecolor=BG)
    plt.close(fig)


def chart_age_distribution(df: pd.DataFrame):
    age = df["Age_Group"].value_counts().reindex(AGE_ORDER).fillna(0)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(age.index, age.values, color=SKY, linewidth=2, marker="o", markersize=4)
    ax.fill_between(age.index, age.values, color=SKY, alpha=0.15)
    ax.set_title("Encounters by Age Group", color=TEXT)
    ax.tick_params(axis="x", rotation=45, labelsize=8)
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/encounters_by_age_group.png", dpi=150, facecolor=BG)
    plt.close(fig)


def chart_readmission_status(df: pd.DataFrame):
    status = df["Readmitted"].map({
        "NO": "Not Readmitted", "<30": "Readmitted <30 Days", ">30": "Readmitted >30 Days",
    }).value_counts()
    colors = ["#38bdf8", "#0ea5e9", "#7dd3fc"]
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(status.values, labels=status.index, colors=colors[:len(status)],
           autopct="%1.1f%%", pctdistance=0.8, textprops={"color": TEXT},
           wedgeprops={"width": 0.4, "edgecolor": BG})
    ax.set_title("Readmission Breakdown", color=TEXT)
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/readmission_status.png", dpi=150, facecolor=BG)
    plt.close(fig)


def chart_gender_split(df: pd.DataFrame):
    gender = df["Gender"].value_counts()
    fig, ax = plt.subplots(figsize=(5, 4.5))
    ax.bar(gender.index, gender.values, color=[SKY_DARK, SKY])
    ax.set_title("Patients by Gender", color=TEXT)
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/patients_by_gender.png", dpi=150, facecolor=BG)
    plt.close(fig)


def print_insights(df: pd.DataFrame):
    spec_counts = (df[df["Medical_Specialty"] != "Not Recorded"]
                   ["Medical_Specialty"].value_counts())
    top_spec = spec_counts.index[0]

    age_counts = df["Age_Group"].value_counts().reindex(AGE_ORDER).fillna(0)
    peak_age = age_counts.idxmax()

    readmit_rate = (df["Readmitted"] != "NO").sum() / len(df) * 100
    admit_counts = df["Admission_Type"].value_counts()
    top_admit = admit_counts.index[0]

    print("\n=== Business Insights ===")
    print(f"- {top_spec} accounts for the largest share of recorded encounters by specialty.")
    print(f"- The {peak_age} age bracket has the highest encounter volume.")
    print(f"- {readmit_rate:.1f}% of encounters resulted in a readmission (either <30 or >30 days).")
    print(f"- {top_admit} is the most common admission type.")
    print("- Recommendation: prioritize discharge-planning review for the peak age bracket")
    print("  and the specialties with the highest <30-day readmission share, since early")
    print("  readmissions are a key cost and quality-of-care indicator for hospitals.")


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    df = load_clean_data()

    print_kpis(df)
    chart_specialty_encounters(df)
    chart_age_distribution(df)
    chart_readmission_status(df)
    chart_gender_split(df)
    print_insights(df)

    print(f"\n[OK] Charts saved to python/{OUT_DIR}/")
