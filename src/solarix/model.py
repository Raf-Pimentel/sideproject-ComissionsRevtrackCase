"""Modelo de dados: carrega, limpa e junta as fontes. Espelha os 'conjuntos' (joins) da RevTrack."""
from dataclasses import dataclass

import pandas as pd

from .clean import clean_names
from .config import COMPETENCIAS, ERP_EMISSAO, INCLUIR_BAIXAS_APOS_EMISSAO
from .load import load_baixas, load_cadastro, load_controle, load_itens, load_tabela, load_vendas
from .rules.r4_cancelamento import marcar_comissionavel


@dataclass
class Modelo:
    vendas: pd.DataFrame
    itens: pd.DataFrame
    baixas: pd.DataFrame   # baixas + cabeçalho da venda + competência + flag de R4
    tabela: pd.DataFrame
    cadastro: pd.DataFrame
    controle: pd.DataFrame


def montar() -> Modelo:
    vendas, itens, baixas = load_vendas(), load_itens(), load_baixas()
    tabela, cadastro, controle = load_tabela(), load_cadastro(), load_controle()
    vendas, controle, _ = clean_names(vendas, cadastro, controle)

    # conjunto: baixa -> venda (chave id_venda). Validação: toda baixa precisa ter venda.
    b = baixas.merge(vendas, on="id_venda", how="left", validate="many_to_one")
    assert b["tipo"].notna().all(), "baixa sem venda correspondente no CRM"
    b["competencia"] = b["data_pagamento"].dt.strftime("%Y-%m")
    if not INCLUIR_BAIXAS_APOS_EMISSAO:
        b = b[b["data_pagamento"] <= pd.Timestamp(ERP_EMISSAO)]
    b = marcar_comissionavel(b)
    return Modelo(vendas, itens, b, tabela, cadastro, controle)


def baixas_do_periodo(m: Modelo) -> pd.DataFrame:
    """Só as competências pedidas (regime de caixa: mês da data de pagamento)."""
    return m.baixas[m.baixas["competencia"].isin(COMPETENCIAS)]
