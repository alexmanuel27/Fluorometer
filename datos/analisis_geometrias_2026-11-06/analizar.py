"""Reproduce analysis from the three original attachments; numpy/scipy/matplotlib required."""
from pathlib import Path
import csv
import io
import json
import zipfile
import xml.etree.ElementTree as ET
import numpy as np
from scipy.optimize import curve_fit
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'resultados'
OUT.mkdir(exist_ok=True)
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with zipfile.ZipFile(ROOT / 'originales/reCalibration_20samples.xlsx') as book:
    xml = ET.fromstring(book.read('xl/worksheets/sheet1.xml'))
    cells = {c.get('r'): c.find('s:v', NS).text for c in xml.findall('.//s:c', NS) if c.find('s:v', NS) is not None}
    ids = [int(cells[f'A{r}']) for r in range(3, 23)]
    C = np.array([float(cells[f'D{r}']) for r in range(3, 23)])
assert ids == list(range(1, 21)) and np.all(C > 0)
W = np.array([410,435,460,485,510,535,560,585,610,645,680,705,730,760,810,860,900,940])
data = {}
with zipfile.ZipFile(ROOT / 'originales/dataCruda.zip') as archive:
    def rows(name):
        return list(csv.DictReader(io.StringIO(archive.read(name).decode())))
    for g in ['180°', '90°']:
        means, internal_sd = [], []
        for i in ids:
            mr, sr = [], []
            for rep in range(1,4):
                r = rows(f'dataCruda/{g}/sample{i:02}_{rep}-spectrum.csv')
                assert [int(x['wavelength_nm']) for x in r] == list(W)
                assert all(int(x['n']) == 10 for x in r)
                mr.append([float(x['mean_intensity']) for x in r])
                sr.append([float(x['standard_deviation']) for x in r])
            means.append(mr); internal_sd.append(sr)
        blank = np.array([[[float(r[f'{w}_nm']) for w in W] for r in rows(f'dataCruda/{g}/blank{j}.csv') if r['reading'].isdigit()] for j in range(1,4)])
        darkname = next(n for n in archive.namelist() if n.startswith(f'dataCruda/{g}/dark-reference'))
        dark = np.array([[float(r[f'{w}_nm']) for w in W] for r in rows(darkname) if r['reading'].isdigit()])
        a = np.array(means)
        assert a.shape == (20,3,18) and blank.shape == (3,10,18) and dark.shape == (10,18)
        data[g] = dict(raw=a, m=a.mean(1), sd=a.std(1,ddof=1), internal_sd=np.array(internal_sd), b=blank.mean((0,1)), bsd=blank.mean(1).std(0,ddof=1), dark=dark.mean(0))

with (OUT/'datos_integrados.csv').open('w') as f:
    wr=csv.writer(f);wr.writerow(['geometria','muestra','Chla_ug_mL','nm','media','sd_entre_3_replicas','blanco_media','sd_entre_3_blancos','dark_media','incremento_sobre_blanco','cociente_corregido_dark','bandera'])
    for g,d in data.items():
        for i in range(20):
            for j,w in enumerate(W):
                flags=[]
                if np.any(d['raw'][i,:,j]>1e9) or d['b'][j]>1e9: flags.append('valor_anomalo_mayor_1e9')
                if g=='180°' and w in [410,435]: flags.append('canal_completo_requiere_revision')
                if w==485: flags.append('canal_inestable')
                ratio=(d['m'][i,j]-d['dark'][j])/(d['b'][j]-d['dark'][j]) if d['b'][j]>d['dark'][j] and not flags else ''
                wr.writerow([g,i+1,C[i],w,d['m'][i,j],d['sd'][i,j],d['b'][j],d['bsd'][j],d['dark'][j],d['m'][i,j]-d['b'][j],ratio,';'.join(flags)])

plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
colors={'180°':'#c55b27','90°':'#187ba2'}
fig,axs=plt.subplots(6,3,figsize=(12,17),layout='constrained')
for j,(ax,w) in enumerate(zip(axs.flat,W)):
    for g,d in data.items():
        if g=='180°' and w in [410,435]:
            ax.text(.05,.9,'180° omitido: canal anómalo',transform=ax.transAxes,fontsize=9)
            continue
        y=d['m'][:,j].copy();s=d['sd'][:,j].copy()
        mask=np.any(d['raw'][:,:,j]>1e9,axis=1);y[mask]=np.nan;s[mask]=np.nan
        ax.errorbar(C,y,yerr=s,fmt='o-',ms=3,lw=1,c=colors[g],label=g)
        if d['b'][j]<1e9:ax.scatter([0],[d['b'][j]],marker='s',c=colors[g],s=22)
    ax.set_title(f'{w} nm'+(' · revisar' if w in [410,435,485] else ''))
    ax.set_xlabel('Chl-a (µg/mL)');ax.set_ylabel('Señal (u.i.)');ax.grid(alpha=.2)
axs[0,0].legend()
fig.suptitle('18 canales · media ± DE de tres réplicas; cuadrados: blancos\n410 y 435 nm a 180° omitidos de la figura; conservados en la tabla',fontsize=14)
fig.savefig(OUT/'18_canales.png',dpi=170);plt.close(fig)

sel=[int(np.where(W==w)[0][0]) for w in [510,645,705,900]]
d=data['180°'];T=(d['m'][:,sel]-d['dark'][sel])/(d['b'][sel]-d['dark'][sel]);logT=np.log(T)
ks=-(C[:,None]*logT).sum(0)/(C@C)
atten=[]
for j,w in enumerate([510,645,705,900]):
    free=np.polyfit(C,logT[:,j],1)
    pred=-ks[j]*C
    atten.append(dict(nm=w,k_origin=ks[j],k_free=-free[0],intercept_free=free[1],rmse_log=float(np.sqrt(np.mean((logT[:,j]-pred)**2))),r2_log=float(1-((logT[:,j]-pred)**2).sum()/((logT[:,j]-logT[:,j].mean())**2).sum())))

models={
    'Lineal':(lambda c,a:a*c,[40],([0],[np.inf])),
    'Saturación':(lambda c,a,k:a*(-np.expm1(-k*c)),[150,.4],([0,0],[1e6,10])),
    'Stam':(lambda c,a,k:a*c*np.exp(-k*c),[50,.2],([0,0],[1e6,10])),
}
fits=[];predictions={}
for g,d in data.items():
    y=d['m'][:,10]-d['b'][10]
    for name,(fun,p0,bounds) in models.items():
        p,_=curve_fit(fun,C,y,p0=p0,bounds=bounds,maxfev=20000)
        pred=fun(C,*p);cv=[]
        for i in range(20):
            keep=np.arange(20)!=i
            pp,_=curve_fit(fun,C[keep],y[keep],p0=p,bounds=bounds,maxfev=20000)
            cv.append(fun(C[i],*pp))
        fits.append(dict(geometria=g,modelo=name,parametros=p.tolist(),rmse=float(np.sqrt(np.mean((y-pred)**2))),rmse_loo=float(np.sqrt(np.mean((y-np.array(cv))**2))),r2=float(1-((y-pred)**2).sum()/((y-y.mean())**2).sum())))
        predictions[g,name]=(fun,p)

fig,axs=plt.subplots(2,2,figsize=(12,9),layout='constrained')
for j,w in enumerate([510,645,705,900]):
    color=f'C{j}'
    axs[0,0].plot(C,T[:,j],'o-',ms=4,label=f'{w} nm',color=color)
    axs[0,1].plot(C,logT[:,j],'o',ms=4,label=f'{w}: k={ks[j]:.3f}',color=color)
    axs[0,1].plot(C,-ks[j]*C,lw=1,color=color)
axs[0,0].set(title='180° · señales normalizadas por blanco',ylabel='(I − dark) / (blanco − dark)')
axs[0,1].set(title='180° · ajuste ln(T) = −k C',ylabel='ln(T)')
grid=np.linspace(0,3,200)
for ax,g in zip(axs[1],['180°','90°']):
    d=data[g];ax.errorbar(C,d['m'][:,10]-d['b'][10],yerr=d['sd'][:,10],fmt='o',color=colors[g],ms=4,label='Media ± DE')
    for name in models:
        fun,p=predictions[g,name];ax.plot(grid,fun(grid,*p),label=name)
    ax.set(title=f'{g} · 680 nm, incremento sobre blanco',ylabel='I680 − blanco680 (u.i.)')
