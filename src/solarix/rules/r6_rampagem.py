"""R6: rampagem. Consultores nos 3 primeiros meses-calendário de casa têm garantia mínima de R$ 1.500/mês
sobre R1 + R2 (já após o split). Paga-se o complemento da diferença. O bônus de meta não entra na conta."""
import pandas as pd

from ..config import RAMPAGEM_GARANTIA, RAMPAGEM_MESES


def mes_de_casa(admissao: pd.Timestamp, competencia: str) -> int:
    """1 = mês da admissão (conta cheio, mesmo admitido no fim do mês)."""
    ano, mes = map(int, competencia.split("-"))
    return (ano - admissao.year) * 12 + (mes - admissao.month) + 1


def complemento(comissao_mes: float, admissao: pd.Timestamp, competencia: str, eh_consultor: bool) -> float:
    """Complemento até a garantia; zero fora da rampagem ou para quem não é consultor."""
    if not eh_consultor:
        return 0.0
    n = mes_de_casa(admissao, competencia)
    if not (1 <= n <= RAMPAGEM_MESES):
        return 0.0
    return max(0.0, round(RAMPAGEM_GARANTIA - comissao_mes, 2))
