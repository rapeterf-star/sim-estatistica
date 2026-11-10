from __future__ import annotations

import math

import pandas as pd


CONFIANCA_Z = 1.96
MARGEM_ERRO = 0.05
PROPORCAO_PLANEJAMENTO = 0.5
SEMENTE = 2026


def calcular_tamanho_amostral(n_populacao: int) -> int:
    if n_populacao < 1:
        raise ValueError("O tamanho da população deve ser positivo.")
    n0 = (
        CONFIANCA_Z**2
        * PROPORCAO_PLANEJAMENTO
        * (1 - PROPORCAO_PLANEJAMENTO)
        / MARGEM_ERRO**2
    )
    return min(
        n_populacao,
        math.ceil(n0 / (1 + (n0 - 1) / n_populacao)),
    )


def sortear_amostra(populacao: pd.DataFrame) -> pd.DataFrame:
    if "indice_original" not in populacao:
        raise ValueError("A população precisa conter indice_original.")
    if populacao["indice_original"].duplicated().any():
        raise ValueError("indice_original deve identificar cada linha da população.")

    n = calcular_tamanho_amostral(len(populacao))
    amostra = populacao.sort_values("indice_original").sample(
        n=n,
        replace=False,
        random_state=SEMENTE,
    )
    return amostra.sort_values("indice_original").reset_index(drop=True)
