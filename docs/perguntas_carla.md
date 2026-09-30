# Perguntas e pontos para a Carla

Lista consolidada que alimenta a mensagem de fechamento (entregável 3). Revisada pelo Rafael.

## Pontos a informar (não são perguntas)

**I1. Rampagem da Érica Lins em setembro/2026.** O controle não tem complemento de rampagem para a Érica em setembro. Ela foi admitida em 03/08/2026, então setembro é o 2º mês de casa (o mês da admissão conta como o 1º), e a regra R6 garante R$ 1.500,00 por mês na soma das comissões de venda. A comissão de setembro foi R$ 190,16, então o complemento devido é R$ 1.500,00 − R$ 190,16 = **R$ 1.309,84**. Confirmado pelo Rafael como esquecimento no controle.

**I2. Parcela da venda 1031 paga pela metade.** A venda 1031 (Residência Vasconcelos, vendedor João Pedro Almeida) tem 3 parcelas de R$ 13.056,63:

| Parcela | Valor da parcela | Valor pago | Data |
|---|---|---|---|
| P01 | R$ 13.056,63 | R$ 13.056,63 | 17/07 |
| P02 | R$ 13.056,63 | R$ 13.056,63 | 17/08 |
| P03 | R$ 13.056,63 | **R$ 6.528,32** (50%) | 26/09 |

Na 3ª parcela faltam R$ 6.528,31. **Decisão:** comissionamos só o que foi efetivamente pago, como manda o regime de caixa: R$ 6.528,32 × 2,5% = **R$ 163,21** para o João Pedro em setembro. Se o saldo for pago depois, ele gerará mais R$ 163,21 de comissão no mês do pagamento. Se for dado como quitado (perdão), não haverá comissão sobre ele.

## Perguntas

### Q1. Pagamentos com data depois da emissão do relatório
O relatório do ERP diz "Emitido em 25/09/2026", mas 7 baixas têm data de pagamento entre 26 e 30/09, somando R$ 60.308,08:

| Baixa | Parcela | Valor pago | Data |
|---|---|---|---|
| 50051 | 1025-P02 | R$ 2.847,75 | 26/09 |
| 50066 | 1031-P03 | R$ 6.528,32 | 26/09 |
| 50083 | 1043-P03 | R$ 4.934,56 | 26/09 |
| 50030 | 1015-P02 | R$ 10.981,23 | 27/09 |
| 50075 | 1039-P02 | R$ 10.411,47 | 27/09 |
| 50018 | 1011-P03 | R$ 24.154,85 | 30/09 |
| 50099 | 1054-P02 | R$ 449,90 | 30/09 |

Um relatório emitido em 25/09 não deveria ter pagamentos de datas posteriores. Esses pagamentos já aconteceram ou são previstos/agendados? A data de emissão está correta?
**O que fizemos:** incluímos esses valores no cálculo de setembro, porque o seu controle também os inclui. Se forem só previstos, o fechamento de setembro muda.

### Q2. Pagamentos depois do cancelamento da venda
- **Venda 1013** (Residência Moura): cancelada em 15/09/2026, mas há um pagamento de R$ 6.241,01 em 22/09 (baixa 59001). Essa baixa também foge da numeração do ERP (as demais vão de 50001 a 50115).
- **Venda 1011** (Residência Oliveira): cancelada em 25/08/2026, mas há um pagamento de R$ 24.154,85 em 30/09 (baixa 50018).

Esses valores foram devolvidos ao cliente ou foram lançados manualmente por algum motivo?
**O que fizemos:** pela regra R4, esses pagamentos não geram comissão nem override.

### Q3. Instalação da venda 1006 (canal PARCEIRO)
A venda 1006 (Fazenda Santa Luzia, vendedor Bruno Sato, canal PARCEIRO, sem desconto) tem dois itens:

| Item | Valor bruto | % na tabela de comissão |
|---|---|---|
| Kit residencial | R$ 31.055,67 | 2,5% (KIT_RESIDENCIAL / PARCEIRO) |
| Instalação | R$ 5.538,16 | **não existe linha** (a tabela só tem instalação para DIRETO e INDICAÇÃO) |

A observação da própria tabela diz: "No canal PARCEIRO a instalação é feita pelo parceiro". O pagamento de setembro foi de **R$ 18.296,91** (parcela 2, em 05/09). Pela regra R1, o pagamento é dividido entre os itens na proporção do valor bruto de cada um. Há duas formas de tratar a instalação, e elas dão resultados diferentes:

**Opção A (a que usamos): a instalação entra na divisão, mas com 0% de comissão.**
- Soma dos itens: R$ 31.055,67 + R$ 5.538,16 = R$ 36.593,83
- Parte do kit: 31.055,67 ÷ 36.593,83 = 84,87% → R$ 18.296,91 × 84,87% = R$ 15.527,83
- Parte da instalação: 5.538,16 ÷ 36.593,83 = 15,13% → R$ 18.296,91 × 15,13% = R$ 2.769,08 (comissão 0%)
- Comissão: R$ 15.527,83 × 2,5% = **R$ 388,20**

**Opção B: a instalação sai da divisão (todo o pagamento é do kit).**
- Comissão: R$ 18.296,91 × 2,5% = **R$ 457,42**

A diferença é de **R$ 69,22** a mais para o Bruno na Opção B, em setembro. Qual dos dois é o correto para a Solarix?

### Q4. Bruno Sato, setembro/2026
O seu controle tem comissão sobre vendas de **R$ 3.153,94** e o nosso cálculo dá **R$ 2.515,91**, uma diferença de **R$ 638,03**. O bônus de meta bate e os overrides dos gerentes também, o que indica que estamos considerando os mesmos pagamentos. Você consegue enviar a conta por venda do Bruno em setembro (qual pagamento, qual percentual, qual valor de comissão)?

### Q5. Camila Duarte, agosto/2026
O seu controle tem comissão sobre vendas de **R$ 3.896,46** e o nosso cálculo dá **R$ 3.712,46**, uma diferença de **R$ 184,00** (valor redondo). Houve algum ajuste manual? Pode enviar a conta por venda da Camila em agosto?

### Q6. Vendas sem nenhum pagamento
As vendas **1016** (Residência Tavares, 08/06, Ana Ribeiro) e **1010** (Laticínios Serra Azul, 20/08, Ana Ribeiro e Bruno Sato) não têm nenhuma baixa no ERP. Isso é esperado (cliente ainda não pagou), ou falta algum lançamento?

## Origem
I2 e Q1 a Q3 e Q6 vêm das anomalias dos dados (`outputs/conferencia_anomalias.xlsx`). Q4 e Q5 vêm da comparação com o controle (`docs/decisoes.md`, P2 e P3).
