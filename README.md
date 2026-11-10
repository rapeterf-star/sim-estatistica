# SIM Porto Alegre — Estudo complementar de amostragem e inferência

Este repositório é o **estudo complementar** da atividade final de Probabilidade e Estatística. O estudo principal analisa os nascimentos do SINASC de Porto Alegre ([repositório](https://github.com/rapeterf-star/sinasc-estatistica) · [aplicativo](https://sinasc-poa-estatistica.streamlit.app/)).

Depois de concluir o SINASC, o mesmo desenho amostral (amostragem aleatória simples, 95% de confiança, margem de erro de 5 pontos percentuais, p = 0,5) foi replicado numa segunda base da mesma fonte: os **óbitos infantis** do Sistema de Informações sobre Mortalidade (SIM). A população é cerca de 111 vezes menor (N = 1.776, contra 197.639), o que permitiu observar efeitos que não aparecem no SINASC:

- a **correção para população finita**, que reduz a amostra de 385 para 316 e passa a ser aplicada aos erros-padrão (fração amostral de 17,8%);
- a pequena dependência entre o tamanho da amostra e o tamanho da população;
- a relação entre a precisão escolhida antes do sorteio e o **poder dos testes**.

## Painéis

O aplicativo Streamlit tem três painéis: **População**, **Amostra** e **Inferência**.

- Aplicativo: _link a inserir após a publicação_

## Fonte dos dados

[SIM — Mortalidade e óbitos, Portal de Dados Abertos de Porto Alegre](https://dadosabertos.poa.br/dataset/mortalidade-e-obitos), Secretaria Municipal de Saúde. Licença indicada no catálogo: Creative Commons Attribution (CC BY).

O arquivo original tem 135.548 linhas e 14 variáveis, com óbitos de janeiro de 2011 a dezembro de 2021.

## População, amostra e hipóteses

- **População analítica:** registros de óbito não fetal com mês/ano válidos de nascimento e de óbito, óbito entre 2011 e 2021 e diferença de 0 a 11 meses entre as competências (N = 1.776).
- **Unidade amostral:** uma linha elegível do arquivo SIM.
- **Amostra:** AAS sem reposição, n = 316, semente 2026. O valor foi conferido na calculadora da SurveyMonkey (`docs/evidencias/`).
- **Hipóteses:**
  - **H1:** a proporção de meninos entre os óbitos infantis supera a dos nascimentos (51,15% no SINASC)?
  - **H2:** a proporção de óbitos no mesmo mês/ano do nascimento difere entre os sexos?
  - **H3:** a idade média aproximada ao óbito supera 1 mês?
  - **H4:** a idade média aproximada difere entre os sexos?

Métodos, resultados e limitações estão em [docs/hipoteses_e_testes.md](docs/hipoteses_e_testes.md) e em [docs/relatorio_final_sim.md](docs/relatorio_final_sim.md).

## Reprodução

Os microdados não são publicados. Com o CSV original em `data/raw/sim_obitos.csv`, execute na raiz do projeto:

```powershell
python -m src.01_preparar_populacao
python -m src.02_amostra
python -m src.04_preparar_publicacao
python -m streamlit run app\app.py
```

A referência de H1 usa contagens agregadas de nascidos vivos por sexo do SINASC (`src/04_sinasc_dados_agregados.py`), sem nenhuma vinculação individual entre as bases.

## Privacidade

Microdados e derivados em nível de registro (`data/raw/`, `data/processed/`) ficam apenas locais e são ignorados pelo Git. O aplicativo consome somente `data/resumo_publico.json`, com frequências e medidas agregadas; as categorias exibidas têm pelo menos 10 registros.

## Limitações principais

A base informa apenas mês e ano de nascimento e de óbito, então a idade ao óbito é aproximada. Linhas integralmente repetidas foram mantidas, por falta de um identificador confiável para validá-las. Os testes descrevem a composição dos registros de óbito, não o risco individual de morte por sexo.
