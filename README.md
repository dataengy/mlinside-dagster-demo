# mlinside-dagster-demo

Демо-проект трёх живых демо лекции **«Современная оркестрация ML-пайплайнов (Dagster)»**
курса MLInside.

Три демо идут на **одном** проекте, и граф прирастает слева направо — это и есть главная
мысль лекции: dbt-часть, ML-часть и реестр моделей живут в одном графе, а не в трёх
несвязанных системах.

```
DEMO 1 · Quick Start          feature_table → training_dataset_qs → trained_model_qs

DEMO 2 · Dagster + dbt        raw_orders ┐
                              raw_items  ┴→ stg_* → int_order_features → feature_mart

DEMO 3 · ML lifecycle         feature_mart → training_dataset → trained_model
                                          → evaluation → registered_model
```

Сценарий показа, состояние «до демо», ожидаемый результат каждого шага и план возврата
к слайдам — в [`docs/RUNBOOK.md`](docs/RUNBOOK.md).

## Запуск

```bash
uv sync
just reset        # данные на месте, ничего не материализовано, manifest.json собран
just dev          # → http://localhost:3111
```

Отдельно интерфейс MLflow поверх того же локального хранилища:

```bash
just mlflow       # → http://localhost:5000
```

Проверить, что демо поедет, не открывая браузер:

```bash
just smoke        # материализует весь граф; должно закончиться RUN_SUCCESS
```

## Границы: чего здесь намеренно нет

Демо проводится на записи, поэтому проект не зависит **ни от чего внешнего**:

| Нет | Почему |
|---|---|
| сети и внешних API | отвалится молча и посреди показа |
| облачного деплоя | то же плюс задержки |
| Docker и docker-compose | сборка образа — минуты ожидания без содержания |
| скачивания данных | всё сырьё лежит в `data/raw/` прямо в репозитории |
| сервера MLflow | локальный SQLite, `mlflow ui` читает тот же файл |
| долгого обучения | маленькая выборка + логистическая регрессия, обучение — секунды |

Если обучение вдруг занимает больше десяти секунд — уменьшайте выборку, а не терпите
паузу: пауза на записи ломает показ.

## Устройство

```
dbt_demo/                      dbt на DuckDB
  models/sources/              источники, ключи совпадают с ингест-ассетами Dagster
  models/staging/              stg_orders, stg_items
  models/intermediate/         int_order_features
  models/marts/feature_mart    ВИТРИНА ПРИЗНАКОВ — стык dbt-мира и ML-мира
                               здесь же тесты dbt → приезжают как asset checks
src/dagster_demo/
  project.py                   DbtProject — всё, что нужно Dagster, чтобы узнать про dbt
  translator.py                DagsterDbtTranslator: имя, группа, описание ассета
  defs/ingest.py               загрузка сырья в DuckDB; ключи = ключи источников dbt
  defs/dbt_defs.py             @dbt_assets, команда `build` (а не `run`)
  defs/quickstart.py           автономная цепочка DEMO 1
  defs/ml.py                   DEMO 3: обучение, оценка, регистрация в MLflow
  resources.py                 MLflow на локальном SQLite
scripts/                       генерация данных и предзагрузка сырья
data/raw/*.csv                 сырьё, лежит в репозитории намеренно
```

### Два решения, которые стоит объяснить

**Команда `dbt build`, а не `dbt run`.** Тогда тесты dbt выполняются вместе с моделями и
приезжают в Dagster как **asset checks** — проверки качества появляются на карточках
ассетов без единой написанной вручную проверки.

**Исполнение строго последовательное** (`in_process_executor`). DuckDB — однофайловая база
и не даёт писать в себя из двух процессов: при обычном multiprocess-исполнении ингест-ассеты
дерутся за блокировку файла и демо падает. Проект крошечный, экономить параллелизмом нечего.

## Связь с домашним заданием

ДЗ-2 курса ([`mlinside-hw-olist`](https://github.com/hnkovr/mlinside-hw-olist), `docs/HW2-dagster.md`)
решает ту же задачу на настоящем датасете Olist и в ClickHouse. Здесь данные синтетические,
а колонки названы так же (`freight_ratio`, `distance_km`, `n_items`, `seller_delay_d`) —
чтобы демо лекции и домашнее задание говорили на одном языке.

Разница по назначению: этот проект оптимизирован под **показ на камере** (секунды, ноль
внешних зависимостей), домашнее задание — под **реальную работу** (ClickHouse, docker-compose,
132 проверки).
