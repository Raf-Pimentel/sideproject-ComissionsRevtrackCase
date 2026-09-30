"""Leitura dos arquivos brutos do cliente. Só lê e renomeia colunas; a limpeza fica em clean.py."""
import pandas as pd

from .config import FILES, RAW

# Colunas são renomeadas por posição (o export do cliente usa cabeçalhos longos e com acento).
# Se o layout do arquivo mudar, a leitura falha alto em vez de trocar colunas em silêncio.


def _path(key):
    return RAW / FILES[key]


def _br_number(s: pd.Series) -> pd.Series:
    """Converte texto em formato BR para float: '23.503,28' -> 23503.28."""
    return s.str.strip().str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float)


def load_vendas() -> pd.DataFrame:
    df = pd.read_excel(_path("vendas"))
    df.columns = ["id_venda", "tipo", "data_venda", "cliente", "vendedor", "vendedor2",
                  "canal", "desconto_pct", "status", "data_cancelamento"]
    return df


def load_itens() -> pd.DataFrame:
    df = pd.read_excel(_path("itens"))
    df.columns = ["id_item", "id_venda", "linha_produto", "descricao", "valor_bruto"]
    return df


def load_baixas() -> pd.DataFrame:
    """Relatório do ERP: título/período nas 3 primeiras linhas, tabela a partir da 4ª."""
    # dtype=str evita o pandas interpretar '1.234,56' e datas dd/mm de forma errada
    df = pd.read_excel(_path("baixas"), header=3, dtype=str)
    df.columns = ["n_baixa", "n_parcela", "id_venda", "parcela", "total_parcelas",
                  "valor_parcela", "valor_pago", "data_pagamento"]
    df["n_baixa"] = df["n_baixa"].astype(int)
    df["id_venda"] = df["id_venda"].astype(int)
    df["parcela"] = df["parcela"].astype(int)
    df["total_parcelas"] = df["total_parcelas"].astype(int)
    df["valor_parcela"] = _br_number(df["valor_parcela"])
    df["valor_pago"] = _br_number(df["valor_pago"])
    # formato explícito: erro se aparecer data fora do padrão, sem inversão dia/mês
    df["data_pagamento"] = pd.to_datetime(df["data_pagamento"], format="%d/%m/%Y")
    return df


def load_tabela() -> pd.DataFrame:
    df = pd.read_excel(_path("tabela"))
    df.columns = ["linha_produto", "canal", "pct_comissao", "observacao"]
    return df


def load_cadastro() -> pd.DataFrame:
    df = pd.read_excel(_path("cadastro"))
    df.columns = ["nome", "cargo", "equipe", "gerente", "data_admissao", "meta_mensal", "email"]
    return df


def load_controle() -> pd.DataFrame:
    """Controle manual da Carla (referência para conferência, não é insumo do cálculo)."""
    df = pd.read_excel(_path("controle"), header=3)
    df.columns = ["nome", "competencia", "comissao", "bonus_meta", "rampagem", "override", "total"]
    return df
