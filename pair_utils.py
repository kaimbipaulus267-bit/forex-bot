from config import SYMBOL


def is_jpy_pair(symbol=None):
    """
    Checks if the forex pair is a JPY pair.
    JPY pairs usually use 0.01 as pip size.
    """

    if symbol is None:
        symbol = SYMBOL

    symbol = symbol.upper()

    return "JPY" in symbol


def get_pip_size(symbol=None):
    """
    Returns the correct pip size for the selected forex pair.
    """

    if is_jpy_pair(symbol):
        return 0.01

    return 0.0001