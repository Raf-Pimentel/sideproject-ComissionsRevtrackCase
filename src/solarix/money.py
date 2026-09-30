"""Arredondamento monetário. Decisão D5: 2 casas, meio para cima, aplicado por linha de cálculo."""
from decimal import ROUND_HALF_UP, Decimal


def r2(x: float) -> float:
    """Arredonda para centavos com ROUND_HALF_UP (o round() do Python usa banker's rounding)."""
    # repr() evita ruído binário de float ao converter para Decimal
    return float(Decimal(repr(float(x))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
