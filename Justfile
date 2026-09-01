# Демо-проект трёх живых демо лекции MLInside про Dagster.
# Всё локально: ни сети, ни облака, ни Docker, ни долгого обучения.

_dir := justfile_directory()

# Полный сброс к состоянию «до демо»: данные на месте, ничего не материализовано.
reset:
    cd {{_dir}} && rm -rf .dagster_home dbt_demo/target data/warehouse.duckdb \
      data/mlflow.db data/mlruns && mkdir -p .dagster_home
    cd {{_dir}} && just seed
    cd {{_dir}} && just dbt-parse

# Сгенерировать исходные данные (обычно не нужно — они лежат в репозитории).
seed seed="7":
    cd {{_dir}} && uv run python scripts/make_seeds.py --seed {{seed}}
    cd {{_dir}} && uv run python scripts/make_features.py {{seed}} data/features.parquet

# Загрузить сырьё в DuckDB и собрать manifest.json — ОБЯЗАТЕЛЬНО до записи демо.
dbt-parse:
    cd {{_dir}} && uv run python scripts/load_raw.py
    cd {{_dir}}/dbt_demo && uv run dbt parse --profiles-dir .

# Поднять интерфейс. Порт нестандартный, чтобы не драться с чужим Dagster.
dev port="3111":
    cd {{_dir}} && DAGSTER_HOME={{_dir}}/.dagster_home uv run dg dev --port {{port}}

# Прогнать весь граф без интерфейса — проверка, что демо поедет.
smoke:
    cd {{_dir}} && DAGSTER_HOME={{_dir}}/.dagster_home \
      uv run dagster asset materialize --select '*' -m dagster_demo.definitions

# Интерфейс MLflow поверх того же локального SQLite.
mlflow port="5000":
    cd {{_dir}} && uv run mlflow ui --port {{port}} \
      --backend-store-uri sqlite:///{{_dir}}/data/mlflow.db

# Подменить витрину на второй вариант — шаг «поменяли upstream» в DEMO 1.
swap-features seed="42":
    cd {{_dir}} && uv run python scripts/make_features.py {{seed}} data/features.parquet
