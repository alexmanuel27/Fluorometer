"""All 9 disjoint train/test combinations of 85, 9, 11; fixed ln(B645/I645) form."""
from itertools import combinations
from pathlib import Path
import csv
import hashlib
import json
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
DATA = OUT.parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(DATA/'transferencia_9_11_ln645_blanco'))
from analisis import score
from analisis_blanco import feature, BLANKS
from analisis_85 import load, fit, errors, BINS, LABELS, markdown_table

GROUPS = ('85', '9', '11')
TRAINING_SETS = [c for n in (1, 2) for c in combinations(GROUPS, n)]


def write_csv(name, rows):
    with (OUT/name).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    loaded = {g: load(g) for g in GROUPS}
    models = {}
    for groups in TRAINING_SETS:
        key = '+'.join(groups)
        x = np.concatenate([feature(loaded[g][0][:, 3], BLANKS[g]) for g in groups])
        y = np.concatenate([loaded[g][0][:, 2] for g in groups])
        a, b = map(float, fit(x, y))
        slope = np.sum((x-x.mean())*(y-y.mean()))/np.sum((x-x.mean())**2)
        assert np.allclose([a, b], [y.mean()-slope*x.mean(), slope], atol=1e-10)
        assert np.allclose([np.sum(a+b*x-y), np.dot(x, a+b*x-y)], 0, atol=1e-9)
        models[key] = {'train_datasets': list(groups), 'fit_n': len(y), 'intercept': a, 'slope': b,
                       'equation': 'C_ug_ml = intercept + slope * ln(B645_session/I645)',
                       'method': 'OLS with intercept; equal weight per sample, not per dataset',
                       'training_feature_range': [float(x.min()), float(x.max())],
                       'training_concentration_range_ug_ml': [float(y.min()), float(y.max())],
                       'sources': {g: {'path': str(loaded[g][1]), 'sha256': loaded[g][2]} for g in groups},
                       'training_fit_not_cv': score(y, a+b*x)}
    assert len(models) == 6
    frozen = {'session_blanks_I645': BLANKS, 'models': models,
              'blank_source': 'Fixed session means supplied by Alex, not fitted',
              'form_selection': 'Same linear ln(B/I) form for every combination; no selection of extra terms'}
    model_path = OUT/'modelos_fijados.json'
    model_path.write_text(json.dumps(frozen, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    snapshot = model_path.read_bytes()

    metrics, predictions, ranges, low_high = [], [], [], []
    plot_data = {}
    for test in GROUPS:
        data = loaded[test][0]
        y = data[:, 2]
        x = feature(data[:, 3], BLANKS[test])
        for key, model in models.items():
            if test in model['train_datasets']:
                continue
            assert set(model['train_datasets']).isdisjoint({test})
            p = model['intercept']+model['slope']*x
            lo, hi = model['training_feature_range']
            inside = (x >= lo) & (x <= hi)
            identity = {'train_datasets': key, 'test_dataset': test}
            low = errors(y[y < 1], p[y < 1])
            m = {**identity, 'train_n': model['fit_n'], **score(y, p),
                 'outside_training_feature_range_n': int((~inside).sum()),
                 'below_1_n': low['n'], 'below_1_rmse_ug_ml': low['rmse_ug_ml'],
                 'below_1_mae_ug_ml': low['mae_ug_ml'], 'below_1_mape_percent': low['mape_percent']}
            metrics.append(m)
            plot_data[(key, test)] = (p, inside)
            coverage = np.zeros(len(y), dtype=int)
            for j, (left, right, label) in enumerate(zip(BINS[:-1], BINS[1:], LABELS)):
                mask = (y >= left) & ((y <= right) if j == len(LABELS)-1 else (y < right))
                coverage += mask
                ranges.append({**identity, 'range_ug_ml': label, 'lower_ug_ml': left, 'upper_ug_ml': right,
                               'upper_inclusive': j == len(LABELS)-1, **errors(y[mask], p[mask])})
            assert np.all(coverage == 1)
            rr = [r for r in ranges if r['train_datasets'] == key and r['test_dataset'] == test and r['n']]
            assert np.isclose(sum(r['n']*r['mae_ug_ml'] for r in rr)/len(y), m['mae_ug_ml'])
            assert np.isclose(sum(r['n']*r['rmse_ug_ml']**2 for r in rr)/len(y), m['rmse_ug_ml']**2)
            for label, mask in [('<1', y < 1), ('>=1', y >= 1)]:
                low_high.append({**identity, 'range_ug_ml': label, **errors(y[mask], p[mask])})
            for i, row in enumerate(data):
                predictions.append({**identity, 'source': loaded[test][1].name, 'sample': int(row[0]),
                                    'excel_row': int(row[1]), 'reference_ug_ml': row[2], 'I645': row[3],
                                    'B645_session': BLANKS[test], 'ln_B645_over_I645': float(x[i]),
                                    'prediction_ug_ml': float(p[i]), 'error_ug_ml': float(p[i]-y[i]),
                                    'absolute_relative_error_percent': float(abs(p[i]-y[i])/y[i]*100),
                                    'inside_training_feature_range': bool(inside[i])})
    assert model_path.read_bytes() == snapshot
    assert len(metrics) == 9 and len(predictions) == 315 and len(ranges) == 72 and len(low_high) == 18
    selection = {}
    for test in GROUPS:
        evaluated = sorted([r for r in metrics if r['test_dataset'] == test], key=lambda r: r['rmse_ug_ml'])
        assert len(evaluated) == 3
        for rank, r in enumerate(evaluated, 1):
            r['rank_rmse_same_test'] = rank
        selection[test] = {'lowest_rmse': evaluated[0]['train_datasets'],
                           'lowest_mape': min(evaluated, key=lambda r: r['mape_percent'])['train_datasets'],
                           'lowest_mae_below_1': min(evaluated, key=lambda r: r['below_1_mae_ug_ml'])['train_datasets'],
                           'lowest_mape_below_1': min(evaluated, key=lambda r: r['below_1_mape_percent'])['train_datasets']}
    metrics.sort(key=lambda r: (GROUPS.index(r['test_dataset']), r['rank_rmse_same_test']))
    for _, path, digest in loaded.values():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
    write_csv('comparacion_nueve_combinaciones.csv', metrics)
    write_csv('predicciones_prueba.csv', predictions)
    write_csv('errores_por_rango.csv', ranges)
    write_csv('errores_menor_y_mayor_1.csv', low_high)
    result = {'frozen_models': frozen, 'test_metrics': metrics, 'selection_within_each_test': selection,
              'ranges': ranges, 'below_above_1': low_high, 'source_sha256': {g: d[2] for g, d in loaded.items()},
              'selection_scope': 'Exploratory minimum RMSE within the same test dataset, not a global validated winner'}
    (OUT/'resultados.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(3, 2, figsize=(11, 10), constrained_layout=True)
    for row, test in enumerate(GROUPS):
        evaluated = [r for r in metrics if r['test_dataset'] == test]
        for col, (metric, unit) in enumerate([('rmse_ug_ml', 'RMSE (µg/mL)'), ('mape_percent', 'MAPE (%)')]):
            ax = axes[row, col]
            values = [r[metric] for r in evaluated]
            lowest = min(values)
            bars = ax.bar([r['train_datasets'] for r in evaluated], values,
                          color=['#21966a' if v == lowest else '#2675b8' for v in values])
            for bar, v in zip(bars, values):
                ax.annotate(f'{v:.3f}' if col == 0 else f'{v:.2f}%',
                            (bar.get_x()+bar.get_width()/2, v), xytext=(0, 4), textcoords='offset points', ha='center')
            ax.set(title=f'Prueba en {test} muestras', ylabel=unit, xlabel='Conjuntos utilizados para entrenar')
            ax.margins(y=.22)
            ax.set_axisbelow(True)
            ax.grid(axis='y', alpha=.15)
    fig.suptitle('Comparar dentro de cada fila · verde = menor error de ese panel · ln(B645/I645)', fontsize=12)
    fig.savefig(OUT/'01_comparacion_errores.png', dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(3, 3, figsize=(13, 13), constrained_layout=True)
    for row, test in enumerate(GROUPS):
        y = loaded[test][0][:, 2]
        evaluated = [r for r in metrics if r['test_dataset'] == test]
        all_p = np.concatenate([plot_data[(r['train_datasets'], test)][0] for r in evaluated])
        limits = (min(-.1, float(all_p.min())-.15), max(float(y.max()), float(all_p.max()))+.25)
        for ax, m in zip(axes[row], evaluated):
            p, inside = plot_data[(m['train_datasets'], test)]
            ax.plot(limits, limits, '--', color='#777777')
            for mask, marker, color in [(inside, 'o', '#2675b8'), (~inside, '^', '#d66c1d')]:
                ax.scatter(y[mask], p[mask], marker=marker, color=color, s=25, alpha=.8)
            ax.set(xlim=limits, ylim=limits, xlabel='Referencia (µg/mL)', ylabel='Predicción (µg/mL)',
                   title=f"Entrenar {m['train_datasets']} → probar {test}")
            ax.set_aspect('equal', adjustable='box')
            ax.text(.04, .96, f"RMSE {m['rmse_ug_ml']:.3f}\nMAPE {m['mape_percent']:.1f}%\nR² {m['r2_predictive']:.4f}",
                    transform=ax.transAxes, va='top', fontsize=9, bbox={'facecolor': 'white', 'edgecolor': '#dddddd'})
            ax.grid(alpha=.15)
    fig.suptitle('Predicciones en conjuntos excluidos del ajuste · cada fila comparte las mismas referencias\nColumnas ordenadas por RMSE dentro de la fila · triángulo naranja = extrapolación de señal', fontsize=12)
    fig.savefig(OUT/'02_nueve_pruebas.png', dpi=160)
    plt.close(fig)

    headers = ['Entrenar', 'Probar', 'n prueba', 'R² predictivo', 'RMSE', 'MAE', 'Sesgo', 'MAPE (%)', 'MAPE <1 (%)']
    table = markdown_table(headers, [[r['train_datasets'], r['test_dataset'], r['n'], f"{r['r2_predictive']:.5f}"]+
                          [f"{r[k]:.5f}" for k in ('rmse_ug_ml', 'mae_ug_ml', 'bias_ug_ml')]+
                          [f"{r['mape_percent']:.2f}", f"{r['below_1_mape_percent']:.2f}"] for r in metrics])
    report = ['# Todas las combinaciones de entrenamiento y prueba: ln645 con blanco', '',
              'Fecha: 18 de octubre de 2026.', '', '## Diseño y criterio',
              'Se ajustan seis ecuaciones: entrenar con 85, 9, 11, 85+9, 85+11 o 9+11. Cada ecuación se prueba en todos los conjuntos individuales que no participaron en su ajuste: seis pruebas con entrenamiento simple y tres con entrenamiento doble, nueve en total. No se mezclan muestras de prueba dentro de una evaluación.',
              'Se mantiene C = a + b × ln(B645/I645), con intercepto libre y mínimos cuadrados ordinarios. Igual peso por muestra, no por tanda. Los blancos fijos proporcionados por Alex son 1356, 1214 y 1256 para 85, 9 y 11, respectivamente. Se emplean al entrenar y al predecir, sin optimizarlos ni añadir blancos como puntos de concentración cero.',
              'Cada entrenamiento usa solo las concentraciones de sus grupos. Se guardan las seis ecuaciones antes de calcular los errores de transferencia en este análisis. No se eliminan atípicos, no se recortan negativos ni se pondera por las desviaciones del sensor.',
              'Criterio principal: menor RMSE entre las tres alternativas evaluadas sobre exactamente el mismo conjunto de prueba. Se muestran también MAE, sesgo, MAPE y error bajo 1 µg/mL. No se elige ganador por el mayor R² entre pruebas con rangos distintos.', '',
              '## Las nueve combinaciones', table,
              'RMSE, MAE y sesgo en µg/mL. MAPE = promedio del error relativo absoluto. Las filas se ordenan por RMSE dentro de cada conjunto de prueba. n de la evaluación <1: 30 para prueba 85, 7 para prueba 9 y 3 para prueba 11.', '',
              '## Mejores resultados observados para cada prueba']
    for test in GROUPS:
        r = next(r for r in metrics if r['test_dataset'] == test and r['rank_rmse_same_test'] == 1)
        report += [f"- Prueba {test}: entrenar con **{r['train_datasets']}**, RMSE {r['rmse_ug_ml']:.5f} µg/mL; MAE {r['mae_ug_ml']:.5f}; MAPE {r['mape_percent']:.2f}%; MAPE <1 {r['below_1_mape_percent']:.2f}%."]
    report += ['', 'No hay un ganador universal demostrado: los conjuntos de prueba tienen distinto rango, protocolo y número de muestras. El menor RMSE de las nueve filas se observa con 85 → 9 (0,09241 µg/mL), pero no permite afirmar ese rendimiento en las once, donde la misma calibración da 0,32363 µg/mL.',
               'Para prueba 85, entrenar con nueve minimiza RMSE y MAE; entrenar con 9+11 minimiza MAPE, incluido el rango <1. Por tanto, el criterio elegido cambia la selección. Las otras dos pruebas favorecen entrenar solo con 85 para ambas métricas.',
               'Añadir las nueve a las 85 no mejora la prueba sobre las once; añadir las once a las 85 no mejora la prueba sobre las nueve. La diferencia de RMSE entre 85 → 11 y 85+9 → 11 es pequeña: este orden numérico no demuestra una diferencia estadísticamente significativa.', '',
               '## Ecuaciones completas de entrenamiento',
               'ln es el logaritmo natural. B645 es el blanco de la sesión de la muestra que se evalúa e I645 su intensidad media. Ambos deben ser positivos y finitos, en las mismas unidades y configuración.']
    for key, model in models.items():
        report += [f"- Entrenar {key}, n={model['fit_n']}: C (µg/mL) = {model['intercept']:.10f} + {model['slope']:.10f} × ln(B645/I645)."]
    report += ['', '## Gráficas', '![Comparación de RMSE y MAPE](01_comparacion_errores.png)',
               '![Las nueve pruebas](02_nueve_pruebas.png)', '', '## Alcance de la selección',
               'Al buscar la mejor combinación mirando todos los resultados, los tres conjuntos pasan a formar parte de la exploración. Los errores del ganador observado no son una estimación independiente de su selección. No se debe descartar la tanda de once solo porque dé peor resultado ni ocultar las pruebas desfavorables al publicar.',
               'La tanda de nueve son diluciones de un solo extracto, no nueve extractos independientes. Las 85 cubren 0,02384–7,98964 µg/mL; las nueve 0,0244–3,9098; las once 0,7944–3,07062. La extrapolación se identifica además según el intervalo de ln(B/I) entrenado y se conserva en los CSV.',
               'El MAPE puede crecer mucho cerca de cero y no es incertidumbre ni error máximo garantizado. Este análisis no calcula LOD/LOQ, rendimiento en lagos ni incertidumbre de los blancos. No se han modificado el firmware ni los .bin.', '',
               '## Fuentes y resultados detallados',
               'Fuentes originales: calibracion_85_puntos (1).xlsx, Sheet1 A1:D86; 9Samples.xlsx, Sheet1 A1:AL10; 11Samples.xlsx, Sheet1 A1:AL12. Se usan identificador, concentración e I645. Las filas con solo identificadores del primer libro no son mediciones. Los tres originales se verifican por SHA-256 y permanecen intactos.',
               'modelos_fijados.json contiene las seis ecuaciones y las métricas de ajuste sobre su propio entrenamiento, claramente separadas de las pruebas y sin denominarlas CV. comparacion_nueve_combinaciones.csv contiene las nueve evaluaciones; predicciones_prueba.csv contiene 315 predicciones fuera del ajuste correspondiente, tres por muestra. No son 315 muestras independientes.',
               'errores_por_rango.csv conserva 72 intervalos, incluidos los vacíos; errores_menor_y_mayor_1.csv resume 18 evaluaciones. resultados.json contiene todo lo anterior y la selección por RMSE, MAPE y métricas bajas, dentro de cada prueba.',
               'Los análisis previos se conservan. Se reutilizan funciones verificadas de lectura, normalización y métricas. Se comprueban exclusión entre entrenamiento y prueba, cobertura de las nueve combinaciones, ajustes por covarianza y ecuaciones normales, recuentos, rangos y conservación de ecuaciones y fuentes.']
    (OUT/'informe.md').write_text('\n'.join(report)+'\n', encoding='utf-8')
    print(json.dumps({'test_metrics': metrics, 'selection_within_each_test': selection, 'checks': 'passed'}, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
