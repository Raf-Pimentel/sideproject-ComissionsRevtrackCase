"""R5: bônus de meta mensal dos consultores.

Competência = mês da DATA DA VENDA (não do pagamento). Base = valor líquido (itens x (1 - desconto)) dos
PROJETOS não cancelados, com vendas conjuntas divididas 60/40. Compara-se com a meta mensal do cadastro.
"""
import pandas as pd

from ..config import META_FAIXAS
from .r3_split import dividir_valor


def bonus_por_atingimento(atingimento: float) -> float:
    """Faixa pelo atingimento (limite inferior inclusivo): <80% 0; 80-<100% 800; 100-<120% 1500; >=120% 2500."""
    # round(…, 9) evita que ruído de float derrube um valor exatamente no limite
    a = round(atingimento, 9)
    bonus = 0.0
    for minimo, valor in META_FAIXAS:
        if a >= minimo:
            bonus = valor
    return bonus


def bonus_meta(vendas: pd.DataFrame, itens: pd.DataFrame, cadastro: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por (consultor, mês da venda) com líquido, meta, atingimento e bônus."""
    bruto = itens.groupby("id_venda")["valor_bruto"].sum()
    v = vendas[(vendas["tipo"] == "PROJETO") & (vendas["status"] != "CANCELADA")].copy()
    v["liquido"] = v["id_venda"].map(bruto) * (1 - v["desconto_pct"] / 100)
    v["competencia"] = v["data_venda"].dt.strftime("%Y-%m")

    linhas = []
    for r in v.itertuples():
        principal, v2 = dividir_valor(r.liquido, pd.notna(r.vendedor2))
        linhas.append((r.vendedor, r.competencia, principal))
        if pd.notna(r.vendedor2):
            linhas.append((r.vendedor2, r.competencia, v2))
    df = pd.DataFrame(linhas, columns=["nome", "competencia", "liquido"]).groupby(
        ["nome", "competencia"], as_index=False)["liquido"].sum()

    metas = cadastro.dropna(subset=["meta_mensal"]).set_index("nome")["meta_mensal"]
    df = df[df["nome"].isin(metas.index)].copy()  # só quem tem meta (consultores)
    df["meta"] = df["nome"].map(metas)
    df["atingimento"] = df["liquido"] / df["meta"]
    df["bonus_meta"] = df["atingimento"].map(bonus_por_atingimento)
    return df
