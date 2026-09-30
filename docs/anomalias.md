# Log de anomalias dos dados

Gerado por `python -m solarix.reports.anomalias`. Cada item indica o que foi encontrado, o tratamento proposto e o que perguntar à Carla.

| ID | Sev. | Fonte | Título |
|---|---|---|---|
| B01 | ALTA | 03_ERP_Baixas | Baixas com data posterior à emissão do relatório |
| T01 | ALTA | 04_Tabela x 01/02 | Item sem % na tabela de comissão |
| A01 | MEDIA | 01_CRM_Vendas | Nome divergente em 'vendedor' |
| B02 | MEDIA | 03_ERP_Baixas | Nº de baixa fora da sequência |
| B03 | MEDIA | 03_ERP_Baixas | Pagamentos posteriores ao cancelamento da venda |
| B05 | MEDIA | 03_ERP_Baixas | Parcela paga a menor (saldo em aberto) |
| T02 | MEDIA | 04_Tabela x briefing | Monitoramento aparece como 50% na tabela e em R2 |
| B06 | BAIXA | 01 x 03 | Vendas sem nenhuma baixa no ERP |
| B04 | INFO | 03_ERP_Baixas | Parcelas pagas em mais de uma baixa |
| C01 | INFO | 05_Cadastro | Gerentes sem meta e sem vendas |
| C02 | INFO | 05_Cadastro | Consultores em rampagem (R6) |
| V03 | INFO | 01_CRM_Vendas | Vendas canceladas (R4) |
| V04 | INFO | 01_CRM_Vendas | Descontos exatamente nos limites das faixas (5/10/15%) |
| V05 | INFO | 01_CRM_Vendas | Vendas conjuntas |

## B01 — Baixas com data posterior à emissão do relatório
**Severidade:** ALTA · **Fonte:** 03_ERP_Baixas

**O que encontrei:** Relatório 'emitido em 25/09/2026', mas 7 baixas têm pagamento de 26 a 30/09 (soma R$ 60,308.08). Afeta só a competência set/2026.

**Tratamento proposto:** Mantidas no cálculo (cenário base); impacto isolado no fechamento.

**Pergunta para a Carla:** Essas baixas são previstas/agendadas ou realizadas? A data de emissão está correta?

**Chaves afetadas:** 50051, 50066, 50083, 50030, 50075, 50018, 50099

## T01 — Item sem % na tabela de comissão
**Severidade:** ALTA · **Fonte:** 04_Tabela x 01/02

**O que encontrei:** item 1006-2 (INSTALACAO / PARCEIRO, R$ 5,538.16, Bruno Sato). Observação da tabela: 'No canal PARCEIRO a instalação é feita pelo parceiro'.

**Tratamento proposto:** Item comissionado a 0%, mas mantido no denominador do rateio (R1 rateia pelo bruto de todos os itens).

**Pergunta para a Carla:** Instalação em venda PARCEIRO não gera comissão? O item deve entrar no rateio?

**Chaves afetadas:** 1006

## A01 — Nome divergente em 'vendedor'
**Severidade:** MEDIA · **Fonte:** 01_CRM_Vendas

**O que encontrei:** 10 linhas com grafia diferente do cadastro (acento/espaço): {"'Joao Pedro Almeida'": 5, "'João Pedro Almeida '": 5}

**Tratamento proposto:** Normalizado para o nome do cadastro (chave sem acento, minúscula, sem espaços nas pontas).

**Chaves afetadas:** 1012, 1015, 1027, 1031, 1036, 1039, 1048, 1049, 1057, 1060

## B02 — Nº de baixa fora da sequência
**Severidade:** MEDIA · **Fonte:** 03_ERP_Baixas

**O que encontrei:** Baixa 59001 (1013-P05, 22/09/2026, R$ 6,241.01) foge da numeração 50001–50115; a venda foi cancelada em 15/09/2026, antes do pagamento.

**Tratamento proposto:** Mantida no dado; a regra R4 exclui por ser posterior ao cancelamento.

**Pergunta para a Carla:** Por que houve pagamento após o cancelamento? Foi estornado ou é um lançamento manual?

**Chaves afetadas:** 59001

## B03 — Pagamentos posteriores ao cancelamento da venda
**Severidade:** MEDIA · **Fonte:** 03_ERP_Baixas

**O que encontrei:** 1 baixa(s) de venda cancelada com data depois do cancelamento: 1011-P03 em 30/09/2026 (cancel. 25/08/2026)

**Tratamento proposto:** R4: cancelamento em até 60 dias zera tudo; depois de 60 dias só contam baixas até a data do cancelamento.

**Pergunta para a Carla:** Confirmar se esses valores foram devolvidos ao cliente.

**Chaves afetadas:** 50018

