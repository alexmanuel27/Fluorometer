"""Historical analysis: the active model since 2026-11-20 is the global linear
90°/680 nm model in lineal_90_680/generar_entrega.py (relative to the paper root).
This module preserves the previous analysis and is also reused for its readers.

Extract-only calibration. Run with Python + numpy, scipy, matplotlib.

Reads the ZIP and the external XLSX without changing either. Outputs are replaced
only under resultados/. The three acquisitions are averaged before any split.
"""
from pathlib import Path
from itertools import combinations
from collections import Counter
import csv
import hashlib
import io
import json
import platform
import sys
import zipfile
import xml.etree.ElementTree as ET

import numpy as np
import scipy
from scipy.optimize import minimize_scalar
from scipy.stats import spearmanr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "resultados"
W = np.array([410, 435, 460, 485, 510, 535, 560, 585, 610, 645,
              680, 705, 730, 760, 810, 860, 900, 940])
GEOMETRIES = ["90°", "180°"]
COLORS = {"90°": "#264653", "180°": "#E76F51"}


def write_csv(name, records):
    records = list(records)
    with (OUT / name).open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def load():
    ns = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(ROOT / "reCalibration_20samples.xlsx") as z:
        xml = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
        cells = {c.get("r"): c.find("s:v", ns).text
                 for c in xml.findall(".//s:c", ns) if c.find("s:v", ns) is not None}
        ids = [int(cells[f"A{r}"]) for r in range(3, 23)]
        c = np.r_[0., [float(cells[f"D{r}"]) for r in range(3, 23)]]
    assert ids == list(range(1, 21)) and np.allclose(c, np.arange(21) * .15)
    data = {}
    with zipfile.ZipFile(ROOT / "dataCruda.zip") as z:
        for g in GEOMETRIES:
            def rows(name):
                return list(csv.DictReader(io.StringIO(z.read(f"dataCruda/{g}/{name}").decode())))
            raw, internal = [], []
            for i in ids:
                rs = [rows(f"sample{i:02}_{r}-spectrum.csv") for r in range(1, 4)]
                assert all([int(x["wavelength_nm"]) for x in r] == list(W) for r in rs)
                assert all(int(x["n"]) == 10 for r in rs for x in r)
                raw.append([[float(x["mean_intensity"]) for x in r] for r in rs])
                internal.append([[float(x["standard_deviation"]) for x in r] for r in rs])
            blanks = np.array([[[float(r[f"{w}_nm"]) for w in W]
                                for r in rows(f"blank{b}.csv") if r["reading"].isdigit()]
                               for b in range(1, 4)])
            darkname = next(n.rsplit("/", 1)[1] for n in z.namelist()
                            if n.startswith(f"dataCruda/{g}/dark-reference") and n.endswith(".csv"))
            dark = np.array([[float(r[f"{w}_nm"]) for w in W]
                             for r in rows(darkname) if r["reading"].isdigit()])
            raw = np.array(raw)
            assert raw.shape == (20, 3, 18) and blanks.shape == (3, 10, 18)
            assert dark.shape == (10, 18) and np.isfinite(raw).all()
            reps = np.concatenate([blanks.mean(1)[None, :, :], raw])
            sd = np.concatenate([blanks.std(1, ddof=1)[None, :, :], np.array(internal)])
            data[g] = dict(reps=reps, internal=sd, mean=reps.mean(1),
                           sd=reps.std(1, ddof=1), blank=blanks.mean((0, 1)),
                           dark=dark, blanks=blanks)
    return c, data


def quality(g, w):
    if g == "180°" and w in (410, 435):
        return "excluido: valores próximos a 2^32"
    if w == 485:
        return "excluido: variabilidad excesiva dentro y entre adquisiciones"
    return "utilizable"


