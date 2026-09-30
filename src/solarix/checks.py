"""Verificações de integridade e qualidade. Cada função devolve uma lista de Anomaly; nenhuma altera dados."""
import pandas as pd

from .clean import Anomaly
from .config import ERP_EMISSAO


def _ids(s):
    """Lista ordenada de ints (converte tipos numpy para exibição/serialização)."""
    return sorted(int(x) for x in s)


def check_baixas(baixas, vendas):
    """Consistência das baixas do ERP entre si e contra o CRM."""
    out = []
    emit = pd.Timestamp(ERP_EMISSAO)

    # Pagamento "no futuro" em relação à emissão do relatório
    fut =baixas[baixas["data_pagamento"] > emit]
    if len(fut):
        out.append(Anomaly(
            "B01", "ALTA", "03_ERP_Baixas", "Baixas com data posterior à emissão do relatório",
            f"Relatório 'emitido em 25/09/2026', mas {len(fut)} baixas têm pagamento de 26 a 30/09 "
            f"(soma R$ {fut['valor_pago'].sum():,.2f}). Afeta só a competência set/2026.",
            "Mantidas no cálculo (cenário base); impacto isolado no fechamento.",
            "Essas baixas são previstas/agendadas ou realizadas? A data de emissão está correta?",
            rows=fut["n_baixa"].tolist()))

    # A numeração do ERP é sequencial (50001..50115); número fora da faixa sugere lançamento manual
    odd = baixas[(baixas["n_baixa"] < 50001) | (baixas["n_baixa"] > 50115)]
    if len(odd):
        r = odd.iloc[0]
        canc = vendas.set_index("id_venda").loc[r["id_venda"], "data_cancelamento"]
        out.append(Anomaly(
            "B02", "MEDIA", "03_ERP_Baixas", "Nº de baixa fora da sequência",
            f"Baixa {r['n_baixa']} ({r['n_parcela']}, {r['data_pagamento']:%d/%m/%Y}, R$ {r['valor_pago']:,.2f}) "
            f"foge da numeração 50001–50115; a venda foi cancelada em {canc:%d/%m/%Y}, antes do pagamento.",
            "Mantida no dado; a regra R4 exclui por ser posterior ao cancelamento.",
            "Por que houve pagamento após o cancelamento? Foi estornado ou é um lançamento manual?",
            rows=odd["n_baixa"].tolist()))

    # Baixas depois do cancelamento (a de numeração atípica já foi reportada em B02)
    canc = vendas[vendas["status"] == "CANCELADA"].set_index("id_venda")
    post =baixas[baixas["id_venda"].isin(canc.index)].copy()
    post["canc"] = post["id_venda"].map(canc["data_cancelamento"])
    post = post[(post["data_pagamento"] > post["canc"]) & ~post["n_baixa"].isin(odd["n_baixa"])]
    if len(post):
        out.append(Anomaly(
            "B03", "MEDIA", "03_ERP_Baixas", "Pagamentos posteriores ao cancelamento da venda",
            f"{len(post)} baixa(s) de venda cancelada com data depois do cancelamento: "
            + "; ".join(f"{r.n_parcela} em {r.data_pagamento:%d/%m/%Y} (cancel. {r.canc:%d/%m/%Y})" for r in post.itertuples()),
            "R4: cancelamento em até 60 dias zera tudo; depois de 60 dias só contam baixas até a data do cancelamento.",
            "Confirmar se esses valores foram devolvidos ao cliente.", rows=post["n_baixa"].tolist()))

    # Agrega por parcela: uma parcela pode ter várias baixas (pagamento fracionado)
    parc = baixas.groupby(["id_venda", "parcela"]).agg(
        n=("n_baixa", "size"), parcela_valor=("valor_parcela", "first"), pago=("valor_pago", "sum")).reset_index()
    split = parc[parc["n"] > 1]
    if len(split):
        out.append(Anomaly(
            "B04", "INFO", "03_ERP_Baixas", "Parcelas pagas em mais de uma baixa",
            f"{len(split)} parcelas com 2+ baixas: " + ", ".join(f"{r.id_venda}-P{r.parcela:02d}" for r in split.itertuples())
            + ". As baixas de uma mesma parcela podem cair em meses diferentes.",
            "Cada baixa é comissionada na competência da própria data de pagamento (regime de caixa).",
            rows=_ids(split["id_venda"].unique())))
    # Tolerância de 1 centavo (+0.011) para não acusar diferença de arredondamento como saldo aberto
    short = parc[parc["pago"] + 0.011 < parc["parcela_valor"]]
    if len(short):
        out.append(Anomaly(
            "B05", "MEDIA", "03_ERP_Baixas", "Parcela paga a menor (saldo em aberto)",
            "; ".join(f"{r.id_venda}-P{r.parcela:02d}: pago R$ {r.pago:,.2f} de R$ {r.parcela_valor:,.2f}" for r in short.itertuples()),
            "Comissão sobre o valor efetivamente pago (R1).",
            "Confirmar que o saldo segue em aberto e não é perdão de dívida.", rows=_ids(short["id_venda"].unique())))

    sem = vendas[~vendas["id_venda"].isin(baixas["id_venda"])]
    if len(sem):
        out.append(Anomaly(
            "B06", "BAIXA", "01 x 03", "Vendas sem nenhuma baixa no ERP",
            "; ".join(f"{r.id_venda} ({r.tipo}, {r.data_venda:%d/%m/%Y})" for r in sem.itertuples()),
            "Sem baixa não há comissão de caixa; PROJETOS entram na meta (R5).",
            "Confirmar que são vendas ainda sem recebimento. Atenção às antigas: "
            + ", ".join(f"{r.id_venda} ({r.data_venda:%d/%m})" for r in sem.itertuples()
                        if (pd.Timestamp(ERP_EMISSAO) - r.data_venda).days > 30)
            + " estão há mais de 30 dias sem nenhuma baixa.", rows=_ids(sem["id_venda"])))
    return out


