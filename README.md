# Automated EV Infrastructure ETL Pipeline

## Project Overview
This project demonstrates an end to end data acquisition and ETL pipeline designed to analyze public electric vehicle infrastructure. The primary engineering challenge was extracting unstructured data via federal APIs, profiling the data for quality issues, and transforming it into a clean dimensional format loaded into MySQL for geospatial visualization.

## ETL Architecture & Data Processing

### 1. Data Extraction (Python & APIs)
* Engineered automated Python scripts (`src/download_data.py`) to extract raw charging station data and electric vehicle registration records securely using the NREL and US Census APIs.
* Collected underlying demographic features to provide necessary context for infrastructure density.

### 2. Data Transformation & Profiling
* Data Quality Control: Performed extensive data profiling (`src/clean_chargers.py`) to identify missing values and standardize inconsistent geographic naming conventions.
* Feature Engineering: Engineered new geospatial variables (`src/build_state_features.py`) using Pandas and GeoPandas to normalize charging station availability against local population density.

### 3. Load & Database Management (MySQL)
* Engineered a local relational database structure to house the cleaned analytical tables.
* Executed automated bulk load operations to move transformed data into MySQL for final query execution and dashboard visualization.

## Technical Setup & Deployment

1. Install required Python packages: pandas, seaborn, scikit learn, geopandas, pymysql.
2. Set API keys in your environment variables before initiating the download scripts:
    export NREL_API_KEY='your_key'
    export CENSUS_API_KEY='your_key'
3. Execute the ETL pipeline:
    python3 src/download_data.py
    python3 src/clean_chargers.py
    python3 src/build_state_features.py
4. Load the transformed data into MySQL:
    MYSQL_PWD='your_pw' mysql -uroot -h127.0.0.1 -P3306 --local-infile=1 < sql/mysql_setup.sql

## Repository Contents
* /src/: The core Python ETL scripts handling data extraction, cleaning, and transformation.
* /sql/: The database setup scripts and load commands.
* /notebooks/: Exploratory data analysis, regression modeling, and SQL query demonstrations.
* infrastructure_analysis_report.pdf: The comprehensive report detailing the data environment constraints, profiling methodology, and final geospatial insights.
