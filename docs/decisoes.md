# Registro de decisões — Projeto SIM

## 2026-11-08 — Abertura do projeto

- O projeto SIM fica em diretório separado do projeto SINASC: `C:\Users\maque\VSCODE\sim-estatistica`.
- Foram copiadas para este diretório a base recebida e sua documentação, sem mover nem alterar os arquivos do SINASC.
- A fonte é o conjunto [SIM — Sistema de Informações de Mortalidade](https://dadosabertos.poa.br/dataset/mortalidade-e-obitos), publicado pela Secretaria Municipal de Saúde de Porto Alegre. O catálogo indica licença CC BY; atribuir a fonte nas publicações.
- A abrangência territorial confirmada é Porto Alegre.
- Os campos de nascimento e óbito registram mês/ano, não datas completas; uma idade calculada a partir deles será aproximada.
- A base original e dados derivados em nível de registro não devem ser publicados nem versionados.
- Nenhum filtro, deduplicação, população analítica, amostra ou hipótese foi definido nesta etapa.
- Antes do planejamento estatístico, é necessário esclarecer as duplicidades e o identificador descrito como cifrado.
- Foi confirmado o formato geral das entregas e a realização de quatro testes, com perguntas e variáveis adaptadas ao SIM.
- O foco indicado pelo usuário é sexo e óbitos de bebês e, se houver dados apropriados, peso ao nascer entre bebês que morreram.
- O usuário pediu que mudanças se restrinjam a operações relacionadas ao estudo e à correção de erros de dados confirmados.
- O SIM recebido não contém campo de peso; o perfil registra números descritivos de sexo e as limitações sobre risco e peso. Não foi feita vinculação individual com o SINASC.
- O usuário autorizou usar somente contagens agregadas do SINASC por sexo e ano como denominadores para estimar taxas; nenhum arquivo do SINASC foi alterado ou copiado.
- As taxas exploratórias de óbito infantil por sexo estão registradas em `docs/perfil_inicial.md`; permanecem provisórias até verificar a compatibilidade territorial/temporal e esclarecer as repetições relevantes.
- O arquivo SIM não contém peso ao nascer e não há identificador comum confiável com o CSV SINASC. Não é possível estimar peso entre óbitos com as cópias atuais.
- Uma busca inicial no catálogo oficial de Porto Alegre não localizou uma publicação pública vinculada SIM–SINASC com peso e desfecho; a busca não exclui fonte restrita ou outra fonte ainda não localizada.

## 2026-11-08 — Desenho da atividade avaliativa final

- O enunciado integral da atividade da disciplina é a referência normativa para este projeto; a estrutura do trabalho SINASC foi usada como modelo de etapas e painel, não como substituto do enunciado.
- A população deste exercício foi restringida aos 1.776 registros não fetais com nascimento e óbito válidos em mês/ano, ano do óbito de 2011 a 2021 e diferença entre competências de 0 a 11 meses. Essa proposta foi apresentada ao usuário e aprovada.
- A idade ao óbito é uma variável derivada aproximada. O usuário aprovou usá-la como medida quantitativa, mantendo a ressalva de que o SIM não contém datas completas.
- O tamanho da AAS é 316, calculado para confiança de 95%, erro de 5 p.p., `p = 0,5` e população finita. O sorteio sem reposição usa semente 2026.
- As quatro hipóteses foram operacionalizadas como no estudo anterior: um teste de uma proporção, um teste de diferença de proporções, um teste de uma média e um teste de diferença de médias.
- Como `n/N = 17,79%`, a análise aplica correção para população finita aos erros-padrão e intervalos. Não se usa a regra de independência aproximada de 10% sem correção.
- A comparação de proporção masculina em registros de óbito não equivale a comparação de risco de morte por sexo. Nenhum resultado será descrito como causal.
- Os testes exploratórios preliminares registrados antes de se receber o enunciado não são os testes da atividade e foram substituídos no documento de hipóteses.
- A publicação final permanece agendada para a entrega no Moodle até 15/11/2026 às 23h59; painéis e vídeo devem ser revisados antes do envio.
