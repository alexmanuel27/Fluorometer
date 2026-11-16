"""Compare the six extract/kaolin preparations, without fitting a concentration model.

Python + NumPy + Matplotlib. Sources stay unchanged; resultados/ is regenerated.
"""
from pathlib import Path
import csv
import hashlib
import io
import json
import platform
import sys
import zipfile

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "resultados"
W = np.array([410,435,460,485,510,535,560,585,610,645,680,705,730,760,810,860,900,940])
GEOMETRIES = ["90°","180°"]
GROUPS = ["blanco_etanol","extracto_puro","kaolin_b","kaolin_a",
          "extracto+kaolin_b","extracto+kaolin_a"]
LOAD = np.array([0,0,1.25,2.5,1.25,2.5])
CHLA = np.array([0,3,0,0,3,3])
K = [0,2,3]
EK = [1,4,5]
COLORS = {"90°":"#264653","180°":"#E76F51"}
REFERENCES = [460,645,705,730,760,810,860,900,940]


def write_csv(name, rows):
    rows = list(rows)
    with (OUT/name).open("w",newline="",encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def quality(g,w):
    if g=="180°" and w in (410,435):
        return "excluido: blanco próximo a 2^32"
    if w==485:
        return "excluido: canal inestable"
    return "utilizable"


def load():
    data,inventory = {},[]
    with zipfile.ZipFile(ROOT/"kaolin+extracto.zip") as z:
        names = [n for n in z.namelist() if n.endswith(".csv") and "__MACOSX" not in n]
        assert len(names)==38
        for name in names:
            extracted = ROOT/name
            assert extracted.is_file() and extracted.read_bytes()==z.read(name), name
            info = z.getinfo(name)
            inventory.append(dict(archivo=name,fecha_ZIP_sin_zona=str(info.date_time),
                                  sha256=hashlib.sha256(z.read(name)).hexdigest()))
        for g in GEOMETRIES:
            raw,internal = [],[]
            for group in GROUPS:
                spectra = []
                for rep in range(1,4):
                    name = f"kaolin+extracto/{g}/{group}{rep:02}-spectrum.csv"
                    rows = list(csv.DictReader(io.StringIO(z.read(name).decode())))
                    assert [int(r["wavelength_nm"]) for r in rows]==list(W)
                    assert all(int(r["n"])==10 for r in rows)
                    spectra.append(rows)
                raw.append([[float(r["mean_intensity"]) for r in rows] for rows in spectra])
                internal.append([[float(r["standard_deviation"]) for r in rows] for rows in spectra])
            name = next(n for n in names if n.startswith(f"kaolin+extracto/{g}/dark-reference"))
            rows = list(csv.DictReader(io.StringIO(z.read(name).decode())))
            dark = np.array([[float(r[f"{w}_nm"]) for w in W]
                             for r in rows if r["reading"].isdigit()])
            raw,internal = np.array(raw),np.array(internal)
            assert raw.shape==internal.shape==(6,3,18) and dark.shape==(10,18)
            assert np.isfinite(raw).all() and (raw>=0).all() and (internal>=0).all()
            data[g] = dict(raw=raw,internal=internal,mean=raw.mean(1),
                           sd=raw.std(1,ddof=1),se=raw.std(1,ddof=1)/np.sqrt(3),dark=dark)
    return data,inventory


def contrasts(d):
    """Independent acquisition groups; covariance is retained at the shared zero-load point."""
    m,v = d["mean"],d["se"]**2
    result = []
    for level,(k,ek) in enumerate(zip(K,EK)):
        f0 = m[1]-m[0]
        particle = m[k]-m[0]
        direct = m[ek]-m[0]
        matched = m[ek]-m[k]
        interaction = matched-f0
        particle_se = np.sqrt(v[k]+v[0]) if level else np.zeros(18)
        interaction_se = np.sqrt(v[ek]+v[k]+v[1]+v[0]) if level else np.zeros(18)
        result.append(dict(load=LOAD[k],f0=f0,particle=particle,direct=direct,matched=matched,
                           interaction=interaction,particle_se=particle_se,
                           direct_se=np.sqrt(v[ek]+v[0]),matched_se=np.sqrt(v[ek]+v[k]),
                           interaction_se=interaction_se))
    return result


def background_proxy(raw,blank,reference):
    j = list(W).index(reference)
    beta = blank[10]/blank[j]
    return raw[...,10]-beta*raw[...,j],beta


def normalized(values):
    """Zero = ethanol; one = pure extract. This is a response scale, not concentration."""
    means = values.mean(1)
    span = means[1]-means[0]
    assert abs(span)>1e-9
    return (means-means[0])/span,values.std(1,ddof=1)/abs(span)


def diagnostics(g,d):
    raw,b = d["raw"],d["mean"][0]
    features = [("I680",raw[:,:,10]),("I730",raw[:,:,12]),
                ("I680/I730",raw[:,:,10]/raw[:,:,12]),
                ("I680/I705",raw[:,:,10]/raw[:,:,11]),
                ("I680/I810",raw[:,:,10]/raw[:,:,14]),
                ("I730/I705",raw[:,:,12]/raw[:,:,11]),
                ("ln(I810)",np.log(raw[:,:,14])),
                ("ln(I645)",np.log(raw[:,:,9]))]
    beta = {}
    for ref in REFERENCES:
        values,beta[ref] = background_proxy(raw,b,ref)
        features.append((f"I680 - (B680/B{ref})*I{ref}",values))
    rows = []
    for name,values in features:
        score,_ = normalized(values)
        rows.append(dict(geometria=g,indicador=name,
                         caolin_b_pct=100*score[2],caolin_a_pct=100*score[3],
                         mezcla_b_pct=100*score[4],mezcla_a_pct=100*score[5],
                         escala="etanol=0; extracto puro=100; no es concentración"))
    return rows,beta


def self_check():
    assert np.isclose(.1/.04,2.5) and np.isclose(.1/.08,1.25)
    base = np.ones(18)*20
    effect = np.arange(18)+1
    particle = np.arange(18)*3
    m = np.array([base,base+effect,base+particle,base+2*particle,
                  base+particle+effect,base+2*particle+effect])
    d = dict(mean=m,se=np.ones((6,18)))
    cc = contrasts(d)
    assert all(np.allclose(r["matched"],effect) for r in cc)
    assert all(np.allclose(r["interaction"],0) for r in cc)
    assert np.all(cc[0]["interaction_se"]==0)
    # A common changing background must cancel without fitting the mixture.
    b = np.ones(18)*10
    b[10]=4
    b[14]=20
    simulated = np.stack([b,b+np.eye(1,18,10)[0]*50,
                          b*.2,b*.2+np.eye(1,18,10)[0]*50])
    signal,beta = background_proxy(simulated,b,810)
    assert np.allclose(signal,[0,50,0,50]) and np.isclose(beta,.2)
    assert np.allclose(normalized(np.array([[2,2,2],[5,5,5],[8,8,8]]))[0],[0,1,2])


def save(fig,name):
    for fmt in ("png","svg"):
        fig.savefig(OUT/"figuras"/f"{name}.{fmt}",dpi=300,bbox_inches="tight")
    plt.close(fig)


def figures(data):
    plt.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False,
                         "axes.prop_cycle":plt.cycler(color=["#264653","#2A9D8F","#E9C46A","#E76F51","#6C757D"]),
                         "svg.fonttype":"none"})
    x = np.array([0,1.25,2.5])
    fig,axs = plt.subplots(2,2,figsize=(10.5,8),layout="constrained")
    for ax,g,letter in zip(axs[0],GEOMETRIES,"AB"):
        d=data[g]
        for ids,color,marker,label in [(K,"#6C757D","s","No extract"),(EK,"#2A9D8F","o","Extract: 3 µg/mL")]:
            ax.errorbar(x,d["mean"][ids,10],yerr=d["sd"][ids,10],color=color,marker=marker,
                        ms=5,capsize=3,label=label)
        ax.set(title=f"{letter}  {g}: measured 680 nm intensity",xlabel="Nominal kaolin (g/L)",
               ylabel="Intensity (a.u.)",xticks=x,ylim=(0,112))
        ax.legend(frameon=False,fontsize=9)
    for ax,corrected,letter in [(axs[1,0],False,"C"),(axs[1,1],True,"D")]:
        for g,d in data.items():
            values = background_proxy(d["raw"],d["mean"][0],810)[0] if corrected else d["raw"][:,:,10]
            score,sd = normalized(values)
            for ids,ls,marker,label in [(EK,"-","o",f"{g}, extract"),(K,"--","s",f"{g}, no extract")]:
                ax.errorbar(x,100*score[ids],yerr=100*sd[ids],color=COLORS[g],ls=ls,
                            marker=marker,capsize=3,ms=4,label=label)
        for y in (0,100):ax.axhline(y,c="#6C757D",lw=.7)
        ax.set(title=f"{letter}  "+("680 nm with the 810 nm background model" if corrected else "680 nm response relative to pure extract"),
               xlabel="Nominal kaolin (g/L)",ylabel="Response (pure extract = 100%)",xticks=x,
               ylim=(-100,124) if not corrected else (-12,124))
        ax.legend(frameon=False,fontsize=8,loc="lower left" if not corrected else "center left")
    save(fig,"01_figura_principal")

    fig,axs = plt.subplots(2,2,figsize=(10.5,7.3),layout="constrained")
    for col,g in enumerate(GEOMETRIES):
        d=data[g]
        ax=axs[0,col]
        for ids,color,marker,label in [(K,"#6C757D","s","No extract"),(EK,"#2A9D8F","o","Extract: 3 µg/mL")]:
            ax.errorbar(x,d["mean"][ids,12],yerr=d["sd"][ids,12],c=color,marker=marker,capsize=3,label=label)
        ax.set(title=f"{g}: measured 730 nm intensity",ylabel="Intensity (a.u.)",xlabel="Nominal kaolin (g/L)",xticks=x,ylim=(0,240))
        ax.legend(frameon=False,fontsize=8)
        ax=axs[1,col]
        cc=contrasts(d)
        for j,color,marker in [(10,"#264653","o"),(12,"#E76F51","^")]:
            ax.errorbar(x,[r["matched"][j] for r in cc],yerr=[r["matched_se"][j] for r in cc],
                        c=color,marker=marker,capsize=3,label=f"{W[j]} nm")
        ax.axhline(0,c="#6C757D",lw=.7)
        ax.set(title=f"{g}: extract-associated contrast",xlabel="Nominal kaolin (g/L)",
               ylabel="Mixture − matched control\n(a.u.)",xticks=x,ylim=(-65,125))
        ax.legend(frameon=False,fontsize=8)
    save(fig,"02_canales_rojos_y_contrastes")
    for g,d in data.items():
        fig,axs=plt.subplots(6,3,figsize=(11,15),layout="constrained")
        for j,(w,ax) in enumerate(zip(W,axs.flat)):
            if quality(g,w)!="utilizable":
                ax.text(.5,.5,"Excluded from interpretation\n"+("~2³² blank" if w!=485 else "Unstable channel"),
                        transform=ax.transAxes,ha="center",va="center",fontsize=9,color="#E76F51")
            else:
                for ids,color,marker in [(K,"#6C757D","s"),(EK,"#2A9D8F","o")]:
                    ax.errorbar(x,d["mean"][ids,j],yerr=d["sd"][ids,j],c=color,marker=marker,
                                ms=3,capsize=2,lw=1)
            ax.set(title=f"{w} nm",xlabel="Kaolin (g/L)",ylabel="Intensity (a.u.)",xticks=x)
        fig.suptitle(f"{g} · mean ± SD, three acquisitions · green: extract; grey: no extract",fontsize=12)
        save(fig,"03_18_canales_"+g.replace("°",""))
    spectra_figure(data)


