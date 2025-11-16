from __future__ import annotations
import numpy as np
import pandas as pd

from .config import PreprocessingConfig


def find_peaks_1d(
    x: np.ndarray,
    min_distance: int = 1,
    min_rel_height: float = 0.0,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Very simple peak finder.

    A point i is a peak if:
    - It is strictly greater than its immediate neighbors (x[i] > x[i-1] and x[i] > x[i+1]).
    - It satisfies a relative height threshold relative to the signal's range.

    Parameters
    ----------
    x : array-like
        Input signal, shape (n,).
    min_distance : int
        Minimum index distance between consecutive peaks. Smaller peaks
        within this distance of a higher peak are removed.
    min_rel_height : float
        Minimum height relative to the global range of x.
        Example: 0.05 means peak must be at least 5% of (max(x) - min(x))
        above the minimum to be accepted.

    Returns
    -------
    peak_indices : np.ndarray
        Indices of detected peaks.
    peak_values : np.ndarray
        Heights of detected peaks.
    """
    x = np.asarray(x, dtype=float)
    n = x.size
    if n < 3:
        return np.array([], dtype=int), np.array([], dtype=float)

    # Basic local maxima
    candidates = []
    for i in range(1, n - 1):
        if x[i] > x[i - 1] and x[i] > x[i + 1]:
            candidates.append(i)

    if not candidates:
        return np.array([], dtype=int), np.array([], dtype=float)

    candidates = np.array(candidates, dtype=int)
    values = x[candidates]

    # Relative height filter
    if min_rel_height > 0.0:
        x_min = x.min()
        x_max = x.max()
        amplitude = x_max - x_min
        if amplitude > 0:
            min_abs_height = x_min + min_rel_height * amplitude
            mask = values >= min_abs_height
            candidates = candidates[mask]
            values = values[mask]

    # Enforce min_distance by greedy removal of lower peaks
    if min_distance > 1 and candidates.size > 1:
        order = np.argsort(-values)  # sort by descending height
        kept = []

        occupied = np.zeros_like(x, dtype=bool)
        for idx in order:
            i = candidates[idx]
            if not occupied[max(0, i - min_distance): min(n, i + min_distance + 1)].any():
                kept.append(idx)
                occupied[max(0, i - min_distance): min(n, i + min_distance + 1)] = True

        kept = np.array(kept, dtype=int)
        candidates = candidates[kept]
        values = values[kept]

        # Sort peaks by index
        sort_idx = np.argsort(candidates)
        candidates = candidates[sort_idx]
        values = values[sort_idx]

    return candidates, values


def annotate_peaks_dataframe(
    df: pd.DataFrame,
    config: PreprocessingConfig,
) -> pd.DataFrame:
    """
    Detect peaks for each column and keep only those with height > mean peak height
    within that same curve.

    Returns a tidy annotations DataFrame with columns:
        - curve_id (column name)
        - peak_index (position along the time axis)
        - peak_value (smoothed, normalized value at the peak)
        - is_salient (bool, height > mean height of all peaks for that curve)
    """
    rows = []

    for col in df.columns:
        y = df[col].to_numpy()
        peak_idx, peak_vals = find_peaks_1d(
            y,
            min_distance=config.min_peak_distance,
            min_rel_height=config.min_rel_height,
        )

        if peak_idx.size == 0:
            continue

        mean_height = float(peak_vals.mean())
        for i, v in zip(peak_idx, peak_vals):
            rows.append(
                {
                    "curve_id": col,
                    "peak_index": int(i),
                    "peak_value": float(v),
                    "is_salient": bool(v > mean_height),
                }
            )

    if not rows:
        return pd.DataFrame(
            columns=["curve_id", "peak_index", "peak_value", "is_salient"]
        )

    annotations = pd.DataFrame(rows)
    return annotations
