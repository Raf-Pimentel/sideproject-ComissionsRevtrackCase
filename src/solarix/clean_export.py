"""Gera data/clean/: as bases tratadas, prontas para subir na RevTrack, depois de validadas.

Só corrige erros de formato e de cadastro (nomes, espaços, tipos). Não calcula nada: rateio, competência,
split etc. são colunas calculadas da plataforma. Uso: python -m solarix.clean_export
"""
import pandas as pd

from .clean import clean_names
from .config import CLEAN
from .load import load_baixas, load_cadastro, load_controle, load_itens, load_tabela, load_vendas

# Colunas de cada base, na ordem de saída
COLUNAS = {
    "vendas": ["id_venda", "tipo", "data_venda", "cliente", "vendedor", "vendedor2", "canal", "desconto_pct", "status",
               "data_cancelamento"],
    "itens": ["id_item", "id_venda", "linha_produto", "descricao", "valor_bruto"],
    "baixas": ["n_baixa", "n_parcela", "id_venda", "parcela", "total_parcelas", "valor_parcela", "valor_pago", "data_pagamento"],
    "tabela_comissao": ["linha_produto", "canal", "pct_comissao", "observacao"],
    "cadastro": ["nome", "cargo", "equipe", "gerente", "data_admissao", "meta_mensal", "email"],
    "controle_carla": ["nome", "competencia", "comissao", "bonus_meta", "rampagem", "override", "total"],
}
ARQUIVO = {k: f"{i + 1:02d}_{k}" for i, k in enumerate(COLUNAS)}

# D2 (Opção A): a tabela original não tem instalação em PARCEIRO. A linha explícita com 0% evita
# que o join da plataforma devolva nulo e deixa a decisão visível.
LINHA_ADICIONADA = {
    "linha_produto": "INSTALACAO", "canal": "PARCEIRO", "pct_comissao": 0.0,
    "observacao": ("Linha ADICIONADA (não existe na tabela do cliente): instalação no canal PARCEIRO "
                   "é feita pelo parceiro; 0% (decisão D2)")}


def _limpar_texto(df: pd.DataFrame) -> pd.DataFrame:
    """Remove espaços nas pontas e normaliza espaços repetidos em todas as colunas de texto."""
    df = df.copy()
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].map(lambda x: " ".join(x.split()) if isinstance(x, str) else x)
    return df


def preparar() -> dict[str, pd.DataFrame]:
    """Carrega os brutos, corrige o que for erro e devolve as bases limpas."""
    cadastro, vendas = load_cadastro(), load_vendas()
    vendas, controle, _ = clean_names(vendas, cadastro, load_controle())
    tabela = pd.concat([load_tabela(), pd.DataFrame([LINHA_ADICIONADA])], ignore_index=True)
    bases = {"vendas": vendas, "itens": load_itens(), "baixas": load_baixas(), "tabela_comissao": tabela,
             "cadastro": cadastro, "controle_carla": controle}
    return {k: _limpar_texto(v)[COLUNAS[k]] for k, v in bases.items()}


