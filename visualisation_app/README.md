# TVET visualisation backend

The current application is a read-only FastAPI backend. It exposes the two
datasets needed to reproduce the notebook visuals and generates interactive
Swagger documentation. A frontend is not included yet.

## Run locally

Build the SQLite database, then start the API from the repository root:

```powershell
.\.venv\Scripts\python.exe scripts\build_database.py
.\.venv\Scripts\python.exe scripts\run_api.py --reload
```

Open <http://127.0.0.1:8000/docs> to inspect the schemas and execute requests
from Swagger UI. The machine-readable OpenAPI schema is available at
<http://127.0.0.1:8000/openapi.json>.

## Endpoints

| Endpoint | Purpose |
| --- | --- |
| `GET /health` | Confirms that the generated SQLite database is readable. |
| `GET /api/v1/school-pathways` | Complete dataset for the school-pathway visual. |
| `GET /api/v1/salary-offers` | Individual salary offers and qualification summaries. |

The [frontend API contract](API_CONTRACT.md) defines field meanings, ordering,
units, missing-value behaviour and methodological caveats. The backend reads
the views documented in the [database guide](../database/README.md).

All results are unweighted sample descriptions. The public CSVs do not contain
an identifiable survey-weight field. The label associated with employer code
`A1 = 3` comes from the published questionnaire and is not confirmed for the
released CSV export; this status is included in the salary response.
