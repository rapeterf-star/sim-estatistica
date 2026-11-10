from __future__ import annotations

import math
import re
import unicodedata
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "raw" / "sim_obitos.csv"
OUTPUT_PATH = ROOT / "data" / "processed" / "populacao_infantil.parquet"
ANOS_OBITO = range(2011, 2022)


def normalizar_texto(valor: object) -> str:
    if pd.isna(valor):
        return ""
    texto = unicodedata.normalize("NFKD", str(valor))
    texto = texto.encode("ascii", "ignore").decode("ascii").upper()
    return re.sub(r"\s+", " ", texto).strip()


def preparar_populacao() -> pd.DataFrame:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Arquivo SIM não encontrado: {CSV_PATH}")

    dados = pd.read_csv(
        CSV_PATH,
        sep=";",
        encoding="utf-8-sig",
        dtype=str,
        keep_default_na=False,
    )
    dados.insert(0, "indice_original", range(len(dados)))

    for coluna in ("sexo", "tipo_obito", "nascimento", "obito", "gestacao", "raca"):
        if coluna not in dados:
            raise ValueError(f"Coluna necessária ausente no CSV SIM: {coluna}")

    dados["tipo_obito"] = dados["tipo_obito"].map(normalizar_texto)
    dados["sexo"] = dados["sexo"].map(normalizar_texto).replace("", "NAO INFORMADO")
    dados["gestacao"] = dados["gestacao"].map(normalizar_texto).replace("", "NAO INFORMADO")
    dados["raca"] = dados["raca"].map(normalizar_texto).replace("", "NAO INFORMADO")
    nascimento = pd.to_datetime(
        dados["nascimento"].str.strip(),
        format="%m/%Y",
        errors="coerce",
    )
    obito = pd.to_datetime(
        dados["obito"].str.strip(),
        format="%m/%Y",
        errors="coerce",
    )

    idade_meses = (
        (obito.dt.year - nascimento.dt.year) * 12
        + obito.dt.month
        - nascimento.dt.month
    )
    dados["idade_obito_meses_aprox"] = idade_meses
    dados["ano_obito"] = obito.dt.year
    dados["mesma_competencia"] = idade_meses.eq(0).astype("int8")

    elegiveis = (
        dados["tipo_obito"].eq("NAO FETAL")
        & dados["ano_obito"].isin(ANOS_OBITO)
        & idade_meses.ge(0)
        & idade_meses.lt(12)
    )
    populacao = dados.loc[elegiveis].copy()
    populacao["idade_obito_meses_aprox"] = (
        populacao["idade_obito_meses_aprox"].astype("int8")
    )
    populacao["ano_obito"] = populacao["ano_obito"].astype("int16")
    populacao.sort_values("indice_original", inplace=True)

    if populacao.empty:
        raise ValueError("A definição operacional não encontrou registros elegíveis.")
    if populacao["indice_original"].duplicated().any():
        raise ValueError("O índice de origem deveria ser único.")
    if not populacao["idade_obito_meses_aprox"].between(0, 11).all():
        raise ValueError("A idade aproximada ao óbito deve estar entre 0 e 11 meses.")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    populacao.to_parquet(OUTPUT_PATH, index=False)
    return populacao


def main() -> None:
    populacao = preparar_populacao()
    n0 = 1.96**2 * 0.5 * (1 - 0.5) / 0.05**2
    n = math.ceil(n0 / (1 + (n0 - 1) / len(populacao)))
    print(f"População analítica: {len(populacao):,} registros".replace(",", "."))
    print(f"Amostra planejada: {n} registros (95% de confiança; erro de 5 p.p.)")
    print(f"População salva em: {OUTPUT_PATH}")
    print("O arquivo contém registros SIM; mantê-lo local e não o publicar.")


if __name__ == "__main__":
    main()
