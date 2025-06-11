def get_open_positions_and_pnl(client):
    balances = client.get_account()["balances"]
    result = []
    for b in balances:
        asset = b["asset"]
        qty = float(b["free"]) + float(b["locked"])
        if asset in ("USDT", "BUSD") or qty == 0:
            continue
        symbol = asset + "USDT"
        try:
            trades = client.get_my_trades(symbol=symbol)
            total_cost = sum(float(t["qty"]) * float(t["price"]) for t in trades if t["isBuyer"])
            total_qty = sum(float(t["qty"]) for t in trades if t["isBuyer"])
            if total_qty == 0:
                continue
            avg_buy_price = total_cost / total_qty
            ticker = client.get_symbol_ticker(symbol=symbol)
            last_price = float(ticker["price"])
            pnl = (last_price - avg_buy_price) * qty
            result.append({"symbol": symbol, "qty": qty, "buy_price": avg_buy_price, "last_price": last_price, "pnl": pnl})
        except Exception:
            continue
    return result