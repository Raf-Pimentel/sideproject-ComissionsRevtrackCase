# Como configurei a conta da Solarix na RevTrack

Este documento explica, em linguagem simples, como montei na RevTrack o cálculo das comissões da Solarix para **agosto e setembro de 2026**, por que montei assim, como conferi se está certo e o que ainda falta.

## 1. Em poucas palavras

- Coloquei na RevTrack os dados da Solarix (vendas, itens, pagamentos, tabela de comissão e cadastro dos vendedores).
- Ensinei a plataforma a aplicar as **7 regras** do plano (R1 a R7). **Todas rodam dentro da RevTrack.**
- Fiz o mesmo cálculo por fora, em Python, como uma **segunda opinião**, e comparei os dois. O total bate: **R$ 58.710,44** na plataforma e **R$ 58.710,45** no Python. A diferença (alguns centavos) é só arredondamento.
- Comparei também com o controle manual da Carla: **13 das 16 linhas batem** (cada linha é uma pessoa em um mês). As 3 que não batem estão explicadas na seção 8 e viraram perguntas para ela.

**Uma regra que vale para tudo:** a empresa trabalha em **regime de caixa**. Isso quer dizer que a comissão é do **mês em que o cliente pagou**, e não do mês em que a venda foi fechada. A única exceção é o bônus de meta, que conta pelo mês da venda.

## 2. Glossário rápido (palavras da plataforma)

| Termo | O que é, de forma simples |
|---|---|
| **Fonte de dados** | Um arquivo que subi na plataforma (aqui, 6 arquivos CSV). |
| **Conjunto de dados** | Uma tabela dentro da plataforma, feita a partir de uma ou mais fontes. |
| **Join** (juntar) | Como um PROCV do Excel: pega uma linha de uma tabela, procura o mesmo código em outra e traz as colunas de lá. |
| **Coluna calculada** | Uma coluna nova, com fórmula, igual a uma coluna de fórmula no Excel. |
| **Componente** | Uma forma de a pessoa ganhar dinheiro (por exemplo, "comissão" ou "bônus de meta"). |
| **Plano** | Uma caixa que reúne componentes e define quais pessoas participam. |
| **Baixa** | Um pagamento recebido de um cliente, registrado no ERP. |

## 3. De onde vêm os dados

Subi 6 arquivos, já limpos e validados por código (sem nomes repetidos ou escritos de forma diferente, sem campos obrigatórios vazios, sem vendas sem itens). Nenhuma **regra** foi aplicada nos arquivos. As regras ficam na plataforma, para qualquer pessoa poder ver e alterar.

| Arquivo | O que tem | Linhas |
|---|---|---|
| `01_vendas` | Uma linha por venda: vendedor, segundo vendedor, canal, desconto, status, datas | 60 |
| `02_itens` | Os itens de cada venda (kit, instalação, monitoramento) e o valor de cada um | 89 |
| `03_baixas` | Cada pagamento recebido, com valor e data | 115 |
| `04_tabela_comissao` | O percentual de comissão por tipo de produto e canal | 12 |
| `05_cadastro` | Os 8 comissionados: equipe, gerente, data de admissão e meta | 8 |
| `06_controle_carla` | O controle manual da Carla. **Só serve para conferir, não entra no cálculo.** | 16 |

Uma observação: a tabela original não tinha o percentual de **instalação no canal PARCEIRO**. Adicionei essa linha com **0%**, com uma observação explicando (decisão D2 na seção 9).

## 4. Como juntei os dados

Para calcular uma comissão, preciso ao mesmo tempo do **pagamento** (quanto entrou e quando), da **venda** (quem vendeu, qual o desconto, se foi cancelada) e dos **itens** (o que foi vendido, para saber qual percentual usar). Cada informação está em um arquivo diferente. Então juntei tudo, em etapas, sempre conferindo o número de linhas.