def catalogue(g, d):
    """Feature definitions use only measured intensities and the session blank."""
    m, b = d["mean"], d["blank"]
    candidates = []
    valid = [j for j, w in enumerate(W) if quality(g, w) == "utilizable"]
    delta = m - b
    logs = np.log(m / b)

    def add(kind, js, features, terms, alpha=0.):
        name = kind + "_" + "_".join(str(W[j]) for j in js)
        if alpha:
            name += f"_a{alpha:g}"
        candidates.append(dict(name=name, kind=kind, channels=[int(W[j]) for j in js],
                               x=np.asarray(features), terms=terms, alpha=alpha,
                               complexity=(len(js), len(terms), name)))

    for j in valid:
        x, z, w = delta[:, j], logs[:, j], W[j]
        add("lineal", [j], x[:, None], [f"dI{w}"])
        add("cuadratico", [j], np.c_[x, x*x], [f"dI{w}", f"dI{w}^2"])
        add("log", [j], z[:, None], [f"ln(I{w}/B{w})"])
    for j, k in combinations(valid, 2):
        add("dos_lineal", [j, k], delta[:, [j, k]], [f"dI{W[j]}", f"dI{W[k]}"])
        add("dos_log", [j, k], logs[:, [j, k]],
            [f"ln(I{W[j]}/B{W[j]})", f"ln(I{W[k]}/B{W[k]})"])
    for red in (680, 730):
        j = list(W).index(red)
        for k in valid:
            if j != k:
                add("emision_log", [j, k], np.c_[delta[:, j], logs[:, k]],
                    [f"dI{red}", f"ln(I{W[k]}/B{W[k]})"])
        if red == 680 or g == "90°":
            # Two-parameter forward response; inverted without clipping predictions.
            add("saturacion", [j], delta[:, j, None], ["A", "k"])
    red_indices = [list(W).index(w) for w in (680,705,730)]
    for j in red_indices:
        for k in valid:
            if j != k:
                ratio = (m[:,j]/m[:,k])/(b[j]/b[k]) - 1
                term = f"(I{W[j]}/I{W[k]})/(B{W[j]}/B{W[k]})-1"
                add("cociente", [j,k], ratio[:,None], [term])
                add("cociente_cuadratico", [j,k], np.c_[ratio,ratio**2], [term,f"({term})^2"])
    for j,k in combinations(red_indices,2):
        x,z = delta[:,j],delta[:,k]
        add("dos_cuadratico", [j,k], np.c_[x,z,x*x,x*z,z*z],
            [f"dI{W[j]}",f"dI{W[k]}",f"dI{W[j]}^2",f"dI{W[j]}*dI{W[k]}",f"dI{W[k]}^2"])
    for kind, x, terms in (("ridge", delta[:, valid], [f"dI{W[j]}" for j in valid]),
                           ("ridge_log", logs[:, valid], [f"ln(I{W[j]}/B{W[j]})" for j in valid])):
        for alpha in (.1, 1., 10., 100.):
            add(kind, valid, x, terms, alpha)
    assert len({m["name"] for m in candidates}) == len(candidates)
    return candidates


def fit(model, c, train):
    x = model["x"][train]
    y = c[train]
    if model["kind"] == "saturacion":
        signal = x[:, 0]
        def loss(logk):
            q = -np.expm1(-np.exp(logk) * y)
            a = (q @ signal) / (q @ q)
            return np.sum((signal - a*q)**2)
        opt = minimize_scalar(loss, bounds=(np.log(1e-5), np.log(3.)), method="bounded")
        k = np.exp(opt.x)
        q = -np.expm1(-k * y)
        a = (q @ signal) / (q @ q)
        return np.array([a, k])
    mu, scale = x.mean(0), x.std(0)
    scale = np.where(scale > 1e-12, scale, 1.)
    xx = np.c_[np.ones(len(train)), (x - mu) / scale]
    if model["alpha"]:
        penalty = np.diag(np.r_[0., np.repeat(model["alpha"], x.shape[1])])
        coef = np.linalg.solve(xx.T @ xx + penalty, xx.T @ y)
    else:
        coef = np.linalg.lstsq(xx, y, rcond=None)[0]
    beta = coef[1:] / scale
    return np.r_[coef[0] - mu @ beta, beta]


def predict(model, params, indices=None, features=None):
    x = model["x"][indices] if features is None else np.asarray(features)
    if model["kind"] == "saturacion":
        a, k = params
        with np.errstate(invalid="ignore", divide="ignore"):
            return -np.log1p(-x[:, 0]/a) / k
    return params[0] + x @ params[1:]


def cv(model, c, train):
    """Exact LOO for OLS via PRESS; ridge scaling and nonlinear fits are refitted."""
    train = np.asarray(train)
    test = train[train != 0]
    if model["alpha"] or model["kind"] == "saturacion":
        predictions = np.array([predict(model, fit(model, c, train[train != i]), [i])[0]
                                for i in test])
    else:
        x = model["x"][train]
        scale = x.std(0)
        xx = np.c_[np.ones(len(train)), (x - x.mean(0))/np.where(scale > 1e-12, scale, 1.)]
        pinv = np.linalg.pinv(xx)
        hat = np.sum(xx * pinv.T, axis=1)
        pos = np.flatnonzero(train != 0)
        if np.any(1-hat[pos] < 1e-8):
            return np.full(len(test), np.inf)
        residual = c[train] - xx @ (pinv @ c[train])
        predictions = c[test] - residual[pos] / (1-hat[pos])
    return predictions


def metrics(y, pred):
    if not np.isfinite(pred).all():
        return dict(RMSE=float("inf"), MAE=float("inf"), bias=float("inf"), max_error=float("inf"), Q2=float("-inf"))
    e = pred - y
    return dict(RMSE=float(np.sqrt(np.mean(e*e))), MAE=float(np.mean(abs(e))),
                bias=float(e.mean()), max_error=float(abs(e).max()),
                Q2=float(1-np.sum(e*e)/np.sum((y-y.mean())**2)))


def choose(models, errors, indices, simple=True):
    mse = np.mean(errors*errors, axis=1)
    eligible = [i for i in indices if np.isfinite(mse[i])]
    best = min(eligible, key=lambda i: mse[i])
    if not simple:
        return best
    tolerance = np.std(errors[best]**2, ddof=1)/np.sqrt(errors.shape[1])
    return min((i for i in eligible if mse[i] <= mse[best] + tolerance),
               key=lambda i: models[i]["complexity"][:2] + (mse[i], models[i]["name"]))


