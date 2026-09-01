"""Загрузить сырьё в DuckDB — то же, что делают ингест-ассеты Dagster.

Нужен для pre-flight: dbt должен уметь распарсить источники ДО того, как
Dagster первый раз что-то материализует.
"""

from pathlib import Path

import duckdb

DATA = Path(__file__).resolve().parents[1] / "data"

with duckdb.connect(str(DATA / "warehouse.duckdb")) as con:
    for table in ("raw_orders", "raw_items"):
        csv = DATA / "raw" / f"{table}.csv"
        con.execute(f"create or replace table {table} as select * from read_csv_auto('{csv}')")
        rows = con.execute(f"select count(*) from {table}").fetchone()[0]
        print(f"{table}: {rows} строк")
