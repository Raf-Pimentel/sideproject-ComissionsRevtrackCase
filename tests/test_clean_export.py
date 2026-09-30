"""Testes das bases limpas: a validação precisa passar nos dados reais e pegar cada tipo de erro."""
import pandas as pd
import pytest

from solarix.clean_export import preparar, validar


@pytest.fixture()
def bases():
    return preparar()


def test_bases_limpas_nao_tem_erros(bases):
    assert validar(bases) == []


def test_nomes_do_joao_pedro_foram_unificados(bases):
    nomes = set(bases["vendas"]["vendedor"]) | set(bases["vendas"]["vendedor2"].dropna())
    assert nomes <= set(bases["cadastro"]["nome"])


def test_tabela_tem_linha_explicita_da_instalacao_parceiro(bases):
    t = bases["tabela_comissao"]
    linha = t[(t["linha_produto"] == "INSTALACAO") & (t["canal"] == "PARCEIRO")]
    assert len(linha) == 1 and linha["pct_comissao"].iloc[0] == 0.0


def test_quantidade_de_linhas_bate_com_os_arquivos_originais(bases):
    assert {k: len(v) for k, v in bases.items()} == {
        "vendas": 60, "itens": 89, "baixas": 115, "tabela_comissao": 12, "cadastro": 8, "controle_carla": 16}


def test_validacao_pega_chave_duplicada(bases):
    bases["vendas"] = pd.concat([bases["vendas"], bases["vendas"].iloc[[0]]], ignore_index=True)
    assert any("chave duplicada" in e for e in validar(bases))


def test_validacao_pega_espaco_sobrando(bases):
    bases["vendas"].loc[0, "vendedor"] = "Ana Ribeiro "
    erros = validar(bases)
    assert any("espaços sobrando" in e for e in erros) and any("fora do cadastro" in e for e in erros)


def test_validacao_pega_item_sem_percentual(bases):
    t = bases["tabela_comissao"]
    bases["tabela_comissao"] = t[~((t["linha_produto"] == "INSTALACAO") & (t["canal"] == "PARCEIRO"))]
    assert any("sem % na tabela_comissao" in e for e in validar(bases))


def test_validacao_pega_baixa_sem_venda(bases):
    bases["baixas"].loc[0, "id_venda"] = 9999
    assert any("id_venda inexistente" in e for e in validar(bases))


def test_validacao_pega_cancelamento_sem_data(bases):
    bases["vendas"].loc[bases["vendas"]["status"] == "CANCELADA", "data_cancelamento"] = None
    assert any("data_cancelamento" in e for e in validar(bases))
