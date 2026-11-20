"""Current paper delivery: Alex's 2026-11-20 choice of the global 90°/680 nm line.

Reuses the original readers and fits. Writes only this folder's resultados/,
figure index and report. Historical outputs and the firmware remain untouched.
"""
from pathlib import Path
import csv
import hashlib
import json
import shutil
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(ROOT), str(ROOT / "algas"), str(ROOT / "kaolin")]
import analizar_extractos as cal
import aplicar_modelo_90_680 as algae
import analizar_kaolin as kaolin
from resolver_dudas import metrics, read_csv

OUT = HERE / "resultados"
FIG = OUT / "figuras"
P, T, Y, C, G = "#264653", "#2A9D8F", "#E9C46A", "#E76F51", "#6C757D"
COLORS = [P, T, Y, C, G]
plt = cal.plt
CATALOG = []


def write_csv(name, rows):
    with (OUT / name).open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def save(fig, code, title, caption, foot=""):
    fig.suptitle(title, fontsize=12)
    fig.get_layout_engine().set(rect=(0, .13, 1, .84))
    fig.text(.065, .025, foot or "Three acquisitions per sample. Error bars: acquisition SD only; fixed session blank.\n"
             "No independent preparation replicates or total measurement-uncertainty intervals are implied.", fontsize=8)
    for fmt in ("png", "svg"):
        fig.savefig(FIG / f"{code}.{fmt}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    CATALOG.append(dict(codigo=code, titulo=title, pie_ingles=caption, origen="generated with selected linear model"))


def clean(axes):
    for ax in np.asarray(axes, dtype=object).flat:
        ax.grid(axis="y", color=G, alpha=.13)
        ax.set_axisbelow(True)


def extract_figures(c, d, a, b, pred, regions):
    x = d["mean"][:, 10]-d["blank"][10]
    err = pred-c[1:]
    grid = np.linspace(0, x.max()*1.025, 250)
    fig, ax = plt.subplots(2, 2, figsize=(11, 8), layout="constrained")
    ax[0, 0].errorbar(x, c, xerr=d["sd"][:, 10], fmt="o", color=G, ms=4, capsize=2)
    ax[0, 0].plot(grid, a+b*grid, color=P, lw=1.6)
    ax[0, 0].axhline(0, color=G, lw=.7)
    ax[0, 0].set(title="A  Selected global linear calibration", xlabel="Blank-subtracted I680 (a.u.)", ylabel="Concentration (µg/mL)")
    ax[0, 1].scatter(c[1:], pred, color=P, s=25)
    ax[0, 1].plot([0, 3.1], [0, 3.1], color=G, ls=":")
    ax[0, 1].set(title="B  Held-out predictions", xlabel="Reference (µg/mL)", ylabel="LOO prediction (µg/mL)")
    ax[1, 0].plot(c[1:], 100*err/c[1:], color=P, marker="o", lw=.7, ms=4)
    ax[1, 0].axhline(0, color=G, lw=.7)
    ax[1, 0].set(title="C  Signed relative prediction errors", xlabel="Reference (µg/mL)", ylabel="Prediction error (%)")
    ax[1, 1].bar(np.arange(5), [r["MAPE_pct"] for r in regions[1:]], color=P)
    ax[1, 1].set(title="D  Mean absolute relative error", xticks=np.arange(5),
                 xticklabels=[r["region"].replace("–", "–\n") for r in regions[1:]], ylabel="MAPE (%)", xlabel="Reference region (µg/mL)")
    clean(ax)
    save(fig, "F1_calibracion_lineal", "Extract calibration · 90° / 680 nm · selected linear model",
         "Linear extract calibration selected by Alex on 20 November 2026. (A) Mean net intensities and their acquisition SD, with the global concentration-on-signal fit including the measured zero-reference blank. (B) Leave-one-sample-out concentration predictions. (C) Signed relative errors. (D) MAPE in five groups of four reference levels. Each held-out unit is a complete sample; the session blank remains available. Residual structure persists.",
         f"Fixed-model internal validation: RMSE = {regions[0]['RMSE_ug_mL']:.4f} µg/mL; MAPE = {regions[0]['MAPE_pct']:.2f}%.\n"
         "The blank has reference concentration zero; the freely fitted intercept is not constrained to zero. No clipping.")

    fig, ax = plt.subplots(1, 2, figsize=(10, 4.7), layout="constrained")
    for ar in ax:
        ar.errorbar(x, c, xerr=d["sd"][:, 10], fmt="o", color=G, ms=4, capsize=2, label="References")
        ar.plot(grid, a+b*grid, color=P, label="Selected line")
        ar.axhline(0, color=G, lw=.7)
        ar.set(xlabel="Blank-subtracted I680 (a.u.)", ylabel="Concentration (µg/mL)")
    ax[0].set_title("A  All calibration points")
    ax[1].set(title="B  Low end · same global fit", xlim=(-1, x[4]*1.12), ylim=(-.48, .78))
    ax[0].legend(frameon=False, fontsize=8)
    clean(ax)
    save(fig, "S01_curva_y_zona_baja", "Selected linear calibration · full range and low-end enlargement",
         "The same global linear calibration is shown over the full measured range and enlarged at the low end. Gray points include the measured zero-reference blank. Horizontal error bars show acquisition SD. The enlargement is not a locally refitted line. The freely fitted intercept is negative.")

    fig, ax = plt.subplots(2, 2, figsize=(10.5, 7.5), layout="constrained")
    fit_error = a+b*x[1:]-c[1:]
    for y, color, marker, label in [(err, P, "o", "Held-out"), (fit_error, T, "^", "Full-fit residual")]:
        ax[0, 0].plot(c[1:], y, color=color, marker=marker, lw=.7, ms=4, label=label)
    ax[0, 0].legend(frameon=False, fontsize=8)
    ax[0, 0].set(title="A  Concentration errors", xlabel="Reference (µg/mL)", ylabel="Prediction − reference (µg/mL)")
    ax[0, 1].scatter(c[1:], 100*err/c[1:], color=P, s=25)
    ax[0, 1].set(title="B  Signed relative errors", xlabel="Reference (µg/mL)", ylabel="Error (%)")
    ax[1, 0].scatter(pred, err, color=P, s=25)
    ax[1, 0].set(title="C  Errors versus predictions", xlabel="Held-out prediction (µg/mL)", ylabel="Prediction − reference (µg/mL)")
    ax[1, 1].plot(np.arange(1, 21), err, color=P, marker="o", lw=.7, ms=4)
    ax[1, 1].set(title="D  Errors by sample identifier", xlabel="Sample ID · not a verified time axis", ylabel="Prediction − reference (µg/mL)")
    for ar in ax.flat:
        ar.axhline(0, color=G, lw=.7)
    clean(ax)
    save(fig, "S02_residuos_lineal", "Selected line · residual diagnostics",
         "Full-fit and held-out concentration errors are distinguished. The lower-right panel follows sample identifiers and does not establish measurement chronology. Local bias persists; a near-zero global average must not be interpreted as absence of bias. Shared references and the session blank limit independence assumptions.",
         "All 20 positive references retained. LOO errors exclude the tested sample from fitting.\nNo residual independence, normality or constant-variance claim is made.")

    fig, ax = plt.subplots(1, 3, figsize=(12.2, 4.6), layout="constrained")
    for ar, key, title, ylabel in zip(ax, ["MAPE_pct", "RMSE_ug_mL", "sesgo_ug_mL"],
            ["A  Absolute relative error", "B  RMSE", "C  Mean signed bias"], ["MAPE (%)", "RMSE (µg/mL)", "Bias (µg/mL)"]):
        bars = ar.bar(np.arange(5), [r[key] for r in regions[1:]], color=P)
        ar.bar_label(bars, fmt="%.2f" if key == "MAPE_pct" else "%.3f", padding=3, fontsize=8)
        ar.set(title=title, ylabel=ylabel, xticks=np.arange(5), xticklabels=[r["region"].replace("–", "–\n") for r in regions[1:]])
        ar.tick_params(axis="x", labelsize=8)
        ar.axhline(0, color=G, lw=.7)
        ar.margins(y=.25)
    clean(ax)
    save(fig, "S03_errores_por_region", "Selected line · errors in five concentration regions",
         "Internal held-out errors of the selected line in five groups of four consecutive references: MAPE, RMSE and mean signed bias. The blank is excluded from relative errors. Bars summarize observed errors and are not uncertainty intervals.",
         "Four positive standards per region; shared session blank.\nPositive bias indicates overestimation, negative bias underestimation.")

    fig, ax = plt.subplots(1, 2, figsize=(10.2, 4.6), layout="constrained")
    models = read_csv(ROOT / "resultados/modelos.csv")
    previous = read_csv(ROOT / "resultados/residuos_correccion_fondo.csv")
    comparison = []
    for kind, color, marker, ls, label in [("lineal", P, "o", "-", "Selected line"), ("cuadratico", T, "^", "--", "Historical quadratic")]:
        row = next(r for r in models if r["geometria"] == "90°" and r["modelo"] == f"{kind}_680")
        coef = np.array(json.loads(row["parametros"]))
        curve = coef[0]+coef[1]*grid+(coef[2]*grid**2 if len(coef) == 3 else 0)
        er = np.array([float(r["error_LOO"]) for r in previous if r["geometria"] == "90°" and r["referencia_nm"] == "solo_blanco" and r["funcion"] == kind])
        assert len(er) == 20
        comparison.append(dict(modelo=kind, **metrics(c[1:], er)))
        ax[0].plot(grid, curve, color=color, ls=ls, label=label)
        ax[1].plot(c[1:], 100*er/c[1:], color=color, marker=marker, ls=ls, lw=.7, ms=4, label=label)
    ax[0].scatter(x, c, color=G, s=15)
    ax[0].set(title="A  Fits to all calibration points", xlabel="Net I680 (a.u.)", ylabel="Concentration (µg/mL)")
    ax[1].set(title="B  Held-out relative errors", xlabel="Reference (µg/mL)", ylabel="Signed prediction error (%)")
    for ar in ax:
        ar.axhline(0, color=G, lw=.7)
        ar.legend(frameon=False, fontsize=8)
    clean(ax)
    save(fig, "S04_lineal_y_cuadratico", "Selected line and historical quadratic · transparent model comparison",
         "The selected line is compared with the previously studied quadratic on the same references and held-out splits. Selection of the line is an explicit operational choice, not a claim that it minimizes RMSE. Both retain structured errors.",
         "Petroleum: selected linear model. Teal dashed: historical quadratic.\nThe quadratic has lower overall RMSE; neither model is uniformly better across concentrations.")
    write_csv("comparacion_modelos.csv", comparison)

    fig, ax = plt.subplots(1, 2, figsize=(10, 4.6), layout="constrained")
    sd_c = abs(b)*d["sd"][1:, 10]
    ax[0].plot(c[1:], sd_c, color=T, marker="^", ms=4, label="SD of three acquisitions")
    ax[0].scatter(c[1:], abs(err), color=P, s=23, label="Absolute held-out error")
    ax[0].set(title="A  Reading variability and prediction error", xlabel="Reference (µg/mL)", ylabel="Concentration scale (µg/mL)")
    ax[0].legend(frameon=False, fontsize=8)
    ax[1].scatter(c[1:], 100*sd_c/c[1:], color=T, marker="^", s=25)
    ax[1].set(title="B  Acquisition SD relative to reference", xlabel="Reference (µg/mL)", ylabel="100 × acquisition SD / reference (%)")
    clean(ax)
    save(fig, "S05_repetibilidad_y_error", "Reading repeatability does not represent total calibration error",
         "Variation among three acquisitions is mapped to the concentration scale using the fixed slope and contrasted with held-out prediction errors. These are distinct quantities: acquisition SD is not uncertainty of the sample mean or a prediction interval. Relative SD is divided by the assigned reference.",
         "Blank and slope held fixed for acquisition SD. This comparison shows magnitudes only.\nNo complete uncertainty budget or independent preparation precision is available.")


def culture_figures(quantity, d, rows, a, b, cal_signal, c):
    x = np.array([r["delta_I680"] for r in rows])
    sd = d["sd"][:, 10]
    y = a+b*x
    fig, ax = plt.subplots(1, 2, figsize=(10.3, 4.8), layout="constrained")
    for ar in ax:
        ar.errorbar(quantity, x, yerr=sd, color=P, marker="o", ls="none", ms=4, capsize=3)
        ar.axhline(0, color=G, lw=.7)
        ar.set(xlabel="Recorded relative culture amount", ylabel="Medium-subtracted I680 (a.u.)")
    ax[0].set_title("A  Linear quantity axis")
    ax[1].set(title="B  Same measurements · log quantity axis", xscale="log")
    clean(ax)
    save(fig, "F3_AO_respuesta_medida", "AO culture · 90° / 680 nm · measured response",
         "Medium-subtracted 680 nm response from ten recorded relative AO culture levels at 90° under 430 nm excitation. Linear and logarithmic horizontal axes show the same means and acquisition SD. The medium blank is fixed. Chlorophyll concentrations of the cultures were not determined independently; the horizontal axis has no absolute concentration unit.")

    fig, ax = plt.subplots(2, 2, figsize=(10.8, 7.8), layout="constrained")
    for ar in ax[0]:
        for mask, color, marker, label in [(y < 0, C, "v", "Negative estimate"), (y >= 0, P, "o", "Nonnegative estimate")]:
            ar.errorbar(quantity[mask], y[mask], yerr=abs(b)*sd[mask], color=color, marker=marker,
                        ls="none", capsize=2, ms=4, label=label)
        ar.axhline(0, color=G, lw=.8)
        ar.set(xlabel="Recorded relative culture amount", ylabel="Extract-equivalent estimate (µg/mL)")
    ax[0, 0].set_title("A  Signed equivalent estimates")
    ax[0, 1].set(title="B  Same estimates · log quantity axis", xscale="log")
    grid = np.linspace(0, max(cal_signal)*1.02, 250)
    for ar in ax[1]:
        ar.plot(grid, a+b*grid, color=P)
        ar.scatter(cal_signal, c, color=G, s=15)
        for mask, color, marker in [(y < 0, C, "v"), (y >= 0, P, "o")]:
            ar.scatter(x[mask], y[mask], color=color, marker=marker, s=25)
        ar.axhline(0, color=G, lw=.8)
        ar.axvline(-a/b, color=G, ls=":", lw=.8)
        ar.set(xlabel="Blank-subtracted I680 (a.u.)", ylabel="Extract-equivalent estimate (µg/mL)")
    ax[1, 0].set_title("C  Position on the selected line")
    ax[1, 1].set(title="D  AO signal range enlarged", xlim=(0, 27), ylim=(-.46, .25))
    ax[0, 0].legend(frameon=False, fontsize=8)
    clean(ax)
    save(fig, "S06_AO_conversion_lineal", "AO · signed outputs of the selected linear calibration",
         "Exploratory application of the selected extract line to AO using its session-medium blank. Nine mean outputs are negative and all ten lie below 0.15 µg/mL. Negative values are retained; they are model estimates, not physical negative concentrations. The zero crossing is a property of the line and is not a detection limit. Error bars describe acquisition SD with fixed blank and coefficients.",
         f"Nine of ten mean estimates are negative. f(0) = {a:.4f} µg/mL; zero crossing = {-a/b:.3f} net a.u.\n"
         "All AO mean signals fall below the lowest positive extract signal. No absolute concentration validation in AO.")

    fig, ax = plt.subplots(1, 2, figsize=(12, 5.7), layout="constrained")
    for i in range(10):
        color, marker = COLORS[i % 5], "o" if i < 5 else "^"
        for ar, values in zip(ax, [d["mean"][i], d["mean"][i]-d["blank"]]):
            ar.plot(cal.W, values, color=color, marker=marker, ms=3, lw=.8, ls="-" if i < 5 else "--", label=f"AO{i+1:02}")
    for ar in ax:
        ar.set(yscale="symlog", xlabel="Wavelength (nm)", ylabel="Intensity (a.u.)", xticks=cal.W)
        ar.tick_params(axis="x", labelrotation=55, labelsize=7)
        ar.axvspan(478, 492, color=Y, alpha=.2)
        ar.axvline(680, color=G, lw=.7)
    ax[0].set_title("A  Original channel intensities")
    ax[1].set_title("B  Session-medium-subtracted intensities")
    ax[0].legend(ncol=2, frameon=False, fontsize=7)
    clean(ax)
    save(fig, "S07_AO_espectros_18_canales", "AO · all 18 channels · all ten culture levels",
         "Original and medium-subtracted channel spectra for all ten AO levels at 90°. Colors and markers distinguish levels in both panels. Signed logarithmic axes preserve negative differences. The 485 nm band is flagged as unstable and is retained for traceability; 680 nm is the selected analysis channel.",
         "Signed logarithmic vertical axes; mean of three acquisitions per level.\nYellow band: unstable 485 nm channel. No spectral unmixing or fluorescence-purity claim is made.")


def other_figures(c, data, ad, kd, a, b, krows):
    fig, ax = plt.subplots(1, 2, figsize=(10, 4.5), layout="constrained")
    for ar, blanks, title in [(ax[0], data["90°"]["blanks"][:, :, 10], "A  Extract-calibration blanks"),
                               (ax[1], ad["blanks"][:, :, 10], "B  AO medium blanks")]:
        for i, values in enumerate(blanks):
            ar.plot(np.arange(1, 11), values, color=COLORS[i], marker=["o", "^", "s"][i], ms=3, lw=.7, label=f"File {i+1}")
        ar.axhline(blanks.mean(), color=G, ls=":", label=f"Mean B = {blanks.mean():.4f}")
        ar.set(title=title, xlabel="Internal reading within file", ylabel="I680 (a.u.)")
        ar.legend(frameon=False, fontsize=8)
    clean(ax)
    save(fig, "S08_blancos_680", "680 nm reference readings · calibration and AO sessions",
         "Ten internal readings from each of three blank files in the extract-calibration and AO-medium datasets. Dotted lines indicate the session means used in subtraction. These files do not represent thirty independent blank preparations and do not establish a method LOD or LOQ.",
         "Three files per session; ten internal readings per file. Different media and session references.\nThese traces do not establish a method detection or quantification limit.")

    fig, ax = plt.subplots(1, 2, figsize=(10, 4.6), layout="constrained")
    d = data["90°"]
    values = np.array([d["mean"][-1, 10]-d["blank"][10], kd["90°"]["mean"][1, 10]-kd["90°"]["mean"][0, 10]])
    sd = np.array([d["sd"][-1, 10], kd["90°"]["sd"][1, 10]])
    labels = ["Calibration series", "Kaolin series: pure extract"]
    for ar, y, sy, ylabel in [(ax[0], values, sd, "Net I680 (a.u.)"), (ax[1], a+b*values, abs(b)*sd, "Linear equivalent (µg/mL)")]:
        ar.bar(np.arange(2), y, yerr=sy, color=[P, T], capsize=3, error_kw=dict(ecolor=G, color=G))
        ar.set(xticks=np.arange(2), xticklabels=labels, ylabel=ylabel)
        ar.tick_params(axis="x", labelsize=8)
    ax[0].set_title("A  Same nominal reference: 3 µg/mL")
    ax[1].set_title("B  Fixed selected line applied to both")
    ax[1].axhline(3, color=G, ls="--", label="Nominal reference")
    ax[1].legend(frameon=False, fontsize=8)
    clean(ax)
    save(fig, "S09_transferencia_entre_series", "Between-series response comparison at nominal 3 µg/mL",
         "The highest extract reference of the calibration series and pure extract of the kaolin series have the same nominal concentration but different net responses. Fixed-line outputs are shown as a transfer sensitivity check. The differences do not identify a cause or establish independently measured concentration recovery.",
         "Separate supplied series; session-specific ethanol subtraction. Error bars: acquisition SD only.\nNominal concentrations are not an independent remeasurement after preparation or contact with particles.")

    fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.8), layout="constrained")
    labels = ["Ethanol", "Extract", "Kaolin b", "Kaolin a", "Extract + b", "Extract + a"]
    for ar, key, sdkey, title, ylabel in [(ax[0], "delta_I680", "DE_I680", "A  Measured net response", "Net I680 (a.u.)"),
                                         (ax[1], "C_equiv_lineal", "DE_C_lecturas", "B  Exploratory linear equivalents", "Equivalent estimate (µg/mL)")]:
        ar.bar(np.arange(6), [r[key] for r in krows], yerr=[r[sdkey] for r in krows], capsize=2,
               color=[G, P, T, C, T, C], error_kw=dict(ecolor=G, color=G))
        ar.axhline(0, color=G, lw=.8)
        ar.set(title=title, ylabel=ylabel, xticks=np.arange(6), xticklabels=labels)
        ar.tick_params(axis="x", rotation=32, labelsize=8)
    clean(ax)
    save(fig, "S10_caolin_equivalentes_lineales", "Kaolin series · selected 90° / 680 nm line applied without refitting",
         "Measured net responses and corresponding fixed-line equivalent estimates for all six kaolin-series preparations at 90°. Negative outputs for controls are retained. These are transfer calculations, not validated concentration recoveries; the nominal chlorophyll-containing preparations were supplied at 3 µg/mL. Acquisition SD holds the ethanol reference and slope fixed.")


