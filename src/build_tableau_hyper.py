"""Build a Tableau Hyper extract from Tableau-ready CSV exports."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any, Callable


CSV_TABLES = {
    "funnel_overview": {
        "path": "tableau/funnel_overview.csv",
        "columns": [
            ("step_order", "int"),
            ("step", "text"),
            ("sessions", "int"),
            ("next_step", "text"),
            ("next_step_sessions", "int"),
            ("step_conversion_rate", "double"),
            ("dropoff_rate", "double"),
            ("metric_source", "text"),
        ],
    },
    "segment_opportunity": {
        "path": "tableau/segment_opportunity.csv",
        "columns": [
            ("segment_name", "text"),
            ("user_source", "text"),
            ("user_medium", "text"),
            ("device_category", "text"),
            ("eligible_sessions", "int"),
            ("begin_checkout_sessions", "int"),
            ("purchase_sessions", "int"),
            ("revenue", "double"),
            ("segment_conversion_rate", "double"),
            ("benchmark_conversion_rate", "double"),
            ("conversion_rate_gap", "double"),
            ("average_order_value", "double"),
            ("estimated_missed_conversions", "double"),
            ("estimated_revenue_opportunity", "double"),
            ("metric_source", "text"),
        ],
    },
    "experiment_feasibility": {
        "path": "tableau/experiment_feasibility.csv",
        "columns": [
            ("metric_name", "text"),
            ("metric_value", "text"),
            ("metric_source", "text"),
        ],
    },
    "kpi_summary": {
        "path": "tableau/kpi_summary.csv",
        "columns": [
            ("metric_name", "text"),
            ("metric_value", "text"),
            ("metric_source", "text"),
        ],
    },
}


def parse_int(value: str) -> int | None:
    if value == "":
        return None
    return int(float(value))


def parse_double(value: str) -> float | None:
    if value == "":
        return None
    return float(value)


def parse_text(value: str) -> str | None:
    if value == "":
        return None
    return value


PARSERS: dict[str, Callable[[str], Any]] = {
    "int": parse_int,
    "double": parse_double,
    "text": parse_text,
}


def read_rows(path: str | Path, columns: list[tuple[str, str]]) -> list[list[Any]]:
    with Path(path).open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        return [[PARSERS[column_type](row[column_name]) for column_name, column_type in columns] for row in reader]


def build_hyper(output_path: str | Path) -> None:
    try:
        from tableauhyperapi import (
            Connection,
            CreateMode,
            HyperProcess,
            Inserter,
            SqlType,
            TableDefinition,
            TableName,
            Telemetry,
        )
    except ImportError as exc:
        raise SystemExit(
            "Missing Tableau Hyper API dependency. Install it with:\n"
            "  pip install -r requirements-tableau.txt"
        ) from exc

    sql_types = {
        "int": SqlType.big_int(),
        "double": SqlType.double(),
        "text": SqlType.text(),
    }

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
        with Connection(endpoint=hyper.endpoint, database=output, create_mode=CreateMode.CREATE_AND_REPLACE) as connection:
            connection.catalog.create_schema("Extract")
            for table_name, table_config in CSV_TABLES.items():
                columns = table_config["columns"]
                definition = TableDefinition(
                    table_name=TableName("Extract", table_name),
                    columns=[
                        TableDefinition.Column(column_name, sql_types[column_type])
                        for column_name, column_type in columns
                    ],
                )
                connection.catalog.create_table(definition)
                rows = read_rows(table_config["path"], columns)
                with Inserter(connection, definition) as inserter:
                    inserter.add_rows(rows)
                    inserter.execute()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a Tableau Hyper extract from generated CSV exports.")
    parser.add_argument("--output", default="tableau/ga4_funnel_portfolio.hyper")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    build_hyper(args.output)
