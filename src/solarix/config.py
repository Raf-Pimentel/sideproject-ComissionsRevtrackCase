"""Caminhos e parâmetros do case. Nenhuma regra de negócio deve ter número mágico fora daqui."""
from pathlib import Path

# Caminhos relativos à raiz do projeto, para funcionar em qualquer máquina
ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"      # originais do cliente: somente leitura
OUTPUTS = ROOT / "outputs"       # entregáveis gerados (xlsx)
DOCS = ROOT / "docs"

# Nome de cada arquivo de entrada; centralizado para trocar em um só lugar
FILES = {
    "vendas": "01_CRM_Vendas.xlsx",
    "itens": "02_CRM_Itens_da_Venda.xlsx",
    "baixas": "03_ERP_Relatorio_de_Baixas.xlsx",
    "tabela": "04_Tabela_de_Comissao.xlsx",
    "cadastro": "05_Cadastro_Comissionados.xlsx",
    "controle": "06_Controle_Comissoes_Cliente_Ago-Set.xlsx",
}

# Meses (AAAA-MM) a calcular, conforme o briefing
COMPETENCIAS = ("2026-08", "2026-09")
# Usada para detectar baixas com data posterior à emissão do relatório
ERP_EMISSAO = "2026-09-25"  # "Emitido em 25/09/2026" no cabeçalho do relatório de baixas

# ---- Parâmetros das regras (briefing). Cada um aponta a regra e, se houver, a decisão em docs/decisoes.md ----

# R1: redutor do % da tabela por desconto da venda. (limite superior inclusivo, fator). Decisão D3.
DESCONTO_FAIXAS = [(5, 1.0), (10, 0.8), (15, 0.6), (float("inf"), 0.4)]
# R2: comissão sobre a 1ª mensalidade paga
ASSINATURA_PCT = 0.50
# R3: divisão em venda conjunta
SPLIT_PRINCIPAL = 0.60
SPLIT_VENDEDOR2 = 0.40
# R4: cancelamento até N dias corridos após a venda zera tudo
PRAZO_CANCELAMENTO_DIAS = 60
# R5: (atingimento mínimo inclusivo, bônus), em ordem crescente
META_FAIXAS = [(0.0, 0.0), (0.8, 800.0), (1.0, 1500.0), (1.2, 2500.0)]
# R6: consultores nos N primeiros meses-calendário de casa (mês da admissão = 1º) têm garantia mensal
RAMPAGEM_MESES = 3
RAMPAGEM_GARANTIA = 1500.0
# R7: override do gerente sobre o valor pago das baixas comissionáveis
OVERRIDE_PCT = 0.01

# ---- Chaves de cenário (decisões abertas; alterar aqui para ver o impacto) ----
# D2 (confirmada, Opção A): item sem % na tabela (instalação em PARCEIRO) paga 0% mas continua no rateio
ITEM_SEM_PCT_ENTRA_NO_RATEIO = True
# D1 (padrão, pendente): baixas datadas após a emissão do relatório entram no cálculo
INCLUIR_BAIXAS_APOS_EMISSAO = True

# Diferença aceita entre nosso cálculo e o controle da Carla (briefing)
TOLERANCIA_RS = 1.00
