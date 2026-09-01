"""Сборка определений демо-проекта.

Три демо лекции живут в одном проекте и в одном графе:

  DEMO 1  quickstart: feature_table → training_dataset_qs → trained_model_qs
  DEMO 2  raw + dbt:  raw_orders/raw_items → staging → intermediate → feature_mart
  DEMO 3  ml:         feature_mart → training_dataset → trained_model
                      → evaluation → registered_model
"""

import dagster as dg
from dagster_dbt import DbtCliResource

from dagster_demo.defs import dbt_defs, ingest, ml, quickstart
from dagster_demo.project import dbt_demo_project
from dagster_demo.resources import MLflowResource

# Исполнение СТРОГО последовательное. DuckDB — однофайловая база и не даёт писать
# в неё из двух процессов: при обычном multiprocess-исполнении ingest-ассеты дерутся
# за блокировку файла и демо падает на камере. Проект крошечный, всё считается
# секундами, поэтому параллелизм здесь нечего экономить.
defs = dg.Definitions(
    executor=dg.in_process_executor,
    assets=[
        *dg.load_assets_from_modules([quickstart, ingest, ml]),
        dbt_defs.dbt_demo_models,
    ],
    asset_checks=[*dg.load_asset_checks_from_modules([ml, quickstart])],
    resources={
        "dbt": DbtCliResource(project_dir=dbt_demo_project),
        "mlflow_res": MLflowResource(),
    },
)