| Etapa | O que fiz | Linhas |
|---|---|---|
| 1 | `total_bruto_venda`: somei o valor dos itens de cada venda | 60 (uma por venda) |
| 2 | `baixa_venda`: juntei cada pagamento com a sua venda | 115 |
| 3 | `baixa_item`: juntei com os itens da venda | 161 |
| 4 | `baixa_item_total`: trouxe o total da venda para cada linha | 161 |
| 5 | `baixa_item_pct`: trouxe o percentual de comissão (por produto **e** canal) | 161 |
| 6 | `baixa_item_gerente`: trouxe o gerente de cada vendedor, do cadastro | 161 |

**Por que 161 linhas, se há só 115 pagamentos?** Porque uma venda pode ter 2 itens (kit e instalação). Cada pagamento de uma venda com 2 itens vira 2 linhas, uma por item. São 31 vendas com 1 item e 29 com 2. Se algum passo desse um número diferente de 161, eu saberia que um join saiu errado.

Usei sempre o join do tipo "esquerda", que **não perde nenhum pagamento** nem em caso de erro. Se algo não tivesse correspondência, apareceria como campo vazio, e não sumiria em silêncio.

## 5. Como cada regra virou uma coluna

Aqui está o coração da configuração. Em vez de calcular tudo de uma vez, criei uma coluna por passo, e cada uma pode ser conferida separadamente.

**Exemplo para acompanhar:** a venda 1004 foi feita pela Ana Ribeiro junto com a Camila Duarte. O pagamento (baixa 50006) gerou R$ 773,15 de comissão, que foi dividido: R$ 463,89 para a Ana (60%) e R$ 309,26 para a Camila (40%).

| Regra | O que a regra diz | Como configurei |
|---|---|---|
| **R1** Comissão de projetos | O valor pago é dividido entre os itens, na proporção do valor de cada um. Sobre a parte de cada item aplica-se o percentual da tabela, reduzido pelo desconto da venda. | Coluna `peso_item` (quanto cada item pesa na venda), `base_item` (a parte do pagamento de cada item) e `redutor` (1, 0,8, 0,6 ou 0,4 conforme o desconto: até 5%, até 10%, até 15% e acima disso). |
| **R2** Assinaturas | Paga 50% da **primeira** mensalidade, sem redutor de desconto. | A mesma coluna de comissão do item olha o tipo da venda. Se for assinatura, só a parcela 1 gera comissão, usando os 50% da tabela. |
| **R3** Venda conjunta | Quando há dois vendedores, divide 60% e 40%. | Coluna `comissao_vendedor2` (40%) e `comissao_vendedor1` (o que sobra, 60%). A soma sempre fecha com o total. |
| **R4** Cancelamento | Cancelada em até 60 dias da venda: nada é pago. Cancelada depois de 60 dias: só valem os pagamentos feitos até a data do cancelamento. | Coluna `dias_cancel` (quantos dias entre a venda e o cancelamento) e `comissionavel` (1 = conta, 0 = não conta). |
| **R7** Override do gerente | O gerente ganha 1% do valor pago das vendas feitas por vendedores da equipe dele. | Coluna `override_item` (1% da parte do pagamento) e a coluna `gerente`, trazida do cadastro. |

Para conferir cada coluna, comparei algumas linhas com o Python. Por exemplo, na venda 1004 a soma das partes da Ana e da Camila fecha exatamente com os R$ 773,15.

### Mês de cada pagamento
A coluna `competencia` pega o mês da data de pagamento (agosto de 2026 vira 202608). É ela que garante o regime de caixa.

## 6. Meta, bônus e rampagem

### Bônus de meta (R5)
**A regra:** cada consultor tem uma meta mensal (entre R$ 60 mil e R$ 150 mil). O bônus depende de quanto da meta foi atingido: abaixo de 80% nada; de 80% a menos de 100%, R$ 800; de 100% a menos de 120%, R$ 1.500; a partir de 120%, R$ 2.500. O mês que vale é o da **venda**, e só entram projetos não cancelados. Em venda conjunta, vale o 60/40.

**O problema:** a meta da plataforma é **uma só para todo mundo**, mas a meta de cada consultor é diferente.

