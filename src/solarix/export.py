"""Exporta a tabela de fechamento (entregável 2) em xlsx."""
import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill

from .compare import COMPONENTES

ROTULOS = {"comissao": "Comissão s/ vendas", "bonus_meta": "Bônus de meta", "rampagem": "Compl. rampagem",
           "override": "Override", "total": "Total"}


def exportar_fechamento(comp: pd.DataFrame, por_baixa: pd.DataFrame, caminho):
    """Uma linha por comissionado x mês: nosso, Carla e diferença de cada componente."""
    cols = ["nome", "competencia"]
    for k in COMPONENTES:
        cols += [f"{k}_nosso", f"{k}_carla", f"{k}_dif"]
    out = comp[cols + ["bateu"]].sort_values(["nome", "competencia"]).copy()
    out["bateu"] = out["bateu"].map({True: "Sim", False: "NÃO"})
    # cabeçalho em duas camadas: componente / (nosso, Carla, diferença)
    out.columns = pd.MultiIndex.from_tuples(
        [("", "Comissionado"), ("", "Competência")]
        + [(ROTULOS[k], s) for k in COMPONENTES for s in ("Nosso", "Carla", "Dif.")] + [("", "Bateu?")])
    with pd.ExcelWriter(caminho, engine="openpyxl") as w:
        out.to_excel(w, sheet_name="Fechamento")
        por_baixa.to_excel(w, sheet_name="Comissão por baixa", index=False)
        ws = w.sheets["Fechamento"]
        ws.delete_rows(3)  # remove linha vazia que o pandas cria sob cabeçalho multinível
        ws.column_dimensions["B"].width = 22
        ws.column_dimensions["C"].width = 12
        red = PatternFill("solid", fgColor="F8CBAD")
        for row in ws.iter_rows(min_row=3):
            for c in row:
                if isinstance(c.value, float):
                    c.number_format = "#,##0.00"
            if row[-1].value == "NÃO":
                for c in row:
                    c.fill = red
        for c in ws[1] + ws[2]:
            c.font = Font(bold=True)
            c.alignment = Alignment(horizontal="center")
        ws.freeze_panes = "D3"
