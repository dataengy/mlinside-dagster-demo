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

## Состояние стенда

Стенд подготовлен к записи и находится в состоянии «до демо». Проверено **на живом инстансе**:
`uv sync` → `just reset` → `just dev` отработали, webserver слушает `http://127.0.0.1:3111`.

Запрос к GraphQL работающего Dagster подтверждает:

- code location `mlinside-dagster-demo` загружен, **13 ассетов** в 5 группах —
  `quickstart` (3), `raw` (2), `staging` (2), `intermediate` (1), `marts` (1), `ml` (4);
- **материализовано 0 из 13** — состояние «до демо» нетронуто;
- зарегистрировано **7 asset checks**, из них 5 на `feature_mart`
  (`unique_*`/`not_null_*`/`accepted_values_*`) — это те самые тесты dbt, приехавшие
  через `dbt build` без единой проверки, написанной руками. Главный эффект DEMO 2 — на месте.

Оба стыка графа, на которых держится лекция, целы:

| Стык | Рёбра в живом графе | Что сломалось бы |
|---|---|---|
| ингест ↔ dbt sources | `stg_orders ← raw_orders`, `stg_items ← raw_items` | DEMO 2: dbt-слой оторвался бы от ингеста |
| dbt ↔ ML | `training_dataset ← feature_mart` | DEMO 3: граф распался бы на два куска |

Дополнительно: `dagster definitions validate -m dagster_demo.definitions` — **Validation successful**.

`just smoke` намеренно **не** запускался: он материализует весь граф (0/13 → 13/13), а
последующий `just reset` удаляет `.dagster_home` у работающего `dg dev` и потребует
перезапуска сервера. Решение о прогоне — за человеком, см. пункт 1 в [`TODO.md`](TODO.md).

## Что дальше

Предложения по следующим шагам — в [`.claude/TODO.md`](TODO.md). Ни один из них не согласован,
все они опциональны: для самой записи лекции проект уже готов.
