# Como configurei a conta da Solarix na RevTrack

Configuração das 7 regras do plano de comissões (R1 a R7) para os meses de agosto e setembro/2026, validada contra um cálculo de referência independente em Python e contra o controle manual da Carla.

## 1. Visão geral

```
6 fontes (CSV) ──> conjuntos de dados (joins) ──> colunas calculadas ──> componentes ──> planos ──> relatório
```

- **Regime de caixa:** a comissão, o override e a rampagem pertencem ao mês da **data de pagamento** da baixa. O bônus de meta pertence ao mês da **data da venda**.
- **Duas camadas independentes:** a plataforma calcula; o pipeline em Python (`src/solarix/`) recalcula tudo por conta própria e serve de conferência. Os dois só são comparados no fim.
- **Fontes:** as bases tratadas (`data/clean/`, CSV) foram geradas pelo código com validação (chaves, domínios, integridade, nomes do cadastro). Nenhuma regra de negócio foi aplicada nos arquivos: elas vivem na plataforma.

## 2. Fontes de dados

| Fonte | Linhas | Uso |
|---|---|---|
| `01_vendas` | 60 | Cabeçalho da venda: vendedor, vendedor 2, canal, desconto, status, datas |
| `02_itens` | 89 | Itens de cada venda (linha de produto e valor bruto) |
| `03_baixas` | 115 | Pagamentos do ERP (base do regime de caixa) |
| `04_tabela_comissao` | 12 | % de comissão por linha de produto e canal (inclui a linha adicionada de instalação em PARCEIRO a 0%, decisão D2) |
| `05_cadastro` | 8 | Equipe, gerente, admissão e meta mensal |
| `06_controle_carla` | 16 | Só referência para conferência. **Não entra no cálculo.** |

## 3. Conjuntos de dados (joins)

Todos os joins são do tipo **esquerda (Left Join)**, para que uma baixa nunca desapareça em silêncio. Cada conjunto foi conferido pela contagem de linhas.

### 3.1 Cadeia da comissão (uma linha por baixa e por item)

| Conjunto | Construção | Chave | Linhas |
|---|---|---|---|
| `total_bruto_venda` | Agrupamento de `02_itens` por venda, soma de `valor_bruto` | `id_venda` | 60 |
| `baixa_venda` | `03_baixas` ⟕ `01_vendas` | `id_venda` | 115 |
| `baixa_item` | `baixa_venda` ⟕ `02_itens` | `id_venda` | 161 |
| `baixa_item_total` | `baixa_item` ⟕ `total_bruto_venda` | `id_venda` | 161 |
| `baixa_item_pct` | `baixa_item_total` ⟕ `04_tabela_comissao` | `linha_produto` **e** `canal` | 161 |
| `baixa_item_gerente` | `baixa_item_pct` ⟕ `05_cadastro` | `vendedor` = `nome` | 161 |

Os 161 vêm de 115 baixas multiplicadas pelos itens da venda (31 vendas com 1 item e 29 com 2). Um número diferente de 161 em qualquer etapa indicaria join errado.

### 3.2 Cadeia da meta (uma linha por item e por pessoa)

| Conjunto | Construção | Linhas |
|---|---|---|
| `venda_item` | `02_itens` ⟕ `01_vendas` por `id_venda` | 89 |
| `meta_principal` | `venda_item` ⟕ `05_cadastro` por `vendedor` = `nome` | 89 |
| `meta_vendedor2` | `venda_item` ⟕ `05_cadastro` por `vendedor2` = `nome` | 89 |
| `meta_base` | União (Union All) de `meta_principal` e `meta_vendedor2` | 178 |

A união coloca a venda conjunta nas duas pessoas (60% e 40%) e permite somar o atingimento de cada consultor, juntando os dois papéis.

## 4. Colunas calculadas

### Em `baixa_item_pct`

| Coluna | Fórmula | Regra |
|---|---|---|
| `peso_item` | `{valor_bruto} / {total_bruto}` | R1: parte do item no valor da venda |
| `competencia` | `YEAR({data_pagamento}) * 100 + MONTH({data_pagamento})` | Regime de caixa |
| `redutor` | `IF({tipo} = "ASSINATURA", 1, CASE WHEN {desconto_pct} <= 5 THEN 1 WHEN {desconto_pct} <= 10 THEN 0.8 WHEN {desconto_pct} <= 15 THEN 0.6 ELSE 0.4 END)` | R1: redutor de desconto, limites inclusivos (D3); assinatura sem redutor |
| `base_item` | `{valor_pago} * {peso_item}` | R1: rateio do pago entre os itens |
| `dias_cancel` | `DATEDIFF({data_cancelamento}, {data_venda})` | R4 |
| `comissionavel` | `IF({status} = "ATIVA", 1, IF({dias_cancel} <= 60, 0, IF({data_pagamento} > {data_cancelamento}, 0, 1)))` | R4: até 60 dias zera tudo; depois só conta até a data do cancelamento |
| `comissao_item` | `IF({comissionavel} = 0, 0, IF({tipo} = "ASSINATURA", IF({parcela} = 1, ROUND({base_item} * {pct_comissao} / 100, 2), 0), ROUND({base_item} * {pct_comissao} / 100 * {redutor}, 2)))` | R1 e R2: projetos pelo % da tabela com redutor; assinatura só na 1ª parcela (50% da tabela) |
| `comissao_vendedor2` | `IF(COALESCE({vendedor2}, "") = "", 0, ROUND({comissao_item} * 0.4, 2))` | R3: 40% |
| `comissao_vendedor1` | `{comissao_item} - {comissao_vendedor2}` | R3: o restante (60%), a soma sempre fecha |