## B05 — Parcela paga a menor (saldo em aberto)
**Severidade:** MEDIA · **Fonte:** 03_ERP_Baixas

**O que encontrei:** 1031-P03: pago R$ 6,528.32 de R$ 13,056.63

**Tratamento proposto:** Comissão sobre o valor efetivamente pago (R1).

**Pergunta para a Carla:** Confirmar que o saldo segue em aberto e não é perdão de dívida.

**Chaves afetadas:** 1031

## T02 — Monitoramento aparece como 50% na tabela e em R2
**Severidade:** MEDIA · **Fonte:** 04_Tabela x briefing

**O que encontrei:** A tabela tem 3 linhas de MONITORAMENTO a 50% ('somente sobre a 1ª mensalidade paga') e a regra R2 diz o mesmo. Risco de aplicar duas vezes.

**Tratamento proposto:** Aplicar 50% uma única vez, só na parcela 1; R1 (rateio/redutor) fica restrito a PROJETO.

## B06 — Vendas sem nenhuma baixa no ERP
**Severidade:** BAIXA · **Fonte:** 01 x 03

**O que encontrei:** 1010 (PROJETO, 20/08/2026); 1016 (PROJETO, 08/06/2026); 1032 (PROJETO, 24/09/2026); 1033 (PROJETO, 28/09/2026); 1048 (ASSINATURA, 19/09/2026); 1053 (ASSINATURA, 15/09/2026)

**Tratamento proposto:** Sem baixa não há comissão de caixa; PROJETOS entram na meta (R5).

**Pergunta para a Carla:** Confirmar que são vendas ainda sem recebimento. Atenção às antigas: 1010 (20/08), 1016 (08/06) estão há mais de 30 dias sem nenhuma baixa.

**Chaves afetadas:** 1010, 1016, 1032, 1033, 1048, 1053

## B04 — Parcelas pagas em mais de uma baixa
**Severidade:** INFO · **Fonte:** 03_ERP_Baixas

**O que encontrei:** 7 parcelas com 2+ baixas: 1002-P01, 1008-P01, 1020-P01, 1024-P03, 1025-P02, 1026-P02, 1026-P03. As baixas de uma mesma parcela podem cair em meses diferentes.

**Tratamento proposto:** Cada baixa é comissionada na competência da própria data de pagamento (regime de caixa).

**Chaves afetadas:** 1002, 1008, 1020, 1024, 1025, 1026

## C01 — Gerentes sem meta e sem vendas
**Severidade:** INFO · **Fonte:** 05_Cadastro

**O que encontrei:** Marcos Teles, Paula Nogueira não têm meta e não aparecem como vendedores; recebem só override (R7).

**Tratamento proposto:** Tratados como gerentes puros.

## C02 — Consultores em rampagem (R6)
**Severidade:** INFO · **Fonte:** 05_Cadastro

**O que encontrei:** Diego Ferraz (admissão 20/07/2026); Érica Lins (admissão 03/08/2026). Mês de admissão = 1º mês: Diego = jul, ago, set; Érica = ago, set, out.

**Tratamento proposto:** Ambos elegíveis em ago e set/2026.

## V03 — Vendas canceladas (R4)
**Severidade:** INFO · **Fonte:** 01_CRM_Vendas

**O que encontrei:** 1011: venda 10/07, cancelada 25/08 = 46 dias -> até 60 dias: zera tudo; 1013: venda 05/06, cancelada 15/09 = 102 dias -> após 60 dias: vale até a data do cancelamento

**Tratamento proposto:** Aplicado conforme R4 (dias = cancelamento − venda; ≤ 60 zera).

**Chaves afetadas:** 1011, 1013

## V04 — Descontos exatamente nos limites das faixas (5/10/15%)
**Severidade:** INFO · **Fonte:** 01_CRM_Vendas

**O que encontrei:** 13 projetos: 5% = 7, 10% = 4, 15% = 2.

**Tratamento proposto:** Limite superior inclusivo (5% => 100%; 10% => 80%; 15% => 60%), como no texto 'até 5% (inclusive)'.

**Pergunta para a Carla:** Confirmar que 10% e 15% também são inclusivos.

**Chaves afetadas:** 1004, 1008, 1012, 1014, 1017, 1022, 1024, 1025, 1029, 1030, 1033, 1036, 1040

## V05 — Vendas conjuntas
**Severidade:** INFO · **Fonte:** 01_CRM_Vendas

**O que encontrei:** 1004: Ana Ribeiro + Camila Duarte; 1010: Ana Ribeiro + Bruno Sato; 1013: Bruno Sato + João Pedro Almeida; 1042: Camila Duarte + Ana Ribeiro

**Tratamento proposto:** Split 60/40 (R3), incluindo meta (R5). Override (R7) usa só a equipe do vendedor principal.

**Chaves afetadas:** 1004, 1010, 1013, 1042
