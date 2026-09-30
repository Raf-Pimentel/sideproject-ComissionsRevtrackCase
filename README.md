# Case RevTrack / Solarix

Cálculo de referência das comissões da Solarix Energia (ago e set/2026), conferido contra o controle manual da cliente.

## Estrutura
- `data/raw/`: arquivos originais do cliente (não editar)
- `src/solarix/`: pipeline (`load`, `clean`, `checks`, `model`, regras R1 a R7 em `rules/`, `closing`, `compare`, `export`)
- `tests/`: testes por regra (casos de borda)
- `docs/`: briefing, plano, decisões, perguntas para a cliente, pendências, log de anomalias, cálculo detalhado
- `outputs/`: fechamento e conferência de anomalias (xlsx/csv, gerados)

## Como rodar
```
pip install -e ".[dev]"
python -m pytest                          # testes
python -m solarix.run                     # fechamento + comparação com o controle da Carla
python -m solarix.anomalias               # docs/anomalias.md
python -m solarix.conferencia             # outputs/conferencia_anomalias.xlsx
python -m solarix.detalhe "Ana Ribeiro"   # docs/calculo_ana_ribeiro.md
```
(sem instalar o pacote, use `PYTHONPATH=src` antes dos comandos)

## Onde estão as decisões
Ver `docs/decisoes.md` (hipóteses e status) e `docs/perguntas_carla.md` (o que perguntar à cliente).
