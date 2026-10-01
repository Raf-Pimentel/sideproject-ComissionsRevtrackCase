# Pendências

## Concluído
- [x] Pipeline em Python (R1 a R7) com testes e comparação com o controle da Carla.
- [x] Bases limpas em `data/clean/` (CSV) e subidas na RevTrack.
- [x] Configuração na RevTrack das 7 regras, validada contra o Python (total ago + set: R$ 58.710,44; diferenças de até R$ 0,15 por pessoa, por arredondamento por item).
  - Conjuntos: `baixa_venda`, `baixa_item`, `total_bruto_venda`, `baixa_item_total`, `baixa_item_pct`, `baixa_item_gerente`, `venda_item`, `meta_principal`, `meta_vendedor2`, `meta_base`.
  - Planos: `Solarix - Comissões 2026` (comissão principal, comissão vendedor 2, override) e `Rampagem` (comissões, bônus de meta e mínimo garantido de R$ 1.500 sobre as duas comissões; só Diego e Érica).
- [x] Conferir o cálculo da Ana (`docs/calculo_ana_ribeiro.md`): verificado à mão, bateu exatamente.
- [x] Revisar as perguntas para a Carla (`docs/perguntas_carla.md`).

## Do Rafael (conferir)
- [ ] Revisar as anomalias dos dados (`outputs/conferencia_anomalias.xlsx`: abas "Resumo" e "Onde conferir").
- [ ] Olhar os arquivos originais à procura de algo que o log de anomalias não pegou.
- [ ] Confirmar as decisões ainda como "Padrão" em `docs/decisoes.md` (D4 a D8; D1, D2 e D3 já confirmadas).
- [ ] Reconferir a redação final das perguntas antes do envio à Carla.

## Do Claude (próximos passos)
- [ ] Mensagem para a Carla (entregável 3), a partir de `docs/perguntas_carla.md`.
- [ ] Página "como configurei" (entregável 4), incluindo as ressalvas: o cartão "Vendas Totais" do relatório soma as bases dos componentes (não é faturamento); a faixa final do bônus usa 999% como "sem limite" porque a plataforma exige limite superior; a meta é uma só, de valor 100, e a base de cada linha já vem em fração da meta da pessoa.
- [ ] Atualizar a planilha de fechamento com os números da plataforma, se o Rafael exportar os relatórios de agosto e setembro.
- [ ] Corrigir o cartão "Vendas Totais" da RevTrack (base dos componentes de comissão = valor pago, taxa por coluna). Procedimento em `docs/como_configurei.md`, seção 10 (limitação 1). Combinado para depois da apresentação.
