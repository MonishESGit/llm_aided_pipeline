import numpy as np
import pandas as pd

from timeseries_preproc.config import PreprocessingConfig
from timeseries_preproc.smoothing import moving_average_1d, smooth_dataframe


def test_moving_average_simple():
    x = np.array([1, 2, 3, 4, 5], dtype=float)
    # For window=3 and reflect padding, we just check the length
    # and basic average behavior in the center.
    y = moving_average_1d(x, window=3, center=True)

    assert y.shape == x.shape
    # Check central point explicitly: (1+2+3)/3 = 2
    assert np.isclose(y[2], (2 + 3 + 4) / 3.0, atol=1e-6)


def test_moving_average_window_one_no_change():
    x = np.array([1, 2, 3, 4, 5], dtype=float)
    y = moving_average_1d(x, window=1, center=True)
    assert np.allclose(x, y)


def test_smooth_dataframe_shape_and_columns():
    df = pd.DataFrame(
        {
            "curve1": [1, 2, 3, 4, 5],
            "curve2": [5, 4, 3, 2, 1],
        }
    )

    config = PreprocessingConfig(smoothing_window=3, smoothing_center=True)
    smoothed = smooth_dataframe(df, config)

    assert smoothed.shape == df.shape
    assert list(smoothed.columns) == ["curve1", "curve2"]