def check_tabela(itens, vendas, tabela):
    """Cobertura da tabela de comissão sobre os itens vendidos."""
    out = []
    # left join: item sem linha na tabela fica com % nulo e é reportado
    m =itens.merge(vendas[["id_venda", "canal", "vendedor"]], on="id_venda").merge(
        tabela, on=["linha_produto", "canal"], how="left")
    miss = m[m["pct_comissao"].isna()]
    if len(miss):
        out.append(Anomaly(
            "T01", "ALTA", "04_Tabela x 01/02", "Item sem % na tabela de comissão",
            "; ".join(f"item {r.id_item} ({r.linha_produto} / {r.canal}, R$ {r.valor_bruto:,.2f}, {r.vendedor})" for r in miss.itertuples())
            + ". Observação da tabela: 'No canal PARCEIRO a instalação é feita pelo parceiro'.",
            "Item comissionado a 0%, mas mantido no denominador do rateio (R1 rateia pelo bruto de todos os itens).",
            "Instalação em venda PARCEIRO não gera comissão? O item deve entrar no rateio?",
            rows=_ids(miss["id_venda"].unique())))
    mon = tabela[tabela["linha_produto"] == "MONITORAMENTO"]
    out.append(Anomaly(
        "T02", "MEDIA", "04_Tabela x briefing", "Monitoramento aparece como 50% na tabela e em R2",
        f"A tabela tem {len(mon)} linhas de MONITORAMENTO a 50% ('somente sobre a 1ª mensalidade paga') e a regra R2 diz o mesmo. Risco de aplicar duas vezes.",
        "Aplicar 50% uma única vez, só na parcela 1; R1 (rateio/redutor) fica restrito a PROJETO."))
    return out


