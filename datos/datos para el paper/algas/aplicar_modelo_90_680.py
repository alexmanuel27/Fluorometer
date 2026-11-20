"""Historical analysis: the active model since 2026-11-20 is the global linear
90°/680 nm model in lineal_90_680/generar_entrega.py (relative to the paper root).
This module preserves the previous analysis and is also reused for its readers.

Apply the frozen extract calibration to the two intact-culture series.

No fitting or clipping. Read the original ZIP and relative-quantity table;
replace only outputs under resultados/. Python + NumPy/SciPy/Matplotlib.
"""
from pathlib import Path
import csv
import hashlib
import io
import json
import sys
import zipfile

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import analizar_extractos as calibration

OUT = ROOT / "resultados"
SERIES = ("AO", "CV")
COLORS = {"AO": "#264653", "CV": "#2A9D8F"}
J = list(calibration.W).index(680)


def write_csv(name, records):
    with (OUT / name).open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def load():
    # shortcut: supplied .xlsx is actually TSV; revise reader if the source format changes.
    text = (ROOT / "cultivos.xlsx").read_text(encoding="utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(text), delimiter="\t"))
    assert list(rows[0]) == ["muestra", "Cantidad relativa"]
    ids = np.array([int(r["muestra"]) for r in rows])
    quantity = np.array([float(r["Cantidad relativa"].replace(",", ".")) for r in rows])
    assert ids.tolist() == list(range(1, 11))
    assert np.isfinite(quantity).all() and np.all(quantity > 0) and np.all(np.diff(quantity) > 0)
    data, inventory = {}, []
    with zipfile.ZipFile(ROOT / "cultivos.zip") as z:
        names = [n for n in z.namelist() if n.endswith(".csv") and "__MACOSX" not in n]
        assert len(names) == 136
        for name in names:
            contents = z.read(name)
            assert (ROOT / name).is_file() and (ROOT / name).read_bytes() == contents, name
            inventory.append(dict(archivo=name, sha256=hashlib.sha256(contents).hexdigest(),
                                  usado_en_modelo="/90°/" in name))

        def read(name):
            return list(csv.DictReader(io.StringIO(z.read(name).decode("utf-8-sig"))))

        def reference(name):
            values = np.array([[float(r[f"{w}_nm"]) for w in calibration.W]
                               for r in read(name) if r["reading"].isdigit()])
            assert values.shape == (10, 18) and np.isfinite(values).all()
            return values

        for series in SERIES:
            prefix = f"cultivos/{series}/90°/"
            raw, internal = [], []
            for sample in ids:
                readings = [read(f"{prefix}{series}{sample:02}_{rep}-spectrum.csv") for rep in (1, 2, 3)]
                assert all([int(r["wavelength_nm"]) for r in rs] == list(calibration.W) for rs in readings)
                assert all(int(r["n"]) == 10 for rs in readings for r in rs)
                raw.append([[float(r["mean_intensity"]) for r in rs] for rs in readings])
                internal.append([[float(r["standard_deviation"]) for r in rs] for rs in readings])
            blank_names = sorted(n for n in names if n.startswith(prefix + "white-reference"))
            dark_names = [n for n in names if n.startswith(prefix + "dark-reference")]
            assert len(blank_names) == 3 and len(dark_names) == 1
            blanks = np.array([reference(n) for n in blank_names])
            raw, internal = np.array(raw), np.array(internal)
            assert raw.shape == internal.shape == (10, 3, 18)
            assert np.isfinite(raw).all() and np.isfinite(internal).all()
            assert np.all(raw >= 0) and np.all(internal >= 0)
            data[series] = dict(raw=raw, internal=internal, mean=raw.mean(1), sd=raw.std(1, ddof=1),
                                blanks=blanks, blank=blanks.mean((0, 1)), blank_names=blank_names,
                                dark=reference(dark_names[0]))
    assert np.array_equal(data["AO"]["blanks"], data["CV"]["blanks"]), "Check shared-reference interpretation"
    return quantity, data, inventory


def apply(signal, coefficients):
    x = np.asarray(signal)
    return calibration.predict(dict(kind="cuadratico"), coefficients, features=np.stack([x, x*x], axis=-1))


def main():
    quantity, data, inventory = load()
    coeff_file = ROOT.parent / "resultados/coeficientes.json"
    frozen = next(r for r in json.loads(coeff_file.read_text())
                  if r["geometria"] == "90°" and r["grupo"] == "un_canal")
    assert frozen["modelo"] == "cuadratico_680" and frozen["canales"] == [680]
    coefficients = np.array(frozen["parametros"])
    _, cal_data = calibration.load()
    cal_signal = cal_data["90°"]["mean"][1:, J] - frozen["blancos"]["680"]
    positive_min, positive_max = float(cal_signal.min()), float(cal_signal.max())
    expected = coefficients[0] + coefficients[1]*cal_signal + coefficients[2]*cal_signal**2
    assert np.allclose(apply(cal_signal, coefficients), expected)
    assert np.isclose(apply(np.array([0.]), coefficients)[0], coefficients[0])
    OUT.mkdir(exist_ok=True)
    (OUT / "figuras").mkdir(exist_ok=True)
    results, acquisitions, means, reference_rows, summary = [], [], [], [], {}
    for series, d in data.items():
        signal = d["mean"][:, J] - d["blank"][J]
        predicted = apply(signal, coefficients)
        predicted_reps = apply(d["raw"][:, :, J] - d["blank"][J], coefficients)
        literal = apply(d["mean"][:, J] - frozen["blancos"]["680"], coefficients)
        d.update(signal=signal, predicted=predicted, prediction_sd=predicted_reps.std(1, ddof=1))
        assert np.isfinite(predicted).all() and np.isfinite(literal).all()
        for k in range(10):
            status = "por debajo de 0,15" if predicted[k] < .15 else "por encima de 3" if predicted[k] > 3 else "entre 0,15 y 3"
            results.append(dict(serie=series, muestra=f"{series}{k+1:02}", cantidad_relativa=quantity[k],
                                I680=d["mean"][k, J], DE_I680_3_adquisiciones=d["sd"][k, J],
                                blanco_medio_680=d["blank"][J], delta_I680=signal[k],
                                C_equiv_extracto_ug_mL=predicted[k],
                                DE_C_solo_adquisiciones=predicted_reps[k].std(ddof=1),
                                C_literal_blanco_original_ug_mL=literal[k],
                                rango_C_equivalente=status,
                                delta_inferior_al_menor_extracto=bool(signal[k] < positive_min),
                                validacion_concentracion="sin referencia de clorofila; no validada en cultivos"))
            for j, wavelength in enumerate(calibration.W):
                means.append(dict(serie=series, muestra=f"{series}{k+1:02}", cantidad_relativa=quantity[k],
                                  nm=int(wavelength), intensidad=d["mean"][k, j],
                                  DE_3_adquisiciones=d["sd"][k, j], blanco_medio=d["blank"][j],
                                  delta_I=d["mean"][k, j]-d["blank"][j],
                                  calidad=calibration.quality("90°", wavelength)))
            for rep in range(3):
                acquisitions.append(dict(serie=series, muestra=f"{series}{k+1:02}", adquisicion=rep+1,
                                         cantidad_relativa=quantity[k], I680=d["raw"][k, rep, J],
                                         DE_interna_10_lecturas=d["internal"][k, rep, J],
                                         C_equiv_extracto_ug_mL=predicted_reps[k, rep]))
        for b, name in enumerate(d["blank_names"]):
            for j, wavelength in enumerate(calibration.W):
                reference_rows.append(dict(serie=series, archivo=name, nm=int(wavelength),
                                           media_10_lecturas=d["blanks"][b, :, j].mean(),
                                           DE_10_lecturas=d["blanks"][b, :, j].std(ddof=1),
                                           referencia_compartida_AO_CV=True))
        summary[series] = dict(I680_min=float(d["mean"][:, J].min()), I680_max=float(d["mean"][:, J].max()),
                               blanco_680=float(d["blank"][J]),
                               DE_entre_medias_de_3_blancos_680=float(d["blanks"][:, :, J].mean(1).std(ddof=1)),
                               C_equivalente_min=float(predicted.min()), C_equivalente_max=float(predicted.max()),
                               salidas_negativas=int(np.sum(predicted < 0)),
                               salidas_por_debajo_015=int(np.sum(predicted < .15)),
                               señales_bajo_minimo_extracto=int(np.sum(signal < positive_min)),
                               max_cambio_al_usar_blanco_actual=float(np.max(abs(predicted-literal))),
                               dark_todo_cero=bool(np.all(d["dark"] == 0)),
                               Spearman_cantidad_relativa_I680=float(calibration.spearmanr(quantity, signal).statistic))
    for name, records in [("predicciones.csv", results), ("adquisiciones_680.csv", acquisitions),
                          ("medias_18_canales.csv", means), ("referencias.csv", reference_rows),
                          ("inventario_fuentes.csv", inventory)]:
        write_csv(name, records)
    metadata = dict(fecha="2026-11-16", modelo=frozen, rango_concentracion_calibrada=[.15, 3.],
                    rango_delta_extractos_sin_blanco=[positive_min, positive_max],
                    muestras_nuevas=20, adquisiciones_nuevas=60, referencias_independientes_de_series=False,
                    confirmaciones_Alex=dict(AO_y_CV="dos especies en cultivo, células intactas; nombres completos no especificados",
                                             blanco="medio sin algas", condiciones="mismo LED y ajustes de calibración",
                                             concentracion_clorofila="no disponible"),
                    tabla_relativa="cultivos.xlsx es TSV, no un libro XLSX; valores relativos sin unidad absoluta",
                    fuente_sha256={str(p.relative_to(ROOT.parent)): hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in [ROOT/"cultivos.zip", ROOT/"cultivos.xlsx", coeff_file,
                                             ROOT.parent/"dataCruda.zip", ROOT.parent/"reCalibration_20samples.xlsx"]},
                    software=dict(python=sys.version, numpy=np.__version__), resumen=summary,
                    cambio_blanco="coeficientes sin cambiar; principal I680−medio actual; literal con blanco original como sensibilidad",
                    incertidumbre="DE de adquisiciones con blanco y coeficientes fijos; no intervalo de predicción ni incertidumbre total",
                    no_realizado=["reajustar modelo", "recortar negativos", "corregir filtro interno", "analizar 180°", "RMSE externo sin C de referencia"])
    (OUT / "resumen.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    figures(quantity, data, positive_min)
    report(results, metadata)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def figures(quantity, data, positive_min):
    plt = calibration.plt
    plt.rcParams.update({"font.size":10, "svg.fonttype":"none", "axes.spines.top":False, "axes.spines.right":False})
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 5.5))
    fig.subplots_adjust(left=.075, right=.985, top=.85, bottom=.30, wspace=.25)
    for series, d in data.items():
        marker = "o" if series == "AO" else "^"
        axes[0].errorbar(quantity, d["signal"], yerr=d["sd"][:, J], color=COLORS[series],
                         marker=marker, lw=1, ms=4, capsize=2, label=series)
        axes[1].errorbar(quantity, d["predicted"], yerr=d["prediction_sd"], color=COLORS[series],
                         marker=marker, lw=1, ms=4, capsize=2, label=series)
    axes[0].axhline(positive_min, color="#6C757D", ls="--", lw=.9)
    axes[0].text(.0022, positive_min+.7, "Menor señal de extracto calibrado", color="#6C757D", fontsize=8)
    axes[1].axhspan(-.04, .15, color="#6C757D", alpha=.08)
    axes[1].axhline(.15, color="#6C757D", ls="--", lw=.9)
    axes[1].text(.0022, .155, "Nivel inferior de referencia: 0,15 µg/mL", color="#6C757D", fontsize=8)
    for ax in axes:
        ax.axhline(0, color="#6C757D", lw=.6)
        ax.set_xscale("log")
        ax.set(xlabel="Cantidad relativa indicada en la tabla", xlim=(.0016, 1.3))
        ax.grid(axis="y", color="#6C757D", alpha=.15)
        ax.legend(frameon=False)
    axes[0].set(title="A  Respuesta a 680 nm", ylabel="I680 − medio sin algas (u.a.)", ylim=(-.8, 27))
    axes[1].set(title="B  Aplicación del modelo de extracto", ylabel="Concentración equivalente de extracto (µg/mL)", ylim=(-.035, .27))
    fig.suptitle("Cultivos AO y CV · 90° / 680 nm · coeficientes sin reajustar", fontsize=13)
    fig.text(.075, .07, "Medias de tres adquisiciones. Blanco: medio de esta sesión. Eje horizontal logarítmico.\n"
             "Barras: DE entre adquisiciones; no incluyen incertidumbre del blanco, del modelo o de transferencia.\n"
             "La zona sombreada está por debajo del nivel de referencia inferior; no equivale a un límite de detección.", fontsize=9)
    for fmt in ("png", "svg"):
        fig.savefig(OUT / "figuras" / f"01_aplicacion_modelo_90_680.{fmt}", dpi=300, bbox_inches="tight")
    plt.close(fig)


