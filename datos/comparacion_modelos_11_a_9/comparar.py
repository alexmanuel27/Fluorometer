"""Fit every candidate on 11 only; compare unchanged predictions on 9.

The 9-sample batch is reused to explore models, so rankings are exploratory.
Requires numpy, openpyxl, matplotlib, scipy and scikit-learn.
"""
from pathlib import Path
import csv
import hashlib
import json
import sys

import numpy as np
import openpyxl
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.cross_decomposition import PLSRegression
from sklearn.model_selection import GridSearchCV, LeaveOneOut, cross_val_predict

OUT = Path(__file__).resolve().parent
DATA = OUT.parent
sys.path.insert(0, str(DATA/'relacion_645_680_sin_blanco'))
from analizar_relacion import metrics, markdown_table

WAVES = [460,485,510,535,560,585,610,645,680,705,730,760,810,860,900,940]
BLANKS = {'11':1256.,'9':1214.}  # One 645 nm ethanol blank per session, supplied by Alex.


def load(group):
    path=DATA/f'{group}Samples.xlsx'
    wb=openpyxl.load_workbook(path,data_only=True,read_only=True)
    source=list(wb.active.values);headers=source[0]
    rows=[(i,r) for i,r in enumerate(source[1:],2) if isinstance(r[1],(float,int))]
    wb.close()
    g={'c':np.array([r[1] for _,r in rows]),'id':np.array([r[0] for _,r in rows]),
       'row':np.array([i for i,_ in rows]),'blank645':BLANKS[group]}
    for nm in WAVES:g[str(nm)]=np.array([r[headers.index(f'I({nm})')] for _,r in rows])
    assert len(g['c'])==int(group)
    assert all(np.isfinite(g[str(nm)]).all() and (g[str(nm)]>0).all() for nm in WAVES)
    return g,hashlib.sha256(path.read_bytes()).hexdigest()


def candidates():
    specs=[]
    def add(key,label,formula,fn,blank='No'):
        specs.append({'id':key,'label':label,'formula_features':formula,'fn':fn,'blank':blank})
    for nm in WAVES:
        add(f'linear_{nm}',f'I{nm}',f'I{nm}',lambda g,nm=nm:g[str(nm)])
        add(f'log_{nm}',f'ln(I{nm})',f'ln(I{nm})',lambda g,nm=nm:np.log(g[str(nm)]))
    transforms={'ratio':lambda r:r,'sqrt':np.sqrt,'log':np.log}
    for denom in (645,705,460,860):
        for kind,fn in transforms.items():
            label=f'I680/I{denom}' if kind=='ratio' else f'{kind}(I680/I{denom})'
            add(f'{kind}_680_{denom}',label,label,lambda g,d=denom,f=fn:f(g['680']/g[str(d)]))
    for denom in (645,705):
        add(f'nd_680_{denom}',f'ND(680,{denom})',f'(I680-I{denom})/(I680+I{denom})',lambda g,d=denom:(g['680']-g[str(d)])/(g['680']+g[str(d)]))
    add('quadratic_ratio_680_645','Quadratic I680/I645','r; r², r=I680/I645',lambda g:np.c_[g['680']/g['645'],(g['680']/g['645'])**2])
    add('pair_raw','I645 + I680','I645; I680',lambda g:np.c_[g['645'],g['680']])
    add('pair_log','ln(I645) + ln(I680)','ln(I645); ln(I680)',lambda g:np.c_[np.log(g['645']),np.log(g['680'])])
    add('pair_mixed','ln(I645) + I680','ln(I645); I680',lambda g:np.c_[np.log(g['645']),g['680']])
    add('blank_log_645','ln(B645/I645)','ln(B645/I645)',lambda g:np.log(g['blank645']/g['645']),'645, sesión')
    add('blank_linear_645','I645/B645','I645/B645',lambda g:g['645']/g['blank645'],'645, sesión')
    add('blank_subtract_645','B645 - I645','B645-I645',lambda g:g['blank645']-g['645'],'645, sesión')
    for kind,fn in transforms.items():
        label=f'{kind}(B645 × I680/I645)'
        add(f'blank_{kind}_ratio',label,label,lambda g,f=fn:f(g['blank645']*g['680']/g['645']),'645, normalización parcial')
    return specs


