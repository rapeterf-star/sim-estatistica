from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy import stats


ROOT = Path(__file__).resolve().parents[1]
RESUMO_PATH = ROOT / "data" / "resumo_publico.json"
ROTULOS_FAIXA = ["0–1 mês", "2–3 meses", "4–5 meses", "6–11 meses"]
ALPHA = 0.05


@st.cache_data
def carregar_resumo() -> dict:
    if not RESUMO_PATH.exists():
        raise FileNotFoundError(
            f"Resumo agregado não encontrado: {RESUMO_PATH}. "
            "Execute python src/04_preparar_publicacao.py."
        )
    with RESUMO_PATH.open("r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def formatar_numero(valor: float, casas: int = 2) -> str:
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def formatar_percentual(valor: float, casas: int = 1) -> str:
    return f"{formatar_numero(valor * 100, casas)}%"


def _frequencia_selecionada(dados: dict, variavel: str) -> pd.DataFrame:
    if variavel == "Sexo":
        return pd.DataFrame(
            {
                "Categoria": ["Meninas", "Meninos"],
                "Registros": [
                    dados["frequencia_sexo"]["FEMININO"],
                    dados["frequencia_sexo"]["MASCULINO"],
                ],
            }
        )
    if variavel == "Idade aproximada ao óbito":
        return pd.DataFrame(
            {
                "Categoria": ROTULOS_FAIXA,
                "Registros": [
                    dados["frequencia_faixa_idade"][faixa]
                    for faixa in ROTULOS_FAIXA
                ],
            }
        )
    return pd.DataFrame(
        {
            "Categoria": ["Mesmo mês/ano", "Diferença de 1–11 meses"],
            "Registros": [
                sum(
                    dados["mesmo_mes_por_sexo"][sexo]["mesmo_mes"]
                    for sexo in ("FEMININO", "MASCULINO")
                ),
                sum(
                    dados["mesmo_mes_por_sexo"][sexo]["meses_posteriores"]
                    for sexo in ("FEMININO", "MASCULINO")
                ),
            ],
        }
    )


def renderizar_descritiva(dados: dict, titulo: str, prefixo: str) -> None:
    idade = dados["idade"]
    with st.container(horizontal=True):
        st.metric("Registros", f"{dados['n']:,}".replace(",", "."), border=True)
        st.metric(
            "Idade média aproximada",
            f"{formatar_numero(idade['media'])} meses",
            border=True,
        )
        st.metric(
            "DP da idade",
            f"{formatar_numero(idade['desvio_padrao'])} meses",
            border=True,
        )
        st.metric(
            "Proporção masculina",
            formatar_percentual(dados["proporcao_masculina"]),
            border=True,
        )

    st.subheader(f"Distribuição — {titulo}")
    coluna_distribuicao, coluna_medidas = st.columns(2)
    with coluna_distribuicao:
        with st.container(border=True):
            st.markdown("**Variáveis qualitativas**")
            variavel = st.selectbox(
                "Variável qualitativa",
                [
                    "Sexo",
                    "Idade aproximada ao óbito",
                    "Mês/ano do óbito vs. nascimento",
                ],
                key=f"{prefixo}_variavel",
            )
            frequencias = _frequencia_selecionada(dados, variavel)
            frequencias["Proporção"] = (
                frequencias["Registros"] / frequencias["Registros"].sum()
            )
            st.bar_chart(frequencias.set_index("Categoria")[["Registros"]])
            st.dataframe(
                frequencias.assign(
                    Proporção=frequencias["Proporção"].map(formatar_percentual)
                ),
                hide_index=True,
                width="stretch",
            )

    with coluna_medidas:
        with st.container(border=True):
            st.markdown("**Idade aproximada ao óbito**")
            medidas = [
                ("Observações válidas", f"{dados['n']:,}".replace(",", ".")),
                ("Média", formatar_numero(idade["media"])),
                ("Mediana", formatar_numero(idade["mediana"])),
                ("Moda", formatar_numero(idade["moda"])),
                ("Desvio-padrão", formatar_numero(idade["desvio_padrao"])),
                ("Variância", formatar_numero(idade["variancia"])),
                ("Mínimo", formatar_numero(idade["minimo"])),
                ("Q1", formatar_numero(idade["q1"])),
                ("Q3", formatar_numero(idade["q3"])),
                ("Máximo", formatar_numero(idade["maximo"])),
            ]
            st.dataframe(
                pd.DataFrame(medidas, columns=["Medida", "Valor"]),
                hide_index=True,
                width="stretch",
            )
    st.caption(
        "A idade é uma diferença de mês/ano, não uma idade exata em dias. "
        "O valor 0 significa nascimento e óbito registrados na mesma competência."
    )


def renderizar_comparacao(resumo: dict) -> None:
    populacao = resumo["populacao"]
    amostra = resumo["amostra"]
    configuracoes = (
        ("Média da idade aproximada", "media", " meses", False),
        ("Proporção masculina", "proporcao_masculina", "", True),
        ("Óbito no mesmo mês/ano", "proporcao_mesmo_mes", "", True),
    )
    with st.container(horizontal=True):
        for titulo, chave, unidade, percentual in configuracoes:
            valor_pop = (
                populacao["idade"]["media"]
                if chave == "media"
                else populacao[chave]
            )
            valor_amostra = (
                amostra["idade"]["media"]
                if chave == "media"
                else amostra[chave]
            )
            exibicao = formatar_percentual if percentual else formatar_numero
            diferenca_exibicao = (
                f"{formatar_numero((valor_amostra - valor_pop) * 100, 2)} p.p."
                if percentual
                else f"{formatar_numero(valor_amostra - valor_pop)}{unidade}"
            )
            st.metric(
                titulo,
                exibicao(valor_amostra) + unidade,
                delta=f"{diferenca_exibicao} vs. população",
                border=True,
            )

    categorias = ["0–1 mês", "2–3 meses", "4–5 meses", "6–11 meses"]
    comparacao_idade = pd.DataFrame(
        {
            "População": [
                populacao["frequencia_faixa_idade"][faixa] / populacao["n"]
                for faixa in categorias
            ],
            "Amostra": [
                amostra["frequencia_faixa_idade"][faixa] / amostra["n"]
                for faixa in categorias
            ],
        },
        index=categorias,
    )
    st.subheader("Distribuição etária: população × amostra")
    st.bar_chart(comparacao_idade)

    tabela = pd.DataFrame(
        [
            {
                "Medida": "Idade média aproximada (meses)",
                "População": populacao["idade"]["media"],
                "Amostra": amostra["idade"]["media"],
            },
            {
                "Medida": "Proporção masculina",
                "População": populacao["proporcao_masculina"],
                "Amostra": amostra["proporcao_masculina"],
            },
            {
                "Medida": "Proporção no mesmo mês/ano",
                "População": populacao["proporcao_mesmo_mes"],
                "Amostra": amostra["proporcao_mesmo_mes"],
            },
        ]
    )
    st.dataframe(tabela, hide_index=True, width="stretch")
    st.caption(
        "Diferenças entre população e amostra são esperadas pela variabilidade "
        "do sorteio; os intervalos de confiança são apresentados no Painel 3."
    )


def _curva_referencia(resultado: dict) -> go.Figure:
    graus = resultado["graus_liberdade"]
    distribuicao = (
        stats.norm
        if resultado["distribuicao"] == "normal padrão"
        else stats.t(df=graus)
    )
    limite = max(4.5, abs(resultado["estatistica"]) * 1.1)
    x = np.linspace(-limite, limite, 1200)
    y = distribuicao.pdf(x)
    figura = go.Figure()
    figura.add_trace(
        go.Scatter(x=x, y=y, mode="lines", name="Distribuição sob H₀")
    )
    figura.add_vline(
        x=resultado["estatistica"],
        line_dash="dash",
        line_color="#d62728",
        annotation_text="Estatística observada",
    )
    unilateral = resultado.get("cauda") == "direita"
    critico = distribuicao.ppf(1 - ALPHA if unilateral else 1 - ALPHA / 2)
    if unilateral:
        figura.add_vrect(
            x0=critico,
            x1=float(x.max()),
            fillcolor="rgba(214,39,40,0.18)",
            line_width=0,
        )
        figura.add_vline(x=critico, line_dash="dot", line_color="#d62728")
    else:
        figura.add_vrect(
            x0=float(x.min()),
            x1=-critico,
            fillcolor="rgba(214,39,40,0.18)",
            line_width=0,
        )
        figura.add_vrect(
            x0=critico,
            x1=float(x.max()),
            fillcolor="rgba(214,39,40,0.18)",
            line_width=0,
        )
        figura.add_vline(x=-critico, line_dash="dot", line_color="#d62728")
        figura.add_vline(x=critico, line_dash="dot", line_color="#d62728")
    figura.update_layout(
        title="Distribuição de referência e região de rejeição (α = 5%)",
        xaxis_title="Estatística padronizada",
        yaxis_title="Densidade",
        height=340,
        margin={"l": 10, "r": 10, "t": 55, "b": 10},
    )
    return figura


def _formatar_estimativa(resultado: dict, valor: float) -> str:
    codigo = resultado["codigo"]
    if codigo == "H1":
        return formatar_percentual(valor)
    if codigo == "H2":
        return f"{formatar_numero(valor * 100, 2)} p.p."
    return f"{formatar_numero(valor, 3)} meses"


def renderizar_teste(resultado: dict) -> None:
    st.header(f"{resultado['codigo']} — {resultado['pergunta']}")
    st.markdown(
        f"**Variável:** {resultado['variavel']}  \n"
        f"**Hipóteses:** H₀: {resultado['hipotese_nula']} · "
        f"H₁: {resultado['hipotese_alternativa']} · **α = 5%**  \n"
        f"**Procedimento:** {resultado['procedimento']}"
    )
    if resultado.get("justificativa"):
        st.caption(f"**Por que esta hipótese?** {resultado['justificativa']}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Estimativa amostral",
            _formatar_estimativa(resultado, resultado["estimativa"]),
        )
        st.metric(
            "Parâmetro na população",
            _formatar_estimativa(resultado, resultado["parametro_populacional"]),
        )
    with col2:
        st.metric(
            "Intervalo de confiança de 95%",
            f"[{_formatar_estimativa(resultado, resultado['intervalo'][0])}; "
            f"{_formatar_estimativa(resultado, resultado['intervalo'][1])}]",
        )
        st.metric(
            "IC contém o parâmetro?",
            "Sim" if resultado["contem_parametro"] else "Não",
        )
        if resultado.get("limite_inferior_unilateral") is not None:
            st.metric(
                "Limite inferior unilateral (95%)",
                _formatar_estimativa(resultado, resultado["limite_inferior_unilateral"]),
                help=(
                    "Coerente com o teste unilateral: rejeita-se H₀ quando este "
                    "limite fica acima do valor de referência."
                ),
            )
    with col3:
        gl = resultado.get("graus_liberdade")
        rotulo = "Estatística Z" if gl is None else f"Estatística t (gl = {formatar_numero(gl, 1 if gl % 1 else 0)})"
        st.metric(rotulo, formatar_numero(resultado["estatistica"], 3))
        st.metric("Valor-p", f"{resultado['valor_p']:.4g}")
    if resultado["codigo"] == "H2":
        st.caption(
            f"Proporção no mesmo mês: meninas "
            f"{formatar_percentual(resultado['estimativa_feminino'])} "
            f"(população {formatar_percentual(resultado['parametro_feminino'])}); "
            f"meninos {formatar_percentual(resultado['estimativa_masculino'])} "
            f"(população {formatar_percentual(resultado['parametro_masculino'])})."
        )
    elif resultado["codigo"] == "H4":
        st.caption(
            f"Média aproximada: meninas "
            f"{formatar_numero(resultado['estimativa_feminino'], 3)} "
            f"(população {formatar_numero(resultado['parametro_feminino'], 3)}) meses; "
            f"meninos {formatar_numero(resultado['estimativa_masculino'], 3)} "
            f"(população {formatar_numero(resultado['parametro_masculino'], 3)}) meses."
        )
    decisao = "Rejeitamos H₀" if resultado["rejeita_h0"] else "Não rejeitamos H₀"
    st.markdown(
        f"**Decisão:** {decisao} (valor-p "
        f"{'<' if resultado['valor_p'] < ALPHA else '≥'} 0,05)."
    )
    st.plotly_chart(
        _curva_referencia(resultado),
        width="stretch",
        key=f"curva_{resultado['codigo']}",
    )
    with st.expander("Condições de aplicação"):
        for condicao in resultado["condicoes"]:
            st.write(f"- {condicao}")
    conclusao = resultado.get("conclusao", {})
    col_amostra, col_populacao = st.columns(2)
    with col_amostra:
        st.info(f"**Conclusão com a amostra.** {conclusao.get('amostra', '')}")
    with col_populacao:
        aviso = st.success if "correta" in resultado["classificacao"] else st.warning
        aviso(
            f"**Conferência com a população — {resultado['classificacao']}.** "
            f"{conclusao.get('populacao', '')}"
        )


def renderizar_inferencia(resumo: dict) -> None:
    resultados = resumo["testes"]

    def resumo_tabela(resultado: dict) -> dict[str, str]:
        inferior, superior = resultado["intervalo"]
        return {
            "Hipótese": resultado["codigo"],
            "Parâmetro populacional": _formatar_estimativa(
                resultado, resultado["parametro_populacional"]
            ),
            "Estimativa amostral": _formatar_estimativa(
                resultado, resultado["estimativa"]
            ),
            "IC de 95%": (
                f"[{_formatar_estimativa(resultado, inferior)}; "
                f"{_formatar_estimativa(resultado, superior)}]"
            ),
            "IC contém o parâmetro?": (
                "Sim" if resultado["contem_parametro"] else "Não"
            ),
            "Valor-p": f"{resultado['valor_p']:.4g}",
            "Decisão": "Rejeita H₀" if resultado["rejeita_h0"] else "Não rejeita H₀",
            "Conferência com a população": resultado["classificacao"],
        }

    st.markdown(
        f"Os quatro testes usam a amostra aleatória simples de {resumo['n']} "
        f"registros. O nível de significância é **α = 5%**. As estimativas e "
        "os intervalos são comparados aos parâmetros calculados diretamente "
        "na população."
    )
    st.subheader("Resumo dos resultados")
    st.dataframe(
        [resumo_tabela(resultado) for resultado in resultados],
        hide_index=True,
        width="stretch",
    )
    st.caption(
        "Não rejeitar H₀ não significa provar que ela é verdadeira. Os testes "
        "descrevem a composição dos registros elegíveis, não o risco causal "
        "de mortalidade."
    )
    for resultado in resultados:
        st.divider()
        renderizar_teste(resultado)
    st.divider()
    renderizar_limitacoes(resumo)


def renderizar_limitacoes(resumo: dict) -> None:
    st.header("Variabilidade amostral e limitações")
    contidos = sum(r["contem_parametro"] for r in resumo["testes"])
    h1 = next(r for r in resumo["testes"] if r["codigo"] == "H1")
    efeito_h1 = (h1["parametro_populacional"] - h1["referencia_nula"]) * 100
    leitura_h1 = (
        "A não rejeição de H₀ em H1 é um erro tipo II, que só se identifica "
        "porque a população está disponível."
        if h1["classificacao"] == "Erro tipo II"
        else f"Em H1, a decisão foi: {h1['classificacao'].lower()}."
    )
    itens = [
        f"**Estimativas pontuais × parâmetros:** nenhuma estimativa coincide "
        f"exatamente com o parâmetro populacional, como esperado; {contidos} dos "
        f"{len(resumo['testes'])} intervalos de 95% contêm o parâmetro. Em "
        "repetidos sorteios, cerca de 5% dos intervalos não o conteriam.",
        f"**Poder do teste:** com n = {resumo['n']}, efeitos pequenos (como a "
        f"diferença de {formatar_numero(efeito_h1, 1)} p.p., na população, entre "
        "a proporção de meninos nos óbitos e nos nascimentos) podem não ser "
        f"detectados. {leitura_h1}",
        "**Hipóteses de igualdade (H2 e H4):** em população finita, uma "
        "diferença exatamente zero quase nunca ocorre, por isso a não rejeição "
        "aparece formalmente como erro tipo II. As diferenças populacionais, "
        "porém, são pequenas demais para ter relevância prática.",
        "**Idade aproximada:** a base tem só mês/ano; o valor 0 não equivale "
        "ao período neonatal, e óbitos com 12 meses de calendário mas menos de "
        "1 ano de vida ficam fora da população.",
        "**Registros, não pessoas:** linhas duplicadas foram mantidas e a "
        "base contém apenas óbitos; os testes descrevem a composição dos "
        "registros e não estimam risco causal de morte por sexo.",
    ]
    st.markdown("\n".join(f"- {item}" for item in itens))


def renderizar_contexto_base(resumo: dict) -> None:
    base = resumo.get("base_completa")
    if not base:
        return
    st.subheader("Da base completa à população analisada")
    with st.container(horizontal=True):
        st.metric("Linhas no arquivo SIM", f"{base['linhas']:,}".replace(",", "."), border=True)
        st.metric("Variáveis", base["variaveis"], border=True)
        st.metric("Óbitos não fetais", f"{base['obitos_nao_fetais']:,}".replace(",", "."), border=True)
        st.metric("Óbitos infantis (população)", f"{resumo['N']:,}".replace(",", "."), border=True)
    st.markdown(
        "A base completa reúne todos os óbitos registrados em Porto Alegre "
        f"({base['linhas']:,} linhas e {base['variaveis']} variáveis). ".replace(",", ".")
        + "Este estudo recorta os **óbitos infantis** (menos de 1 ano), um "
        "indicador clássico de saúde pública, porque permite comparar a "
        "composição por sexo dos óbitos com a dos nascimentos registrados no "
        "SINASC. Os óbitos fetais e os de pessoas com 1 ano ou mais ficam fora "
        "da população analisada."
    )
    por_ano = base.get("obitos_por_ano")
    if por_ano:
        st.bar_chart(
            pd.DataFrame({"Óbitos (todas as idades)": por_ano}),
            x_label="Ano do óbito",
            y_label="Registros",
            height=220,
        )