def validar(d: dict[str, pd.DataFrame]) -> list[str]:
    """Devolve a lista de erros encontrados (vazia = bases prontas para subir)."""
    erros = []
    v, it, b, t, c = d["vendas"], d["itens"], d["baixas"], d["tabela_comissao"], d["cadastro"]

    # chaves únicas
    for nome, df, chave in [("vendas", v, ["id_venda"]), ("itens", it, ["id_item"]), ("baixas", b, ["n_baixa"]),
                            ("tabela_comissao", t, ["linha_produto", "canal"]), ("cadastro", c, ["nome"])]:
        if df.duplicated(chave).any():
            erros.append(f"{nome}: chave duplicada {chave}")

    # obrigatórios
    obrig = {"vendas": ["id_venda", "tipo", "data_venda", "cliente", "vendedor", "canal", "desconto_pct", "status"],
             "itens": COLUNAS["itens"], "baixas": COLUNAS["baixas"],
             "tabela_comissao": ["linha_produto", "canal", "pct_comissao"],
             "cadastro": ["nome", "cargo", "equipe", "data_admissao", "email"]}
    for nome, cols in obrig.items():
        for col in cols:
            if d[nome][col].isna().any():
                erros.append(f"{nome}.{col}: {int(d[nome][col].isna().sum())} valores vazios")
    if (v["status"].eq("CANCELADA") != v["data_cancelamento"].notna()).any():
        erros.append("vendas: data_cancelamento deve existir exatamente nas vendas CANCELADA")
    consult = c["cargo"].str.startswith("Consultor")
    if c.loc[consult, "meta_mensal"].isna().any():
        erros.append("cadastro: consultor sem meta_mensal")

    # domínios
    dominios = [("tipo", {"PROJETO", "ASSINATURA"}), ("canal", {"DIRETO", "PARCEIRO", "INDICACAO"}),
                ("status", {"ATIVA", "CANCELADA"})]
    for col, validos in dominios:
        ruins = set(v[col]) - validos
        if ruins:
            erros.append(f"vendas.{col}: valores fora do domínio {sorted(ruins)}")
    if not v["desconto_pct"].between(0, 100).all():
        erros.append("vendas.desconto_pct fora de 0..100")
    if (it["valor_bruto"] <= 0).any() or (b["valor_pago"] <= 0).any() or (b["valor_parcela"] <= 0).any():
        erros.append("valores monetários devem ser positivos")

    # integridade referencial
    if set(b["id_venda"]) - set(v["id_venda"]):
        erros.append("baixas: id_venda inexistente em vendas")
    if set(it["id_venda"]) ^ set(v["id_venda"]):
        erros.append("vendas/itens: venda sem item ou item sem venda")
    pessoas = set(c["nome"])
    if (set(v["vendedor"]) | set(v["vendedor2"].dropna()) | set(c["gerente"].dropna())) - pessoas:
        erros.append("vendas/cadastro: nome de pessoa fora do cadastro")
    usados = it.merge(v[["id_venda", "canal"]], on="id_venda")[["linha_produto", "canal"]].drop_duplicates()
    sem_pct = set(map(tuple, usados.values)) - set(map(tuple, t[["linha_produto", "canal"]].values))
    if sem_pct:
        erros.append(f"itens sem % na tabela_comissao: {sorted(sem_pct)}")

    # consistência interna
    if (b["n_parcela"] != b["id_venda"].astype(str) + "-P" + b["parcela"].astype(str).str.zfill(2)).any():
        erros.append("baixas: n_parcela não corresponde a id_venda + parcela")
    if (b["parcela"] > b["total_parcelas"]).any():
        erros.append("baixas: parcela maior que total_parcelas")
    pago = b.groupby(["id_venda", "parcela"]).agg(pago=("valor_pago", "sum"), parc=("valor_parcela", "first"))
    if (pago["pago"] > pago["parc"] + 0.011).any():
        erros.append("baixas: pagamentos de uma parcela somam mais que o valor da parcela")
    tipos = it.merge(v[["id_venda", "tipo"]], on="id_venda")
    if ((tipos["tipo"] == "ASSINATURA") != (tipos["linha_produto"] == "MONITORAMENTO")).any():
        erros.append("itens: MONITORAMENTO deve existir só em vendas ASSINATURA")
    m = b.merge(v[["id_venda", "data_venda", "data_cancelamento"]], on="id_venda")
    if (m["data_pagamento"] < m["data_venda"]).any():
        erros.append("baixas: pagamento antes da data da venda")
    if (v["data_cancelamento"] < v["data_venda"]).any():
        erros.append("vendas: cancelamento antes da venda")

    # espaços sobrando em qualquer texto
    for nome, df in d.items():
        for col in df.select_dtypes(include=["object", "string"]).columns:
            s = df[col].dropna()
            if (s != s.map(lambda x: " ".join(x.split()))).any():
                erros.append(f"{nome}.{col}: espaços sobrando")
    return erros


def gravar(d: dict[str, pd.DataFrame], pasta=CLEAN):
    """Um CSV por base (UTF-8, vírgula, ponto decimal, datas AAAA-MM-DD)."""
    pasta.mkdir(parents=True, exist_ok=True)
    for nome, df in d.items():
        df.to_csv(pasta / f"{ARQUIVO[nome]}.csv", index=False, encoding="utf-8", date_format="%Y-%m-%d")


def main():
    d = preparar()
    erros = validar(d)
    if erros:
        raise SystemExit("Bases com erro, nada foi gravado:\n- " + "\n- ".join(erros))
    gravar(d)
    for nome, df in d.items():
        print(f"{ARQUIVO[nome]}: {len(df)} linhas, {len(df.columns)} colunas")
    print("Validação: 0 erros")


if __name__ == "__main__":
    main()
