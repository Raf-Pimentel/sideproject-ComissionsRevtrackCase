# Log de decisões e hipóteses

Status: **Confirmada** (decidida pelo Rafael) · **Padrão** (assumida pelo Claude, aguardando confirmação) · **Evidência** = o que o controle da Carla mostrou.

| ID | Tema | Decisão | Status | Evidência / impacto |
| -- | ---- | ------- | ------ | ------------------- |
| D1 | Baixas de 26 a 30/09 (relatório "emitido em 25/09") | Entram no cálculo | **Confirmada** | Sem elas, João Pedro (-R$ 821), Paula (-R$ 329) e Marcos (-R$ 28) deixam de bater com a Carla: ela também as incluiu. Valor: 7 baixas, R$ 60.308,08, só em set. A dúvida sobre a origem dessas datas vai para a Carla (Q1). Chave: `INCLUIR_BAIXAS_APOS_EMISSAO`. |
| D2 | Item sem % na tabela (instalação da venda 1006, canal PARCEIRO) | 0% no item, mantido no rateio (Opção A) | **Confirmada** (segue como pergunta Q3) | A Opção B (tirar do rateio) daria +R$ 69,22 ao Bruno em set. O controle não distingue A de B. Chave: `ITEM_SEM_PCT_ENTRA_NO_RATEIO`. |
| D3 | Limites de desconto (5/10/15%) | Limite superior inclusivo | **Confirmada** | O texto do briefing ("acima de 5% até 10%", "acima de 10% até 15%") já inclui 10% e 15% nas faixas de 80% e 60%. Testei todas as variações "exclusivas": qualquer uma piora de 13/16 para no máximo 12/16. Confirmado pelo Rafael: não vai para a Carla. |
| D4 | Override em venda conjunta | 1% sobre 100% do valor pago, equipe do vendedor principal | Padrão | Override bate em 16/16 linhas. |
| D5 | Arredondamento | Por item (R1), meio para cima, 2 casas | Padrão | Diferenças de R$ 0,01 em Ana (set) e Bruno (ago), dentro da tolerância. |
| D6 | Contagem dos 60 dias (R4) | cancelamento − venda ≤ 60 zera tudo | Padrão | Bate. Casos do dado (46 e 102 dias) não ficam perto do limite. |
| D7 | Rampagem | Complemento = 1.500 − (R1+R2 pós-split), meses 1 a 3 com o mês da admissão contando | Padrão | Diego bate. Érica set: ver P1. |
| D8 | Bônus de meta | Meta cheia, sem proporcionalidade; só PROJETO não cancelado | Padrão | Bônus bate em 16/16 linhas. |

## Divergências com o controle da Carla

| ID | Linha | Diferença (nosso − Carla) | Leitura |
| -- | ----- | ------------------------- | ------- |
| P1 | Érica Lins, set/2026 | Rampagem +R$ 1.309,84 | **Confirmado pelo Rafael: a Carla esqueceu de pagar.** Comissão de set = R$ 190,16 e a Érica está no 2º mês de casa (admitida 03/08/2026), então a R6 garante R$ 1.500,00 e o complemento é R$ 1.500,00 − R$ 190,16 = R$ 1.309,84. **Vai na mensagem à Carla como ponto a informar (I1).** |
| P2 | Bruno Sato, set/2026 | Comissão −R$ 638,03 (Carla acima) | **Não explicada.** O override dos gerentes bate, então o conjunto de baixas é o mesmo. Testei: variações de faixa de desconto, split, baixas de outros meses ou pós-cancelamento, monitoramento parcela 2+, Opção B da D2. Nenhuma fecha. Abordagem escolhida pelo Rafael: registrar como pergunta (Q4). |
| P3 | Camila Duarte, ago/2026 | Comissão −R$ 184,00 (Carla acima) | **Não explicada.** Mesmo teste do P2, sem resultado. O valor redondo sugere ajuste manual. Abordagem escolhida pelo Rafael: registrar como pergunta (Q5). |