def write_csv(name,rows):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    train,ht=load('11');test,hv=load('9')
    summary,estimates,equations=[],{},{}
    for spec in candidates():
        X=np.c_[np.ones(11),spec['fn'](train)];Xt=np.c_[np.ones(9),spec['fn'](test)]
        coef=np.linalg.lstsq(X,train['c'],rcond=None)[0]
        fitted=X@coef;pred=Xt@coef;loo=np.empty(11)
        for i in range(11):
            keep=np.arange(11)!=i
            loo[i]=X[i]@np.linalg.lstsq(X[keep],train['c'][keep],rcond=None)[0]
        fm,cm,tm=metrics(train['c'],fitted),metrics(train['c'],loo),metrics(test['c'],pred)
        summary.append({'model':spec['id'],'label':spec['label'],'blank':spec['blank'],
                        'r2_fit11':fm['r2'],'rmse_fit11':fm['rmse_ug_ml'],'rmse_LOO11':cm['rmse_ug_ml'],
                        'r2_pred9':tm['r2'],'rmse_pred9':tm['rmse_ug_ml'],'mae_pred9':tm['mae_ug_ml'],
                        'bias_pred9':tm['bias_ug_ml'],'max_error_pred9':tm['max_abs_error_ug_ml']})
        estimates[spec['id']]={'fit11':fitted,'pred9':pred,'loo11':loo}
        equations[spec['id']]={'features':spec['formula_features'],'coefficients':[float(v) for v in coef],
                               'equation':'C = intercept + sum(coefficient_i * feature_i), coefficients in feature order',
                               'blank':spec['blank']}

    # One PLS result; choose components using 11 only, nested LOO for its training diagnostic.
    X=np.column_stack([train[str(nm)] for nm in WAVES]);Xt=np.column_stack([test[str(nm)] for nm in WAVES])
    search=GridSearchCV(PLSRegression(scale=True),{'n_components':[1,2,3]},cv=LeaveOneOut(),scoring='neg_mean_squared_error')
    loo=cross_val_predict(search,X,train['c'],cv=LeaveOneOut()).reshape(-1)
    search.fit(X,train['c']);fitted=search.predict(X).reshape(-1);pred=search.predict(Xt).reshape(-1)
    fm,cm,tm=metrics(train['c'],fitted),metrics(train['c'],loo),metrics(test['c'],pred)
    label=f"PLS 16 channels ({search.best_params_['n_components']} component)"
    summary.append({'model':'pls','label':label,'blank':'No','r2_fit11':fm['r2'],'rmse_fit11':fm['rmse_ug_ml'],
                    'rmse_LOO11':cm['rmse_ug_ml'],'r2_pred9':tm['r2'],'rmse_pred9':tm['rmse_ug_ml'],
                    'mae_pred9':tm['mae_ug_ml'],'bias_pred9':tm['bias_ug_ml'],'max_error_pred9':tm['max_abs_error_ug_ml']})
    estimates['pls']={'fit11':fitted,'pred9':pred,'loo11':loo}
    equations['pls']={'n_components':search.best_params_['n_components'],'channel_order':WAVES,'scale':True}
    ranked=sorted(summary,key=lambda r:r['rmse_pred9']);byid={r['model']:r for r in summary}
    write_csv('ranking_modelos.csv',ranked)
    predictions=[]
    for key,est in estimates.items():
        for group,g,p in [('11',train,est['fit11']),('9',test,est['pred9'])]:
            for i,v in enumerate(p):
                predictions.append({'model':key,'dataset_n':int(group),'sample':int(g['id'][i]),'excel_row':int(g['row'][i]),
                                    'reference_ug_ml':g['c'][i],'predicted_ug_ml':v,'error_ug_ml':v-g['c'][i]})
    write_csv('predicciones_todos_modelos.csv',predictions)
    (OUT/'ecuaciones.json').write_text(json.dumps({'calibration_n':11,'comparison_n':9,'blank645':BLANKS,
                                                'source_sha256':{'11':ht,'9':hv},'models':equations},indent=2),encoding='utf-8')

    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    def panels(ids,filename,columns=3):
        rows=(len(ids)+columns-1)//columns
        fig,axes=plt.subplots(rows,columns,figsize=(columns*4.5,rows*4.1),constrained_layout=True,squeeze=False)
        for ax,key in zip(axes.flat,ids):
            r=byid[key];e=estimates[key];lo=min(0,float(e['pred9'].min()));hi=max(4.15,float(e['pred9'].max())+.1)
            ax.plot([lo,hi],[lo,hi],'--',color='#777777',lw=1)
            ax.scatter(train['c'],e['fit11'],s=24,color='#d66c1d',alpha=.6,label='11 calibration')
            ax.scatter(test['c'],e['pred9'],s=32,color='#21966a',label='9 comparison')
            ax.set(xlabel='Reference (µg/mL)',ylabel='Predicted (µg/mL)',title=r['label'],xlim=(lo,hi),ylim=(lo,hi))
            ax.text(.04,.96,f"R² on 9 = {r['r2_pred9']:.4f}\nRMSE on 9 = {r['rmse_pred9']:.3f} µg/mL",transform=ax.transAxes,ha='left',va='top',fontsize=9,bbox={'facecolor':'white','edgecolor':'#dddddd','alpha':.9})
            ax.grid(alpha=.15)
        for ax in list(axes.flat)[len(ids):]:ax.set_visible(False)
        axes.flat[0].legend(loc='lower right',fontsize=8)
        fig.suptitle('All coefficients fitted on 11; same equations applied to 9',fontsize=14)
        fig.savefig(OUT/filename,dpi=180);plt.close(fig)
    panels(['log_645','blank_log_645','sqrt_680_645','blank_sqrt_ratio','sqrt_680_705','sqrt_680_860'],
           '01_comparacion_con_y_sin_blanco.png')
    panels([r['model'] for r in ranked[:9]],'02_mejores_modelos_en_9.png')
    panels([f'log_{nm}' for nm in WAVES],'03_canales_individuales_log.png',4)

    keys=list(dict.fromkeys([r['model'] for r in ranked[:10]]+['log_645','blank_log_645','linear_680','pair_mixed','pls']))
    fig,ax=plt.subplots(figsize=(12,7.5),constrained_layout=True)
    yy=np.arange(len(keys))
    ax.barh(yy-.18,[byid[k]['rmse_LOO11'] for k in keys],height=.36,color='#d66c1d',label='LOO on 11')
    ax.barh(yy+.18,[byid[k]['rmse_pred9'] for k in keys],height=.36,color='#2675b8',label='Prediction on 9')
    ax.set_yticks(yy,[byid[k]['label'] for k in keys]);ax.invert_yaxis()
    ax.set(xlabel='RMSE (µg/mL)',title='Small error on calibration does not guarantee transfer')
    ax.legend(loc='lower right');ax.grid(axis='x',alpha=.15)
    fig.savefig(OUT/'04_error_calibracion_vs_transferencia.png',dpi=180);plt.close(fig)

    best_free=next(r for r in ranked if r['blank']=='No')
    best_blank=next(r for r in ranked if r['blank']!='No')
    r=lambda key: byid[key]
    heads=['Modelo','Blanco','R² ajuste 11','RMSE ajuste 11','RMSE LOO 11','R² predicción 9','RMSE predicción 9','Sesgo 9']
    def rows(records):return [[v['label'],v['blank'],f"{v['r2_fit11']:.4f}",f"{v['rmse_fit11']:.4f}",f"{v['rmse_LOO11']:.4f}",f"{v['r2_pred9']:.4f}",f"{v['rmse_pred9']:.4f}",f"{v['bias_pred9']:+.4f}"] for v in records]
    report=['# Modelos ajustados con 11 y aplicados a 9','', 'Fecha: 18 de octubre de 2026. Todos los errores de concentración están en µg/mL.',
            '', '## Qué significaban las tablas anteriores',
            'R² de ajuste describe las mismas 11 muestras que fijaron los coeficientes. LOO 11 deja una muestra fuera por turno para revisar interpolación dentro de esa tanda. Predicción 9 aplica los coeficientes fijados con 11 a las nueve diluciones.',
            'Para C = 24,62904595 − 3,46519495 ln(I645), R² de ajuste 11 = 0,9981 y RMSE ajuste 11 = 0,0325. Al aplicar a 9, R² predictivo = 0,8893 y RMSE = 0,4051. Estos valores coinciden con el informe y las gráficas previas.',
            'La fórmula de raíz I680/I645 se exploró posteriormente y es otra relación: sobre 9 alcanza R² = 0,9906 y RMSE = 0,1181. El informe inicial comparó, entre otros, I680/I705, no su raíz ni la raíz I680/I645.',
            '', '## Diseño de las pruebas',
            f'Se comparan {len(summary)} modelos: canales individuales lineales y logarítmicos, cocientes de 680 con 645/705/460/860, raíces y logaritmos de cocientes, contrastes normalizados, un cociente cuadrático, combinaciones de dos canales y PLS. 410/435 se excluyen por saturación, aceptada como condición del equipo. 485 se conserva como predictor; no se usan las desviaciones como pesos.',
            'Los coeficientes se ajustan solo con las 11 muestras. PLS elige 1–3 componentes usando exclusivamente las 11; su LOO es anidado. No se excluyen muestras, no se usa la concentración de las nueve para calcular coeficientes y no se recortan predicciones negativas.',
            'Las nueve se consultan repetidamente para explorar y ordenar modelos. Por tanto, el ranking es exploratorio y no es una validación ciega ni demuestra el rendimiento en sesiones nuevas.',
            '', '## Blanco de sesión: qué se usa',
            'Se usa un único blanco645 por sesión: B645=1256 para las 11 y B645=1214 para las nueve, aportados por Alex. No se solicita ni utiliza blanco por muestra. No hay blanco680 ni de otros canales: no se inventa ni se resta.',
            'Las pruebas con blanco645 incluyen ln(B645/I645), I645/B645 y B645−I645. También se compara transformar B645·I680/I645: esto normaliza el denominador I645 por su blanco mientras mantiene I680 tal como se midió. Es una normalización parcial empírica, no una sustracción de fondo680 ni una corrección óptica completa.',
            'Dividir ambos canales por el mismo B645 dejaría el cociente I680/I645 exactamente igual. Con un único valor de blanco en la tanda de entrenamiento tampoco se puede aprender un efecto independiente del blanco: solo probar estas normalizaciones predefinidas.',
            '', '## Comparaciones principales',
            markdown_table(heads,rows([r(k) for k in ['log_645','blank_log_645','sqrt_680_645','blank_sqrt_ratio','sqrt_680_705','sqrt_680_860','linear_680','pair_mixed','pls']])),
            '', '## Mejores resultados de esta exploración',
            f"Sin blanco: {best_free['label']}, RMSE9={best_free['rmse_pred9']:.5f}, R²9={best_free['r2_pred9']:.5f}.",
            f"Con blanco645: {best_blank['label']}, RMSE9={best_blank['rmse_pred9']:.5f}, R²9={best_blank['r2_pred9']:.5f}.",
            'Las raíces de cocientes transfieren mejor que varios canales individuales en esta comparación. El mejor ajuste dentro de 11 no determina el mejor resultado sobre 9.',
            '', '## Ecuaciones de interés (coeficientes calculados solo con 11)']
    for key in list(dict.fromkeys([best_free['model'],best_blank['model'],'sqrt_680_645','log_645','blank_log_645'])):
        eq=equations[key];coef=eq['coefficients']
        report.append(f"- {byid[key]['label']}: C = {coef[0]:.8f} {coef[1]:+.8f} × [{eq['features']}].")
    report += ['', 'Las intensidades corresponden a los promedios suministrados en los Excel. C se expresa en µg/mL. B645 debe ser el blanco de la misma sesión, medido con la configuración del equipo correspondiente.',
               '', '## Ranking completo por error en las nueve',markdown_table(heads,rows(ranked)),
               '', '## Predicciones de las nueve con los mejores modelos',
               markdown_table(['ID','Referencia',best_free['label'],best_blank['label'],'sqrt(I680/I645)'],
                              [[int(test['id'][i]),f"{test['c'][i]:.4f}",f"{estimates[best_free['model']]['pred9'][i]:.4f}",f"{estimates[best_blank['model']]['pred9'][i]:.4f}",f"{estimates['sqrt_680_645']['pred9'][i]:.4f}"] for i in range(9)]),
               '', '## Límites concretos',
               'Las 11 cubren 0,7944–3,07062 µg/mL y las nueve 0,0244–3,9098. Por tanto, las nueve incluyen extrapolación a ambos extremos. Las nueve proceden de un mismo extracto madre. La incertidumbre compartida de esa referencia no se conoce. R² alto no equivale a precisión relativa alta cerca de cero.',
               'Las predicciones negativas cerca de cero y todos los errores por muestra se conservan en los CSV. Las figuras muestran concentraciones predichas, no intervalos de confianza: no se presenta la desviación de repetición instrumental como incertidumbre total del modelo.',
               'Se reconoce la presencia de filtros espectrales incorporados en el sensor. Estas pruebas no cambian el montaje ni el firmware.',
               '', '## Archivos',
               '01: comparación principal con y sin blanco. 02: nueve mejores modelos sobre las nueve muestras (selección exploratoria). 03: todos los canales individuales en forma logarítmica. 04: error dentro de 11 frente al error sobre 9. Los CSV guardan todos los resultados y predicciones; ecuaciones.json guarda coeficientes y procedencia.',
               'Fuentes: 11Samples.xlsx y 9Samples.xlsx, Sheet1. Blancos645 procedentes del mensaje de Alex, no de los Excel. Los originales permanecen intactos.']
    (OUT/'informe.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    assert hashlib.sha256((DATA/'11Samples.xlsx').read_bytes()).hexdigest()==ht
    assert hashlib.sha256((DATA/'9Samples.xlsx').read_bytes()).hexdigest()==hv
    # Same scalar formula as the earlier result; blank scaling is verified independently.
    a,b=equations['sqrt_680_645']['coefficients']
    assert np.allclose(estimates['sqrt_680_645']['pred9'],a+b*np.sqrt(test['680']/test['645']))
    assert np.allclose(estimates['blank_sqrt_ratio']['pred9'],a+b*np.sqrt(test['680']/test['645']*BLANKS['9']/BLANKS['11']))
    assert np.allclose(equations['log_645']['coefficients'],[24.629045946394292,-3.46519495286695])
    print(json.dumps({'models':len(summary),'best_without_blank':best_free,'best_with_blank':best_blank,
                      'top10':ranked[:10]},indent=2))


if __name__=='__main__':main()
