import numpy as np
import pandas as pd

from timeseries_preproc.config import PreprocessingConfig
from timeseries_preproc.pipeline import preprocess_dataframe


def test_preprocess_dataframe_end_to_end():
    # Create a simple DataFrame with two curves.
    n = 10
    t = np.arange(n)

    # curve1: one clear peak in the middle
    curve1 = np.array([0, 1, 2, 3, 4, 3, 2, 1, 0, 0], dtype=float)
    # curve2: more flat, small bump
    curve2 = np.array([0, 0, 1, 0, 0, 0, 0, 0, 0, 0], dtype=float)

    df = pd.DataFrame(
        {
            "curve1": curve1,
            "curve2": curve2,
        },
        index=t,
    )

    config = PreprocessingConfig(
        smoothing_window=3,
        smoothing_center=True,
        arc_normalization=True,
        min_peak_distance=1,
        min_rel_height=0.0,
    )

    preprocessed, annotations = preprocess_dataframe(df, config)

    # Preprocessed DataFrame should have the same shape and columns
    assert preprocessed.shape == df.shape
    assert list(preprocessed.columns) == ["curve1", "curve2"]

    # Annotations should be a DataFrame with required columns
    required_cols = {"curve_id", "peak_index", "peak_value", "is_salient"}
    assert required_cols.issubset(set(annotations.columns))

    # Any annotated curve_id should be in the original columns
    assert set(annotations["curve_id"]).issubset(set(df.columns))
