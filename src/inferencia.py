from __future__ import annotations

from math import sqrt
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


ALPHA = 0.05
MEDIA_NULA_MESES = 1.0
SINASC_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "sinasc_sexo_ano.csv"
SEXO_FEMININO = "FEMININO"
SEXO_MASCULINO = "MASCULINO"
SEXOS_CONHECIDOS = {SEXO_FEMININO, SEXO_MASCULINO}


def carregar_referencia_sinasc(caminho: Path = SINASC_PATH) -> dict[str, float]:
    """Proporção de meninos entre os nascidos vivos (SINASC POA, 2011–2021).

    Usada como valor de referência externo de H1: compara a composição por
    sexo dos óbitos infantis com a composição por sexo dos nascimentos.
    """
    if not caminho.exists():
        raise FileNotFoundError(
            f"Agregado do SINASC não encontrado: {caminho}. "
            "Execute src/04_sinasc_dados_agregados.py."
        )
    nascimentos = pd.read_csv(caminho, sep=";")
    por_sexo = nascimentos.groupby("sexo")["nascidos_vivos"].sum()
    total = int(por_sexo.sum())
    return {
        "proporcao_masculina": float(por_sexo["MASCULINO"] / total),
        "nascidos_vivos": total,
        "ano_inicial": int(nascimentos["ano"].min()),
        "ano_final": int(nascimentos["ano"].max()),
    }


def _fpc(n: int, n_populacao: int) -> float:
    """Fator de correção para população finita aplicado à variância: (N − n)/(N − 1)."""
    return _fator_correcao_finita(n, n_populacao) ** 2


def _fator_correcao_finita(n: int, n_populacao: int) -> float:
    if n < 1 or n_populacao < 1 or n > n_populacao:
        raise ValueError("Tamanho amostral/populacional inválido.")
    if n_populacao == 1:
        return 0.0
    return sqrt((n_populacao - n) / (n_populacao - 1))


def _erro_padrao_proporcao(
    proporcao: float,
    n: int,
    n_populacao: int,
) -> float:
    return sqrt(proporcao * (1 - proporcao) / n * _fpc(n, n_populacao))


def _ic_proporcao(
    proporcao: float,
    n: int,
    n_populacao: int,
) -> tuple[float, float]:
    erro = _erro_padrao_proporcao(proporcao, n, n_populacao)
    z = stats.norm.ppf(1 - ALPHA / 2)
    return max(0.0, proporcao - z * erro), min(1.0, proporcao + z * erro)


def _ic_media(
    media: float,
    desvio: float,
    n: int,
    n_populacao: int,
    graus_liberdade: float,
) -> tuple[float, float]:
    erro = desvio / sqrt(n) * _fator_correcao_finita(n, n_populacao)
    critico = stats.t.ppf(1 - ALPHA / 2, graus_liberdade)
    return media - critico * erro, media + critico * erro


def _resumo_verdade_populacional(
    *,
    h0_verdadeira: bool,
    rejeita_h0: bool,
) -> str:
    if rejeita_h0 and h0_verdadeira:
        return "Erro tipo I"
    if not rejeita_h0 and not h0_verdadeira:
        return "Erro tipo II"
    if rejeita_h0:
        return "Rejeição correta de H₀"
    return "Não rejeição correta de H₀"


def _registros_por_sexo(df: pd.DataFrame, sexo: str) -> pd.DataFrame:
    return df.loc[df["sexo"].isin(SEXOS_CONHECIDOS) & df["sexo"].eq(sexo)]