def spectra_figure(data):
    """All 18 channels, including flagged readings; ethanol subtraction only."""
    plt.rcParams.update({"font.size":10,"axes.spines.top":False,
                         "axes.spines.right":False,"svg.fonttype":"none"})
    styles = [
        ("Etanol", "#6C757D", ":", "s"),
        ("Extracto puro", "#264653", "-", "o"),
        ("Caolín b · 1,25 g/L", "#2A9D8F", "--", "^"),
        ("Caolín a · 2,50 g/L", "#E76F51", "--", "v"),
        ("Extracto + caolín b", "#2A9D8F", "-", "^"),
        ("Extracto + caolín a", "#E76F51", "-", "v"),
    ]
    fig,axs=plt.subplots(2,2,figsize=(13,9.5))
    fig.subplots_adjust(left=.085,right=.98,top=.92,bottom=.26,hspace=.5,wspace=.24)
    for col,g in enumerate(GEOMETRIES):
        m=data[g]["mean"]
        corrected=m-m[0]
        assert np.allclose(corrected[0],0)
        for row,values in enumerate((m,corrected)):
            ax=axs[row,col]
            for i,(label,color,ls,marker) in enumerate(styles):
                ax.plot(W,values[i],label=label,color=color,ls=ls,marker=marker,
                        ms=3.5,lw=1.25,markerfacecolor="white" if i in (2,3) else color)
            ax.set_yscale("log" if row==0 else "symlog",**({} if row==0 else {"linthresh":5}))
            if row==1:
                ax.set_yticks([-100,-10,0,10,100,1000] if g=="90°" else
                             [-1e10,-1e8,-1e6,-1e4,-100,0,100])
            ax.axvspan(478,492,color="#E9C46A",alpha=.22,zorder=0)
            if g=="180°":
                for w in (410,435):ax.axvspan(w-7,w+7,color="#6C757D",alpha=.18,zorder=0)
            if row==1:ax.axhline(0,color="#6C757D",lw=.7,zorder=0)
            ax.set(title=f"{'ABCD'[row*2+col]}  {g} · "+("Intensidad original" if row==0 else "Resta del blanco de etanol"),
                   xlabel="Longitud de onda (nm)",ylabel="Intensidad (u.a.)" if row==0 else "I − blanco (u.a.)",
                   xticks=W,xlim=(400,950))
            ax.tick_params(axis="x",rotation=55,labelsize=8)
            ax.grid(axis="y",alpha=.15,color="#6C757D")
    fig.suptitle("Extracto y caolín · seis preparaciones · media de tres adquisiciones",fontsize=14,y=.99)
    handles,labels=axs[0,0].get_legend_handles_labels()
    fig.legend(handles,labels,loc="lower center",bbox_to_anchor=(.53,.11),ncol=3,frameon=False,fontsize=10)
    fig.text(.085,.035,
             "Arriba: escala logarítmica. Abajo: escala logarítmica con signo y zona lineal entre −5 y +5 u.a.\n"
             "Gris: blanco anómalo a 180° (410/435 nm). Amarillo: canal inestable (485 nm).\n"
             "Blanco: media del etanol de cada geometría. Las regiones señaladas se conservan para mostrar los datos, sin validarlas.",
             fontsize=9,va="bottom")
    save(fig,"04_espectros_raw_y_blanco")


