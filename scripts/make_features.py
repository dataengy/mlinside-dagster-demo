"""Витрина признаков для демо: маленькая, детерминированная, обучается за секунды."""
import numpy as np, pandas as pd, sys

n, seed = 4000, int(sys.argv[1]) if len(sys.argv) > 1 else 7
rng = np.random.default_rng(seed)
X = rng.normal(size=(n, 6))
w = np.array([1.4, -0.9, 0.6, 0.0, 0.3, -1.1])
p = 1 / (1 + np.exp(-(X @ w)))
df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(6)])
df["target"] = (rng.uniform(size=n) < p).astype(int)
df["split"] = np.where(rng.uniform(size=n) < 0.8, "train", "test")
df.to_parquet(sys.argv[2] if len(sys.argv) > 2 else "data/features.parquet")
print(f"rows={len(df)} seed={seed}")
