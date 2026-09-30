# Case RevTrack — Solarix Energia

**Para:** Rafael Melo  **De:** Lars Kunath (RevTrack)
**Entrega:** segunda-feira, 28/09, até 12h  **Conversa de devolutiva:** segunda à tarde (45 min)

---

## O cenário

Você acabou de assumir como Head de CS & Operações da RevTrack. A Solarix Energia, integradora de energia solar de Campinas, fechou contrato semana passada. O kickoff já aconteceu e a Carla (controller da Solarix) mandou tudo o que a gente pediu: exports do CRM e do ERP, a tabela de comissão, o cadastro do time e o controle que ela faz hoje à mão.

A partir daqui a bola está com você. O objetivo é deixar a conta configurada e calculando agosto e setembro de 2026, validar contra o controle da Carla e voltar para ela com um fechamento que ela possa confiar.

Na RevTrack não existe comissão "quase certa": ou bate na vírgula, ou a gente precisa saber exatamente por que não bate.

## Acesso

Você vai receber login da nossa conta demo. Pode criar fontes de dados, conjuntos, colunas calculadas, planos, componentes e membros à vontade. Uma regra: ao cadastrar membros, deixe **desmarcado** o envio de convite por e-mail (use os e-mails fictícios do cadastro).

## Arquivos

| Arquivo                       | O que é                                                                                          |
| ----------------------------- | ------------------------------------------------------------------------------------------------- |
| 01_CRM_Vendas                 | Cabeçalho das vendas (projetos e assinaturas), vendedor, venda conjunta, canal, desconto, status |
| 02_CRM_Itens_da_Venda         | Itens de cada venda, com linha de produto e valor bruto                                           |
| 03_ERP_Relatorio_de_Baixas    | Recebimentos (baixas) exportados do ERP, de jun a set                                             |
| 04_Tabela_de_Comissao         | % de comissão por linha de produto × canal                                                      |
| 05_Cadastro_Comissionados     | Time comercial: cargo, equipe, gerente, admissão, meta mensal                                    |
| 06_Controle_Comissoes_Cliente | O controle manual da Carla para ago e set                                                         |

Os arquivos vieram do jeito que o cliente exporta. Trate como dado real de cliente.

## Regras de comissão da Solarix

Tudo é pago em **regime de caixa**: a competência da comissão é o mês da data de pagamento da baixa. Calcule as competências **agosto/2026** e **setembro/2026**.

**R1. Comissão de projetos.** Para cada baixa de uma venda do tipo PROJETO, o valor pago é rateado entre os itens da venda na proporção do valor bruto de cada item. Sobre a parte de cada item aplica-se o % da tabela (linha de produto × canal da venda). Esse % é reduzido conforme o desconto concedido na venda:

| Desconto da venda     | % aplicado                   |
| --------------------- | ---------------------------- |
| até 5% (inclusive)   | 100% do percentual da tabela |
| acima de 5% até 10%  | 80%                          |
| acima de 10% até 15% | 60%                          |
| acima de 15%          | 40%                          |

**R2. Assinaturas de monitoramento.** Paga 50% do valor pago da **1ª mensalidade**. As demais mensalidades não geram comissão. Não há redutor de desconto.

**R3. Venda conjunta.** Quando existe "Vendedor 2", a comissão (R1 e R2) é dividida 60% para o vendedor principal e 40% para o vendedor 2. A mesma divisão vale para a meta (R5).

**R4. Cancelamentos.** Venda cancelada até 60 dias corridos após a data da venda: nenhuma comissão nem override, mesmo sobre baixas já recebidas. Venda cancelada depois de 60 dias: as baixas com data de pagamento até a data de cancelamento (inclusive) continuam comissionáveis; as posteriores não.

**R5. Bônus de meta mensal (consultores).** A competência aqui é o mês da **data da venda** (não do pagamento). Soma-se o valor líquido (itens × (1 − desconto)) dos PROJETOS não cancelados, com vendas conjuntas divididas 60/40, e compara-se com a meta mensal do cadastro:

| Atingimento          | Bônus   |
| -------------------- | -------- |
| abaixo de 80%        | R$ 0     |
| 80% a menos de 100%  | R$ 800   |
| 100% a menos de 120% | R$ 1.500 |
| 120% ou mais         | R$ 2.500 |

**R6. Rampagem.** Consultores nos 3 primeiros meses-calendário de casa (o mês da admissão conta como o 1º) têm garantia mínima de R$ 1.500 por mês na soma de R1 + R2 (já depois do split). Se a comissão do mês ficar abaixo disso, paga-se um complemento igual à diferença. O bônus de meta não entra nessa conta.

**R7. Override de gerência.** Cada gerente recebe 1% do valor pago das baixas comissionáveis (as que geram comissão por R1 ou R2, respeitando R4) das vendas cujo vendedor principal é da sua equipe.

## O que entregar

1. **A conta configurada e calculada** para ago e set/2026: fontes de dados, conjuntos (joins), colunas calculadas, planos, componentes e membros. Quero conseguir abrir o relatório de comissões e ver o resultado por comissionado.
2. **Uma tabela de fechamento** (planilha) com, para cada comissionado e cada mês: comissão sobre vendas, bônus de meta, complemento de rampagem, override e total, lado a lado com o controle da Carla e a diferença.
3. **A mensagem que você mandaria para a Carla** (e-mail ou WhatsApp) apresentando o fechamento: onde bateu, onde não bateu e por quê, e o que você precisa que ela confirme. Escreva como se ela fosse ler de verdade.
4. **Uma página de "como configurei"**: a arquitetura da conta (quais bases, quais joins, quais colunas calculadas, quais componentes e por quê), as hipóteses que você assumiu e o que ficou pendente.

Na devolutiva de segunda você vai abrir a conta e me explicar ao vivo as decisões principais.

## Regras do jogo

Pode usar qualquer ferramenta, inclusive IA, documentação e os tutoriais que eu te mandei. A condição é você conseguir explicar e defender cada decisão na segunda.

Se a plataforma não permitir fazer algo do jeito ideal, não trave: resolva da melhor forma possível e documente o contorno. Isso faz parte do trabalho real.

Se alguma regra parecer ambígua ou algum dado não fechar, você não consegue falar com a Carla até segunda. Decida, siga em frente e registre a pergunta na mensagem para ela.

Tolerância de arredondamento: até R$ 1,00 por comissionado por mês.

Estimativa honesta de esforço: 8 a 12 horas. Se passar muito disso, pare, entregue o que tiver e me conte onde travou. Saber onde travou também é informação útil.

Boa sorte, e bom final de semana.