def evaluate(g, c, d):
    models = catalogue(g, d)
    allrows = np.arange(len(c))
    fixed_pred = np.array([cv(m, c, allrows) for m in models])
    errors = fixed_pred - c[1:]
    pools = dict(un_canal=[i for i,m in enumerate(models) if len(m["channels"]) == 1],
                 multicanal=[i for i,m in enumerate(models) if len(m["channels"]) > 1],
                 todos=list(range(len(models))),
                 emision=[i for i,m in enumerate(models)
                          if set(m["channels"]) <= ({680,705,730} if g=="90°" else {680})])
    selections = {pool: choose(models, errors, ids) for pool, ids in pools.items()}
    minimums = {pool: choose(models, errors, ids, False) for pool, ids in pools.items()}
    nested = {pool: [] for pool in pools}
    chosen = {pool: [] for pool in pools}
    for held in range(1, len(c)):
        train = allrows[allrows != held]
        inner_errors = np.array([cv(m, c, train) for m in models]) - c[train[train != 0]]
        for pool, ids in pools.items():
            selected = choose(models, inner_errors, ids)
            nested[pool].append(float(predict(models[selected], fit(models[selected], c, train), [held])[0]))
            chosen[pool].append(models[selected]["name"])
    table = []
    for i, m in enumerate(models):
        p = fit(m, c, allrows)
        r = dict(geometria=g, modelo=m["name"], canales_nm=";".join(map(str,m["channels"])),
                 n_canales=len(m["channels"]), n_terminos=len(m["terms"]),
                 terminos=json.dumps(m["terms"],ensure_ascii=False),
                 parametros=json.dumps(p.tolist()),alpha=m["alpha"],
                 **metrics(c[1:], fixed_pred[i]),
                 blanco_predicho=float(predict(m,p,[0])[0]),
                 seleccionado=";".join(k for k,v in selections.items() if v==i))
        table.append(r)
    summary = {}
    for pool in pools:
        idx = selections[pool]
        summary[pool] = dict(modelo_final=models[idx]["name"],
                             minimo_RMSE=models[minimums[pool]]["name"],
                             CV_fijo=metrics(c[1:], fixed_pred[idx]),
                             CV_anidada=metrics(c[1:], np.array(nested[pool])),
                             frecuencia_seleccion=dict(Counter(chosen[pool])))
    return dict(models=models, fixed=fixed_pred, table=table, summary=summary,
                nested=nested, chosen=chosen, selections=selections, minimums=minimums)


def self_check():
    c = np.linspace(0,3,21)
    x = np.c_[np.expm1(c), c*c + c]
    model = dict(x=x, kind="lineal", alpha=0.)
    train = np.arange(21)
    fast = cv(model,c,train)
    slow = np.array([predict(model,fit(model,c,train[train!=i]),[i])[0] for i in train[1:]])
    assert np.allclose(fast,slow,atol=1e-9), "PRESS must match explicit held-out fits"
    model.update(kind="saturacion", x=(100*(-np.expm1(-.4*c)))[:,None])
    params = fit(model,c,train)
    assert np.allclose(predict(model,params,train),c,atol=1e-5)
    assert np.isnan(predict(model,params,features=[[101]]))[0], "No clipping outside inverse domain"


