"""DagsterDbtTranslator — как модель dbt становится ассетом Dagster.

В демо его НЕ пишут живьём: показывают роль и готовый результат. Он отвечает
на три вопроса — как назвать ассет, в какую группу его положить и что написать
в описании.
"""

from typing import Any, Mapping

import dagster as dg
from dagster_dbt import DagsterDbtTranslator


class DemoDbtTranslator(DagsterDbtTranslator):
    """Раскладывает модели по группам по имени папки и даёт ассетам короткие ключи."""

    def get_asset_key(self, props: Mapping[str, Any]) -> dg.AssetKey:
        return dg.AssetKey([props["name"]])

    def get_group_name(self, props: Mapping[str, Any]) -> str | None:
        path = props.get("fqn") or []
        # fqn = [проект, папка, ..., имя модели]
        return path[1] if len(path) > 2 else "dbt"

    def get_description(self, props: Mapping[str, Any]) -> str:
        return props.get("description") or f"dbt-модель {props['name']}"
