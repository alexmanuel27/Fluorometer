"""Fit ln(I645) on 11 samples and apply unchanged to 9 and 85. No blank.
Requires numpy, openpyxl, matplotlib. Run from any directory.
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

OUT = Path(__file__).resolve().parent
DATA = OUT.parent
sys.path.insert(0, str(DATA/'relacion_645_680_sin_blanco'))
from analizar_relacion import metrics, markdown_table


def load(group):
    name = 'calibracion_85_puntos (1).xlsx' if group=='85' else f'{group}Samples.xlsx'
    path = DATA/name
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    rows = list(wb.active.values)
    h = rows[0]
    records = [[row[0],num,row[h.index('Chl(a) [µg/mL]')],row[h.index('I(645)')]]
               for num,row in enumerate(rows[1:],2)
               if isinstance(row[h.index('Chl(a) [µg/mL]')],(int,float))
               and isinstance(row[h.index('I(645)')],(int,float))]
    wb.close()
    v = np.array(records,dtype=float)
    assert v.shape==(int(group),4) and np.isfinite(v).all() and (v[:,3]>0).all()
    return v,path,hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    loaded = {g:load(g) for g in ('11','9','85')}
    train = loaded['11'][0]
    X = np.c_[np.ones(len(train)),np.log(train[:,3])]
    a,b = np.linalg.lstsq(X,train[:,2],rcond=None)[0]
    # Check OLS coefficients independently using centered covariance.
    x = np.log(train[:,3]); yc = train[:,2]
    slope = np.sum((x-x.mean())*(yc-yc.mean()))/np.sum((x-x.mean())**2)
    assert np.allclose([a,b],[yc.mean()-slope*x.mean(),slope])
    results = {'equation':'C = a + b * ln(I645)','fit_group':'11','a':a,'b':b,'blank_used':False,'metrics':{},'source_sha256':{}}
    prediction_rows=[]
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    for group in ('9','85'):
        data = loaded[group][0]
        logi = np.log(data[:,3])
        prediction = a+b*logi
        m = metrics(data[:,2],prediction)
        results['metrics'][group] = m
        color = '#21966a' if group=='9' else '#2675b8'
        fig,axs=plt.subplots(1,2,figsize=(12,5.2),constrained_layout=True)
        xx=np.linspace(min(x.min(),logi.min()),max(x.max(),logi.max()),200)
        axs[0].plot(xx,a+b*xx,'--',color='#555555',lw=1.5,label='Same equation, extended beyond calibration')
        xf=np.linspace(x.min(),x.max(),100)
        axs[0].plot(xf,a+b*xf,color='#333333',lw=2,label='Equation fitted on 11 samples')
        axs[0].scatter(x,train[:,2],color='#d66c1d',s=34,alpha=.85,label='11 calibration samples',zorder=3)
        axs[0].scatter(logi,data[:,2],color=color,s=30,alpha=.8,label=f'{group} comparison samples',zorder=4)
        axs[0].set(xlabel='ln(I645)',ylabel='Reference chlorophyll a (µg/mL)',title='Reference points over the 645 nm relationship')
        low=min(0,data[:,2].min(),prediction.min());high=max(data[:,2].max(),prediction.max())*1.05
        axs[1].plot([low,high],[low,high],'--',color='#555555',lw=1.5,label='Ideal prediction')
        axs[1].scatter(data[:,2],prediction,color=color,s=35,alpha=.85)
        axs[1].set(xlabel='Reference chlorophyll a (µg/mL)',ylabel='Predicted chlorophyll a (µg/mL)',title=f'Apply unchanged to {group} samples',xlim=(low,high),ylim=(low,high))
        axs[1].text(.04,.96,f"Predictive R² = {m['r2']:.4f}\nRMSE = {m['rmse_ug_ml']:.3f} µg/mL\nBias = {m['bias_ug_ml']:+.3f} µg/mL",transform=axs[1].transAxes,ha='left',va='top',bbox={'facecolor':'white','edgecolor':'#dddddd','alpha':.9})
        if group=='9':
            for i in range(len(data)):
                axs[1].annotate(str(int(data[i,0])),(data[i,2],prediction[i]),xytext=(5,4),textcoords='offset points',fontsize=8,color=color)
        for ax in axs:ax.legend(fontsize=8,loc='lower right' if ax==axs[1] else 'best');ax.grid(alpha=.15)
        fig.suptitle(f'C = {a:.5f} {b:+.5f} × ln(I645) · calibrated on 11 · no blank',fontsize=13)
        fig.savefig(OUT/f'aplicada_{group}_muestras.png',dpi=180)
        plt.close(fig)
        for i,p in enumerate(prediction):
            prediction_rows.append({'dataset_n':int(group),'source':loaded[group][1].name,'sample':int(data[i,0]),'excel_row':int(data[i,1]),'I645':data[i,3],'reference_ug_ml':data[i,2],'predicted_ug_ml':p,'error_ug_ml':p-data[i,2]})
    with (OUT/'predicciones.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=list(prediction_rows[0]));writer.writeheader();writer.writerows(prediction_rows)
    for group,(_,path,digest) in loaded.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest()==digest
        results['source_sha256'][group]=digest
    results['calibration_fit']=metrics(train[:,2],X@np.array([a,b]))
    (OUT/'resultados.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    report=['# Relación con 645 nm, sin blanco','',f'C (µg/mL) = {a:.8f} {b:+.8f} × ln(I645).',
            'ln es el logaritmo natural. Los coeficientes se ajustan solo con las 11 muestras y se aplican sin cambios a las nueve y las 85. No se utiliza blanco ni I680. Las predicciones negativas se conservan para mostrar el comportamiento real de la ecuación.',
            '',markdown_table(['Grupo de comprobación','R² predictivo','RMSE (µg/mL)','MAE (µg/mL)','Sesgo (µg/mL)','Error máximo (µg/mL)'],
            [[g,f"{m['r2']:.5f}",f"{m['rmse_ug_ml']:.5f}",f"{m['mae_ug_ml']:.5f}",f"{m['bias_ug_ml']:+.5f}",f"{m['max_abs_error_ug_ml']:.5f}"] for g,m in results['metrics'].items()]),
            '', 'Cada figura muestra los puntos de referencia sobre la curva y la concentración predicha frente a la referencia. La diagonal representa predicción perfecta. La línea discontinua de la curva marca su extensión fuera del intervalo de I645 usado para calibrar.',
            'La calibración de 11 cubre 0,7944–3,07062 µg/mL. Las nueve cubren 0,0244–3,9098 y las 85 cubren 0,02384–7,98964. Hay extrapolación de la calibración en ambos grupos, especialmente a concentraciones altas del grupo de 85. El ajuste sobre las 11 no establece exactitud sobre esos otros rangos.',
            'La transferencia con I645 sola es peor que con el cociente de dos canales en las nueve muestras. El error calculado corresponde a todos los puntos completos, sin eliminar atípicos ni reajustar en las tandas de comparación. Los tres Excel originales se verifican con SHA-256 y permanecen intactos.']
    (OUT/'informe.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    print(json.dumps(results,indent=2))


if __name__=='__main__':main()
