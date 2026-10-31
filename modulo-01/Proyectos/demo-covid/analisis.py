"""Analiza casos COVID-19 de Boyacá y genera un tablero HTML con gráficos agregados."""

from __future__ import annotations

import html
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
CSV_PATH = (
    ROOT
    / "modulo-01"
    / "Proyectos"
    / "Casos_positivos_de_COVID-19_en_Colombia._20261031.csv"
)
OUTPUT_DIR = ROOT / "docs" / "proyectos" / "demo-covid"
CHART_DIR = OUTPUT_DIR / "graficos"
SOURCE_URL = (
    "https://www.datos.gov.co/Salud-y-Protecci-n-Social/"
    "Casos-positivos-de-COVID-19-en-Colombia-/gt2j-8ykr/about_data"
)
DEPARTMENT = "BOYACA"
DATE_COLUMN = "fecha reporte web"
DEPARTMENT_COLUMN = "Nombre departamento"
CASE_ID_COLUMN = "ID de caso"
MUNICIPALITY_COLUMN = "Nombre municipio"
SPANISH_MONTHS = (
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
)

def format_integer(value: int) -> str:
    """Formatea cantidades con separador de miles legible en español."""
    return f"{value:,}".replace(",", ".")


def main() -> None:
    if not CSV_PATH.is_file():
        raise FileNotFoundError(f"No se encontró el CSV de entrada: {CSV_PATH}")

    data = pd.read_csv(CSV_PATH, low_memory=False, encoding="utf-8-sig")
    required = {DATE_COLUMN, DEPARTMENT_COLUMN, CASE_ID_COLUMN, MUNICIPALITY_COLUMN}
    missing_columns = required.difference(data.columns)
    if missing_columns:
        raise ValueError(
            "Faltan columnas necesarias en el CSV: " + ", ".join(sorted(missing_columns))
        )

    data[DEPARTMENT_COLUMN] = (
        data[DEPARTMENT_COLUMN].astype("string").str.strip().str.upper()
    )
    boyaca = data.loc[data[DEPARTMENT_COLUMN].eq(DEPARTMENT)].copy()
    if boyaca.empty:
        raise ValueError(f"El filtro {DEPARTMENT_COLUMN}={DEPARTMENT} no encontró casos.")

    boyaca[DATE_COLUMN] = pd.to_datetime(boyaca[DATE_COLUMN], errors="coerce")
    invalid_dates = int(boyaca[DATE_COLUMN].isna().sum())
    valid = boyaca.dropna(subset=[DATE_COLUMN, CASE_ID_COLUMN]).copy()
    if valid.empty:
        raise ValueError("No hay casos con fecha de reporte e identificador válidos.")

    # El identificador permite contar casos y no depender de que cada fila sea única.
    valid[CASE_ID_COLUMN] = valid[CASE_ID_COLUMN].astype("string").str.strip()
    valid = valid.loc[valid[CASE_ID_COLUMN].ne("")].copy()
    valid["mes"] = valid[DATE_COLUMN].dt.to_period("M")
    monthly = valid.groupby("mes")[CASE_ID_COLUMN].nunique().sort_index()
    full_months = pd.period_range(monthly.index.min(), monthly.index.max(), freq="M")
    monthly = monthly.reindex(full_months, fill_value=0).astype("int64")

    total_cases = int(valid[CASE_ID_COLUMN].nunique())
    peak_month = monthly.idxmax()
    peak_cases = int(monthly.max())
    start_date = valid[DATE_COLUMN].min().date().isoformat()
    end_date = valid[DATE_COLUMN].max().date().isoformat()

    municipalities = (
        valid.groupby(MUNICIPALITY_COLUMN, dropna=False)[CASE_ID_COLUMN]
        .nunique()
        .sort_values(ascending=False)
        .head(10)
    )
    municipality_labels = [
        "Sin dato" if pd.isna(name) or not str(name).strip() else str(name)
        for name in municipalities.index
    ]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    monthly_path = CHART_DIR / "casos_mensuales.png"
    fig, ax = plt.subplots(figsize=(12, 5.5), constrained_layout=True)
    x_values = monthly.index.to_timestamp()
    ax.bar(x_values, monthly.values, width=24, color="#246b73")
    ax.set_title("Casos reportados por mes — Boyacá", loc="left", weight="bold")
    ax.set_xlabel("Mes de fecha reporte web")
    ax.set_ylabel("Casos (ID únicos)")
    ax.grid(axis="y", alpha=0.22)
    ax.spines[["top", "right"]].set_visible(False)
    fig.savefig(monthly_path, dpi=160, bbox_inches="tight")
    plt.close(fig)

    municipality_path = CHART_DIR / "casos_por_municipio.png"
    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)
    positions = range(len(municipalities))
    ax.barh(list(positions), municipalities.values, color="#d76b45")
    ax.set_yticks(list(positions), labels=municipality_labels)
    ax.invert_yaxis()
    ax.set_title("Municipios con más casos registrados — Boyacá", loc="left", weight="bold")
    ax.set_xlabel("Casos (ID únicos)")
    ax.grid(axis="x", alpha=0.22)
    ax.spines[["top", "right"]].set_visible(False)
    fig.savefig(municipality_path, dpi=160, bbox_inches="tight")
    plt.close(fig)

    peak_label = f"{SPANISH_MONTHS[peak_month.month - 1].capitalize()} de {peak_month.year}"
    monthly_rows = "\n".join(
        f"<tr><td>{period.strftime('%Y-%m')}</td><td>{format_integer(int(count))}</td></tr>"
        for period, count in monthly.items()
    )
    limitations = [
        "La fecha de agrupación es «fecha reporte web»; los resultados describen fecha de reporte, no necesariamente inicio de síntomas, diagnóstico o fecha de notificación.",
        "El conteo usa identificadores únicos de caso; identificadores faltantes se excluyen. Si la fuente contiene correcciones o revisiones históricas, esta extracción no las caracteriza por separado.",
        f"En Boyacá se excluyeron {format_integer(invalid_dates)} filas con fecha de reporte no interpretable o faltante.",
        "El gráfico municipal muestra solo los 10 municipios con más casos; los valores no son tasas poblacionales y no permiten inferir riesgo individual.",
        "El CSV local es una extracción; los resultados pueden no coincidir con versiones posteriores publicadas en la fuente oficial.",
    ]
    limitations_html = "\n".join(f"<li>{html.escape(item)}</li>" for item in limitations)
    page = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>COVID-19 en Boyacá | Tablero</title>
  <style>
    :root {{ color-scheme: light; --ink:#1d2935; --muted:#596875; --accent:#246b73; --paper:#f4f7f5; }}
    * {{ box-sizing:border-box; }} body {{ margin:0; font:16px/1.6 system-ui,sans-serif; color:var(--ink); background:var(--paper); }}
    main {{ width:min(1100px, calc(100% - 32px)); margin:40px auto; }} header, section {{ background:#fff; border:1px solid #dce5e1; border-radius:16px; padding:24px; margin-bottom:20px; }}
    h1,h2 {{ line-height:1.2; }} h1 {{ margin:4px 0; }} h2 {{ font-size:1.25rem; }} .muted {{ color:var(--muted); }}
    .cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:14px; }} .card {{ padding:18px; border-radius:12px; background:#eef5f2; }} .value {{ display:block; font-size:1.8rem; font-weight:750; color:var(--accent); }}
    figure {{ margin:0; }} figure img {{ display:block; width:100%; height:auto; }}
    .chart-link {{ display:block; border-radius:10px; cursor:zoom-in; }}
    .chart-link:focus-visible {{ outline:3px solid var(--accent); outline-offset:4px; }}
    figcaption {{ color:var(--muted); font-size:.92rem; margin-top:8px; }}
    .charts {{ display:grid; grid-template-columns:1fr; gap:18px; }} table {{ border-collapse:collapse; width:100%; }} th,td {{ text-align:left; padding:8px 10px; border-bottom:1px solid #e1e7e4; }} th {{ background:#eef5f2; }} .table-wrap {{ max-height:420px; overflow:auto; }}
    @media(min-width:850px) {{ .charts {{ grid-template-columns:1fr 1fr; }} }}
  </style>
</head>
<body><main>
  <header>
    <p class="muted">Análisis reproducible de casos positivos</p>
    <h1>COVID-19 en {html.escape(DEPARTMENT.title())}</h1>
    <p>Departamento filtrado: <strong>{html.escape(DEPARTMENT)}</strong> · Periodo de fecha de reporte: <strong>{start_date} a {end_date}</strong></p>
    <p>Fuente: <a href="{SOURCE_URL}" rel="noopener noreferrer">Casos positivos de COVID-19 en Colombia — datos.gov.co</a></p>
  </header>
  <section><h2>Indicadores</h2><div class="cards">
    <div class="card"><span class="muted">Casos en el periodo</span><span class="value">{format_integer(total_cases)}</span><span class="muted">IDs de caso únicos con fecha válida</span></div>
    <div class="card"><span class="muted">Mes con más reportes</span><span class="value">{html.escape(peak_label)}</span><span class="muted">{format_integer(peak_cases)} casos reportados</span></div>
  </div></section>
  <section><h2>Hallazgo</h2><p>El máximo mensual de la serie observada ocurrió en <strong>{html.escape(peak_label)}</strong>, con <strong>{format_integer(peak_cases)}</strong> casos identificados por ID. La serie usa la fecha de reporte web y completa con cero los meses intermedios sin registros.</p></section>
  <section><h2>Gráficos</h2><div class="charts">
    <figure><a class="chart-link" href="graficos/casos_mensuales.png" target="_blank" rel="noopener" aria-label="Abrir el gráfico mensual en tamaño completo"><img src="graficos/casos_mensuales.png" alt="Gráfico de barras de casos reportados por mes en Boyacá"></a><figcaption>Haz clic en el gráfico para abrirlo en tamaño completo. Conteo mensual según fecha reporte web; cada caso se cuenta una vez por ID.</figcaption></figure>
    <figure><a class="chart-link" href="graficos/casos_por_municipio.png" target="_blank" rel="noopener" aria-label="Abrir el gráfico por municipio en tamaño completo"><img src="graficos/casos_por_municipio.png" alt="Gráfico de barras de los diez municipios con más casos en Boyacá"></a><figcaption>Haz clic en el gráfico para abrirlo en tamaño completo. Diez municipios con más casos registrados durante el periodo completo.</figcaption></figure>
  </div></section>
  <section><h2>Casos por mes</h2><div class="table-wrap"><table><thead><tr><th>Mes</th><th>Casos (ID únicos)</th></tr></thead><tbody>{monthly_rows}</tbody></table></div></section>
  <section><h2>Limitaciones</h2><ul>{limitations_html}</ul><p class="muted">Conteos descriptivos: no representan tasas poblacionales ni estimaciones de incidencia.</p></section>
</main></body></html>
"""
    index_path = OUTPUT_DIR / "index.html"
    index_path.write_text(page, encoding="utf-8")

    print(f"Departamento: {DEPARTMENT}")
    print(f"Periodo: {start_date} a {end_date}")
    print(f"Casos (ID únicos): {total_cases}")
    print(f"Máximo mensual: {peak_label} ({peak_cases})")
    print(f"Fechas inválidas excluidas: {invalid_dates}")
    print(f"Tablero: {index_path}")
    print(f"Gráficos: {monthly_path} | {municipality_path}")


if __name__ == "__main__":
    main()
