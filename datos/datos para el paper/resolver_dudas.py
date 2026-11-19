"""Check the three paper questions without replacing previous analysis outputs.

Run with the environment in requirements.txt. Only resultados/dudas/ is written.
The zero-intercept quadratic is a sensitivity check, not a replacement model.
"""
import csv
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

import analizar_extractos as calibration

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "algas"))
import aplicar_modelo_90_680 as algae

OUT = ROOT / "resultados/dudas"
PETROL, YELLOW, CORAL, GRAY = "#264653", "#E9C46A", "#E76F51", "#6C757D"


def read_csv(path):
    with path.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(name, rows):
    with (OUT / name).open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def metrics(reference, error):
    assert np.all(reference > 0), "Relative error is undefined for the blank"
    relative = 100 * error / reference
    return dict(n=len(reference), RMSE_ug_mL=float(np.sqrt(np.mean(error**2))),
                MAE_ug_mL=float(np.mean(abs(error))), sesgo_ug_mL=float(error.mean()),
                MAPE_pct=float(np.mean(abs(relative))),
                RMSRE_pct=float(np.sqrt(np.mean(relative**2))),
                max_error_absoluto_ug_mL=float(np.max(abs(error))),
                max_error_relativo_absoluto_pct=float(np.max(abs(relative))))


def save_figure(fig, name):
    for fmt in ("png", "svg"):
        fig.savefig(OUT / f"{name}.{fmt}", dpi=300, bbox_inches="tight")
    calibration.plt.close(fig)


def residual_figure(reference, error, regions):
    plt = calibration.plt
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.6))
    fig.subplots_adjust(left=.07, right=.99, top=.84, bottom=.31, wspace=.34)
    for ax, values, label in [(axes[0], error, "Prediction − reference (µg/mL)"),
                               (axes[1], 100*error/reference, "Signed relative error (%)")]:
        ax.scatter(reference, values, color=PETROL, s=28)
        ax.axhline(0, color=GRAY, lw=.8)
        ax.set(xlabel="Reference concentration (µg/mL)", ylabel=label, xlim=(0, 3.15))
    axes[0].set_title("A  Absolute units · LOO")
    axes[1].set_title("B  Relative to each reference")
    axes[1].annotate(f"0.15 µg/mL: {100*error[0]/reference[0]:+.1f}%", (reference[0], 100*error[0]/reference[0]),
                     xytext=(.55, 52), arrowprops=dict(arrowstyle="->", color=CORAL), fontsize=8, color=CORAL)
    bars = regions[1:]
    axes[2].bar(np.arange(5), [r["MAPE_pct"] for r in bars], color=PETROL)
    axes[2].set(xticks=np.arange(5), xticklabels=[r["region_ug_mL"] for r in bars],
                ylabel="Mean absolute relative error (%)", xlabel="Reference region (µg/mL)", ylim=(0, 26))
    axes[2].tick_params(axis="x", labelrotation=30, labelsize=8)
    axes[2].set_title("C  Four samples per region")
    for i, r in enumerate(bars):
        axes[2].text(i, r["MAPE_pct"]+.5, f'{r["MAPE_pct"]:.1f}%', ha="center", fontsize=8)
    for ax in axes:
        ax.grid(axis="y", alpha=.14, color=GRAY)
        ax.set_axisbelow(True)
    fig.suptitle("90° · 680 nm · fixed quadratic · internal leave-one-sample-out errors", fontsize=12)
    fig.text(.07, .04, "Each prediction excludes that sample's three acquisitions; the session blank remains available.\n"
             "All 20 positive standards retained. No relative error is assigned to the zero blank.\n"
             "These are internal prediction errors, not a 95% uncertainty interval or a detection limit.", fontsize=8)
    save_figure(fig, "01_errores_y_regiones")


