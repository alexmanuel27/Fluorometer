"""Historical analysis: the active model since 2026-11-20 is the global linear
90°/680 nm model in lineal_90_680/generar_entrega.py (relative to the paper root).
This module preserves the previous analysis and is also reused for its readers.

Explain the frozen intensity-to-concentration conversion using AO only."""
import csv
import json
import numpy as np
import aplicar_modelo_90_680 as analysis


def main():
    out = analysis.OUT
    with (out / "predicciones.csv").open(encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f) if r["serie"] == "AO"]
    assert len(rows) == 10 and [r["muestra"] for r in rows] == [f"AO{i:02}" for i in range(1, 11)]
    meta = json.loads((out / "resumen.json").read_text())
    coefficients = np.array(meta["modelo"]["parametros"])
    quantity = np.array([float(r["cantidad_relativa"]) for r in rows])
    signal = np.array([float(r["delta_I680"]) for r in rows])
    predicted = np.array([float(r["C_equiv_extracto_ug_mL"]) for r in rows])
    assert np.allclose(analysis.apply(signal, coefficients), predicted, atol=1e-12)
    analysis.write_csv("predicciones_AO.csv", rows)
    with (analysis.ROOT.parent / "resultados/medias.csv").open(encoding="utf-8-sig") as f:
        ref = next(r for r in csv.DictReader(f) if r["geometria"] == "90°" and r["muestra"] == "1" and r["nm"] == "680")
    first_signal, first_concentration = float(ref["delta_I"]), float(ref["concentracion_ug_mL"])
    assert np.isclose(first_signal, meta["rango_delta_extractos_sin_blanco"][0])
    plt = analysis.calibration.plt
    plt.rcParams.update({"font.size":10, "svg.fonttype":"none", "axes.spines.top":False, "axes.spines.right":False})
    fig, axes = plt.subplots(1, 2, figsize=(11.3, 5.7))
    fig.subplots_adjust(left=.075, right=.98, top=.84, bottom=.28, wspace=.29)
    axes[0].errorbar(quantity, signal, yerr=[float(r["DE_I680_3_adquisiciones"]) for r in rows],
                     color="#264653", marker="o", ms=4, lw=1, capsize=2)
    axes[0].set(title="A  Lo que mide el sensor · AO", xlabel="Cantidad relativa de cultivo (sin unidad)",
                ylabel="Intensidad neta a 680 nm (u.a.)", xlim=(-.02, 1.06), ylim=(-.5, 27))
    for i, offset in [(7, (-24, 10)), (8, (-22, 10)), (9, (-30, 10))]:
        axes[0].annotate(rows[i]["muestra"], (quantity[i], signal[i]), xytext=offset,
                         textcoords="offset points", fontsize=9, color="#264653")
    low, high = np.linspace(0, first_signal, 150), np.linspace(first_signal, 34, 100)
    axes[1].plot(low, analysis.apply(low, coefficients), color="#6C757D", ls="--", lw=1.3,
                 label="Modelo entre blanco y primer extracto")
    axes[1].plot(high, analysis.apply(high, coefficients), color="#264653", lw=1.3)
    axes[1].scatter(signal, predicted, color="#264653", s=27, label="AO · resultado calculado")
    axes[1].scatter([first_signal], [first_concentration], color="#E76F51", marker="s", s=40,
                    label="Primer extracto · referencia 0,15 µg/mL")
    axes[1].annotate("AO10: 23,536 → 0,229", (signal[-1], predicted[-1]), xytext=(8, .28),
                     arrowprops=dict(arrowstyle="->", color="#264653"), fontsize=9, color="#264653")
    axes[1].set(title="B  Lo que calcula la ecuación", xlabel="Intensidad neta a 680 nm (u.a.)",
                ylabel="Concentración equivalente de extracto (µg/mL)", xlim=(-.3, 34), ylim=(-.04, .4))
    axes[1].legend(frameon=False, loc="upper left", fontsize=8)
    for ax in axes:
        ax.axhline(0, color="#6C757D", lw=.6)
        ax.grid(axis="y", color="#6C757D", alpha=.15)
    fig.suptitle("Solo AO · de la intensidad medida al resultado del modelo", fontsize=13)
    fig.text(.075, .065, "A: medias ± DE de tres adquisiciones; ejes lineales. B: cada intensidad AO entra en la ecuación de extracto.\n"
             "Los puntos AO de B son resultados calculados; su posición sobre la curva no valida concentraciones en el cultivo.", fontsize=9)
    for fmt in ("png", "svg"):
        fig.savefig(out / "figuras" / f"02_explicacion_modelo_AO.{fmt}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    paper_figure(rows, out)
    terms = [coefficients[0], coefficients[1]*signal[-1], coefficients[2]*signal[-1]**2]
    print(dict(AO10_intensidad_neta=signal[-1], terminos=terms, C_equivalente=predicted[-1]))


def paper_figure(rows, out):
    assert len(rows) == 10 and all(r["serie"] == "AO" for r in rows)
    quantity = np.array([float(r["cantidad_relativa"]) for r in rows])
    signal = np.array([float(r["delta_I680"]) for r in rows])
    predicted = np.array([float(r["C_equiv_extracto_ug_mL"]) for r in rows])
    plt = analysis.calibration.plt
    plt.rcParams.update({"font.size":10, "svg.fonttype":"none", "axes.spines.top":False, "axes.spines.right":False})
    fig, axes = plt.subplots(1, 2, figsize=(10.7, 4.9))
    fig.subplots_adjust(left=.075, right=.985, top=.87, bottom=.28, wspace=.29)
    for ax, values, sd in [(axes[0], signal, "DE_I680_3_adquisiciones"),
                            (axes[1], predicted, "DE_C_solo_adquisiciones")]:
        ax.errorbar(quantity, values, yerr=[float(r[sd]) for r in rows], color="#264653",
                     marker="o", ms=4, ls="none", capsize=2)
        ax.axhline(0, color="#6C757D", lw=.7)
        ax.set(xlabel="Relative culture amount", xlim=(-.025, 1.045))
        ax.grid(axis="y", color="#6C757D", alpha=.15)
    axes[0].set(title="A  AO · measured response", ylabel="Medium-subtracted I680 (a.u.)", ylim=(-.5, 26))
    axes[1].axhspan(-.025, .15, color="#6C757D", alpha=.08)
    axes[1].axhline(.15, color="#6C757D", ls="--", lw=.9)
    axes[1].text(.015, .175, "Lowest calibration reference: 0.15 µg/mL", fontsize=8, color="#6C757D")
    axes[1].set(title="B  Extract-referenced estimate", ylabel="Chlorophyll a equivalent (µg/mL)", ylim=(-.025, .26))
    fig.suptitle("AO culture · 90° · 430 nm excitation · 680 nm channel", fontsize=12)
    fig.text(.075, .065, "Ten culture levels; three acquisitions per level. Fixed extract-calibration coefficients and session-medium blank.\n"
             "Error bars show acquisition SD only. Equivalents are not independently validated culture concentrations.\n"
             "Shading indicates estimates below the lowest positive calibration reference, not a detection limit.", fontsize=8)
    for fmt in ("png", "svg"):
        fig.savefig(out / "figuras" / f"03_AO_paper.{fmt}", dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
