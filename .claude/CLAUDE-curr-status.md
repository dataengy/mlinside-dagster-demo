# Текущий статус проекта

> Файл обновляется агентом на старте сессии. Последнее обновление: **2026-09-18**.

Проект: `mlinside-dagster-demo` — демо-стенд трёх живых демо лекции MLInside про Dagster.
Ветка: `main`, синхронизирована с `origin/main`, рабочее дерево чистое.

## Последние завершённые задачи

В репозитории пока **один** коммит — вся история проекта это первичная выкладка.

| Коммит | Дата | Автор | Что сделано |
|---|---|---|---|
| [`d6669d6`](https://github.com/dataengy/mlinside-dagster-demo/commit/d6669d6) | 2026-09-01 | Nikolay Krupiy | feat: демо-проект трёх живых демо лекции MLInside про Dagster |

Внутри этого коммита закрыто фактически три куска работы:

1. **DEMO 1 · Quick Start** — автономная цепочка `feature_table → training_dataset_qs → trained_model_qs`
   (`src/dagster_demo/defs/quickstart.py`).
2. **DEMO 2 · Dagster + dbt** — ингест сырья в DuckDB и dbt-слой `stg_* → int_order_features → feature_mart`;
   команда `dbt build`, поэтому тесты dbt приезжают как asset checks
   (`src/dagster_demo/defs/dbt_defs.py`, `dbt_demo/models/`).
3. **DEMO 3 · ML lifecycle** — обучение, оценка и регистрация модели в локальном MLflow на SQLite
   (`src/dagster_demo/defs/ml.py`, `src/dagster_demo/resources.py`).

Плюс операционная обвязка: `Justfile` (`reset` / `seed` / `dbt-parse` / `dev` / `smoke` / `mlflow` /
`swap-features`), `README.md` и сценарий показа `docs/RUNBOOK.md`.

## Незавершённые задачи за последние 2 рабочих дня

**Нет.** Ни одного маркера `TODO` / `FIXME` / `XXX` в исходниках, доках, `Justfile` и dbt-моделях;
незакоммиченных изменений нет; неотправленных коммитов нет.

## Состояние стенда на диске

Стенд подготовлен к записи и находится в состоянии «до демо»:

- `just reset` отработал — `data/warehouse.duckdb` и `data/features.parquet` на месте,
  `dbt_demo/target/manifest.json` собран;
- ничего не материализовано — `data/mlflow.db` и `data/mlruns/` отсутствуют;
- `.dagster_home/` создан, интерфейс `just dev` уже поднимался.

Проверка на этой сессии: `dagster definitions validate -m dagster_demo.definitions` —
**Validation successful**, все code locations проходят. `just smoke` намеренно **не** запускался:
он материализует весь граф и сломал бы состояние «до демо».

## Что дальше

Предложения по следующим шагам — в [`.claude/TODO.md`](TODO.md). Ни один из них не согласован,
все они опциональны: для самой записи лекции проект уже готов.
