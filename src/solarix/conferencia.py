"""Gera outputs/conferencia_anomalias.xlsx: cada problema em linguagem simples, com arquivo e linha do Excel.
Uso: python -m solarix.conferencia
"""
import pandas as pd
from openpyxl.styles import Alignment

from .clean import _key
from .config import ERP_EMISSAO, FILES, RAW
from .load import load_baixas, load_cadastro, load_itens, load_tabela, load_vendas

OUT = RAW.parents[1] / "outputs" / "conferencia_anomalias.xlsx"

# Deslocamento entre o índice do DataFrame e o número da linha no Excel de origem:
# arquivos com cabeçalho na linha 1 -> +2; baixas (3 linhas de título + cabeçalho) -> +5
OFF = {"vendas": 2, "itens": 2, "tabela": 2, "baixas": 5}


def _fmt(d):
    return d.strftime("%d/%m/%Y")


def _ev(problem, key, idx, text):
    """Uma evidência: linha do Excel de origem onde o problema pode ser visto."""
    return {"Problema": problem, "Arquivo": FILES[key], "Linha no Excel": int(idx) + OFF[key], "O que você vai ver na linha": text}


def build():
    v, it, b = load_vendas(), load_itens(), load_baixas()
    tab, cad = load_tabela(), load_cadastro()
    ev = []

    # 1. Baixas depois da data de emissão do relatório
    for i, r in b[b["data_pagamento"] > pd.Timestamp(ERP_EMISSAO)].iterrows():
        ev.append(_ev(1, "baixas", i, f"Baixa {r.n_baixa}: parcela {r.n_parcela}, R$ {r.valor_pago:,.2f}, paga em {_fmt(r.data_pagamento)}"))

    # 2 e 3. Pagamentos depois do cancelamento
    canc = v[v["status"] == "CANCELADA"].set_index("id_venda")
    for i, r in b[b["id_venda"].isin(canc.index)].iterrows():
        dc = canc.loc[r.id_venda, "data_cancelamento"]
        if r.data_pagamento > dc:
            ev.append(_ev(2, "baixas", i, f"Baixa {r.n_baixa}: parcela {r.n_parcela} paga em {_fmt(r.data_pagamento)}, mas a venda foi cancelada em {_fmt(dc)}"))

    # 4. Instalação em venda PARCEIRO sem % na tabela
    m = it.reset_index().merge(v[["id_venda", "canal"]], on="id_venda").merge(tab[["linha_produto", "canal", "pct_comissao"]], on=["linha_produto", "canal"], how="left")
    for _, r in m[m["pct_comissao"].isna()].iterrows():
        ev.append(_ev(3, "itens", r["index"], f"Item {r.id_item}: {r.linha_produto}, R$ {r.valor_bruto:,.2f} (venda {r.id_venda}, canal {r.canal})"))
        vi = v.index[v["id_venda"] == r.id_venda][0]
        ev.append(_ev(3, "vendas", vi, f"Venda {r.id_venda}: canal {v.loc[vi, 'canal']}"))
    inst = tab[tab["linha_produto"] == "INSTALACAO"]
    for i, r in inst.iterrows():
        ev.append(_ev(3, "tabela", i, f"INSTALACAO / {r.canal}: {r.pct_comissao}%  (não existe linha INSTALACAO / PARCEIRO)"))

    # 5. Nome de vendedor com grafia diferente do cadastro
    canon = {_key(n): n for n in cad["nome"]}
    for i, r in v.iterrows():
        for col in ("vendedor", "vendedor2"):
            x = r[col]
            if pd.notna(x) and x != canon.get(_key(x), x):
                ev.append(_ev(4, "vendas", i, f"Venda {r.id_venda}: '{x}' (no cadastro é '{canon[_key(x)]}')"))

    # 6. Parcela paga pela metade
    g = b.groupby(["id_venda", "parcela"]).agg(pago=("valor_pago", "sum"), parc=("valor_parcela", "first"))
    for (venda, parc), r in g[g["pago"] + 0.011 < g["parc"]].iterrows():
        for i, x in b[(b.id_venda == venda) & (b.parcela == parc)].iterrows():
            ev.append(_ev(5, "baixas", i, f"Baixa {x.n_baixa}: parcela {x.n_parcela}, pago R$ {x.valor_pago:,.2f} de R$ {x.valor_parcela:,.2f}"))

    # 7. Vendas sem nenhuma baixa
    for i, r in v[~v["id_venda"].isin(b["id_venda"])].iterrows():
        ev.append(_ev(6, "vendas", i, f"Venda {r.id_venda} ({r.tipo}) de {_fmt(r.data_venda)}: nenhuma baixa correspondente no ERP"))

    # 8. Descontos exatamente nos limites das faixas
    for i, r in v[(v["tipo"] == "PROJETO") & v["desconto_pct"].isin([10, 15])].iterrows():
        ev.append(_ev(7, "vendas", i, f"Venda {r.id_venda}: desconto de {r.desconto_pct}%"))

    # 9. Monitoramento: 50% já na tabela
    for i, r in tab[tab["linha_produto"] == "MONITORAMENTO"].iterrows():
        ev.append(_ev(8, "tabela", i, f"MONITORAMENTO / {r.canal}: {r.pct_comissao}%  ({r.observacao})"))
    return pd.DataFrame(ev)


