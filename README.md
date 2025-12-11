# EV Charging Needs Analysis (CS439 Project)

I keep everything in Python and MySQL. Data lives under `data/` and notebooks under `notebooks/`.

## Setup
1) Install Python 3.12+ (It's what I used but other versions may work) and packages: pandas, seaborn, scikit-learn, geopandas, pymysql.
2) Set API keys in env before downloads:
   - `export NREL_API_KEY=...`
   - `export CENSUS_API_KEY=...`
3) Fetch data (optional if you keep the processed CSVs):
   - `python3 src/download_data.py`
   - `python3 src/clean_chargers.py`
   - `python3 src/build_state_features.py`

## Notebooks
- `01_nj_county.ipynb` shows the NJ county attempt (sparse data, negative R²).
- `02_state_model.ipynb` trains the state-level model (2022).
- `03_sql_demo.ipynb` queries the MySQL table.

## MySQL
- Load table from project root:
  - `MYSQL_PWD='your_pw' mysql -uroot -h127.0.0.1 -P3306 --local-infile=1 < sql/mysql_setup.sql`
- Query example:
  - `MYSQL_PWD='your_pw' mysql -uroot -h127.0.0.1 -P3306 -D ev_project -e "SELECT State, chargers_per_100k, stations FROM state_features_2022 ORDER BY chargers_per_100k DESC LIMIT 10;"`

## Notes
- Keys are not hardcoded; set env vars.
- Paths are relative to repo root.
- State model (2022): Linear RMSE ~0.317, R² ~0.657; RF RMSE ~0.326, R² ~0.638.
- NJ model kept to show thinking process: Linear R² ~ -475 (too sparse to use).
