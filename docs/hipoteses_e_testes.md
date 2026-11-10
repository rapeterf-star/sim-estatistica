# Amostragem, hipóteses e inferência — atividade final do SIM

**Status:** desenho aprovado e análise da AAS implementada; valores abaixo foram calculados com a população analítica e a amostra reproduzível. A revisão final e a publicação estão reservadas para 15/11/2026.

## 1. Objetivo e correspondência com a atividade

O fluxo segue o enunciado da Atividade Avaliativa Final de Probabilidade e Estatística para IA e o mesmo desenho aplicado no estudo anterior do SINASC:

1. definir a população e a unidade amostral;
2. dimensionar e sortear uma amostra aleatória simples (AAS), sem reposição;
3. descrever população e amostra em painéis separados;
4. executar, usando a amostra, dois testes para proporções e dois para médias;
5. comparar estimativas e intervalos da amostra com os parâmetros calculados diretamente na população.

O foco no SIM é a composição por sexo dos registros de óbito infantil. O SIM recebido não tem peso ao nascer nem idade em dias; por isso, a idade só pode ser aproximada a partir de mês/ano. As inferências não serão apresentadas como estimativas de risco causal de mortalidade.

## 2. Fonte, população e unidade amostral

- **Fonte:** [SIM — Dados Abertos de Porto Alegre](https://dadosabertos.poa.br/dataset/mortalidade-e-obitos), Secretaria Municipal de Saúde.
- **Base original:** `data/raw/sim_obitos.csv`, com 135.548 linhas e 14 variáveis; permanece local.
- **População analítica deste exercício:** registros não fetais com mês/ano válido de nascimento e óbito, óbito entre 2011 e 2021 e diferença não negativa menor que 12 meses entre os meses registrados. O arquivo tem **N = 1.776** registros elegíveis.
- **Unidade amostral:** uma linha elegível do CSV SIM. Não há identificador confiável para afirmar que cada linha corresponde a uma pessoa distinta; linhas integralmente repetidas foram mantidas, sem deduplicação não validada.
- **População-alvo da inferência:** os registros elegíveis do arquivo recebido, não todas as crianças de Porto Alegre nem todas as crianças nascidas no período.

### Variáveis usadas

| Variável | Tipo | Definição operacional e uso |
| --- | --- | --- |
| `sexo` | Qualitativa nominal | FEMININO, MASCULINO ou não informado; proporções comparativas usam sexo conhecido. |
| `idade_obito_meses_aprox` | Quantitativa discreta derivada | Diferença entre as competências de óbito e nascimento; valores 0 a 11. Não é idade exata. |
| `mesma_competencia` | Qualitativa binária derivada | 1 se nascimento e óbito têm o mesmo mês/ano registrado; 0 se a diferença é de 1 a 11 meses. |
| `gestacao`, `raca` | Qualitativas | Usadas para caracterização descritiva, sem testes principais. |

O valor de idade igual a zero quer dizer somente que nascimento e óbito foram registrados no mesmo mês/ano; não permite afirmar que a criança morreu no período neonatal ou que viveu menos de 28 dias.

## 3. Dimensionamento e seleção da AAS

Parâmetros definidos antes de examinar os resultados da amostra:

- confiança de 95% (`Z = 1,96`);
- margem de erro de 5 pontos percentuais (`d = 0,05`);
- proporção conservadora `p = 0,5`;
- tamanho da população analítica `N = 1.776`.

Primeiro, o tamanho para população infinita:

```text
n₀ = Z² p(1 − p) / d² = 1,96² × 0,5 × 0,5 / 0,05² = 384,16
```

Aplicando a correção para população finita:

```text
n = ceil[n₀ / (1 + (n₀ − 1)/N)] = ceil(315,99) = 316
```

A amostra foi sorteada uma única vez, sem reposição, após ordenar pelo índice original da linha:

```python
amostra = populacao.sort_values("indice_original").sample(
    n=316, replace=False, random_state=2026
)
```

A semente fixa `2026` permite reproduzir o sorteio; cada linha elegível tem probabilidade `316/1.776 = 17,79%` de seleção. A fração amostral supera 10%, portanto os erros-padrão e intervalos aplicam a correção para população finita. Os arquivos individuais `populacao_infantil.parquet` e `amostra_infantil.csv` ficam em `data/processed/`, ignorados pelo Git.

## 4. Hipóteses e métodos

Todos os testes usam `α = 0,05`. Os intervalos de confiança são de 95%. Parâmetros populacionais são calculados diretamente sobre os registros elegíveis; estimativas, intervalos e testes são calculados a partir da AAS.

| Código | Pergunta e hipóteses | Método |
| --- | --- | --- |
| **H1 — proporção** | Os meninos têm, entre os óbitos infantis, participação maior do que entre os nascimentos? Referência: 51,15% de meninos entre os 197.780 nascidos vivos do SINASC POA 2011–2021. `H₀: π ≤ 0,5115`; `H₁: π > 0,5115`. | Teste Z unilateral de uma proporção; IC de Wald com correção para população finita e limite inferior unilateral de 95%. Sexo não informado é excluído desta proporção. |
| **H2 — diferença de proporções** | A proporção de óbitos registrados no mesmo mês/ano do nascimento difere entre meninas e meninos? `H₀: πF − πM = 0`; `H₁: πF − πM ≠ 0`. | Teste Z bilateral de duas proporções; IC da diferença com correção para população finita em cada grupo. |
| **H3 — média** | Em média, o óbito infantil ocorre depois do primeiro mês de calendário após o nascimento? Mais da metade dos registros tem diferença 0; `μ₀ = 1` representa óbitos concentrados, em média, até o mês seguinte ao nascimento. `H₀: μ ≤ 1`; `H₁: μ > 1`. | Teste t unilateral de uma amostra; IC t e limite inferior unilateral, ambos com correção para população finita. |
| **H4 — diferença de médias** | A idade média aproximada ao óbito difere entre meninas e meninos? `H₀: μF − μM = 0`; `H₁: μF − μM ≠ 0`. | Teste t bilateral de Welch; IC da diferença, com correção para população finita em cada grupo. |

### Condições e interpretação

- O sorteio é AAS sem reposição. A fração amostral de 17,79% foi considerada explicitamente por meio da correção para população finita.
- Em H1, as contagens esperadas de sucessos e fracassos sob `H₀` excedem 10.
- Em H2, as contagens esperadas de eventos e não eventos em ambos os grupos excedem 10.
- Em H3, embora a idade aproximada seja discreta e assimétrica, `n = 316` sustenta a aproximação do TCL para a média amostral.
- Em H4, os dois grupos amostrais têm mais de 30 observações; Welch não pressupõe variâncias iguais.
- Os testes tratam o arquivo como a população de registros definida. Eles não corrigem possível sub-registro, classificação incorreta ou duplicidade e não demonstram causalidade.
- A pergunta “meninos morrem mais do que meninas?” exige denominadores de crianças vivas por sexo e seguimento compatível. H1 compara a composição por sexo **dos registros de óbito** com a composição por sexo **dos nascimentos** (agregado do SINASC), o que indica sobremortalidade relativa sem estimar taxas individuais. O SINASC agregado entra apenas como valor de referência fixo; ele não transforma esta AAS de óbitos em uma amostra de nascimentos.
- Em H1 e H3, o IC bilateral de 95% descreve a estimativa; a decisão unilateral equivale a comparar o valor de referência com o limite inferior unilateral de 95%.
- A correção para população finita usa o mesmo fator `(N − n)/(N − 1)` em todos os testes, aplicado separadamente por grupo em H2 e H4.

## 5. Resultados calculados

| Teste | Estimativa amostral (parâmetro populacional) | IC 95% | Estatística e valor-p | Decisão a 5% |
| --- | --- | --- | --- | --- |
| H1 | Proporção masculina: **55,06%** (**54,89%**) | 50,09% a 60,04% (limite unilateral: 50,89%) | `Z = 1,536`; `p = 0,0623` | Não rejeitar `H₀`. Na população, `H₀` é falsa (54,89% > 51,15%): **erro tipo II** por baixo poder diante de um efeito de 3,7 p.p. |
| H2 | `πF − πM`: **−3,19 p.p.** (**−1,80 p.p.**) | −13,22 a 6,84 p.p. | `Z = −0,623`; `p = 0,5332` | Não rejeitar `H₀`; não há evidência suficiente de diferença na proporção de registros no mesmo mês/ano. |
| H3 | Idade média aproximada: **1,424 meses** (**1,476 meses**) | 1,175 a 1,673 meses (limite unilateral: 1,215) | `t(315) = 3,345`; `p = 0,0005` | Rejeitar `H₀`; a média supera 1 mês. Decisão correta na população (1,476 > 1). |
| H4 | `μF − μM`: **0,368 meses** (**0,124 meses**) | −0,142 a 0,878 meses | `t(276,14) = 1,421`; `p = 0,1563` | Não rejeitar `H₀`; não há evidência suficiente de diferença na média aproximada entre sexos. |

Os intervalos da amostra contêm os respectivos parâmetros calculados na população. Isso é uma comparação deste sorteio específico, não uma garantia de que qualquer intervalo de 95% contenha o parâmetro.

## 6. Reprodutibilidade e execução

Na raiz do projeto, executar:

```powershell
python -m src.01_preparar_populacao
python -m src.02_amostra
python -m src.04_preparar_publicacao
python -m streamlit run app\app.py
```

O terceiro comando gera `data/resumo_publico.json` com tabelas e estatísticas agregadas; não inclui índices nem registros individuais. Os painéis Streamlit consomem esse resumo.

## 7. Limitações

1. A diferença de meses não equivale à idade exata em dias ou semanas; o mesmo mês/ano pode representar tempos de vida diferentes.
2. A população é de linhas do arquivo. Há registros integralmente repetidos, inclusive entre os elegíveis; foram mantidos porque sua exclusão não foi validada com a fonte.
3. O conjunto contém somente óbitos e não permite estimar, por si só, a probabilidade de morrer em cada sexo.
4. A referência de 1 mês em H3 é operacional, não um limite clínico. A referência de H1 vem dos nascimentos de 2011–2021; óbitos infantis do início de 2011 incluem crianças nascidas em 2010, fora desse agregado.
5. Crianças que morreram com menos de 1 ano, mas com 12 meses de diferença no calendário (por exemplo, nascidas em 15/01 e mortas em 10/01 do ano seguinte), ficam fora da população.
6. Inferência e generalização ficam restritas ao arquivo recebido e à regra de inclusão definida.
