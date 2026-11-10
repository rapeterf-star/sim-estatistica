# Plano de Trabalho — Atividade Avaliativa Final (SIM Porto Alegre)

**Enunciado de referência:** Atividade Avaliativa Final — Probabilidade e Estatística para IA, UFRGS, entrega em 15/11/2026 às 23h59. O plano replica as etapas do trabalho SINASC e adapta população, variáveis e hipóteses ao conjunto SIM.

## Objetivo e entregas

Comparar parâmetros calculados para a população analítica do SIM com estimativas obtidas em uma amostra aleatória simples (AAS), usando intervalos de confiança e testes de hipóteses para duas proporções e duas médias. Entregas previstas:

1. Painel interativo da população;
2. Painel interativo da amostra;
3. Painel de inferência e comparação população–amostra;
4. Link da base de dados original e identificação da fonte;
5. Vídeo de apresentação de até cinco minutos.

## Base de dados e população analítica

- **Fonte:** [SIM — Dados Abertos de Porto Alegre](https://dadosabertos.poa.br/dataset/mortalidade-e-obitos), Secretaria Municipal de Saúde.
- **Arquivo local:** `data/raw/sim_obitos.csv` (135.548 linhas, 14 variáveis).
- **Contexto:** registros de mortalidade municipal; o arquivo recebido tem óbitos de 2011 a 2021.
- **População deste exercício:** registros não fetais com mês/ano válido de nascimento e óbito, ano do óbito entre 2011 e 2021 e diferença não negativa menor que 12 meses entre os meses registrados. Total elegível: **N = 1.776**.
- **Unidade amostral:** cada linha elegível do CSV. Linhas integralmente repetidas são mantidas porque não há validação da fonte que autorize excluí-las; a população representa registros do arquivo, não necessariamente indivíduos únicos.
- **Variáveis:** sexo, idade aproximada ao óbito em meses e indicador de nascimento e óbito na mesma competência. O SIM não contém peso ao nascer nem datas completas.

## Etapa 1 — Preparação e definição da população

- [x] Conferir a origem, a estrutura, as variáveis e o período da base.
- [x] Definir foco, unidade amostral e população de interesse.
- [x] Derivar a idade aproximada a partir dos campos mês/ano e definir explicitamente o limite de 0 a 11 meses.
- [x] Preservar o índice da linha de origem para rastrear o sorteio.
- [x] Manter os microdados e derivados individuais locais, ignorados pelo Git.
- [x] Gerar população analítica em `data/processed/populacao_infantil.parquet` com `python -m src.01_preparar_populacao`.

## Etapa 2 — Dimensionamento e seleção da amostra

- [x] Usar confiança de 95%, erro de 5 pontos percentuais, `p = 0,5` e correção para população finita.
- [x] Calcular `n₀ = 384,16` e `n = 316` para `N = 1.776`.
- [x] Conferir `n = 316` em calculadora online: USP/Bauru fora do ar em 09/11/2026; conferido na SurveyMonkey (N = 1.776, 95%, 5%) → 316. Captura em `docs/evidencias/calculadora_surveymonkey_n316.png`.
- [x] Sortear uma AAS sem reposição, uma única vez, com semente fixa 2026.
- [x] Salvar `data/processed/amostra_infantil.csv`, local e ignorado pelo Git.
- [x] Validar reprodutibilidade, tamanho amostral, ausência de reposição e pertencimento à população.

## Etapa 3 — Painel 1: descrição da população

- [x] Apresentar contexto, fonte, recorte, unidade amostral e tamanho `N`.
- [x] Apresentar a média, mediana, moda, desvio-padrão, variância, quartis e extremos da idade aproximada.
- [x] Apresentar frequências e proporções por sexo, faixas de idade aproximada e ocorrência na mesma competência.
- [x] Usar gráficos adequados às variáveis e permitir selecionar a distribuição exibida.

## Etapa 4 — Painel 2: descrição da amostra

- [x] Reproduzir a descrição do Painel 1 com os `n = 316` registros sorteados.
- [x] Exibir semente, método, fração amostral e procedimento de sorteio.
- [x] Comparar medidas e distribuições selecionadas com os parâmetros da população.
- [x] Não exibir nem oferecer download de linhas individuais nos painéis.

## Etapa 5 — Painel 3: inferência

- [x] H1: teste unilateral para proporção masculina acima de 50%.
- [x] H2: teste bilateral para diferença entre sexos na proporção de registros no mesmo mês/ano.
- [x] H3: teste t de uma amostra para a idade média aproximada versus 1 mês (unilateral, μ > 1).
- [x] H4: teste t de Welch para diferença de idade média aproximada entre sexos.
- [x] Calcular ICs, estatísticas de teste, graus de liberdade quando aplicável, valores-p, decisões e comparação com a verdade populacional.
- [x] Verificar condições e aplicar correção para população finita, necessária porque `n/N = 17,79%`.
- [x] Registrar limitações da idade mensal aproximada, dos registros repetidos e da interpretação restrita à composição dos óbitos.

## Etapa 6 — Privacidade e painéis

- [x] Gerar `data/resumo_publico.json` com estatísticas e frequências agregadas, sem identificadores nem registros individuais.
- [x] Implementar navegação pelos três painéis em `app/`.
- [x] Revisar os três painéis no navegador; confirmar conteúdo, navegação e ausência de registros individuais.
- [ ] Criar um repositório público separado no GitHub, sob a mesma conta do repositório SINASC (`rapeterf-star`), e publicar o código e o resumo agregado sem microdados.
- [ ] Publicar o app no Streamlit Community Cloud usando `app/app.py`; escolher uma URL curta após verificar disponibilidade.
- [ ] Testar em janela anônima as páginas Apresentação, População, Amostra e Inferência e registrar os três links diretos para o Moodle.

## Etapa 7 — Comunicação e entrega (até 15/11/2026)

- [x] Atualizar o relatório em Markdown e LaTeX conforme o enunciado e compilar o PDF.
- [ ] Fazer revisão final do relatório e inserir os links públicos quando os painéis e o vídeo forem publicados.
- [ ] Preparar e ensaiar o vídeo, com no máximo cinco minutos.
- [ ] Publicar o vídeo no YouTube e confirmar que o link é acessível ao avaliador.
- [ ] Revisar os três painéis publicados e o link da base original.
- [ ] Enviar os links no Moodle até 15/11/2026 às 23h59.

## Limites que devem constar na apresentação

- A idade é uma diferença de mês/ano, não idade exata em dias; mesma competência não define período neonatal.
- Os testes de proporção por sexo tratam da composição dos registros de óbito. Sem denominadores e desenho adequados, não demonstram que meninos tenham maior risco de morrer.
- As linhas duplicadas não foram removidas, pois sua natureza não foi confirmada pela fonte.
- As conclusões referem-se à população analítica do arquivo e à regra operacional adotada.
