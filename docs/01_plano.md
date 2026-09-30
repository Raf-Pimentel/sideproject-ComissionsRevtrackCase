# Plano do case RevTrack / Solarix

## 1. Decisões já tomadas

| Tema          | Decisão                                                                                                                                                                                |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Stack         | Python + pandas, pytest                                                                                                                                                                 |
| Arquitetura   | Pipeline em camadas, uma função por regra (R1..R7)                                                                                                                                    |
| Uso do Claude | Claude implementa, Rafael valida e decide ambiguidades, Claude não toma decisões importantes sem perguntar antes, claude não faz hipóteses ou simplificações sem perguntar antes. |
| Entregáveis  | `.xlsx` (fechamento) + `.md` (mensagem Carla, "como configurei")                                                                                                                    |

## 2. Arquitetura de código

```
solarix/
  data/raw/            # arquivos originais, NUNCA editados
  data/clean/          # saída da limpeza (parquet/csv)
  src/solarix/
    config.py          # constantes: competências, faixas de desconto/meta, splits, 60 dias
    load.py            # leitura dos xlsx (encoding, cabeçalho do ERP, formato BR)
    clean.py           # normalização de nomes, datas, decimais, dedup; gera relatório de anomalias
    model.py           # joins: baixas -> vendas -> itens -> tabela % -> cadastro
    rules/
      r1_projetos.py   # rateio por item, % tabela, redutor de desconto
      r2_assinaturas.py
      r3_split.py
      r4_cancelamento.py
      r5_meta.py
      r6_rampagem.py
      r7_override.py
    closing.py         # consolida por comissionado x mês
    compare.py         # vs. controle da Carla, diferença, tolerância R$ 1,00
    export.py          # xlsx de fechamento
  tests/               # 1 arquivo por regra, com casos de borda
  docs/
    anomalias.md       # tudo que a limpeza encontrou
    decisoes.md        # log de hipóteses e decisoes tomadas (ID, regra, ambiguidade, decisão, impacto R$)
    mensagem_carla.md
    como_configurei.md 
```

Princípios:

- **Dados brutos imutáveis**; toda transformação é reproduzível com um comando (`python -m solarix.run`).
- **Regras como funções puras** (DataFrame entra, DataFrame sai), sem I/O, fáceis de testar.
- **Parâmetros em `config.py`**, nada de números mágicos hard coded dentro das regras.
- **Rastreabilidade linha a linha**: a saída de R1/R2 guarda baixa, item, %, redutor, split e valor, para explicar qualquer centavo.
- **Cada regra espelha um componente da RevTrack**, então a Fase 4 vira tradução, não redescoberta.
- **Dinheiro**: `Decimal` ou arredondamento explícito e documentado (ROUND_HALF_UP, no fim de cada linha ou no total, decisão registrada).
- **Testes**: casos de borda (desconto exatamente 5/10/15%, cancelamento no dia 60 e 61, pagamento na data do cancelamento, rampagem mês 3 vs. 4, split 60/40, gerente sem vendas).
- **Validações de integridade** (falham alto): baixa sem venda, venda sem item, soma dos rateios = valor pago, chaves duplicadas.

## 3. Filosofia de uso do Claude

1. **Plano antes de código.** Este documento e o log de decisões vêm primeiro.
2. **Claude propõe, Rafael valida e decide.** Toda ambiguidade vai para `docs/decisoes.md` com a opção padrão; nada é decidido em silêncio.
3. **Uma regra por vez**, na ordem R4 -> R1 -> R2 -> R3 -> R6/R5 -> R7, cada uma com testes verdes antes da próxima.
4. **Verificação independente.** Rafael confere à mão 2 a 3 vendas por regra (uma simples, uma com split, uma com cancelamento). Isso é o que sustenta a defesa na devolutiva.
5. **Nada de confiança cega no controle da Carla.** Divergência não significa que ela errou nem que nós erramos; cada uma é classificada (arredondamento, regra ambígua, erro dela, erro nosso, dado sujo).
6. **Números só vêm do código.** Claude nunca escreve valores na mensagem ou na documentação de cabeça; eles são gerados a partir da saída do pipeline.
7. **Explicabilidade:** ao fim de cada etapa, Claude resume em linguagem simples o que a regra faz, para Rafael conseguir explicar ao vivo.
8. **Fora do escopo do Claude:** configurar a conta demo da RevTrack (sem acesso). Ele entrega a especificação pronta para replicar.

