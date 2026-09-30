"""Executa o pipeline completo. Uso: python -m solarix.run"""
from .closing import calcular
from .compare import COMPONENTES, comparar
from .config import OUTPUTS
from .export import exportar_fechamento
from .model import montar


def main():
    m = montar()
    fech, por_baixa = calcular(m)
    comp = comparar(fech, m.controle)
    OUTPUTS.mkdir(exist_ok=True)
    # o detalhe por baixa vai na 2ª aba do xlsx (não há csv separado)
    exportar_fechamento(comp, por_baixa, OUTPUTS / "fechamento_solarix.xlsx")

    print(f"{int(comp['bateu'].sum())} de {len(comp)} linhas batem (tolerância R$ 1,00)\n")
    cols = ["nome", "competencia"] + [f"{k}_dif" for k in COMPONENTES]
    print(comp.loc[~comp["bateu"], cols].to_string(index=False))


if __name__ == "__main__":
    main()
