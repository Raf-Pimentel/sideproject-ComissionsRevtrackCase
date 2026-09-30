"""Limpeza: normaliza nomes e devolve dados limpos + anomalias encontradas no caminho."""
import unicodedata
from dataclasses import dataclass, field

import pandas as pd


@dataclass
class Anomaly:
    """Um achado de qualidade de dados; alimenta o docs/anomalias.md."""
    id: str
    severity: str          # ALTA | MEDIA | BAIXA | INFO
    source: str
    title: str
    detail: str
    treatment: str
    question: str = ""
    rows: list = field(default_factory=list)


def _key(s: str) -> str:
    """Chave de comparação: sem acento, minúscula, sem espaços nas pontas."""
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return " ".join(s.lower().split())


def clean_names(vendas: pd.DataFrame, cadastro: pd.DataFrame, controle: pd.DataFrame):
    """Mapeia cada variação de nome de pessoa para o nome canônico do cadastro."""
    # O cadastro é a fonte de verdade dos nomes; o CRM varia
    canon = {_key(n): n for n in cadastro["nome"]}
    anomalies = []
    v = vendas.copy()  # não altera o DataFrame recebido
    for col in ("vendedor", "vendedor2"):
        raw = v[col]
        fixed = raw.map(lambda x: canon.get(_key(x), x) if pd.notna(x) else x)
        changed = raw.notna() & (raw != fixed)
        if changed.any():
            variants = raw[changed].map(repr).value_counts().to_dict()
            anomalies.append(Anomaly(
                id="A01", severity="MEDIA", source="01_CRM_Vendas", title=f"Nome divergente em '{col}'",
                detail=f"{int(changed.sum())} linhas com grafia diferente do cadastro (acento/espaço): {variants}",
                treatment="Normalizado para o nome do cadastro (chave sem acento, minúscula, sem espaços nas pontas).",
                rows=v.loc[changed, "id_venda"].tolist()))
        v[col] = fixed
    # Nome que continua fora do cadastro após a normalização não pode ser corrigido automaticamente
    unknown = set(v["vendedor"]) - set(canon.values())
    unknown |= set(v["vendedor2"].dropna()) - set(canon.values())
    if unknown:
        anomalies.append(Anomaly("A02", "ALTA", "01_CRM_Vendas", "Vendedor fora do cadastro",
                                 f"{sorted(unknown)}", "Nenhum tratamento automático; revisar."))
    c = controle.copy()
    c["nome"] = c["nome"].map(lambda x: canon.get(_key(x), x))
    return v, c, anomalies
