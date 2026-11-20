"""Historical analysis: the active model since 2026-11-20 is the global linear
90°/680 nm model in lineal_90_680/generar_entrega.py (relative to the paper root).
This module preserves the previous analysis and is also reused for its readers.

Exploratory LOO check of blank-scaled 680 nm proxies in pure extracts.

Reuses the original sample splits and fit functions. No kaolin mixtures enter
the fits. The two auxiliary bands were reviewed after the kaolin experiment;
these are fixed-candidate internal errors, not external validation.
"""
import csv
from pathlib import Path
import numpy as np
import analizar_extractos as calibration


def main():
    calibration.self_check()
    c,data=calibration.load()
    root=Path(__file__).resolve().parent
    with (root/"resultados/modelos.csv").open(encoding="utf-8-sig") as f:
        previous=list(csv.DictReader(f))
    rows=[]
    residuals=[]
    diagnostic=[]
    for g,d in data.items():
        for ref in (None,810,860):
            if ref is None:
                signal=d["mean"][:,10]-d["blank"][10]
                beta=""
            else:
                j=list(calibration.W).index(ref)
                beta=d["blank"][10]/d["blank"][j]
                signal=d["mean"][:,10]-beta*d["mean"][:,j]
            assert np.isclose(signal[0],0,atol=1e-9)
            for kind in ("lineal","cuadratico","saturacion"):
                x=np.c_[signal,signal**2] if kind=="cuadratico" else signal[:,None]
                model=dict(kind=kind,alpha=0.,x=x)
                prediction=calibration.cv(model,c,np.arange(len(c)))
                result=calibration.metrics(c[1:],prediction)
                assert np.isfinite(prediction).all()
                full=calibration.predict(model,calibration.fit(model,c,np.arange(len(c))),np.arange(1,len(c)))
                error=prediction-c[1:]
                for i in range(1,len(c)):
                    residuals.append(dict(geometria=g,referencia_nm=ref or "solo_blanco",funcion=kind,
                                          muestra=i,concentracion_ug_mL=c[i],prediccion_LOO=prediction[i-1],
                                          error_LOO=error[i-1],error_relativo_pct=100*error[i-1]/c[i],
                                          error_ajuste_completo=full[i-1]-c[i]))
                if kind=="cuadratico":
                    remaining=np.arange(len(c))[np.arange(len(c))!=19]
                    sensitivity=calibration.cv(model,c,remaining)-c[remaining[remaining!=0]]
                    explicit=np.array([calibration.predict(model,calibration.fit(model,c,remaining[remaining!=i]),[i])[0]
                                       for i in remaining if i!=0])-c[remaining[remaining!=0]]
                    assert np.allclose(sensitivity,explicit,atol=1e-9), "Sensitivity must refit without sample 19"
                    diagnostic.append(dict(geometria=g,referencia_nm=ref or "solo_blanco",
                                           RMSE_LOO=result["RMSE"],sesgo_medio=error.mean(),
                                           numero_tramos_mismo_signo=1+np.count_nonzero(np.sign(error[1:])!=np.sign(error[:-1])),
                                           muestra_error_maximo=int(np.argmax(abs(error))+1),
                                           error_muestra19=error[18],fraccion_SSE_muestra19_pct=100*error[18]**2/(error@error),
                                           error_relativo_muestra1_pct=100*error[0]/c[1],
                                           sesgo_C015_a_060=error[:4].mean(),sesgo_C075_a_120=error[4:8].mean(),
                                           sesgo_C135_a_180=error[8:12].mean(),sesgo_C195_a_240=error[12:16].mean(),
                                           sesgo_C255_a_300=error[16:].mean(),
                                           RMSE_LOO_reajustado_sin19_solo_sensibilidad=np.sqrt(np.mean(sensitivity**2))))
                if ref is None and kind=="cuadratico":
                    old=next(r for r in previous if r["geometria"]==g and r["modelo"]=="cuadratico_680")
                    assert np.isclose(result["RMSE"],float(old["RMSE"]),atol=1e-10)
                rows.append(dict(geometria=g,referencia_nm=ref or "solo_blanco",beta=beta,
                                 funcion=kind,RMSE_LOO_ug_mL=result["RMSE"],MAE_LOO_ug_mL=result["MAE"],
                                 nota="candidato fijado; 20 extractos; blanco compartido; no CV anidada ni validación externa"))
    out=root/"resultados/comprobacion_correccion_fondo.csv"
    with out.open("w",newline="",encoding="utf-8-sig") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    for name,records in [("residuos_correccion_fondo.csv",residuals),("diagnostico_residuos.csv",diagnostic)]:
        with (root/"resultados"/name).open("w",newline="",encoding="utf-8-sig") as f:
            writer=csv.DictWriter(f,fieldnames=list(records[0]))
            writer.writeheader();writer.writerows(records)
    correlations=[]
    for ref in ("solo_blanco",810,860):
        series=[np.array([r["error_LOO"] for r in residuals if r["geometria"]==g and
                          r["referencia_nm"]==ref and r["funcion"]=="cuadratico"]) for g in calibration.GEOMETRIES]
        correlations.append(dict(referencia_nm=ref,correlacion_errores_90_180=float(np.corrcoef(series)[0,1])))
    with (root/"resultados/correlacion_residuos_geometrias.csv").open("w",newline="",encoding="utf-8-sig") as f:
        writer=csv.DictWriter(f,fieldnames=list(correlations[0]))
        writer.writeheader();writer.writerows(correlations)
    plot_residuals(root,residuals)
    print(out)