def carry_figures():
    sources = [
        ("kaolin/resultados/figuras/01_figura_principal", "F2_caolin_geometrias", "Kaolin response · 90° and 180°", "Measured 680 nm intensities and normalized responses with and without kaolin. The 810 nm correction is exploratory. Response percentages are not concentration recoveries."),
        ("kaolin/resultados/figuras/02_canales_rojos_y_contrastes", "S11_caolin_rojos", "Kaolin · red-channel contrasts", "Red-channel signals and matched contrasts across kaolin loadings. Contrasts show measured response differences and do not isolate pure chlorophyll fluorescence."),
        ("kaolin/resultados/figuras/04_espectros_raw_y_blanco", "S12_caolin_espectros", "Kaolin · all wavelengths, original and blank-subtracted", "All six preparations and 18 channels, with 90° on the left and 180° on the right. Original spectra are above and ethanol-subtracted spectra below. Flagged bands remain visible. Signed logarithmic scaling is identified on the figure."),
        ("kaolin/resultados/figuras/03_18_canales_90", "S13_caolin_18_canales_90", "Kaolin · 18-channel review at 90°", "Individual channel responses at 90° for preparations with and without extract. The unstable 485 nm band is flagged; acquisitions are technical replicates."),
        ("kaolin/resultados/figuras/03_18_canales_180", "S14_caolin_18_canales_180", "Kaolin · 18-channel review at 180°", "Individual channel responses at 180°. Near-2^32 readings at 410/435 nm and the unstable 485 nm band are flagged and excluded from interpretation."),
        ("resultados/figuras/02_canales_90", "S15_extractos_18_canales_90", "Extract standards · 18-channel review at 90°", "Observed 18-channel responses across the extract references at 90°. This measurement overview does not make other channel fits the selected calibration."),
        ("resultados/figuras/02_canales_180", "S16_extractos_18_canales_180", "Extract standards · 18-channel review at 180°", "Observed 18-channel responses across the extract references at 180°. Flagged channels remain documented. The current selected geometry is 90°."),
    ]
    for source, code, title, caption in sources:
        for fmt in ("png", "svg"):
            shutil.copy2(ROOT / f"{source}.{fmt}", FIG / f"{code}.{fmt}")
        CATALOG.append(dict(codigo=code, titulo=title, pie_ingles=caption,
                            origen=f"unchanged measured-data figure: {source}"))


