"""Dibuja el precio de cierre de AAPL y guarda un PNG en charts/."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

import config

BASE = Path(__file__).resolve().parent
SYMBOL = "AAPL"

csv_path = BASE / "data" / f"{SYMBOL}_{config.TIMEFRAME}.csv"
charts_dir = BASE / "charts"
charts_dir.mkdir(exist_ok=True)

# --- Cargar datos ---
df = pd.read_csv(csv_path, parse_dates=["timestamp"], index_col="timestamp")

# --- Grafico del precio close ---
fig, ax = plt.subplots(figsize=(14, 7))
ax.plot(df.index, df["close"], color="#1f77b4", linewidth=1.2, label="Close")

ax.set_title(f"{SYMBOL} - Precio de cierre ({config.TIMEFRAME})")
ax.set_xlabel("Fecha")
ax.set_ylabel("Precio (USD)")
ax.grid(True, alpha=0.3)
ax.legend()
fig.tight_layout()

# --- Guardar PNG ---
output = charts_dir / f"{SYMBOL}_{config.TIMEFRAME}_close.png"
fig.savefig(output, dpi=150)
print(f"Grafico guardado en {output}")
