"""Independent ln(B645/I645) fits: train 9/test 11 and train 11/test 9; no 85 data."""
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
sys.path.insert(0, str(DATA/'cv_85_ln645_blanco'))
# These imported functions do not open any workbook or run previous analyses.
from analisis_blanco import feature
from analisis_85 import load, fit, errors, BINS, LABELS, markdown_table

BLANKS = {'9': 1214.0, '11': 1256.0}
DIRECTIONS = [('9', '11'), ('11', '9')]


def write_csv(name, rows):
    with (OUT/name).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def score(y, p):
    return {**errors(y, p), 'r2_predictive': float(1-np.sum((p-y)**2)/np.sum((y-y.mean())**2))}


def main():
    loaded = {g: load(g) for g in ('9', '11')}
    assert set(loaded) == {'9', '11'}
    models = {}
    for train, test in DIRECTIONS:
        d, path, digest = loaded[train]
        x, y = feature(d[:, 3], BLANKS[train]), d[:, 2]
        a, b = map(float, fit(x, y))
        slope = np.sum((x-x.mean())*(y-y.mean()))/np.sum((x-x.mean())**2)
        assert np.allclose([a, b], [y.mean()-slope*x.mean(), slope], atol=1e-10)
        assert np.allclose([np.sum(a+b*x-y), np.dot(x, a+b*x-y)], 0, atol=1e-9)
        model = {'equation': 'C_ug_ml = intercept + slope * ln(B645_session/I645)',
                 'intercept': a, 'slope': b, 'train_dataset': train, 'test_dataset': test,
                 'fit_n': len(d), 'fit_method': 'OLS with intercept; equal weight per sample',
                 'session_blanks_I645': BLANKS, 'training_source': str(path), 'training_sha256': digest,
                 'training_feature_range': [float(x.min()), float(x.max())],
                 'training_concentration_range_ug_ml': [float(y.min()), float(y.max())],
                 'test_used_for_fitting_or_model_selection': False, 'dataset_85_used': False}
        models[train] = model
        (OUT/f'modelo_entrenado_{train}.json').write_text(json.dumps(model, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    # Freeze both equations before evaluating either transfer direction.
    snapshot = json.dumps(models, sort_keys=True)
    metrics, points, ranges, low_high, test_predictions = [], [], [], [], {}
    for train, test in DIRECTIONS:
        model = models[train]
        a, b = model['intercept'], model['slope']
        for role, group in [('calibration', train), ('test', test)]:
            d = loaded[group][0]
            x, y = feature(d[:, 3], BLANKS[group]), d[:, 2]
            p = a+b*x
            lo, hi = model['training_feature_range']
            inside = (x >= lo) & (x <= hi)
            metrics.append({'train_dataset': train, 'evaluated_dataset': group, 'role': role,
                            **score(y, p), 'outside_training_feature_range_n': int((~inside).sum())})
            for i, row in enumerate(d):
                points.append({'train_dataset': train, 'evaluated_dataset': group, 'role': role,
                               'source': loaded[group][1].name, 'sample': int(row[0]), 'excel_row': int(row[1]),
                               'reference_ug_ml': row[2], 'I645': row[3], 'B645_session': BLANKS[group],
                               'ln_B645_over_I645': float(x[i]), 'prediction_ug_ml': float(p[i]),
                               'error_ug_ml': float(p[i]-y[i]),
                               'absolute_relative_error_percent': float(abs(p[i]-y[i])/y[i]*100),
                               'inside_training_feature_range': bool(inside[i])})
            if role != 'test':
                continue
            test_predictions[train] = (p, inside)
            coverage = np.zeros(len(y), dtype=int)
            identity = {'train_dataset': train, 'test_dataset': test}
            for j, (left, right, label) in enumerate(zip(BINS[:-1], BINS[1:], LABELS)):
                mask = (y >= left) & ((y <= right) if j == len(LABELS)-1 else (y < right))
                coverage += mask
                ranges.append({**identity, 'range_ug_ml': label, 'lower_ug_ml': left, 'upper_ug_ml': right,
                               'upper_inclusive': j == len(LABELS)-1, **errors(y[mask], p[mask])})
            assert np.all(coverage == 1)
            rr = [r for r in ranges if r['train_dataset'] == train and r['n']]
            assert np.isclose(sum(r['n']*r['mae_ug_ml'] for r in rr)/len(y), score(y, p)['mae_ug_ml'])
            assert np.isclose(sum(r['n']*r['rmse_ug_ml']**2 for r in rr)/len(y), score(y, p)['rmse_ug_ml']**2)
            for label, mask in [('<1', y < 1), ('>=1', y >= 1)]:
                low_high.append({**identity, 'range_ug_ml': label, **errors(y[mask], p[mask])})
    assert json.dumps(models, sort_keys=True) == snapshot
    assert len(points) == 40 and len(metrics) == 4 and len(ranges) == 16 and len(low_high) == 4
    for _, path, digest in loaded.values():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
    write_csv('predicciones.csv', points)
    write_csv('metricas.csv', metrics)
    write_csv('errores_por_rango.csv', ranges)
    write_csv('errores_menor_y_mayor_1.csv', low_high)
    result = {'models': models, 'metrics': metrics, 'test_ranges': ranges, 'test_low_high': low_high,
              'source_sha256': {g: d[2] for g, d in loaded.items()}, 'dataset_85_read_or_used': False}
    (OUT/'resultados.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

    plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5), constrained_layout=True)
    for ax, (train, test) in zip(axes, DIRECTIONS):
        d = loaded[test][0]
        y = d[:, 2]
        p, inside = test_predictions[train]
        m = next(r for r in metrics if r['train_dataset'] == train and r['role'] == 'test')
        limits = (min(-.1, float(p.min())-.15), max(float(y.max()), float(p.max()))+.25)
        ax.plot(limits, limits, '--', color='#777777', label='Predicción ideal')
        for mask, marker, label in [(inside, 'o', 'Dentro del intervalo de señal'), (~inside, '^', 'Extrapolación de señal')]:
            if mask.any():
                ax.scatter(y[mask], p[mask], s=52, marker=marker, color='#2675b8' if marker == 'o' else '#d66c1d', label=label)
        ax.set(xlabel='Chl(a) de referencia (µg/mL)', ylabel='Chl(a) predicha (µg/mL)',
               title=f'Entrenar con {train} → probar en {test}', xlim=limits, ylim=limits)
        ax.set_aspect('equal', adjustable='box')
        ax.text(.04, .96, f"R² predictivo = {m['r2_predictive']:.4f}\nRMSE = {m['rmse_ug_ml']:.4f} µg/mL\nMAE = {m['mae_ug_ml']:.4f} µg/mL\nMAPE = {m['mape_percent']:.2f}%",
                transform=ax.transAxes, va='top', fontsize=10, bbox={'facecolor': 'white', 'edgecolor': '#dddddd'})
        ax.legend(fontsize=8, loc='lower right')
        ax.grid(alpha=.15)
    fig.suptitle('ln(B645/I645) · blanco por sesión · dos ecuaciones independientes · sin las 85', fontsize=12)
    fig.savefig(OUT/'01_prueba_ambas_direcciones.png', dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)
    for ax, (train, test) in zip(axes, DIRECTIONS):
        model = models[train]
        all_x = []
        for group, color, label in [(train, '#2675b8', 'Entrenamiento'), (test, '#d66c1d', 'Prueba, no ajusta la recta')]:
            d = loaded[group][0]
            x = feature(d[:, 3], BLANKS[group])
            all_x.extend(x)
            ax.scatter(x, d[:, 2], s=40, color=color, label=f'{label}: {group}')
        xx = np.linspace(min(all_x), max(all_x), 200)
        ax.plot(xx, model['intercept']+model['slope']*xx, '--', color='#777777')
        xx = np.linspace(*model['training_feature_range'], 100)
        ax.plot(xx, model['intercept']+model['slope']*xx, color='#333333', label='Recta en intervalo de entrenamiento')
        ax.set(xlabel='ln(B645 de la sesión / I645)', ylabel='Chl(a) de referencia (µg/mL)',
               title=f"Entrenar con {train}: C = {model['intercept']:.5f} + {model['slope']:.5f} × ln(B/I)")
        ax.legend(fontsize=8)
        ax.grid(alpha=.15)
    fig.savefig(OUT/'02_curvas_calibracion.png', dpi=180)
    plt.close(fig)

    def table(rows, by_range=False):
        headers = ['Entrenar → probar']+(['Rango (µg/mL)'] if by_range else [])+['n', 'RMSE', 'MAE', 'Sesgo', 'MAPE (%)']
        values = [[f"{r['train_dataset']} → {r.get('test_dataset', r.get('evaluated_dataset'))}"]+
                  ([r['range_ug_ml']] if by_range else [])+[r['n']]+
                  [f"{r[k]:.5f}" if r[k] is not None else '—' for k in ('rmse_ug_ml', 'mae_ug_ml', 'bias_ug_ml')]+
                  [f"{r['mape_percent']:.2f}" if r['mape_percent'] is not None else '—'] for r in rows]
        return markdown_table(headers, values)
    tests = [r for r in metrics if r['role'] == 'test']
    report = ['# Entrenar con nueve y probar en once, y viceversa; ln645 con blanco', '',
              'Fecha: 18 de octubre de 2026.', '', '## Diseño',
              'Se excluyen completamente las 85: este análisis solo abre los Excel de nueve y once. Se hacen dos ajustes independientes, con mínimos cuadrados ordinarios, intercepto libre e igual peso por muestra. Se mantiene la forma C = a + b × ln(B645/I645).',
              'Blancos de sesión proporcionados por Alex: B645 = 1214 para las nueve y 1256 para las once. Se usan tanto al entrenar como al predecir. No se añaden como puntos de concentración cero ni se optimizan sus valores.',
              'En la dirección 9 → 11 solo las concentraciones de las nueve calculan los coeficientes. En 11 → 9 ocurre lo contrario. Las ecuaciones se fijan antes de evaluar los errores de transferencia; no se seleccionan formas, pesos ni ajustes adicionales mirando el conjunto de prueba.', '', '## Ecuaciones']
    for train, test in DIRECTIONS:
        model = models[train]
        report += [f"Entrenar con {train}, probar en {test}: **C (µg/mL) = {model['intercept']:.10f} + {model['slope']:.10f} × ln(B645/I645).**"]
    report += ['ln es el logaritmo natural. I645 es la intensidad media de la muestra; B645 es el blanco de su sesión, en las mismas unidades y configuración. Ambos deben ser positivos y finitos.', '',
               '## Resultados de prueba, no de entrenamiento', table(tests)]
    for r in tests:
        report += [f"{r['train_dataset']} → {r['evaluated_dataset']}: R² predictivo = {r['r2_predictive']:.5f}; señales fuera del intervalo de entrenamiento = {r['outside_training_feature_range_n']}/{r['n']}; predicciones negativas = {r['negative_predictions_n']}."]
    report += ['RMSE, MAE y sesgo en µg/mL. Sesgo = promedio(predicción − referencia); MAPE = promedio(|predicción − referencia|/referencia) × 100. No se recortan negativos ni se eliminan atípicos. Las métricas del ajuste sobre el propio entrenamiento están separadas en metricas.csv; no son CV.', '',
               '## Prueba por debajo y por encima de 1 µg/mL', table(low_high, True), '',
               '## Prueba por intervalos fijos', table(ranges, True),
               'Intervalos según concentración de referencia: extremo inferior incluido y superior excluido, salvo el último que incluye 8. — significa ausencia de muestras, no error cero. Un rango con una observación no estima su variabilidad.', '',
               '## Gráficas', '![Prueba en ambas direcciones](01_prueba_ambas_direcciones.png)',
               '![Rectas de calibración y puntos de prueba](02_curvas_calibracion.png)', '', '## Cómo interpretar la comparación',
               f"Con nueve para entrenar, las once se subestiman: sesgo {tests[0]['bias_ug_ml']:+.5f} µg/mL. Con once para entrenar, el sesgo medio sobre las nueve es {tests[1]['bias_ug_ml']:+.5f} µg/mL. Las pendientes son distintas: {models['9']['slope']:.5f} frente a {models['11']['slope']:.5f}. Normalizar por el blanco no elimina la discrepancia entre estas dos tandas.",
               'Las métricas de ambas direcciones se calculan sobre conjuntos distintos y rangos distintos. No constituyen una comparación de dos modelos sobre las mismas muestras de prueba. El entrenamiento de once cubre 0,7944–3,07062 µg/mL; el de nueve cubre 0,0244–3,9098. Al predecir las nueve con la calibración de once hay concentraciones inferiores y superiores al rango entrenado. La figura marca además la extrapolación según la señal normalizada, que no coincide necesariamente con esos límites de concentración.',
               'Las nueve proceden de diluciones de un solo extracto madre. Los dos conjuntos ya se han examinado en etapas previas, por lo que se trata de comprobaciones retrospectivas de transferencia, no de validación prospectiva ciega. Cada conjunto tiene un papel distinto en cada prueba; no hay una única reserva de datos intacta tras ambas direcciones.',
               'El MAPE es muy sensible a concentraciones cercanas a cero. No representa incertidumbre ni garantiza un error máximo. No se determina LOD/LOQ ni rendimiento en lagos. No se cambia el firmware ni los .bin.', '', '## Fuentes y archivos',
               '9Samples.xlsx: Sheet1 A1:AL10. 11Samples.xlsx: Sheet1 A1:AL12. Se usan identificador, concentración de referencia e I645. Ambos originales se verifican por SHA-256 y permanecen intactos. Los blancos proceden de los valores de sesión aportados por Alex.',
               'Los dos modelo_entrenado_*.json conservan los coeficientes. resultados.json conserva métricas y procedencia. predicciones.csv contiene 40 filas: 20 de ajuste sobre su propio entrenamiento y 20 de transferencia. metricas.csv identifica ambos papeles. errores_por_rango.csv contiene 16 intervalos y errores_menor_y_mayor_1.csv resume cuatro evaluaciones.',
               'Los análisis previos se conservan. Se reutilizan únicamente funciones de lectura, normalización y métricas, no coeficientes de otros conjuntos. Se verifican los ajustes por covarianza y ecuaciones normales, los recuentos de puntos y rangos, la agregación de errores y la conservación de las ecuaciones.']
    (OUT/'informe.md').write_text('\n'.join(report)+'\n', encoding='utf-8')
    print(json.dumps({'models': models, 'test_metrics': tests, 'test_low_high': low_high, 'checks': 'passed'}, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