def main():
    OUT.mkdir(exist_ok=True)
    (OUT/"figuras").mkdir(exist_ok=True)
    self_check()
    c, data = load()
    ref = [dict(muestra=i, concentracion_ug_mL=float(v),
                origen="blanco medido" if i == 0 else f"Sheet1!D{i+2}") for i,v in enumerate(c)]
    write_csv("concentraciones.csv",ref)
    replicate_rows, mean_rows, channel_rows = [], [], []
    for g,d in data.items():
        for i, conc in enumerate(c):
            for j,w in enumerate(W):
                mean_rows.append(dict(geometria=g,muestra=i,concentracion_ug_mL=conc,nm=w,
                                      intensidad=d["mean"][i,j],DE_3_adquisiciones=d["sd"][i,j],
                                      blanco=d["blank"][j],delta_I=d["mean"][i,j]-d["blank"][j],
                                      calidad=quality(g,w)))
                for r in range(3):
                    replicate_rows.append(dict(geometria=g,muestra=i,concentracion_ug_mL=conc,
                                               replica=r+1,nm=w,intensidad=d["reps"][i,r,j],
                                               DE_interna_10_lecturas=d["internal"][i,r,j],n=10,
                                               calidad=quality(g,w)))
        for j,w in enumerate(W):
            m = d["mean"][1:,j]
            channel_rows.append(dict(geometria=g,nm=w,calidad=quality(g,w),blanco=d["blank"][j],
                                     DE_3_blancos=d["sd"][0,j],delta_a_3=d["mean"][-1,j]-d["blank"][j],
                                     Pearson=float(np.corrcoef(c[1:],m)[0,1]),
                                     Spearman=float(spearmanr(c[1:],m).statistic),
                                     CV_mediana_3_adquisiciones_pct=float(np.median(d["sd"][1:,j]/m)*100),
                                     CV_mediana_interna_pct=float(np.median(
                                         d["internal"][1:,:,j][d["reps"][1:,:,j]>0] /
                                         d["reps"][1:,:,j][d["reps"][1:,:,j]>0])*100),
                                     ceros_DE_adquisicion=int(np.sum(d["sd"][1:,j]==0)),
                                     n_medias_mayor_1e9=int(np.sum(d["reps"][:,:,j]>1e9))))
    write_csv("adquisiciones.csv",replicate_rows)
    write_csv("medias.csv",mean_rows)
    write_csv("canales.csv",channel_rows)
    analyses = {}
    for g,d in data.items():
        print(f"Evaluating {g}...",flush=True)
        analyses[g] = evaluate(g,c,d)
    write_csv("modelos.csv",sorted([r for a in analyses.values() for r in a["table"]],
                                   key=lambda r:(r["geometria"],r["RMSE"])))
    predictions, coeffs = [], []
    for g,a in analyses.items():
        for pool in a["summary"]:
            idx = a["selections"][pool]
            model = a["models"][idx]
            params = fit(model,c,np.arange(21))
            coeffs.append(dict(geometria=g,grupo=pool,modelo=model["name"],
                               terminos=model["terms"],parametros=params.tolist(),
                               alpha=model["alpha"],canales=model["channels"],
                               blancos={str(w):float(data[g]["blank"][list(W).index(w)]) for w in model["channels"]},
                               intensidad_min={str(w):float(data[g]["mean"][:,list(W).index(w)].min()) for w in model["channels"]},
                               intensidad_max={str(w):float(data[g]["mean"][:,list(W).index(w)].max()) for w in model["channels"]}))
            for i in range(1,21):
                predictions.append(dict(geometria=g,grupo=pool,muestra=i,referencia_ug_mL=c[i],
                                        prediccion_CV_anidada=a["nested"][pool][i-1],
                                        error_CV_anidada=a["nested"][pool][i-1]-c[i],
                                        modelo_elegido_en_pliegue=a["chosen"][pool][i-1],
                                        prediccion_CV_modelo_final=a["fixed"][idx,i-1]))
    write_csv("predicciones.csv",predictions)
    (OUT/"coeficientes.json").write_text(json.dumps(coeffs,ensure_ascii=False,indent=2))
    summary = {g:a["summary"] for g,a in analyses.items()}
    (OUT/"resumen.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    manifest = dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__,
                    matplotlib=matplotlib.__version__,platform=platform.platform(),
                    sources={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest()
                             for n in ["dataCruda.zip","reCalibration_20samples.xlsx"]},
                    candidates={g:len(a["models"]) for g,a in analyses.items()},
                    dark_all_zero={g:bool(np.all(d["dark"]==0)) for g,d in data.items()})
    (OUT/"trazabilidad.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    figures(c,data,analyses)
    report(c,data,analyses,channel_rows)
    print(json.dumps(summary,ensure_ascii=False,indent=2))


def save(fig, name):
    fig.savefig(OUT/"figuras"/f"{name}.png",dpi=300,bbox_inches="tight")
    fig.savefig(OUT/"figuras"/f"{name}.svg",bbox_inches="tight")
    plt.close(fig)


def figures(c,data,analyses):
    plt.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False,
                         "axes.prop_cycle":plt.cycler(color=["#264653","#2A9D8F","#E9C46A","#E76F51","#6C757D"]),
                         "svg.fonttype":"none","font.family":"DejaVu Sans"})
    fig,axs = plt.subplots(2,2,figsize=(10.2,8.3),layout="constrained")
    for col,g in enumerate(GEOMETRIES):
        d,a = data[g],analyses[g]
        ax = axs[0,col]
        for w,color,marker in [(680,"#264653","o"),(730,"#E76F51","^")]:
            j = list(W).index(w)
            ax.errorbar(c,d["mean"][:,j]-d["blank"][j],yerr=d["sd"][:,j],
                        color=color,marker=marker,ls="none",ms=4,capsize=2,label=f"{w} nm")
        model = next(m for m in a["models"] if m["name"]=="cuadratico_680")
        signal = np.linspace(0,model["x"][:,0].max(),200)
        conc = predict(model,fit(model,c,np.arange(21)),features=np.c_[signal,signal**2])
        ax.plot(conc,signal,color="#264653",lw=1.2,label="680 nm quadratic calibration")
        ax.axhline(0,c="#6C757D",lw=.6)
        ax.set(xlim=(-.06,3.1),xlabel="Reference Chl a (µg/mL)",ylabel="Intensity − session blank (a.u.)",
               title=f"{'AB'[col]}  {g}: red-channel response")
        ax.legend(frameon=False,fontsize=8)
        ax = axs[1,col]
        for pool,color,marker,label in [("un_canal","#264653","o","Single-channel selection"),
                                        ("multicanal","#E76F51","^","Multichannel selection")]:
            pred = a["nested"][pool]
            rmse = a["summary"][pool]["CV_anidada"]["RMSE"]
            ax.scatter(c[1:],pred,color=color,marker=marker,s=28,
                       label=f"{label}\nNested RMSE = {rmse:.3f} µg/mL")
        ax.plot([0,3.15],[0,3.15],c="#6C757D",ls="--",lw=1)
        ax.set(xlim=(0,3.15),ylim=(0,3.25),xlabel="Reference Chl a (µg/mL)",
               ylabel="Held-out prediction (µg/mL)",title=f"{'CD'[col]}  {g}: concentration prediction")
        ax.legend(frameon=False,fontsize=8,loc="upper left")
    save(fig,"01_figura_principal")

    for g,d in data.items():
        fig,axs = plt.subplots(6,3,figsize=(11,15),layout="constrained")
        for j,(w,ax) in enumerate(zip(W,axs.flat)):
            if quality(g,w)!="utilizable":
                ax.text(.5,.5,"Excluded from modelling\n"+("~2³² readings" if w!=485 else "Unstable readings"),
                        transform=ax.transAxes,ha="center",va="center",color="#E76F51")
            else:
                ax.errorbar(c[1:],d["mean"][1:,j],yerr=d["sd"][1:,j],fmt="o",ms=3,
                            color=COLORS[g],capsize=2)
                ax.errorbar([0],[d["mean"][0,j]],yerr=[d["sd"][0,j]],fmt="s",ms=5,c="#6C757D",capsize=3)
            ax.set(title=f"{w} nm",xlabel="Chl a (µg/mL)",ylabel="Intensity (a.u.)",xlim=(-.1,3.1))
        fig.suptitle(f"{g} · 18 channels · mean ± SD of 3 acquisitions; square: blank",fontsize=13)
        save(fig,"02_canales_"+g.replace("°",""))

    fig,axs = plt.subplots(1,2,figsize=(10.2,3.7),layout="constrained",sharey=True)
    for g,ax in zip(GEOMETRIES,axs):
        a = analyses[g]
        for pool,color,marker,label in [("un_canal","#264653","o","Single channel"),
                                        ("multicanal","#E76F51","^","Multichannel")]:
            ax.scatter(c[1:],np.array(a["nested"][pool])-c[1:],c=color,marker=marker,label=label,s=24)
        ax.axhline(0,color="#6C757D",lw=.8)
        ax.set(title=g,xlabel="Reference Chl a (µg/mL)",ylabel="Nested-CV error (µg/mL)")
        ax.legend(frameon=False,fontsize=8)
    save(fig,"03_residuos")