**A solução:** em vez de comparar o valor vendido com metas diferentes, dividi o valor de cada linha pela meta **da própria pessoa**. Assim, a soma das linhas de alguém é o percentual da meta que ele atingiu. Por exemplo, quem vende R$ 60 mil com meta de R$ 120 mil fica em 0,50, ou seja, 50%. Com isso, a meta da plataforma passou a ser a mesma para todos (o valor **100**, que representa 100%).

Para somar a parte como vendedor principal e a parte como segundo vendedor da mesma pessoa, montei uma tabela que junta os dois papéis (`meta_base`, com 178 linhas: 89 do vendedor principal e 89 do segundo vendedor).

### Rampagem (R6)
**A regra:** consultores nos 3 primeiros meses de casa (o mês da admissão conta como o 1º) têm uma garantia mínima de R$ 1.500 por mês, somando só as comissões de venda (R1 e R2, depois do split 60/40). Se ganharem menos, a empresa paga a diferença. **O bônus de meta não entra nessa conta.**

**Como configurei:** a plataforma tem um recurso chamado **Mínimo Garantido**, que faz exatamente isso. Criei um plano separado, o **Rampagem**, só com quem está nos 3 primeiros meses (Diego e Érica), e ativei o mínimo de R$ 1.500 selecionando apenas os componentes de comissão. O bônus de meta fica no mesmo plano, mas **fora** da conta do mínimo.

- **Diego** (admitido em 20/07): garantia em julho, agosto e setembro. Em agosto ganhou R$ 690,46 de comissão e recebeu o complemento de **R$ 809,54**.
- **Érica** (admitida em 03/08): garantia em agosto, setembro e outubro. Em setembro ganhou R$ 190,16 e o complemento é de **R$ 1.309,84**.

> No começo eu tinha resolvido a rampagem com um arquivo de apoio calculado em Python, porque os tipos de ganho comuns (comissão, faixas, bônus) não sabem fazer "1.500 menos o total do mês". Depois, com a orientação do time da RevTrack, descobri o Mínimo Garantido e passei a regra para dentro da plataforma. O arquivo foi descartado.

## 7. Planos e componentes

### Plano `Solarix - Comissões 2026`
**Quem participa:** Ana Ribeiro, Bruno Sato, Camila Duarte, João Pedro Almeida (consultores) e Marcos Teles e Paula Nogueira (gerentes).

| Componente | Quem recebe | O que paga |
|---|---|---|
| Comissão – vendedor principal | O vendedor principal da venda | A comissão dele (R1, R2, R3 e R4) |
| Comissão – vendedor 2 | O segundo vendedor | A parte de 40% (só existe em venda conjunta) |
| Override de gerência (1%) | O gerente da equipe | 1% do valor pago (R7) |
| Bônus de meta | O consultor | O bônus pelo atingimento da meta (R5) |

Nos componentes de comissão e override, a coluna já traz o valor final de cada linha, e a plataforma só repassa esse valor (taxa de 100%).

### Plano `Rampagem`
**Quem participa:** só Diego Ferraz e Érica Lins.
**Componentes:** os mesmos de comissão (principal e vendedor 2) e o bônus de meta, com o **Mínimo Garantido** de R$ 1.500 sobre os dois de comissão.

**Por que Diego e Érica não ficam no plano principal:** o Mínimo Garantido vale para todos os que estão no plano, e a regra só vale nos 3 primeiros meses. Então quem está na rampagem fica no plano próprio. Quando acabam os 3 meses, a pessoa passa para o plano principal (essa troca é manual).

## 8. Como conferi se está certo

### Contra o Python (as 7 regras, agosto + setembro)

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

**Por que a diferença de centavos?** A plataforma arredonda o valor de cada item, e o Python arredonda o valor de cada pagamento. Dá uma diferença de 1 a 15 centavos por pessoa, bem abaixo da tolerância de R$ 1,00 do briefing.

### Contra o controle da Carla
- **13 das 16 linhas batem.** Bônus de meta e override batem nas 16.
- As 3 que não batem:
  - **Érica, setembro:** o controle não tem o complemento de rampagem de **R$ 1.309,84**. O total dela no controle é R$ 190,16 de comissão mais R$ 2.500 de bônus, o que sugere que o bônus entrou na conta da garantia. Pela regra, o bônus não conta.
  - **Bruno, setembro:** o controle da Carla tem R$ 638,03 a mais de comissão. Não consegui explicar.
  - **Camila, agosto:** o controle tem R$ 184,00 a mais de comissão. O valor redondo sugere um ajuste manual.
