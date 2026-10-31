"""
Ejercicio 2 | Problema -> sin ajuste -> con ajuste: mitigar sesgo en tres etapas

Entrenamos nuestro propio clasificador de reincidencia con los datos de ProPublica
(sin usar la variable raza como entrada) y comparamos cuatro versiones:

    0. Sin ajuste           : regresión logística, umbral 0.5 para todos.
    1. Datos (antes)        : reponderación (Kamiran y Calders, 2012; "Reweighing" en AIF360). Repondera los ejemplos
                              para que grupo y etiqueta sean independientes en el entrenamiento.
    2. Modelo (al entrenar) : gradiente exponenciado (ExponentiatedGradient en Fairlearn) con restricción de paridad en la tasa
                              de falsos positivos (Agarwal et al., 2018). Requiere fairlearn.
                              Ojo: produce un clasificador aleatorizado (mezcla de modelos).
    3. Decisión (después)   : umbrales por grupo para igualar la tasa de falsos positivos
                              (idea de Hardt, Price y Srebro, 2016).

Referencias
-----------
- Kamiran, F. y Calders, T. (2012). Data preprocessing techniques for classification without
  discrimination. Knowledge and Information Systems, 33(1), 1-33. doi:10.1007/s10115-011-0463-8
- Agarwal, A. et al. (2018). A Reductions Approach to Fair Classification. ICML, PMLR 80:60-69.
- Hardt, M., Price, E. y Srebro, N. (2016). Equality of Opportunity in Supervised Learning.
  NeurIPS 29. arXiv:1610.02413
- Fairlearn (Weerts et al., 2023, JMLR 24(257)): https://fairlearn.org
  La etapa 2 sigue el uso documentado de fairlearn.reductions.ExponentiatedGradient.

Ejecución:
    python modulo-etica/ejercicios/02_mitigacion_compas.py
    (Opcional, para la etapa 2: pip install fairlearn)

Nota ética: este ejercicio es pedagógico. Igualar una métrica casi siempre empeora otra
(Chouldechova, 2017; Kleinberg et al., 2017). La pregunta de fondo no es técnica:
¿qué error es más grave en este contexto y quién decide?
"""

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).parent))
from importlib import import_module  # noqa: E402

auditoria = import_module("01_auditoria_compas")

VARIABLES = [
    "age",
    "priors_count",
    "juv_fel_count",
    "juv_misd_count",
    "juv_other_count",
    "es_mujer",
    "delito_grave",
]
GRUPO_A, GRUPO_B = "African-American", "Caucasian"


def preparar() -> tuple:
    df = auditoria.filtrar_como_propublica(auditoria.cargar_datos())
    df = df[df["race"].isin([GRUPO_A, GRUPO_B])].copy()
    df["es_mujer"] = (df["sex"] == "Female").astype(int)
    df["delito_grave"] = (df["c_charge_degree"] == "F").astype(int)
    X = df[VARIABLES]
    y = df["two_year_recid"].to_numpy()
    grupo = df["race"].to_numpy()
    return train_test_split(X, y, grupo, test_size=0.3, random_state=42, stratify=y)


def modelo_base():
    return make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))


def resumen(nombre: str, y: np.ndarray, pred: np.ndarray, grupo: np.ndarray) -> dict:
    fila = {"versión": nombre, "exactitud": (pred == y).mean()}
    for g, etiqueta in [(GRUPO_A, "afro"), (GRUPO_B, "blanco")]:
        m = grupo == g
        neg, pos = (y[m] == 0), (y[m] == 1)
        fila[f"TFP_{etiqueta}"] = pred[m][neg].mean()
        fila[f"TFN_{etiqueta}"] = 1 - pred[m][pos].mean()
    fila["brecha_TFP"] = fila["TFP_afro"] - fila["TFP_blanco"]
    fila["brecha_TFN"] = fila["TFN_afro"] - fila["TFN_blanco"]
    return fila


