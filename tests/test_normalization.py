import numpy as np
import pandas as pd

from timeseries_preproc.config import PreprocessingConfig
from timeseries_preproc.normalization import (
    arc_length,
    arc_normalize_1d,
    arc_normalize_dataframe,
)


def test_arc_length_constant_signal():
    x = np.ones(5)
    L = arc_length(x)
    # Differences are zero, so each segment has length sqrt(1+0) = 1
    # There are (n-1) segments.
    assert np.isclose(L, 4.0, atol=1e-6)


def test_arc_normalization_scales_signal():
    x = np.array([0.0, 1.0, 2.0, 3.0])
    y = arc_normalize_1d(x)
    # Arc length should be positive
    assert np.isfinite(arc_length(x))
    # Normalized signal should sum to something smaller than original
    assert np.abs(y).sum() < np.abs(x).sum()


def test_arc_normalize_dataframe_structure():
    df = pd.DataFrame(
        {
            "curve1": [0.0, 1.0, 2.0, 3.0],
            "curve2": [1.0, 1.0, 1.0, 1.0],
        }
    )
    config = PreprocessingConfig(arc_normalization=True)
    norm_df = arc_normalize_dataframe(df, config)

    assert norm_df.shape == df.shape
    assert list(norm_df.columns) == list(df.columns)

    # For a constant curve [1,1,1,1], arc_length = 3,
    # so arc_normalization divides by 3 -> [1/3, 1/3, 1/3, 1/3]
    expected = np.full(4, 1.0 / 3.0)
    assert np.allclose(norm_df["curve2"].to_numpy(), expected, atol=1e-6)
