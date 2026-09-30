"""Executa o pipeline completo. Uso: python -m solarix.run"""
from .closing import calcular
from .compare import COMPONENTES, comparar
from .config import ROOT
from .export import exportar_fechamento
from .model import montar

OUT = ROOT / "outputs"


def main():
    m = montar()
    fech, por_baixa = calcular(m)
    comp = comparar(fech, m.controle)
    OUT.mkdir(exist_ok=True)
    comp.to_csv(OUT / "comparacao.csv", index=False, encoding="utf-8-sig")
    por_baixa.to_csv(OUT / "comissao_por_baixa.csv", index=False, encoding="utf-8-sig")
    exportar_fechamento(comp, por_baixa, OUT / "fechamento_solarix.xlsx")

    print(f"{int(comp['bateu'].sum())} de {len(comp)} linhas batem (tolerância R$ 1,00)\n")
    cols = ["nome", "competencia"] + [f"{k}_dif" for k in COMPONENTES]
    print(comp.loc[~comp["bateu"], cols].to_string(index=False))


if __name__ == "__main__":
    main()
