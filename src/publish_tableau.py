"""Publish a Tableau datasource or workbook to Tableau Cloud/Server.

This script is intentionally opt-in for live API calls. By default it runs a
dry-run that validates configuration without contacting Tableau.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path


REQUIRED_ENV_VARS = [
    "TABLEAU_SERVER_URL",
    "TABLEAU_SITE_ID",
    "TABLEAU_TOKEN_NAME",
    "TABLEAU_TOKEN_VALUE",
    "TABLEAU_PROJECT_NAME",
]


def env_config() -> dict[str, str]:
    return {name: os.environ.get(name, "") for name in REQUIRED_ENV_VARS}


def validate_config(config: dict[str, str], publish_path: Path) -> list[str]:
    errors = []
    for name, value in config.items():
        if not value:
            errors.append(f"Missing environment variable: {name}")
    if not publish_path.exists():
        errors.append(f"Publish path does not exist: {publish_path}")
    return errors


def dry_run(args: argparse.Namespace, config: dict[str, str], errors: list[str]) -> None:
    print("Tableau publish dry-run")
    print(f"- publish_type: {args.publish_type}")
    print(f"- path: {args.path}")
    print(f"- name: {args.name}")
    print(f"- server_url: {config['TABLEAU_SERVER_URL'] or '[missing]'}")
    print(f"- site_id: {config['TABLEAU_SITE_ID'] or '[missing]'}")
    print(f"- project_name: {config['TABLEAU_PROJECT_NAME'] or '[missing]'}")
    print("- token_value: [redacted]" if config["TABLEAU_TOKEN_VALUE"] else "- token_value: [missing]")
    if errors:
        print("\nConfiguration errors:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(2)
    print("\nDry-run passed. Re-run with --confirm-live-api to publish.")


def publish(args: argparse.Namespace, config: dict[str, str]) -> str:
    try:
        import tableauserverclient as TSC
    except ImportError as exc:
        raise SystemExit(
            "Missing Tableau Server Client dependency. Install it with:\n"
            "  pip install -r requirements-tableau.txt"
        ) from exc

    server = TSC.Server(config["TABLEAU_SERVER_URL"], use_server_version=True)
    auth = TSC.PersonalAccessTokenAuth(
        token_name=config["TABLEAU_TOKEN_NAME"],
        personal_access_token=config["TABLEAU_TOKEN_VALUE"],
        site_id=config["TABLEAU_SITE_ID"],
    )

    with server.auth.sign_in(auth):
        projects = list(TSC.Pager(server.projects))
        project = next((item for item in projects if item.name == config["TABLEAU_PROJECT_NAME"]), None)
        if project is None:
            raise SystemExit(f"Tableau project not found: {config['TABLEAU_PROJECT_NAME']}")

        mode = TSC.Server.PublishMode.Overwrite
        if args.publish_type == "datasource":
            item = TSC.DatasourceItem(project_id=project.id, name=args.name)
            published = server.datasources.publish(item, args.path, mode)
            return published.webpage_url

        item = TSC.WorkbookItem(project_id=project.id, name=args.name)
        published = server.workbooks.publish(item, args.path, mode)
        return published.webpage_url


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish a Tableau datasource or workbook.")
    parser.add_argument("--path", default="tableau/ga4_funnel_portfolio.hyper")
    parser.add_argument("--name", default="GA4 Funnel Portfolio")
    parser.add_argument("--publish-type", choices=["datasource", "workbook"], default="datasource")
    parser.add_argument("--confirm-live-api", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    config = env_config()
    publish_path = Path(args.path)
    errors = validate_config(config, publish_path)

    if not args.confirm_live_api:
        dry_run(args, config, errors)

    if errors:
        for error in errors:
            print(error)
        raise SystemExit(2)

    url = publish(args, config)
    print(f"Published to Tableau: {url}")
