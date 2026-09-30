"""Comparação do nosso fechamento com o controle manual da Carla."""
import pandas as pd

from .config import TOLERANCIA_RS

COMPONENTES = ["comissao", "bonus_meta", "rampagem", "override", "total"]


def comparar(fechamento: pd.DataFrame, controle: pd.DataFrame) -> pd.DataFrame:
    """Lado a lado por (nome, competência): nosso, Carla e diferença de cada componente."""
    c = controle.rename(columns={k: f"{k}_carla" for k in COMPONENTES})
    df = fechamento.rename(columns={k: f"{k}_nosso" for k in COMPONENTES}).merge(
        c, on=["nome", "competencia"], how="outer", validate="one_to_one")
    for k in COMPONENTES:
        df[f"{k}_dif"] = (df[f"{k}_nosso"] - df[f"{k}_carla"]).round(2)
    # bateu = todos os componentes dentro da tolerância
    df["bateu"] = df[[f"{k}_dif" for k in COMPONENTES]].abs().le(TOLERANCIA_RS).all(axis=1)
    return df
