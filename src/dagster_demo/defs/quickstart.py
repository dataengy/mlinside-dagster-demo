"""DEMO 1: минимальная цепочка Quick Start — три ассета и одна проверка.

Держится отдельно от dbt- и ML-частей намеренно: первое демо должно работать
даже если dbt-проект ещё не собран. Это и есть «шаги 1–3» со слайдов.
"""

import dagster as dg
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

from dagster_demo.project import DATA

GROUP = "quickstart"


@dg.asset(group_name=GROUP, compute_kind="pandas", code_version="1",
          description="Витрина признаков — точка, где начинается рабочий день MLE.")
def feature_table() -> pd.DataFrame:
    return pd.read_parquet(DATA / "features.parquet")


@dg.asset(group_name=GROUP, compute_kind="pandas", code_version="1",
          description="Зависимость объявлена аргументом функции — ребро графа берётся отсюда.")
def training_dataset_qs(feature_table: pd.DataFrame) -> pd.DataFrame:
    df = feature_table.dropna()
    return df[df.split == "train"]


@dg.asset(group_name=GROUP, compute_kind="sklearn", code_version="1",
          description="Модель описывается тем же декоратором, что и таблица.")
def trained_model_qs(training_dataset_qs: pd.DataFrame) -> dg.MaterializeResult:
    features = [c for c in training_dataset_qs.columns if c.startswith("feature_")]
    X, y = training_dataset_qs[features], training_dataset_qs["target"]
    clf = LogisticRegression(max_iter=1000).fit(X, y)
    roc = float(roc_auc_score(y, clf.predict_proba(X)[:, 1]))
    return dg.MaterializeResult(
        metadata={"roc_auc": round(roc, 4), "rows": len(training_dataset_qs),
                  "features": len(features)},
    )


@dg.asset_check(asset=training_dataset_qs, description="В целевой колонке нет пропусков.")
def net_propuskov_qs(training_dataset_qs: pd.DataFrame) -> dg.AssetCheckResult:
    bad = int(training_dataset_qs["target"].isna().sum())
    return dg.AssetCheckResult(passed=bad == 0, metadata={"propuski": bad})
