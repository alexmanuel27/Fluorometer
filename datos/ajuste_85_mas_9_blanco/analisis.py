"""Fit C = a + b ln(B645/I645) on 85+9; apply frozen equation to 11."""
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
from analisis_blanco import feature, BLANKS
from analisis_85 import load, fit, errors, BINS, LABELS, markdown_table


def write_csv(name, rows):
    with (OUT/name).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def score(y, p):
    result = errors(y, p)
    result['r2_predictive'] = float(1-np.sum((p-y)**2)/np.sum((y-y.mean())**2))
    return result


def main():
    # Both calibration sets are loaded before fitting; the 11-point test is not.
    loaded = {g: load(g) for g in ('85', '9')}
    z = np.concatenate([feature(d[0][:, 3], BLANKS[g]) for g, d in loaded.items()])
    y = np.concatenate([d[0][:, 2] for d in loaded.values()])
    assert len(z) == len(y) == 94
    alpha, beta = map(float, fit(z, y))
    fitted = alpha+beta*z
    # Verify OLS independently with centered covariance and normal equations.
    slope = np.sum((z-z.mean())*(y-y.mean()))/np.sum((z-z.mean())**2)
    assert np.allclose([alpha, beta], [y.mean()-slope*z.mean(), slope], atol=1e-10)
    assert np.allclose([np.sum(fitted-y), np.dot(z, fitted-y)], 0, atol=1e-9)
    model = {'equation': 'C_ug_ml = intercept + slope * ln(B645_session/I645)',
             'intercept': alpha, 'slope': beta, 'fit_n': 94, 'fit_datasets': ['85', '9'],
             'test_dataset': '11', 'fit_method': 'OLS with intercept; equal weight per sample',
             'session_blanks_I645': BLANKS, 'blank_source': 'Fixed session means supplied by Alex',
             'training_sources': {g: {'path': str(d[1]), 'sha256': d[2]} for g, d in loaded.items()},
             'training_concentration_range_ug_ml': [float(y.min()), float(y.max())],
             'training_feature_range': [float(z.min()), float(z.max())],
             'test_used_for_fitting_or_selection': False}
    frozen_path = OUT/'modelo_fijado_94.json'
    frozen_path.write_text(json.dumps(model, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    snapshot = frozen_path.read_bytes()
    loaded['11'] = load('11')
    predictions = {g: alpha+beta*feature(d[0][:, 3], BLANKS[g]) for g, d in loaded.items()}
    assert frozen_path.read_bytes() == snapshot

    train_score = score(y, fitted)
    test_data = loaded['11'][0]
    test_y, test_p = test_data[:, 2], predictions['11']
    test_score = score(test_y, test_p)
    test_z = feature(test_data[:, 3], BLANKS['11'])
    test_score['outside_training_feature_range_n'] = int(((test_z < z.min()) | (test_z > z.max())).sum())
    metrics = [{'evaluation': 'Ajuste de calibración 85+9, no CV', 'dataset': '94', **train_score}]
    for group, (d, _, _) in loaded.items():
        role = 'Prueba: no utilizada para ajustar' if group == '11' else 'Parte de la calibración, no CV'
        metrics.append({'evaluation': role, 'dataset': group, **score(d[:, 2], predictions[group])})
    ranges = []
    coverage = np.zeros(11, dtype=int)
    for j, (left, right, label) in enumerate(zip(BINS[:-1], BINS[1:], LABELS)):
        mask = (test_y >= left) & ((test_y <= right) if j == len(LABELS)-1 else (test_y < right))
        coverage += mask
        ranges.append({'range_ug_ml': label, 'lower_ug_ml': left, 'upper_ug_ml': right,
                       'upper_inclusive': j == len(LABELS)-1, **errors(test_y[mask], test_p[mask])})
    assert np.all(coverage == 1)
    assert np.isclose(sum(r['n']*r['mae_ug_ml'] for r in ranges if r['n'])/11, test_score['mae_ug_ml'])
    assert np.isclose(sum(r['n']*r['rmse_ug_ml']**2 for r in ranges if r['n'])/11, test_score['rmse_ug_ml']**2)
    low_high = [{'range_ug_ml': label, **errors(test_y[mask], test_p[mask])}
                for label, mask in [('<1', test_y < 1), ('>=1', test_y >= 1)]]
    points = []
    for group, (d, path, digest) in loaded.items():
        for i, row in enumerate(d):
            p = predictions[group][i]
            points.append({'dataset': group, 'role': 'test' if group == '11' else 'calibration',
                           'source': path.name, 'sample': int(row[0]), 'excel_row': int(row[1]),
                           'reference_ug_ml': row[2], 'I645': row[3], 'B645_session': BLANKS[group],
                           'ln_B645_over_I645': float(feature(row[3], BLANKS[group])),
                           'prediction_ug_ml': p, 'error_ug_ml': p-row[2],
                           'absolute_relative_error_percent': abs(p-row[2])/row[2]*100})
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
    write_csv('predicciones.csv', points)
    write_csv('metricas.csv', metrics)
    write_csv('errores_por_rango_11.csv', ranges)
    write_csv('errores_menor_y_mayor_1_11.csv', low_high)
    result = {'model': model, 'calibration_94_in_sample': train_score, 'test_11': test_score,
              'metrics': metrics, 'test_11_ranges': ranges, 'test_11_low_high': low_high,
              'source_sha256': {g: d[2] for g, d in loaded.items()}}
    (OUT/'resultados.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

    plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, ax = plt.subplots(figsize=(8.5, 5.5), constrained_layout=True)
    for group, color in [('85', '#2675b8'), ('9', '#21966a')]:
        d = loaded[group][0]
        ax.scatter(feature(d[:, 3], BLANKS[group]), d[:, 2], s=32, alpha=.8, color=color, label=f'{group} muestras de calibración')
    xx = np.linspace(z.min(), z.max(), 200)
    ax.plot(xx, alpha+beta*xx, color='#333333', label='Ajuste con las 94 muestras')
    ax.set(xlabel='ln(B645 de la sesión / I645)', ylabel='Chl(a) de referencia (µg/mL)',
           title=f'C = {alpha:.6f} + {beta:.6f} × ln(B645/I645)')
    ax.grid(alpha=.15)
    ax.legend()
    fig.savefig(OUT/'01_ajuste_94.png', dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.2), constrained_layout=True)
    limits = (min(0, test_p.min()-.15), max(test_y.max(), test_p.max())+.2)
    axes[0].plot(limits, limits, '--', color='#777777', label='Predicción ideal')
    axes[0].scatter(test_y, test_p, color='#d66c1d', s=48, label='11 muestras de prueba')
    axes[0].set(xlabel='Chl(a) de referencia (µg/mL)', ylabel='Chl(a) predicha (µg/mL)',
                title='Ecuación de las 94 aplicada fija a las 11', xlim=limits, ylim=limits)
    axes[0].set_aspect('equal', adjustable='box')
    axes[0].text(.04, .96, f"R² predictivo = {test_score['r2_predictive']:.4f}\nRMSE = {test_score['rmse_ug_ml']:.4f} µg/mL\nMAE = {test_score['mae_ug_ml']:.4f} µg/mL\nMAPE = {test_score['mape_percent']:.2f}%",
                 transform=axes[0].transAxes, va='top', fontsize=10, bbox={'facecolor': 'white', 'edgecolor': '#dddddd'})
    axes[0].legend(fontsize=9, loc='lower right')
    axes[1].axhline(0, ls='--', color='#777777')
    axes[1].scatter(test_y, test_p-test_y, color='#d66c1d', s=48)
    for i in range(11):
        axes[1].annotate(str(int(test_data[i, 0])), (test_y[i], test_p[i]-test_y[i]),
                         xytext=(4, 5), textcoords='offset points', fontsize=8)
    axes[1].set(xlabel='Chl(a) de referencia (µg/mL)', ylabel='Predicción − referencia (µg/mL)', title='Errores de las 11 muestras')
    for ax in axes:
        ax.grid(alpha=.15)
    fig.suptitle(f'C = {alpha:.6f} + {beta:.6f} × ln(B645/I645)   ·   B645 de las 11 = 1256', fontsize=12)
    fig.savefig(OUT/'02_prueba_11.png', dpi=180)
    plt.close(fig)

    def table(rows, first):
        return markdown_table([first, 'n', 'RMSE', 'MAE', 'Sesgo', 'MAPE (%)'],
                              [[r.get('range_ug_ml', r.get('evaluation', '')), r['n']]+
                               [f"{r[k]:.5f}" if r[k] is not None else '—' for k in ('rmse_ug_ml', 'mae_ug_ml', 'bias_ug_ml')]+
                               [f"{r['mape_percent']:.2f}" if r['mape_percent'] is not None else '—'] for r in rows])
    report = ['# Ajuste conjunto con 85 + 9 y blanco de sesión; prueba en las 11', '',
              'Fecha: 18 de octubre de 2026.', '', '## Diseño solicitado',
              'Calibración: las 85 y las 9 juntas, 94 puntos. Prueba: las 11, excluidas del cálculo de los coeficientes. Se mantiene una única relación lineal con intercepto en ln(B645/I645), sin polinomios ni selección posterior mirando las once.',
              'Blancos fijos proporcionados por Alex: 1356 para las 85, 1214 para las 9 y 1256 para las 11. Se emplea el blanco de cada sesión, no un blanco por muestra. No se añaden los blancos como puntos de concentración cero.',
              'Mínimos cuadrados ordinarios, igual peso por muestra: la tanda de 85 aporta 85/94 del peso y la de nueve 9/94. No se igualan los pesos por tanda ni se pondera por las desviaciones del sensor.', '',
              '## Ecuación nueva', f'**Chl(a) (µg/mL) = {alpha:.10f} + {beta:.10f} × ln(B645 / I645).**',
              'I645 es la intensidad media de la muestra. B645 es la intensidad del blanco de la sesión en la misma configuración y unidades instrumentales. ln es el logaritmo natural. I y B deben ser positivos y finitos.',
              'Ambos coeficientes se recalculan con los 94 puntos. No es la ecuación anterior de las 85 aplicada otra vez. Se guarda modelo_fijado_94.json antes de abrir las once. No se recortan predicciones negativas ni se eliminan atípicos.', '',
              '## Ajuste y prueba', table([metrics[0], metrics[-1]], 'Evaluación'),
              f"R² del ajuste de las 94 = {train_score['r2_predictive']:.5f}. R² predictivo en las once = {test_score['r2_predictive']:.5f}.",
              'RMSE, MAE y sesgo en µg/mL. Las métricas de las 94 describen el ajuste sobre sus propios datos, no CV. Las métricas de las 11 corresponden a aplicación sin reajustar. Sesgo positivo significa sobreestimación. MAPE es el promedio del error relativo absoluto, no incertidumbre expandida.', '',
              '## Prueba en las 11 por rango', table(low_high, 'Rango (µg/mL)'), '',
              table(ranges, 'Rango fijo (µg/mL)'),
              'Los rangos se determinan por la concentración de referencia. Extremo inferior incluido y superior excluido, excepto el último, que incluye 8. — indica ausencia de muestras. Los rangos con n=1 describen solo esa observación.', '',
              '## Gráficas', '![Ajuste con las 94](01_ajuste_94.png)', '![Aplicación fija a las 11](02_prueba_11.png)', '',
              '## Interpretación y alcance',
              f"En las once el sesgo medio es {test_score['bias_ug_ml']:+.5f} µg/mL. La inclusión de las nueve cambia poco la ecuación porque son 9 de 94 puntos y, tras normalizar por el blanco, ya estaban próximas a la relación de las 85.",
              'Las once no se usan para ajustar o elegir la forma de esta nueva ecuación. Sin embargo, ya se examinaron en etapas previas: esta es una comprobación retrospectiva de transferencia, no una validación prospectiva ciega.',
              'Las nueve son diluciones de un único extracto madre, no nueve extractos independientes. No se establece incertidumbre del blanco, LOD/LOQ ni rendimiento en lagos. No se ha modificado el firmware ni generado nuevos .bin.', '',
              '## Fuentes y archivos',
              'calibracion_85_puntos (1).xlsx: Sheet1 A1:D86; 9Samples.xlsx: Sheet1 A1:AL10; 11Samples.xlsx: Sheet1 A1:AL12. Se usan identificador, concentración e I645. Los originales permanecen intactos y sus SHA-256 se conservan en resultados.json.',
              'modelo_fijado_94.json conserva la ecuación previa a la prueba; resultados.json contiene métricas y procedencia; predicciones.csv contiene 94 filas de calibración y 11 de prueba; metricas.csv separa ambas evaluaciones y las partes del ajuste. Los CSV de errores conservan la prueba de las once por rango y por debajo/encima de 1 µg/mL.',
              'Los análisis anteriores se conservan sin cambios. El cálculo reutiliza las funciones verificadas de lectura, normalización y métricas. Se comprueba el ajuste por una segunda fórmula, las ecuaciones normales, los recuentos de muestras, la conservación del modelo y la agregación de errores por rango.']
    (OUT/'informe.md').write_text('\n'.join(report)+'\n', encoding='utf-8')
    print(json.dumps({'equation': {'intercept': alpha, 'slope': beta}, 'calibration_94': train_score,
                      'test_11': test_score, 'test_11_low_high': low_high, 'checks': 'passed'}, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
