from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.amostragem import SEMENTE, sortear_amostra


ROOT = Path(__file__).resolve().parents[1]
POPULACAO_PATH = ROOT / "data" / "processed" / "populacao_infantil.parquet"
OUTPUT_PATH = ROOT / "data" / "processed" / "amostra_infantil.csv"


def main() -> None:
    if not POPULACAO_PATH.exists():
        raise FileNotFoundError(
            f"População não encontrada: {POPULACAO_PATH}. "
            "Execute primeiro src/01_preparar_populacao.py."
        )

    populacao = pd.read_parquet(POPULACAO_PATH)
    amostra = sortear_amostra(populacao)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    amostra.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"Amostra AAS sem reposição: n={len(amostra)} de N={len(populacao)}")
    print(f"Semente: {SEMENTE}; fração amostral: {len(amostra) / len(populacao):.2%}")
    print(f"Arquivo local: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
