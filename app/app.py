import sys
from pathlib import Path

import streamlit as st

# O arquivo principal fica em app/; a raiz do projeto precisa estar no caminho
# de importação para que `src` seja encontrado também no Streamlit Cloud.
RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))


st.set_page_config(
    page_title="SIM Porto Alegre — Estatística",
    page_icon=":material/monitoring:",
    layout="wide",
)

paginas = [
    st.Page("inicio.py", title="Apresentação", icon=":material/home:", default=True),
    st.Page(
        "pages/1_Populacao.py",
        title="População",
        icon=":material/analytics:",
    ),
    st.Page(
        "pages/2_Amostra.py",
        title="Amostra",
        icon=":material/bar_chart:",
    ),
    st.Page(
        "pages/3_Inferencia.py",
        title="Inferência",
        icon=":material/science:",
    ),
]
pagina = st.navigation(paginas, position="top")
pagina.run()