### Em `baixa_item_gerente`

| Coluna | Fórmula | Regra |
|---|---|---|
| `override_item` | `IF({comissionavel} = 0, 0, IF({tipo} = "ASSINATURA", IF({parcela} = 1, ROUND({base_item} * 0.01, 2), 0), ROUND({base_item} * 0.01, 2)))` | R7: 1% do valor pago das baixas comissionáveis que geram comissão |

A coluna `gerente` vem do join com o cadastro (gerente do vendedor principal).

### Em `meta_principal` e `meta_vendedor2`

| Coluna | Fórmula | Regra |
|---|---|---|
| `pessoa` | `{vendedor}` (principal) ou `{vendedor2}` (vendedor 2) | Quem recebe |
| `base_meta` (principal) | `IF({tipo} = "PROJETO" AND {status} = "ATIVA", {valor_bruto} * (1 - {desconto_pct} / 100) * IF(COALESCE({vendedor2}, "") = "", 1, 0.6) / {meta_mensal}, 0)` | R5 e R3: valor líquido do projeto não cancelado, com split, em fração da meta da pessoa |
| `base_meta` (vendedor 2) | igual, com `AND COALESCE({vendedor2}, "") != ""` e fator `0.4` | R5 e R3 |

## 5. Meta, planos e componentes

**Meta:** `Meta mensal de vendas`, tipo Número, recorrente, mensal, "altera ao longo do tempo", com **100** em agosto e em setembro. A meta da plataforma é uma só para todos, e as metas individuais são diferentes (R$ 60 mil a R$ 150 mil). Por isso a divisão pela meta de cada pessoa foi feita na coluna `base_meta`, de modo que o atingimento de qualquer um seja medido contra o mesmo "100%".

### Plano `Solarix - Comissões 2026`
Membros: Ana Ribeiro, Bruno Sato, Camila Duarte, João Pedro Almeida (consultores), Marcos Teles e Paula Nogueira (gerentes).

| Componente | Conjunto | Vendedor | Base de vendas | Data | Ganho |
|---|---|---|---|---|---|
| Comissão – vendedor principal | `baixa_item_pct` | `vendedor` | `comissao_vendedor1` | `data_pagamento` | Comissão, taxa única de 100% |
| Comissão – vendedor 2 | `baixa_item_pct` | `vendedor2` | `comissao_vendedor2` | `data_pagamento` | Comissão, taxa única de 100%. Filtro: `comissao_vendedor2 > 0` |
| Override de gerência (1%) | `baixa_item_gerente` | `gerente` | `override_item` | `data_pagamento` | Comissão, taxa única de 100%. Filtro: `override_item > 0` |
| Bônus de meta | `meta_base` | `pessoa` | `base_meta` | `data_venda` | Bônus por faixas, "Alcance %", soma total dos negócios, meta ligada |

As faixas do bônus (R5): 0 a 80% = R$ 0; 80 a 100% = R$ 800; 100 a 120% = R$ 1.500; 120% ou mais = R$ 2.500. O limite final é 999, porque a plataforma exige limite superior em todas as faixas.

Nos componentes de comissão e override, o valor da coluna já é a comissão final de cada linha, e a taxa de 100% só o repassa.

### Plano `Rampagem` (R6)
Membros: Diego Ferraz e Érica Lins (consultores nos 3 primeiros meses de casa).

- **Componentes:** os mesmos de comissão do plano principal (vendedor principal e vendedor 2) e o Bônus de meta.
- **Mínimo garantido:** R$ 1.500, base "bruto dos componentes selecionados", **selecionando só as duas comissões**. O bônus de meta fica fora da soma, como manda a regra. A plataforma paga a diferença quando a soma das comissões do mês é menor que R$ 1.500.
- O período da garantia é definido por quem está no plano: o Diego (admitido em 20/07) está na garantia em julho, agosto e setembro; a Érica (admitida em 03/08), em agosto, setembro e outubro. Ao fim dos 3 meses, a pessoa passa para o plano principal (a plataforma não faz essa troca sozinha).

## 6. Validação

**Contra o Python (7 regras, ago + set):**

