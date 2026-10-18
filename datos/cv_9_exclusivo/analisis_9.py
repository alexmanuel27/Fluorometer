"""CV on 9Samples.xlsx only: reuse fixed model definitions, never other data."""
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
INPUT = OUT.parent / '9Samples.xlsx'
sys.path.insert(0, str(OUT.parent / 'cv_11_exclusivo'))
# These functions do not load data or previous model coefficients.
from analisis_11 import WAVELENGTHS, catalogue, fit_predict, table


def read_input():
    book = openpyxl.load_workbook(INPUT, data_only=True, read_only=True)
    sheet = book['Sheet1']
    source = list(sheet.values)
    book.close()
    headers = source[0]
    rows = [(num, row) for num, row in enumerate(source[1:], 2)
            if isinstance(row[1], (float, int))]
    assert len(rows) == 9
    g = {'y': np.array([r[1] for _, r in rows], dtype=float),
         'id': np.array([r[0] for _, r in rows], dtype=int),
         'row': np.array([num for num, _ in rows], dtype=int)}
    assert len(set(g['id'])) == 9 and np.isfinite(g['y']).all() and (g['y'] > 0).all()
    for nm in WAVELENGTHS:
        g[nm] = np.array([r[headers.index(f'I({nm})')] for _, r in rows], dtype=float)
        assert np.isfinite(g[nm]).all() and (g[nm] > 0).all()
    for nm in (410, 435):
        assert all(r[headers.index(f'I({nm})')] == 2**32 for _, r in rows)
    return g


def scores(y, p):
    e = p - y
    low = y < 1
    return {'r2_cv9': float(1 - np.sum(e**2) / np.sum((y-y.mean())**2)),
            'rmse_cv9_ug_ml': float(np.sqrt(np.mean(e**2))),
            'mae_cv9_ug_ml': float(np.mean(abs(e))), 'bias_cv9_ug_ml': float(e.mean()),
            'max_error_cv9_ug_ml': float(max(abs(e))),
            'low_n': int(low.sum()),
            'low_mape_cv9_percent': float(np.mean(abs(e[low]) / y[low]) * 100),
            'low_mae_cv9_ug_ml': float(np.mean(abs(e[low]))),
            'low_rmse_cv9_ug_ml': float(np.sqrt(np.mean(e[low]**2))),
            'negative_predictions_n': int((p < 0).sum())}


