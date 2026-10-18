"""Standalone cross-validation: the only workbook opened is 11Samples.xlsx.

Run from any directory. Requires numpy, openpyxl, matplotlib, scikit-learn.
All plotted points are leave-one-out predictions, never full-fit predictions.
"""
from pathlib import Path
import csv
import hashlib
import json

import numpy as np
import openpyxl
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.cross_decomposition import PLSRegression

OUT=Path(__file__).resolve().parent
INPUT=OUT.parent/'11Samples.xlsx'
WAVELENGTHS=[460,485,510,535,560,585,610,645,680,705,730,760,810,860,900,940]
SESSION_BLANK_645=1256.


def read_input():
    source_hash=hashlib.sha256(INPUT.read_bytes()).hexdigest()
    book=openpyxl.load_workbook(INPUT,data_only=True,read_only=True)
    sheet=book.active
    source=list(sheet.values);headers=source[0]
    rows=[(i,r) for i,r in enumerate(source[1:],2) if isinstance(r[1],(float,int))]
    book.close()
    assert len(rows)==11
    g={'y':np.array([r[1] for _,r in rows],dtype=float),
       'id':np.array([r[0] for _,r in rows],dtype=int),
       'row':np.array([i for i,_ in rows],dtype=int)}
    assert len(set(g['id']))==11 and np.isfinite(g['y']).all()
    for nm in WAVELENGTHS:
        g[nm]=np.array([r[headers.index(f'I({nm})')] for _,r in rows],dtype=float)
        assert np.isfinite(g[nm]).all() and (g[nm]>0).all()
    for nm in (410,435):
        values=np.array([r[headers.index(f'I({nm})')] for _,r in rows])
        assert np.all(values==2**32), 'Review saturation exclusion if these channels change'
    return g,source_hash


def catalogue(g):
    models=[]
    def add(key,label,feature_names,features,blank=False):
        x=np.asarray(features)
        if x.ndim==1:x=x[:,None]
        models.append({'id':key,'label':label,'feature_names':feature_names,'x':x,'blank':blank,'kind':'OLS'})
    for nm in WAVELENGTHS:
        add(f'linear_{nm}',f'I{nm}',[f'I{nm}'],g[nm])
        add(f'log_{nm}',f'ln(I{nm})',[f'ln(I{nm})'],np.log(g[nm]))
    for nm in (645,680):
        z=np.log(g[nm])
        add(f'quadratic_log_{nm}',f'Quadratic ln(I{nm})',[f'ln(I{nm})',f'ln(I{nm})²'],np.c_[z,z*z])
    for denom in (645,705,460,860):
        r=g[680]/g[denom]
        for key,fn in [('ratio',lambda x:x),('sqrt',np.sqrt),('log',np.log)]:
            name=f'I680/I{denom}' if key=='ratio' else f'{key}(I680/I{denom})'
            add(f'{key}_680_{denom}',name,[name],fn(r))
    r=g[680]/g[645]
    add('quadratic_ratio','Quadratic I680/I645',['r=I680/I645','r²'],np.c_[r,r*r])
    for denom in (645,705):
        name=f'(I680-I{denom})/(I680+I{denom})'
        add(f'nd_680_{denom}',f'ND(680,{denom})',[name],(g[680]-g[denom])/(g[680]+g[denom]))
    add('pair_raw','I645 + I680',['I645','I680'],np.c_[g[645],g[680]])
    add('pair_log','ln(I645) + ln(I680)',['ln(I645)','ln(I680)'],np.c_[np.log(g[645]),np.log(g[680])])
    add('pair_mixed','ln(I645) + I680',['ln(I645)','I680'],np.c_[np.log(g[645]),g[680]])
    add('blank_log_645','ln(B645/I645)',['ln(B645/I645)'],np.log(SESSION_BLANK_645/g[645]),True)
    add('blank_sqrt_ratio','sqrt(B645 × I680/I645)',['sqrt(B645 × I680/I645)'],np.sqrt(SESSION_BLANK_645*r),True)
    raw=np.column_stack([g[nm] for nm in WAVELENGTHS])
    for count in (1,2,3):
        models.append({'id':f'pls_{count}','label':f'PLS, {count} components (16 channels)',
                       'feature_names':[str(nm) for nm in WAVELENGTHS],'x':raw,'blank':False,'kind':'PLS','components':count})
    return models


