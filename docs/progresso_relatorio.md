# Progresso do estudo SIM — atividade avaliativa final

**Status atual:** população analítica, AAS, quatro testes, três painéis e relatório alinhados à rubrica da atividade. A revisão final, a publicação dos painéis e o vídeo continuam pendentes para a entrega em 15/11/2026.
## 2026-11-08 — Abertura do projeto e relação com o estudo anterior

- O projeto foi criado em diretório próprio, separado do experimento do SINASC.
- Este estudo do SIM deriva do fluxo de trabalho do estudo anterior, mas mantém objetivos, variáveis e hipóteses próprias.
- A relação com o estudo anterior é metodológica e documental, não de vinculação individual entre registros.
- A base recebida foi validada como `data/raw/sim_obitos.csv`.
- A fonte foi confirmada como SIM de Porto Alegre, com catálogo oficial e licença CC BY.
- Foram registrados os limites iniciais da base: 135.548 registros, 14 colunas, separador ponto e vírgula, período de 2011 a 2021.
- Foi identificado o campo de identificador cifrado como não confiável para vinculação ou deduplicação inicial.
- A base foi tratada como microdados locais, sem publicação.

## 2026-11-08 — Definição do foco e das hipóteses

- O estudo foi orientado para: (1) sexo e óbitos de bebês; (2) peso ao nascer, somente se houver fonte oficial vinculada confiável.
- Foram formuladas hipóteses sobre: óbito infantil, óbito fetal, perfil sociodemográfico dos óbitos e admissibilidade da variável peso ao nascer.
- Foi documentada a regra de que a análise deve evitar inventar variáveis e não usar elementos não confirmados pela fonte.

## 2026-11-08 — Análise descritiva inicial

- Foi realizado o resumo do CSV recebido.
- Foram confirmados os totais: 135.548 linhas; 1.761 óbitos fetais; 133.787 óbitos não fetais; 2.002 registros de interesse por sexo ausente/ignorado; sexo conhecido em 135.440 registros.
- Foi calculada a distribuição por sexo dos óbitos: 67.432 femininos e 68.008 masculinos.
- Foi calculada uma regra operacional de óbito infantil aproximado, usando diferença menor que 12 meses entre nascimento e óbito.
- Foram identificados 1.769 registros infantis aproximados com sexo conhecido: 798 femininos e 971 masculinos.
- Foram mantenidas as interpretações apenas como composição descritiva dos óbitos, sem inferência causal.

## 2026-11-08 — Agregação dos denominadores do SINASC

- Foi identificado o arquivo do SINASC no diretório do experimento anterior: `C:\Users\maque\VSCODE\sinasc-estatistica\data\sinasc_nascimentos.csv`.
- Foi criado um arquivo agregado para este projeto em `data/processed/sinasc_sexo_ano.csv`.
- A agregação foi feita por ano e sexo, utilizando `data_nascimento` do SINASC.
- O arquivo gerado contém contagens de nascidos vivos por sexo e ano, com o formato esperado pela análise do SIM.

## 2026-11-08 — Cálculo das taxas preliminares

- Foi implementado o script `src/03_taxa_obito_infantil_por_sexo.py` para calcular taxa de óbito infantil aproximado por sexo e ano.
- A taxa foi calculada como (óbitos infantis SIM / nascidos vivos SINASC) × 1.000.
- Foi mantida a regra operacional de diferencia entre nascimento e óbito menor que 12 meses.
- Foram verificados os resultados para 2011–2021.

## Observações de interpretação e status dos pontos críticos

