"""Ресурсы демо. Оба локальные: сети, облаков и внешних API в демо нет."""

from pathlib import Path

import dagster as dg
import mlflow

from dagster_demo.project import DATA


class MLflowResource(dg.ConfigurableResource):
    """MLflow на локальном SQLite — без сервера и без сети.

    Именно SQLite, а не './mlruns': файловый backend в свежих версиях MLflow
    объявлен deprecated и падает с MlflowException. SQLite-файл лежит рядом
    с проектом, артефакты — в data/mlruns.

    Тот же самый store открывается интерфейсом:
        mlflow ui --backend-store-uri sqlite:///<...>/mlflow.db
    """

    tracking_uri: str = ""
    experiment: str = "dagster-demo"

    def _uri(self) -> str:
        return self.tracking_uri or f"sqlite:///{(DATA / 'mlflow.db').as_posix()}"

    def setup(self) -> None:
        DATA.mkdir(parents=True, exist_ok=True)
        (DATA / "mlruns").mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(self._uri())
        mlflow.set_registry_uri(self._uri())
        try:
            mlflow.set_experiment(self.experiment)
        except Exception:
            mlflow.create_experiment(
                self.experiment, artifact_location=(DATA / "mlruns").as_uri()
            )
            mlflow.set_experiment(self.experiment)

    @property
    def ui_hint(self) -> str:
        return f"mlflow ui --backend-store-uri {self._uri()}"
