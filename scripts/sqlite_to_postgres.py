"""Copy all data from the old SQLite database into Postgres.

Run once when moving an existing Lagoa installation to Postgres, after
DATABASE_URL in .env points at the new, empty database:

    uv run python -m scripts.sqlite_to_postgres
    uv run python -m scripts.sqlite_to_postgres --source path/to/data.db

The script brings the Postgres schema up to date with the migrations, refuses
to write into tables that already hold data, copies every table keeping the
ids, moves the id sequences past the copied rows and checks the row counts.
Everything happens in one transaction: if any step fails, Postgres is left
untouched. The SQLite file is only read.
"""

import argparse
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import DateTime, Engine, create_engine, func, select, text

from backend.config import SQLITE_PATH, cfg
from backend.db import Base, migrate


class MigrationError(Exception):
    """Raised when the data can't be copied safely."""


def _as_utc(row: dict, datetime_columns: list[str]) -> dict:
    # SQLite keeps times without a time zone although they are UTC. Postgres
    # would read a naive time in its own session time zone, so mark them.
    for name in datetime_columns:
        value = row[name]
        if isinstance(value, datetime) and value.tzinfo is None:
            row[name] = value.replace(tzinfo=timezone.utc)
    return row


def copy_data(source: Engine, target: Engine) -> dict[str, int]:
    """Copy every table from ``source`` to ``target`` and return row counts.

    Raises:
        MigrationError: If the target already has data or the counts differ.
    """
    tables = Base.metadata.sorted_tables  # parents before children
    counts = {}
    with source.connect() as src, target.begin() as dst:
        for table in tables:
            if dst.execute(select(func.count()).select_from(table)).scalar_one():
                raise MigrationError(
                    f"Table {table.name!r} in Postgres already has data. "
                    "The script only fills an empty database."
                )

        for table in tables:
            datetime_columns = [c.name for c in table.columns if isinstance(c.type, DateTime)]
            rows = [
                _as_utc(dict(row), datetime_columns)
                for row in src.execute(select(table)).mappings()
            ]
            if rows:
                dst.execute(table.insert(), rows)
            counts[table.name] = len(rows)

            # Rows came with their ids, so the sequence behind each id column
            # still starts at 1; move it past them or the next insert fails.
            # A key without a sequence (chat_summary.chat_id) gets NULL here,
            # and setval(NULL, ...) does nothing.
            for column in table.primary_key.columns:
                dst.execute(text(
                    f"SELECT setval(pg_get_serial_sequence('{table.name}', '{column.name}'), "
                    f"coalesce(max({column.name}), 1), max({column.name}) IS NOT NULL) "
                    f"FROM {table.name}"
                ))

        for table in tables:
            copied = dst.execute(select(func.count()).select_from(table)).scalar_one()
            if copied != counts[table.name]:
                raise MigrationError(
                    f"Table {table.name!r}: {counts[table.name]} rows in SQLite, "
                    f"{copied} in Postgres."
                )
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--source", type=Path, default=SQLITE_PATH,
        help=f"SQLite file to copy from (default: {SQLITE_PATH.name} in the project root)",
    )
    args = parser.parse_args()

    if not args.source.is_file():
        raise SystemExit(f"SQLite database not found: {args.source}")
    target = create_engine(cfg.database_url)
    if target.dialect.name != "postgresql":
        raise SystemExit("DATABASE_URL must point at Postgres, see README.")
    source = create_engine(f"sqlite:///{args.source.resolve().as_posix()}")

    print(f"Updating the schema in {target.url.render_as_string(hide_password=True)}...")
    migrate()
    try:
        counts = copy_data(source, target)
    except MigrationError as error:
        raise SystemExit(f"Nothing was copied: {error}")
    for name, count in counts.items():
        print(f"  {name}: {count} rows")
    print("Done. The SQLite file was not changed; keep it as a backup.")


if __name__ == "__main__":
    main()
