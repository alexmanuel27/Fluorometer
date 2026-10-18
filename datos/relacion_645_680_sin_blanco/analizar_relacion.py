"""Two-channel calibration. No blank enters the data or the calculation.

Dependencies: numpy, openpyxl, matplotlib. Run this file to reproduce results.
The functional form was selected after inspecting both batches; the second
batch is therefore an exploratory transfer check, not a blind validation.
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

OUT = Path(__file__).resolve().parent
DATA = OUT.parent
MODELS = ('raw_pair', 'log_pair', 'ratio', 'log_ratio', 'ND',
          'log645_plus_680', '645_plus_log680', 'log645_baseline',
          'ratio_quadratic', 'log_ratio_quadratic', 'sqrt_ratio',
          'log_contrast', 'ratio_plus_logratio')
SELECTED = 'sqrt_ratio'


def load(group):
    path = DATA / f'{group}Samples.xlsx'
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    sheet = wb.active
    rows = list(sheet.values)
    headers = rows[0]
    items = []
    for rownum, row in enumerate(rows[1:], 2):
        if isinstance(row[1], (int, float)):
            items.append([row[0], rownum, row[1], row[headers.index('I(645)')], row[headers.index('I(680)')]])
    values = np.array(items, dtype=float)
    assert values.shape == (int(group), 5)
    assert np.isfinite(values).all() and (values[:, 3:] > 0).all()
    wb.close()
    return {'id': values[:, 0], 'row': values[:, 1], 'c': values[:, 2],
            'i645': values[:, 3], 'i680': values[:, 4],
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def design(data, model):
    a, b = data['i645'], data['i680']
    r, z = b / a, np.log(b / a)
    transforms = {
        'raw_pair': np.c_[a, b], 'log_pair': np.c_[np.log(a), np.log(b)],
        'ratio': r, 'log_ratio': z, 'ND': (b-a)/(b+a),
        'log645_plus_680': np.c_[np.log(a), b],
        '645_plus_log680': np.c_[a, np.log(b)], 'log645_baseline': np.log(a),
        'ratio_quadratic': np.c_[r, r*r], 'log_ratio_quadratic': np.c_[z, z*z],
        'sqrt_ratio': np.sqrt(r), 'log_contrast': np.log(b/(a+b)),
        'ratio_plus_logratio': np.c_[r, z],
    }
    return np.c_[np.ones(len(a)), transforms[model]]


def metrics(reference, prediction):
    error = prediction - reference
    return {'n': len(reference), 'r2': float(1-np.sum(error**2)/np.sum((reference-reference.mean())**2)),
            'rmse_ug_ml': float(np.sqrt(np.mean(error**2))),
            'mae_ug_ml': float(np.mean(abs(error))),
            'bias_ug_ml': float(np.mean(error)), 'max_abs_error_ug_ml': float(max(abs(error)))}


def save_csv(name, records):
    with (OUT/name).open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def markdown_table(headers, rows):
    return '| '+' | '.join(headers)+' |\n|'+'|'.join(['---']*len(headers))+'|\n'+''.join('| '+' | '.join(map(str, r))+' |\n' for r in rows)


def main():
    groups = {group: load(group) for group in ('11', '9')}
    comparison, coefficients = [], {}
    for group, train in groups.items():
        target = '9' if group == '11' else '11'
        test = groups[target]
        coefficients[group] = {}
        for model in MODELS:
            X, Xt = design(train, model), design(test, model)
            coef = np.linalg.lstsq(X, train['c'], rcond=None)[0]
            coefficients[group][model] = coef.tolist()
            loo = np.empty(len(X))
            for i in range(len(X)):
                keep = np.arange(len(X)) != i
                loo[i] = X[i] @ np.linalg.lstsq(X[keep], train['c'][keep], rcond=None)[0]
            for kind, y, p in [('calibration_fit', train['c'], X@coef),
                               ('within_batch_LOOCV', train['c'], loo),
                               ('transfer_check_exploratory', test['c'], Xt@coef)]:
                comparison.append({'model': model, 'train': group, 'test': target if kind.startswith('transfer') else group,
                                   'evaluation': kind, **metrics(y, p)})

    a, b = coefficients['11'][SELECTED]
    primary, reverse = [], []
    for train_group, records in [('11', primary), ('9', reverse)]:
        coef = np.array(coefficients[train_group][SELECTED])
        for group, data in groups.items():
            p = design(data, SELECTED)@coef
            for i in range(len(p)):
                records.append({'calibrated_on_n': int(train_group), 'dataset_n': int(group),
                                'role': 'calibration' if group == train_group else 'transfer_check',
                                'sample': int(data['id'][i]), 'excel_row': int(data['row'][i]),
                                'reference_ug_ml': data['c'][i], 'I645': data['i645'][i],
                                'I680': data['i680'][i], 'I680_over_I645': data['i680'][i]/data['i645'][i],
                                'predicted_ug_ml': p[i], 'error_ug_ml': p[i]-data['c'][i]})
    save_csv('predicciones_calibracion_11.csv', primary)
    save_csv('predicciones_calibracion_9.csv', reverse)
    save_csv('comparacion_modelos.csv', comparison)
    info = {'selected_model': SELECTED, 'primary_calibration': '11',
            'intercept': a, 'coefficient_sqrt_ratio': b,
            'equation': 'C_ug_ml = intercept + coefficient_sqrt_ratio * sqrt(I680 / I645)',
            'selection': 'Exploratory: both batches were inspected to compare functional forms. Coefficients use only the calibration batch.',
            'source_sha256': {g: d['sha256'] for g,d in groups.items()},
            'all_coefficients': coefficients, 'metrics': comparison}
    (OUT/'resultados.json').write_text(json.dumps(info, indent=2), encoding='utf-8')

    plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False})
    colors = {'11': '#d66c1d', '9': '#21966a'}
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), constrained_layout=True)
    qs = np.concatenate([np.sqrt(d['i680']/d['i645']) for d in groups.values()])
    q = np.linspace(qs.min(), qs.max(), 200)
    axes[0].plot(q, a+b*q, color='#303945', label='Calibration fitted on 11 only')
    for group, data in groups.items():
        pred = design(data, SELECTED) @ np.array([a,b])
        axes[0].scatter(np.sqrt(data['i680']/data['i645']), data['c'], color=colors[group], label=group+' samples')
        axes[1].scatter(data['c'], pred, color=colors[group], label=group+(' (calibration)' if group=='11' else ' (transfer check)'))
        axes[2].scatter(data['c'], pred-data['c'], color=colors[group], label=group+' samples')
        if group=='9':
            for i in range(len(pred)):
                axes[1].annotate(str(int(data['id'][i])), (data['c'][i], pred[i]), xytext=(5,4), textcoords='offset points', fontsize=8, color=colors[group])
    axes[0].set(xlabel='sqrt(I680 / I645)', ylabel='Reference chlorophyll a (µg/mL)', title='Two-channel relationship; no blank')
    axes[1].plot([0,4.3],[0,4.3],'--',color='#666666',linewidth=1)
    axes[1].set(xlabel='Reference chlorophyll a (µg/mL)', ylabel='Predicted chlorophyll a (µg/mL)', title='Apply the same equation to all nine dilutions')
    axes[2].axhline(0,color='#666666',linewidth=1)
    axes[2].set(xlabel='Reference chlorophyll a (µg/mL)', ylabel='Prediction − reference (µg/mL)', title='Error by concentration')
    for ax in axes:
        ax.grid(alpha=.15)
        ax.legend(fontsize=8)
    fig.suptitle(f'C = {a:.5f} + {b:.5f} × sqrt(I680 / I645)', fontsize=15)
    fig.savefig(OUT/'relacion_y_prediccion.png', dpi=180)
    plt.close(fig)

    chosen = [r for r in comparison if r['model']==SELECTED]
    contrast = [r for r in comparison if r['evaluation']=='transfer_check_exploratory']
    point_rows = [[r['sample'],f"{r['reference_ug_ml']:.4f}",f"{r['predicted_ug_ml']:.4f}",f"{r['error_ug_ml']:+.4f}"] for r in primary if r['dataset_n']==9]
    text = ['# Relación 645/680 sin blanco', '', 'Fecha: 18 de octubre de 2026.',
            '', '## Resultado',
            f'**C (µg/mL) = {a:.8f} + {b:.8f} × √(I680/I645).**',
            'Los dos coeficientes se ajustaron exclusivamente con las 11 muestras. Se aplica la misma ecuación a las nueve diluciones, sin recalibrar, cambiar la escala, restar fondo, usar blancos o limitar las predicciones a cero.',
            'Se adopta la raíz del cociente por su sencillez (dos coeficientes) y su transferencia razonable en ambos sentidos. La forma funcional se eligió después de explorar ambas tandas: la segunda tanda es una comprobación de transferencia exploratoria, no una validación ciega de una ecuación fijada previamente.',
            '', '## Errores y ajuste',
            markdown_table(['Calibración','Evaluación','n','R² predictivo/ajuste','RMSE (µg/mL)','MAE (µg/mL)','Sesgo (µg/mL)','Error máximo (µg/mL)'],
                           [[r['train'],r['evaluation'],r['n'],f"{r['r2']:.5f}",f"{r['rmse_ug_ml']:.5f}",f"{r['mae_ug_ml']:.5f}",f"{r['bias_ug_ml']:+.5f}",f"{r['max_abs_error_ug_ml']:.5f}"] for r in chosen]),
            'RMSE es la raíz del error cuadrático medio. MAE es el error absoluto medio. El sesgo usa predicción menos referencia. R² compara las predicciones con la identidad predicho=referencia, no es solo el cuadrado de una correlación.',
            '', '## Las nueve diluciones predichas con la ecuación de las 11',
            markdown_table(['ID','Referencia (µg/mL)','Predicción (µg/mL)','Error (µg/mL)'],point_rows),
            '', '## Comparación de relaciones exploradas',
            'Todas las opciones usan exclusivamente 645/680; ln(I645) se conserva como control de un solo canal. Cada ajuste usa únicamente la tanda indicada como calibración. Las columnas de comprobación no se usaron para ajustar coeficientes, pero sí se consultaron para escoger la forma funcional.',
            markdown_table(['Relación','Calibración','Comprobación','R²','RMSE (µg/mL)','Error máximo (µg/mL)'],
                           [[r['model'],r['train'],r['test'],f"{r['r2']:.5f}",f"{r['rmse_ug_ml']:.5f}",f"{r['max_abs_error_ug_ml']:.5f}"] for r in contrast]),
            'Definiciones: ratio=I680/I645; log_ratio=ln(ratio); ND=(I680−I645)/(I680+I645); sqrt_ratio=√ratio. Los modelos pair ajustan intercepto y ambos canales o sus logaritmos; quadratic agrega el cuadrado de la variable; ratio_plus_logratio combina ratio y ln(ratio); log_contrast=ln(I680/(I645+I680)).',
            '', '## Alcance',
            '- La calibración de 11 cubre 0,7944–3,07062 µg/mL. La comprobación de nueve cubre 0,0244–3,9098 µg/mL, con extrapolación a ambos extremos. No hay muestra cero medida.',
            '- El intervalo observado del cociente en ambas tandas es aproximadamente 0,051–0,408. No se establece validez fuera de él. Para usar la ecuación se requieren intensidades positivas, ganancia/integración y montaje comparables.',
            '- El cociente puede cancelar cambios que multipliquen ambos canales por el mismo factor. No corrige automáticamente fondos aditivos ni cambios diferentes entre canales. La raíz es una transformación empírica y no se presenta como ley física.',
            '- El error absoluto del modelo debe considerarse cerca de concentraciones bajas. Un R² alto no acredita precisión relativa alta cerca de cero ni establece un límite de detección.',
            '- Las nueve diluciones comparten un extracto madre. Una nueva sesión o un nuevo extracto permitirán comprobar la fórmula ya fijada sin volver a escogerla.',
            '- Los canales saturados 410/435 y sus datos no participan. Se reconoce que el sensor lleva filtros espectrales incorporados. El análisis no exige modificar la óptica ni medir blanco por muestra; no usa ningún blanco, ni siquiera el de sesión.',
            '- Las concentraciones se toman de los Excel como referencia suministrada. Los archivos no permiten auditar las absorbancias ni factores de dilución. El firmware no se ha modificado.',
            '', '## Archivos',
            'La figura muestra la relación y los errores de transferencia. Los CSV contienen las predicciones por muestra en ambos sentidos y la comparación completa. Los hashes SHA-256 de los originales y los coeficientes completos quedan en resultados.json.',
            '', 'Fuentes: 11Samples.xlsx y 9Samples.xlsx, Sheet1. B=concentración, U=I645, W=I680.']
    (OUT/'informe.md').write_text('\n'.join(text)+'\n',encoding='utf-8')

    # Verify fitting and scalar evaluation independently on synthetic and real data.
    toy={'i645':np.array([100.,200.,300.,400.]),'i680':np.array([1.,8.,27.,64.])}
    X=design(toy,SELECTED)
    recovered=np.linalg.lstsq(X,X@np.array([-2.,10.]),rcond=None)[0]
    assert np.allclose(recovered,[-2.,10.])
    for group, data in groups.items():
        assert hashlib.sha256((DATA/f'{group}Samples.xlsx').read_bytes()).hexdigest()==data['sha256']
        assert np.allclose(design(data,SELECTED)@np.array([a,b]),a+b*np.sqrt(data['i680']/data['i645']))
    print(json.dumps({'equation':info['equation'],'a':a,'b':b,'selected_metrics':chosen,'nine_predictions':[r for r in primary if r['dataset_n']==9]},indent=2))


if __name__ == '__main__':
    main()
