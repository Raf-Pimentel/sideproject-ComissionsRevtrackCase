"""Fechamento: aplica R1..R7 e consolida por comissionado x competência."""
import pandas as pd

from .config import COMPETENCIAS
from .model import Modelo, baixas_do_periodo
from .rules.r1_projetos import comissao_projetos
from .rules.r2_assinaturas import comissao_assinaturas
from .rules.r3_split import atribuir_comissao
from .rules.r5_meta import bonus_meta
from .rules.r6_rampagem import complemento
from .rules.r7_override import override_gerencia


def calcular(m: Modelo):
    """Devolve (fechamento, detalhe_por_baixa). O detalhe permite explicar qualquer valor do fechamento."""
    b = baixas_do_periodo(m)
    ok = b[b["comissionavel"]]  # R4 aplicada

    proj = comissao_projetos(ok[ok["tipo"] == "PROJETO"], m.itens, m.tabela)
    ass = comissao_assinaturas(ok[ok["tipo"] == "ASSINATURA"])
    # comissão total por baixa (R1 soma itens; R2 já é por baixa)
    por_baixa = pd.concat([
        proj.groupby(["n_baixa", "id_venda", "competencia"], as_index=False)["comissao"].sum(),
        ass[["n_baixa", "id_venda", "competencia", "comissao"]]])
    por_baixa["comissao"] = por_baixa["comissao"].round(2)

    pessoas = atribuir_comissao(por_baixa, m.vendas)              # R3
    comissao = pessoas.groupby(["nome", "competencia"], as_index=False)["comissao"].sum()
    over = override_gerencia(ok, por_baixa, m.vendas, m.cadastro)  # R7
    over_g = over.groupby(["nome", "competencia"], as_index=False)["override"].sum()
    meta = bonus_meta(m.vendas, m.itens, m.cadastro)              # R5 (competência = mês da venda)

    # grade completa: todo comissionado x toda competência, mesmo sem movimento
    grade = pd.MultiIndex.from_product([m.cadastro["nome"], COMPETENCIAS], names=["nome", "competencia"]).to_frame(index=False)
    f = grade.merge(comissao, how="left").merge(
        meta[["nome", "competencia", "bonus_meta"]], how="left").merge(over_g, how="left")
    f[["comissao", "bonus_meta", "override"]] = f[["comissao", "bonus_meta", "override"]].fillna(0.0)

    adm = m.cadastro.set_index("nome")["data_admissao"]
    consultor = m.cadastro.set_index("nome")["cargo"].str.startswith("Consultor")
    f["rampagem"] = [complemento(r.comissao, adm[r.nome], r.competencia, bool(consultor[r.nome]))
                     for r in f.itertuples()]  # R6 (sobre R1 + R2 pós-split, sem bônus)
    f["total"] = (f["comissao"] + f["bonus_meta"] + f["rampagem"] + f["override"]).round(2)
    return f, por_baixa