- Os dois últimos já viraram perguntas na mensagem para a Carla (`docs/mensagem_carla.md`).

## 9. Decisões que tomei (hipóteses)

Quando o briefing deixou dúvidas, escolhi um caminho e registrei. A lista completa está em `docs/decisoes.md`.

**Já confirmadas:**
- **D1:** os pagamentos de 26 a 30/09 entram no cálculo, mesmo o relatório sendo "emitido em 25/09". O controle da Carla também os inclui.
- **D2:** a instalação da venda 1006 (canal PARCEIRO) tem 0% de comissão, mas continua entrando na divisão do pagamento entre os itens. Se fosse retirada da divisão, o Bruno ganharia R$ 69,22 a mais em setembro.
- **D3:** os limites de desconto de 5%, 10% e 15% estão **incluídos** na faixa de baixo. Por exemplo, exatamente 10% de desconto fica na faixa de "até 10%".

**Ainda aguardam confirmação (D4 a D8):** o override é sobre 100% do valor pago, mesmo em venda conjunta; o arredondamento é por item; os 60 dias contam como "data do cancelamento menos data da venda"; a rampagem é sobre R1 e R2 depois do split, sem o bônus; e o bônus de meta usa a meta cheia, sem proporcionalidade.

**Outras:**
- Em parcela paga pela metade (venda 1031), comissiona-se só o que foi pago.
- Venda conjunta conta 60/40 também para a meta.

## 10. Limitações (o que não ficou perfeito)

1. **O cartão "Vendas Totais" do relatório não é o faturamento.** Ele soma o campo "Base de vendas" de todos os componentes. Como as nossas colunas já entregam a comissão pronta, esse campo carrega a **comissão** (e, no bônus, a fração da meta), e não o valor vendido. Hoje o cartão mostra R$ 42.203,27, que é exatamente 31.889,72 de comissões + 10.301,34 de override + 12,23 de bônus. **Isso não afeta nenhum valor de comissão, bônus, rampagem ou override.** O faturamento real do período está na planilha de fechamento: R$ 1,03 milhão pago e R$ 1,13 milhão vendido.
   - **Por que acho que aconteceu:** a plataforma parece usar o mesmo campo como base da taxa e como valor de vendas nos relatórios.
   - **Como corrigir, depois da apresentação:** trocar a base dos componentes de comissão pelo valor pago de cada parte (`venda_principal` e `venda_vendedor2`) e ler o percentual de uma coluna por linha (`taxa_comissao`, com a opção "Comissão pré definida (Tabelada)"). Filtrando o relatório por esses dois componentes, o cartão mostraria R$ 1.034.449,90. Sem filtro, o override e o bônus ainda somariam cerca de R$ 10,3 mil por cima. Para fazer com segurança: criar os componentes novos ao lado dos antigos, desativar os antigos, recalcular e conferir se o total continua em R$ 58.710,44.
2. **A última faixa do bônus termina em 999%.** A plataforma exige um limite superior em todas as faixas, então usei 999 como "sem limite". O maior atingimento real foi 233,73% (Érica, em setembro).
3. **A meta da plataforma tem o valor 100 para todos.** É o contorno explicado na seção 6: a meta real de cada pessoa entra na coluna que calcula a base do bônus.
4. **A troca de plano no fim da rampagem é manual.** A plataforma não faz sozinha.
5. **Pessoa sem nenhuma comissão no mês.** Não testei como o Mínimo Garantido se comporta se alguém na rampagem não tiver nenhuma linha de comissão no mês. Nos dados de agosto e setembro isso não acontece.
6. **O PROCV só funciona em arquivos originais.** Por isso o cadastro foi trazido por join nas tabelas calculadas, e não por busca.

## 11. O que ainda falta

