/* =====================================================================
   Hospital Analytics Project — SQL Server Setup Script
   Run this in SQL Server Management Studio (SSMS) or Azure Data Studio.
   Creates a REAL database + table that Power BI connects to via
   Get Data -> SQL Server (not a static file).

   DATA SOURCE: this version loads REAL, de-identified patient encounter
   data — "Diabetes 130-US Hospitals for Years 1999-2008" (Strack et al.,
   2014), UCI Machine Learning Repository, CC BY 4.0. 101,766 genuine
   inpatient encounters from 130 real US hospitals; this project uses an
   8,281-row reproducible sample of it (see data/Hospital_Raw_Data.csv).

   NOTE ON MISSING COLUMNS: the original mock version of this project had
   Patient_Name, Doctor_Name, Bill_Amount, Room_Type, Bed_Number and City.
   No legitimate real, publicly available hospital dataset contains those
   — patient names, physician identities, room/bed assignments and exact
   billing are Protected Health Information (PHI) and are never published
   in open data. Those columns are dropped here; the real schema below
   uses only fields that are actually published for real patients.
   ===================================================================== */

IF DB_ID('HospitalAnalyticsDB') IS NULL
BEGIN
    CREATE DATABASE HospitalAnalyticsDB;
END
GO

USE HospitalAnalyticsDB;
GO

-- Raw staging table — matches the columns in data/Hospital_Raw_Data.csv.
IF OBJECT_ID('dbo.Hospital_Raw', 'U') IS NOT NULL
    DROP TABLE dbo.Hospital_Raw;
GO

CREATE TABLE dbo.Hospital_Raw (
    Row_ID                          INT,
    Encounter_ID                    BIGINT,
    Patient_Number                  BIGINT,
    Race                            NVARCHAR(30),
    Gender                          NVARCHAR(20),
    Age_Group                       NVARCHAR(15),   -- e.g. '[60-70)'
    Admission_Type                  NVARCHAR(30),
    Admission_Source                NVARCHAR(60),
    Discharge_Status                NVARCHAR(60),
    Medical_Specialty               NVARCHAR(60),
    Payer_Code                      NVARCHAR(20),
    Length_of_Stay_Days             INT,
    Num_Lab_Procedures              INT,
    Num_Procedures                  INT,
    Num_Medications                 INT,
    Prior_Outpatient_Visits         INT,
    Prior_Emergency_Visits          INT,
    Prior_Inpatient_Visits          INT,
    Primary_Diagnosis_Code          NVARCHAR(20),
    Number_of_Diagnoses             INT,
    Max_Glucose_Serum_Test          NVARCHAR(10),
    A1C_Test_Result                 NVARCHAR(10),
    Diabetes_Medication_Prescribed  NVARCHAR(5),
    Medication_Changed              NVARCHAR(5),
    Readmitted                      NVARCHAR(5)     -- 'NO', '<30', '>30'
);
GO

/* =====================================================================
   Load the data — two options:

   OPTION A (recommended, no code):
     Right-click HospitalAnalyticsDB -> Tasks -> Import Flat File...
     Point it to "Hospital_Raw_Data.csv" and map it to dbo.Hospital_Raw.

   OPTION B (T-SQL BULK INSERT):
     1. Copy Hospital_Raw_Data.csv to a folder the SQL Server *service
        account* can read, e.g. C:\HospitalData\Hospital_Raw_Data.csv
     2. Update the FROM path below and run:
   ===================================================================== */

BULK INSERT dbo.Hospital_Raw
FROM 'C:\HospitalData\Hospital_Raw_Data.csv'   -- <-- change this path
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '0x0a',
    CODEPAGE = '65001',
    TABLOCK
);
GO

SELECT COUNT(*) AS row_count FROM dbo.Hospital_Raw;
SELECT TOP 20 * FROM dbo.Hospital_Raw;
GO

/* =====================================================================
   In Power BI Desktop:
     Get Data -> SQL Server database
     Server: localhost (or your machine name)
     Database: HospitalAnalyticsDB
     -> select dbo.Hospital_Raw -> Transform Data
     Apply the cleaning steps described in python/clean_data.py — Power
     Query and Python implement the same rules so both stacks agree.
   ===================================================================== */
