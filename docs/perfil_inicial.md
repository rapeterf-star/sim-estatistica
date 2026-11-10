# Perfil inicial da base SIM — Porto Alegre

> **Documento histórico de triagem.** Os números e critérios abaixo são preliminares e não representam os resultados finais da atividade avaliativa. Para o desenho aprovado, a amostra e os testes, consulte [o relatório final](./relatorio_final_sim.md) e [as hipóteses e testes](./hipoteses_e_testes.md).

**Caráter:** triagem exploratória para orientar o planejamento. Os números abaixo descrevem o CSV tal como recebido; não são resultados finais nem incluem qualquer correção das duplicidades.

## Origem e cobertura

- Fonte: [SIM — Sistema de Informações de Mortalidade, Dados Abertos de Porto Alegre](https://dadosabertos.poa.br/dataset/mortalidade-e-obitos), Secretaria Municipal de Saúde.
- Licença informada no catálogo: Creative Commons Attribution (CC BY); atribuir a fonte nas publicações.
- A cópia recebida corresponde em tamanho ao recurso publicado, atualizado no catálogo em 1º de outubro de 2026.
- 135.548 linhas, 14 campos; óbito registrado por mês/ano, de janeiro de 2011 a dezembro de 2021.
- 133.787 registros são classificados como não fetais e 1.761 como fetais.

## Variáveis aproveitáveis para planejamento

Há campos para sexo, raça/cor, escolaridade, causa básica CID, tipo de óbito e um indicador `obito_prematuro`. O dicionário não define como o indicador de óbito prematuro é calculado; não o usaremos até confirmar sua regra.

Nascimento e óbito são informados somente por mês e ano. Uma idade aproximada pode ser calculada pela diferença entre os meses, mas não equivale a uma idade exata em dias ou anos completos. Para comparações por idade, os registros fetais e aqueles sem mês/ano de nascimento válido não permitem esse cálculo. A classificação junto a um limite etário também pode ser incerta.

Os registros são óbitos, não denominadores populacionais. Portanto, contagens ou proporções dentro desta base descrevem a composição dos óbitos, não o risco ou a taxa de mortalidade de cada grupo.

## Qualidade e privacidade

- Foram identificadas 602 linhas integralmente repetidas no arquivo; 453 delas estão entre os registros não fetais. Não foram removidas.
- O dicionário descreve `identificador_pessoa2` como identificador cifrado. Ele está ausente em muitos registros e concentra-se excessivamente em um único valor; não é uma chave confiável para deduplicação ou vinculação na cópia recebida.
- A indicação `obito_prematuro` tem 28.636 casos “Sim”, mas sua definição operacional não consta no dicionário recebido.
- Microdados e derivados em nível individual permanecem locais. A base não deve ser publicada no aplicativo ou enviada a terceiros.

## Foco indicado pelo usuário

O usuário quer investigar (1) sexo e óbitos de bebês, distinguindo proporção entre os casos de risco de mortalidade, e (2) peso ao nascer entre bebês que morreram, se houver dados apropriados. Não deseja transformações alheias às perguntas; só corrigir erros de dados quando forem confirmados e relevantes.

### Sexo nos registros de óbito: números descritivos preliminares

| Grupo no CSV recebido | Masculino | Feminino | Sexo ausente | Proporção masculina entre sexos conhecidos |
| --- | ---: | ---: | ---: | ---: |
| Óbitos fetais | 929 | 766 | 66 | 54,8% |
| Óbitos não fetais com diferença entre os meses de nascimento e óbito menor que 12 | 971 | 798 | 7 | 54,9% |

O grupo não fetal com diferença de meses menor que 12 é apenas uma aproximação operacional de óbito antes de um ano: o CSV não registra o dia do nascimento nem do óbito. Há 149 linhas repetidas entre os registros fetais e 29 no grupo infantil aproximado; esses registros foram mantidos e não se devem tratar os percentuais como resultados finais.

Testar se a proporção masculina nos óbitos é 50% descreve a composição dos registros de óbito. Isso, isoladamente, **não** demonstra que sexo aumente o risco de morrer. Para estimar e comparar risco/taxa por sexo são necessários denominadores de nascimentos por sexo, período e geografia compatível. Uma análise agregada com dados do SINASC pode ser possível, sem vincular linhas individuais nem alterar o projeto SINASC, após confirmar que o usuário autoriza esse uso e que as definições geográficas e temporais coincidem.

O usuário autorizou usar apenas contagens agregadas do SINASC por sexo e ano como denominadores, sem alterar o projeto SINASC nem fazer vinculação individual. Como verificação exploratória, foram agregados todos os nascidos vivos de 2011–2020, sem o corte de 500 g usado no SINASC anterior. Considerando óbitos não fetais com diferença entre os meses de nascimento e óbito menor que 12, coortes de nascimento de 2011–2020 e sexo conhecido:

| Sexo | Nascidos vivos no SINASC | Óbitos infantis aproximados no SIM | Óbitos antes de 1 ano por 1.000 nascidos vivos (provisório) |
| --- | ---: | ---: | ---: |
| Feminino | 89.719 | 744 | 8,29 |
| Masculino | 93.915 | 890 | 9,48 |

O SINASC indica 51,1% de nascimentos masculinos no período, não exatamente 50%. As razões acima são agregadas e preliminares, não um teste inferencial nem conclusão de efeito causal. Há 27 linhas integralmente repetidas no numerador de óbitos usado nesta agregação. A compatibilidade territorial dos registros de óbito e dos nascimentos, a definição de seguimento e o tratamento dessas repetições ainda precisam ser validados antes de testar ou publicar as taxas.

### Peso ao nascer: indisponível neste CSV

O arquivo SIM tem 14 colunas e nenhuma contém peso. O dicionário também não define peso ao nascer. Há faixa de gestação em semanas para alguns registros, mas isso não é medida de peso. O ID de paciente cifrado está ausente em muitos registros, concentra-se excessivamente em um único valor e não tem uma coluna correspondente no arquivo SINASC; não é uma chave confiável para ligar este SIM ao SINASC.

Assim, não é possível testar com os arquivos atuais se o peso dos bebês que morreram difere de cerca de 3.100 g. O CSV SINASC separado contém peso dos nascidos vivos, mas não tem chave comum confiável para identificar quais registros correspondem aos óbitos. Uma busca inicial no catálogo oficial de Porto Alegre não encontrou uma publicação vinculada SIM–SINASC; isso não exclui acesso restrito ou outra fonte ainda não localizada. Para isso é necessária uma base oficial já vinculada contendo, para cada nascimento, peso e desfecho, ou outro mecanismo de vinculação confiável e autorizado. A média de todos os nascimentos do SINASC não substitui a média dos bebês falecidos.

### Próximos testes a planejar

1. Verificar a composição por sexo nos óbitos infantis e comparar riscos por sexo usando os denominadores agregados do SINASC, somente depois de validar a compatibilidade geográfica, temporal e de coorte.
2. Investigar se existe uma fonte oficial vinculada com peso ao nascer e desfecho de óbito. Se for localizada, propor testes de média de peso; se não, não inferir peso a partir da gestação.
3. Completar os quatro testes exigidos com perguntas sustentadas por variáveis disponíveis; não apresentar peso como analisável até obter dados vinculados.

As hipóteses e os quatro testes finais ainda serão definidos após validar a taxa por sexo e verificar a disponibilidade de uma fonte de peso vinculada.
