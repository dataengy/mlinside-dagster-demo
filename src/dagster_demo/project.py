"""Пути проекта и объект DbtProject — то, с чего начинается DEMO 2."""

from pathlib import Path

from dagster_dbt import DbtProject

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"

# DbtProject — это ВСЁ, что нужно Dagster, чтобы узнать про модели dbt.
# `prepare_if_dev` пересобирает manifest.json при `dg dev`, но на записи демо
# манифест должен быть уже собран: ожидание на камере — потерянное время.
dbt_demo_project = DbtProject(
    project_dir=ROOT / "dbt_demo",
    profiles_dir=ROOT / "dbt_demo",
)
dbt_demo_project.prepare_if_dev()
