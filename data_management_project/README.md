# F1 Data Management Project (Winter 2026/27)

Curated, quality-assessed and FAIR-documented Formula 1 World Championship race results
(1950-2025), with a reproducible cleaning pipeline and a NetworkX property-graph analysis.

| Component | Presents | Main code | Main outputs |
|---|---|---|---|
| A - FAIR assessment & metadata | Chirag Adhikari | `src/fair_assessment.py`, `src/metadata.py`, `src/pid_enrichment.py`, `src/run_fuji_assessment.py` | `outputs/component_a_fair/` |
| B - Data quality & profiling | Manohar Zalki | `src/profiling.py`, `src/quality_charts.py` | `outputs/component_b_quality/` |
| C - Data cleaning & pipeline | Nicolas Bonilla | `src/cleaning.py`, `src/vocabularies.py`, `src/schema.py` | `data/cleaned/`, `outputs/component_c_cleaning/` |
| Graph modelling (shared) | all | `src/graph_model.py` | `outputs/graph/` |
| Interactive dashboard (shared) | all | `../dashboard/build_web_data.py`, `../dashboard/static/` | `../dashboard/static/data.js`, `outputs/dashboard/` |
| Architecture diagram | all | `src/architecture.py` | `outputs/architecture/` |
| Report and slides | all | `src/build_report.py`, `src/build_slides.py` | `report/` |

Group: Chirag Adhikari, Manohar Zalki, Nicolas Bonilla (joint work on every component).

## Run it

Requirements: Python 3.11 or newer and the packages in `requirements.txt`. No network access is needed
once the packages are installed. LibreOffice is only needed to turn the Word report and the slides into
PDF (macOS: `brew install --cask libreoffice`); without it the `.docx` and `.pptx` are still written.

macOS / Linux:

```bash
cd data_management_project
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run_all.py --from-scratch   # rebuild every dataset, table and figure (~90 s)
python -m pytest -q                # 14 tests on the key cleaning decisions
python -m src.build_report         # joint report (Word + PDF)
python -m src.build_slides         # presentation deck (PowerPoint + PDF) and presenter script
python build_submission.py         # group ZIP for the course portal -> dist/
```

Windows (PowerShell): the same commands, with `py -3.11 -m venv .venv` and `.venv\Scripts\Activate.ps1`.

Everything the pipeline produces is already committed, so the report (`report/`), the slides
(`report/presentation/`), the submission ZIP (`dist/`) and the dashboard open without running anything.
A run from scratch must print these hashes for the cleaned files (the CSVs are stored byte-for-byte, see
`.gitattributes`):

```
0d468653082d5059f6ab911add127aca35a086c0512a8d1b603175d731be0c01  f1_race_results_clean.csv
2cc92f9ed57f42bcfef134f96887be215602c21316ad53631e839a617b685834  races_clean.csv
661d6b1953c109e94aac42bbb12ae9c851348c960faddea68e8bd1c7659154be  circuits_clean.csv
4add2b09038350297b0715da016f1b9cae134f9c5ae2619d1554350b417af733  drivers_clean.csv
649eb1db014bdc45ec5bab87a06d1c9ff5235ead0b9a70eb68cc47ca20c9922d  constructors_clean.csv
```

`run_all.py` runs, in order: raw extraction (step 0) -> PID crosswalk (cached) -> profiling (B) ->
cleaning (C) -> figures -> graph -> F-UJI summary -> RDA assessment -> metadata (A) -> dashboard data
-> architecture diagram. It prints the SHA-256 of every cleaned file; two runs from scratch produce
identical hashes.

## Interactive dashboard

The final stage of the pipeline. `run_all.py` writes `../dashboard/static/data.js` from the validated
outputs; open the dashboard with `cd ../dashboard` and `streamlit run app.py` (http://localhost:8501), or
open `../dashboard/static/index.html` directly in a browser. Seven views: constructor eras, all-time timing
tower, grid to finish, reliability, circuits globe, team-mate network and the data-quality story. Building it
revealed issue B29 (retirement causes not recorded from 2023). The earlier multi-page dashboard built on the
Spark gold layer (sections RQ1-RQ6) is kept unchanged as `../dashboard/app_classic.py`
(`streamlit run app_classic.py`).

## Data flow

```
data/source/racing_f1_data.zip          original package (SHA-256 81b027c4...c748), never modified
  -> data/raw/*.csv                     flattened, values unchanged, + source_file/source_line lineage
  -> outputs/component_b_quality/       29-issue register, profiles, passed checks, figures
  -> data/cleaned/*.csv                 25,873 results x 35 columns + 4 reference tables
  -> outputs/component_c_cleaning/      audit log, 55 validation gates, issue resolution
  -> outputs/graph/                     property graph + team-mate network (GEXF for Gephi), metrics
  -> outputs/component_a_fair/          F-UJI evidence, RDA scores, DataCite 4.5, schema.org, PROV-O
  -> ../dashboard/static/data.js        interactive dashboard (served zone)
```

## Before submission (group to complete)

1. Add ORCID iDs in `src/config.py` (`TEAM`), and confirm who presents each block, then re-run
   `python run_all.py`, `python -m src.build_report` and `python -m src.build_slides`.
2. Confirm the institution ROR in `src/metadata.py` (candidate: https://ror.org/00g07sz63).
3. Optionally deposit `data/cleaned/` on Zenodo to mint the DOI that replaces
   `10.5281/zenodo.TO-BE-MINTED`.
4. Personalise the reflection drafts in `report/reflection_drafts/` (each student submits their own).

## Re-running the live F-UJI assessment (optional)

The stored responses in `outputs/component_a_fair/fuji/` are the evidence used in the report. To repeat
the evaluation, start a local F-UJI server (Python 3.13, https://github.com/pangaea-data-publisher/fuji)
and run `python -m src.run_fuji_assessment`.

## Licences

* Data (`data/`): CC BY-NC-SA 4.0, inherited from Jolpica-F1 / Ergast (see
  `outputs/component_a_fair/LICENSE-DATA.md`). Non-commercial use only.
* Code (`src/`, `tests/`, scripts): MIT.

## AI tool use

AI assistance (Claude Code) was used with the instructor's agreement; see Appendix G of the report.
