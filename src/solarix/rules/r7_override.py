"""R7: override de gerência. Cada gerente recebe 1% do valor pago das baixas comissionáveis (que geram
comissão por R1 ou R2, respeitando R4) das vendas cujo vendedor PRINCIPAL é da sua equipe."""
import pandas as pd

from ..config import OVERRIDE_PCT
from ..money import r2


def override_gerencia(baixas_comissionaveis: pd.DataFrame, comissao_por_baixa: pd.DataFrame,
                      vendas: pd.DataFrame, cadastro: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por (baixa, gerente). Só entram baixas cuja comissão total é maior que zero."""
    geram = comissao_por_baixa[comissao_por_baixa["comissao"] > 0][["n_baixa"]]
    b = baixas_comissionaveis.merge(geram, on="n_baixa")
    b = b.merge(vendas[["id_venda", "vendedor"]], on="id_venda", suffixes=("", "_v"))
    b = b.merge(cadastro[["nome", "gerente"]], left_on="vendedor", right_on="nome", how="left")
    # D4 (A5): override sobre 100% do valor pago, mesmo em venda conjunta; equipe = do vendedor principal
    b["override"] = [r2(v * OVERRIDE_PCT) for v in b["valor_pago"]]
    return b[["n_baixa", "id_venda", "competencia", "gerente", "valor_pago", "override"]].rename(columns={"gerente": "nome"})
