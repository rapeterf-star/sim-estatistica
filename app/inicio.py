import sys
from pathlib import Path

import streamlit as st

# Permite abrir esta página também como arquivo principal do Streamlit.
RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from src.painel_sim import carregar_resumo


resumo = carregar_resumo()
n_populacao = f"{resumo['N']:,}".replace(",", ".")

st.title("SIM Porto Alegre")
st.write(
    "Análise descritiva da população de registros de óbito infantil aproximado, "
    "de uma amostra aleatória simples e dos resultados de inferência estatística."
)
st.markdown(
    f"A população analítica contém **{n_populacao} registros** de óbitos "
    f"registrados em Porto Alegre entre {resumo['periodo_obito']}. A amostra "
    f"aleatória simples, sem reposição, contém **{resumo['n']} registros**. "
    "Os dados individuais permanecem locais; o aplicativo apresenta apenas "
    "estatísticas agregadas."
)
st.link_button(
    "Fonte dos dados — SIM Porto Alegre",
    resumo["url_fonte"],
    icon=":material/open_in_new:",
)
st.info(
    "Use a navegação acima para explorar os painéis de população, amostra e "
    "inferência. A idade é aproximada pela diferença entre mês/ano de "
    "nascimento e óbito e não representa uma idade exata em dias."
)