- **Respostas da Carla** (`docs/mensagem_carla.md`): Érica, Bruno, Camila e mais 5 itens de confirmação (pagamentos depois da emissão, pagamentos depois do cancelamento, instalação da venda 1006, parcela pela metade da venda 1031 e vendas sem pagamento). Qualquer resposta que mude os dados exige recalcular.
- **Confirmar as decisões D4 a D8.**
- **Corrigir o cartão "Vendas Totais"** (limitação 1).
- **Testar o Mínimo Garantido** com uma pessoa sem comissão no mês.

## 12. Como recalcular quando algo mudar

1. Se os dados mudaram, atualize as fontes em **Integrações** (clique em sincronizar).
2. Vá em **Cálculos → Por Período**, coloque as datas (por exemplo, 01/08/2026 a 30/09/2026) e clique em **Corrigir Período**. Espere aparecer "Concluído" no histórico.
3. Se mudou uma coluna calculada, um componente ou os membros de um plano, use também **Reprocessar Tudo** uma vez.
4. Abra **Relatórios**, filtre o período e compare com a planilha `outputs/fechamento_solarix.xlsx`.

## Anexo: as fórmulas, para quem quiser conferir

**No conjunto `baixa_item_pct`:**

| Coluna | Fórmula |
|---|---|
| `peso_item` | `{valor_bruto} / {total_bruto}` |
| `competencia` | `YEAR({data_pagamento}) * 100 + MONTH({data_pagamento})` |
| `redutor` | `IF({tipo} = "ASSINATURA", 1, CASE WHEN {desconto_pct} <= 5 THEN 1 WHEN {desconto_pct} <= 10 THEN 0.8 WHEN {desconto_pct} <= 15 THEN 0.6 ELSE 0.4 END)` |
| `base_item` | `{valor_pago} * {peso_item}` |
| `dias_cancel` | `DATEDIFF({data_cancelamento}, {data_venda})` |
| `comissionavel` | `IF({status} = "ATIVA", 1, IF({dias_cancel} <= 60, 0, IF({data_pagamento} > {data_cancelamento}, 0, 1)))` |
| `comissao_item` | `IF({comissionavel} = 0, 0, IF({tipo} = "ASSINATURA", IF({parcela} = 1, ROUND({base_item} * {pct_comissao} / 100, 2), 0), ROUND({base_item} * {pct_comissao} / 100 * {redutor}, 2)))` |
| `comissao_vendedor2` | `IF(COALESCE({vendedor2}, "") = "", 0, ROUND({comissao_item} * 0.4, 2))` |
| `comissao_vendedor1` | `{comissao_item} - {comissao_vendedor2}` |

**No conjunto `baixa_item_gerente`:**

| Coluna | Fórmula |
|---|---|
| `override_item` | `IF({comissionavel} = 0, 0, IF({tipo} = "ASSINATURA", IF({parcela} = 1, ROUND({base_item} * 0.01, 2), 0), ROUND({base_item} * 0.01, 2)))` |

**Nos conjuntos `meta_principal` e `meta_vendedor2`:**

| Coluna | Fórmula |
|---|---|
| `pessoa` | `{vendedor}` (principal) ou `{vendedor2}` (segundo vendedor) |
| `base_meta` (principal) | `IF({tipo} = "PROJETO" AND {status} = "ATIVA", {valor_bruto} * (1 - {desconto_pct} / 100) * IF(COALESCE({vendedor2}, "") = "", 1, 0.6) / {meta_mensal}, 0)` |
| `base_meta` (vendedor 2) | `IF({tipo} = "PROJETO" AND {status} = "ATIVA" AND COALESCE({vendedor2}, "") != "", {valor_bruto} * (1 - {desconto_pct} / 100) * 0.4 / {meta_mensal}, 0)` |

**Meta:** `Meta mensal de vendas`, tipo Número, recorrente, mensal, "altera ao longo do tempo", com **100** em agosto e em setembro. **Faixas do bônus:** 0 a 80% = R$ 0; 80 a 100% = R$ 800; 100 a 120% = R$ 1.500; 120 a 999% = R$ 2.500 ("Alcance %" sobre a soma total dos negócios).