def ao_figures(rows, coefficients, zero, first_signal):
    plt = calibration.plt
    q = np.array([float(r["cantidad_relativa"]) for r in rows])
    x = np.array([float(r["delta_I680"]) for r in rows])
    y = np.array([float(r["C_equiv_extracto_ug_mL"]) for r in rows])
    sx = np.array([float(r["DE_I680_3_adquisiciones"]) for r in rows])
    sy = np.array([float(r["DE_C_solo_adquisiciones"]) for r in rows])
    neg = y < 0
    fig, axes = plt.subplots(2, 2, figsize=(11, 8.5))
    fig.subplots_adjust(left=.09, right=.98, top=.91, bottom=.16, wspace=.29, hspace=.43)
    for ax, values, sd, label in [(axes[0, 0], x, sx, "Medium-subtracted I680 (a.u.)"),
                                  (axes[0, 1], y, sy, "Extract-equivalent estimate (µg/mL)"),
                                  (axes[1, 1], y, sy, "Extract-equivalent estimate (µg/mL)")]:
        for mask, color, marker in [(neg, CORAL, "v"), (~neg, PETROL, "o")]:
            if ax is axes[1, 1]:
                mask = mask & (q <= .2)
            ax.errorbar(q[mask], values[mask], yerr=sd[mask], color=color, marker=marker,
                        ms=4, ls="none", capsize=2)
        ax.set(xscale="log", xlabel="Relative culture amount", ylabel=label)
        ax.axhline(0, color=GRAY, lw=.8)
    axes[0, 0].axhline(first_signal, color=GRAY, ls="--", lw=.8)
    axes[0, 0].text(.0022, first_signal+1, "Lowest positive extract signal", fontsize=8, color=GRAY)
    axes[0, 0].set(title="A  All ten signals are positive", ylim=(-1, 28))
    axes[0, 1].axhline(.15, color=GRAY, ls="--", lw=.8)
    axes[0, 1].text(.0022, .157, "Lowest positive reference: 0.15 µg/mL", fontsize=8, color=GRAY)
    axes[0, 1].set(title="B  Frozen model · all AO levels", ylim=(-.023, .26))
    ax = axes[1, 0]
    grid = np.linspace(0, 4.4, 200)
    ax.plot(grid, algae.apply(grid, coefficients), color=PETROL, ls="--", lw=1.2)
    ax.axhline(0, color=GRAY, lw=.8)
    ax.axvline(zero, color=GRAY, ls=":", lw=1)
    ax.axvspan(0, zero, color=YELLOW, alpha=.18)
    for mask, color, marker in [(neg, CORAL, "v"), (~neg & (q <= .2), PETROL, "o")]:
        ax.scatter(x[mask], y[mask], color=color, marker=marker, s=26, zorder=3)
    ax.annotate(f"f(0) = {coefficients[0]:.4f}", (0, coefficients[0]), xytext=(.3, -.020), fontsize=8)
    ax.text(zero+.12, -.016, f"f(x) = 0\nx = {zero:.3f} a.u.\nNot a detection limit", fontsize=8, color=GRAY)
    ax.set(title="C  Why a positive signal can give a negative estimate",
           xlabel="Medium-subtracted I680 (a.u.)", ylabel="Model estimate (µg/mL)",
           xlim=(-.1, 4.4), ylim=(-.023, .021))
    axes[1, 1].set(title="D  Low AO levels · enlarged", ylim=(-.009, .027), xlim=(.0016, .29))
    for i in range(7):
        axes[1, 1].annotate(f"{i+1:02}", (q[i], y[i]), xytext=(3, -12 if neg[i] else 7),
                            textcoords="offset points", fontsize=8, color=CORAL if neg[i] else PETROL)
    for ax in axes.flat:
        ax.grid(axis="y", alpha=.14, color=GRAY)
    fig.suptitle("AO · 90° / 680 nm · diagnosing negative model estimates", fontsize=12)
    fig.text(.09, .025, "Coral triangles: AO01–AO04, negative model outputs; petroleum circles: other AO levels. No values are clipped.\n"
             "A, B and D: mean ± SD of three acquisitions, with blank and coefficients fixed; these are not prediction intervals.\n"
             "All AO signals lie between the blank and the lowest positive extract standard: low-end quantification is unvalidated.", fontsize=8)
    save_figure(fig, "02_AO_negativos")

    fig, ax = plt.subplots(figsize=(7.2, 4.7))
    fig.subplots_adjust(left=.13, right=.97, top=.86, bottom=.26)
    ax.errorbar(q, x, yerr=sx, color=PETROL, marker="o", ms=4, ls="none", capsize=3)
    ax.axhline(0, color=GRAY, lw=.8)
    ax.set(xscale="log", xlabel="Relative culture amount", ylabel="Medium-subtracted I680 (a.u.)",
           title="AO culture · measured fluorescence-channel response", ylim=(-.6, 27))
    ax.grid(axis="y", alpha=.14, color=GRAY)
    fig.text(.13, .04, "90°; 430 nm excitation; 680 nm channel. Mean ± SD of three acquisitions per level.\n"
             "The session-medium blank is fixed. The horizontal axis has no absolute concentration unit.\n"
             "A positive response does not establish a validated chlorophyll concentration.", fontsize=8)
    save_figure(fig, "03_AO_respuesta_recomendada")