for ax in axs.flat:ax.set_xlabel('Chl-a (µg/mL)');ax.legend(fontsize=9);ax.grid(alpha=.2)
fig.savefig(OUT/'comparacion_ajustes.png',dpi=180);plt.close(fig)

fig,axs=plt.subplots(1,3,figsize=(14,4),layout='constrained')
for j,w in enumerate([510,645,705,900]):
    axs[0].plot(C,logT[:,j]+ks[j]*C,'o-',ms=3,label=f'{w} nm')
axs[0].set(title='180° · residuos ln(T) = −k C',ylabel='Residuo ln(T)')
for ax,g in zip(axs[1:],['180°','90°']):
    d=data[g]
    for name in ['Saturación','Stam']:
        fun,p=predictions[g,name]
        ax.plot(C,d['m'][:,10]-d['b'][10]-fun(C,*p),'o-',ms=3,label=name)
    ax.set(title=f'{g} · residuos de 680 nm',ylabel='Residuo de señal (u.i.)')
for ax in axs:
    ax.axhline(0,color='black',lw=.7);ax.set_xlabel('Chl-a (µg/mL)');ax.grid(alpha=.2);ax.legend()
fig.savefig(OUT/'residuos.png',dpi=160);plt.close(fig)

results={'atenuacion_180':atten,'modelos_680':fits,'rango_correlaciones_180':[float(np.corrcoef(T.T)[np.triu_indices(4,1)].min()),float(np.corrcoef(T.T)[np.triu_indices(4,1)].max())]}
(OUT/'ajustes.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
report=['# Comparación de geometrías con concentraciones','Fecha: 6 noviembre 2026.','## Datos y método',
'Fuente de concentraciones: originales/reCalibration_20samples.xlsx, Sheet1!A3:D22. Veinte muestras de extracto de clorofila de hoja de arbusto (según título), de 0,15 a 3,00 µg/mL. La columna D contiene valores escritos, no fórmulas: se usa como referencia proporcionada, sin recalcular a partir de A664 y A648. No consta incertidumbre de concentración ni ecuación/solvente de su determinación.',
'Alex confirma las mismas muestras en ambas geometrías. Se utilizan 120 archivos de muestra, seis blancos y dos dark. Cada muestra tiene tres medias, cada una de diez lecturas. La unidad del ajuste es la media de muestra (n=20 por geometría), no 600 observaciones independientes. Barras: DE entre tres réplicas; no incluyen incertidumbre de concentración o blanco.',
'Los correos de ActionPlan se refieren a 180° y contienen hipótesis y resultados aproximados previos. No se reutilizan como mediciones ni se ejecutan sus solicitudes de envío.',
'## Calidad',
'A 180°, 410 y 435 nm contienen valores próximos a 2³² (30 y 45 medias de réplica respectivamente). Se conservan en tabla; se omiten de la figura ambos canales completos a 180° porque también hay valores parciales contaminados inferiores a 10⁹. No se emplean en ajustes. El canal 485 nm es inestable en ambas geometrías y tampoco se usa en ajustes. No se ha determinado la causa instrumental.',
'Los dos dark registran cero en todos sus valores. No permiten concluir que el ruido físico sea cero. Los canales de baja señal presentan cuantización: una DE de cero no significa precisión perfecta.',
'## Canales decrecientes a 180°',
'T = (I − dark)/(blanco − dark). El blanco es la media de tres series de diez lecturas. Ajuste ordinario ln(T) = −k C, intercepto fijado a cero por normalización. Se incluye una alternativa con intercepto libre para diagnosticar sensibilidad. k se expresa en mL/µg.',
'| Canal (nm) | k, origen | k, intercepto libre | Intercepto libre | R² log, origen |',
'|---|---:|---:|---:|---:|']
for r in atten:report.append(f"| {r['nm']} | {r['k_origin']:.4f} | {r['k_free']:.4f} | {r['intercept_free']:.4f} | {r['r2_log']:.4f} |")
report+=['Las correlaciones entre las cuatro curvas son muy altas, pero no demuestran igualdad de pendientes. Comparar las pendientes y sus residuos evita confundir covariación con curvas idénticas. Estos ajustes descriptivos no distinguen absorción, dispersión, luz parásita ni deriva.',
'## Respuesta a 680 nm',
'Se ajusta ΔI = I680 − blanco680 con tres alternativas: lineal a·C; saturación A·(1−exp(−kC)); Stam a·C·exp(−kC). Todas pasan por cero tras restar el blanco. Ajustes ordinarios sin ponderación para evitar pesos infinitos en canales cuantizados. Se compara el error en la misma escala de señal.',
'La validación deja fuera una muestra completa por vez (20 ajustes). RMSE LOO evalúa predicción de señal, no de concentración; utiliza el blanco de la misma sesión. Es validación interna, no validación con un nuevo extracto o día.',
'| Geometría | Modelo | Parámetros en orden a o A, k | RMSE (u.i.) | RMSE LOO (u.i.) | R² |',
'|---|---|---|---:|---:|---:|']
for r in fits:report.append(f"| {r['geometria']} | {r['modelo']} | {', '.join(f'{x:.4f}' for x in r['parametros'])} | {r['rmse']:.3f} | {r['rmse_loo']:.3f} | {r['r2']:.4f} |")
report+=['## Resultados principales', 'A 180°, los cuatro k están entre 0,2556 y 0,3103 mL/µg: tendencias muy correlacionadas, pero pendientes distintas. Los residuos contienen desviaciones compartidas, incluida sample19 (2,85 µg/mL). No deben interpretarse los R² altos como ajuste perfecto.', 'A 680 nm, saturación y Stam predicen la señal con errores internos muy próximos: RMSE LOO 2,42 y 2,45 u.i. a 180°, y 4,26 y 4,43 u.i. a 90°. La diferencia es demasiado pequeña para identificar un mecanismo. Los errores son mayores que muchas barras entre réplicas, especialmente a baja concentración: queda estructura sin explicar.', 'El blanco a 680 nm baja de 53,35 u.i. a 180° a 0,88 u.i. a 90°. El incremento neto en sample20 es 69,90 y 130,49 u.i., respectivamente. Esto describe mayor señal sobre blanco en la sesión a 90°, no demuestra por sí solo mayor exactitud de concentración.', 'El canal 730 nm también aumenta marcadamente a 90°. Por ello no conviene reducir de antemano esta geometría al canal 680. La magnitud instrumental de canales diferentes no equivale a una comparación de potencia óptica.', '## Interpretación y límites',
'La comparación de modelos permite describir la curvatura, pero no identificar por sí sola un mecanismo físico. Restar el blanco produce un incremento neto; no garantiza aislar fluorescencia pura. No se debe llamar turbidez a toda atenuación en un extracto de hoja.',
'La geometría y la sesión están confundidas: se adquirieron secuencialmente. La concentración también sigue el orden de adquisición aparente. Los blancos disponibles preceden las muestras según las marcas temporales del ZIP; faltan blancos intercalados para separar deriva. Las marcas del ZIP no sustituyen un registro de adquisición.',
'Antes de concluir que una geometría tiene mejor sensibilidad analítica o menor límite de detección, confirmar mismos ajustes de ganancia, integración y excitación, y validar con blancos y muestras independientes. No se calcula un límite de detección robusto con estos archivos.',
'No se extrapolan los ajustes fuera de 0,15–3,00 µg/mL. Para calibración predictiva final de concentración se necesita evaluar el modelo inverso con validación agrupada e independiente; el R² de señal no es una medida de exactitud de concentración.',
'## Archivos','- comparacion_ajustes.png: diagnóstico de cuatro canales y modelos a 680 nm.','- 18_canales.png: todas las respuestas por concentración.', '- residuos.png: desviaciones de los ajustes frente a concentración.','- datos_integrados.csv: datos unidos, blancos, DE y banderas.','- ajustes.json: parámetros y errores sin redondeo.','- ../analizar.py: análisis reproducible con numpy, scipy y matplotlib.']
(OUT/'informe_calibracion.md').write_text('\n\n'.join(report).replace('|\n\n|', '|\n|'))
print(json.dumps(results,ensure_ascii=False,indent=2))