- As taxas calculadas são preliminares e devem ser interpretadas como comparação de composição do evento e dos nascimentos, não como risco causal.
- A regra de idade aproximada exige cautela por ausência de data completa.
- A análise geográfica, temporal e de coorte ainda precisa ser validada antes de qualquer inferência formal sobre risco por sexo.
- O peso ao nascer continua como variável não analisável neste estudo, porque a base SIM recebida não inclui esse campo e não foi localizada uma fonte oficial vinculada confirmada.
- O denominador do SINASC foi incorporado ao projeto em forma agregada (`data/processed/sinasc_sexo_ano.csv`), com a mesma restrição metodológica do estudo anterior: uso apenas em nível agregado, sem cruzamento de linhas individuais e sem alterar o repositório do SINASC.
- O ponto que permanece parcialmente aberto é a validação final de qualidade e de duplicidade nas bases; a lógica de deduplicação e exclusão não foi aplicada de forma definitiva, mas também não foi usada para sustentar conclusões estatísticas.
- Em resumo, os pontos fundamentais já resolvidos são: origem da base, estrutura do fluxo, foco da investigação, agregação do denominador e cálculos preliminares. Os pontos que ainda exigem validação adicional são: compatibilidade geográfica/temporal completa, definição final de exclusões e presença de fonte vinculada para peso ao nascer.

## 2026-11-08 — Correção do desenho para seguir a atividade avaliativa

- Após conferir o enunciado integral da atividade, foi constatado que os testes exploratórios anteriores não atendiam ao requisito de comparar população e AAS, nem cobriam duas hipóteses para proporção e duas para média. Eles não são resultados da avaliação.
- O usuário aprovou a população operacional de registros de óbito infantil aproximado: 1.776 linhas não fetais com datas válidas e diferença de 0 a 11 meses entre nascimento e óbito.
- Foi gerada uma AAS sem reposição de 316 linhas, com 95% de confiança, margem de erro de 5 pontos percentuais, p = 0,5, correção de população finita e semente 2026.
- Foram implementados os quatro testes da atividade: proporção masculina; diferença entre sexos na proporção de registros no mesmo mês/ano; idade média aproximada versus 1 mês (unilateral); e diferença da idade média aproximada entre sexos.
- Erros-padrão e intervalos usam correção para população finita, pois a fração amostral é 17,79%.
- Os métodos, resultados da AAS, condições e limitações estão documentados em `docs/hipoteses_e_testes.md`. O resumo de dados preparado para os painéis é agregado e não contém registros individuais.
- A aplicação possui três páginas Streamlit correspondentes aos painéis exigidos. A publicação final e o vídeo permanecem reservados para revisão antes de 15/11/2026.

## Artefatos exploratórios anteriores

- `docs/perfil_inicial.md`, `docs/analise_descritiva_sim.md` e `docs/relatorio_metodos_resultados_limites.md` preservam análises exploratórias anteriores; não devem ser usados como resultados da atividade.
- `docs/relatorio_final_sim.md` e `docs/relatorio_final_sim.tex` foram reescritos para a atividade, com o dimensionamento, a AAS, os intervalos e os quatro testes definidos conforme o enunciado.
- O PDF foi compilado em quatro páginas; a tabela de resumo foi ajustada para eliminar o aviso de linha excedente. A compilação terminou com código 0.
- Os três painéis foram abertos e verificados no navegador; navegação, conteúdo e ausência de dados individuais foram conferidos. Testes automatizados, verificação de sintaxe e checagem de whitespace também passaram.
- Permanecem pendentes: revisão metodológica final, preenchimento dos links públicos após publicação, vídeo de até cinco minutos e preparação da entrega no Moodle antes de 15/11/2026.
- Em 08/11/2026, foi incluída no relatório a moda (zero mês) ao lado da mediana (zero mês), com a frequência observada: 939/1.776 registros da população (52,87%) e 168/316 da amostra (53,16%) têm diferença de mês/ano igual a zero. Isso explica as medidas sem sugerir idade exata em dias.
- O cálculo independente do tamanho amostral confirma `n = 316` (valor não arredondado ≈ 315,99). O endereço da calculadora USP/Bauru expirou por timeout tanto na consulta web quanto na tentativa HTTP direta; a conferência direta no site permanece pendente.
- A publicação via GitHub ainda não está configurada neste diretório: não há remoto Git cadastrado nem configuração `.github/`. Antes de publicar, será necessário criar/vincular o repositório, verificar a exclusão de microdados e decidir/implementar hospedagem pública dos painéis.