def pesos_reweighing(y: np.ndarray, grupo: np.ndarray) -> np.ndarray:
    """w(g, y) = P(g) * P(y) / P(g, y)  (Kamiran y Calders, 2012)."""
    w = np.empty(len(y))
    for g in np.unique(grupo):
        for etiqueta in (0, 1):
            m = (grupo == g) & (y == etiqueta)
            w[m] = (grupo == g).mean() * (y == etiqueta).mean() / m.mean()
    return w


def umbrales_por_grupo(prob, y, grupo, fpr_objetivo: float) -> dict:
    """Para cada grupo, el umbral más bajo cuya TFP en entrenamiento no supera el objetivo."""
    umbrales = {}
    for g in np.unique(grupo):
        negativos = np.sort(prob[(grupo == g) & (y == 0)])
        k = int(np.floor((1 - fpr_objetivo) * len(negativos)))
        umbrales[g] = negativos[min(k, len(negativos) - 1)]
    return umbrales


def main() -> None:
    X_tr, X_te, y_tr, y_te, g_tr, g_te = preparar()
    filas = []

    # 0. Sin ajuste
    base = modelo_base().fit(X_tr, y_tr)
    filas.append(resumen("0. Sin ajuste", y_te, base.predict(X_te), g_te))

    # 1. Datos (antes de entrenar): reponderación
    pesos = pesos_reweighing(y_tr, g_tr)
    rew = modelo_base().fit(X_tr, y_tr, logisticregression__sample_weight=pesos)
    filas.append(resumen("1. Datos: reponderación", y_te, rew.predict(X_te), g_te))

    # 2. Modelo (al entrenar): restricción durante el entrenamiento (fairlearn)
    if importlib.util.find_spec("fairlearn"):
        from fairlearn.reductions import ExponentiatedGradient, FalsePositiveRateParity

        X_tr_s = StandardScaler().fit(X_tr)
        mitigador = ExponentiatedGradient(
            LogisticRegression(max_iter=1000), constraints=FalsePositiveRateParity()
        )
        mitigador.fit(X_tr_s.transform(X_tr), y_tr, sensitive_features=g_tr)
        pred = mitigador.predict(X_tr_s.transform(X_te), random_state=42)
        filas.append(resumen("2. Modelo: gradiente exp.", y_te, np.asarray(pred), g_te))
    else:
        print("[fairlearn no instalado: se omite la etapa 2. Instálalo con pip install fairlearn]")

    # 3. Decisión (después de entrenar): umbrales por grupo para igualar la TFP
    #    (fairlearn.postprocessing.ThresholdOptimizer automatiza esta idea).
    prob_tr = base.predict_proba(X_tr)[:, 1]
    fpr_global = (prob_tr[y_tr == 0] >= 0.5).mean()
    umbrales = umbrales_por_grupo(prob_tr, y_tr, g_tr, fpr_global)
    prob_te = base.predict_proba(X_te)[:, 1]
    pred_post = np.array([p >= umbrales[g] for p, g in zip(prob_te, g_te)]).astype(int)
    filas.append(resumen("3. Decisión: umbral/grupo", y_te, pred_post, g_te))

    tabla = pd.DataFrame(filas).set_index("versión")
    pd.set_option("display.width", 140)
    print("\nResultados en el conjunto de prueba (30 %). TFP = tasa de falsos positivos; TFN = tasa de falsos negativos:\n")
    print(tabla.round(3).to_string())
    print(
        "\nUmbrales de la etapa 3:",
        {g: round(float(u), 3) for g, u in umbrales.items()},
    )
    print(
        "\nPara discutir: ¿cuál brecha se cerró, cuál se abrió y cuánto costó en exactitud?"
        "\n¿Es aceptable usar un umbral distinto según el grupo? ¿Quién debería decidirlo?"
    )


if __name__ == "__main__":
    main()
