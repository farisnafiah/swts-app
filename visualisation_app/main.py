"""Read-only FastAPI backend for the TVET visualisations."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "database" / "build" / "kri.sqlite"


class ApiIndex(BaseModel):
    name: str
    documentation: str
    openapi_schema: str


class HealthResponse(BaseModel):
    status: Literal["ok"]
    database: Literal["available"]


class SchoolPathwayItem(BaseModel):
    ethnicity_group: str
    ethnicity_order: int
    school_pathway: str
    pathway_order: int
    respondents: int = Field(ge=0)
    ethnicity_respondents: int = Field(ge=0)
    sample_share_percent: float = Field(ge=0, le=100)


class SchoolPathwayResponse(BaseModel):
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

    connection = sqlite3.connect(f"{DATABASE_PATH.as_uri()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()


@app.get("/", response_model=ApiIndex, tags=["Service"])
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
    "/api/v1/school-pathways",
    response_model=SchoolPathwayResponse,
    tags=["Visualisations"],
)
def school_pathways(
    connection: sqlite3.Connection = Depends(get_connection),
) -> SchoolPathwayResponse:
    """Return the complete ethnicity-by-pathway matrix for visualisation 1."""
    rows = connection.execute(
        """
        SELECT
            ethnicity_group,
            ethnicity_order,
            school_pathway,
            pathway_order,
            respondents,
            ethnicity_respondents,
            sample_share_percent
        FROM analysis_school_pathways_by_ethnicity
        ORDER BY ethnicity_order, pathway_order
        """
    ).fetchall()
    items = [SchoolPathwayItem(**dict(row)) for row in rows]
    return SchoolPathwayResponse(
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
) -> SalaryOfferResponse:
    """Return individual offers and summary measures for visualisation 2."""
    employer_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM clean_salary_offers
        WHERE employer_type_code = 3
          AND qualification_order = 1
        """
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
        ORDER BY qualification_order, maximum_offer_rm, employer_id
        """
    ).fetchall()
    summary_rows = connection.execute(
        """
        SELECT
            qualification_order,
            qualification,
            responses,
            mean_rm,
            median_rm,
            minimum_rm,
            maximum_rm
        FROM analysis_salary_offers_a1_3
        ORDER BY qualification_order
        """
    ).fetchall()
    return SalaryOfferResponse(
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
