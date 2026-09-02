"""
main.py
-------
Runs the whole pipeline end-to-end from VS Code with a single command:

    python main.py

1) extract_from_sql.py  -> pulls raw data from SQL Server (or CSV fallback)
2) clean_data.py        -> applies the same cleaning rules as Power Query
3) analyze.py            -> prints KPIs/insights and saves charts

This is the "VS Code" leg of the project: the same dataset that lives in
SQL Server (sql/) and that Power BI (powerbi/) visualizes is also fully
scriptable and analyzable here in Python.
"""

import subprocess
import sys

STEPS = ["extract_from_sql.py", "clean_data.py", "analyze.py"]


def run():
    for step in STEPS:
        print(f"\n{'='*60}\nRunning {step}\n{'='*60}")
        result = subprocess.run([sys.executable, step])
        if result.returncode != 0:
            print(f"[FAIL] {step} exited with an error. Stopping pipeline.")
            sys.exit(result.returncode)
    print(f"\n{'='*60}\nPipeline complete. See hospital_clean.csv and charts/\n{'='*60}")


if __name__ == "__main__":
    run()
