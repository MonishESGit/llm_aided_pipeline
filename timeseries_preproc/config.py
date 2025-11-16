from dataclasses import dataclass

@dataclass
class PreprocessingConfig:
    """
    Configuration for the time series preprocessing pipeline.
    """

    # Smoothing
    smoothing_window: int = 7  # odd integer >= 1
    smoothing_center: bool = True  # center the moving window

    # Arc normalization
    arc_normalization: bool = True

    # Peak detection
    min_peak_distance: int = 1  # minimum index distance between peaks
    # Optionally ignore tiny peaks relative to the curve's amplitude
    min_rel_height: float = 0.0  # e.g. 0.05 => ignore peaks smaller than 5% of range

    # CSV / IO
    time_index_column: str | None = None  # if there is a time column to drop