def reports(summary, regions, ao):
    CATALOG.sort(key=lambda r: (not r["codigo"].startswith("F"), r["codigo"]))
    write_csv("indice_figuras.csv", CATALOG)
    lines = ["# Figuras y pies para Daniela · selección lineal 90°/680 nm", "",
             "20 de noviembre de 2026. F1–F3: propuestas principales; S01–S16: material complementario.",
             "Las figuras F1, S01–S05 y S06–S10 son nuevas. Las siete figuras restantes describen mediciones y se conservan sin cambiar sus datos.",
             "Paleta: azul petróleo, teal, amarillo, coral y gris. En las comparaciones de modelos nuevas, petróleo identifica la recta elegida y teal el cuadrático histórico.", ""]
    for r in CATALOG:
        stem = f"resultados/figuras/{r['codigo']}"
        lines += [f"## {r['codigo']} · {r['titulo']}", "", f"[PNG]({stem}.png) · [SVG editable]({stem}.svg)", "",
                  f"![{r['titulo']}]({stem}.png)", "", "**Caption:** "+r["pie_ingles"], ""]
    (HERE / "FIGURAS_Y_PIES.md").write_text("\n".join(lines), encoding="utf-8")
    a, b = summary["modelo"]["parametros"]
    lines = ["# Informe actual · modelo lineal 90°/680 nm", "", "**Decisión explícita de Alex: 20 de noviembre de 2026.** Modelo global con intercepto libre; no se obliga a pasar por cero y no se ajusta una recta local.", "",
             f"`C_eq [µg/mL] = {a:.12f} + {b:.12f} × (I680 − B680)`.", "",
             f"Presentación normalizada: `u = (I680 − B680)/100`; `C_eq = {100*b:.6f}u {a:+.6f}` en µg/mL. Escalar la variable no divide la concentración entre 100.", "",
             "## Extractos: error interno", "", "| Referencias (µg/mL) | n | RMSE (µg/mL) | MAPE (%) | Sesgo (µg/mL) |", "|---|---:|---:|---:|---:|"]
    for r in regions:
        lines.append(f"| {r['region']} | {r['n']} | {r['RMSE_ug_mL']:.4f} | {r['MAPE_pct']:.2f} | {r['sesgo_ug_mL']:+.4f} |")
    lines += ["", "Se mantienen las 20 referencias positivas y el blanco. Las tres adquisiciones se promedian antes de cualquier división. Cada predicción LOO se obtiene sin esa muestra, con blanco de sesión disponible. El error relativo se calcula contra la referencia de cada muestra y no se define para el blanco cero.", "",
              "La selección de la recta es operativa. Su MAPE global es similar al del cuadrático, pero su RMSE es mayor y conserva sesgos locales. En 1,35–1,80 sobreestima; en 2,55–3,00 subestima. Estas métricas no son un error garantizado ni un intervalo de incertidumbre para cualquier muestra.", "",
              "## AO: aplicación y negativos", "",
              f"Con el blanco de medio de AO, B680 = {summary['blanco_AO']:.9f} u.a., **{sum(r['C_equiv_lineal'] < 0 for r in ao)} de las diez medias son negativas**. AO10 da **{ao[-1]['C_equiv_lineal']:.6f} µg/mL equivalentes**. Todos los resultados son inferiores a 0,15 µg/mL. La respuesta neta medida sigue siendo positiva.", "",
              f"La recta predice {a:.6f} µg/mL para intensidad neta cero y cruza cero en {-a/b:.6f} u.a. Esa raíz no es un límite de detección. El cambio de cuatro negativos del cuadrático a nueve de la recta se debe al cambio del modelo, sin alterar intensidades. No se recortan las salidas ni se interpretan como concentraciones físicas negativas.", "",
              "Todas las medias AO quedan entre el blanco y el menor patrón positivo de extracto. AO no dispone de una referencia absoluta de clorofila; por tanto, no se puede calcular su error de concentración o validar estos equivalentes. F3 muestra la respuesta medida y S06 conserva la conversión con signo. CV permanece únicamente como antecedente y fuente original.", "",
              "## Caolín y transferencia", "",
              "La comparación de señales con partículas conserva su interpretación: a 90° las mezclas mantienen aproximadamente 101,54/101,40% de la respuesta neta del extracto puro; a 180°, 76,96/69,20%. Son porcentajes de señal, no recuperación de concentración. La corrección a 810 nm es exploratoria.", "",
              "Aplicar la recta a las muestras de caolín es una comprobación de transferencia, documentada separadamente en S09/S10 y en la tabla correspondiente. Las concentraciones nominales y la conservación relativa de señal no validan automáticamente concentraciones obtenidas con coeficientes de otra serie.", "",
              "## Límites y próximos experimentos", "",
              "LOD/LOQ no establecidos. Tres archivos de blanco con diez lecturas internas no equivalen a treinta preparaciones independientes; dark nulos no acreditan ruido cero. Faltan validación del extremo bajo, variación entre días/preparaciones y, si se pretende exactitud absoluta en AO, referencia independiente de clorofila. No se aplicó corrección de filtro interno ni se modificó el firmware.", "",
              "## Archivos", "", "- [Modelo elegido](resultados/modelo_seleccionado.json).", "- [Resultados y huellas](resultados/resumen.json).",
              "- [Extractos y errores por muestra](resultados/extractos_muestras.csv).", "- [Errores por región](resultados/errores_regiones.csv).",
              "- [AO](resultados/AO_muestras.csv) y [adquisiciones](resultados/AO_adquisiciones.csv).", "- [Caolín a 90°](resultados/kaolin_90_muestras.csv).",
              "- [Todas las figuras y pies](FIGURAS_Y_PIES.md).", "", "Reproducir desde la carpeta superior con `python lineal_90_680/generar_entrega.py`, usando su `requirements.txt`. Se escriben solo resultados de esta entrega y sus índices."]
    (HERE / "INFORME.md").write_text("\n".join(lines)+"\n", encoding="utf-8")


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    CATALOG.clear()
    plt.rcParams.update({"font.size": 9, "svg.fonttype": "none", "axes.spines.top": False, "axes.spines.right": False,
                         "axes.prop_cycle": plt.cycler(color=COLORS)})
    cal.self_check()
    kaolin.self_check()
    c, data = cal.load()
    d = data["90°"]
    x = d["mean"][:, 10]-d["blank"][10]
    model = dict(kind="lineal", alpha=0., x=x[:, None])
    train = np.arange(len(c))
    a, b = cal.fit(model, c, train)
    original = next(r for r in read_csv(ROOT / "resultados/modelos.csv") if r["geometria"] == "90°" and r["modelo"] == "lineal_680")
    assert np.allclose([a, b], json.loads(original["parametros"]), atol=1e-12, rtol=0)
    pred = cal.cv(model, c, train)
    explicit = np.array([cal.predict(model, cal.fit(model, c, train[train != i]), [i])[0] for i in train[1:]])
    assert np.allclose(pred, explicit, atol=1e-10, rtol=0)
    err = pred-c[1:]
    selected = dict(fecha_decision="2026-11-20", geometria="90°", excitacion_nm=430, canal_nm=680, modelo="lineal_680",
                    parametros=[float(a), float(b)], orden_parametros=["intercepto", "pendiente"], variable="I680 − blanco de sesión",
                    unidad_intensidad="u.a.", unidad_concentracion="µg/mL", blanco_calibracion=float(d["blank"][10]),
                    criterio="elección explícita de Alex; recta global, no mínimo RMSE ni recta local",
                    intercepto_libre=True, recorte_negativos=False, rango_patrones_positivos=[.15, 3.])
    round_error = max(abs((-.436013-a)+(2.391484-100*b)*u) for u in [0., x.max()/100])
    assert round_error < 2.8e-7
    assert np.isclose(a+b*23.5362444, .12685229121222963, atol=1e-12, rtol=0)
    selected.update(coeficientes_normalizados_u=[float(a), float(100*b)],
                    error_maximo_redondeo_presentacion_ug_mL=float(round_error))
    (OUT / "modelo_seleccionado.json").write_text(json.dumps(selected, ensure_ascii=False, indent=2)+"\n")
    full = a+b*x
    records = [dict(muestra=i, referencia_ug_mL=float(c[i]), I680=float(d["mean"][i, 10]), delta_I680=float(x[i]),
                    DE_I680=float(d["sd"][i, 10]), prediccion_ajuste_completo=float(full[i]),
                    prediccion_LOO=float(pred[i-1]) if i else "", error_LOO=float(err[i-1]) if i else "",
                    error_relativo_LOO_pct=float(100*err[i-1]/c[i]) if i else "") for i in train]
    write_csv("extractos_muestras.csv", records)
    reps = [dict(muestra=i, referencia_ug_mL=float(c[i]), adquisicion=r+1, I680=float(d["reps"][i, r, 10]),
                 delta_I680=float(d["reps"][i, r, 10]-d["blank"][10])) for i in train for r in range(3)]
    write_csv("extractos_adquisiciones.csv", reps)
    regions = [dict(region="0.15–3.00", **metrics(c[1:], err))]
    for start in range(0, 20, 4):
        ref = c[1:][start:start+4]
        regions.append(dict(region=f"{ref[0]:.2f}–{ref[-1]:.2f}", **metrics(ref, err[start:start+4])))
    assert np.isclose(regions[0]["RMSE_ug_mL"], float(original["RMSE"]), atol=1e-12, rtol=0)
    write_csv("errores_regiones.csv", regions)

    quantity, cultures, _ = algae.load()
    ad = cultures["AO"]
    ao, ao_reps = [], []
    for i in range(10):
        raw = ad["raw"][i, :, 10]
        net = raw-ad["blank"][10]
        ao.append(dict(muestra=f"AO{i+1:02}", cantidad_relativa=float(quantity[i]), I680=float(raw.mean()),
                       blanco_medio=float(ad["blank"][10]), delta_I680=float(net.mean()), DE_I680=float(raw.std(ddof=1)),
                       C_equiv_lineal=float(a+b*net.mean()), DE_C_solo_lecturas=float(abs(b)*raw.std(ddof=1)),
                       C_con_blanco_original_sensibilidad=float(a+b*(raw.mean()-d["blank"][10])),
                       estado="sin cuantificación validada; inferior al menor patrón positivo"))
        for r in range(3):
            ao_reps.append(dict(muestra=f"AO{i+1:02}", adquisicion=r+1, I680=float(raw[r]), delta_I680=float(net[r]), C_equiv_lineal=float(a+b*net[r])))
    assert sum(r["C_equiv_lineal"] < 0 for r in ao) == 9
    assert all(r["delta_I680"] > 0 and r["delta_I680"] < x[1:].min() for r in ao)
    assert all(r["C_equiv_lineal"] < .15 for r in ao)
    write_csv("AO_muestras.csv", ao)
    write_csv("AO_adquisiciones.csv", ao_reps)
    kd, _ = kaolin.load()
    k = kd["90°"]
    krows = [dict(preparacion=g, kaolin_nominal_g_L=float(kaolin.LOAD[i]), clorofila_nominal_ug_mL=float(kaolin.CHLA[i]),
                  delta_I680=float(k["mean"][i, 10]-k["mean"][0, 10]), DE_I680=float(k["sd"][i, 10]),
                  C_equiv_lineal=float(a+b*(k["mean"][i, 10]-k["mean"][0, 10])), DE_C_lecturas=float(abs(b)*k["sd"][i, 10]),
                  estado="aplicación exploratoria entre series; no recuperación validada") for i, g in enumerate(kaolin.GROUPS)]
    write_csv("kaolin_90_muestras.csv", krows)
    blanks = [dict(serie=label, archivo_indice=i+1, media_680=float(values.mean()), SD_interna_10_lecturas=float(values.std(ddof=1)))
              for label, values_set in [("calibracion", d["blanks"][:, :, 10]), ("AO", ad["blanks"][:, :, 10])]
              for i, values in enumerate(values_set)]
    write_csv("blancos_680.csv", blanks)
    sources = [ROOT / n for n in ["dataCruda.zip", "reCalibration_20samples.xlsx", "resultados/modelos.csv",
                "algas/cultivos.zip", "algas/cultivos.xlsx", "kaolin/kaolin+extracto.zip"]]
    summary = dict(fecha="2026-11-20", modelo=selected, error_global=regions[0], blanco_AO=float(ad["blank"][10]),
                   AO_medias_negativas=9, AO10_C_equiv=ao[-1]["C_equiv_lineal"], incertidumbre="SD de adquisiciones con parámetros/blanco fijos; no incertidumbre total",
                   fuentes_sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources})
    (OUT / "resumen.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2)+"\n")
    extract_figures(c, d, a, b, pred, regions)
    culture_figures(quantity, ad, ao, a, b, x, c)
    other_figures(c, data, ad, kd, a, b, krows)
    carry_figures()
    reports(summary, regions, ao)
    print(json.dumps(dict(figuras=len(CATALOG), RMSE=regions[0]["RMSE_ug_mL"], MAPE=regions[0]["MAPE_pct"], AO_negativos=9), ensure_ascii=False))


if __name__ == "__main__":
    main()
