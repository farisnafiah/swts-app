# TVET participation and pay

An independent visualisation project using Khazanah Research Institute's School-to-Work Transition Survey (SWTS). The aim is to practise communicating policy research through charts, using an existing dataset and report rather than starting a new research study.

## Project workflow

The project began with the data. SWTS was selected because it provides survey CSVs, supporting documentation and a published analysis of education and work in Malaysia. TVET participation and salary offers provided a manageable focus for two visuals.

1. **Choose and document the inputs.** Retain the in-school and employer datasets, collect their column definitions, and use the report to understand what the fields represent. Start with the [raw-data guide](raw_data/README.md).
2. **Check the coding and build the visuals.** Use the notebook to interpret category codes, handle missing responses and calculate sample summaries. The report, questionnaires and CSVs do not always use matching codes, so unresolved mappings are documented. Continue with the [notebook guide](notebooks/README.md).
3. **Define and build the SQL data layer.** The [data model](database/DATA_MODEL.md) defines the grains, keys, relationships and app-facing contract. A reproducible script then loads both source CSVs into SQLite and creates documented clean and analysis views; see the [database guide](database/README.md).
4. **Expose and visualise the results.** A FastAPI backend queries the stable SQLite views and documents its contract through Swagger and a checked-in [API contract](webapp/API_CONTRACT.md). The frontend consumes that contract to show school pathways and employer salary offers.

The notebook, first database layer, read-only backend and both visualisations are implemented. A shared state selector filters both survey samples independently.

## The two visuals

- **School pathways by ethnicity:** the distribution of school pathways within each ethnic group, calculated from 7,026 in-school respondents, with TVET counts and shares labelled.
- **Maximum salary offers by qualification:** individual responses, means and medians for employers recorded as `A1 = 3`. The questionnaire labels this code public sector/government agency, but its meaning in the CSV export is not confirmed.

Both visuals use unweighted sample calculations. The report uses survey weights that are absent from the released CSVs, so these results are not presented as reproductions of its population estimates. They describe participation and offers, without establishing why differences occur.

## Project structure

```text
KRI-app/
|-- raw_data/               # 1. Original CSVs, metadata and source report
|-- notebooks/              # 2. Analysis notebook and PNG/SVG exports
|-- database/               # 3. SQLite builder, SQL and generated database
|-- webapp/                 # 4. FastAPI backend, API contract and frontend
|-- requirements.txt
`-- .venv/                  # Local Python environment; excluded from Git
```

## Run the notebook

Open [tvet_pathway.ipynb](notebooks/tvet_pathway.ipynb), select **KRI-app (.venv)** and choose **Run All**. It reads the original CSVs and saves figures to `notebooks/outputs/`.

On a new computer, install Python 3.12 and run these commands from the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m ipykernel install --user --name kri-app --display-name "KRI-app (.venv)"
```

On macOS/Linux, use `python3` and `.venv/bin/python` instead.

## Build the database

From the repository root:

```powershell
.\.venv\Scripts\python.exe database\build_database.py
```

This creates the ignored file `database/build/kri.sqlite`. The build preserves
all raw fields and applies the notebook's mappings in versioned SQL views; see
the [data-layer documentation](database/README.md) for the schema and decisions.

## Run the backend

After building the database, start the API:

```powershell
.\.venv\Scripts\python.exe webapp\run.py --reload
```

Open <http://127.0.0.1:8000> for the visualisations or
<http://127.0.0.1:8000/docs> for Swagger UI. The frontend's expected fields are
documented in the [API contract](webapp/API_CONTRACT.md).

Data and report: Khazanah Research Institute (2018), *The School-to-Work Transition of Young Malaysians*. CC BY 3.0. This is an independent project, not an official KRI application.
