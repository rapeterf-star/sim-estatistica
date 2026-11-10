import streamlit as st

from src.painel_sim import carregar_resumo, renderizar_inferencia


st.title("Painel 3 — Inferência")
resumo = carregar_resumo()
n_populacao_formatado = f"{resumo['N']:,}".replace(",", ".")
st.warning(
    "A variável idade é aproximada: a base informa somente mês e ano. "
    "Os testes descrevem a composição dos registros de óbito infantil; "
    "não estimam risco causal de mortalidade por sexo."
)
st.caption(
    f"AAS sem reposição: n = {resumo['n']}, N = {n_populacao_formatado}; "
    "IC de 95%; α = 0,05. A correção para população finita é aplicada aos "
    "erros-padrão."
)
renderizar_inferencia(resumo)