def executar_inferencia(
    amostra: pd.DataFrame,
    populacao: pd.DataFrame,
    proporcao_nula: float | None = None,
) -> list[dict[str, object]]:
    """Executa H1–H4 com a amostra e compara com os parâmetros da população.

    ``proporcao_nula`` é a referência de H1; por padrão, a proporção de
    meninos entre os nascidos vivos do SINASC POA.
    """
    if proporcao_nula is None:
        proporcao_nula = carregar_referencia_sinasc()["proporcao_masculina"]
    if not 0 < proporcao_nula < 1:
        raise ValueError("A proporção de referência de H1 deve estar entre 0 e 1.")
    z_unilateral = stats.norm.ppf(1 - ALPHA)
    colunas = {"sexo", "idade_obito_meses_aprox", "mesma_competencia"}
    for nome, df in (("amostra", amostra), ("população", populacao)):
        ausentes = colunas.difference(df.columns)
        if ausentes:
            raise ValueError(f"{nome} não contém as colunas: {sorted(ausentes)}")
    if amostra.empty or populacao.empty:
        raise ValueError("A amostra e a população não podem estar vazias.")
    if len(amostra) > len(populacao):
        raise ValueError("A amostra não pode ser maior que a população.")

    n_populacao = len(populacao)
    resultados: list[dict[str, object]] = []

    conhecidos_amostra = amostra.loc[amostra["sexo"].isin(SEXOS_CONHECIDOS)]
    conhecidos_populacao = populacao.loc[populacao["sexo"].isin(SEXOS_CONHECIDOS)]
    n1 = len(conhecidos_amostra)
    N1 = len(conhecidos_populacao)
    sucessos = int(conhecidos_amostra["sexo"].eq(SEXO_MASCULINO).sum())
    proporcao = sucessos / n1
    proporcao_pop = float(
        conhecidos_populacao["sexo"].eq(SEXO_MASCULINO).mean()
    )
    erro_h1 = _erro_padrao_proporcao(proporcao_nula, n1, N1)
    z_h1 = (proporcao - proporcao_nula) / erro_h1
    p_h1 = float(stats.norm.sf(z_h1))
    ic_h1 = _ic_proporcao(proporcao, n1, N1)
    limite_h1 = proporcao - z_unilateral * _erro_padrao_proporcao(proporcao, n1, N1)
    rejeita_h1 = p_h1 < ALPHA
    h0_h1_verdadeira = proporcao_pop <= proporcao_nula
    ref_h1 = f"{proporcao_nula * 100:.2f}".replace(".", ",")
    resultados.append(
        {
            "codigo": "H1",
            "pergunta": (
                "Os meninos têm, entre os óbitos infantis, participação maior do "
                "que entre os nascimentos?"
            ),
            "variavel": "Sexo (masculino entre registros com sexo conhecido)",
            "justificativa": (
                f"A referência π₀ = {ref_h1}% é a proporção de meninos entre os "
                "nascidos vivos de Porto Alegre no SINASC (2011–2021). Se o sexo "
                "não influenciasse o óbito infantil, a composição dos óbitos "
                "repetiria a dos nascimentos; uma proporção maior indica "
                "sobremortalidade masculina relativa."
            ),
            "hipotese_nula": f"π ≤ {ref_h1}% (proporção de meninos nos nascimentos)",
            "hipotese_alternativa": f"π > {ref_h1}%",
            "referencia_nula": proporcao_nula,
            "cauda": "direita",
            "procedimento": "Teste Z unilateral de 1 proporção; IC de Wald com correção para população finita",
            "estimativa": proporcao,
            "parametro_populacional": proporcao_pop,
            "intervalo": ic_h1,
            "limite_inferior_unilateral": limite_h1,
            "estatistica": z_h1,
            "distribuicao": "normal padrão",
            "graus_liberdade": None,
            "valor_p": p_h1,
            "rejeita_h0": rejeita_h1,
            "h0_verdadeira_na_populacao": h0_h1_verdadeira,
            "contem_parametro": ic_h1[0] <= proporcao_pop <= ic_h1[1],
            "classificacao": _resumo_verdade_populacional(
                h0_verdadeira=h0_h1_verdadeira,
                rejeita_h0=rejeita_h1,
            ),
            "n_amostra": n1,
            "N_populacao": N1,
            "condicoes": [
                f"AAS sem reposição; n/N analítico = {n1 / N1:.1%}; correção para população finita aplicada.",
                f"Em H₀: {n1 * proporcao_nula:.0f} sucessos e {n1 * (1 - proporcao_nula):.0f} fracassos esperados (ambos ≥ 10).",
                "O IC bilateral de 95% descreve a estimativa; a decisão unilateral equivale a comparar π₀ com o limite inferior unilateral de 95%.",
            ],
        }
    )

    eventos_por_sexo: dict[str, tuple[int, int, float, float]] = {}
    for sexo in (SEXO_FEMININO, SEXO_MASCULINO):
        grupo_amostra = _registros_por_sexo(amostra, sexo)
        grupo_populacao = _registros_por_sexo(populacao, sexo)
        n_grupo = len(grupo_amostra)
        N_grupo = len(grupo_populacao)
        if n_grupo < 1 or N_grupo < 1:
            raise ValueError(f"Não há registros suficientes para o grupo {sexo}.")
        x_grupo = int(grupo_amostra["mesma_competencia"].sum())
        p_grupo = x_grupo / n_grupo
        p_pop_grupo = float(grupo_populacao["mesma_competencia"].mean())
        eventos_por_sexo[sexo] = (x_grupo, n_grupo, p_grupo, p_pop_grupo)

    x_f, n_f, p_f, p_f_pop = eventos_por_sexo[SEXO_FEMININO]
    x_m, n_m, p_m, p_m_pop = eventos_por_sexo[SEXO_MASCULINO]
    N_f = len(_registros_por_sexo(populacao, SEXO_FEMININO))
    N_m = len(_registros_por_sexo(populacao, SEXO_MASCULINO))
    p_pool = (x_f + x_m) / (n_f + n_m)
    erro_h2 = sqrt(
        p_pool * (1 - p_pool) * (_fpc(n_f, N_f) / n_f + _fpc(n_m, N_m) / n_m)
    )
    diferenca_h2 = p_f - p_m
    z_h2 = diferenca_h2 / erro_h2
    p_h2 = float(2 * stats.norm.sf(abs(z_h2)))
    erro_ic_h2 = sqrt(
        p_f * (1 - p_f) / n_f * _fpc(n_f, N_f)
        + p_m * (1 - p_m) / n_m * _fpc(n_m, N_m)
    )
    z_critico = stats.norm.ppf(1 - ALPHA / 2)
    ic_h2 = (
        diferenca_h2 - z_critico * erro_ic_h2,
        diferenca_h2 + z_critico * erro_ic_h2,
    )
    diferenca_h2_pop = p_f_pop - p_m_pop
    rejeita_h2 = p_h2 < ALPHA
    h0_h2_verdadeira = bool(np.isclose(diferenca_h2_pop, 0, atol=1e-12))
    resultados.append(
        {
            "codigo": "H2",
            "pergunta": "A proporção de óbitos registrados no mesmo mês do nascimento difere entre meninas e meninos?",
            "variavel": "Mesmo mês/ano de nascimento e óbito (diferença registrada de 0 mês)",
            "justificativa": (
                "O óbito no mesmo mês/ano do nascimento aproxima os óbitos mais "
                "precoces (sobretudo neonatais). A pergunta é se essa concentração "
                "precoce é diferente entre meninas e meninos."
            ),
            "cauda": "bilateral",
            "hipotese_nula": "π_feminino − π_masculino = 0",
            "hipotese_alternativa": "π_feminino − π_masculino ≠ 0",
            "procedimento": "Teste Z bilateral de 2 proporções; IC da diferença com correção para população finita",
            "estimativa": diferenca_h2,
            "parametro_populacional": diferenca_h2_pop,
            "intervalo": ic_h2,
            "estatistica": z_h2,
            "distribuicao": "normal padrão",
            "graus_liberdade": None,
            "valor_p": p_h2,
            "rejeita_h0": rejeita_h2,
            "h0_verdadeira_na_populacao": h0_h2_verdadeira,
            "contem_parametro": ic_h2[0] <= diferenca_h2_pop <= ic_h2[1],
            "classificacao": _resumo_verdade_populacional(
                h0_verdadeira=h0_h2_verdadeira,
                rejeita_h0=rejeita_h2,
            ),
            "estimativa_feminino": p_f,
            "estimativa_masculino": p_m,
            "parametro_feminino": p_f_pop,
            "parametro_masculino": p_m_pop,
            "n_amostra": (n_f, n_m),
            "N_populacao": (N_f, N_m),
            "condicoes": [
                "AAS sem reposição; as variâncias dos grupos incluem correção para população finita.",
                f"Contagens esperadas sob H₀ (feminino/masculino): {n_f * p_pool:.0f}/{n_m * p_pool:.0f} eventos e {n_f * (1 - p_pool):.0f}/{n_m * (1 - p_pool):.0f} não eventos.",
            ],
        }
    )

    idades_amostra = amostra["idade_obito_meses_aprox"].astype(float)
    idades_populacao = populacao["idade_obito_meses_aprox"].astype(float)
    n_idade = len(idades_amostra)
    media_idade = float(idades_amostra.mean())
    desvio_idade = float(idades_amostra.std(ddof=1))
    media_idade_pop = float(idades_populacao.mean())
    erro_h3 = (
        desvio_idade
        / sqrt(n_idade)
        * _fator_correcao_finita(n_idade, n_populacao)
    )
    t_h3 = (media_idade - MEDIA_NULA_MESES) / erro_h3
    gl_h3 = n_idade - 1
    p_h3 = float(stats.t.sf(t_h3, gl_h3))
    limite_h3 = media_idade - stats.t.ppf(1 - ALPHA, gl_h3) * erro_h3
    ic_h3 = _ic_media(
        media_idade,
        desvio_idade,
        n_idade,
        n_populacao,
        gl_h3,
    )
    rejeita_h3 = p_h3 < ALPHA
    h0_h3_verdadeira = media_idade_pop <= MEDIA_NULA_MESES
    resultados.append(
        {
            "codigo": "H3",
            "pergunta": (
                "Em média, o óbito infantil ocorre depois do primeiro mês "
                "de calendário após o nascimento?"
            ),
            "variavel": "Diferença entre mês/ano do óbito e do nascimento",
            "justificativa": (
                "Mais da metade dos registros tem diferença 0 (óbito no mesmo "
                "mês/ano do nascimento), o que sugere concentração no primeiro mês. "
                "A referência μ₀ = 1 mês representa um padrão em que os óbitos "
                "ocorrem, em média, até o mês seguinte ao nascimento. Rejeitar H₀ "
                "indica que os óbitos pós-neonatais deslocam a média para além "
                "desse patamar."
            ),
            "hipotese_nula": "μ ≤ 1 mês",
            "hipotese_alternativa": "μ > 1 mês",
            "referencia_nula": MEDIA_NULA_MESES,
            "cauda": "direita",
            "procedimento": "Teste t unilateral de 1 amostra; IC t com correção para população finita",
            "estimativa": media_idade,
            "parametro_populacional": media_idade_pop,
            "intervalo": ic_h3,
            "limite_inferior_unilateral": limite_h3,
            "estatistica": t_h3,
            "distribuicao": "t de Student",
            "graus_liberdade": gl_h3,
            "valor_p": p_h3,
            "rejeita_h0": rejeita_h3,
            "h0_verdadeira_na_populacao": h0_h3_verdadeira,
            "contem_parametro": ic_h3[0] <= media_idade_pop <= ic_h3[1],
            "classificacao": _resumo_verdade_populacional(
                h0_verdadeira=h0_h3_verdadeira,
                rejeita_h0=rejeita_h3,
            ),
            "desvio_amostral": desvio_idade,
            "n_amostra": n_idade,
            "N_populacao": n_populacao,
            "condicoes": [
                f"AAS sem reposição; n/N = {n_idade / n_populacao:.1%}; correção para população finita aplicada.",
                "A variável tem resolução mensal e distribuição assimétrica à direita; com n = 316 o TCL sustenta a aproximação t para a média, mas a idade é operacional e aproximada.",
                "O IC bilateral de 95% descreve a estimativa; a decisão unilateral equivale a comparar μ₀ com o limite inferior unilateral de 95%.",
            ],
        }
    )

    grupos_amostra = {
        sexo: _registros_por_sexo(amostra, sexo)["idade_obito_meses_aprox"].astype(float)
        for sexo in (SEXO_FEMININO, SEXO_MASCULINO)
    }
    grupos_populacao = {
        sexo: _registros_por_sexo(populacao, sexo)["idade_obito_meses_aprox"].astype(float)
        for sexo in (SEXO_FEMININO, SEXO_MASCULINO)
    }
    n_f, n_m = (len(grupos_amostra[sexo]) for sexo in (SEXO_FEMININO, SEXO_MASCULINO))
    N_f, N_m = (len(grupos_populacao[sexo]) for sexo in (SEXO_FEMININO, SEXO_MASCULINO))
    media_f = float(grupos_amostra[SEXO_FEMININO].mean())
    media_m = float(grupos_amostra[SEXO_MASCULINO].mean())
    media_f_pop = float(grupos_populacao[SEXO_FEMININO].mean())
    media_m_pop = float(grupos_populacao[SEXO_MASCULINO].mean())
    var_f = float(grupos_amostra[SEXO_FEMININO].var(ddof=1)) / n_f * _fpc(n_f, N_f)
    var_m = float(grupos_amostra[SEXO_MASCULINO].var(ddof=1)) / n_m * _fpc(n_m, N_m)
    erro_h4 = sqrt(var_f + var_m)
    t_h4 = (media_f - media_m) / erro_h4
    gl_h4 = (var_f + var_m) ** 2 / (
        var_f**2 / (n_f - 1) + var_m**2 / (n_m - 1)
    )
    p_h4 = float(2 * stats.t.sf(abs(t_h4), gl_h4))
    critico_h4 = stats.t.ppf(1 - ALPHA / 2, gl_h4)
    diferenca_h4 = media_f - media_m
    ic_h4 = (
        diferenca_h4 - critico_h4 * erro_h4,
        diferenca_h4 + critico_h4 * erro_h4,
    )
    diferenca_h4_pop = media_f_pop - media_m_pop
    rejeita_h4 = p_h4 < ALPHA
    h0_h4_verdadeira = bool(np.isclose(diferenca_h4_pop, 0, atol=1e-12))
    resultados.append(
        {
            "codigo": "H4",
            "pergunta": "A idade média aproximada ao óbito difere entre meninas e meninos?",
            "variavel": "Diferença entre mês/ano do óbito e do nascimento",
            "justificativa": (
                "Complementa H2 com a variável quantitativa: verifica se o momento "
                "médio do óbito infantil é diferente entre os sexos."
            ),
            "cauda": "bilateral",
            "hipotese_nula": "μ_feminino − μ_masculino = 0",
            "hipotese_alternativa": "μ_feminino − μ_masculino ≠ 0",
            "procedimento": "Teste t bilateral de Welch; IC da diferença com correção para população finita",
            "estimativa": diferenca_h4,
            "parametro_populacional": diferenca_h4_pop,
            "intervalo": ic_h4,
            "estatistica": t_h4,
            "distribuicao": "t de Student (Welch)",
            "graus_liberdade": gl_h4,
            "valor_p": p_h4,
            "rejeita_h0": rejeita_h4,
            "h0_verdadeira_na_populacao": h0_h4_verdadeira,
            "contem_parametro": ic_h4[0] <= diferenca_h4_pop <= ic_h4[1],
            "classificacao": _resumo_verdade_populacional(
                h0_verdadeira=h0_h4_verdadeira,
                rejeita_h0=rejeita_h4,
            ),
            "estimativa_feminino": media_f,
            "estimativa_masculino": media_m,
            "parametro_feminino": media_f_pop,
            "parametro_masculino": media_m_pop,
            "n_amostra": (n_f, n_m),
            "N_populacao": (N_f, N_m),
            "condicoes": [
                f"AAS sem reposição; FPC aplicada separadamente por sexo (n/N: {n_f}/{N_f} e {n_m}/{N_m}).",
                f"Cada grupo tem n > 30 ({n_f} e {n_m}); a média é analisada pela aproximação t de Welch.",
            ],
        }
    )
    for resultado in resultados:
        resultado["conclusao"] = _conclusao(resultado)
    return resultados


