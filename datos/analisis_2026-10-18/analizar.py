"""Reproducible, read-only analysis of the three original Excel files.

Requires numpy, scipy, matplotlib, scikit-learn and openpyxl.
Run from any directory. Outputs stay beside this script.
"""
from pathlib import Path
import csv
import hashlib
import json
import warnings

import numpy as np
import openpyxl
from scipy.stats import linregress, spearmanr, t
from sklearn.cross_decomposition import PLSRegression
from sklearn.model_selection import GridSearchCV, LeaveOneOut, cross_val_predict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
DATA = OUT.parent
FILES = {"85": "calibracion_85_puntos (1).xlsx", "11": "11Samples.xlsx", "9": "9Samples.xlsx"}
BLANKS = {"85": 1356., "11": 1256., "9": 1214.}
COLORS = {"85": "#2675b8", "11": "#d66c1d", "9": "#21966a"}
WAVES = [410,435,460,485,510,535,560,585,610,645,680,705,730,760,810,860,900,940]
VALID_WAVES = [nm for nm in WAVES if nm not in (410,435)]
np.set_printoptions(precision=5, suppress=True)
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.dpi": 120, "savefig.dpi": 180})


def load():
    groups, audit, hashes = {}, [], {}
    for group, filename in FILES.items():
        path = DATA / filename
        hashes[filename] = hashlib.sha256(path.read_bytes()).hexdigest()
        sh = openpyxl.load_workbook(path, data_only=True, read_only=True).active
        rows = list(sh.values)
        headers = list(rows[0])
        records = []
        for rownum, row in enumerate(rows[1:], 2):
            if all(v is None for v in row):
                continue
            rec = dict(zip(headers, row))
            if not isinstance(rec.get("Chl(a) [µg/mL]"), (int, float)) or not isinstance(rec.get("I(645)"), (int,float)):
                audit.append({"group":group,"row":rownum,"issue":"ID without concentration/intensity; excluded"})
                continue
            rec["row"] = rownum
            records.append(rec)
        assert len(records) == int(group), (group, len(records))
        g = {"y": np.array([r["Chl(a) [µg/mL]"] for r in records]),
             "id": np.array([r["samples"] for r in records]),
             "row": np.array([r["row"] for r in records]), "records": records}
        for nm in WAVES:
            if f"I({nm})" in headers:
                g[f"I{nm}"] = np.array([r[f"I({nm})"] for r in records], dtype=float)
                g[f"sd{nm}"] = np.array([r[f"desviacion ({nm})"] for r in records], dtype=float)
        assert np.all(np.isfinite(g["y"])) and np.all(g["I645"] > 0)
        g["z"] = np.log(BLANKS[group] / g["I645"])
        for nm in (410,435):
            if f"I{nm}" in g:
                assert np.all(g[f"I{nm}"] == 2**32)
                audit.append({"group":group,"row":"all","issue":f"I{nm}=4294967296 constant, excluded from models"})
        for nm in WAVES:
            if f"sd{nm}" in g:
                for i in np.flatnonzero(g[f"sd{nm}"] > g[f"I{nm}"]):
                    audit.append({"group":group,"row":int(g["row"][i]),"issue":f"SD{nm}={g[f'sd{nm}'][i]:g} exceeds intensity; not used as a weight"})
        groups[group] = g
    return groups, audit, hashes


def metrics(y, pred):
    e = np.asarray(pred).reshape(-1) - y
    return {"n":len(y), "r2":float(1 - (e@e)/np.sum((y-y.mean())**2)) if len(y)>1 else None,
            "rmse":float(np.sqrt(np.mean(e**2))),"mae":float(np.mean(np.abs(e))),"bias":float(e.mean())}


def design(g, name):
    if name == "I645": x = g["I645"][:,None]
    elif name == "lnI645": x = np.log(g["I645"])[:,None]
    elif name == "ln_blank_ratio": x = g["z"][:,None]
    elif name == "lnI645_quadratic":
        z = np.log(g["I645"]); x = np.c_[z,z*z]
    elif name == "I680": x = g["I680"][:,None]
    elif name == "I680_over_I705": x = (g["I680"]/g["I705"])[:,None]
    elif name == "lnI645_and_I680": x = np.c_[np.log(g["I645"]),g["I680"]]
    elif name.startswith("channel_"): x = g["I"+name.split('_')[1]][:,None]
    else: raise ValueError(name)
    return np.c_[np.ones(len(g["y"])),x]


