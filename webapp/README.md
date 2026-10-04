# TVET visualisation web app

The application combines a read-only FastAPI backend with a page containing
both notebook visuals: school-pathway distribution by ethnicity and maximum
salary offers by qualification. The page is plain HTML, CSS and JavaScript
served by FastAPI and reads its data from the versioned API contract.

## Run locally

Build the SQLite database, then start the API from the repository root:

```powershell
.\.venv\Scripts\python.exe database\build_database.py
.\.venv\Scripts\python.exe webapp\run.py --reload
```

Open <http://127.0.0.1:8000> for the visualisation. Swagger UI remains at <http://127.0.0.1:8000/docs>, and the machine-readable OpenAPI schema is at <http://127.0.0.1:8000/openapi.json>.

## Endpoints

| Endpoint | Purpose |
| --- | --- |
| `GET /` | Serves both visualisations. |
| `GET /health` | Confirms that the generated SQLite database is readable. |
| `GET /api/v1/states` | Supplies verified labels for the shared state selector. |
| `GET /api/v1/school-pathways` | Complete dataset for the school-pathway visual. |
| `GET /api/v1/salary-offers` | Individual salary offers and qualification summaries. |

The [frontend API contract](API_CONTRACT.md) defines field meanings, ordering,
units, missing-value behaviour and methodological caveats. The backend reads
the views documented in the [database guide](../database/README.md).

The frontend source is in `frontend/`. It has no Node build step and no runtime
dependency on a charting library. Its state selector sends the same optional
`state_code` to both endpoints; the API filters and aggregates the two samples
independently.

All results are unweighted sample descriptions. The public CSVs do not contain
an identifiable survey-weight field. The label associated with employer code
`A1 = 3` comes from the published questionnaire and is not confirmed for the
released CSV export; this status is included in the salary response.
