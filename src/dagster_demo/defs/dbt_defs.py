"""DEMO 2: dbt-граф становится частью большего графа Dagster.

Всё подключение — DbtProject плюс один декоратор. Команда именно `build`,
а не `run`: тогда тесты dbt выполняются вместе с моделями и приезжают
в Dagster как asset checks.
"""

import dagster as dg
from dagster_dbt import DbtCliResource, dbt_assets

from dagster_demo.project import dbt_demo_project
from dagster_demo.translator import DemoDbtTranslator


@dbt_assets(
    manifest=dbt_demo_project.manifest_path,
    dagster_dbt_translator=DemoDbtTranslator(),
)
def dbt_demo_models(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()