def main():
    OUT.mkdir(exist_ok=True, parents=True)
    plt = calibration.plt
    plt.rcParams.update({"font.size": 9, "svg.fonttype": "none", "axes.spines.top": False, "axes.spines.right": False})
    calibration.self_check()
    known = metrics(np.array([1., 2.]), np.array([.1, -.2]))
    assert np.isclose(known["MAPE_pct"], 10.) and np.isclose(known["RMSE_ug_mL"], np.sqrt(.025))
    c, data = calibration.load()
    d = data["90°"]
    j = list(calibration.W).index(680)
    frozen = next(r for r in json.loads((ROOT / "resultados/coeficientes.json").read_text())
                  if r["geometria"] == "90°" and r["grupo"] == "un_canal")
    coefficients = np.array(frozen["parametros"])
    signal = d["mean"][:, j] - frozen["blancos"]["680"]
    model = dict(kind="cuadratico", alpha=0., x=np.c_[signal, signal**2])
    train = np.arange(len(c))
    prediction = calibration.cv(model, c, train)
    explicit = np.array([calibration.predict(model, calibration.fit(model, c, train[train != i]), [i])[0]
                         for i in train[1:]])
    stored = [r for r in read_csv(ROOT / "resultados/residuos_correccion_fondo.csv")
              if r["geometria"] == "90°" and r["referencia_nm"] == "solo_blanco" and r["funcion"] == "cuadratico"]
    assert len(stored) == 20 and np.allclose(prediction, explicit, atol=1e-10, rtol=0)
    assert np.allclose(prediction, [float(r["prediccion_LOO"]) for r in stored], atol=1e-10, rtol=0)
    assert np.allclose(calibration.fit(model, c, train), coefficients, atol=1e-12, rtol=0)
    error = prediction-c[1:]
    per_sample = [dict(muestra=i, referencia_ug_mL=c[i], prediccion_LOO_ug_mL=prediction[i-1],
                       error_LOO_ug_mL=error[i-1], error_relativo_pct=100*error[i-1]/c[i]) for i in train[1:]]
    regions = [dict(region_ug_mL="0.15–3.00", **metrics(c[1:], error))]
    for start in range(0, 20, 4):
        subset = slice(start, start+4)
        regions.append(dict(region_ug_mL=f"{c[1:][subset][0]:.2f}–{c[1:][subset][-1]:.2f}",
                            **metrics(c[1:][subset], error[subset])))
    write_csv("errores_por_muestra.csv", per_sample)
    write_csv("errores_por_region.csv", regions)

    scaled = coefficients*np.array([1., 100., 10000.])
    rounded = np.array([-.01715, .78497, 1.10942])
    grid = np.linspace(0, signal.max(), 10001)
    assert np.allclose(algae.apply(grid, coefficients), algae.apply(grid/100, scaled), atol=1e-12, rtol=0)
    difference = rounded-scaled
    candidates = [0., signal.max()/100]
    vertex = -difference[1]/(2*difference[2])
    if 0 < vertex < candidates[1]:
        candidates.append(vertex)
    rounding_error = float(np.max(abs(algae.apply(np.array(candidates), difference))))
    assert np.isclose(rounding_error, np.max(abs(algae.apply(grid/100, rounded)-algae.apply(grid, coefficients))))
    assert rounding_error < 1e-5
    zero = float(max(np.roots(coefficients[::-1])))
    assert abs(algae.apply(np.array([zero]), coefficients)[0]) < 1e-12

    # Diagnostic only: forcing zero changes the model, not just its notation.
    design = np.c_[signal/100, (signal/100)**2]
    anchored = np.linalg.lstsq(design, c, rcond=None)[0]
    anchored_loo = np.array([design[i] @ np.linalg.lstsq(design[train != i], c[train != i], rcond=None)[0]
                             for i in train[1:]])
    assert np.all(anchored > 0), "The diagnostic fit must be monotone and nonnegative for nonnegative signals"
    assert np.isclose(metrics(c[1:], error)["RMSE_ug_mL"], .09378949925080231)
    write_csv("comparacion_anclaje_cero.csv", [dict(muestra=i, referencia_ug_mL=c[i],
              modelo_actual_LOO=prediction[i-1], modelo_anclado_LOO=anchored_loo[i-1]) for i in train[1:]])

    rows = read_csv(ROOT / "algas/resultados/predicciones_AO.csv")
    assert len(rows) == 10 and [r["muestra"] for r in rows] == [f"AO{i:02}" for i in range(1, 11)]
    _, cultures, _ = algae.load()
    ad = cultures["AO"]
    x = ad["mean"][:, j]-ad["blank"][j]
    y = algae.apply(x, coefficients)
    assert np.allclose(x, [float(r["delta_I680"]) for r in rows], atol=1e-12, rtol=0)
    assert np.allclose(y, [float(r["C_equiv_extracto_ug_mL"]) for r in rows], atol=1e-12, rtol=0)
    assert np.all(x > 0) and np.all(x < signal[1:].min())
    assert np.array_equal(y < 0, x < zero) and np.sum(y < 0) == 4
    diagnostic = [dict(muestra=r["muestra"], cantidad_relativa=r["cantidad_relativa"],
                       intensidad_neta_680=x[i], DE_intensidad=r["DE_I680_3_adquisiciones"],
                       C_equiv_modelo_actual_ug_mL=y[i], DE_C_solo_lecturas=r["DE_C_solo_adquisiciones"],
                       modelo_actual_negativo=bool(y[i] < 0),
                       bajo_senal_menor_patron_positivo=bool(x[i] < signal[1:].min()),
                       C_equiv_anclado_solo_diagnostico_ug_mL=float(np.array([x[i]/100, (x[i]/100)**2]) @ anchored))
                  for i, r in enumerate(rows)]
    write_csv("AO_diagnostico.csv", diagnostic)
    summary = dict(fecha="2026-11-19", configuracion="90°/680 nm", errores_globales=regions[0],
                   coeficientes_normalizados_u_deltaI_div_100=scaled.tolist(),
                   coeficientes_redondeados=rounded.tolist(), max_error_redondeo_ug_mL=rounding_error,
                   raiz_positiva_deltaI=zero, concentracion_predicha_blanco=float(coefficients[0]),
                   menor_senal_patron_positivo=float(signal[1:].min()),
                   blanco_calibracion=float(frozen["blancos"]["680"]), blanco_AO=float(ad["blank"][j]),
                   medias_tres_blancos_calibracion=d["blanks"][:, :, j].mean(1).tolist(),
                   medias_tres_blancos_AO=ad["blanks"][:, :, j].mean(1).tolist(),
                   SD_entre_tres_medias_blanco_AO=float(ad["blanks"][:, :, j].mean(1).std(ddof=1)),
                   AO_negativos=[r["muestra"] for r in diagnostic if r["modelo_actual_negativo"]],
                   AO_bajo_menor_senal_patron_positivo=int(np.sum(x < signal[1:].min())),
                   ajuste_anclado_solo_diagnostico=dict(coeficientes_u=anchored.tolist(),
                       errores=metrics(c[1:], anchored_loo-c[1:]),
                       primer_patron_predicho_LOO=float(anchored_loo[0])),
                   LOD_LOQ="No establecidos; tres archivos de blanco y adquisiciones técnicas no validan el método",
                   fuentes_sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in [ROOT/"dataCruda.zip", ROOT/"reCalibration_20samples.xlsx",
                                             ROOT/"resultados/coeficientes.json", ROOT/"resultados/residuos_correccion_fondo.csv",
                                             ROOT/"algas/cultivos.zip", ROOT/"algas/cultivos.xlsx",
                                             ROOT/"algas/resultados/predicciones_AO.csv"]})
    (OUT / "resumen.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    residual_figure(c[1:], error, regions)
    ao_figures(rows, coefficients, zero, float(signal[1:].min()))
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
