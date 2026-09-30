"""Gera docs/calculo_<nome>.md: o cálculo de um comissionado, conta por conta, para conferência manual.
Uso: python -m solarix.reports.detalhe "Ana Ribeiro"
"""
import sys

import pandas as pd

from ..closing import calcular
from ..compare import comparar
from ..config import COMPETENCIAS, DOCS
from ..model import Modelo, baixas_do_periodo, montar
from ..rules.r1_projetos import comissao_projetos
from ..rules.r2_assinaturas import comissao_assinaturas
from ..rules.r3_split import dividir_valor
from ..rules.r5_meta import bonus_por_atingimento


def BRL(x: float) -> str:  # noqa: N802
    """Moeda no formato brasileiro: R$ 1.234,56."""
    return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def PCT(x: float) -> str:  # noqa: N802
    """Percentual com vírgula decimal."""
    return f"{x:g}%".replace(".", ",")


def DATA(d) -> str:  # noqa: N802
    return f"{d:%d/%m/%Y}"


def _secao_baixas(m: Modelo, nome: str, comp: str, out: list):
    b = baixas_do_periodo(m)
    b = b[(b["competencia"] == comp) & b["comissionavel"] & ((b["vendedor"] == nome) | (b["vendedor2"] == nome))]
    total = 0.0
    if b.empty:
        out.append("_Nenhuma baixa comissionável neste mês._\n")
        return 0.0
    proj = comissao_projetos(b[b["tipo"] == "PROJETO"], m.itens, m.tabela) if (b["tipo"] == "PROJETO").any() else None
    ass = comissao_assinaturas(b[b["tipo"] == "ASSINATURA"]) if (b["tipo"] == "ASSINATURA").any() else None
    for r in b.sort_values("data_pagamento").itertuples():
        papel = "principal" if r.vendedor == nome else "vendedor 2"
        out.append(f"### Baixa {r.n_baixa} · parcela {r.n_parcela} · {DATA(r.data_pagamento)} · venda {r.id_venda} ({r.tipo}, canal {r.canal})")
        out.append(f"Valor pago: **{BRL(r.valor_pago)}** · desconto da venda: {PCT(r.desconto_pct)} · {nome} é {papel}\n")
        if r.tipo == "PROJETO":
            itens = m.itens.set_index("id_item")["valor_bruto"]
            linhas = proj[proj["n_baixa"] == r.n_baixa]
            tot_bruto = sum(itens[i] for i in linhas["id_item"])
            out.append("| Item | Bruto | Peso (bruto do item ÷ bruto total) | Parte do pagamento que cabe ao item | % tabela | Redutor | Comissão do item |")
            out.append("|---|---|---|---|---|---|---|")
            for x in linhas.itertuples():
                out.append(f"| {x.id_item} ({x.linha_produto}) | {BRL(itens[x.id_item])} | "
                           f"{PCT(round(itens[x.id_item] / tot_bruto * 100, 2))} | "
                           f"{BRL(r.valor_pago)} × {BRL(itens[x.id_item])} / {BRL(tot_bruto)} = {BRL(x.base_item)} | "
                           f"{PCT(x.pct_comissao)} | {PCT(x.redutor * 100)} | {BRL(x.base_item)} × {PCT(x.pct_comissao)} × {PCT(x.redutor * 100)} = **{BRL(x.comissao)}** |")
            com = round(linhas["comissao"].sum(), 2)
            out.append(f"\nComissão da baixa (soma dos itens): **{BRL(com)}**")
        else:
            com = float(ass.loc[ass["n_baixa"] == r.n_baixa, "comissao"].sum()) if r.parcela == 1 else 0.0
            if r.parcela == 1:
                out.append(f"Assinatura, 1ª mensalidade: {BRL(r.valor_pago)} × 50% = **{BRL(com)}**")
            else:
                out.append(f"Assinatura, parcela {r.parcela}: só a 1ª mensalidade comissiona, então **{BRL(0)}**")
        principal, v2 = dividir_valor(com, pd.notna(r.vendedor2))
        if pd.notna(r.vendedor2):
            minha = principal if papel == "principal" else v2
            out.append(f"Venda conjunta ({r.vendedor} 60% / {r.vendedor2} 40%): parte de {nome} = **{BRL(minha)}**")
        else:
            minha = com
            out.append(f"Sem venda conjunta: {nome} fica com 100% = **{BRL(minha)}**")
        out.append("")
        total += minha
    return round(total, 2)