def main():
    OUT.mkdir(exist_ok=True)
    (OUT/"figuras").mkdir(exist_ok=True)
    self_check()
    data,inventory=load()
    write_csv("inventario_fuentes.csv",inventory)
    write_csv("preparaciones.csv",[dict(preparacion=group,clorofila_nominal_ug_mL=CHLA[i],
                                        caolin_nominal_g_L=LOAD[i],
                                        masa_caolin_g=0 if i<2 else .1,
                                        volumen_preparacion_mL="" if i<2 else (80 if i in (2,4) else 40))
                                    for i,group in enumerate(GROUPS)])
    reps,means,changes,diags,coefs,summary=[],[],[],[],[],{}
    for g,d in data.items():
        for i,group in enumerate(GROUPS):
            for j,w in enumerate(W):
                common=dict(geometria=g,preparacion=group,clorofila_nominal_ug_mL=CHLA[i],
                            caolin_nominal_g_L=LOAD[i],nm=w,calidad=quality(g,w))
                means.append(dict(**common,media=d["mean"][i,j],DE_3_adquisiciones=d["sd"][i,j],
                                  EE_media=d["se"][i,j]))
                for r in range(3):
                    reps.append(dict(**common,replica=r+1,intensidad=d["raw"][i,r,j],
                                     DE_interna=d["internal"][i,r,j],n_lecturas_internas=10))
        for cc in contrasts(d):
            for j,w in enumerate(W):
                f0=cc["f0"][j]
                changes.append(dict(geometria=g,caolin_g_L=cc["load"],nm=w,calidad=quality(g,w),
                                    contraste_extracto_sin_caolin=f0,
                                    efecto_caolin_sin_extracto=cc["particle"][j],EE_efecto_caolin=cc["particle_se"][j],
                                    mezcla_menos_etanol=cc["direct"][j],EE_mezcla_menos_etanol=cc["direct_se"][j],
                                    mezcla_menos_caolin=cc["matched"][j],EE_mezcla_menos_caolin=cc["matched_se"][j],
                                    interaccion=cc["interaction"][j],EE_interaccion=cc["interaction_se"][j],
                                    respuesta_directa_pct=100*cc["direct"][j]/f0 if abs(f0)>1e-9 else "",
                                    contraste_emparejado_pct=100*cc["matched"][j]/f0 if abs(f0)>1e-9 else ""))
        diagnostic,beta=diagnostics(g,d)
        diags.extend(diagnostic)
        coefs.extend(dict(geometria=g,referencia_nm=ref,beta=val,
                          formula=f"S = I680 - {val:.12g} * I{ref}",
                          obtenido_de="solo las tres adquisiciones de etanol") for ref,val in beta.items())
        summary[g]=dict(F0_680=float(d["mean"][1,10]-d["mean"][0,10]),
                         indicadores={r["indicador"]:{k:float(r[k]) for k in
                                       ("caolin_b_pct","caolin_a_pct","mezcla_b_pct","mezcla_a_pct")} for r in diagnostic},
                         beta_680_810=beta[810],dark_todo_cero=bool(np.all(d["dark"]==0)))
    write_csv("adquisiciones.csv",reps)
    write_csv("medias.csv",means)
    write_csv("contrastes.csv",changes)
    write_csv("diagnosticos.csv",diags)
    write_csv("coeficientes_fondo.csv",coefs)
    comparison=[]
    previous=ROOT.parent/"resultados/medias.csv"
    with previous.open(encoding="utf-8-sig") as f:
        old=list(csv.DictReader(f))
    for g,d in data.items():
        r=next(r for r in old if r["geometria"]==g and r["muestra"]=="20" and r["nm"]=="680")
        old_delta=float(r["delta_I"])
        comparison.append(dict(geometria=g,contraste_680_serie_anterior=old_delta,
                               contraste_680_extracto_actual=summary[g]["F0_680"],
                               cambio_pct=100*(summary[g]["F0_680"]/old_delta-1),
                               nota="referencias nominales de 3 µg/mL; sesiones diferentes; no aplicar calibración anterior como validada"))
    write_csv("comparacion_entre_sesiones.csv",comparison)
    (OUT/"resumen.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    metadata=dict(analisis="2026-11-15",fecha_dark_en_archivos="2026-11-10",python=sys.version,
                  numpy=np.__version__,matplotlib=matplotlib.__version__,platform=platform.platform(),
                  fuente_sha256=hashlib.sha256((ROOT/"kaolin+extracto.zip").read_bytes()).hexdigest(),
                  medias_serie_anterior_sha256=hashlib.sha256(previous.read_bytes()).hexdigest(),
                  usuario=dict(excitacion_nm=430,mismos_LED_ganancia_integracion_entre_geometrias=True,
                               agitacion_antes_de_cada_lectura=True,espera_tras_agitacion_s=None,
                               clorofila_nominal_extracto_ug_mL=3,masa_caolin_g=.1,
                               volumen_a_mL=40,volumen_b_mL=80),
                  independencia="tres adquisiciones por preparación; réplicas de preparación no documentadas",
                  nota_fondo="coeficientes del blanco; bandas auxiliares revisadas tras ver los datos; prueba exploratoria sin validación externa")
    (OUT/"trazabilidad.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2))
    figures(data)
    report(data,summary,comparison)
    print(json.dumps(summary,ensure_ascii=False,indent=2))


def report(data,summary,comparison):
    # shortcut: interpretation is specific to this six-preparation assay; revise before replacing its sources.
    def row(g,key):return summary[g]["indicadores"][key]
    def line(r):return " | ".join(f"{r[k]:.2f}" for k in ("caolin_b_pct","caolin_a_pct","mezcla_b_pct","mezcla_a_pct"))
    text=["# Extracto con partículas de caolín: elección de geometría",
          "Análisis: 15 de noviembre de 2026. Los nombres de los dark indican adquisiciones del 10 de noviembre.",
          "## Conclusión para estas muestras",
          "**Elegiría 90° y 680 nm como señal principal de fluorescencia del extracto en presencia de caolín.** "
          "Es la combinación que conserva la respuesta con menos tratamiento: las mezclas cambian aproximadamente +1,4–1,5% "
          "y el caolín sin extracto produce solo +0,07–0,35% de la respuesta del extracto puro. "
          "**180° aporta información complementaria sobre el fondo y la atenuación**, pero la resta convencional del blanco "
          "no conserva la respuesta a caolín constante: la señal neta de 680 cae aproximadamente 23–31%. "
          "Una resta de fondo escalada mediante un canal auxiliar mejora mucho esa estabilidad en este ensayo. "
          "Es una opción para desarrollar, sin sustituir todavía la elección más sencilla de 90°.",
          "## Diseño y fuentes",
          "Se lee `../kaolin+extracto.zip`, que contiene 36 espectros (seis preparaciones × tres adquisiciones × dos geometrías) "
          "y dos dark. Los 38 CSV coinciden exactamente con la carpeta extraída, que se conserva intacta. "
          "Cada espectro guarda media, DE y n=10 por canal; las diez lecturas originales no están presentes. "
          "Las tres adquisiciones se tratan como repeticiones de lectura de una preparación; no hay tres preparaciones independientes documentadas.",
          "Alex confirma el mismo LED azul de 430 nm y los mismos ajustes de ganancia e integración entre 90° y 180°. "
          "Confirma agitación antes de cada lectura; el tiempo entre agitación y medición no fue especificado. "
          "Los valores numéricos de los ajustes, corriente y volumen realmente medido en la cámara no están incluidos en estos CSV.",
          "| Preparación | Clorofila nominal (µg/mL) | Caolín nominal (g/L) | Composición indicada |",
          "|---|---:|---:|---|",
          "| Etanol | 0 | 0 | Etanol sin extracto ni caolín |",
          "| Extracto puro | 3 | 0 | Extracto sin caolín |",
          "| Caolín b | 0 | 1,25 | 0,1 g en 80 mL de etanol |",
          "| Caolín a | 0 | 2,50 | 0,1 g en 40 mL de etanol |",
          "| Extracto + caolín b | 3 | 1,25 | 0,1 g en 80 mL del extracto |",
          "| Extracto + caolín a | 3 | 2,50 | 0,1 g en 40 mL del extracto |",
          "Las dos mezclas conservan nominalmente 3 µg/mL de clorofila: cambiar 40 por 80 mL de un mismo extracto "
          "no cambia esa concentración. Las cargas de caolín son masa/volumen de preparación, no una medida de NTU/FNU ni de material efectivamente suspendido. "
          "Esto es un contraste factorial de dos matrices (con/sin extracto) y tres cargas, **no una nueva calibración de concentración**. "
          "No se entrenan clasificadores ni regresiones de clorofila con solo los niveles 0 y 3.",
          "## Qué se compara",
          "Sea B el etanol, E el extracto puro, K el caolín en etanol y EK la mezcla con la misma carga. "
          "Se calculan por canal: F₀=E−B; P=K−B; D=EK−B; Fₖ=EK−K; e interacción H=EK−K−E+B. "
          "D/F₀ mide conservación de la respuesta con blanco habitual; Fₖ/F₀ compara la contribución asociada a añadir extracto "
          "frente a un control de partículas. **Fₖ es un contraste entre preparaciones, no fluorescencia pura corregida:** "
          "la absorción, dispersión u otras interacciones pueden cambiar al añadir extracto.",
          "Se muestran medias y DE entre tres adquisiciones. Para diferencias de medias se calcula EE por suma de varianzas s²/3, "
          "tratando los grupos como no emparejados; el índice de réplica no acredita un emparejamiento. "
          "En carga cero se cancela la covarianza del control compartido: la interacción es exactamente cero, sin error artificial. "
          "Estas dispersiones describen repetibilidad de lectura, no incertidumbre de preparación ni confianza sobre muestras ambientales.",
          "## 680 nm: respuesta a extracto y efecto de partículas",
          "| Geometría | Preparación | Media (u.a.) | DE de tres adquisiciones |",
          "|---|---|---:|---:|"]
    for g,d in data.items():
        for i,group in enumerate(GROUPS):
            text.append(f"| {g} | {group} | {d['mean'][i,10]:.3f} | {d['sd'][i,10]:.3f} |")
    text += ["La tabla siguiente expresa respuestas normalizadas: etanol=0 y extracto puro=100. "
             "Los porcentajes **no son concentraciones recuperadas ni exactitud de concentración**. "
             "Un valor negativo en un control significa supresión del fondo, no una falsa fluorescencia positiva.",
             "| Geometría e indicador | Caolín b (%) | Caolín a (%) | Mezcla b (%) | Mezcla a (%) |",
             "|---|---:|---:|---:|---:|"]
    for g in GEOMETRIES:
        text.append(f"| {g}, I680 con blanco habitual | {line(row(g,'I680'))} |")
    text += ["A 90°, la señal neta del extracto sin caolín es 100,744 u.a. y permanece casi igual con partículas. "
             "A 180° es 50,072 u.a.; pasa a 38,533 y 34,652 u.a. usando el mismo blanco de etanol. "
             "La intensidad absoluta de los controles de caolín a 680 nm baja de 45,202 (etanol) a 5,999 y 3,176 u.a. "
             "Por tanto, la configuración de 180° no está midiendo solo una emisión sobre fondo constante.",
             "Restar el control de caolín de igual carga da a 180° contrastes de 77,737 y 76,678 u.a., "
             "frente a 50,072 sin partículas: alrededor de 155 y 153%. "
             "Esa aparente mejora tras restar K **no demuestra que la fluorescencia aumente un 55%**. "
             "El fondo que llega al detector ya cambia por efecto del extracto y de las partículas. "
             "A 90°, el mismo contraste se conserva en aproximadamente 101,5 y 101,1%.",
             "## El canal 730 revela por qué 180° es informativo, pero ambiguo",
             "A 90°, 730 nm aumenta de 2,432 u.a. en etanol a 110,509 en extracto puro; "
             "el caolín sin extracto queda en 4,054–5,405 y las mezclas en 114,266–117,374. "
             "Es una segunda banda roja compatible con el extracto, algo más sensible al caolín que 680 nm.",
             "A 180°, el etanol da 226,937 u.a. y el extracto puro 170,561: la respuesta neta es negativa (−56,376). "
             "Sin embargo, las mezclas dan 103,401 y 96,672, muy por encima de los controles de caolín de 22,459 y 9,729. "
             "El contraste asociado a extracto cambia de signo y llega a +80,943 y +86,943 u.a. "
             "Esto es compatible con una señal roja del extracto superpuesta a un fondo grande que se atenúa. "
             "La caída de 730 nm en extracto puro no bastaba para concluir ausencia de una contribución fluorescente. "
             "Tampoco este ensayo identifica por sí solo cuánto corresponde a emisión, transmisión u otras interacciones.",
             "En los canales azules, 90° sí aporta información de las partículas: "
             "435 nm aumenta de 781,988 u.a. en etanol a 1836,030 y 2368,112 con caolín sin extracto, "
             "mientras 680 nm queda casi al nivel del blanco. A 180°, 460 nm cae desde 7687,402 hasta 509,902 y 201,963. "
             "Estas respuestas complementan el rojo como diagnóstico de interacción con partículas; "
             "no representan por sí solas turbidez calibrada. No es necesario dividir la señal roja estable de 90° por un canal azul "
             "que cambia con las partículas para aprovechar esa información.",
             "## Corrección multicanal sencilla: prueba exploratoria",
             "Se prueba `Sⱼ = I680 − βⱼ·Iⱼ`, con `βⱼ = B680/Bⱼ`. "
             "Cada coeficiente se obtiene **solo del etanol**, sin ajustar los valores de las mezclas. "
             "La hipótesis es que una parte del fondo de 680 nm cambia proporcionalmente al canal auxiliar. "
             "Se revisan 460, 645, 705, 730, 760, 810, 860, 900 y 940 nm, y se conservan todos los resultados, "
             "sin presentar el mínimo encontrado como validación independiente. "
             "Esta hipótesis no equivale a una corrección física de filtro interno ni demuestra que el canal auxiliar esté libre de emisión.",
             f"Como ejemplo explícito a 180°: `S810 = I680 − {summary['180°']['beta_680_810']:.9f}·I810`. "
             "S810 es aproximadamente 77,076 u.a. para extracto puro, 79,721 para la mezcla b y 76,987 para la a. "
             "Se normaliza con el mismo extracto puro para comparar estabilidad de respuesta.",
             "| Geometría, fondo escalado con 810 nm | Caolín b (%) | Caolín a (%) | Mezcla b (%) | Mezcla a (%) |",
             "|---|---:|---:|---:|---:|"]
    for g in GEOMETRIES:
        text.append(f"| {g} | {line(row(g,'I680 - (B680/B810)*I810'))} |")
    text += ["A 180°, esta corrección conserva la respuesta del extracto en aproximadamente 103,4 y 99,9%, "
             "y deja residuos de caolín de 2,6 y 2,1% de la señal de referencia. "
             "Es una mejora clara frente al blanco fijo y apoya estudiar la información conjunta emisión/fondo. "
             "A 90° no hace falta: el canal 680 solo ya tiene menor interferencia, y la corrección con 810 añade sesgo en los controles. "
             "860 nm da residuos incluso menores a 180° en esta serie, pero está fuertemente cuantizado; "
             "no se declara óptimo por tener DE cero. 810 nm se muestra como ejemplo interpretable; "
             "la banda auxiliar definitiva necesita otra serie independiente.",
             "La normalización anterior usa el extracto de 3 µg/mL de esta misma sesión. "
             "No valida una ecuación C(S), la transferencia de los coeficientes a otras concentraciones, "
             "ni que no exista compensación fortuita entre una disminución de emisión y un aumento de luz parásita. "
             "Faltan varios niveles no nulos de clorofila cruzados con varias cargas de partículas para resolverlo.",
             "## Qué ocurre con cocientes y predictores del ensayo anterior",
             "Se revisan I680/I730, I680/I705, I680/I810, I730/I705, ln(I810) y ln(I645), "
             "además de los canales rojos directos. Los resultados están en `diagnosticos.csv`. "
             "Los cocientes se calculan en cada adquisición antes de promediar, sin coeficientes aprendidos de las mezclas. "
             "No se presupone que dividir por un canal compense la dispersión: el denominador también puede responder al caolín.",
             "Especialmente, **ln(I810), buen predictor de las diluciones puras a 180°, no es específico de clorofila en esta matriz**: "
             "con caolín sin clorofila su respuesta normalizada equivale a aproximadamente 267 y 369% de la del extracto puro. "
             "Las mezclas quedan en 266 y 303%. No deben presentarse como concentraciones calculadas, "
             "pero sí muestran que un ajuste excelente en diluciones puras puede confundir atenuación por partículas con pigmento.",
             "## Comparación entre sesiones",
             "El extracto nominal de 3 µg/mL de esta sesión tiene una respuesta neta a 680 nm menor que el extremo de 3 µg/mL "
             "de la calibración anterior. No se identifica aquí si cambió la muestra, su conservación, el blanco, la alineación u otro factor. "
             "La confirmación de ajustes iguales se refiere a 90° frente a 180° en este ensayo. "
             "Por eso las ecuaciones anteriores no se aplican como calibraciones de concentración ya validadas a estas mezclas.",
             "| Geometría | ΔI680 serie anterior | ΔI680 extracto actual | Cambio (%) |",
             "|---|---:|---:|---:|"]
    for r in comparison:
        text.append(f"| {r['geometria']} | {r['contraste_680_serie_anterior']:.3f} | {r['contraste_680_extracto_actual']:.3f} | {r['cambio_pct']:.1f} |")
    text += ["## Elección de figura para el paper",
             "**Usaría `figuras/01_figura_principal.svg`**, con cuatro paneles. A–B enseñan las lecturas reales de 680 nm "
             "con y sin extracto en cada geometría. C cuantifica el efecto del caolín con el blanco habitual. "
             "D muestra qué mejora la resta de fondo escalada con 810 nm, aplicando la misma fórmula en ambas geometrías. "
             "Así la figura no oculta la interferencia original ni presenta una corrección exploratoria como fluorescencia aislada. "
             "Barras: DE entre tres adquisiciones; en C–D la DE se escala por la diferencia entre las medias del extracto puro y del etanol, "
             "tratando esa referencia como fija para el gráfico. No incluye su incertidumbre compartida.",
             "![Figura principal](figuras/01_figura_principal.png)",
             "**Segunda figura, si hay espacio:** `02_canales_rojos_y_contrastes.svg`, por la inversión de signo de 730 nm "
             "y el efecto de restar controles con igual caolín. Sus paneles superiores muestran media±DE; "
             "los inferiores, contrastes de medias±EE propagado. "
             "Las dos láminas `03_18_canales_90.svg` y `03_18_canales_180.svg` quedarían como material suplementario. "
             "No usaría una nueva recta concentración–intensidad: solo hay una concentración no nula de clorofila.",
             "### Suggested English caption",
             "Effect of nominal kaolin loading on the optical response of chlorophyll extracts under 430 nm excitation. "
             "Extract-containing preparations had a nominal chlorophyll a concentration of 3 µg/mL; matched no-extract controls contained ethanol. "
             "Kaolin loadings were 0, 1.25 and 2.50 g/L. (A, B) Measured 680 nm intensities in the 90° and 180° configurations. "
             "(C) Ethanol-referenced 680 nm response, normalized to the pure-extract response in each configuration. "
             "(D) Exploratory background-scaled proxy S810 = I680 − (B680/B810)I810, normalized in the same way; "
             "B denotes the ethanol reference. Coefficients were derived from ethanol measurements, not fitted to mixture values. "
             "Symbols and error bars show means and standard deviations of three acquisitions. "
             "Reference means are treated as fixed when scaling error bars. Normalized responses are not concentration recoveries. "
             "The background-scaling assumption and transfer to other pigment concentrations require independent testing.",
             "## Límites y siguiente prueba decisiva",
             "Los datos apoyan una elección operativa para este extracto etanólico, estas cargas y estas sesiones. "
             "Ambas geometrías distinguen las mezclas de sus controles a 3 µg/mL; no se estima sensibilidad/especificidad de clasificación con ellas. "
             "Las geometrías se adquirieron sucesivamente y las condiciones por bloques; la agitación reduce pero no cuantifica la sedimentación. "
             "Faltan tiempo de espera, blancos intercalados y preparaciones independientes. "
             "No se mide clorofila disuelta después del contacto con caolín; no se separan óptica, adsorción o cambios químicos. "
             "No hay turbidez en NTU/FNU, validación en agua natural ni serie de varias concentraciones con caolín. "
             "Se retienen anomalías: 410/435 nm a 180° se excluyen por el blanco próximo a 2³²; "
             "485 se excluye en ambas geometrías por inestabilidad. Ambos dark son cero; no acreditan ausencia de ruido.",
             "La prueba siguiente más informativa sería cruzar varias concentraciones de extracto, incluida una baja, "
             "con las mismas cargas de caolín y preparaciones independientes. "
             "Registrar un tiempo fijo tras agitar. Comparar 90°/680 con 180°/S810 usando coeficientes bloqueados "
             "antes de ver las nuevas mezclas y referencias analíticas de clorofila. "
             "Hasta entonces: 90° para la señal principal; 180° como vía complementaria de diagnóstico y desarrollo multicanal.",
             "## Archivos y reproducción",
             "Ejecutar `python3 analizar_kaolin.py` desde `kaolin/`, con NumPy y Matplotlib. "
             "Se regeneran exclusivamente los resultados de esta carpeta. "
             "Para comparar sesiones se lee también `../../resultados/medias.csv` desde el informe, "
             "correspondiente al análisis previo de extractos puros.",
             "- `preparaciones.csv`: composiciones nominales.\n"
             "- `adquisiciones.csv` (648 filas) y `medias.csv` (216): datos y banderas.\n"
             "- `contrastes.csv` (108): efectos, interacciones y errores estándar.\n"
             "- `diagnosticos.csv` (34): canales, cocientes y nueve restas de fondo por geometría.\n"
             "- `coeficientes_fondo.csv`: todos los coeficientes obtenidos del etanol.\n"
             "- `comparacion_entre_sesiones.csv`: extracto puro nominal de 3 µg/mL.\n"
             "- `resumen.json`, `inventario_fuentes.csv` y `trazabilidad.json`: resultados sin redondeo, fuentes y confirmaciones de Alex.\n"
             "- `figuras/`: PNG a 300 dpi y SVG editables.",
             "## Contexto bibliográfico",
             "Las partículas pueden modificar tanto la excitación como la luz que recibe el detector, "
             "y las correcciones dependen del instrumento y de la matriz: [guía USGS de fluorescencia de pigmentos](https://pubs.usgs.gov/publication/tm1D10/full). "
             "Un ejemplo experimental con clorofila constante y arcilla es [Puiu et al., 2015](https://doi.org/10.3390/s150614415). "
             "Estos trabajos justifican evaluar la interferencia; no validan la fórmula S810 de este instrumento. "
             "La interpretación y elección anteriores se basan en los controles medidos aquí."]
    (OUT/"informe.md").write_text("\n\n".join(text).replace("|\n\n|","|\n|"),encoding="utf-8")


if __name__=="__main__":
    main()
