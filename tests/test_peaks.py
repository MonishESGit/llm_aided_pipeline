import numpy as np
import pandas as pd

from timeseries_preproc.config import PreprocessingConfig
from timeseries_preproc.peaks import find_peaks_1d, annotate_peaks_dataframe


def test_find_peaks_simple():
    # Simple hill with a single peak at index 2 (value 3)
    x = np.array([1.0, 2.0, 3.0, 2.0, 1.0])
    idx, vals = find_peaks_1d(x, min_distance=1, min_rel_height=0.0)

    assert idx.size == 1
    assert idx[0] == 2
    assert np.isclose(vals[0], 3.0)


def test_find_peaks_relative_height_filter():
    # Two smaller peaks (1.0 and 0.5) and one large peak (3.0)
    x = np.array([0.0, 1.0, 0.0, 0.5, 0.0, 3.0, 0.0])

    # With min_rel_height=0.4:
    #   range = 3.0, threshold = 0 + 0.4 * 3 = 1.2
    #   -> 1.0 is below threshold, 3.0 is above
    idx, vals = find_peaks_1d(x, min_distance=1, min_rel_height=0.4)

    assert np.allclose(vals, [3.0])
    assert np.all(idx == np.array([5]))



def test_annotate_peaks_dataframe_salient_flag():
    df = pd.DataFrame(
        {
            "curveA": [0, 2, 0, 4, 0],  # peaks at 1 (2) and 3 (4)
        }
    )
    config = PreprocessingConfig(min_peak_distance=1, min_rel_height=0.0)
    annotations = annotate_peaks_dataframe(df, config)

    # We should have 2 rows for curveA
    assert annotations.shape[0] == 2
    assert set(annotations["curve_id"]) == {"curveA"}

    # Mean peak height is (2 + 4) / 2 = 3
    # So only the peak with height 4 should have is_salient=True
    salient = annotations[annotations["is_salient"]]
    assert salient.shape[0] == 1
    assert np.isclose(salient["peak_value"].iloc[0], 4.0)
