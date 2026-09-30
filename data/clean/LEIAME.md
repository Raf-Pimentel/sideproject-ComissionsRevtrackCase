# Bases limpas para a RevTrack

Geradas por `python -m solarix.clean_export` a partir de `data/raw/`. O comando **não grava nada** se a validação encontrar qualquer erro (chaves duplicadas, campos vazios, valores fora do domínio, vendas sem item, baixas sem venda, nomes fora do cadastro, espaços sobrando etc.). Última validação: **0 erros**.

Cada base existe em dois formatos com o mesmo conteúdo:
- `csv/`: UTF-8 sem BOM, separador vírgula, ponto decimal, datas `AAAA-MM-DD`, vazio = sem valor.
- `xlsx/`: uma planilha por base, datas como data do Excel.

## Bases

| Arquivo | Linhas | Chave | O que é |
|---|---|---|---|
| `01_vendas` | 60 | `id_venda` | Cabeçalho das vendas (46 projetos e 14 assinaturas) |
| `02_itens` | 89 | `id_item` | Itens de cada venda (liga por `id_venda`) |
| `03_baixas` | 115 | `n_baixa` | Pagamentos do ERP, jun a set/2026 (liga por `id_venda`) |
| `04_tabela_comissao` | 12 | `linha_produto` + `canal` | % de comissão por linha de produto e canal |
| `05_cadastro` | 8 | `nome` | Time comercial (6 consultores e 2 gerentes) |
| `06_controle_carla` | 16 | `nome` + `competencia` | Controle manual da cliente (só para conferência, não é insumo do cálculo) |

## Dicionário de colunas

**01_vendas**: `id_venda` (inteiro) · `tipo` (PROJETO ou ASSINATURA) · `data_venda` (data) · `cliente` · `vendedor` (nome do cadastro) · `vendedor2` (nome do cadastro, vazio se não há venda conjunta) · `canal` (DIRETO, PARCEIRO ou INDICACAO) · `desconto_pct` (pontos percentuais: 12 = 12%) · `status` (ATIVA ou CANCELADA) · `data_cancelamento` (data, só nas canceladas)

**02_itens**: `id_item` (ex.: 1001-1) · `id_venda` · `linha_produto` (KIT_RESIDENCIAL, KIT_COMERCIAL, INSTALACAO ou MONITORAMENTO) · `descricao` · `valor_bruto` (R$, antes do desconto)

**03_baixas**: `n_baixa` · `n_parcela` (ex.: 1004-P01) · `id_venda` · `parcela` (nº da parcela) · `total_parcelas` · `valor_parcela` (R$) · `valor_pago` (R$, pode ser menor que a parcela) · `data_pagamento` (data)

**04_tabela_comissao**: `linha_produto` · `canal` · `pct_comissao` (pontos percentuais: 2.5 = 2,5%) · `observacao`

**05_cadastro**: `nome` · `cargo` · `equipe` (Capital ou Interior) · `gerente` (vazio para gerentes) · `data_admissao` (data) · `meta_mensal` (R$, vazio para gerentes) · `email` (fictício)

**06_controle_carla**: `nome` · `competencia` (AAAA-MM) · `comissao` · `bonus_meta` · `rampagem` · `override` · `total` (R$)

## O que foi alterado em relação aos originais

| # | Alteração | Onde | Motivo |
|---|---|---|---|
| 1 | "João Pedro Almeida" estava escrito de 3 jeitos (sem acento, com espaço no fim): unificado com o nome do cadastro | `vendas.vendedor` e `vendas.vendedor2` (10 linhas) | Um join por nome perderia essas vendas |
| 2 | Adicionada a linha INSTALACAO / PARCEIRO com 0% e observação explicando | `tabela_comissao` (1 linha, marcada na coluna `observacao`) | A tabela do cliente não tem essa combinação (a instalação no canal PARCEIRO é feita pelo parceiro) e a venda 1006 tem um item assim. Decisão D2 |
| 3 | Números e datas do ERP convertidos do formato brasileiro (`23.503,28`, `09/06/2026`) | `baixas` | Padronização |
| 4 | Linhas de título do relatório do ERP removidas; colunas renomeadas para `snake_case` | `baixas` e demais | Padronização |
| 5 | Espaços nas pontas e repetidos removidos de todos os textos | todas | Evita falhas de comparação |

Nenhuma linha de dado foi excluída. Nenhum valor monetário foi alterado.

## O que NÃO foi feito de propósito
- **Nenhuma coluna calculada** (rateio, competência, split, cancelamento, rampagem...). Elas devem ser criadas na plataforma.
- **Anomalias de negócio não foram "corrigidas"**: pagamentos com data após a emissão do relatório, pagamentos depois do cancelamento, parcela paga pela metade, vendas sem pagamento. São fatos dos dados do cliente e estão em `docs/perguntas_carla.md`.