def write_csv(name, rows):
    with (OUT/name).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    digest = hashlib.sha256(INPUT.read_bytes()).hexdigest()
    g = read_input()
    y, n = g['y'], len(g['y'])
    low = y < 1
    # Constant-blank transformations duplicate these models; no blank is used.
    models = [m for m in catalogue(g) if not m['blank']]
    assert len(models) == 55 and low.sum() == 7
    results, predictions, exported, folds = [], {}, [], []
    for m in models:
        p = np.full(n, np.nan)
        seen = np.zeros(n, dtype=int)
        for i in range(n):
            keep = np.arange(n) != i
            assert keep.sum() == 8 and not keep[i]
            p[i] = fit_predict(m, m['x'][keep], y[keep], m['x'][i:i+1])[0]
            seen[i] += 1
            folds.append({'model': m['id'], 'held_out_sample': int(g['id'][i]),
                          'training_samples': g['id'][keep].tolist()})
        assert np.all(seen == 1) and np.isfinite(p).all()
        result = {'model': m['id'], 'label': m['label'], 'method': m['kind'],
                  'n_samples': n, 'n_folds': n, 'training_samples_per_fold': 8, **scores(y, p)}
        results.append(result)
        predictions[m['id']] = p
        for i in range(n):
            exported.append({'model': m['id'], 'sample': int(g['id'][i]), 'excel_row': int(g['row'][i]),
                             'reference_ug_ml': y[i], 'cv_prediction_ug_ml': p[i],
                             'cv_error_ug_ml': p[i]-y[i],
                             'absolute_relative_error_percent': abs(p[i]-y[i])/y[i]*100,
                             'reference_below_1_ug_ml': bool(low[i])})
    ranked = sorted(results, key=lambda r: (r['rmse_cv9_ug_ml'], r['model']))
    ranked_low = sorted(results, key=lambda r: (r['low_mape_cv9_percent'], r['model']))
    byid = {r['model']: r for r in results}
    write_csv('comparacion_cv_9.csv', ranked)
    write_csv('predicciones_cv_9.csv', exported)
    metadata = {'input_file': str(INPUT), 'input_sha256': digest, 'model_count': len(models),
                'validation': 'LOOCV: train on 8, predict the held-out 1, repeat 9 times',
                'blank_used': False, 'saturated_channels_excluded': [410, 435],
                'source_concentrations_ug_ml': y.tolist(), 'n_below_1': int(low.sum()),
                'models_ranked_by_global_rmse': ranked,
                'models_ranked_by_low_mape': [r['model'] for r in ranked_low], 'folds': folds}
    (OUT/'resultados_9.json').write_text(json.dumps(metadata, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})

    def panels(ids, name, low_only=False, title_override=None):
        columns = 3 if len(ids) == 6 else 2
        rows = (len(ids)+columns-1)//columns
        fig, axes = plt.subplots(rows, columns, figsize=(4.3*columns, 4.35*rows),
                                 constrained_layout=True, squeeze=False)
        mask = low if low_only else np.ones(n, dtype=bool)
        limit_low = min(-.05 if low_only else -.15, min(float(predictions[k][mask].min()) for k in ids)-.04)
        limit_high = max(1.05 if low_only else 4.15, max(float(predictions[k][mask].max()) for k in ids)+.08)
        for ax, key in zip(axes.flat, ids):
            p = predictions[key]
            r = byid[key]
            ax.plot([limit_low, limit_high], [limit_low, limit_high], '--', color='#777777', lw=1)
            ax.scatter(y[mask], p[mask], s=38, color='#2675b8')
            for i in np.flatnonzero(mask):
                ax.annotate(str(g['id'][i]), (y[i], p[i]), xytext=(4, 3),
                            textcoords='offset points', fontsize=8, color='#35566d')
            ax.set(xlabel='Chl(a) de referencia (µg/mL)', ylabel='Chl(a) predicha por CV (µg/mL)',
                   title=r['label'], xlim=(limit_low, limit_high), ylim=(limit_low, limit_high))
            ax.set_aspect('equal', adjustable='box')
            note = (f"Error relativo medio <1 = {r['low_mape_cv9_percent']:.1f}%\nMAE <1 = {r['low_mae_cv9_ug_ml']:.4f} µg/mL"
                    if low_only else f"R² CV9 = {r['r2_cv9']:.4f}\nRMSE CV9 = {r['rmse_cv9_ug_ml']:.4f} µg/mL")
            ax.text(.035, .97, note, transform=ax.transAxes, va='top', fontsize=9,
                    bbox={'facecolor': 'white', 'edgecolor': '#dddddd', 'alpha': .95})
            ax.grid(alpha=.15)
        for ax in list(axes.flat)[len(ids):]:
            ax.set_visible(False)
        title = ('Menor error relativo en las 7 concentraciones inferiores a 1 µg/mL\n'
                 'Mismas predicciones de CV9, sin recalibrar el subconjunto'
                 if low_only else 'Menor RMSE de CV en las 9 muestras\nCada punto predicho usando solo las otras 8')
        fig.suptitle(title_override or title, fontsize=14)
        fig.savefig(OUT/name, dpi=170)
        plt.close(fig)

    panels([r['model'] for r in ranked[:6]], '01_mejores_rmse_cv_9.png')
    panels([r['model'] for r in ranked_low[:6]], '02_bajas_concentraciones_cv_9.png', low_only=True)
    controls = ['log_645', 'quadratic_log_645', 'sqrt_680_645', 'sqrt_680_705']
    panels(controls, '03_modelos_comparables_cv_9.png',
           title_override='Comparación de formas conocidas, calibradas solo con las 9\nCada punto predicho usando solo las otras 8')
    headers = ['Modelo', 'R² CV9', 'RMSE CV9 (µg/mL)', 'MAE CV9 (µg/mL)',
               'Error relativo medio <1 (%)', 'MAE <1 (µg/mL)', 'Error máximo CV9 (µg/mL)']
    def rows(rr):
        return [[r['label'], f"{r['r2_cv9']:.6f}", f"{r['rmse_cv9_ug_ml']:.6f}",
                 f"{r['mae_cv9_ug_ml']:.6f}", f"{r['low_mape_cv9_percent']:.2f}",
                 f"{r['low_mae_cv9_ug_ml']:.6f}", f"{r['max_error_cv9_ug_ml']:.6f}"] for r in rr]
    report = ['# Validación cruzada exclusivamente sobre las nueve muestras', '',
              'Único Excel utilizado: 9Samples.xlsx, Sheet1, A1:AL10. No se leen los conjuntos de once ni de 85 ni sus resultados o coeficientes. Se reutilizan únicamente las definiciones matemáticas de los modelos y las funciones de ajuste.', '',
              '## Método',
              'Se comparan 55 candidatos sin blanco: lineal y logarítmico por cada canal válido, cocientes y sus transformaciones, diferencias normalizadas, modelos de dos predictores y PLS de 1–3 componentes con los 16 canales no saturados.',
              'Cada modelo se entrena con ocho muestras y predice la omitida. Se repite nueve veces. Todas las métricas y puntos de las figuras usan esas nueve predicciones fuera del entrenamiento. PLS aprende centrado y escalado únicamente con las ocho muestras de cada turno.',
              'R² CV9 = 1 − Σ(predicción − referencia)² / Σ(referencia − media de referencia)². No es R² de entrenamiento ni correlación al cuadrado. RMSE y MAE están en µg/mL.',
              'Error relativo absoluto medio <1 = promedio de |predicción − referencia| / referencia × 100 en las siete referencias menores de 1 µg/mL. Ese subconjunto solo se usa para evaluar las mismas predicciones de CV9, no para recalibrar.',
              'No se eliminan muestras, no se recortan predicciones negativas, no se fuerzan interceptos y no se usan desviaciones instrumentales como pesos. Los canales 410 y 435 se excluyen por saturación. Las variantes con blanco constante que solo cambian escala o intercepto no se duplican.', '',
              '## Menor RMSE global', table(headers, rows(ranked[:10])), '',
              '## Menor error relativo en concentraciones inferiores a 1 µg/mL', table(headers, rows(ranked_low[:10])), '',
              '## Formas comparables con los modelos anteriores, ahora calibradas solo con ocho por turno', table(headers, rows([byid[k] for k in controls])), '',
              '## Predicciones de validación de los tres primeros por RMSE global',
              table(['ID', 'Referencia (µg/mL)']+[r['label'] for r in ranked[:3]],
                    [[int(g['id'][i]), f'{y[i]:.5f}']+[f"{predictions[r['model']][i]:.5f}" for r in ranked[:3]] for i in range(n)]), '',
              '## Alcance de la comparación',
              'Rango de referencia: 0,0244–3,9098 µg/mL. Hay siete muestras por debajo de 1 µg/mL. Las nueve son diluciones de un mismo extracto madre, no nueve extractos independientes. La CV evalúa puntos de esta misma serie y no demuestra exactitud entre extractos, sesiones o protocolos.',
              'Al omitir el extremo superior, se entrena hasta 1,9549 y se predice 3,9098 µg/mL: ese turno requiere extrapolación. Esto se mantiene para todos los candidatos, sin excluirlo de las métricas.',
              'Comparar muchos candidatos con solo nueve puntos puede favorecer por azar al mínimo. Las métricas son CV por candidato, no una validación anidada del proceso de selección ni una validación externa de un ganador. No se atribuye superioridad definitiva al primero. Los porcentajes relativos son sensibles a las referencias cercanas a cero.', '',
              '## Comparación completa', table(headers, rows(ranked)), '',
              '## Resultados',
              '01_mejores_rmse_cv_9.png compara los seis menores RMSE globales. 02_bajas_concentraciones_cv_9.png muestra los seis menores errores relativos por debajo de 1. 03_modelos_comparables_cv_9.png muestra cuatro formas conocidas, reentrenadas exclusivamente con estas muestras.',
              'comparacion_cv_9.csv contiene las 55 comparaciones. predicciones_cv_9.csv contiene las 495 predicciones de validación con sus referencias y errores. resultados_9.json documenta todos los turnos y la procedencia.',
              f'SHA-256 de la entrada: {digest}. El Excel original permanece intacto.']
    (OUT/'informe.md').write_text('\n'.join(report)+'\n', encoding='utf-8')

    # Independently verify all nine univariate logarithmic fits by covariance.
    for i in range(n):
        keep = np.arange(n) != i
        x, yy = np.log(g[645][keep]), y[keep]
        b = np.sum((x-x.mean())*(yy-yy.mean()))/np.sum((x-x.mean())**2)
        direct = yy.mean()+b*(np.log(g[645][i])-x.mean())
        assert np.isclose(direct, predictions['log_645'][i], atol=1e-10)
    assert len(exported) == 55*9
    assert hashlib.sha256(INPUT.read_bytes()).hexdigest() == digest
    print(json.dumps({'n': n, 'n_below_1': int(low.sum()), 'model_count': len(models),
                      'top_rmse': ranked[:8], 'top_low_mape': ranked_low[:6],
                      'controls': [byid[k] for k in controls], 'checks': 'passed'}, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