def fit(g, name):
    X, y = design(g,name),g["y"]
    b = np.linalg.lstsq(X,y,rcond=None)[0]
    fitted = X@b
    hat = np.sum((X@np.linalg.pinv(X.T@X))*X,axis=1)
    # PRESS gives exactly the prediction for each left-out sample for fixed OLS features.
    loo = y - (y-fitted)/(1-hat)
    return b,fitted,loo


def table(headers, rows):
    return '| '+' | '.join(headers)+' |\n|'+'|'.join(['---']*len(headers))+'|\n'+''.join('| '+' | '.join(str(v) for v in r)+' |\n' for r in rows)


def save_csv(name, rows):
    with (OUT/name).open('w',newline='',encoding='utf-8-sig') as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)


def main():
    groups,audit,hashes=load()
    model_rows, pred_rows, equations, transfers, correlations = [],[],{},[],[]
    baselines = ["I645","lnI645","ln_blank_ratio","lnI645_quadratic"]
    spectral_models = ["I680","I680_over_I705","lnI645_and_I680"]
    for group,g in groups.items():
        equations[group]={}
        for name in baselines+(spectral_models if group!='85' else []):
            b,fitted,loo=fit(g,name)
            equations[group][name]=b.tolist()
            model_rows.append({"group":group,"model":name,"validation":"fit",**metrics(g['y'],fitted)})
            model_rows.append({"group":group,"model":name,"validation":"LOOCV_exploratory",**metrics(g['y'],loo)})
            for i in range(len(loo)):
                pred_rows.append({"train":group,"test":group,"validation":"LOOCV_exploratory","model":name,"sample":int(g['id'][i]),"reference":g['y'][i],"prediction":loo[i]})
        for target,gt in groups.items():
            if target==group: continue
            for name in ["lnI645","ln_blank_ratio"]+(spectral_models if group!='85' and target!='85' else []):
                b=np.array(equations[group][name]);prediction=design(gt,name)@b
                transfers.append({"train":group,"test":target,"model":name,**metrics(gt['y'],prediction)})
                for i,p in enumerate(prediction):
                    pred_rows.append({"train":group,"test":target,"validation":"external_batch","model":name,"sample":int(gt['id'][i]),"reference":gt['y'][i],"prediction":p})
        if group!='85':
            for nm in VALID_WAVES:
                correlations.append({"group":group,"channel_nm":nm,"pearson_r":float(np.corrcoef(g[f'I{nm}'],g['y'])[0,1]),
                                     "spearman_r":float(spearmanr(g[f'I{nm}'],g['y']).statistic),
                                     "median_sd_over_I_percent":float(np.median(g[f'sd{nm}']/g[f'I{nm}'])*100)})

    # Multichannel models: scaling and component choice are trained within every fold.
    # Nested LOOCV is descriptive within batch, not independent extract validation for the dilution series.
    pls_results=[]
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',UserWarning)
        for group in ('11','9'):
            g=groups[group];X=np.column_stack([g[f'I{nm}'] for nm in VALID_WAVES]);y=g['y']
            search=GridSearchCV(PLSRegression(scale=True),{'n_components':[1,2,3]},cv=LeaveOneOut(),scoring='neg_mean_squared_error')
            pp=cross_val_predict(search,X,y,cv=LeaveOneOut()).reshape(-1)
            search.fit(X,y)
            pls_results.append({"group":group,"model":"PLS_16_valid_channels","validation":"nested_LOOCV_exploratory",**metrics(y,pp),"components_all_data":int(search.best_params_['n_components'])})
            other='9' if group=='11' else '11';gt=groups[other]
            pt=search.predict(np.column_stack([gt[f'I{nm}'] for nm in VALID_WAVES])).reshape(-1)
            transfers.append({"train":group,"test":other,"model":"PLS_16_valid_channels",**metrics(gt['y'],pt)})
            for i,p in enumerate(pp):pred_rows.append({"train":group,"test":group,"validation":"nested_LOOCV_exploratory","model":"PLS_16_valid_channels","sample":int(g['id'][i]),"reference":y[i],"prediction":p})

    # Deployed historic formula, evaluated without refitting, also on unseen batches.
    historical={group:metrics(g['y'],-2.7924*np.log(g['I645'])+20.1264) for group,g in groups.items()}
    save_csv('modelos.csv',model_rows+[{k:v for k,v in r.items() if k!='components_all_data'} for r in pls_results])
    save_csv('transferencia_entre_tandas.csv',transfers)
    save_csv('predicciones.csv',pred_rows)
    save_csv('canales.csv',correlations)
    clean=[]
    for group,g in groups.items():
        for i in range(len(g['y'])):
            row={"group":group,"source":FILES[group],"excel_row":int(g['row'][i]),"sample":int(g['id'][i]),"chl_a_ug_ml":g['y'][i],"blank_I645":BLANKS[group],"ln_blank_over_I645":g['z'][i]}
            row.update({f'I{nm}':float(g[f'I{nm}'][i]) if f'I{nm}' in g else '' for nm in WAVES})
            clean.append(row)
    save_csv('datos_analizados.csv',clean)
    save_csv('incidencias.csv',audit)
    summary={"equations":equations,"models":model_rows,"transfers":transfers,"pls":pls_results,"historical":historical,"source_sha256":hashes}
    (OUT/'resultados.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')

    fig,axs=plt.subplots(2,2,figsize=(12,8),constrained_layout=True)
    for group,g in groups.items():
        col=COLORS[group]
        axs[0,0].scatter(g['y'],g['I645'],label=f"{group} samples",color=col,s=25,alpha=.8)
        axs[0,1].scatter(g['z'],g['y'],color=col,s=25)
        b=np.array(equations[group]['ln_blank_ratio']);xx=np.linspace(g['z'].min(),g['z'].max(),100)
        axs[0,1].plot(xx,b[0]+b[1]*xx,color=col,label=f"{group}: slope {b[1]:.3f}")
        pred=design(g,'ln_blank_ratio')@np.array(equations['85']['ln_blank_ratio'])
        axs[1,0].scatter(g['y'],pred,color=col,s=25,label="85 (fit)" if group=='85' else f"Test {group}")
        _,fitted,_=fit(g,'lnI645')
        axs[1,1].scatter(g['y'],fitted-g['y'],color=col,s=25,label=group)
    axs[0,0].set(xlabel='Reference chlorophyll a (µg/mL)',ylabel='I645 (instrument units)',title='645 nm intensity decreases with concentration')
    axs[0,1].set(xlabel='ln(I645 blank / I645 sample)',ylabel='Reference chlorophyll a (µg/mL)',title='Different slopes between batches')
    axs[1,0].plot([0,8],[0,8],'k--',lw=1);axs[1,0].set(xlabel='Reference chlorophyll a (µg/mL)',ylabel='Predicted chlorophyll a (µg/mL)',title='Train on 85: blank-normalized log calibration')
    axs[1,1].axhline(0,color='k',lw=1);axs[1,1].set(xlabel='Reference chlorophyll a (µg/mL)',ylabel='Fit residual, prediction − reference (µg/mL)',title='Within-batch log fit residuals')
    for ax in axs.flat:ax.legend(fontsize=8);ax.grid(alpha=.15)
    fig.savefig(OUT/'01_calibracion_645.png');plt.close(fig)

    fig,axs=plt.subplots(1,3,figsize=(15,4.7),constrained_layout=True)
    for group in ('11','9'):
        g=groups[group];col=COLORS[group]
        axs[0].errorbar(g['y'],g['I680'],yerr=g['sd680'],fmt='o',ms=4,color=col,label=group+' samples',capsize=2)
        axs[1].scatter(g['y'],g['I680']/g['I705'],color=col,s=25,label=group+' samples')
        cc=[r for r in correlations if r['group']==group]
        axs[2].plot([r['channel_nm'] for r in cc],[r['pearson_r'] for r in cc],'-o',ms=4,color=col,label=group+' samples')
    axs[0].set(xlabel='Reference chlorophyll a (µg/mL)',ylabel='I680 (instrument units)',title='680 nm: increasing signal, nonlinear at high C')
    axs[1].set(xlabel='Reference chlorophyll a (µg/mL)',ylabel='I680 / I705',title='Spectral ratio: exploratory candidate')
    axs[2].axhline(0,color='k',lw=1);axs[2].set(xlabel='Wavelength (nm)',ylabel='Pearson correlation with concentration',title='Most channels fall; 680 nm rises',ylim=(-1.1,1.1))
    for ax in axs:ax.legend(fontsize=8);ax.grid(alpha=.15)
    fig.savefig(OUT/'02_canales_y_fluorescencia.png');plt.close(fig)

    fig,axs=plt.subplots(1,2,figsize=(12,4.5),constrained_layout=True)
    names=['lnI645','I680','I680_over_I705','lnI645_and_I680','PLS_16_valid_channels']
    labels=['ln(I645)','I680','I680 / I705','ln(I645) + I680','PLS (16 channels)']
    for k,group in enumerate(('11','9')):
        vals=[next(r['rmse'] for r in model_rows+pls_results if r['group']==group and r['model']==name and r['validation']!='fit') for name in names]
        axs[0].bar(np.arange(len(names))+(k-.5)*.36,vals,width=.36,color=COLORS[group],label=group+' samples')
        vals=[next(r['rmse'] for r in transfers if r['train']==group and r['test']==('9' if group=='11' else '11') and r['model']==name) for name in names]
        axs[1].bar(np.arange(len(names))+(k-.5)*.36,vals,width=.36,color=COLORS[group],label='Train '+group+' → test '+('9' if group=='11' else '11'))
    for ax in axs:ax.set_xticks(range(len(names)),labels,rotation=25,ha='right');ax.set_ylabel('RMSE (µg/mL)');ax.legend(fontsize=8);ax.grid(axis='y',alpha=.15)
    axs[0].set_title('Within-batch cross-validation (exploratory)');axs[1].set_title('Transfer between protocols (includes range shifts)')
    fig.savefig(OUT/'03_validacion_modelos.png');plt.close(fig)

    overview=[]
    for group,g in groups.items():
        rr=next(r for r in model_rows if r['group']==group and r['model']=='lnI645' and r['validation']=='fit')
        cv=next(r for r in model_rows if r['group']==group and r['model']=='lnI645' and r['validation']!='fit')
        overview.append([group,f"{g['y'].min():.4f}–{g['y'].max():.4f}",f"{rr['r2']:.4f}",f"{rr['rmse']:.4f}",f"{cv['rmse']:.4f}"])
    largest=[]
    for group,g in groups.items():
        _,fitted,_=fit(g,'lnI645')
        for i in np.argsort(np.abs(fitted-g['y']))[-3:][::-1]:
            largest.append([group,int(g['id'][i]),f"{g['y'][i]:.5f}",f"{g['I645'][i]:.3f}",f"{fitted[i]-g['y'][i]:+.4f}"])
    overlap=(groups['85']['y']>=groups['11']['y'].min()) & (groups['85']['y']<=groups['11']['y'].max())
    bo=np.linalg.lstsq(np.c_[np.ones(overlap.sum()),groups['85']['z'][overlap]],groups['85']['y'][overlap],rcond=None)[0]
    lines=['# Análisis de calibración de clorofila a', '', 'Fecha: 18 de octubre de 2026. Unidad de concentración: µg/mL.',
    '', '## Resultado principal',
    'Hay información útil: I645 tiene una relación logarítmica fuerte con la concentración. La normalización por blanco aproxima mucho las 85 muestras y las nueve diluciones, pero no resuelve la diferencia con las 11 muestras. El modelo multicanal probado no mejora la predicción respecto al logaritmo de I645 dentro de cada tanda. 680 nm es el canal que merece estudiar como candidato de emisión.',
    'La prioridad es controlar fondo óptico, saturación y protocolo, y validar con extractos independientes. Los resultados actuales sostienen una calibración empírica, no demuestran una medida pura de fluorescencia ni una ecuación universal.',
    '', '## Qué contienen los archivos',
    'Hay 105 registros completos: 85 con I645 y 20 con los 18 canales y sus desviaciones. No hay absorbancias 664/648, factores de dilución, concentración del extracto madre, espectros de los blancos, datos ADC crudos ni las 10 lecturas individuales. Por tanto, no se puede auditar la concentración de referencia ni recalcular las desviaciones.',
    'El fichero de 85 también contiene 84 filas con solo un identificador, excluidas de los análisis sin modificar el original. Los rangos reales son 0,02384–7,98964 (85), 0,7944–3,07062 (11) y 0,0244–3,9098 (9). No existe una muestra cero en estas tablas.',
    '', '## Calidad de los datos',
    '410 y 435 nm valen exactamente 4294967296 (=2³²) en las 20 muestras, con desviación cero. Son datos inválidos para cuantificación. Esto es compatible con un problema de rango, saturación o conversión, pero estos Excel no permiten identificar la causa. Se excluyeron ambos canales, no las muestras.',
    'La muestra 5 del grupo de nueve tiene desviación(485)=1589592733 (celda J6) frente a I485=1343,57367. Se conserva el original y se marca el error. No se utiliza como peso ni barra de error. 485 presenta dispersión irregular y requiere revisión de la exportación.',
    'Las desviaciones son de repetición instrumental, no incertidumbre de extracción, dilución o referencia. No se ponderaron los ajustes por esas desviaciones. Las unidades radiométricas de intensidad no se acreditan en los archivos: se usan unidades del instrumento y cocientes adimensionales.',
    '', '## Calibración con 645 nm',
    'Modelo: C = a + b·ln(I645). ln es logaritmo natural. Se incluyen todas las muestras completas, sin eliminar atípicos.',
    table(['Grupo','Rango real','R² ajuste','RMSE ajuste','RMSE dejar-una-fuera'],overview)]
    for group in groups:
        b=equations[group]['lnI645'];bn=equations[group]['ln_blank_ratio']
        slope=linregress(np.log(groups[group]['I645']),groups[group]['y']);ci=t.ppf(.975,int(group)-2)*slope.stderr
        lines.append(f"- Grupo {group}: C = {b[0]:.6f} {b[1]:+.6f}·ln(I645). Equivalente: C = {bn[0]:.6f} + {bn[1]:.6f}·ln(I0/I645), I0={BLANKS[group]:g}. IC95% convencional de la pendiente ln(I): [{slope.slope-ci:.4f}, {slope.slope+ci:.4f}].")
    lines += ['', 'RMSE es la raíz del error cuadrático medio de concentración, en µg/mL. R² de ajuste describe los mismos puntos usados para calibrar; no es validación externa. Los intervalos convencionales suponen errores de referencia independientes y no incluyen incertidumbre común del extracto madre.',
              f"Sensibilidad al rango: usando solo las {int(overlap.sum())} muestras del grupo 85 que caen en el intervalo del grupo 11, la pendiente frente a ln(I0/I) pasa de 2,843 a {bo[1]:.3f}. La diferencia de pendientes no permite aislar un efecto de protocolo: también influyen rango, dispersión y error de referencia. No se ha descartado ninguna muestra por su residual.",
              'Mayores residuales por tanda (para revisar registros, no para eliminarlos automáticamente):',
              table(['Grupo','ID','C referencia','I645','Predicción − referencia'],largest),
              '', 'Los blancos (dato aportado por Alex) son 1356, 1256 y 1214. Respecto al de 85, cambian −7,37% y −10,47%. Normalizar por blanco corrige una escala multiplicativa, pero no elimina diferencias de pendiente, composición, geometría o protocolo. Restar el blanco produce valores negativos en I645 y no debe interpretarse como fluorescencia neta positiva.',
              '', '### Transferencia de la calibración de 85',
              table(['Test','Modelo','RMSE','Sesgo predicho − referencia'],[[r['test'],r['model'],f"{r['rmse']:.4f}",f"{r['bias']:+.4f}"] for r in transfers if r['train']=='85']),
              'La fórmula ya usada en el firmware, C = −2,7924·ln(I645)+20,1264, evaluada sin reajustar:',
              table(['Grupo','RMSE','Sesgo'],[[g,f"{m['rmse']:.4f}",f"{m['bias']:+.4f}"] for g,m in historical.items()]),
              '', '## ¿Es fluorescencia?',
              'Según Alex, LED y detector están de frente y la excitación es aproximadamente 430–435 nm. Esa disposición puede captar emisión, transmisión y luz dispersada. No se ha confirmado la presencia de filtro óptico. El blanco de etanol ya tiene I645 alta, y I645 cae al aumentar C. Por tanto, no está demostrado que la señal total a 645 sea fluorescencia de clorofila a. Puede servir como calibración empírica de atenuación, pero el origen físico exige un control experimental.',
              '680 nm es el único de los 16 canales utilizables que crece sistemáticamente con C en ambas tandas. Es un candidato más coherente con emisión de clorofila a. Los datos no prueban que sea fluorescencia pura: falta el blanco espectral de 680 y un control con filtro. La literatura sitúa una banda de Chl a en etanol alrededor de 671 nm, dentro de la proximidad espectral de este canal [1].',
              '', '## Modelos espectrales exploratorios',
              'Se compararon alternativas pequeñas: I680, I680/I705 y ln(I645)+I680. PLS emplea 16 canales (se excluyen 410/435) y elige 1–3 componentes dentro de validación anidada. Los modelos individuales usan dejar-una-fuera con variables fijas. La observación de estos espectros motivó evaluar 680 y su cociente: su selección no es una prueba independiente. La comparación entre alternativas sigue siendo exploratoria y necesita una prueba nueva. La validación anidada reduce el optimismo de elegir componentes PLS sobre los mismos puntos que se usan para evaluar [2].',
              table(['Grupo','Modelo','RMSE validación','R² validación'],[[r['group'],r['model'],f"{r['rmse']:.4f}",f"{r['r2']:.4f}"] for r in model_rows+pls_results if r['group']!='85' and r['validation']!='fit' and r['model'] in ['lnI645']+spectral_models+['PLS_16_valid_channels']]),
              'Transferencia entre protocolos:',
              table(['Entrena','Prueba','Modelo','RMSE','Sesgo'],[[r['train'],r['test'],r['model'],f"{r['rmse']:.4f}",f"{r['bias']:+.4f}"] for r in transfers if r['train']!='85' and r['test']!='85']),
              'Los nueve estándares proceden de un único extracto madre. Dejar una dilución fuera mide interpolación dentro de esa serie; no valida un extracto independiente y no estima la incertidumbre común de la concentración madre. Entrenar con 11 y probar con nueve incluye extrapolación por debajo de 0,7944 y por encima de 3,07062. Entrenar con nueve y probar con 11 no extrapola en concentración, pero sí cambia protocolo/matriz. Las mejoras multicanal no acreditan todavía una calibración universal.',
              '', '## Acciones concretas',
              '1. Guardar los 18 canales del etanol, del sistema con LED apagado y de una muestra con LED encendido. Revisar el origen de 4294967296 con ADC crudo y ganancia/integración registrados. Reducir ganancia, aumentar atenuación o bajar potencia hasta que el ADC no sature.',
              '2. Comparar la medida frontal con una geometría a 90° y un filtro de emisión adecuado para bloquear excitación. Un blanco medido en idénticas condiciones permitirá separar fondo y señal.',
              '3. Preparar varios extractos madre independientes y varias diluciones de cada uno. Aleatorizar el orden, medir el blanco por tanda y controlar calentamiento y posición. Reservar extractos completos, no lecturas repetidas, para validación externa.',
              '4. Recuperar Abs664, Abs648, ecuación de referencia, factor de dilución y concentración madre para auditar la referencia. Registrar etanol %, cuveta, trayectoria, filtros, integración, ganancia y potencia.',
              '5. Mantener como candidato la calibración logarítmica I645 y evaluar en paralelo 680 y cocientes espectrales. No reemplazar todavía la ecuación del firmware a partir de estos 20 espectros.',
              'No es posible calcular un límite de detección defendible con un solo valor medio de blanco por tanda y sin réplicas independientes del blanco.',
              '', '## Archivos y reproducibilidad',
              'Los tres gráficos muestran calibración/transferencia a 645, comportamiento de 680/canales y comparación de validación. CSV adicionales contienen métricas, predicciones por muestra y los datos unidos con procedencia. `resultados.json` guarda ecuaciones y hashes SHA-256 de los originales.',
              '', '## Referencias',
              '[1] Kinetics of Chlorophyll Degradation in Japanese Maple Leaves with In Situ Heating Visible and Near-Infrared Spectroscopic Monitoring (2025). https://www.mdpi.com/2075-1729/15/3/335',
              '[2] Scikit-learn: Nested versus non-nested cross-validation. https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html',
              '[3] ams AS7265x datasheet. https://cdn.sparkfun.com/assets/c/2/9/0/a/AS7265x_Datasheet.pdf']
    (OUT/'informe.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    for filename,expected in hashes.items():assert hashlib.sha256((DATA/filename).read_bytes()).hexdigest()==expected
    assert np.allclose(fit(groups['85'],'lnI645')[1], fit(groups['85'],'ln_blank_ratio')[1])
    for group,g in groups.items():
        for name in baselines:
            X=design(g,name);y=g['y'];_,_,loo=fit(g,name)
            for i in (0,len(y)//2,len(y)-1):
                train=np.arange(len(y))!=i
                direct=X[i]@np.linalg.lstsq(X[train],y[train],rcond=None)[0]
                assert np.isclose(direct,loo[i],atol=1e-5), (group,name,i,direct,loo[i])
    print(json.dumps({"equations":equations,"pls":pls_results,"historical":historical,"transfers":transfers},indent=2))


if __name__ == '__main__':
    main()
