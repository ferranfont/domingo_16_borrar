"""Descarga datos historicos de Apple (AAPL) desde Alpaca.

- Las URLs se leen de config.py
- Las claves se leen del .env
- El timeframe se controla con la variable TIMEFRAME de config.py
"""

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

import config

# --- Credenciales (.env) ---
load_dotenv()
API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

if not API_KEY or not SECRET_KEY:
    raise RuntimeError("Faltan ALPACA_API_KEY o ALPACA_SECRET_KEY en el .env")

# --- Parametros ---
SYMBOL = "AAPL"

# Mapea el TIMEFRAME del config al formato que espera Alpaca
TIMEFRAME_MAP = {
    "1m": "1Min", "5m": "5Min", "15m": "15Min", "30m": "30Min",
    "1h": "1Hour", "4h": "4Hour", "1d": "1Day", "1w": "1Week",
}
timeframe = TIMEFRAME_MAP.get(config.TIMEFRAME, config.TIMEFRAME)

# Rango de fechas: ultimo ano hasta hoy
end = datetime.now(timezone.utc)
start = end - timedelta(days=365)


def get_alpaca_data(symbol: str) -> pd.DataFrame:
    """Descarga las barras de un simbolo paginando hasta traerlas todas."""
    url = f"{config.ALPACA_DATA_ENDPOINT}/stocks/{symbol}/bars"
    headers = {
        "APCA-API-KEY-ID": API_KEY,
        "APCA-API-SECRET-KEY": SECRET_KEY,
    }
    params = {
        "timeframe": timeframe,
        "start": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "limit": 10000,
        "adjustment": "raw",
        "feed": "iex",  # feed gratuito (SIP requiere suscripcion de pago -> 403)
    }

    bars = []
    while True:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        bars.extend(data.get("bars") or [])

        next_token = data.get("next_page_token")
        if not next_token:
            break
        params["page_token"] = next_token

    if not bars:
        raise RuntimeError(f"No se han recibido datos para {symbol}")

    df = pd.DataFrame(bars)
    df = df.rename(columns={
        "t": "timestamp", "o": "open", "h": "high",
        "l": "low", "c": "close", "v": "volume",
        "n": "trades", "vw": "vwap",
    })
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.set_index("timestamp")
    return df


if __name__ == "__main__":
    df = get_alpaca_data(SYMBOL)
    print(f"Descargadas {len(df)} barras de {SYMBOL} ({timeframe})")
    print(df.head())
    print(df.tail())

    data_dir = Path(__file__).resolve().parent / "data"
    data_dir.mkdir(exist_ok=True)
    output = data_dir / f"{SYMBOL}_{config.TIMEFRAME}.csv"
    df.to_csv(output)
    print(f"Datos guardados en {output}")