def plot_residuals(root,records):
    plt=calibration.plt
    plt.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False,"svg.fonttype":"none"})
    fig,axs=plt.subplots(2,2,figsize=(10.8,8.4))
    fig.subplots_adjust(left=.085,right=.98,top=.91,bottom=.18,hspace=.37,wspace=.24)
    for col,g in enumerate(calibration.GEOMETRIES):
        for ref,color,marker,label in [("solo_blanco","#264653","o","680 nm − blanco"),
                                        (810,"#2A9D8F","^","680 nm con fondo escalado a 810 nm")]:
            rows=[r for r in records if r["geometria"]==g and r["referencia_nm"]==ref and r["funcion"]=="cuadratico"]
            assert len(rows)==20
            c=np.array([r["concentracion_ug_mL"] for r in rows])
            error=np.array([r["error_LOO"] for r in rows])
            for row,y in [(0,error),(1,100*error/c)]:
                ax=axs[row,col]
                ax.plot(c,y,color=color,marker=marker,ms=4,lw=.8,label=label)
                ax.scatter(c[18],y[18],s=80,facecolors="none",edgecolors=color,lw=1)
        for row in (0,1):
            ax=axs[row,col]
            ax.axhline(0,color="#6C757D",lw=.8)
            ax.grid(axis="y",alpha=.15,color="#6C757D")
            ax.set(title=f"{'ABCD'[row*2+col]}  {g} · "+("Error de predicción" if row==0 else "Error relativo de predicción"),
                   xlabel="Concentración de referencia (µg/mL)",
                   ylabel="Predicción − referencia (µg/mL)" if row==0 else "Error de predicción (%)",
                   xlim=(0,3.1),ylim=(-.36,.29) if row==0 else (-20,80))
            if row==0:ax.annotate("19",(2.85,-.32 if g=="180°" else -.22),fontsize=9,color="#264653")
    handles,labels=axs[0,0].get_legend_handles_labels()
    fig.legend(handles,labels,loc="lower center",bbox_to_anchor=(.5,.055),ncol=2,frameon=False,fontsize=9)
    fig.suptitle("Residuos al dejar fuera cada muestra · calibraciones cuadráticas fijadas",fontsize=13)
    fig.text(.085,.018,"Cada punto es una muestra no usada en su ajuste. Círculos abiertos: muestra 19 (2,85 µg/mL).\n"
             "Se conservan todas las muestras. Las líneas solo ayudan a seguir el patrón; el blanco de sesión es compartido.",fontsize=9)
    for fmt in ("png","svg"):
        fig.savefig(root/"resultados/figuras"/f"05_revision_residuos.{fmt}",dpi=300,bbox_inches="tight")
    plt.close(fig)


if __name__=="__main__":
    main()
