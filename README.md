# Case RevTrack / Solarix

Cálculo de referência das comissões da Solarix Energia (ago e set/2026), conferido contra o controle manual da cliente.

## Estrutura
- `data/raw/`: arquivos originais do cliente (não editar)
- `data/clean/`: bases validadas e prontas para subir na RevTrack (csv e xlsx), com dicionário em `LEIAME.md`
- `src/solarix/`: pipeline (`load`, `clean`, `model`, regras R1 a R7 em `rules/`, `closing`, `compare`, `export`) e relatórios em `reports/`
- `tests/`: testes por regra (casos de borda)
- `docs/`: briefing, arquitetura, decisões, perguntas para a cliente, pendências, log de anomalias, cálculo detalhado
- `outputs/`: fechamento e conferência de anomalias (xlsx, gerados)

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
- `docs/pendencias.md`: o que falta