def _secao_meta(m: Modelo, nome: str, comp: str, out: list):
    meta = m.cadastro.set_index("nome")["meta_mensal"].get(nome)
    if pd.isna(meta):
        out.append("_Sem meta (gerente): não há bônus de meta._\n")
        return
    bruto = m.itens.groupby("id_venda")["valor_bruto"].sum()
    v = m.vendas[(m.vendas["tipo"] == "PROJETO") & (m.vendas["status"] != "CANCELADA")
                 & (m.vendas["data_venda"].dt.strftime("%Y-%m") == comp)
                 & ((m.vendas["vendedor"] == nome) | (m.vendas["vendedor2"] == nome))]
    out.append("| Venda | Data | Bruto | Desconto | Líquido | Parte de " + nome + " |")
    out.append("|---|---|---|---|---|---|")
    soma = 0.0
    for r in v.sort_values("data_venda").itertuples():
        liq = bruto[r.id_venda] * (1 - r.desconto_pct / 100)
        p, v2 = dividir_valor(liq, pd.notna(r.vendedor2))
        parte = p if r.vendedor == nome else v2
        soma += parte
        out.append(f"| {r.id_venda} | {DATA(r.data_venda)} | {BRL(bruto[r.id_venda])} | {PCT(r.desconto_pct)} | {BRL(liq)} | {BRL(parte)}"
                   f"{' (60/40)' if pd.notna(r.vendedor2) else ''} |")
    ating = soma / meta
    out.append(f"\nTotal vendido (líquido): **{BRL(soma)}** · meta: {BRL(meta)} · atingimento: {BRL(soma)} / {BRL(meta)} = "
               f"**{PCT(round(ating * 100, 2))}** · bônus: **{BRL(bonus_por_atingimento(ating))}**\n")


def gerar(nome: str) -> str:
    m = montar()
    fech, _ = calcular(m)
    comp = comparar(fech, m.controle).set_index(["nome", "competencia"])
    out = [f"# Cálculo detalhado: {nome}", "",
           "Gerado por `python -m solarix.reports.detalhe`. Regras: R1 (projetos), R2 (assinaturas), R3 (split), R4 (cancelamento), R5 (meta), R6 (rampagem), R7 (override).", ""]
    for c in COMPETENCIAS:
        out += [f"## Competência {c}", "", "### Comissão sobre vendas (regime de caixa: mês da data de pagamento)", ""]
        total_com = _secao_baixas(m, nome, c, out)
        out += [f"**Comissão sobre vendas de {c}: {BRL(total_com)}**", "", "### Bônus de meta (mês da data da venda)", ""]
        _secao_meta(m, nome, c, out)
        r = comp.loc[(nome, c)]
        out += ["### Fechamento do mês", "",
                "| Componente | Nosso | Carla | Diferença |", "|---|---|---|---|"]
        for k, rot in [("comissao", "Comissão s/ vendas"), ("bonus_meta", "Bônus de meta"), ("rampagem", "Complemento de rampagem"),
                       ("override", "Override"), ("total", "**Total**")]:
            out.append(f"| {rot} | {BRL(r[k + '_nosso'])} | {BRL(r[k + '_carla'])} | {BRL(r[k + '_dif'])} |")
        out.append("")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    nome = sys.argv[1] if len(sys.argv) > 1 else "Ana Ribeiro"
    DOCS.mkdir(parents=True, exist_ok=True)
    arq = DOCS / f"calculo_{nome.lower().replace(' ', '_')}.md"
    arq.write_text(gerar(nome), encoding="utf-8")
    print(arq)
