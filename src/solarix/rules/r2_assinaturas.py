"""R2: assinaturas de monitoramento. Paga 50% do valor pago da 1ª mensalidade; sem redutor de desconto."""
import pandas as pd

from ..config import ASSINATURA_PCT
from ..money import r2


def comissao_assinaturas(baixas: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por baixa da parcela 1. `baixas` deve conter só baixas comissionáveis (R4) de ASSINATURA."""
    # T02: o 50% é aplicado aqui uma única vez (a tabela também traz 50%, mas não é usada para assinaturas)
    primeira = baixas[baixas["parcela"] == 1].copy()
    primeira["comissao"] = [r2(v * ASSINATURA_PCT) for v in primeira["valor_pago"]]
    return primeira[["n_baixa", "id_venda", "competencia", "valor_pago", "comissao"]]
