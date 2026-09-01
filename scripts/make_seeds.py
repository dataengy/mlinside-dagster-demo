"""Детерминированные seed-CSV для dbt: заказы и позиции в духе Olist.

Данные синтетические, но колонки и логика те же, что в ДЗ на Olist, — чтобы
демо лекции и домашнее задание говорили на одном языке.
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

SEEDS = Path(__file__).resolve().parents[1] / "data" / "raw"


def build(seed: int, n: int = 6000) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    orders = pd.DataFrame({
        "order_id": np.arange(1, n + 1),
        "customer_state": rng.choice(["SP", "RJ", "MG", "BA", "RS"], n),
        "distance_km": np.round(rng.gamma(3.0, 90.0, n), 1),
        "seller_delay_d": rng.poisson(1.4, n),
        "freight_value": np.round(rng.gamma(2.0, 9.0, n), 2),
        "order_value": np.round(rng.gamma(3.0, 45.0, n), 2),
    })
    items = pd.DataFrame({
        "order_id": rng.choice(orders.order_id, size=int(n * 1.8)),
        "product_weight_g": np.round(rng.gamma(2.0, 600.0, int(n * 1.8)), 0),
    })
    return orders, items


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--suffix", default="")
    args = ap.parse_args()
    orders, items = build(args.seed)
    SEEDS.mkdir(parents=True, exist_ok=True)
    orders.to_csv(SEEDS / f"raw_orders{args.suffix}.csv", index=False)
    items.to_csv(SEEDS / f"raw_items{args.suffix}.csv", index=False)
    print(f"seeds: orders={len(orders)} items={len(items)} seed={args.seed}")


if __name__ == "__main__":
    main()
