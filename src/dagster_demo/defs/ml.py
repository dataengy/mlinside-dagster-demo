"""DEMO 3: ML lifecycle как продолжение того же графа.

    feature_mart → training_dataset → trained_model → evaluation → registered_model

Обучение занимает секунды — это требование к демо, а не случайность: маленькая
выборка и простая модель. Долгое обучение на записи ломает показ.
"""

import dagster as dg
import duckdb
import mlflow
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

from dagster_demo.project import DATA
from dagster_demo.resources import MLflowResource

FEATURES = ["freight_ratio", "distance_km", "n_items", "seller_delay_d"]
MODEL_NAME = "olist_delay"


@dg.asset(
    deps=[dg.AssetKey("feature_mart")],   # ← шов между dbt-миром и ML-миром
    group_name="ml",
    compute_kind="pandas",
    code_version="1",
    description="Обучающая выборка: строки витрины со split == train.",
)
def training_dataset() -> dg.Output[pd.DataFrame]:
    with duckdb.connect(str(DATA / "warehouse.duckdb"), read_only=True) as con:
        df = con.execute("select * from feature_mart where split = 'train'").df()
    return dg.Output(df, metadata={"rows": len(df), "features": len(FEATURES)})


@dg.asset(
    group_name="ml",
    compute_kind="sklearn",
    code_version="1",
    description="Обученная модель. Метаданные несут ССЫЛКУ в MLflow, а не копию метрик.",
)
def trained_model(
    context: dg.AssetExecutionContext,
    training_dataset: pd.DataFrame,
    mlflow_res: MLflowResource,
    config: dg.PermissiveConfig,
) -> dg.Output[dict]:
    mlflow_res.setup()
    # Гиперпараметр вынесен в одну строку — в демо он меняется ровно одним движением.
    C = float(getattr(config, "C", 1.0))
    X, y = training_dataset[FEATURES], training_dataset["target"]
    with mlflow.start_run() as run:
        clf = LogisticRegression(max_iter=1000, C=C).fit(X, y)
        roc = float(roc_auc_score(y, clf.predict_proba(X)[:, 1]))
        mlflow.log_param("C", C)
        mlflow.log_metric("roc_auc", roc)
        info = mlflow.sklearn.log_model(clf, name="model")
        run_id, model_uri = run.info.run_id, info.model_uri
    context.log.info(f"MLflow: {mlflow_res.ui_hint}")
    return dg.Output(
        {"run_id": run_id, "model_uri": model_uri, "roc_auc": roc, "C": C},
        metadata={
            "mlflow_run_id": run_id,
            "model_uri": model_uri,
            "roc_auc": round(roc, 4),
            "C": C,
            "preview": dg.MetadataValue.md(
                "| признак | вес |\n|---|---|\n"
                + "\n".join(f"| {f} | {w:.3f} |" for f, w in zip(FEATURES, clf.coef_[0]))
            ),
        },
    )


@dg.asset(
    group_name="ml",
    compute_kind="sklearn",
    code_version="1",
    description="Оценка на отложенной выборке — отдельный ассет, а не шаг внутри обучения.",
)
def evaluation(
    trained_model: dict, mlflow_res: MLflowResource
) -> dg.Output[dict]:
    mlflow_res.setup()
    with duckdb.connect(str(DATA / "warehouse.duckdb"), read_only=True) as con:
        test = con.execute("select * from feature_mart where split = 'test'").df()
    clf = mlflow.sklearn.load_model(trained_model["model_uri"])
    roc = float(roc_auc_score(test["target"], clf.predict_proba(test[FEATURES])[:, 1]))
    passed = roc >= 0.70
    return dg.Output(
        {"roc_auc_test": roc, "passed": passed},
        metadata={"roc_auc_test": round(roc, 4), "rows": len(test), "shluz_projden": passed},
    )


@dg.asset(
    group_name="ml",
    compute_kind="mlflow",
    code_version="1",
    description="Регистрация версии в реестре MLflow. Версией владеет MLflow, Dagster хранит ссылку.",
)
def registered_model(
    trained_model: dict, evaluation: dict, mlflow_res: MLflowResource
) -> dg.MaterializeResult:
    if not evaluation["passed"]:
        raise dg.Failure(
            description="Шлюз качества не пройден — в проде остаётся старая версия.",
            metadata={"roc_auc_test": evaluation["roc_auc_test"]},
        )
    mlflow_res.setup()
    version = mlflow.register_model(trained_model["model_uri"], MODEL_NAME)
    return dg.MaterializeResult(
        metadata={
            "model_name": MODEL_NAME,
            "model_version": int(version.version),
            "model_uri": f"models:/{MODEL_NAME}/{version.version}",
            "mlflow_run_id": trained_model["run_id"],
        },
    )


@dg.asset_check(asset=training_dataset, description="В целевой колонке нет пропусков.")
def net_propuskov(training_dataset: pd.DataFrame) -> dg.AssetCheckResult:
    bad = int(training_dataset["target"].isna().sum())
    return dg.AssetCheckResult(passed=bad == 0, metadata={"propuski": bad})
