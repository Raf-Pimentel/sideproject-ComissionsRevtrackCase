"""Testes das regras com casos de borda. Cada teste cita a regra do briefing."""
import pandas as pd
import pytest

from solarix.money import r2
from solarix.rules.r1_projetos import comissao_projetos, redutor_desconto
from solarix.rules.r2_assinaturas import comissao_assinaturas
from solarix.rules.r3_split import dividir_valor
from solarix.rules.r4_cancelamento import marcar_comissionavel
from solarix.rules.r5_meta import bonus_por_atingimento
from solarix.rules.r6_rampagem import complemento, mes_de_casa
from solarix.rules.r7_override import override_gerencia


def test_arredondamento_meio_para_cima():
    assert r2(0.125) == 0.13   # round() do Python daria 0.12
    assert r2(2.675) == 2.68


@pytest.mark.parametrize("desconto,esperado", [
    (0, 1.0), (5, 1.0), (5.01, 0.8), (10, 0.8), (10.01, 0.6), (15, 0.6), (15.01, 0.4)])
def test_r1_redutor_nos_limites(desconto, esperado):
    assert redutor_desconto(desconto) == esperado


def _baixa(**kw):
    base = dict(n_baixa=1, id_venda=10, valor_pago=1000.0, desconto_pct=0, competencia="2026-08", canal="DIRETO")
    base.update(kw)
    return pd.DataFrame([base])


TABELA = pd.DataFrame({"linha_produto": ["KIT_RESIDENCIAL", "INSTALACAO"], "canal": ["DIRETO", "DIRETO"],
                       "pct_comissao": [4.0, 6.0]})


def test_r1_rateio_por_valor_bruto():
    itens = pd.DataFrame({"id_item": ["10-1", "10-2"], "id_venda": [10, 10],
                          "linha_produto": ["KIT_RESIDENCIAL", "INSTALACAO"], "valor_bruto": [800.0, 200.0]})
    r = comissao_projetos(_baixa(), itens, TABELA)
    # 800 x 4% + 200 x 6% = 32 + 12
    assert r["comissao"].sum() == pytest.approx(44.0)


def test_r1_desconto_reduz_percentual():
    itens = pd.DataFrame({"id_item": ["10-1"], "id_venda": [10], "linha_produto": ["KIT_RESIDENCIAL"], "valor_bruto": [1000.0]})
    r = comissao_projetos(_baixa(desconto_pct=12), itens, TABELA)
    assert r["comissao"].sum() == pytest.approx(1000 * 0.04 * 0.6)


def test_r1_item_sem_percentual_paga_zero_mas_fica_no_rateio():
    # D2 (Opção A): instalação em PARCEIRO não tem % na tabela
    itens = pd.DataFrame({"id_item": ["10-1", "10-2"], "id_venda": [10, 10],
                          "linha_produto": ["KIT_RESIDENCIAL", "INSTALACAO"], "valor_bruto": [800.0, 200.0]})
    tabela = TABELA[TABELA["linha_produto"] == "KIT_RESIDENCIAL"]
    r = comissao_projetos(_baixa(), itens, tabela)
    assert r["comissao"].sum() == pytest.approx(800 * 0.04)  # 32, e não 40


def test_r2_so_primeira_mensalidade_com_50_por_cento():
    b = pd.DataFrame({"n_baixa": [1, 2], "id_venda": [1, 1], "competencia": ["2026-08"] * 2,
                      "parcela": [1, 2], "valor_pago": [449.90, 449.90]})
    r = comissao_assinaturas(b)
    assert list(r["comissao"]) == [224.95]


def test_r3_split_soma_fecha():
    p, v2 = dividir_valor(100.01, True)
    assert p + v2 == pytest.approx(100.01)
    assert dividir_valor(50.0, False) == (50.0, 0.0)


def _venda(dias_ate_cancel, pagamento):
    venda = pd.Timestamp("2026-06-01")
    return pd.DataFrame([{"status": "CANCELADA", "data_venda": venda,
                          "data_cancelamento": venda + pd.Timedelta(days=dias_ate_cancel),
                          "data_pagamento": pd.Timestamp(pagamento)}])


def test_r4_cancelada_ate_60_dias_zera_tudo_mesmo_pago_antes():
    assert not marcar_comissionavel(_venda(60, "2026-06-10")).loc[0, "comissionavel"]


def test_r4_cancelada_apos_60_dias_vale_ate_a_data_do_cancelamento():
    cancel = pd.Timestamp("2026-06-01") + pd.Timedelta(days=61)
    assert marcar_comissionavel(_venda(61, cancel)).loc[0, "comissionavel"]                       # no dia: vale
    assert not marcar_comissionavel(_venda(61, cancel + pd.Timedelta(days=1))).loc[0, "comissionavel"]  # depois: não


def test_r4_venda_ativa_e_comissionavel():
    b = pd.DataFrame([{"status": "ATIVA", "data_venda": pd.Timestamp("2026-06-01"),
                       "data_cancelamento": pd.NaT, "data_pagamento": pd.Timestamp("2026-08-01")}])
    assert marcar_comissionavel(b).loc[0, "comissionavel"]


@pytest.mark.parametrize("ating,bonus", [
    (0.79, 0), (0.80, 800), (0.999, 800), (1.0, 1500), (1.199, 1500), (1.2, 2500), (3.0, 2500)])
def test_r5_faixas_de_bonus(ating, bonus):
    assert bonus_por_atingimento(ating) == bonus


def test_r6_mes_de_casa_conta_o_mes_da_admissao():
    diego = pd.Timestamp("2026-07-20")
    assert [mes_de_casa(diego, c) for c in ("2026-07", "2026-09", "2026-10")] == [1, 3, 4]


def test_r6_complemento_apenas_na_rampagem_e_ate_a_garantia():
    diego = pd.Timestamp("2026-07-20")
    assert complemento(690.47, diego, "2026-08", True) == 809.53
    assert complemento(3343.07, diego, "2026-09", True) == 0.0    # acima da garantia
    assert complemento(100.0, diego, "2026-10", True) == 0.0      # 4º mês: fora da rampagem
    assert complemento(100.0, diego, "2026-08", False) == 0.0     # gerente não tem rampagem


def test_r7_override_so_em_baixa_que_gera_comissao():
    baixas = pd.DataFrame({"n_baixa": [1, 2], "id_venda": [1, 2], "competencia": ["2026-09"] * 2, "valor_pago": [1000.0, 500.0]})
    comissao = pd.DataFrame({"n_baixa": [1, 2], "comissao": [10.0, 0.0]})
    vendas = pd.DataFrame({"id_venda": [1, 2], "vendedor": ["Ana", "Ana"]})
    cadastro = pd.DataFrame({"nome": ["Ana"], "gerente": ["Marcos"]})
    r = override_gerencia(baixas, comissao, vendas, cadastro)
    assert list(r["override"]) == [10.0] and list(r["nome"]) == ["Marcos"]