| Pessoa | RevTrack | Python | Diferença |
|---|---|---|---|
| João Pedro Almeida | 10.410,44 | 10.410,29 | 0,15 |
| Ana Ribeiro | 8.957,16 | 8.957,29 | 0,13 |
| Bruno Sato | 7.502,29 | 7.502,30 | 0,01 |
| Camila Duarte | 6.670,52 | 6.670,55 | 0,03 |
| Diego Ferraz | 7.843,07 | 7.843,05 | 0,02 |
| Érica Lins | 7.025,62 | 7.025,65 | 0,03 |
| Paula Nogueira | 6.108,07 | 6.108,07 | 0,00 |
| Marcos Teles | 4.193,27 | 4.193,25 | 0,02 |
| **Total** | **58.710,44** | **58.710,45** | **0,01** |

As diferenças de centavos vêm do arredondamento: a plataforma arredonda por item, e o Python por baixa. Todas ficam bem abaixo da tolerância de R$ 1,00.

**Contra o controle da Carla:** 13 das 16 linhas (pessoa e mês) batem. Bônus de meta e override batem nas 16. As três que não batem estão em `docs/mensagem_carla.md` e `docs/decisoes.md` (P1, P2, P3):
- Érica, setembro: rampagem de R$ 1.309,84 que não consta no controle.
- Bruno, setembro: comissão R$ 638,03 abaixo do controle (não explicada).
- Camila, agosto: comissão R$ 184,00 abaixo do controle (não explicada).

## 7. Hipóteses assumidas

As decisões com status completo estão em `docs/decisoes.md`. As principais:

- **D1 (confirmada):** pagamentos de 26 a 30/09 entram, apesar de o relatório do ERP ser "emitido em 25/09". O controle da Carla também os inclui.
- **D2 (confirmada):** a instalação da venda 1006 (canal PARCEIRO) tem 0% de comissão, mas continua na divisão do pagamento entre os itens (Opção A: R$ 388,20; Opção B daria R$ 457,42).
- **D3 (confirmada):** os limites de 5%, 10% e 15% de desconto são inclusivos.
- **D4 a D8 (padrão, aguardam confirmação):** override sobre 100% do valor pago em venda conjunta, arredondamento por item, 60 dias contados como cancelamento menos venda, rampagem sobre R1 + R2 após o split (sem o bônus), bônus de meta com meta cheia (sem proporcionalidade).
- Vendas conjuntas contam 60/40 também no bônus de meta.
- Parcela paga pela metade (venda 1031): comissiona-se só o que foi pago.

## 8. Limitações conhecidas

- **Cartão "Vendas Totais" do relatório.** Ele soma o campo "Base de vendas" de cada componente, que aqui é a própria comissão (ou o atingimento da meta). Por isso o valor não representa faturamento e não deve ser lido como tal. O faturamento real do período está na planilha de fechamento (pago de R$ 1,03 milhão e vendido de R$ 1,13 milhão).
- **Faixas do bônus em 999%.** Usado como "sem limite", porque a plataforma exige limite superior.
- **Meta única de valor 100.** Contorno para a meta global; a meta real de cada pessoa está no cadastro e entra na coluna `base_meta`.
- **Pessoas sem comissão no mês.** Sem linha de dados no mês, o comportamento do mínimo garantido deve ser testado antes de um uso em produção. Nos dados de agosto e setembro isso não ocorre.
- **Troca de plano ao fim da rampagem** é manual.
- **PROCV só em arquivos originais.** Por isso o cadastro entra por join nas conexões e não por busca.

### Como a rampagem foi resolvida
A primeira tentativa foi um arquivo com o complemento calculado em Python, porque os componentes de ganho (bônus, comissão, faixas) não fazem "1.500 menos o total do mês". Depois, com a orientação do time da RevTrack, a regra passou a usar o recurso de **Mínimo Garantido do plano**, o que a deixou 100% dentro da plataforma e recalculável. O arquivo foi descartado.

## 9. Pendências

- Respostas da Carla (`docs/mensagem_carla.md`): Érica, Bruno, Camila e os 5 itens de confirmação. Qualquer resposta que mude os dados exige recalcular em **Cálculos > Por Período** (01/08/2026 a 30/09/2026).
- Confirmação das decisões D4 a D8.
- Teste do mínimo garantido para uma pessoa sem nenhuma comissão em um mês de rampagem.
- Exportar os relatórios de agosto e setembro da plataforma para a planilha de fechamento, se for desejado que ela traga os números da plataforma em vez dos do Python (hoje diferem por centavos).

## 10. Como recalcular

1. Conferir se as fontes estão sincronizadas (Integrações).
2. **Cálculos > Por Período**, com as datas do período, e esperar o status "Concluído".
3. Se foi alterada uma coluna calculada, um componente ou o plano de algum membro, usar **Reprocessar Tudo** uma vez.
4. Abrir **Relatórios**, filtrar o período e comparar com o `outputs/fechamento_solarix.xlsx`.
