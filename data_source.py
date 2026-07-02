from config import DATA_FILE, MT5_LIVE_DATA_FILE, SIGNAL_DATA_SOURCE


def get_signal_data_file():
    """
    Returns the correct data file for signal scanning.
    """

    if SIGNAL_DATA_SOURCE == "YAHOO":
        return DATA_FILE

    if SIGNAL_DATA_SOURCE == "MT5":
        return MT5_LIVE_DATA_FILE

    raise ValueError(f"Unknown SIGNAL_DATA_SOURCE: {SIGNAL_DATA_SOURCE}")