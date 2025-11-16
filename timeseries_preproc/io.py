from pathlib import Path
from typing import Union, Optional
import pandas as pd

from .config import PreprocessingConfig

PathLike = Union[str, Path]


def load_timeseries_csv(
    path: PathLike,
    config: Optional[PreprocessingConfig] = None,
) -> pd.DataFrame:
    """
    Load a CSV where each column is a univariate time series.

    Parameters
    ----------
    path : str or Path
        Path to CSV.
    config : PreprocessingConfig, optional
        If provided and config.time_index_column is not None, that column
        will be removed and the rest treated as time series.

    Returns
    -------
    df : pandas.DataFrame
        Columns are different time series curves.
        Index is the original row index in the CSV.
    """
    df = pd.read_csv(path, index_col = 0)
    if config is not None and config.time_index_column is not None:
        if config.time_index_column in df.columns:
            df = df.drop(columns=[config.time_index_column])

    # Ensure numeric dtype where possible
    df = df.apply(pd.to_numeric, errors="coerce")

    return df
