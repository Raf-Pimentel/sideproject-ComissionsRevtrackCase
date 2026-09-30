"""Gera docs/anomalias.md a partir dos dados brutos. Uso: python -m solarix.reports.anomalias"""
from ..checks import check_baixas, check_cadastro, check_tabela, check_vendas
from ..clean import clean_names
from ..config import DOCS
from ..load import load_baixas, load_cadastro, load_controle, load_itens, load_tabela, load_vendas

# Ordem de exibição: o que exige decisão primeiro
ORDER = {"ALTA": 0, "MEDIA": 1, "BAIXA": 2, "INFO": 3}


def collect():
    """Carrega, normaliza nomes e roda todas as verificações; devolve anomalias por severidade."""
    vendas, itens, baixas = load_vendas(), load_itens(), load_baixas()
    tabela, cadastro, controle = load_tabela(), load_cadastro(), load_controle()
    vendas, _, anomalies = clean_names(vendas, cadastro, controle)
    anomalies += check_vendas(vendas, itens, cadastro)
    anomalies += check_baixas(baixas, vendas)
    anomalies += check_tabela(itens, vendas, tabela)
    anomalies += check_cadastro(cadastro)
    return sorted(anomalies, key=lambda a: (ORDER[a.severity], a.id))


def render(anomalies) -> str:
    """Monta o Markdown: tabela-resumo no topo e uma seção detalhada por anomalia."""
    lines = ["# Log de anomalias dos dados", "",
             "Gerado por `python -m solarix.reports.anomalias`. Cada item indica o que foi encontrado, o tratamento proposto e o que perguntar à Carla.",
             "", "| ID | Sev. | Fonte | Título |", "|---|---|---|---|"]
    lines += [f"| {a.id} | {a.severity} | {a.source} | {a.title} |" for a in anomalies]
    for a in anomalies:
        lines += ["", f"## {a.id} — {a.title}", f"**Severidade:** {a.severity} · **Fonte:** {a.source}", "",
                  f"**O que encontrei:** {a.detail}", "", f"**Tratamento proposto:** {a.treatment}"]
        if a.question:
            lines += ["", f"**Pergunta para a Carla:** {a.question}"]
        if a.rows:
            lines += ["", f"**Chaves afetadas:** {', '.join(map(str, a.rows))}"]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    DOCS.mkdir(parents=True, exist_ok=True)
    text = render(collect())
    (DOCS / "anomalias.md").write_text(text, encoding="utf-8")
    print(f"docs/anomalias.md gerado ({text.count(chr(10))} linhas)")