def report(rows, metadata):
    # shortcut: interpretation describes these supplied cultures; revise before replacing sources.
    a, b, c = metadata["modelo"]["parametros"]
    lines = ["# Aplicación de la calibración de extracto a cultivos AO y CV",
             "16 de noviembre de 2026. Alex elige 90°/680 nm y confirma dos especies en cultivo con células intactas, "
             "referencia de medio sin algas y las mismas condiciones instrumentales. No se conocen concentraciones de clorofila de estos cultivos.",
             "## Resultado",
             "La ecuación se puede evaluar, pero sus salidas no validan una concentración de clorofila en células intactas. "
             "19 de las 20 salidas quedan por debajo de 0,15 µg/mL. AO10 da aproximadamente 0,229 µg/mL equivalentes "
             "y CV10 0,0237. Todas las medias de señal neta están por debajo de la menor señal de un extracto no blanco calibrado; "
             "AO10 queda apenas un 0,3% por debajo, por lo que esta frontera no debe tratarse como un umbral físico.",
             "## Método y referencias",
             "Se aplican los coeficientes originales de `../../resultados/coeficientes.json`, sin ajustar ningún parámetro con AO/CV. "
             f"Con x = I680 − B680: C_eq = {a:.12g} + {b:.12g}·x + {c:.12g}·x². "
             "Primero se promedian las tres intensidades de cada nivel y después se aplica la ecuación, como en la calibración original.",
             "El análisis principal sustituye únicamente la referencia por el medio actual: B680 = 0,4940142667 u.a. "
             "La aplicación literal de la ecuación anterior utiliza B680 = 0,8821683333 u.a.; ambas se guardan en la tabla. "
             "El cambio máximo entre estas dos aplicaciones es 0,0051 µg/mL en AO y 0,0035 en CV. "
             "La elección del blanco no resuelve que las señales son bajas respecto a la calibración.",
             "Las tres referencias de medio y el dark están duplicados de forma idéntica entre AO y CV; "
             "se consideran compartidos, no seis referencias independientes. Los dark son nulos y no aportan una estimación física del ruido.",
             "## Resultados por nivel",
             "La cantidad relativa se transcribe tal como aparece en la tabla; no se transforma en µg/mL ni se presupone la concentración del nivel 1. "
             "Las salidas negativas se conservan y no representan cantidades físicas negativas de pigmento.",
             "| Serie | Muestra | Cantidad relativa | ΔI680 (u.a.) | C equivalente (µg/mL) | DE solo adquisiciones | C con blanco original |",
             "|---|---|---:|---:|---:|---:|---:|"]
    for r in rows:
        lines.append(f"| {r['serie']} | {r['muestra']} | {r['cantidad_relativa']:g} | {r['delta_I680']:.4f} | "
                     f"{r['C_equiv_extracto_ug_mL']:.4f} | {r['DE_C_solo_adquisiciones']:.4f} | "
                     f"{r['C_literal_blanco_original_ug_mL']:.4f} |")
    lines += ["## Interpretación y límites",
              "A 680 nm, la intensidad tiende a aumentar con la cantidad relativa en ambas series, sobre todo en los niveles altos. "
              "En los niveles bajos hay mesetas y variaciones que impiden distinguir todos los pasos de dilución. "
              "La respuesta positiva de varios niveles por encima del medio no implica que el modelo pueda cuantificarlos con exactitud.",
              "El paso entre los niveles relativos 0,20 y 0,25 merece revisar la preparación y las etiquetas: "
              "la señal neta aumenta aproximadamente 2,39 veces en AO y 3,07 en CV, frente a un factor de 1,25 en la cantidad relativa. "
              "Es un patrón compartido que no demuestra un error de preparación; se conserva sin corregir ni eliminar muestras.",
              "AO tiene una respuesta roja mayor que CV a igual etiqueta de cantidad relativa. No se conoce una concentración común de referencia "
              "para ambas especies; por tanto, ese contraste no demuestra mayor concentración de clorofila ni mayor rendimiento fluorescente de una especie.",
              "El dominio original comprende referencias de 0,15–3 µg/mL y un blanco en cero, sin validación del intervalo entre cero y 0,15. "
              "La señal neta mínima observada en los extractos no blancos es 23,606818 u.a.; AO10 alcanza 23,536244 y CV10 4,869568. "
              "AO10 produce una C equivalente dentro del rango nominal a pesar de estar ligeramente por debajo de esa señal: "
              "el modelo ya sobreestimaba el nivel inferior de la serie original, según la revisión de residuos.",
              "La DE comunicada recoge únicamente la variación entre adquisiciones, usando blanco y coeficientes fijos. "
              "No es un intervalo de predicción ni incluye incertidumbre del blanco compartido, la calibración o su transferencia a cultivos. "
              "Una DE nula en algunos niveles refleja repetición exacta de valores registrados, no incertidumbre total nula. "
              "Las tres adquisiciones no se tratan como preparaciones independientes. Sin concentraciones de referencia no se calculan residuos "
              "de concentración, RMSE externo, recuperación ni exactitud absoluta. No se inventa una concentración esperada a partir de la cantidad relativa.",
              "Para validar el uso cuantitativo en cultivos, hace falta una determinación independiente de clorofila en muestras emparejadas "
              "y comprobar una calibración que cubra estas señales bajas. La geometría y el canal seleccionados pueden mantenerse; "
              "la transferencia de la ecuación de extracto queda sin validar.",
              "## Archivos y reproducibilidad",
              "- [Figura principal](figuras/01_aplicacion_modelo_90_680.png) · [SVG](figuras/01_aplicacion_modelo_90_680.svg).\n"
              "- [Predicciones de las 20 muestras](predicciones.csv), [60 adquisiciones](adquisiciones_680.csv), "
              "[18 canales procesados](medias_18_canales.csv) y [referencias compartidas](referencias.csv).\n"
              "- [Resumen, coeficientes y huellas de fuentes](resumen.json) e [inventario](inventario_fuentes.csv).",
              "Reproducir con `python3 ../aplicar_modelo_90_680.py` en un entorno con NumPy, SciPy y Matplotlib. "
              "El archivo fuente llamado `cultivos.xlsx` es en realidad una tabla TSV con comas decimales; se lee sin modificarlo. "
              "Los 136 CSV del ZIP coinciden con la carpeta extraída. Se modelan solo las 60 adquisiciones a 90°; "
              "no se reabre la comparación con 180° ni se modifican calibraciones, datos fuente o firmware."]
    lines.insert(0, "> **Aplicación cuadrática histórica.** La selección actual es lineal 90°/680 nm. [Informe vigente](../../lineal_90_680/INFORME.md).")
    (OUT / "informe.md").write_text("\n\n".join(lines).replace("|\n\n|", "|\n|"), encoding="utf-8")


if __name__ == "__main__":
    main()
