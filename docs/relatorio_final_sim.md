# Amostragem e inferência estatística em registros de óbito infantil do SIM — Porto Alegre

**Relatório de trabalho para a Atividade Avaliativa Final de Probabilidade e Estatística para IA**  
**Data de referência:** 8 de novembro de 2026  
**Prazo de entrega:** 15 de novembro de 2026

## Resumo

Este trabalho aplica amostragem aleatória simples, intervalos de confiança e testes de hipóteses a uma base do Sistema de Informações sobre Mortalidade (SIM) de Porto Alegre. A população analítica foi definida como 1.776 registros não fetais com nascimento e óbito registrados por mês/ano e diferença de 0 a 11 meses entre as competências. Dessa população foi sorteada, sem reposição, uma amostra aleatória simples de 316 registros, com confiança de 95%, erro planejado de 5 pontos percentuais, proporção conservadora de 0,5 e semente 2026. A análise incluiu dois testes para proporções e dois para médias, comparando os resultados da amostra com os parâmetros calculados diretamente na população. A proporção masculina amostral foi 55,06% e a idade média aproximada ao óbito foi 1,424 mês. As conclusões descrevem a composição dos registros elegíveis do arquivo; não estimam risco causal de mortalidade por sexo.

## 1. Fonte e contexto

A base é o conjunto [SIM — Dados Abertos de Porto Alegre](https://dadosabertos.poa.br/dataset/mortalidade-e-obitos), publicado pela Secretaria Municipal de Saúde de Porto Alegre. O CSV recebido possui 135.548 linhas e 14 variáveis, com registros de óbitos entre 2011 e 2021.

O foco do exercício é a composição por sexo entre óbitos infantis. O arquivo não tem peso ao nascer e registra nascimento e óbito apenas por mês/ano. Assim, a idade ao óbito foi derivada como diferença entre as competências mensais, sem precisão em dias.

## 2. População e unidade amostral

A população analítica compreende registros que satisfazem simultaneamente:

1. `tipo_obito` não fetal;
2. mês/ano de nascimento e de óbito válidos;
3. ano do óbito entre 2011 e 2021;
4. diferença entre as competências de nascimento e óbito de 0 a 11 meses.

O conjunto resultante tem **N = 1.776 registros**. A unidade amostral é uma linha elegível do CSV. Linhas integralmente repetidas foram mantidas, pois não houve validação da fonte que autorizasse removê-las; portanto, esta população representa registros no arquivo, não necessariamente indivíduos distintos.

Variáveis principais:

- **Sexo:** feminino, masculino ou não informado. As comparações por sexo usam somente os registros com sexo conhecido.
- **Idade aproximada ao óbito:** diferença entre mês/ano do óbito e do nascimento, em meses inteiros de 0 a 11.
- **Mesmo mês/ano:** indicador de que nascimento e óbito foram registrados na mesma competência.

Um valor de idade igual a zero não significa idade exata inferior a 28 dias; indica somente que os dois eventos foram registrados no mesmo mês/ano.

## 3. Dimensionamento e seleção da amostra

O dimensionamento foi baseado nos parâmetros recomendados para estimar proporções com maior variabilidade:

- nível de confiança: 95% (`Z = 1,96`);
- margem de erro: 5 pontos percentuais (`d = 0,05`);
- proporção de planejamento: `p = 0,5`;
- população finita: `N = 1.776`.

O tamanho inicial para população infinita foi:

```text
n₀ = Z² p(1 − p) / d² = 384,16
```

Após correção para população finita:

```text
n = ceil[n₀ / (1 + (n₀ − 1)/N)] = 316
```

Com `N = 1.776`, o valor antes do arredondamento é aproximadamente `315,99`; arredondando para cima, obtém-se `n = 316`. O cálculo foi reproduzido no código do projeto com esses parâmetros. A calculadora USP/Bauru indicada no enunciado estava fora do ar em 09/11/2026; por isso, o valor foi conferido na [calculadora de tamanho de amostra da SurveyMonkey](https://pt.surveymonkey.com/learn/research-and-analysis/sample-size-calculator/), com população 1.776, confiança de 95% e margem de erro de 5%, que também resulta em **n = 316** (captura em `docs/evidencias/calculadora_surveymonkey_n316.png`).

A seleção foi uma AAS sem reposição, feita uma vez, após ordenar pelo índice original da linha:

```python
amostra = populacao.sort_values("indice_original").sample(
    n=316, replace=False, random_state=2026
)
```

A fração amostral é 17,79%. Como supera 10%, os erros-padrão e intervalos incorporam a correção para população finita. O sorteio é reprodutível pela semente 2026.

## 4. Descrição da população e da amostra

| Medida | População (`N = 1.776`) | AAS (`n = 316`) |
| --- | ---: | ---: |
| Idade média aproximada ao óbito | 1,476 mês | 1,424 mês |
| Desvio-padrão da idade | 2,426 meses | 2,485 meses |
| Mediana da idade | 0 mês | 0 mês |
| Moda da idade aproximada | 0 mês | 0 mês |
| Proporção masculina entre sexos conhecidos | 54,89% | 55,06% |
| Proporção no mesmo mês/ano entre sexos conhecidos | 52,74% | 53,16% |

Na população, a mediana e a moda iguais a zero não indicam ausência de cálculo: 939 dos 1.776 registros (52,87%) têm diferença de mês/ano igual a zero. Assim, pelo menos metade dos valores é zero, o que resulta em mediana zero; zero também é a categoria mais frequente, portanto é a moda. Na amostra, 168 de 316 registros (53,16%) têm valor zero, e mediana e moda também são zero. Zero significa que nascimento e óbito foram registrados na mesma competência mensal, não uma idade exata em dias. Havia 971 registros masculinos e 798 femininos com sexo conhecido na população. As distribuições por faixa de idade aproximada (0–1, 2–3, 4–5 e 6–11 meses), por sexo e pela ocorrência na mesma competência são apresentadas nos Painéis 1 e 2. Diferenças entre as medidas amostrais e populacionais são esperadas pela variabilidade do sorteio.

## 5. Inferência estatística

Todos os testes foram definidos com significância de 5%. Os intervalos são de 95%. Parâmetros populacionais foram calculados usando a população completa; estimativas, intervalos e testes inferenciais usam a AAS.

### H1 — Uma proporção

**Pergunta:** os meninos têm, entre os óbitos infantis, participação maior do que entre os nascimentos?

**Justificativa da referência:** entre os 197.780 nascidos vivos de Porto Alegre registrados no SINASC de 2011 a 2021, **51,15%** são meninos. Se o sexo não influenciasse o óbito infantil, a composição por sexo dos óbitos repetiria a dos nascimentos. Uma proporção maior de meninos entre os óbitos indica sobremortalidade masculina relativa, sem exigir o cálculo de taxas com denominadores individuais.

- `H₀: π ≤ 0,5115`
- `H₁: π > 0,5115`
- Método: teste Z unilateral de uma proporção; IC de Wald com correção para população finita.
- Amostra: 174 meninos em 316 registros com sexo conhecido; `P = 55,06%`.
- Parâmetro populacional: `π = 54,89%`.
- IC 95%: **50,09% a 60,04%**; limite inferior unilateral de 95%: **50,89%**.
- Estatística: `Z = 1,536`; valor-p: **0,0623**.

Não se rejeita `H₀` a 5%: o limite inferior unilateral (50,89%) fica abaixo da referência de 51,15%. A amostra aponta na direção de H₁, mas a evidência não é suficiente. Como a população está disponível, sabe-se que `H₀` é falsa (54,89% > 51,15%). Trata-se de um **erro tipo II**: a diferença real, de 3,7 pontos percentuais, é pequena em relação ao erro-padrão de uma amostra de 316 registros (cerca de 2,5 p.p.), e o teste tem pouco poder para detectá-la. Com a referência simplista de 50%, a mesma amostra levaria à rejeição (`Z = 1,986`; `p = 0,0235`), o que mostra como a escolha do valor de referência condiciona a conclusão.

### H2 — Diferença de proporções

**Pergunta:** a proporção de registros no mesmo mês/ano do nascimento difere entre meninas e meninos?

- `H₀: πF − πM = 0`
- `H₁: πF − πM ≠ 0`
- Método: teste Z bilateral para duas proporções; IC da diferença com correção para população finita em cada grupo.
- Na amostra, as proporções foram 51,41% para meninas e 54,60% para meninos; diferença `πF − πM = −3,19` pontos percentuais.
- Diferença populacional: `−1,80` ponto percentual.
- IC 95% da diferença: **−13,22 a 6,84 pontos percentuais**.
- Estatística: `Z = −0,623`; valor-p: **0,5332**.

Não se rejeita `H₀`; a amostra não fornece evidência suficiente de diferença. O período é definido somente pela competência mensal e não deve ser interpretado como período neonatal exato.

### H3 — Uma média

**Pergunta:** em média, o óbito infantil ocorre depois do primeiro mês de calendário após o nascimento?

**Justificativa da referência:** mais da metade dos registros tem diferença zero (óbito no mesmo mês/ano do nascimento), o que indica forte concentração dos óbitos infantis logo após o nascimento. A referência `μ₀ = 1 mês` representa um padrão em que os óbitos ocorrem, em média, até o mês seguinte ao nascimento. Rejeitar `H₀` indica que os óbitos pós-neonatais, embora menos numerosos, deslocam a média para além desse patamar.

- `H₀: μ ≤ 1 mês`
- `H₁: μ > 1 mês`
- Método: teste t unilateral de uma amostra; IC t com correção para população finita.
- Média amostral: `x̄ = 1,424 meses` (`s = 2,485`); parâmetro populacional: `μ = 1,476 meses`.
- IC 95%: **1,175 a 1,673 meses**; limite inferior unilateral de 95%: **1,215 mês**.
- Estatística: `t(315) = 3,345`; valor-p: **0,0005**.

Rejeita-se `H₀`. A idade média aproximada ao óbito supera 1 mês: apesar de a mediana e a moda serem zero, a cauda longa de óbitos entre 2 e 11 meses eleva a média. Na população, `μ = 1,476 > 1`, então a decisão está correta. A distribuição é muito assimétrica, e por isso média e mediana contam histórias diferentes; o teste t se apoia no TCL, razoável com n = 316. A referência de 1 mês é operacional, não um limite clínico.

### H4 — Diferença de médias

**Pergunta:** a idade média aproximada ao óbito difere entre meninas e meninos?

- `H₀: μF − μM = 0`
- `H₁: μF − μM ≠ 0`
- Método: teste t bilateral de Welch; IC da diferença com correção para população finita em cada grupo.
- Média amostral: meninas `1,627 meses`; meninos `1,259 meses`; diferença `0,368 mês`.
- Diferença populacional: `0,124 mês`.
- IC 95% da diferença: **−0,142 a 0,878 mês**.
- Estatística: `t(276,14) = 1,421`; valor-p: **0,1563**.

Não se rejeita `H₀`; não há evidência suficiente de diferença entre as médias aproximadas nesta amostra.

## 6. Comparação e interpretação

Os intervalos de confiança dos quatro testes contêm os parâmetros correspondentes calculados na população para esta AAS. Somente H3 rejeita a hipótese nula; H1, H2 e H4 não a rejeitam. As diferenças entre estimativas pontuais e parâmetros populacionais ilustram a variabilidade amostral.

Como a população está disponível, é possível conferir cada decisão:

| Teste | Decisão com a amostra | Situação na população | Leitura |
| --- | --- | --- | --- |
| H1 | Não rejeita | `H₀` falsa (54,89% > 51,15%) | Erro tipo II: efeito pequeno e teste com pouco poder |
| H2 | Não rejeita | Diferença de −1,80 p.p. | Formalmente erro tipo II, mas a diferença não tem relevância prática |
| H3 | Rejeita | `H₀` falsa (1,476 > 1) | Decisão correta |
| H4 | Não rejeita | Diferença de 0,124 mês | Formalmente erro tipo II, mas a diferença não tem relevância prática |

Em população finita, uma diferença exatamente igual a zero quase nunca ocorre, por isso as não rejeições de H2 e H4 aparecem formalmente como erros tipo II. O caso informativo é H1: há uma diferença real e de interesse, mas a amostra dimensionada para estimar proporções com margem de 5 p.p. não tem precisão suficiente para detectar um efeito de 3,7 p.p. Uma não rejeição não prova igualdade, e uma rejeição não implica relevância prática nem causalidade.

O painel de inferência apresenta para cada hipótese o enunciado, as hipóteses, o método, a estimativa, o intervalo, a estatística, o valor-p, a decisão, as condições e a comparação com a população. Os painéis descritivos reproduzem as frequências e medidas para população e amostra.

## 7. Limitações

1. Nascimento e óbito contêm apenas mês/ano; a idade é aproximada e pode classificar incorretamente registros próximos ao limite de 12 meses.
2. Mesma competência não identifica a duração exata entre nascimento e óbito.
3. Linhas integralmente repetidas foram mantidas; não foi possível confirmar se representam duplicação do arquivo ou eventos distintos.
4. O SIM contém apenas registros de óbito. Os testes de proporção não estimam risco de morte por sexo; para isso seriam necessários denominadores de nascimentos compatíveis e desenho apropriado.
5. Os resultados se restringem à população analítica do arquivo e não devem ser generalizados para todas as crianças ou para relações causais.

## 8. Fonte, painéis e entrega

- **Base original:** [SIM — Dados Abertos de Porto Alegre](https://dadosabertos.poa.br/dataset/mortalidade-e-obitos).
- **Painel 1:** população — link será inserido após publicação.
- **Painel 2:** amostra — link será inserido após publicação.
- **Painel 3:** inferência — link será inserido após publicação.
- **Vídeo de apresentação (máximo de cinco minutos):** link será inserido após publicação no YouTube.

Os arquivos com registros individuais permanecem locais. A aplicação utiliza o resumo de estatísticas agregadas, sem identificadores ou linhas individuais.
