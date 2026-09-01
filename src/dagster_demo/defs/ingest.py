"""Загрузка сырья — часть графа, а не шаг «до».

Ключи этих ассетов СОВПАДАЮТ с ключами источников dbt (см. translator).
Благодаря совпадению Dagster склеивает две половины в один граф, и на слайде
про сшивку ключей видно именно это.
"""

import dagster as dg
import duckdb

from dagster_demo.project import DATA

RAW = DATA / "raw"
GROUP = "raw"


def _load_csv(table: str) -> dg.MaterializeResult:
    csv = RAW / f"{table}.csv"
    with duckdb.connect(str(DATA / "warehouse.duckdb")) as con:
        con.execute(
            f"create or replace table {table} as select * from read_csv_auto('{csv}')"
        )
        rows = con.execute(f"select count(*) from {table}").fetchone()[0]
    return dg.MaterializeResult(metadata={"dagster/row_count": rows, "file": csv.name})


@dg.asset(key=dg.AssetKey(["raw_orders"]), group_name=GROUP, compute_kind="duckdb",
          code_version="1", description="Сырые заказы, загруженные в DuckDB.")
def raw_orders() -> dg.MaterializeResult:
    return _load_csv("raw_orders")


@dg.asset(key=dg.AssetKey(["raw_items"]), group_name=GROUP, compute_kind="duckdb",
          code_version="1", description="Сырые позиции заказов, загруженные в DuckDB.")
def raw_items() -> dg.MaterializeResult:
    return _load_csv("raw_items")