PROBLEMAS = [
    (1, "ALTA", "Pagamentos com data depois da emissão do relatório",
     "O ERP diz 'Emitido em 25/09/2026', mas 7 pagamentos têm data de 26 a 30/09. Não deveriam existir num relatório emitido antes.",
     "Set/2026 (R$ 60.308,08 de baixas)", "Mantenho no cálculo e mostro o impacto separado.",
     "Esses pagamentos já aconteceram ou são previstos? Se previstos, tiro do cálculo."),
    (2, "MEDIA", "Pagamentos feitos depois do cancelamento da venda",
     "Duas vendas canceladas receberam pagamento depois do cancelamento (1011 e 1013). A baixa 59001 ainda tem numeração fora do padrão do ERP (50001 a 50115).",
     "Regra R4 (cancelamento)", "A regra R4 já exclui esses pagamentos da comissão.",
     "Esses valores foram devolvidos ao cliente ou é lançamento manual?"),
    (3, "ALTA", "Instalação da venda 1006 não tem % de comissão",
     "A venda 1006 é do canal PARCEIRO e tem um item de instalação. A tabela de comissão não tem linha 'INSTALACAO / PARCEIRO' (a observação diz que a instalação é do parceiro).",
     "Bruno Sato, set/2026", "Comissão de 0% nesse item, mas ele continua contando no rateio da baixa.",
     "DECISÃO SUA: 0% mantendo no rateio (padrão) ou tirar o item do rateio?"),
    (4, "MEDIA", "Nome 'João Pedro Almeida' escrito de 3 jeitos no CRM",
     "'Joao Pedro Almeida' (sem acento) e 'João Pedro Almeida ' (espaço no fim) aparecem em 10 vendas. Para o computador são pessoas diferentes.",
     "Sem tratamento, essas vendas ficariam sem vendedor no cálculo", "Padronizo pelo nome do cadastro.", "Nada. Só confirmar que é a mesma pessoa."),
    (5, "MEDIA", "Parcela paga pela metade",
     "A parcela 3 da venda 1031 tem R$ 13.056,63, mas só R$ 6.528,32 foi pago.",
     "Comissão sobre o valor pago", "Comissiono só o valor efetivamente pago (regra R1).", "O saldo continua em aberto?"),
    (6, "BAIXA", "Vendas sem nenhum pagamento no ERP",
     "6 vendas não têm nenhum pagamento. Duas são antigas: a 1016 (08/06) e a 1010 (20/08).",
     "Nenhuma comissão de caixa nessas vendas (contam só na meta)", "Nenhuma comissão sobre elas.", "Por que 1016 e 1010 nunca receberam nada?"),
    (7, "INFO", "Descontos de exatamente 10% e 15%",
     "6 projetos têm desconto exatamente no limite das faixas (a regra diz 'até 5% inclusive', mas não diz para 10% e 15%).",
     "Muda o % de comissão desses projetos", "Trato o limite como inclusivo: 10% paga 80% e 15% paga 60%.",
     "DECISÃO SUA: confirma que 10% e 15% também são inclusivos?"),
    (8, "MEDIA", "Monitoramento com 50% na tabela e também na regra R2",
     "O 50% do monitoramento aparece na tabela de comissão e de novo na regra R2. Se o cálculo aplicar os dois, paga em dobro.",
     "Assinaturas de monitoramento", "Aplico o 50% uma vez só, sobre a 1ª mensalidade.", "Nada."),
]


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    resumo = pd.DataFrame(PROBLEMAS, columns=["Nº", "Gravidade", "Problema", "O que está errado (em português)", "O que afeta", "O que eu vou fazer", "O que preciso de você"])
    ev = build()
    with pd.ExcelWriter(OUT, engine="openpyxl") as w:
        resumo.to_excel(w, sheet_name="Resumo", index=False)
        ev.to_excel(w, sheet_name="Onde conferir", index=False)
        for name, widths in (("Resumo", [5, 11, 40, 70, 34, 45, 55]), ("Onde conferir", [10, 42, 15, 95])):
            ws = w.sheets[name]
            for col, wd in zip("ABCDEFG", widths):
                ws.column_dimensions[col].width = wd
            for row in ws.iter_rows(min_row=2):
                for c in row:
                    c.alignment = Alignment(wrap_text=True, vertical="top")
    print(f"{OUT} ({len(ev)} evidências)")


if __name__ == "__main__":
    main()