def report(c,data,analyses,channels):
    # shortcut: interpretation describes this supplied series; revise before replacing the sources.
    text = ["# Calibración de extractos para el paper",
            "Fecha del análisis: 15 de noviembre de 2026. Excitación: LED azul de 430 nm, según Alex.",
            "## Resultado y elección",
            "**Para este conjunto, elegiría 90° y 680 nm con una calibración cuadrática de concentración.** "
            "A 90°, añadir canales reduce muy poco el error de un modelo fijado y empeora el error de la selección multicanal anidada. "
            "A 180°, la mejor alternativa sencilla para predecir concentración usa ln(I810/B810): su señal disminuye y no se interpreta como fluorescencia. "
            "Si se requiere una señal compatible con fluorescencia a 180°, conservar 680 nm y su calibración cuadrática. "
            "La preferencia por 90° se refiere a estos extractos y estas sesiones, sin demostrar una superioridad general del ángulo.",
            "## Fuentes, blanco y unidad experimental",
            "Se leen exclusivamente `../dataCruda.zip` y el Excel externo `../reCalibration_20samples.xlsx`, "
            "Sheet1!A3:D22. Se usa D como concentración de referencia suministrada: 20 niveles de 0,15 a 3,00 µg/mL. "
            "No se recalculan las referencias a partir de A664/A648 ni se cambia el Excel. "
            "El blanco medido se incorpora como una fila de concentración **0 µg/mL** en cada geometría. "
            "Cero es su concentración nominal; su intensidad medida se conserva y no se sustituye por cero. "
            "Se define Bλ como la media de los tres blancos de sesión y ΔIλ = Iλ − Bλ.",
            "Hay 120 archivos de muestra (20 × 3 × 2), seis blancos de diez lecturas y dos dark de diez lecturas. "
            "Cada archivo de muestra contiene media, DE y n=10, no las diez lecturas individuales. "
            "Se promedian las tres adquisiciones antes del ajuste: 21 puntos por geometría, incluido un solo punto de blanco. "
            "Las 60 adquisiciones de extracto por geometría no son 60 concentraciones independientes. "
            "Las barras representan DE entre tres adquisiciones; no incluyen incertidumbre de concentración ni del blanco compartido. "
            "El ZIP y la carpeta extraída coincidían en sus 128 CSV al iniciar el análisis. "
            "El ZIP coincide con el de la revisión de noviembre anterior; este análisis amplía la búsqueda y la validación, sin añadir muestras.",
            "## Control de calidad",
            "Se conservan todos los valores originales. Se excluyen de los predictores 410 y 435 nm a 180° por registros próximos a 2³², "
            "incluidos blancos. No se intentan reconstruir esos datos ni se presupone que sean saturación óptica. "
            "485 nm se excluye en ambas geometrías por variabilidad excesiva. "
            "Los dos dark contienen únicamente ceros: no permiten cuantificar el ruido físico; no se aplica una corrección oscura inventada. "
            "Hay DE nulas por cuantización, por lo que no se pondera por 1/DE² ni se interpreta DE=0 como precisión perfecta. "
            "Los datos y sus banderas están en `adquisiciones.csv`, `medias.csv` y `canales.csv`.",
            "## Qué canales muestran una respuesta compatible con fluorescencia",
            "La selección espectral parte de extractos, no de células intactas. Como referencia externa, "
            "Greipel et al. observaron, con excitación de 430 nm en extractos metanólicos, un máximo de emisión en 673 nm "
            "y un hombro alrededor de 730 nm [1]. Esto orienta a revisar 680, 705 y 730 nm, "
            "sin fijar el máximo exacto de este extracto cuyo solvente no está documentado aquí. "
            "El AS7265x tiene bandas nominales de 20 nm FWHM [2]; las intensidades de canales diferentes "
            "no equivalen a un espectro de potencia óptica corregido.",
            "| Geometría | Canal (nm) | Blanco (u.a.) | ΔI a 3 µg/mL (u.a.) | Spearman, 20 extractos |",
            "|---|---:|---:|---:|---:|"]
    for r in channels:
        if r["nm"] in (435,460,645,680,705,730,760,810) and r["calidad"]=="utilizable":
            text.append(f"| {r['geometria']} | {r['nm']} | {r['blanco']:.3f} | {r['delta_a_3']:+.3f} | {r['Spearman']:.4f} |")
    text += ["**90°:** 680 y 730 nm son los candidatos principales: aumento grande, casi monotónico y repetible sobre un blanco bajo. "
             "705 nm puede aportar información de la zona roja. 645 y 760 nm también predicen concentración, "
             "pero su correlación no identifica un pigmento ni prueba fluorescencia pura. "
             "El aumento en canales más alejados, como 810–940 nm, no se atribuye automáticamente a emisión de clorofila.",
             "**180°:** 680 nm es el único canal con incremento neto positivo claro a lo largo de la serie. "
             "705 y 730 nm disminuyen respecto al blanco, igual que numerosos canales visibles/NIR. "
             "Son respuestas ópticas útiles como predictores, compatibles con un fondo modificado o atenuación, "
             "sin identificar su mecanismo. Una disminución neta tampoco demuestra ausencia de una contribución fluorescente superpuesta. "
             "No se reconstruye una fluorescencia pura a partir de esa disminución sin una medición independiente del fondo.",
             "## Funciones comparadas y validación",
             f"Se comparan {len(analyses['90°']['models'])} candidatos a 90° y {len(analyses['180°']['models'])} a 180°. "
             "Se incluyen lineal y cuadrático por canal; lineal en ln(I/B); todos los pares de canales válidos en intensidad o logaritmo; "
             "680/730 con un canal logarítmico auxiliar; cocientes normalizados entre cada canal rojo (680/705/730) y canales válidos "
             "con función lineal o cuadrática; polinomios de segundo grado de dos canales rojos, con interacción; "
             "ridge con todos los canales válidos (α=0,1; 1; 10; 100), en intensidad o logaritmo; "
             "y respuesta directa de saturación ΔI=A[1−exp(−kC)] invertida, en 680 nm y además 730 nm a 90°. "
             "La saturación usa k entre 10⁻⁵ y 3 mL/µg, A positivo en estos ajustes, y devuelve inválido si la inversión no existe. "
             "No se recortan concentraciones para mejorar errores. Los modelos lineales en parámetros llevan intercepto libre; "
             "el blanco es un punto real y no una restricción de paso exacto por el origen.",
             "**LOO del modelo fijado:** se deja fuera una de las 20 muestras, se ajusta con las otras 19 y el blanco, "
             "y se predice su concentración. Se repite para cada candidato. Sirve para ordenar candidatos; "
             "el mínimo entre cientos de resultados puede ser optimista [3].",
             "**CV anidada:** en cada una de las 20 particiones externas, se repite la búsqueda mediante LOO interno "
             "solo entre las 19 muestras disponibles, conservando el blanco. Se elige por separado entre un canal, multicanal y todos. "
             "La regla de un error estándar (1-SE) admite candidatos cuyo MSE está a una SE "
             "del mínimo; dentro de ese margen prioriza menos canales, después menos términos, y después menor MSE. "
             "SE = DE de los errores cuadrados del mejor candidato / √n. Es una regla de parsimonia, no una prueba de equivalencia estadística. "
             "La normalización para ridge se calcula dentro de cada entrenamiento. "
             "Todos los errores se puntúan en concentración (µg/mL), usando únicamente las 20 muestras de extracto. "
             "El blanco permanece como referencia compartida y punto de ajuste; no se presenta como predicción independiente.",
             "| Configuración y búsqueda | Modelo final con 21 puntos | RMSE LOO, modelo fijado | RMSE CV anidada, selección | MAE CV anidada | Q² CV anidada |",
             "|---|---|---:|---:|---:|---:|"]
    for g,a in analyses.items():
        for pool in ("un_canal","multicanal","todos","emision"):
            s=a["summary"][pool]; n=s["CV_anidada"]
            label={"un_canal":"un canal","multicanal":"varios canales","todos":"búsqueda completa",
                   "emision":"zona de emisión (680 a 180°)"}[pool]
            text.append(f"| {g}, {label} | `{s['modelo_final']}` | {s['CV_fijo']['RMSE']:.4f} | {n['RMSE']:.4f} | {n['MAE']:.4f} | {n['Q2']:.4f} |")
    text += ["El RMSE anidado evalúa el procedimiento de selección: puede usar un modelo diferente en cada partición. "
             "No es un error externo garantizado para la ecuación final. Q² = 1 − Σ(Cpred−Cref)²/Σ(Cref−media de Cref)²; "
             "no es el R² de un ajuste sobre los propios datos.",
             "### Mínimos numéricos y decisión práctica",
             "A 90°, el mínimo LOO fijado es el cuadrático de dos canales, 680+730 nm (0,0921 µg/mL), "
             "frente a 0,0938 con el cuadrático de 680 nm. La ganancia es de solo 0,0017 µg/mL, "
             "con cinco términos espectrales frente a dos. La búsqueda multicanal anidada da 0,1279 µg/mL; "
             "la de un canal da 0,0938. La búsqueda completa da 0,0990 y elige 680 cuadrático en 19 de 20 particiones. "
             "**No hay una ventaja predictiva convincente de añadir canales aquí.**",
             "A 180°, el mínimo LOO fijado es el cuadrático de 810 nm (0,1017 µg/mL); "
             "ln(I810/B810) queda casi igual (0,1032) con un término menos. La regla 1-SE selecciona el logarítmico. "
             "El mejor par por mínimo numérico es ln(I535/B535)+ln(I810/B810), con 0,1022. "
             "Entre los modelos multicanal, la regla de parsimonia elige el cociente 705/730 normalizado; "
             "su procedimiento de selección da 0,1346 de RMSE anidado, frente a 0,1209 para un canal. "
             "La búsqueda de un canal cambia entre ln810 (11 particiones) y lineal460 (nueve): "
             "810 nm es una elección empírica razonable, sin estabilidad suficiente para llamarla universalmente óptima. "
             "Si se exige trabajar con el canal de incremento fluorescente 680 nm, su cuadrático da 0,1197 de LOO fijado "
             "y la selección de función en 680 da 0,1361 de RMSE anidado.",
             "## Ecuaciones finales y uso",
             "C se expresa en µg/mL, las intensidades son las medias de tres adquisiciones en las unidades originales, "
             "y ln es logaritmo natural. Deben utilizarse el blanco y los ajustes instrumentales de la calibración. "
             "Los coeficientes sin redondeo y los rangos de intensidad están en `coeficientes.json`; "
             "`modelos.csv` conserva también términos y parámetros de todos los candidatos.",
             "**90°, recomendación para fluorescencia de extracto:** con x = I680 − 0,8821683333,",
             "`C = −0,0171463961 + 0,00784968892·x + 0,000110942425·x²`.",
             "**180°, predicción empírica por señal decreciente:**",
             "`C = −0,0714331021 − 3,7628353365·ln(I810 / 216,272109)`.",
             "**180°, alternativa centrada en fluorescencia:** con x = I680 − 53,3535285667,",
             "`C = −0,0356338276 + 0,0205431738·x + 0,000307191661·x²`.",
             "El blanco figura como Cref=0, aunque las regresiones con intercepto libre predicen −0,0171, −0,0714 "
             "y −0,0356 µg/mL, respectivamente, para su intensidad media. No se convierten esos valores en ceros "
             "ni se usan como límite de detección. Si se necesita una fórmula operacional que dé exactamente cero "
             "para cualquier blanco, habría que imponer esa condición y volver a comparar las calibraciones. "
             "Estas ecuaciones se limitan a la serie 0,15–3,00 µg/mL más el blanco; no validan el intervalo entre cero y 0,15. "
             "El rango ensayado tampoco garantiza la misma exactitud relativa en todos los niveles: "
             "un error absoluto cercano a 0,1 µg/mL es grande frente al nivel inferior de 0,15. "
             "No se declara 0,15 µg/mL como límite de cuantificación demostrado.",
             "## Figura elegida para el paper",
             "**Elegir `figuras/01_figura_principal.svg`**, con cuatro paneles y una versión PNG a 300 dpi. "
             "A–B muestran 680 y 730 nm frente a concentración en cada geometría, con el blanco en cero y DE entre adquisiciones. "
             "La curva azul representa la calibración cuadrática inversa de 680 nm; no demuestra un mecanismo de saturación. "
             "C–D muestran concentración predicha frente a referencia, con predicciones externas de CV anidada "
             "para la búsqueda de un canal y la multicanal. La diagonal representa concordancia perfecta. "
             "Las escalas de intensidad de A y B son distintas y están rotuladas; C y D comparten límites. "
             "Esta figura combina evidencia espectral y utilidad de calibración sin escoger por R² visual.",
             "![Figura principal](figuras/01_figura_principal.png)",
             "**Segundo gráfico, si hay espacio:** `figuras/03_residuos.svg`. Ayuda a ver desviaciones sistemáticas "
             "y el comportamiento de las muestras 18–20, que una diagonal de buen aspecto puede ocultar. "
             "**Material suplementario:** `02_canales_90.svg` y `02_canales_180.svg`, con los 18 canales y las exclusiones explícitas. "
             "No usaría una figura con todas las curvas ajustadas ni cientos de modelos como figura principal; "
             "su comparación completa queda en las tablas CSV.",
             "### Suggested English caption",
             "Optical response and internal concentration prediction of chlorophyll a extracts under 430 nm LED excitation. "
             "(A, B) Blank-referenced intensities at 680 and 730 nm for the 90° and 180° configurations, respectively. "
             "Symbols represent means of three acquisitions and error bars show their standard deviations. "
             "The measured session blank is assigned a reference concentration of 0 µg/mL. "
             "Blue curves show inverse representations of the quadratic 680 nm concentration calibrations fitted to all calibration points. "
             "Intensity scales differ between A and B. (C, D) Held-out concentration predictions from nested leave-one-sample-out "
             "selection of single-channel and multichannel models. Each outer test set contains one complete extract sample; "
             "the shared session blank remains available for calibration. Dashed lines indicate identity. "
             "Reported errors describe internal validation within the supplied dilution series and sessions.",
             "## Alcance y límites que afectan a la conclusión",
             "Solo se analizan extractos. No se evalúan caolín, selectividad en agua natural, células intactas ni otros ensayos. "
             "Las dos geometrías se adquirieron en sesiones sucesivas, con tres blancos compartidos por sesión. "
             "No hay validación entre días, stocks o extractos independientes, y geometría y sesión están confundidas. "
             "No se conoce aquí la incertidumbre de la concentración de referencia, el solvente y la igualdad efectiva "
             "de ganancia, integración y potencia de excitación entre sesiones. "
             "La dilución de un mismo extracto hace variar conjuntamente otros pigmentos y componentes: "
             "un buen predictor no acredita selectividad química para clorofila a. "
             "Las desviaciones compartidas a alta concentración, incluida sample19, se conservan sin eliminar muestras. "
             "No se atribuye la curvatura a un mecanismo concreto ni se estima un límite de detección a partir de tres blancos. "
             "La validación anidada reduce el sesgo de selección entre funciones, pero no elimina estas dependencias experimentales.",
             "## Reproducción y archivos",
             "Desde la carpeta `datos para el paper`, ejecutar `python3 analizar_extractos.py` en un entorno "
             "con NumPy, SciPy y Matplotlib. Se regeneran los CSV, JSON, figuras e informe dentro de `resultados/`; "
             "no se modifican las fuentes ni el firmware. El script incluye comprobaciones de estructura, "
             "identificadores, concentraciones, equivalencia de PRESS con LOO explícito e inversión de una saturación conocida.",
             "- `concentraciones.csv`: referencias y blanco 0.\n"
             "- `adquisiciones.csv`: 2.268 filas, incluidas las tres adquisiciones de blanco por geometría.\n"
             "- `medias.csv`: 756 filas, 21 puntos × 18 canales × dos geometrías.\n"
             "- `canales.csv`: 36 resúmenes de tendencia, repetibilidad y calidad.\n"
             "- `modelos.csv`: todos los candidatos, parámetros y LOO de modelo fijado.\n"
             "- `predicciones.csv`: predicción, error y modelo escogido en cada partición externa.\n"
             "- `coeficientes.json`: ecuaciones seleccionadas, blancos y dominio de intensidades.\n"
             "- `resumen.json`: métricas y frecuencias de selección.\n"
             "- `trazabilidad.json`: huellas SHA-256 de las fuentes y versiones del entorno.\n"
             "- `figuras/`: figura principal, residuos y dos láminas de 18 canales, en SVG y PNG.",
             "## Referencias para la interpretación y el método",
             "1. Greipel et al. (2024). [Extraction of chlorophyll a from Tetradesmus obliquus—a method upgrade](https://link.springer.com/article/10.1007/s42977-024-00209-3). "
             "Fundamento del máximo rojo y hombro lejano en extractos; no identifica el solvente ni la composición de esta serie.\n"
             "2. ams OSRAM. [AS7265x Smart Spectral Sensor](https://ams-osram.com/de/products/sensor-solutions/ambient-light-color-spectral-proximity-sensors/ams-as7265x-smart-spectral-sensor). "
             "18 canales y anchura nominal de banda.\n"
             "3. scikit-learn. [Nested versus non-nested cross-validation](https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html). "
             "Justificación de separar selección y evaluación; el cálculo de este proyecto se implementa con NumPy/SciPy."]
    # Separate prose paragraphs while retaining contiguous Markdown table rows.
    text.insert(0, "> **Análisis histórico.** Desde el 20/11/2026, la elección actual es el lineal 90°/680 nm. [Informe vigente](../lineal_90_680/INFORME.md).")
    (OUT/"informe.md").write_text("\n\n".join(text).replace("|\n\n|","|\n|"),encoding="utf-8")


if __name__ == "__main__":
    main()