def check_vendas(vendas, itens, cadastro):
    """Integridade do cabeçalho de vendas e registro dos casos que acionam regras (R3, R4, R1)."""
    out = []
    dup =vendas[vendas["id_venda"].duplicated(keep=False)]
    if len(dup):
        out.append(Anomaly("V01", "ALTA", "01_CRM_Vendas", "ID de venda duplicado", str(_ids(dup["id_venda"].unique())), "Revisar."))
    orfa = set(itens["id_venda"]) ^ set(vendas["id_venda"])
    if orfa:
        out.append(Anomaly("V02", "ALTA", "01 x 02", "Venda sem item ou item sem venda", str(sorted(orfa)), "Revisar."))

    # R4: dias corridos entre venda e cancelamento definem o tratamento
    c = vendas[vendas["status"] == "CANCELADA"].copy()
    c["dias"] = (c["data_cancelamento"] - c["data_venda"]).dt.days
    out.append(Anomaly(
        "V03", "INFO", "01_CRM_Vendas", "Vendas canceladas (R4)",
        "; ".join(f"{r.id_venda}: venda {r.data_venda:%d/%m}, cancelada {r.data_cancelamento:%d/%m} = {r.dias} dias "
                  f"-> {'até 60 dias: zera tudo' if r.dias <= 60 else 'após 60 dias: vale até a data do cancelamento'}"
                  for r in c.itertuples()),
        "Aplicado conforme R4 (dias = cancelamento − venda; ≤ 60 zera).", rows=_ids(c["id_venda"])))

    # Descontos exatamente no limite de faixa são o ponto ambíguo de R1 (< vs <=)
    proj = vendas[vendas["tipo"] == "PROJETO"]
    lim = proj[proj["desconto_pct"].isin([5, 10, 15])]
    out.append(Anomaly(
        "V04", "INFO", "01_CRM_Vendas", "Descontos exatamente nos limites das faixas (5/10/15%)",
        f"{len(lim)} projetos: 5% = {int((lim.desconto_pct == 5).sum())}, 10% = {int((lim.desconto_pct == 10).sum())}, "
        f"15% = {int((lim.desconto_pct == 15).sum())}.",
        "Limite superior inclusivo (5% => 100%; 10% => 80%; 15% => 60%), como no texto 'até 5% (inclusive)'.",
        "Confirmar que 10% e 15% também são inclusivos.", rows=_ids(lim["id_venda"])))

    conj = vendas[vendas["vendedor2"].notna()]
    out.append(Anomaly(
        "V05", "INFO", "01_CRM_Vendas", "Vendas conjuntas",
        "; ".join(f"{r.id_venda}: {r.vendedor} + {r.vendedor2}" for r in conj.itertuples()),
        "Split 60/40 (R3), incluindo meta (R5). Override (R7) usa só a equipe do vendedor principal.",
        rows=_ids(conj["id_venda"])))

    # Venda antes da admissão indicaria vendedor errado no CRM
    adm = cadastro.set_index("nome")["data_admissao"]
    x = vendas.assign(adm=vendas["vendedor"].map(adm))
    ant = x[x["data_venda"] < x["adm"]]
    if len(ant):
        out.append(Anomaly("V06", "ALTA", "01 x 05", "Venda anterior à admissão do vendedor", str(_ids(ant["id_venda"])), "Revisar."))
    return out


def check_cadastro(cadastro):
    """Registra o perfil do time que aciona R6 (rampagem) e R7 (override)."""
    out = []
    ger = cadastro[cadastro["cargo"].str.contains("Gerente")]
    out.append(Anomaly(
        "C01", "INFO", "05_Cadastro", "Gerentes sem meta e sem vendas",
        ", ".join(ger["nome"]) + " não têm meta e não aparecem como vendedores; recebem só override (R7).",
        "Tratados como gerentes puros."))
    ramp = cadastro[cadastro["cargo"].str.contains("Júnior")]
    out.append(Anomaly(
        "C02", "INFO", "05_Cadastro", "Consultores em rampagem (R6)",
        "; ".join(f"{r.nome} (admissão {r.data_admissao:%d/%m/%Y})" for r in ramp.itertuples())
        + ". Mês de admissão = 1º mês: Diego = jul, ago, set; Érica = ago, set, out.",
        "Ambos elegíveis em ago e set/2026."))
    return out
