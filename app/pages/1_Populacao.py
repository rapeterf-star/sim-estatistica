import streamlit as st

from src.painel_sim import (
    carregar_resumo,
    renderizar_contexto_base,
    renderizar_descritiva,
)


st.title("Painel 1 — População")
resumo = carregar_resumo()
populacao = resumo["populacao"]
n_populacao = f"{resumo['N']:,}".replace(",", ".")

st.caption(
    f"Fonte: [{resumo['fonte']}]({resumo['url_fonte']}) · "
    f"óbitos registrados em Porto Alegre, {resumo['periodo_obito']}."
)
st.markdown(
    f"**N da população analítica:** {n_populacao} registros · "
    f"**Unidade amostral:** {resumo['unidade_amostral']}"
)
with st.expander("Definição da população analisada"):
    st.write(
        "Foram incluídos registros de óbito não fetal com mês/ano válido para "
        "nascimento e óbito, e diferença de 0 a 11 meses entre as competências."
    )
    st.caption(resumo["definicao_idade"])
renderizar_contexto_base(resumo)
st.subheader("População analisada: óbitos infantis")
renderizar_descritiva(populacao, "população completa", "populacao")
st.caption(resumo["ressalva"])
