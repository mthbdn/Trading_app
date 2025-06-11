import numpy as np

def moving_average_cross(prices, fast_period=14, slow_period=28):
    if len(prices) < slow_period + 1:
        return "Pas assez de données"
    fast_ma = np.mean(prices[-fast_period:])
    slow_ma = np.mean(prices[-slow_period:])
    if fast_ma > slow_ma:
        return "BUY"
    elif fast_ma < slow_ma:
        return "SELL"
    else:
        return "NEUTRAL"