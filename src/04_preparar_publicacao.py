from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.inferencia import carregar_referencia_sinasc, executar_inferencia


ROOT = Path(__file__).resolve().parents[1]
POPULACAO_PATH = ROOT / "data" / "processed" / "populacao_infantil.parquet"
AMOSTRA_PATH = ROOT / "data" / "processed" / "amostra_infantil.csv"
OUTPUT_PATH = ROOT / "data" / "resumo_publico.json"
RAW_PATH = ROOT / "data" / "raw" / "sim_obitos.csv"
FAIXAS_IDADE = {
    "0–1 mês": (0, 1),
    "2–3 meses": (2, 3),
    "4–5 meses": (4, 5),
    "6–11 meses": (6, 11),
}
SEXOS = ("FEMININO", "MASCULINO")


def _json_default(valor: object) -> object:
    if isinstance(valor, np.generic):
        return valor.item()
    raise TypeError(f"Tipo não serializável no resumo: {type(valor).__name__}")


def _resumir_conjunto(
    dados: pd.DataFrame,
    *,
    populacao: bool,
) -> dict[str, Any]:
    idades = dados["idade_obito_meses_aprox"].astype(float)
    conhecidos = dados.loc[dados["sexo"].isin(SEXOS)]
    contagem_sexo = conhecidos["sexo"].value_counts()
    contagem_mesmo_mes = (
        conhecidos.groupby(["sexo", "mesma_competencia"], observed=True)
        .size()
        .to_dict()
    )
    idade_por_faixa = {
        nome: int(
            dados["idade_obito_meses_aprox"].between(limites[0], limites[1]).sum()
        )
        for nome, limites in FAIXAS_IDADE.items()
    }

    resumo: dict[str, Any] = {
        "n": int(len(dados)),
        "n_sexo_conhecido": int(len(conhecidos)),
        "idade": {
            "media": float(idades.mean()),
            "mediana": float(idades.median()),
            "moda": float(idades.mode().iloc[0]),
            "desvio_padrao": float(idades.std(ddof=0 if populacao else 1)),
            "variancia": float(idades.var(ddof=0 if populacao else 1)),
            "minimo": float(idades.min()),
            "q1": float(idades.quantile(0.25)),
            "q3": float(idades.quantile(0.75)),
            "maximo": float(idades.max()),
        },
        "proporcao_masculina": float(contagem_sexo.get("MASCULINO", 0) / len(conhecidos)),
        "proporcao_mesmo_mes": float(
            conhecidos["mesma_competencia"].mean()
        ),
        "frequencia_sexo": {
            sexo: int(contagem_sexo.get(sexo, 0)) for sexo in SEXOS
        },
        "frequencia_faixa_idade": idade_por_faixa,
        "mesmo_mes_por_sexo": {
            sexo: {
                "mesmo_mes": int(contagem_mesmo_mes.get((sexo, 1), 0)),
                "meses_posteriores": int(contagem_mesmo_mes.get((sexo, 0), 0)),
            }
            for sexo in SEXOS
        },
    }

    if any(valor < 10 for valor in idade_por_faixa.values()):
        raise ValueError("Uma faixa de idade tem menos de 10 registros no conjunto.")
    if any(valor < 10 for valor in resumo["frequencia_sexo"].values()):
        raise ValueError("Uma categoria de sexo tem menos de 10 registros.")
    for contagens in resumo["mesmo_mes_por_sexo"].values():
        if min(contagens.values()) < 10:
            raise ValueError("Uma célula de sexo × mesmo mês tem menos de 10 registros.")
    return resumo


def _resumir_base_completa() -> dict[str, Any]:
    """Contagens agregadas do arquivo original, para contextualizar o recorte."""
    dados = pd.read_csv(RAW_PATH, sep=";", encoding="utf-8-sig", dtype=str, keep_default_na=False)
    nao_fetal = dados["tipo_obito"].str.upper().str.strip().ne("FETAL")
    ano = pd.to_datetime(dados["obito"].str.strip(), format="%m/%Y", errors="coerce").dt.year
    por_ano = ano.value_counts().sort_index()
    return {
        "linhas": int(len(dados)),
        "variaveis": int(dados.shape[1]),
        "obitos_nao_fetais": int(nao_fetal.sum()),
        "obitos_fetais": int((~nao_fetal).sum()),
        "linhas_duplicadas": int(dados.duplicated().sum()),
        "obitos_por_ano": {str(int(k)): int(v) for k, v in por_ano.items()},
    }


def preparar_resumo_publico() -> dict[str, Any]:
    for caminho in (POPULACAO_PATH, AMOSTRA_PATH):
        if not caminho.exists():
            raise FileNotFoundError(f"Arquivo necessário não encontrado: {caminho}")

    populacao = pd.read_parquet(POPULACAO_PATH)
    amostra = pd.read_csv(AMOSTRA_PATH, encoding="utf-8-sig")
    referencia_sinasc = carregar_referencia_sinasc()
    resultados = executar_inferencia(
        amostra, populacao, referencia_sinasc["proporcao_masculina"]
    )
    resumo = {
        "titulo": "Estudo estatístico do SIM — óbitos infantis",
        "fonte": "SIM — Dados Abertos de Porto Alegre, Secretaria Municipal de Saúde",
        "url_fonte": "https://dadosabertos.poa.br/dataset/mortalidade-e-obitos",
        "periodo_obito": "2011–2021",
        "definicao_idade": (
            "Diferença entre mês/ano do óbito e do nascimento, em registros não fetais; "
            "valores de 0 a 11 meses."
        ),
        "unidade_amostral": "Linha do CSV SIM elegível pela definição operacional.",
        "N": int(len(populacao)),
        "n": int(len(amostra)),
        "semente": 2026,
        "nivel_confianca": 0.95,
        "margem_erro_planejada": 0.05,
        "proporcao_planejamento": 0.5,
        "fracao_amostral": float(len(amostra) / len(populacao)),
        "duplicatas_mantidas": True,
        "parametro_h3_mes_referencia": 1.0,
        "referencia_sinasc": referencia_sinasc,
        "base_completa": _resumir_base_completa(),
        "populacao": _resumir_conjunto(populacao, populacao=True),
        "amostra": _resumir_conjunto(amostra, populacao=False),
        "testes": resultados,
        "ressalva": (
            "Os resultados descrevem a composição dos registros de óbito infantil; "
            "não estimam risco causal de mortalidade por sexo. As datas disponíveis "
            "contêm apenas mês e ano."
        ),
    }
    OUTPUT_PATH.write_text(
        json.dumps(
            resumo,
            ensure_ascii=False,
            indent=2,
            default=_json_default,
        ),
        encoding="utf-8",
    )
    return resumo


def main() -> None:
    resumo = preparar_resumo_publico()
    print(f"Resumo agregado criado: {OUTPUT_PATH}")
    print(f"N={resumo['N']}; n={resumo['n']}; nenhum registro individual foi exportado.")


if __name__ == "__main__":
    main()
