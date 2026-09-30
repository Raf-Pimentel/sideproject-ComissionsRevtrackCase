"""R4: vendas canceladas.

- Cancelada em até 60 dias corridos da venda: nenhuma comissão nem override, mesmo em baixas já recebidas.
- Cancelada depois de 60 dias: valem as baixas com pagamento até a data do cancelamento (inclusive).
"""
import pandas as pd

from ..config import PRAZO_CANCELAMENTO_DIAS


def marcar_comissionavel(baixas: pd.DataFrame) -> pd.DataFrame:
    """Adiciona `comissionavel` (bool) a baixas já unidas ao cabeçalho da venda.

    Colunas exigidas: status, data_venda, data_cancelamento, data_pagamento.
    """
    b = baixas.copy()
    cancelada = b["status"] == "CANCELADA"
    dias = (b["data_cancelamento"] - b["data_venda"]).dt.days
    # dias <= 60 zera tudo; acima disso só conta o que foi pago até o dia do cancelamento
    cancel_total = cancelada & (dias <= PRAZO_CANCELAMENTO_DIAS)
    cancel_parcial = cancelada & (dias > PRAZO_CANCELAMENTO_DIAS) & (b["data_pagamento"] > b["data_cancelamento"])
    b["comissionavel"] = ~(cancel_total | cancel_parcial)
    return b
