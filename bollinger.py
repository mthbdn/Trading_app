import numpy as np

def bollinger_signal(prices, period=20, stddev=2):
    if len(prices) < period:
        return "Pas assez de données"
    mean = np.mean(prices[-period:])
    std = np.std(prices[-period:])
    upper = mean + stddev * std
    lower = mean - stddev * std
    price = prices[-1]
    if price > upper:
        return "SELL"
    elif price < lower:
        return "BUY"
    else:
        return "NEUTRAL"