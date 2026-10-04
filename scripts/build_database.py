"""Build the local SQLite database from the preserved SWTS CSV files."""

from __future__ import annotations

import argparse
import csv
import sqlite3
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE = PROJECT_ROOT / "database" / "build" / "kri.sqlite"
SQL_DIRECTORY = PROJECT_ROOT / "database" / "sql"


@dataclass(frozen=True)
class Source:
    filename: str
    table: str


SOURCES = (
    Source("SWTS_InSchool.csv", "raw_in_school"),
    Source("SWTS_Employer.csv", "raw_employer"),
)


def quote_identifier(value: str) -> str:
    """Quote a SQLite identifier sourced from a trusted CSV header."""
    return '"' + value.replace('"', '""') + '"'


def apply_sql_files(connection: sqlite3.Connection, filenames: tuple[str, ...]) -> None:
    for filename in filenames:
        sql_path = SQL_DIRECTORY / filename
        connection.executescript(sql_path.read_text(encoding="utf-8"))


def load_source(connection: sqlite3.Connection, source: Source) -> None:
    csv_path = PROJECT_ROOT / "raw_data" / source.filename
    with csv_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        headers = next(reader)
        if len(headers) != len(set(headers)):
            raise ValueError(f"{source.filename} contains duplicate column names")

        raw_columns = ",\n    ".join(
            f"{quote_identifier(header)} TEXT" for header in headers
        )
        connection.execute(
            f"CREATE TABLE {quote_identifier(source.table)} (\n"
            "    _source_row_number INTEGER PRIMARY KEY,\n"
            f"    {raw_columns}\n"
            ") STRICT"
        )

        placeholders = ", ".join("?" for _ in range(len(headers) + 1))
        insert_sql = (
            f"INSERT INTO {quote_identifier(source.table)} VALUES ({placeholders})"
        )
        rows = []
        for row_number, row in enumerate(reader, start=1):
            if len(row) != len(headers):
                raise ValueError(
                    f"{source.filename} row {row_number}: expected {len(headers)} "
                    f"fields, found {len(row)}"
                )
            rows.append((row_number, *row))

    connection.executemany(insert_sql, rows)


def build_database(destination: Path) -> None:
    destination = destination.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.unlink(missing_ok=True)

    try:
        connection = sqlite3.connect(temporary)
        try:
            with connection:
                for source in SOURCES:
                    load_source(connection, source)
                apply_sql_files(
                    connection,
                    ("001_clean_views.sql", "002_analysis_views.sql"),
                )
                connection.execute("PRAGMA optimize")
        finally:
            connection.close()
        temporary.replace(destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise

    print(f"Built {destination}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_DATABASE,
        help=f"SQLite output path (default: {DEFAULT_DATABASE})",
    )
    return parser.parse_args()


if __name__ == "__main__":
    build_database(parse_args().output)
