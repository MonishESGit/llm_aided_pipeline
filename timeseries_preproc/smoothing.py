import numpy as np
import pandas as pd

from .config import PreprocessingConfig


def moving_average_1d(x: np.ndarray, window: int, center: bool = True) -> np.ndarray:
    """
    Simple moving average for a 1D array.

    Uses 'reflect' padding to avoid shrinking the signal at the edges.

    Parameters
    ----------
    x : array-like
        Input signal, shape (n,).
    window : int
        Window size, must be >= 1.
    center : bool
        If True, window is centered around each element.
        If False, uses a trailing window.

    Returns
    -------
    smoothed : np.ndarray
        Smoothed signal, same shape as x.
    """
    x = np.asarray(x, dtype=float)
    if window <= 1:
        return x.copy()
    if window % 2 == 0 and center:
        raise ValueError("For centered smoothing, window must be odd.")

    pad = window - 1 if not center else window // 2

    # Reflect padding
    x_padded = np.pad(x, pad_width=pad, mode="reflect")
    kernel = np.ones(window, dtype=float) / window
    conv = np.convolve(x_padded, kernel, mode="valid")

    # For center=True with odd window, 'valid' result already aligned
    # with original indices.
    return conv


def smooth_dataframe(
    df: pd.DataFrame,
    config: PreprocessingConfig,
) -> pd.DataFrame:
    """
    Apply moving average smoothing to each column in the DataFrame.
    """
    win = config.smoothing_window
    center = config.smoothing_center

    smoothed_columns = {}
    for col in df.columns:
        series = df[col].to_numpy()
        smoothed = moving_average_1d(series, window=win, center=center)
        smoothed_columns[col] = smoothed

    return pd.DataFrame(smoothed_columns, index=df.index)
