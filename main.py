"""Punto de entrada: ejecuta de forma secuencial la descarga de datos y su graficado."""

import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent

PASOS = [
    ("Descarga de datos", BASE / "get_alpaca_data.py"),
    ("Graficado", BASE / "plot_chart.py"),
]


def main() -> None:
    for nombre, script in PASOS:
        print(f"\n=== {nombre} ({script.name}) ===", flush=True)
        resultado = subprocess.run([sys.executable, str(script)])
        if resultado.returncode != 0:
            print(f"Error en el paso '{nombre}'. Se detiene la ejecucion.")
            sys.exit(resultado.returncode)

    print("\nProceso completado correctamente.")


if __name__ == "__main__":
    main()