_CONCLUSOES = {
    ("H1", True): (
        "A amostra indica que a proporção de meninos entre os óbitos infantis é "
        "maior que entre os nascimentos, sinal de sobremortalidade masculina relativa."
    ),
    ("H1", False): (
        "A amostra não traz evidência suficiente, a 5%, de que a proporção de "
        "meninos entre os óbitos infantis supere a dos nascimentos."
    ),
    ("H2", True): (
        "A amostra indica diferença entre meninas e meninos na proporção de "
        "óbitos no mesmo mês/ano do nascimento."
    ),
    ("H2", False): (
        "A amostra não traz evidência suficiente de diferença entre os sexos na "
        "proporção de óbitos no mesmo mês/ano do nascimento."
    ),
    ("H3", True): (
        "A amostra indica que a idade média aproximada ao óbito supera 1 mês: "
        "apesar da concentração no mês do nascimento, os óbitos pós-neonatais "
        "elevam a média."
    ),
    ("H3", False): (
        "A amostra não traz evidência suficiente de que a idade média aproximada "
        "ao óbito supere 1 mês."
    ),
    ("H4", True): (
        "A amostra indica diferença entre meninas e meninos na idade média "
        "aproximada ao óbito."
    ),
    ("H4", False): (
        "A amostra não traz evidência suficiente de diferença entre os sexos na "
        "idade média aproximada ao óbito."
    ),
}

_LEITURA_POPULACIONAL = {
    "Rejeição correta de H₀": "Na população, H₀ é de fato falsa: a decisão tomada com a amostra está correta.",
    "Não rejeição correta de H₀": "Na população, H₀ é de fato verdadeira: a decisão tomada com a amostra está correta.",
    "Erro tipo I": "Na população, H₀ é verdadeira, mas a amostra levou à rejeição: erro tipo I.",
    "Erro tipo II": (
        "Na população, H₀ é falsa, mas a amostra não teve evidência suficiente "
        "para rejeitá-la: erro tipo II. O efeito real é pequeno em relação ao "
        "erro-padrão de uma amostra de 316 registros (baixo poder do teste)."
    ),
}


def _conclusao(resultado: dict[str, object]) -> dict[str, str]:
    return {
        "amostra": _CONCLUSOES[(resultado["codigo"], resultado["rejeita_h0"])],
        "populacao": _LEITURA_POPULACIONAL[resultado["classificacao"]],
    }
