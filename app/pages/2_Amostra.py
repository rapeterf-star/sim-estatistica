import streamlit as st

from src.painel_sim import carregar_resumo, renderizar_comparacao, renderizar_descritiva


st.title("Painel 2 — Amostra")
resumo = carregar_resumo()
n_populacao_formatado = f"{resumo['N']:,}".replace(",", ".")
fracao_amostral = f"{resumo['fracao_amostral']:.2%}".replace(".", ",")

st.markdown(
    f"**Amostragem aleatória simples, sem reposição:** n = {resumo['n']} · "
    f"semente = {resumo['semente']} · fração amostral = "
    f"{fracao_amostral} · N = {n_populacao_formatado}."
)
st.caption(
    "Dimensionamento: 95% de confiança, margem de erro de 5 pontos percentuais, "
    "p = 0,5 e correção para população finita. O sorteio foi feito uma vez; "
    "os registros individuais não são apresentados."
)
with st.expander("Cálculo do tamanho amostral"):
    st.markdown(
        "Parâmetros: confiança de **95%** (Z = 1,96), margem de erro de "
        "**5 p.p.** e **p = 0,5**, o valor que maximiza p(1 − p) e, portanto, "
        "garante a margem para qualquer proporção estimada."
    )
    st.latex(r"n_0 = \frac{Z^2\,p(1-p)}{d^2} = \frac{1{,}96^2 \times 0{,}25}{0{,}05^2} = 384{,}16")
    st.latex(
        r"n = \left\lceil \frac{n_0}{1 + \frac{n_0 - 1}{N}} \right\rceil"
        r" = \left\lceil \frac{384{,}16}{1 + \frac{383{,}16}{1.776}} \right\rceil = 316"
    )
    st.caption(
        "A correção para população finita reduz n de 385 para 316 porque a "
        "população tem 1.776 registros. O resultado n = 316 foi conferido na "
        "[calculadora de tamanho de amostra da SurveyMonkey]"
        "(https://pt.surveymonkey.com/learn/research-and-analysis/sample-size-calculator/) "
        "(população 1.776, confiança 95%, margem de erro 5%), pois a calculadora "
        "da USP/Bauru sugerida no enunciado estava fora do ar em 09/11/2026."
    )
with st.expander("Procedimento de seleção"):
    st.code(
        "amostra = populacao.sort_values('indice_original').sample("
        "n=316, replace=False, random_state=2026)",
        language="python",
    )
renderizar_descritiva(resumo["amostra"], "amostra aleatória", "amostra")
st.subheader("Amostra em comparação com a população")
renderizar_comparacao(resumo)
