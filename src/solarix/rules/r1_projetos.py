"""R1: comissão de projetos.

Para cada baixa de PROJETO, o valor pago é rateado entre os itens pelo valor bruto de cada um.
Sobre a parte do item aplica-se o % da tabela (linha de produto x canal), reduzido pelo desconto da venda.
"""
import pandas as pd

from ..config import DESCONTO_FAIXAS, ITEM_SEM_PCT_ENTRA_NO_RATEIO
from ..money import r2


def redutor_desconto(desconto_pct: float) -> float:
    """Fator sobre o % da tabela. Limite superior de cada faixa é inclusivo (D3)."""
    for limite, fator in DESCONTO_FAIXAS:
        if desconto_pct <= limite:
            return fator
    raise ValueError(f"desconto fora das faixas: {desconto_pct}")


def comissao_projetos(baixas: pd.DataFrame, itens: pd.DataFrame, tabela: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por (baixa, item). `baixas` deve conter só baixas comissionáveis (R4) de PROJETO."""
    # a tabela é por linha x canal: mantém só o canal da venda
    it = itens.merge(baixas[["id_venda", "canal"]].drop_duplicates(), on="id_venda").merge(
        tabela[["linha_produto", "canal", "pct_comissao"]], on=["linha_produto", "canal"], how="left")
    # D2: item sem % (ex.: instalação em PARCEIRO) comissiona 0%
    it["pct_comissao"] = it["pct_comissao"].fillna(0.0)
    it["com_pct"] = it["pct_comissao"] > 0

    linhas = baixas[["n_baixa", "id_venda", "valor_pago", "desconto_pct", "competencia"]].merge(it, on="id_venda")
    # denominador do rateio: todos os itens (D2, Opção A) ou só os que têm % (Opção B)
    base = linhas if ITEM_SEM_PCT_ENTRA_NO_RATEIO else linhas[linhas["com_pct"]]
    total_bruto = base.groupby("n_baixa")["valor_bruto"].sum().rename("total_bruto")
    linhas = linhas.merge(total_bruto, on="n_baixa")
    if not ITEM_SEM_PCT_ENTRA_NO_RATEIO:
        linhas.loc[~linhas["com_pct"], "valor_bruto"] = 0.0

    linhas["base_item"] = linhas["valor_pago"] * linhas["valor_bruto"] / linhas["total_bruto"]
    linhas["redutor"] = linhas["desconto_pct"].map(redutor_desconto)
    # D5: arredonda por item
    linhas["comissao"] = [r2(b * p / 100 * r) for b, p, r in
                          zip(linhas["base_item"], linhas["pct_comissao"], linhas["redutor"])]
    return linhas[["n_baixa", "id_venda", "competencia", "id_item", "linha_produto", "valor_pago",
                   "base_item", "pct_comissao", "redutor", "comissao"]]
