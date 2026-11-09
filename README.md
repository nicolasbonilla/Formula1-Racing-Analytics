
%md

# 🏎️ F1 Race Analytics — Version 2.0  
### End‑to‑End Incremental Data Engineering Pipeline (Local Workspace Edition)

F1‑Race‑2.0 is a complete end‑to‑end data engineering and analytics system built using PySpark, Parquet, notebook‑driven transformations, and shell‑script orchestration.  
It mirrors a Databricks‑style Medallion Architecture but runs entirely on a local laptop workspace.

---

## 🎓 Data Management coursework (SRH, Winter 2026/27)

Group: **Chirag Adhikari, Manohar Zalki, Nicolas Bonilla** (joint work on every component).

The graded project lives in [`data_management_project/`](data_management_project/): a reproducible
pipeline that turns the Jolpica/Ergast archive into a quality-assessed, cleaned and FAIR-documented
dataset of every World Championship result 1950-2025 (25,873 rows, 29 quality issues, 55 validation
gates, 14 tests), plus a NetworkX team-mate graph and the interactive dashboard in [`dashboard/`](dashboard/).

| What | Where |
|---|---|
| Joint report (Word and PDF) | [`data_management_project/report/`](data_management_project/report/) |
| Presentation (PowerPoint, PDF, presenter script) | [`data_management_project/report/presentation/`](data_management_project/report/presentation/) |
| Q&A preparation and reflection drafts | [`data_management_project/report/`](data_management_project/report/) |
| Submission ZIP for the course portal | [`data_management_project/dist/`](data_management_project/dist/) |
| Cleaned dataset and metadata (DataCite, schema.org, PROV-O) | [`data_management_project/data/cleaned/`](data_management_project/data/cleaned/), [`data_management_project/outputs/component_a_fair/`](data_management_project/outputs/component_a_fair/) |
| Interactive dashboard (served zone of the pipeline) | [`dashboard/app.py`](dashboard/app.py), [`dashboard/static/`](dashboard/static/) |

Reproduce everything on macOS / Linux (Python 3.11+; LibreOffice only for the PDF exports):

```bash
cd data_management_project
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run_all.py --from-scratch && python -m pytest -q
python -m src.build_report && python -m src.build_slides && python build_submission.py
cd ../dashboard && streamlit run app.py        # http://localhost:8501
```

`dashboard/static/index.html` also opens directly in a browser. The earlier multi-page Streamlit
dashboard on the Spark gold layer (RQ1-RQ6) is kept as `dashboard/app_classic.py`
(`cd dashboard && streamlit run app_classic.py`). Full details: [`data_management_project/README.md`](data_management_project/README.md).

---

## 🧱 Architecture Overview

### Medallion Layers  
- **Bronze** → Raw ingestion  
- **Silver** → Cleaned, standardized, conformed  
- **Gold** → Dimensional models + Fact tables  

### Orchestration  
- Batch detection  
- Batch creation  
- Pipeline execution  
- Batch completion  
- Dashboard refresh  

### Dashboard  
- Streamlit analytics dashboard  
- Driver, constructor, and race insights  

---

## 📁 Project Structure

<img width="507" height="477" alt="Screenshot 2026-06-09 at 4 35 00 PM" src="https://github.com/user-attachments/assets/58e1b300-2187-49da-b084-1028eecc6e36" />

---

## 🔄 Incremental Batch Processing

Each batch is a folder inside:

data/landing/<batch_id>/

Example:

data/landing/20250101_090000/


The system automatically:

1. Detects the latest batch folder  
2. Creates a new batch entry  
3. Runs Bronze → Silver → Gold  
4. Marks the batch as completed  
5. Refreshes the dashboard  

---

## 🧠 Orchestration Scripts

### main.sh  
Runs the entire system:

- Cleans old logs  
- Detects latest batch  
- Runs orchestration  
- Runs pipeline  
- Starts dashboard  
- Saves logs  

Run:

bash scripts/main.sh


---

### run_orchestration.sh  
Handles:

- Identify Next Batch  
- Create New Batch  

---

### run_pipeline.sh  
Executes:

- Bronze ingestion  
- Silver transformation  
- Gold modeling  
- Batch completion  

Manual run:

bash scripts/run_pipeline.sh <batch_id>


---

### run_dashboard.sh  
Starts the Streamlit dashboard (`dashboard/app.py`, the coursework dashboard). The original gold-layer
dashboard runs with `cd dashboard && streamlit run app_classic.py`.

---

## 🧪 Pipeline Execution Flow

### Bronze Layer
- Reads raw CSV/JSON files  
- Adds batch metadata  
- Writes raw Parquet  

### Silver Layer
- Cleans data  
- Standardizes schema  
- Fixes types  
- Writes conformed Parquet  

### Gold Layer
Builds:

- dim_races  
- dim_constructors  
- dim_drivers  
- fact_session_results  

---

## 📊 Dashboard

A Streamlit dashboard visualizes:

- Race results  
- Constructor performance  
- Driver statistics  
- Season trends  

Run manually:

bash scripts/run_dashboard.sh


---

## 🛠️ Environment Setup

### Install dependencies

pip install pyspark papermill streamlit pandas


### Configure environment paths  
Inside:

notebooks/00-common/01_environment_config.ipynb


---

## 🚀 Running the Entire System

### Recommended (fully automated)

bash main.sh --workspace "/Users/manoharazalki"


### Manual batch run

export WORKSPACE="/Users/manoharazalki/F1-Analytics"
export BATCH_ID="2025-02"

bash scripts/run_orchestration.sh
bash scripts/run_pipeline.sh
bash scripts/run_dashboard.sh
---

## 🏷️ Versioning

This release is tagged:

v2.0 — F1-Race-2.0


Includes:

- Full local orchestration  
- Auto‑detect batch  
- Auto‑clean logs  
- Updated Gold notebooks  
- Updated environment config  
- Production‑grade shell scripts  

---

## 🧭 Roadmap

- Add Airflow/Dagster orchestration  
- Add unit tests (pytest)  
- Add CI/CD (GitHub Actions)  
- Add data quality checks (Great Expectations)  
- Add historical dashboards  
- Add metadata lineage  

---

## 👨‍💻 Author

**Manohar Anand Zalki**  
Munich, Germany  
MSc Applied Data Science & AI  

---

## 🏁 License

MIT License  
Free to use, modify, and distribute.
