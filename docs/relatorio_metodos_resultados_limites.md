# Método, resultados preliminares e limitações do estudo SIM

> **Documento histórico de resultados preliminares.** As hipóteses e análises aqui descritas antecedem o desenho aprovado para a atividade e não devem ser apresentadas como resultados finais. Consulte [o relatório final](./relatorio_final_sim.md) e [as hipóteses e testes](./hipoteses_e_testes.md).

## 1) Contexto e relação com o estudo anterior

Este estudo do SIM foi desenvolvido seguindo a mesma lógica de organização e documentação do estudo anterior do SINASC, mas com objetivos, variáveis e hipóteses próprias. A continuidade é metodológica e documental: os procedimentos de triagem, registro de decisões e organização das etapas foram reutilizados, sem que houvesse vinculação individual entre registros das duas bases.

A comparação com o SINASC, quando realizada, foi feita em nível agregado por ano e sexo, sem cruzamento de linhas ou manipulação de microdados do SINASC. Esta abordagem foi escolhida para preservar a integridade do estudo anterior e manter o foco no uso de denominadores compatíveis para a análise do SIM, quando a comparação era estatisticamente relevante.

## 2) Dados e população observada

A base analisada foi o arquivo `data/raw/sim_obitos.csv`, contendo registros de óbito de Porto Alegre, com período observado de janeiro de 2011 a dezembro de 2021. O conjunto foi recebido em formato CSV com separador ponto e vírgula, com 14 colunas e 135.548 registros.

Os campos relevantes para esta etapa incluem:

- `sexo`;
- `tipo_obito`;
- `obito`;
- `nascimento`;
- `raca`;
- `escolaridade`;
- `gestacao`;
- `cid_causa_basica`;
- `obito_prematuro`.

A base contém registros ausentes e 602 linhas integralmente duplicadas. Essas condições foram registradas como limitações de qualidade, mas não foram tratadas como base para exclusão definitiva antes de uma validação adicional da fonte e dos critérios de análise.

## 3) Objetivos da análise

O estudo foi orientado para responder a duas perguntas principais:

1. Como se distribui o sexo entre os óbitos do SIM, especialmente entre bebês e fetos?
2. Há base oficial e confiável para comparar peso ao nascer entre bebês falecidos?

O restante do desenho analítico foi organizado em torno destas duas linhas. Como o SIM não registra peso ao nascer em sua cópia recebida, a análise de peso foi tratada como hipótese admissível apenas em presença de fonte vinculada oficial e autorizada, e não como variável investigável no conjunto atual.

## 4) Definições operacionais e regras de análise

### 4.1 Registro de sexo

A variável `sexo` foi tratada conforme o valor informado no CSV. Para comparações por proporção, foram utilizados apenas registros com sexo conhecido.

### 4.2 Óbito fetal

A categoria `tipo_obito` foi usada para separar óbitos fetais e não fetais. Para esse estudo, os óbitos fetais foram descritos separadamente e em proporção por sexo.

### 4.3 Óbito infantil aproximado

Como o arquivo registra apenas mês/ano de nascimento e óbito, foi definida uma regra operacional de óbito infantil aproximado: óbito não fetal em que a diferença entre os meses de nascimento e óbito foi menor que 12 meses. Esta regra foi utilizada apenas para caracterização operacional e para comparação preliminar com a população de nascidos vivos do SINASC, não como idade exata em dias ou anos completos.

### 4.4 Denominadores agregados do SINASC

Para comparação com a população de nascimentos, foi gerado um arquivo agregado do SINASC contendo contagens de nascidos vivos por ano e sexo. A agregação foi feita em nível de contagem total por ano e sexo, sem vínculo individual entre os registros. Este arquivo foi usado exclusivamente para estimar taxas preliminares por 1.000 nascidos vivos, respeitando as limitações da base SIM e da ausência de data completa para o cálculo exato de idade.

## 5) Tratamento de qualidade e limites da base

- O identificador cifrado (`identificador_pessoa2`) não foi usado como chave de vinculação ou deduplicação, porque apareceu ausente em muitos registros e excessivamente repetitivo.
- As linhas duplicadas foram registradas, mas não removidas de forma definitiva antes da revisão da documentação e da orientação da fonte.
- Não foi aplicada qualquer exclusão que alterasse a população observada sem validação adicional.
- A análise foi feita com foco em descrição da composição dos óbitos e comparação agregada, sem atrair conclusões de causalidade.

## 6) Resultados preliminares

### 6.1 Distribuição por sexo em toda a base

Com sexo informado, a base apresentou:

- 67.432 registros femininos;
- 68.008 registros masculinos.

A distribuição total com sexo conhecido foi praticamente equilibrada, com 49,79% de registros femininos e 50,21% masculinos.

### 6.2 Óbitos fetais por sexo

Entre os óbitos fetais com sexo conhecido:

- 766 femininos;
- 929 masculinos.

A proporção masculina entre os fetais com sexo conhecido foi 54,81%, enquanto a feminina foi 45,19%.

### 6.3 Óbitos infantis aproximados por sexo

Usando a regra operacional de diferença menor que 12 meses entre nascimento e óbito, foram identificados 1.769 óbitos infantis aproximados com sexo conhecido:

- 798 femininos;
- 971 masculinos.

A proporção masculina nesse grupo foi 54,89%, e a feminina foi 45,11%.

### 6.4 Taxas preliminares por sexo usando SINASC agregado

A taxa foi calculada como:

Taxa por 1.000 = (óbito infantil aproximado no SIM / nascidos vivos no SINASC) × 1.000

Os resultados por ano e sexo, considerando 2011–2021, foram:

| Ano | Feminino | Masculino |
| --- | ---: | ---: |
| 2011 | 8,48 | 9,49 |
| 2012 | 8,86 | 9,12 |
| 2013 | 8,38 | 10,25 |
| 2014 | 7,89 | 10,70 |
| 2015 | 9,50 | 8,71 |
| 2016 | 7,92 | 9,24 |
| 2017 | 8,31 | 9,65 |
| 2018 | 7,57 | 10,55 |
| 2019 | 8,77 | 7,62 |
| 2020 | 6,96 | 9,21 |
| 2021 | 6,81 | 8,97 |

## 7) Limitações e interpretação

- Os resultados acima são preliminares e descritivos. Eles expressam a composição dos óbitos e a relação agregada com os nascimentos, mas não configuram risco causal por sexo.
- O campo de nascimento e óbito no SIM informa somente mês e ano, não data completa. A regra operacional de óbito infantil aproximado é uma aproximação e não um cálculo exato de idade.
- A base do SIM não contém peso ao nascer; portanto, não foi possível testar a diferença de peso entre bebês que morreram e a população geral de nascidos vivos.
- A comparação com o SINASC exige validação geográfica, temporal e de coorte antes de inferir risco ou taxa formalmente.
- O uso do SINASC foi restrito a contagens agregadas por ano e sexo, sem cruzamento individual de registros e sem alteração do projeto do SINASC.

## 8) Conclusão preliminar

A análise indicou que a composição dos óbitos por sexo é desproporcionalmente mais masculina entre os óbitos fetais e infantis aproximados, mas esta observação não pode ser interpretada como efeito causal. O estudo deve continuar com foco em descrição estatística, validação de qualidade e comparação agregada em nível de coorte, sempre preservando as limitações da base e evitando qualquer inferência que exceda o que os dados permitem.
