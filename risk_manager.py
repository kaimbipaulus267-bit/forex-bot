from config import ACCOUNT_BALANCE, RISK_PERCENT, STOP_LOSS_PIPS, PIP_VALUE_PER_STANDARD_LOT


def calculate_risk_amount():
    """
    Calculates how much money we are allowed to risk per trade.
    """
    return ACCOUNT_BALANCE * (RISK_PERCENT / 100)


def calculate_lot_size():
    """
    Calculates lot size based on account balance, risk percent, and stop loss.
    """
    risk_amount = calculate_risk_amount()

    lot_size = risk_amount / (STOP_LOSS_PIPS * PIP_VALUE_PER_STANDARD_LOT)

    return round(lot_size, 2)