def fit_predict(model,x,y,xt):
    if model['kind']=='PLS':
        estimator=PLSRegression(n_components=model['components'],scale=True)
        estimator.fit(x,y)
        return estimator.predict(xt).reshape(-1)
    design=np.c_[np.ones(len(x)),x]
    coef=np.linalg.lstsq(design,y,rcond=None)[0]
    return np.c_[np.ones(len(xt)),xt]@coef


def scores(y,p):
    e=p-y
    return {'r2_cv11':float(1-np.sum(e**2)/np.sum((y-y.mean())**2)),
            'rmse_cv11':float(np.sqrt(np.mean(e**2))),
            'mae_cv11':float(np.mean(abs(e))), 'bias_cv11':float(e.mean()),
            'max_error_cv11':float(max(abs(e)))}


def write_csv(name,rows):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def table(headers,rows):
    return '| '+' | '.join(headers)+' |\n|'+'|'.join(['---']*len(headers))+'|\n'+''.join('| '+' | '.join(map(str,r))+' |\n' for r in rows)


def main():
    g,source_hash=read_input()
    models=catalogue(g);y=g['y'];n=len(y)
    results=[];predictions={};exported=[];coefficients={}
    for m in models:
        x=m['x'];p=np.full(n,np.nan);seen=np.zeros(n,dtype=int)
        for i in range(n):
            keep=np.arange(n)!=i
            assert keep.sum()==10 and not keep[i]
            # PLS centering/scaling is fitted separately inside each training fold.
            p[i]=fit_predict(m,x[keep],y[keep],x[i:i+1])[0]
            seen[i]+=1
        assert np.all(seen==1) and np.isfinite(p).all()
        result={'model':m['id'],'label':m['label'],'method':m['kind'],
                'n_samples':11,'n_folds':11,'training_samples_per_fold':10,
                'blank645': 'Sesión, constante' if m['blank'] else 'No',**scores(y,p)}
        results.append(result);predictions[m['id']]=p
        for i in range(n):
            exported.append({'model':m['id'],'sample':int(g['id'][i]),'excel_row':int(g['row'][i]),
                             'reference_ug_ml':y[i],'cv_prediction_ug_ml':p[i],'cv_error_ug_ml':p[i]-y[i]})
        if m['kind']=='OLS':
            coefficients[m['id']]={'features':m['feature_names'],'coefficients':np.linalg.lstsq(np.c_[np.ones(n),x],y,rcond=None)[0].tolist(),
                                   'purpose':'Refit on all 11 for future use; not used for CV predictions.'}
        else:coefficients[m['id']]={'components':m['components'],'channel_order':WAVELENGTHS}
    ranked=sorted(results,key=lambda r:(r['rmse_cv11'],r['model']))
    byid={r['model']:r for r in results}
    write_csv('comparacion_cv_11.csv',ranked)
    write_csv('predicciones_cv_11.csv',exported)
    metadata={'input_file':str(INPUT),'input_sha256':source_hash,'n_samples':n,
              'validation':'Leave-one-out: train on 10, predict 1, repeated 11 times',
              'blank645':SESSION_BLANK_645,'model_count':len(models),'models':ranked,'refit_equations':coefficients}
    (OUT/'resultados_11.json').write_text(json.dumps(metadata,indent=2,ensure_ascii=False),encoding='utf-8')

    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    def panels(ids,name,columns):
        rows=(len(ids)+columns-1)//columns
        fig,axes=plt.subplots(rows,columns,figsize=(columns*4.2,rows*4.2),constrained_layout=True,squeeze=False)
        for ax,key in zip(axes.flat,ids):
            result=byid[key];p=predictions[key]
            low=min(.65,float(p.min())-.1);high=max(3.2,float(p.max())+.1)
            ax.plot([low,high],[low,high],'--',color='#777777',lw=1)
            ax.scatter(y,p,color='#2675b8',s=35)
            ax.set(xlabel='Reference Chl(a) (µg/mL)',ylabel='LOO predicted Chl(a) (µg/mL)',
                   title=result['label'],xlim=(low,high),ylim=(low,high))
            ax.text(.04,.96,f"CV R² = {result['r2_cv11']:.4f}\nCV RMSE = {result['rmse_cv11']:.4f} µg/mL",transform=ax.transAxes,va='top',fontsize=9,bbox={'facecolor':'white','edgecolor':'#dddddd','alpha':.95})
            ax.grid(alpha=.15)
        for ax in list(axes.flat)[len(ids):]:ax.set_visible(False)
        fig.suptitle('11 samples only: each point predicted from the other 10',fontsize=14)
        fig.savefig(OUT/name,dpi=180);plt.close(fig)
    # Show distinct forms rather than two mathematically equivalent blank scalings.
    top_ids=[r['model'] for r in ranked if r['blank645']=='No'][:8]
    panels(top_ids,'01_modelos_cv_11.png',4)
    panels([f'log_{nm}' for nm in WAVELENGTHS],'03_canales_cv_11.png',4)
    top=[byid[key] for key in top_ids]+[byid[key] for key in ['sqrt_680_705','linear_645','linear_680','pls_1','pls_2','pls_3'] if key not in top_ids]
    fig,ax=plt.subplots(figsize=(11,7),constrained_layout=True)
    ax.barh(np.arange(len(top)),[r['rmse_cv11'] for r in top],color='#2675b8')
    ax.set_yticks(np.arange(len(top)),[r['label'] for r in top]);ax.invert_yaxis()
    ax.set(xlabel='Leave-one-out RMSE on 11 (µg/mL)',title='Same cross-validation for every model; lower is better')
    ax.grid(axis='x',alpha=.15)
    fig.savefig(OUT/'02_errores_cv_11.png',dpi=180);plt.close(fig)

    row_values=lambda rr:[[r['label'],r['blank645'],f"{r['r2_cv11']:.5f}",f"{r['rmse_cv11']:.5f}",f"{r['mae_cv11']:.5f}",f"{r['max_error_cv11']:.5f}"] for r in rr]
    report=['# Validación cruzada exclusivamente sobre las 11 muestras','',
            'Fecha: 18 de octubre de 2026. Único archivo de entrada: 11Samples.xlsx, Sheet1. No se abre ni se utiliza ningún otro conjunto de muestras.',
            '', '## Método',
            f'Se comparan {len(models)} modelos con el mismo procedimiento: dejar una muestra fuera, ajustar con las otras diez y predecir la omitida; repetir once veces. Cada muestra tiene exactamente una predicción de validación por modelo. Todas las gráficas y métricas de este informe se calculan con esas predicciones, no con el ajuste sobre las once a la vez.',
            'R² CV = 1 − suma de errores de predicción al cuadrado / variación total de las concentraciones de referencia. RMSE CV es la raíz del error cuadrático medio, en µg/mL. Mayor R² y menor RMSE indican mejor resultado para esta misma validación.',
            'Los modelos OLS tienen intercepto y uno o dos predictores. PLS utiliza los 16 canales no saturados, con 1, 2 o 3 componentes como candidatos fijos; la escala y el centrado se calculan dentro de cada turno exclusivamente con sus diez muestras de entrenamiento. Se conserva cada muestra, sin eliminar atípicos ni recortar predicciones.',
            '', '## Comparación principal',
            table(['Modelo','Blanco645','R² CV11','RMSE CV11 (µg/mL)','MAE CV11','Error máximo CV11'],row_values([byid[k] for k in top_ids])),
            '', '## Blanco de sesión',
            'Se considera el valor aportado por Alex: B645=1256. Es constante para las once muestras. Con intercepto, usar ln(B645/I645) es matemáticamente equivalente a usar ln(I645); sus predicciones de validación coinciden. Lo mismo ocurre entre sqrt(B645·I680/I645) y sqrt(I680/I645): solo cambia la escala del predictor.',
            'Por eso esta validación de una sola sesión no puede cuantificar la mejora de un blanco ante cambios entre sesiones. Las variantes se incluyen en la tabla completa, pero no se duplican en la gráfica principal. No se supone blanco de 680 ni de otros canales.',
            '', '## Ecuaciones reajustadas con las once para posible uso posterior',
            'Los coeficientes de abajo se calculan con las once muestras juntas. No se usaron para calcular los resultados de validación de la tabla anterior: en validación se vuelve a ajustar cada modelo con diez muestras en cada turno.',
            table(['Modelo','Predictores x1; x2','a (intercepto)','b1','b2'],
                  [[byid[key]['label'],'; '.join(coefficients[key]['features']),
                    f"{coefficients[key]['coefficients'][0]:.8f}",
                    f"{coefficients[key]['coefficients'][1]:.8f}",
                    f"{coefficients[key]['coefficients'][2]:.8f}" if len(coefficients[key]['coefficients'])>2 else '—']
                   for key in top_ids if 'coefficients' in coefficients[key]]),
            'Forma de la ecuación: C = a + b1·x1 + b2·x2, omitiendo x2 cuando solo existe un predictor. ln es logaritmo natural; C está en µg/mL. ND(680,645)=(I680−I645)/(I680+I645).',
            '', '## Tabla completa: todos los valores son validación cruzada sobre 11',
            table(['Modelo','Blanco645','R² CV11','RMSE CV11 (µg/mL)','MAE CV11','Error máximo CV11'],row_values(ranked)),
            '', '## Predicciones de validación de los modelos principales',
            table(['ID','Referencia']+[byid[key]['label'] for key in top_ids[:4]],
                  [[int(g['id'][i]),f'{y[i]:.5f}']+[f'{predictions[key][i]:.5f}' for key in top_ids[:4]] for i in range(n)]),
            '', '## Alcance',
            'El rango de referencia es 0,7944–3,07062 µg/mL. Son once muestras de una única tanda. El ranking describe este conjunto y estas condiciones. Diferencias pequeñas de CV no demuestran superioridad en otras sesiones. Elegir el mínimo entre muchos modelos introduce optimismo de selección; las métricas aquí son por candidato, no una estimación anidada del proceso de elegir el mejor.',
            'Los canales 410/435 se mantienen excluidos por saturación. Las desviaciones instrumentales no se usan como pesos ni se confunden con incertidumbre de la concentración de referencia. Los filtros incorporados del sensor y el montaje no se modifican.',
            '', '## Resultados guardados',
            '01_modelos_cv_11.png contiene ocho relaciones distintas con predicciones dejar-una-fuera. 02_errores_cv_11.png compara sus errores y varios controles. 03_canales_cv_11.png muestra los dieciséis canales individuales con transformación logarítmica. Los CSV contienen el ranking completo y cada predicción de validación. resultados_11.json guarda procedencia y ecuaciones reajustadas con las once para posible uso posterior; estas ecuaciones completas no se utilizaron para generar las predicciones de validación.',
            f'SHA-256 de la entrada: {source_hash}. El Excel original permanece intacto.']
    (OUT/'informe.md').write_text('\n'.join(report)+'\n',encoding='utf-8')

    # Meaningful checks: same fold predictions for the constant-blank equivalents.
    assert np.allclose(predictions['log_645'],predictions['blank_log_645'],atol=1e-10)
    assert np.allclose(predictions['sqrt_680_645'],predictions['blank_sqrt_ratio'],atol=1e-10)
    # Independently verify the univariate fold fit using centered covariance.
    for i in range(n):
        keep=np.arange(n)!=i;x=np.log(g[645][keep]);yy=y[keep]
        b=np.sum((x-x.mean())*(yy-yy.mean()))/np.sum((x-x.mean())**2)
        direct=yy.mean()+b*(np.log(g[645][i])-x.mean())
        assert np.isclose(direct,predictions['log_645'][i],atol=1e-10)
    assert hashlib.sha256(INPUT.read_bytes()).hexdigest()==source_hash
    print(json.dumps({'input':str(INPUT),'model_count':len(models),'top_distinct':[byid[key] for key in top_ids],
                      'checks':'11 predictions per model; folds disjoint; independent univariate verification; source unchanged'},indent=2))


if __name__=='__main__':main()
