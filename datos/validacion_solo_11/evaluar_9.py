"""Evaluation stage: apply the already frozen model; never search or refit on 9."""
from pathlib import Path
import csv
import hashlib
import json
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT=Path(__file__).resolve().parent
DATA=OUT.parent
sys.path.insert(0,str(DATA/'comparacion_modelos_11_a_9'))
from comparar import candidates, load, metrics, markdown_table


def main():
    path=OUT/'modelo_fijado.json'
    frozen_bytes=path.read_bytes();locked_hash=hashlib.sha256(frozen_bytes).hexdigest()
    m=json.loads(frozen_bytes)
    # The selected model is known before opening comparison samples.
    key=m['selected_id']
    if 'components' in m:
        from sklearn.cross_decomposition import PLSRegression
        train,ht=load('11')
        assert ht==m['training_sha256']
        nm=(460,485,510,535,560,585,610,645,680,705,730,760,810,860,900,940)
        estimator=PLSRegression(n_components=m['components'],scale=True).fit(np.column_stack([train[str(w)] for w in nm]),train['c'])
        g,h9=load('9')
        prediction=estimator.predict(np.column_stack([g[str(w)] for w in nm])).reshape(-1)
        equation=f"PLS with {m['components']} components, fixed from 11"
    else:
        spec=next(s for s in candidates() if s['id']==key)
        coef=np.array(m['coefficients'])
        g,h9=load('9')
        X=np.c_[np.ones(len(g['c'])),spec['fn'](g)]
        prediction=X@coef
        equation='C = '+f'{coef[0]:.8f}'+''.join(f' {v:+.8f} × feature{i}' for i,v in enumerate(coef[1:],1))+f"; features: {m['features']}"
    result=metrics(g['c'],prediction)
    records=[{'sample':int(g['id'][i]),'reference_ug_ml':g['c'][i],
              'predicted_ug_ml':prediction[i],'error_ug_ml':prediction[i]-g['c'][i]} for i in range(len(prediction))]
    with (OUT/'predicciones_9.csv').open('w',encoding='utf-8-sig',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(records[0]));wr.writeheader();wr.writerows(records)
    (OUT/'resultado_9.json').write_text(json.dumps({'frozen_model_sha256':locked_hash,'comparison_sha256':h9,'selected_id':key,'metrics':result},indent=2),encoding='utf-8')
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,axs=plt.subplots(1,2,figsize=(11,5),constrained_layout=True)
    lo=min(0,float(prediction.min()));hi=max(4.15,float(prediction.max())+.1)
    axs[0].plot([lo,hi],[lo,hi],'--',color='#777777',lw=1,label='Ideal prediction')
    axs[0].scatter(g['c'],prediction,color='#21966a',s=40)
    for i in range(len(prediction)):
        axs[0].annotate(str(int(g['id'][i])),(g['c'][i],prediction[i]),xytext=(5,4),textcoords='offset points',fontsize=9)
    axs[0].set(xlabel='Reference chlorophyll a (µg/mL)',ylabel='Predicted chlorophyll a (µg/mL)',title='Fixed model applied to 9 samples',xlim=(lo,hi),ylim=(lo,hi))
    axs[0].text(.04,.96,f"R² = {result['r2']:.4f}\nRMSE = {result['rmse_ug_ml']:.3f} µg/mL",transform=axs[0].transAxes,ha='left',va='top',bbox={'facecolor':'white','edgecolor':'#dddddd'})
    axs[0].legend(loc='lower right')
    axs[1].axhline(0,color='#777777',lw=1)
    axs[1].scatter(g['c'],prediction-g['c'],color='#21966a',s=40)
    axs[1].set(xlabel='Reference chlorophyll a (µg/mL)',ylabel='Prediction − reference (µg/mL)',title='Errors on 9; no recalibration')
    for ax in axs:ax.grid(alpha=.15)
    fig.suptitle('Selection by cross-validation on 11 only: '+m['selected_label'],fontsize=13)
    fig.savefig(OUT/'modelo_fijado_aplicado_a_9.png',dpi=180);plt.close(fig)
    finalists=[]
    specs={s['id']:s for s in candidates()}
    fig,axes=plt.subplots(2,4,figsize=(17,8.5),constrained_layout=True)
    for ax,finalist in zip(axes.flat,m['finalists']):
        if 'components' in finalist:
            from sklearn.cross_decomposition import PLSRegression
            train,ht=load('11');assert ht==m['training_sha256']
            nm=(460,485,510,535,560,585,610,645,680,705,730,760,810,860,900,940)
            estimator=PLSRegression(n_components=finalist['components'],scale=True).fit(np.column_stack([train[str(w)] for w in nm]),train['c'])
            p=estimator.predict(np.column_stack([g[str(w)] for w in nm])).reshape(-1)
        else:
            s=specs[finalist['id']]
            p=np.c_[np.ones(len(g['c'])),s['fn'](g)]@np.array(finalist['coefficients'])
        tm=metrics(g['c'],p)
        finalists.append({'model':finalist['id'],'label':finalist['label'],'blank':finalist['blank'],
                          'rmse_cv11':finalist['rmse_cv11'],'r2_pred9':tm['r2'],'rmse_pred9':tm['rmse_ug_ml']})
        low=min(0,float(p.min()));high=max(4.15,float(p.max())+.1)
        ax.plot([low,high],[low,high],'--',color='#777777',lw=1)
        ax.scatter(g['c'],p,color='#21966a',s=28)
        ax.set(xlabel='Reference (µg/mL)',ylabel='Predicted (µg/mL)',title=finalist['label'],xlim=(low,high),ylim=(low,high))
        ax.text(.03,.97,f"CV11 RMSE: {finalist['rmse_cv11']:.3f}\n9 RMSE: {tm['rmse_ug_ml']:.3f}\n9 R²: {tm['r2']:.4f}",transform=ax.transAxes,va='top',fontsize=9,bbox={'facecolor':'white','edgecolor':'#dddddd'})
        ax.grid(alpha=.15)
    fig.suptitle('Eight finalists fixed by CV on 11; order unchanged after evaluating 9',fontsize=14)
    fig.savefig(OUT/'ocho_finalistas_orden_cv11.png',dpi=180);plt.close(fig)
    with (OUT/'finalistas_9.csv').open('w',encoding='utf-8-sig',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(finalists[0]));wr.writeheader();wr.writerows(finalists)
    with (OUT/'ranking_cv_11.csv').open(encoding='utf-8-sig') as f:ranking=list(csv.DictReader(f))
    report=['# Selección solo con 11; evaluación posterior en 9','',
            'El procedimiento de entrenamiento abre únicamente 11Samples.xlsx. Compara 59 candidatos predefinidos usando dejar-una-fuera. Las equivalencias numéricas favorecen menor complejidad y ausencia de blanco. El modelo elegido se guarda en modelo_fijado.json antes de que la etapa de evaluación abra 9Samples.xlsx.',
            f"Modelo elegido: **{m['selected_label']}**.",equation,
            '',f"CV del modelo elegido sobre 11: RMSE={m['cv_selected_model']['rmse']:.5f} µg/mL, R²={m['cv_selected_model']['r2']:.5f}.",
            f"CV anidada del procedimiento completo de selección sobre 11: RMSE={m['nested_cv_selection_procedure']['rmse_ug_ml']:.5f} µg/mL, R²={m['nested_cv_selection_procedure']['r2']:.5f}. En cada turno se elige el modelo usando solo las otras diez, con una validación interna.",
            '', '## Mejores candidatos según las 11',
            markdown_table(['Modelo','Blanco','RMSE CV11','R² CV11'],[[r['label'],r['blank'],f"{float(r['rmse']):.5f}",f"{float(r['r2']):.5f}"] for r in ranking[:10]]),
            '', '## Ocho finalistas: orden fijado por CV11 antes de evaluar las nueve',
            markdown_table(['Modelo','Blanco','RMSE CV11','R² predicción 9','RMSE predicción 9'],
                           [[r['label'],r['blank'],f"{r['rmse_cv11']:.5f}",f"{r['r2_pred9']:.5f}",f"{r['rmse_pred9']:.5f}"] for r in finalists]),
            'Esta tabla mantiene el orden determinado por las 11; no se reordena por el error en nueve y no modifica la selección principal.',
            '', '## Resultado en las nueve después de fijar la ecuación',
            markdown_table(['n','R² predictivo','RMSE','MAE','Sesgo','Error máximo'],[[result['n'],f"{result['r2']:.5f}",f"{result['rmse_ug_ml']:.5f}",f"{result['mae_ug_ml']:.5f}",f"{result['bias_ug_ml']:+.5f}",f"{result['max_abs_error_ug_ml']:.5f}"]]),
            markdown_table(['ID','Referencia','Predicción','Error'],[[r['sample'],f"{r['reference_ug_ml']:.4f}",f"{r['predicted_ug_ml']:.4f}",f"{r['error_ug_ml']:+.4f}"] for r in records]),
            'Todos los errores de concentración están en µg/mL. No se cambia el modelo ni sus coeficientes después de este resultado.',
            '', '## Interpretación',
            'En los análisis anteriores los coeficientes también se calcularon con 11, pero las nueve se usaron para comparar y elegir formas funcionales. Este nuevo protocolo elimina ese uso de las nueve durante la selección y el ajuste de esta ejecución.',
            'Las nueve ya fueron examinadas en análisis previos y el catálogo de candidatos fue explorado con ellas. Por tanto, esto es un reanálisis con separación del entrenamiento, no una prueba prospectiva completamente ciega. Para una evaluación ciega se necesitarían muestras nuevas después de fijar el catálogo y la ecuación.',
            'La validación sobre 11 evalúa muestras de una única tanda. No aprende por sí misma la variación entre sesiones. Las nueve incluyen concentraciones fuera del rango 0,7944–3,07062 usado para calibrar. Se conservan todos los puntos y predicciones.',
            'Los blancos de sesión permanecen entre las opciones del catálogo, pero la ecuación ganadora se decide solo con CV11. Un blanco constante dentro de esa sesión no permite aprender la respuesta a cambios de blanco entre sesiones.']
    (OUT/'informe.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    assert hashlib.sha256(path.read_bytes()).hexdigest()==locked_hash
    print(json.dumps({'selected':key,'equation':equation,'metrics_9':result},indent=2))


if __name__=='__main__':main()
