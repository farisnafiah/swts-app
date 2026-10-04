# SQLite data layer

This directory turns the preserved survey CSVs into a reproducible SQLite data
layer. The database is generated locally and is not committed.

Start with the [data model](DATA_MODEL.md). It defines the layers, grains, keys,
relationships and application-facing views. This guide describes how that
model is built.

## Build

Run these commands from the repository root:

```powershell
.\.venv\Scripts\python.exe scripts\build_database.py
```

On macOS or Linux, replace `.\.venv\Scripts\python.exe` with
`.venv/bin/python`. The build script uses only the Python standard library.

The build writes `database/build/kri.sqlite`. To write elsewhere, pass
`--output PATH`. The build creates a temporary database and replaces the
destination only after a successful import.

## Implemented layers

| Layer | Objects | Purpose |
| --- | --- | --- |
| Source | `raw_data/*.csv` | Preserved, immutable inputs. |
| Raw | `raw_in_school`, `raw_employer` | Every CSV field retained as text, plus a 1-based source-row number. Empty strings and `#NULL!` are not rewritten. |
| Clean | `clean_in_school`, `clean_salary_offers` | Documented code mappings, numeric conversion and salary fields reshaped to one row per employer and qualification. |
| Analysis | `analysis_school_pathways_by_ethnicity`, `analysis_salary_offers_a1_3` | Results used by the two current notebook visuals. |

The raw table DDL is created by the loader directly from the CSV headers
because the two exports contain 181 source columns in total. All analytical
logic remains reviewable SQL in [`sql/`](sql/):

1. `001_clean_views.sql` owns field selection, missing-value handling and code
   mappings.
2. `002_analysis_views.sql` reproduces the notebook aggregations.

The full entity and field definitions are in the
[data model](DATA_MODEL.md). The decisions below summarise the implemented
transformations.

## Transformation decisions

### School pathways

The clean view maps ethnicity codes `1` and `2` to Bumiputera, `3` to Chinese,
`4` to Indian and `5` to Other. `SchoolType1` codes are grouped as follows:

| Codes | Pathway |
| --- | --- |
| 1-6 | National / residential / Form 6 |
| 7 | Technical / vocational |
| 8-9 | National religious |
| 10-11 | International / private |

The analysis view counts pathways and calculates their unweighted share within
each ethnicity. These are sample summaries, not KRI's weighted population
estimates.

### Salary offers

The four maximum-offer columns are reshaped into `clean_salary_offers`.
Blank values and the literal `#NULL!` become SQL `NULL`; valid values become
`REAL`. The view retains `state_code` and `employer_type_code` to support later
filters.

The current analysis view selects `A1 = 3` and calculates valid response count,
mean, median, minimum and maximum by qualification. The public-sector label is
from the earlier questionnaire and remains unconfirmed for the released CSV,
so the SQL object is deliberately named with the code rather than the label.

## Incremental app boundary

The unfiltered web app queries correspond to the two analysis views. Its
optional state filter uses parameterised queries against the clean views,
applies `state_code` first, and then performs the same groupings. This preserves
the correct denominator for each selected state.

Do not edit the generated SQLite file by hand. Change a numbered SQL file or the
loader, then rebuild. A later schema change should normally be added as the next
numbered SQL file so its order and purpose remain explicit.
