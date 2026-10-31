"""
Ejercicio 1 | Auditar un sistema de riesgo real: COMPAS (Broward County, Florida)

Qué hace este script
--------------------
1. Descarga (una sola vez) los datos públicos que ProPublica usó en "Machine Bias" (2016).
2. Aplica los mismos filtros de la metodología de ProPublica.
3. Calcula, por grupo, las métricas que explican la controversia:
   - Tasa de falsos positivos (TFP): personas que NO reincidieron y fueron marcadas como riesgo.
   - Tasa de falsos negativos (TFN): personas que SÍ reincidieron y fueron marcadas como bajo riesgo.
   - Valor predictivo positivo (VPP): de los marcados como riesgo, cuántos reincidieron.

Fuentes
-------
- Datos y filtros: ProPublica, https://github.com/propublica/compas-analysis
  (archivo compas-scores-two-years.csv y cuaderno "Compas Analysis.ipynb").
- Angwin, J., Larson, J., Mattu, S. y Kirchner, L. (2016). Machine Bias. ProPublica.
  https://www.propublica.org/article/machine-bias-risk-assessments-in-criminal-sentencing
- Larson, J. et al. (2016). How We Analyzed the COMPAS Recidivism Algorithm. ProPublica.
  https://www.propublica.org/article/how-we-analyzed-the-compas-recidivism-algorithm

Ejecución (desde la raíz del repositorio, con el entorno RAGLAB activo):
    python modulo-etica/ejercicios/01_auditoria_compas.py
"""

from pathlib import Path

import pandas as pd

URL_DATOS = (
    "https://raw.githubusercontent.com/propublica/compas-analysis/master/"
    "compas-scores-two-years.csv"
)
RUTA_LOCAL = Path(__file__).parent / "datos" / "compas-scores-two-years.csv"
GRUPOS = ["African-American", "Caucasian"]


def cargar_datos() -> pd.DataFrame:
    """Lee el CSV local; si no existe, lo descarga del repositorio de ProPublica."""
    if not RUTA_LOCAL.exists():
        print("Descargando datos de ProPublica...")
        RUTA_LOCAL.parent.mkdir(parents=True, exist_ok=True)
        pd.read_csv(URL_DATOS).to_csv(RUTA_LOCAL, index=False)
    return pd.read_csv(RUTA_LOCAL)


def filtrar_como_propublica(df: pd.DataFrame) -> pd.DataFrame:
    """Filtros de la metodología de ProPublica (celda 'Data cleaning' de su cuaderno)."""
    return df[
        (df["days_b_screening_arrest"] <= 30)
        & (df["days_b_screening_arrest"] >= -30)
        & (df["is_recid"] != -1)
        & (df["c_charge_degree"] != "O")
        & (df["score_text"] != "N/A")
    ].copy()


def metricas_por_grupo(df: pd.DataFrame, umbral: int) -> pd.DataFrame:
    """Marca 'alto riesgo' si decile_score >= umbral y compara con la reincidencia real."""
    filas = []
    for grupo, datos in df.groupby("race"):
        prediccion = datos["decile_score"] >= umbral
        real = datos["two_year_recid"] == 1
        vp = (prediccion & real).sum()
        fp = (prediccion & ~real).sum()
        fn = (~prediccion & real).sum()
        vn = (~prediccion & ~real).sum()
        filas.append(
            {
                "grupo": grupo,
                "n": len(datos),
                "tasa_base": real.mean(),
                "marcados_alto": prediccion.mean(),
                "TFP": fp / (fp + vn),
                "TFN": fn / (fn + vp),
                "VPP": vp / (vp + fp),
            }
        )
    return pd.DataFrame(filas).set_index("grupo")


def main() -> None:
    datos = filtrar_como_propublica(cargar_datos())
    datos = datos[datos["race"].isin(GRUPOS)]
    print(f"Registros después de los filtros de ProPublica: {len(datos)}\n")

    # ProPublica trató 'Medium' y 'High' (decil >= 5) como predicción de reincidencia.
    tabla = metricas_por_grupo(datos, umbral=5)
    print("Umbral único: decil >= 5 se considera 'alto riesgo'")
    print(tabla.round(3).to_string())

    brecha_fpr = tabla.loc["African-American", "TFP"] - tabla.loc["Caucasian", "TFP"]
    print(f"\nBrecha de falsos positivos, TFP (afroamericanos - blancos): {brecha_fpr:.3f}")
    print(
        "Lectura: entre quienes NO reincidieron, a las personas afroamericanas se les"
        " marcó como riesgo casi el doble de veces."
    )

    # Tabla compacta que alimenta el laboratorio interactivo de la página web.
    print("\nConteos por decil (insumo del laboratorio web):")
    conteos = (
        datos.groupby(["race", "decile_score", "two_year_recid"]).size().unstack(fill_value=0)
    )
    print(conteos.to_string())


if __name__ == "__main__":
    main()