## 4. Etapas e critérios de pronto

| # | Etapa                                          | Pronto quando                                               |
| - | ---------------------------------------------- | ----------------------------------------------------------- |
| 0 | Setup e decisões abertas respondidas          | pastas criadas,`decisoes.md` iniciado                     |
| 1 | Load + clean + anomalias                       | `anomalias.md` revisado por Rafael                        |
| 2 | Modelo (joins)                                 | integridade passa, contagens batem com os raw               |
| 3 | Regras R4, R1, R2, R3                          | testes verdes, amostra conferida à mão                    |
| 4 | R6, R5, R7                                     | idem                                                        |
| 5 | Fechamento e comparação                      | tabela por comissionado x mês, divergências classificadas |
| 6 | Entregáveis (xlsx, mensagem, como configurei) | números gerados pelo código, revisados                    |
| 7 | Configuração na RevTrack (Rafael)            | relatório da plataforma = tabela de referência            |
| 8 | Ensaio da devolutiva                           | Rafael explica as 3 decisões mais difíceis                |

## 5. Ambiguidades já identificadas (defaults propostos)

| #   | Ponto                                                        | Default proposto                                                           |
| --- | ------------------------------------------------------------ | -------------------------------------------------------------------------- |
| A1  | Desconto de exatamente 5/10/15%                              | limite superior inclusivo de cada faixa (5% = 100%, 10% = 80%, 15% = 60%)  |
| A2  | Cancelamento "até 60 dias"                                  | dias = data cancelamento - data venda; <= 60 zera tudo                     |
| A3  | Rampagem: base da garantia                                   | R1 + R2 do mês após split, antes de cancelamentos já excluídos         |
| A4  | Rampagem para quem está em ramp e é vendedor 2             | vale o mesmo cálculo, sobre a parte dele                                  |
| A5  | Override: venda conjunta com vendedor 2 de outra equipe      | usa só o vendedor principal (regra R7); override sobre 100% do valor pago |
| A6  | Meta: vendas de setembro do Diego/Érica e meta proporcional | meta cheia do cadastro, sem proporcionalidade                              |
| A7  | Arredondamento                                               | por linha de item, ROUND_HALF_UP, 2 casas; testar sensibilidade vs. total  |
| A8  | Baixa de assinatura: "1ª mensalidade"                       | parcela = 1, independente da data de pagamento                             |
| A9  | Baixa parcial (valor pago < valor parcela)                   | comissão sobre valor pago, como diz R1                                    |
| A10 | Gerente que também vende                                    | a confirmar no cadastro (Marcos Teles aparece como Gerente Comercial)      |

## 6. Riscos

- Dados sujos escondendo duplicidade (baixas, vendas) -> validações de integridade.
- Plataforma sem suporte a algo (ex.: rateio por item) -> documentar contorno em `como_configurei.md`.
- Tempo: estimativa de 8 a 12h.

## 7. Convenção de comentários (vale para todo o código do projeto)
- Docstring curta em todo módulo e função pública: o que faz, não como.
- Comentário de linha só para o **porquê** (regra de negócio, decisão, armadilha dos dados), citando a regra (R1..R7) ou o ID da anomalia quando houver.
- Nada de comentário que repita o código; nome claro dispensa comentário.
- Toda hipótese assumida no código deve constar em `docs/decisoes.md`.
