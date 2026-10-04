"""Read-only FastAPI backend for the TVET visualisations."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from pathlib import Path
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "database" / "build" / "kri.sqlite"
FRONTEND_PATH = Path(__file__).resolve().parent / "frontend"
STATES = {
    1: "Johor",
    2: "Kedah",
    3: "Kelantan",
    4: "Melaka",
    5: "Negeri Sembilan",
    6: "Pahang",
    7: "Penang",
    8: "Perak",
    9: "Perlis",
    10: "Selangor",
    11: "Terengganu",
    12: "Sabah",
    13: "Sarawak",
    14: "W.P. Kuala Lumpur",
    15: "W.P. Labuan",
    16: "W.P. Putrajaya",
}


class ApiIndex(BaseModel):
    name: str
    documentation: str
    openapi_schema: str


class HealthResponse(BaseModel):
    status: Literal["ok"]
    database: Literal["available"]


class StateOption(BaseModel):
    code: int = Field(ge=1, le=16)
    label: str


class StateListResponse(BaseModel):
    items: list[StateOption]


class SchoolPathwayItem(BaseModel):
    ethnicity_group: str
    ethnicity_order: int
    school_pathway: str
    pathway_order: int
    respondents: int = Field(ge=0)
    ethnicity_respondents: int = Field(ge=0)
    sample_share_percent: float = Field(ge=0, le=100)


class SchoolPathwayResponse(BaseModel):
    state_code: int | None
    state_label: str
    weighting: Literal["unweighted"]
    total_respondents: int = Field(ge=0)
    items: list[SchoolPathwayItem]


class SalaryObservation(BaseModel):
    employer_id: int
    qualification_order: int = Field(ge=1, le=4)
    qualification: str
    maximum_offer_rm: float = Field(ge=0)


class SalarySummary(BaseModel):
    qualification_order: int = Field(ge=1, le=4)
    qualification: str
    responses: int = Field(ge=0)
    mean_rm: float = Field(ge=0)
    median_rm: float = Field(ge=0)
    minimum_rm: float = Field(ge=0)
    maximum_rm: float = Field(ge=0)


class SalaryOfferResponse(BaseModel):
    state_code: int | None
    state_label: str
    employer_type_code: Literal[3]
    employer_type_label: str
    label_status: Literal["questionnaire label; CSV mapping unconfirmed"]
    weighting: Literal["unweighted"]
    currency: Literal["MYR"]
    period: Literal["month"]
    employers: int = Field(ge=0)
    observations: list[SalaryObservation]
    summaries: list[SalarySummary]


app = FastAPI(
    title="TVET visualisation API",
    summary="Read-only chart data from the KRI SWTS extracts",
    description=(
        "Serves the unweighted datasets used by the TVET participation and pay "
        "visualisations. Build the SQLite database before starting the API."
    ),
    version="0.1.0",
)


def get_connection() -> Iterator[sqlite3.Connection]:
    if not DATABASE_PATH.is_file():
        raise HTTPException(
            status_code=503,
            detail="Database not found. Run: python scripts/build_database.py",
        )

    connection = sqlite3.connect(
        f"{DATABASE_PATH.as_uri()}?mode=ro",
        uri=True,
        check_same_thread=False,
    )
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()


@app.get("/api", response_model=ApiIndex, tags=["Service"])
def api_index() -> ApiIndex:
    """Return links to the interactive and machine-readable API documentation."""
    return ApiIndex(
        name=app.title,
        documentation="/docs",
        openapi_schema="/openapi.json",
    )


@app.get("/health", response_model=HealthResponse, tags=["Service"])
def health(
    connection: sqlite3.Connection = Depends(get_connection),
) -> HealthResponse:
    """Confirm that the service can read the generated SQLite database."""
    connection.execute("SELECT 1").fetchone()
    return HealthResponse(status="ok", database="available")


@app.get(
    "/api/v1/states",
    response_model=StateListResponse,
    tags=["Visualisations"],
)
def states() -> StateListResponse:
    """Return the verified SWTS state-code labels used by both samples."""
    return StateListResponse(
        items=[StateOption(code=code, label=label) for code, label in STATES.items()]
    )


@app.get(
    "/api/v1/school-pathways",
    response_model=SchoolPathwayResponse,
    tags=["Visualisations"],
)
def school_pathways(
    connection: sqlite3.Connection = Depends(get_connection),
    state_code: Annotated[
        int | None,
        Query(ge=1, le=16, description="SWTS state code; omit for all states"),
    ] = None,
) -> SchoolPathwayResponse:
    """Return the complete ethnicity-by-pathway matrix for visualisation 1."""
    rows = connection.execute(
        """
        WITH
        ethnicity_groups(ethnicity_group, ethnicity_order) AS (
            VALUES
                ('Bumiputera', 1), ('Indian', 2), ('Chinese', 3), ('Other', 4)
        ),
        pathways(school_pathway, pathway_order) AS (
            VALUES
                ('National / residential / Form 6', 1),
                ('Technical / vocational', 2),
                ('National religious', 3),
                ('International / private', 4)
        ),
        pathway_counts AS (
            SELECT ethnicity_group, school_pathway, COUNT(*) AS respondents
            FROM clean_in_school
            WHERE (? IS NULL OR state_code = ?)
            GROUP BY ethnicity_group, school_pathway
        ),
        complete_counts AS (
            SELECT
                ethnicity_groups.ethnicity_group,
                ethnicity_groups.ethnicity_order,
                pathways.school_pathway,
                pathways.pathway_order,
                COALESCE(pathway_counts.respondents, 0) AS respondents
            FROM ethnicity_groups
            CROSS JOIN pathways
            LEFT JOIN pathway_counts USING (ethnicity_group, school_pathway)
        )
        SELECT
            ethnicity_group,
            ethnicity_order,
            school_pathway,
            pathway_order,
            respondents,
            SUM(respondents) OVER (PARTITION BY ethnicity_group)
                AS ethnicity_respondents,
            CASE
                WHEN SUM(respondents) OVER (PARTITION BY ethnicity_group) = 0 THEN 0
                ELSE ROUND(
                    100.0 * respondents
                    / SUM(respondents) OVER (PARTITION BY ethnicity_group),
                    6
                )
            END AS sample_share_percent
        FROM complete_counts
        ORDER BY ethnicity_order, pathway_order
        """,
        (state_code, state_code),
    ).fetchall()
    items = [SchoolPathwayItem(**dict(row)) for row in rows]
    return SchoolPathwayResponse(
        state_code=state_code,
        state_label=STATES.get(state_code, "All states"),
        weighting="unweighted",
        total_respondents=sum(item.respondents for item in items),
        items=items,
    )


@app.get(
    "/api/v1/salary-offers",
    response_model=SalaryOfferResponse,
    tags=["Visualisations"],
)
def salary_offers(
    connection: sqlite3.Connection = Depends(get_connection),
    state_code: Annotated[
        int | None,
        Query(ge=1, le=16, description="SWTS state code; omit for all states"),
    ] = None,
) -> SalaryOfferResponse:
    """Return individual offers and summary measures for visualisation 2."""
    employer_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM clean_salary_offers
        WHERE employer_type_code = 3
          AND qualification_order = 1
          AND (? IS NULL OR state_code = ?)
        """,
        (state_code, state_code),
    ).fetchone()[0]
    observation_rows = connection.execute(
        """
        SELECT
            employer_id,
            qualification_order,
            qualification,
            maximum_offer_rm
        FROM clean_salary_offers
        WHERE employer_type_code = 3
          AND maximum_offer_rm IS NOT NULL
          AND (? IS NULL OR state_code = ?)
        ORDER BY qualification_order, maximum_offer_rm, employer_id
        """,
        (state_code, state_code),
    ).fetchall()
    summary_rows = connection.execute(
        """
        WITH ranked AS (
            SELECT
                qualification_order,
                qualification,
                maximum_offer_rm,
                ROW_NUMBER() OVER (
                    PARTITION BY qualification
                    ORDER BY maximum_offer_rm
                ) AS value_rank,
                COUNT(*) OVER (PARTITION BY qualification) AS response_count
            FROM clean_salary_offers
            WHERE employer_type_code = 3
              AND maximum_offer_rm IS NOT NULL
              AND (? IS NULL OR state_code = ?)
        )
        SELECT
            qualification_order,
            qualification,
            COUNT(*) AS responses,
            AVG(maximum_offer_rm) AS mean_rm,
            AVG(
                CASE
                    WHEN value_rank IN (
                        (response_count + 1) / 2,
                        (response_count + 2) / 2
                    ) THEN maximum_offer_rm
                END
            ) AS median_rm,
            MIN(maximum_offer_rm) AS minimum_rm,
            MAX(maximum_offer_rm) AS maximum_rm
        FROM ranked
        GROUP BY qualification_order, qualification
        ORDER BY qualification_order
        """,
        (state_code, state_code),
    ).fetchall()
    return SalaryOfferResponse(
        state_code=state_code,
        state_label=STATES.get(state_code, "All states"),
        employer_type_code=3,
        employer_type_label="Public sector/government agency",
        label_status="questionnaire label; CSV mapping unconfirmed",
        weighting="unweighted",
        currency="MYR",
        period="month",
        employers=employer_count,
        observations=[SalaryObservation(**dict(row)) for row in observation_rows],
        summaries=[SalarySummary(**dict(row)) for row in summary_rows],
    )


@app.get("/", include_in_schema=False)
def frontend() -> FileResponse:
    """Serve the first visualisation page."""
    return FileResponse(FRONTEND_PATH / "index.html")


app.mount("/static", StaticFiles(directory=FRONTEND_PATH), name="static")
