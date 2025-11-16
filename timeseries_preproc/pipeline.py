from __future__ import annotations
from typing import Tuple
import pandas as pd

from .config import PreprocessingConfig
from .io import load_timeseries_csv
from .smoothing import smooth_dataframe
from .normalization import arc_normalize_dataframe
from .peaks import annotate_peaks_dataframe


def preprocess_dataframe(
    df: pd.DataFrame,
    config: PreprocessingConfig | None = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Run the full preprocessing pipeline on an in-memory DataFrame.

    Steps:
      1. Smoothing
      2. Arc normalization (optional)
      3. Peak detection + salient peak annotation

    Parameters
    ----------
    df : pandas.DataFrame
        Columns are time series curves.
    config : PreprocessingConfig, optional
        If None, defaults are used.

    Returns
    -------
    preprocessed_df : pandas.DataFrame
        Smoothed (and optionally arc-normalized) time series.
    annotations : pandas.DataFrame
        Tidy peak annotations with columns:
            - curve_id
            - peak_index
            - peak_value
            - is_salient
    """
    if config is None:
        config = PreprocessingConfig()

    smoothed = smooth_dataframe(df, config)
    normalized = arc_normalize_dataframe(smoothed, config)
    annotations = annotate_peaks_dataframe(normalized, config)

    return normalized, annotations


def preprocess_csv(
    path,
    smoothing_window: int = 7,
    arc_normalization: bool = True,
    min_peak_distance: int = 1,
    min_rel_height: float = 0.0,
    time_index_column: str | None = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Convenience wrapper to run the pipeline starting from a CSV path.

    Parameters
    ----------
    path : str or Path
        CSV file where each column is a time series curve.
    smoothing_window : int
        Moving average window size.
    arc_normalization : bool
        Whether to apply arc length normalization after smoothing.
    min_peak_distance : int
        Minimum index distance between peaks in the same curve.
    min_rel_height : float
        Relative minimum height threshold for peak detection.
    time_index_column : str or None
        If not None, this column will be removed after reading the CSV.

    Returns
    -------
    preprocessed_df : pandas.DataFrame
        Preprocessed curves.
    annotations : pandas.DataFrame
        Peak annotations.
    """
    config = PreprocessingConfig(
        smoothing_window=smoothing_window,
        arc_normalization=arc_normalization,
        min_peak_distance=min_peak_distance,
        min_rel_height=min_rel_height,
        time_index_column=time_index_column,
    )

    df = load_timeseries_csv(path, config=config)
    return preprocess_dataframe(df, config=config)
