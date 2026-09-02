"""
config.py
---------
Central configuration for connecting to the SQL Server database created
by sql/setup_hospital_database.sql (or sql/setup_all.ps1).

This file auto-reads the server and database name from ../connection.txt
so you normally DON'T need to edit anything here by hand:

  - Run sql/setup_all.ps1 once (Windows PowerShell) -> it detects your
    SQL Server instance automatically and writes connection.txt for you.
  - Every script in this folder (extract_from_sql.py, main.py, etc.)
    then picks up the same server/database automatically.

If connection.txt doesn't exist yet, sensible defaults are used below,
and if SQL Server still can't be reached, the scripts fall back to
reading data directly from the CSV file so the pipeline still runs.
"""

import os

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_CONN_FILE = os.path.join(_THIS_DIR, "..", "connection.txt")

# ---- Defaults (used only if connection.txt is missing) ----
SQL_SERVER = "localhost\\SQLEXPRESS"
SQL_DATABASE = "HospitalAnalyticsDB"

if os.path.exists(_CONN_FILE):
    with open(_CONN_FILE, "r", encoding="utf-8") as f:
        _lines = [line.strip() for line in f if line.strip()]
    if len(_lines) >= 1:
        SQL_SERVER = _lines[0]
    if len(_lines) >= 2:
        SQL_DATABASE = _lines[1]

SQL_DRIVER = "ODBC Driver 17 for SQL Server"

# Set to True to use Windows Authentication (Trusted Connection) —
# this is what sql/setup_all.ps1 sets up by default.
# Set to False and fill in SQL_USERNAME / SQL_PASSWORD to use a SQL login.
USE_WINDOWS_AUTH = True
SQL_USERNAME = ""
SQL_PASSWORD = ""

def get_connection_string() -> str:
    """Builds an ODBC connection string for pyodbc / SQLAlchemy."""
    if USE_WINDOWS_AUTH:
        return (
            f"Driver={{{SQL_DRIVER}}};"
            f"Server={SQL_SERVER};"
            f"Database={SQL_DATABASE};"
            f"Trusted_Connection=yes;"
        )
    return (
        f"Driver={{{SQL_DRIVER}}};"
        f"Server={SQL_SERVER};"
        f"Database={SQL_DATABASE};"
        f"UID={SQL_USERNAME};"
        f"PWD={SQL_PASSWORD};"
    )

def get_sqlalchemy_url() -> str:
    """Builds a SQLAlchemy connection URL (used by pandas.read_sql)."""
    import urllib.parse
    params = urllib.parse.quote_plus(get_connection_string())
    return f"mssql+pyodbc:///?odbc_connect={params}"

def print_active_config():
    source = "connection.txt" if os.path.exists(_CONN_FILE) else "defaults (connection.txt not found)"
    print(f"[CONFIG] Server={SQL_SERVER}  Database={SQL_DATABASE}  (source: {source})")

# ---- Local file fallback ----
# If SQL Server isn't reachable, the scripts automatically fall back to
# reading directly from this CSV so you can still run the whole
# pipeline end-to-end. This is REAL de-identified patient data (UCI
# "Diabetes 130-US Hospitals 1999-2008", CC BY 4.0) — see README.md.
FALLBACK_CSV_PATH = "../data/Hospital_Raw_Data.csv"

if __name__ == "__main__":
    print_active_config()
