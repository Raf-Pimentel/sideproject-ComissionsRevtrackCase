# Case RevTrack / Solarix

Comissões da Solarix Energia (ago e set/2026): configuração na RevTrack e cálculo de referência em Python, conferidos entre si e contra o controle manual da cliente.

**Resultado:** as 7 regras (R1 a R7) rodam na RevTrack. Total ago + set de R$ 58.710,44 na plataforma e R$ 58.710,45 no Python (diferença de centavos por arredondamento). 13 das 16 linhas (pessoa × mês) batem com o controle da Carla; as 3 restantes estão em `docs/mensagem_carla.md`.

## Estrutura
- `data/raw/`: arquivos originais do cliente (não editar)
- `data/clean/`: bases validadas e prontas para subir na RevTrack (CSV), com dicionário em `LEIAME.md`
- `src/solarix/`: pipeline (`load`, `clean`, `model`, regras R1 a R7 em `rules/`, `closing`, `compare`, `export`) e relatórios em `reports/`
- `tests/`: testes por regra (casos de borda)
- `docs/`: briefing, arquitetura, decisões, perguntas e mensagem para a cliente, como configurei, pendências, log de anomalias, cálculo detalhado
- `outputs/`: planilha de fechamento (abas Resumo, Fechamento e Comissão por baixa) e conferência de anomalias (xlsx, gerados)

## Como rodar
```
pip install -e ".[dev]"
python -m pytest                                   # testes
python -m ruff check src tests                     # lint
python -m solarix.clean_export                     # data/clean (falha se a validação achar erro)
python -m solarix.run                              # fechamento + comparação com o controle da Carla
python -m solarix.reports.anomalias                # docs/anomalias.md
python -m solarix.reports.conferencia              # outputs/conferencia_anomalias.xlsx
python -m solarix.reports.detalhe "Ana Ribeiro"    # docs/calculo_ana_ribeiro.md
```
(sem instalar o pacote, use `PYTHONPATH=src` antes dos comandos)

## Documentação
- `docs/arquitetura.md`: fluxo, princípios e convenções
- `docs/decisoes.md`: hipóteses e status
- `docs/perguntas_carla.md`: avisos e perguntas para a cliente
- `docs/mensagem_carla.md`: mensagem de fechamento para a cliente (entregável 3)
- `docs/como_configurei.md`: arquitetura da conta na RevTrack, hipóteses e pendências (entregável 4)
- `docs/pendencias.md`: o que falta
