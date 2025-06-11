import numpy as np

def rsi_signal(prices, period=14, overbought=70, oversold=30):
    """
    Calcule le RSI et donne un signal de trading.
    - prices : liste ou np.array de prix de clôture (float)
    - period : période du RSI (par défaut 14)
    - overbought : seuil de surachat (par défaut 70)
    - oversold : seuil de survente (par défaut 30)
    Retourne : "BUY", "SELL" ou "NEUTRAL"
    """
    if len(prices) < period + 1:
        return {"error": "Pas assez de données pour calculer le RSI."}

    closes = np.array(prices[-(period+1):])
    deltas = np.diff(closes)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])

    # Évite la division par zéro
    if avg_loss == 0:
        rsi = 100
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

    # Signal
    if rsi < oversold:
        return "BUY"
    elif rsi > overbought:
        return "SELL"
    else:
        return "NEUTRAL"