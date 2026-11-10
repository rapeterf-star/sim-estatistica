# Análise descritiva inicial do SIM

> **Documento histórico de análise exploratória.** Este resumo não corresponde aos painéis descritivos finais da população e da AAS. Para os resultados da atividade, consulte [o relatório final](./relatorio_final_sim.md) e os painéis da aplicação.

Status: resumo provisório, baseado no CSV recebido e sem correção de duplicidades ou exclusões definitivas.

## 1) Panorama geral

- Total de registros: 135548
- Registros com sexo conhecido: 135440
- Óbitos fetais no arquivo: 1761
- Óbitos fetais com sexo conhecido: 1695
- Óbitos fetais sem sexo informado: 66
- Óbitos infantis aproximados (< 12 meses): 1769

## 2) Distribuição por sexo

| Sexo | Registros | % do total com sexo conhecido |
| --- | ---: | ---: |
| FEMININO | 67432 | 49.79% |
| MASCULINO | 68008 | 50.21% |

## 3) Óbitos fetais por sexo

| Sexo | Óbitos fetais com sexo conhecido | % do total de fetais com sexo conhecido |
| --- | ---: | ---: |
| FEMININO | 766 | 45.19% |
| MASCULINO | 929 | 54.81% |

## 4) Óbitos infantis aproximados por sexo

| Sexo | Óbitos infantis aproximados | % do total infantil aproximado |
| --- | ---: | ---: |
| FEMININO | 798 | 45.11% |
| MASCULINO | 971 | 54.89% |

## 5) Interpretação metodológica

- Os valores acima são descritivos e dependem da regra operacional de óbito infantil aproximado: diferença menor que 12 meses entre os campos de nascimento e óbito.
- O arquivo não registra data completa; por isso, a idade é aproximada e deve ser interpretada com cautela.
- Para inferir risco por sexo, ainda são necessários denominadores agregados compatíveis do SINASC e validação geográfica, temporal e de coorte.
- Não há comparação de peso ao nascer neste passo, porque a base recebida não contém esse campo e não há base oficial vinculada confirmada.
