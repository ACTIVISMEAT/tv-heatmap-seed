#!/usr/bin/env python3
"""
update_heatmap.py  –  Genera/actualiza BTC_LIQ_HM.csv para Pine Seeds
Fuente de datos: Coinalyze API (gratuita, se requiere API‑Key)
"""

import os, time, requests, pandas as pd
from datetime import datetime

# 1 )  VARIABLES DE ENTORNO ---------------------------------------------------
API_KEY  = os.getenv("35019fde-cedd-4322-8137-c63d2357dfbe")           # la guardarás en Settings ▸ Secrets
SYMBOL   = "BTCUSDT_PERP.A"                  # perp de Binance agregado
INTERVAL = "daily"                           # '12hour', '6hour', etc. si deseas
BASE_URL = "https://api.coinalyze.net/v1"
CSV_PATH = "data/BTC_LIQ_HM.csv"

# 2 )  DESCARGA LIQUIDACIONES -------------------------------------------------
def fetch_liq():
    now = int(time.time())
    frm = now - 60*60*24*30                 # últimos 30 días
    resp = requests.get(
        f"{BASE_URL}/liquidation-history",
        params = {
            "symbols" : SYMBOL,
            "interval": INTERVAL,
            "from"    : frm,
            "to"      : now
        },
        headers = {"api_key": API_KEY},
        timeout  = 15
    )
    resp.raise_for_status()
    # el endpoint devuelve lista de símbolos; tomamos el primero
    rows = resp.json()[0]["history"]
    df   = pd.DataFrame(rows)
    df["t"] = pd.to_datetime(df["t"], unit="s", utc=True)
    df.rename(columns={"o":"open","h":"high","l":"low","c":"close"}, inplace=True)
    return df[["t","open","high","low","close"]]

# 3 )  ESCRIBE EN FORMATO PINE SEEDS -----------------------------------------
def export_csv(df: pd.DataFrame):
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    lines = [
        f"{int(ts.timestamp()*1000)},{o},{h},{l},{c},{c}\n"
        for ts,o,h,l,c in df.itertuples(index=False)
    ]
    with open(CSV_PATH, "w") as f:
        f.writelines(lines)

# 4 )  EJECUCIÓN --------------------------------------------------------------
if __name__ == "__main__":
    data = fetch_liq()
    export_csv(data.tail(1))         # soltar solo la barra actual (cumples 5 push/día)
    print("CSV actualizado:", data.tail(1)[["t","close"]].to_string(index=False))
