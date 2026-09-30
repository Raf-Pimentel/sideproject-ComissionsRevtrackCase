# Arquitetura e convenções

## Fluxo

```
data/raw (xlsx do cliente, somente leitura)
   -> load.py      lê e padroniza colunas, converte formato BR (números e datas)
   -> clean.py     normaliza nomes (cadastro = fonte de verdade)
   -> model.py     junta baixa -> venda, marca competência e R4 (comissionável)
   -> rules/       R1..R7, uma função por regra, sem I/O
   -> closing.py   aplica as regras e consolida por comissionado x mês
   -> compare.py   compara com o controle da Carla (tolerância R$ 1,00)
   -> export.py    outputs/fechamento_solarix.xlsx
```

Fora do cálculo, `checks.py` detecta anomalias nos dados e `reports/` gera os relatórios (anomalias, conferência em xlsx, cálculo detalhado de uma pessoa).

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `src/solarix/config.py` | Caminhos, parâmetros das regras (faixas, %, prazos) e chaves de cenário |
| `src/solarix/rules/` | `r1_projetos`, `r2_assinaturas`, `r3_split`, `r4_cancelamento`, `r5_meta`, `r6_rampagem`, `r7_override` |
| `src/solarix/reports/` | `anomalias`, `conferencia`, `detalhe` |
| `tests/` | Testes por regra, com casos de borda |
| `docs/` | Briefing, decisões, perguntas para a cliente, pendências, este arquivo |
| `outputs/` | Entregáveis gerados (xlsx) |

## Princípios
- **Dados brutos imutáveis.** Toda transformação é reproduzível por código.
- **Regras como funções puras** (DataFrame entra, DataFrame sai), testáveis sem arquivos.
- **Parâmetros em `config.py`.** Nenhum número de regra de negócio dentro das funções. Decisões em aberto viram chaves (`ITEM_SEM_PCT_ENTRA_NO_RATEIO`, `INCLUIR_BAIXAS_APOS_EMISSAO`).
- **Rastreabilidade.** O fechamento tem a aba "Comissão por baixa", e `reports/detalhe.py` mostra cada conta.
- **Dinheiro:** arredondamento explícito (`money.r2`, meio para cima) por linha de cálculo.
- **Falhar alto:** joins com `validate=`, asserts de integridade, leitura por posição de coluna.
- **Qualidade:** `ruff check src tests` e `pytest` devem passar antes de cada commit.

## Convenção de comentários
- Docstring curta em todo módulo e função pública: o que faz, não como.
- Comentário de linha só para o **porquê** (regra de negócio, decisão, armadilha dos dados), citando a regra (R1 a R7) ou o ID da decisão/anomalia.
- Sem comentário que repita o código.
- Toda hipótese assumida no código consta em `docs/decisoes.md`.

## Uso do Claude neste projeto
- O Claude implementa e testa; o Rafael valida e decide as ambiguidades.
- Nenhuma ambiguidade é decidida em silêncio: vai para `docs/decisoes.md`.
- Números em documentos e mensagens vêm da saída do código, não de memória.
- Toda divergência com a cliente é classificada (arredondamento, regra ambígua, erro da cliente, erro nosso, dado sujo).
- O Claude não tem acesso à conta da RevTrack; entrega a especificação para replicar.
