"""R3: venda conjunta. Comissão dividida 60% (vendedor principal) / 40% (vendedor 2). Vale também para a meta (R5)."""
import pandas as pd

from ..config import SPLIT_PRINCIPAL, SPLIT_VENDEDOR2
from ..money import r2


def dividir_valor(valor: float, tem_vendedor2: bool):
    """Devolve (parte do principal, parte do vendedor 2). A soma sempre fecha com o valor original."""
    if not tem_vendedor2:
        return valor, 0.0
    v2 = r2(valor * SPLIT_VENDEDOR2)
    return r2(valor - v2), v2


def atribuir_comissao(comissao_por_baixa: pd.DataFrame, vendas: pd.DataFrame) -> pd.DataFrame:
    """Recebe `n_baixa, id_venda, competencia, comissao` e devolve uma linha por (baixa, comissionado)."""
    m = comissao_por_baixa.merge(vendas[["id_venda", "vendedor", "vendedor2"]], on="id_venda")
    saida = []
    for r in m.itertuples():
        principal, v2 = dividir_valor(r.comissao, pd.notna(r.vendedor2))
        saida.append((r.n_baixa, r.id_venda, r.competencia, r.vendedor, "principal", principal))
        if pd.notna(r.vendedor2):
            saida.append((r.n_baixa, r.id_venda, r.competencia, r.vendedor2, "vendedor2", v2))
    return pd.DataFrame(saida, columns=["n_baixa", "id_venda", "competencia", "nome", "papel", "comissao"])
