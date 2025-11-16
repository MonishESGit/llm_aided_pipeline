import numpy as np
import pandas as pd

from .config import PreprocessingConfig


def arc_length(x: np.ndarray) -> float:
    """
    Approximate arc length of a 1D curve y(t) where t is uniform.

    Arc length L ≈ sum sqrt(1 + (dy/dt)^2).
    """
    x = np.asarray(x, dtype=float)
    if x.size < 2:
        return 0.0
    dy = np.diff(x)
    # dt = 1, so dy/dt = dy
    seg_lengths = np.sqrt(1.0 + dy * dy)
    return float(seg_lengths.sum())


def arc_normalize_1d(x: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """
    Normalize a curve by its arc length.

    Output: x / L, where L is the arc length.
    """
    L = arc_length(x)
    if L < eps:
        return x * 0.0
    return x / L


def arc_normalize_dataframe(
    df: pd.DataFrame,
    config: PreprocessingConfig,
) -> pd.DataFrame:
    """
    Apply arc length normalization to each column in the DataFrame.
    """
    if not config.arc_normalization:
        return df.copy()

    norm_cols = {}
    for col in df.columns:
        arr = df[col].to_numpy()
        norm_cols[col] = arc_normalize_1d(arr)

    return pd.DataFrame(norm_cols, index=df.index)
