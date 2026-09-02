<#
setup_all.ps1
-------------
Run this ONCE from PowerShell (on Windows, after installing SQL Server
Express + command line tools) to auto-wire the whole project together:

  1. Auto-detects your local SQL Server instance name
  2. Creates HospitalAnalyticsDB + dbo.Hospital_Raw
  3. Imports data/Hospital_Raw_Data.csv into it (using bcp, which runs
     as YOU, so it avoids the classic "BULK INSERT access denied" issue)
  4. Writes the detected server name into connection.txt — the single
     file that python/config.py reads automatically, so Python is wired
     up with zero manual editing.
  5. Prints the exact Server/Database values to paste into Power BI
     Desktop (Get Data -> SQL Server database) — that one paste is the
     only manual step left, because Power BI Desktop is a GUI app that
     can't be scripted from the command line.

Usage (from the sql/ folder):
    powershell -ExecutionPolicy Bypass -File setup_all.ps1
#>

param(
    [string]$CsvPath = "..\data\Hospital_Raw_Data.csv",
    [string]$Database = "HospitalAnalyticsDB"
)

Write-Host "== Hospital Analytics Project - Auto Setup ==" -ForegroundColor Cyan

# ---------------------------------------------------------------
# 1) Auto-detect a local SQL Server instance
# ---------------------------------------------------------------
$detected = $null
$instanceKey = "HKLM:\SOFTWARE\Microsoft\Microsoft SQL Server\Instance Names\SQL"

if (Test-Path $instanceKey) {
    $props = Get-ItemProperty -Path $instanceKey -ErrorAction SilentlyContinue
    if ($props) {
        $names = $props.PSObject.Properties |
                 Where-Object { $_.Name -notmatch '^PS' } |
                 Select-Object -ExpandProperty Name
        if ($names.Count -gt 0) {
            $first = $names[0]
            if ($first -eq "MSSQLSERVER") {
                $detected = $env:COMPUTERNAME
            } else {
                $detected = "$env:COMPUTERNAME\$first"
            }
        }
    }
}

if (-not $detected) {
    Write-Host "Could not auto-detect a local SQL Server instance." -ForegroundColor Yellow
    $detected = Read-Host "Enter your server name manually (e.g. localhost\SQLEXPRESS)"
}

Write-Host "Using SQL Server instance: $detected" -ForegroundColor Green

# ---------------------------------------------------------------
# 2) Create database + table
# ---------------------------------------------------------------
Write-Host "`nCreating database and table..." -ForegroundColor Cyan

sqlcmd -S $detected -Q "IF DB_ID('$Database') IS NULL CREATE DATABASE $Database;"

$createTableSql = @"
IF OBJECT_ID('dbo.Hospital_Raw','U') IS NOT NULL DROP TABLE dbo.Hospital_Raw;
CREATE TABLE dbo.Hospital_Raw (
    Row_ID INT, Encounter_ID BIGINT, Patient_Number BIGINT, Race NVARCHAR(30),
    Gender NVARCHAR(20), Age_Group NVARCHAR(15), Admission_Type NVARCHAR(30),
    Admission_Source NVARCHAR(60), Discharge_Status NVARCHAR(60),
    Medical_Specialty NVARCHAR(60), Payer_Code NVARCHAR(20),
    Length_of_Stay_Days INT, Num_Lab_Procedures INT, Num_Procedures INT,
    Num_Medications INT, Prior_Outpatient_Visits INT, Prior_Emergency_Visits INT,
    Prior_Inpatient_Visits INT, Primary_Diagnosis_Code NVARCHAR(20),
    Number_of_Diagnoses INT, Max_Glucose_Serum_Test NVARCHAR(10),
    A1C_Test_Result NVARCHAR(10), Diabetes_Medication_Prescribed NVARCHAR(5),
    Medication_Changed NVARCHAR(5), Readmitted NVARCHAR(5)
);
"@
sqlcmd -S $detected -d $Database -Q $createTableSql

# ---------------------------------------------------------------
# 3) Import the CSV using bcp (runs as the current user -> no
#    service-account file permission headaches like BULK INSERT)
# ---------------------------------------------------------------
Write-Host "`nImporting $CsvPath ..." -ForegroundColor Cyan
bcp dbo.Hospital_Raw in $CsvPath -S $detected -d $Database -c -t"," -r"\n" -F 2 -C 65001 -T

# ---------------------------------------------------------------
# 4) Write connection.txt — the single file that links SQL Server
#    to the Python side automatically (config.py reads this)
# ---------------------------------------------------------------
$connFile = "..\connection.txt"
"$detected`n$Database" | Out-File -Encoding utf8 $connFile
Write-Host "`nSaved connection info to $connFile" -ForegroundColor Green

# ---------------------------------------------------------------
# 5) Summary
# ---------------------------------------------------------------
Write-Host "`n== Setup complete ==" -ForegroundColor Cyan
Write-Host "Server:   $detected"
Write-Host "Database: $Database"
Write-Host ""
Write-Host "Python side: already wired up automatically via connection.txt." -ForegroundColor Green
Write-Host "Just run:  cd ..\python  &&  pip install -r requirements.txt  &&  python main.py"
Write-Host ""
Write-Host "Power BI side: paste these two values into Get Data -> SQL Server database:" -ForegroundColor Yellow
Write-Host "  Server:   $detected"
Write-Host "  Database: $Database"
