"""LOOCV ln(I645) on 85; then apply frozen coefficients to 9 and 11. No blank."""
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
sys.path.insert(0, str(DATA/'relacion_645_sin_blanco'))
# Reuse only the loader and formatting helpers; their main routines are not run.
from analizar_645 import load, markdown_table

BINS = [0, .1, .25, .5, 1, 2, 3, 5, 8]
LABELS = ['0–<0,1', '0,1–<0,25', '0,25–<0,5', '0,5–<1', '1–<2', '2–<3', '3–<5', '5–8']
ROLES = {'85': 'CV85, entrenamiento con 84 por turno',
         '9': 'Comprobación 9, ecuación fija de 85', '11': 'Comprobación 11, ecuación fija de 85'}
COLORS = {'85': '#2675b8', '9': '#21966a', '11': '#d66c1d'}


def fit(x, y):
    return np.linalg.lstsq(np.c_[np.ones(len(x)), x], y, rcond=None)[0]


def errors(y, p):
    if not len(y):
        return {'n': 0, **{k: None for k in ['rmse_ug_ml', 'mae_ug_ml', 'bias_ug_ml',
                                            'max_abs_error_ug_ml', 'mape_percent', 'negative_predictions_n']}}
    assert np.isfinite(y).all() and np.isfinite(p).all() and (y > 0).all()
    e = p-y
    return {'n': len(y), 'rmse_ug_ml': float(np.sqrt(np.mean(e**2))),
            'mae_ug_ml': float(np.mean(abs(e))), 'bias_ug_ml': float(e.mean()),
            'max_abs_error_ug_ml': float(max(abs(e))),
            'mape_percent': float(np.mean(abs(e)/y)*100), 'negative_predictions_n': int((p < 0).sum())}


def write_csv(name, rows):
    with (OUT/name).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    train, train_path, train_hash = load('85')
    x, y = np.log(train[:, 3]), train[:, 2]
    a, b = fit(x, y)
    # Independent full-fit check using centered covariance.
    slope = np.sum((x-x.mean())*(y-y.mean()))/np.sum((x-x.mean())**2)
    assert np.allclose([a, b], [y.mean()-slope*x.mean(), slope], atol=1e-10)
    cv = np.full(85, np.nan)
    cv_domain = np.zeros(85, dtype=bool)
    folds = []
    for i in range(85):
        keep = np.arange(85) != i
        assert keep.sum() == 84 and not keep[i]
        coef = fit(x[keep], y[keep])
        cv[i] = coef[0] + coef[1]*x[i]
        cv_domain[i] = x[keep].min() <= x[i] <= x[keep].max()
        folds.append({'held_out_sample': int(train[i, 0]), 'training_n': 84,
                      'intercept': float(coef[0]), 'slope_lnI645': float(coef[1])})
    assert np.isfinite(cv).all()
    # Independently verify all explicit folds with the OLS deleted-residual identity.
    full = a+b*x
    leverage = 1/85 + (x-x.mean())**2/np.sum((x-x.mean())**2)
    analytic_cv = y-(y-full)/(1-leverage)
    assert np.allclose(cv, analytic_cv, atol=1e-10)

    frozen = {'equation': 'C_ug_ml = intercept + slope_lnI645 * ln(I645)',
              'intercept': float(a), 'slope_lnI645': float(b), 'fit_n': 85, 'blank_used': False,
              'training_source': str(train_path), 'training_sha256': train_hash,
              'training_concentration_range_ug_ml': [float(y.min()), float(y.max())],
              'training_lnI645_range': [float(x.min()), float(x.max())],
              'purpose': 'Full fit on 85 for application; CV85 uses a separate fit on 84 in each fold.'}
    # Freeze the model before opening either comparison workbook.
    (OUT/'modelo_85_fijado.json').write_text(json.dumps(frozen, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    coef_snapshot = (float(a), float(b))
    loaded = {'85': (train, train_path, train_hash)}
    predictions = {'85': cv}
    domain = {'85': cv_domain}
    for group in ('9', '11'):
        loaded[group] = load(group)
        data = loaded[group][0]
        xt = np.log(data[:, 3])
        predictions[group] = a+b*xt
        domain[group] = (xt >= x.min()) & (xt <= x.max())
    assert (float(a), float(b)) == coef_snapshot

    summary, range_rows, low_high, prediction_rows = {}, [], [], []
    for group, (data, path, digest) in loaded.items():
        yy, pp = data[:, 2], predictions[group]
        score = errors(yy, pp)
        score['r2_predictive'] = float(1 - np.sum((pp-yy)**2)/np.sum((yy-yy.mean())**2))
        score['outside_fitted_signal_domain_n'] = int((~domain[group]).sum())
        summary[group] = {'evaluation': ROLES[group], **score}
        seen = np.zeros(len(data), dtype=int)
        for j, (left, right, label) in enumerate(zip(BINS[:-1], BINS[1:], LABELS)):
            mask = (yy >= left) & ((yy <= right) if j == len(LABELS)-1 else (yy < right))
            seen += mask
            range_rows.append({'dataset': group, 'evaluation': ROLES[group], 'range_ug_ml': label,
                               'lower_ug_ml': left, 'upper_ug_ml': right,
                               'upper_inclusive': j == len(LABELS)-1, **errors(yy[mask], pp[mask])})
        assert np.all(seen == 1)
        rr = [r for r in range_rows if r['dataset'] == group and r['n']]
        assert sum(r['n'] for r in rr) == len(data)
        assert np.isclose(sum(r['n']*r['mae_ug_ml'] for r in rr)/len(data), score['mae_ug_ml'])
        assert np.isclose(sum(r['n']*r['rmse_ug_ml']**2 for r in rr)/len(data), score['rmse_ug_ml']**2)
        for label, mask in [('<1', yy < 1), ('>=1', yy >= 1)]:
            low_high.append({'dataset': group, 'evaluation': ROLES[group], 'range_ug_ml': label,
                             **errors(yy[mask], pp[mask])})
        for i in range(len(data)):
            prediction_rows.append({'dataset': group, 'evaluation': ROLES[group], 'source': path.name,
                                    'sample': int(data[i, 0]), 'excel_row': int(data[i, 1]),
                                    'reference_ug_ml': yy[i], 'I645': data[i, 3], 'lnI645': np.log(data[i, 3]),
                                    'prediction_ug_ml': pp[i], 'error_ug_ml': pp[i]-yy[i],
                                    'absolute_error_ug_ml': abs(pp[i]-yy[i]),
                                    'absolute_relative_error_percent': abs(pp[i]-yy[i])/yy[i]*100,
                                    'inside_fitted_signal_domain': bool(domain[group][i])})
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest

    write_csv('predicciones.csv', prediction_rows)
    write_csv('errores_por_rango.csv', range_rows)
    write_csv('errores_menor_y_mayor_1.csv', low_high)
    result = {'model': frozen, 'global_metrics': summary, 'ranges': range_rows,
              'below_above_1': low_high, 'cv85_folds': folds,
              'source_sha256': {g: d[2] for g, d in loaded.items()},
              'range_definition': 'Reference concentration; lower inclusive, upper exclusive except final 5–8 bin.'}
    (OUT/'resultados.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), constrained_layout=True)
    xx = np.linspace(x.min(), x.max(), 200)
    axes[0].scatter(x, y, s=25, color=COLORS['85'], alpha=.8, label='85 referencias')
    axes[0].plot(xx, a+b*xx, color='#333333', label='Ecuación ajustada con las 85')
    axes[0].set(xlabel='ln(I645)', ylabel='Chl(a) de referencia (µg/mL)', title='Relación y ecuación completa')
    axes[0].legend(fontsize=8)
    low = min(-.2, float(cv.min())-.1)
    high = max(float(y.max()), float(cv.max()))+.3
    axes[1].plot([low, high], [low, high], '--', color='#777777')
    axes[1].scatter(y, cv, s=28, color=COLORS['85'], alpha=.8)
    axes[1].set(xlabel='Chl(a) de referencia (µg/mL)', ylabel='Chl(a) predicha por CV (µg/mL)',
                title='CV85: cada punto predicho usando 84', xlim=(low, high), ylim=(low, high))
    m = summary['85']
    axes[1].text(.04, .96, f"R² CV = {m['r2_predictive']:.4f}\nRMSE CV = {m['rmse_ug_ml']:.4f} µg/mL\nMAE CV = {m['mae_ug_ml']:.4f} µg/mL",
                 transform=axes[1].transAxes, va='top', bbox={'facecolor': 'white', 'edgecolor': '#dddddd'})
    axes[2].axhline(0, ls='--', color='#777777')
    axes[2].scatter(y, cv-y, s=28, color=COLORS['85'], alpha=.8)
    for i in np.argsort(abs(cv-y))[-3:]:
        axes[2].annotate(str(int(train[i, 0])), (y[i], cv[i]-y[i]), xytext=(4, 4), textcoords='offset points', fontsize=8)
    axes[2].set(xlabel='Chl(a) de referencia (µg/mL)', ylabel='Predicción CV − referencia (µg/mL)', title='Errores de las 85 predicciones de CV')
    for ax in axes:
        ax.grid(alpha=.15)
    fig.suptitle(f'C = {a:.6f} {b:+.6f} × ln(I645)   ·   sin blanco', fontsize=14)
    fig.savefig(OUT/'01_cv_85.png', dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.3), constrained_layout=True)
    for ax, group in zip(axes, ('9', '11')):
        data = loaded[group][0]
        yy, pp, m = data[:, 2], predictions[group], summary[group]
        low = min(-.1, float(yy.min())-.15, float(pp.min())-.15)
        high = max(float(yy.max()), float(pp.max()))+.25
        ax.plot([low, high], [low, high], '--', color='#777777', label='Predicción ideal')
        ax.scatter(yy, pp, s=40, color=COLORS[group])
        for i in range(len(data)):
            ax.annotate(str(int(data[i, 0])), (yy[i], pp[i]), xytext=(4, 4), textcoords='offset points', fontsize=8)
        ax.set(xlabel='Chl(a) de referencia (µg/mL)', ylabel='Chl(a) predicha (µg/mL)',
               title=f'Aplicación a {group} muestras, sin reajustar', xlim=(low, high), ylim=(low, high))
        ax.set_aspect('equal', adjustable='box')
        ax.text(.04, .96, f"R² predictivo = {m['r2_predictive']:.4f}\nRMSE = {m['rmse_ug_ml']:.4f} µg/mL\nSesgo = {m['bias_ug_ml']:+.4f} µg/mL",
                transform=ax.transAxes, va='top', fontsize=10, bbox={'facecolor': 'white', 'edgecolor': '#dddddd'})
        ax.grid(alpha=.15)
        ax.legend(fontsize=8, loc='lower right')
    fig.suptitle('Misma ecuación calibrada solo con las 85; sin blanco ni correcciones posteriores', fontsize=13)
    fig.savefig(OUT/'02_aplicacion_9_y_11.png', dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(2, 1, figsize=(12, 8), constrained_layout=True)
    positions = np.arange(len(LABELS))
    for shift, group in enumerate(('85', '9', '11')):
        rr = [r for r in range_rows if r['dataset'] == group]
        for ax, metric in zip(axes, ('mae_ug_ml', 'mape_percent')):
            heights = [r[metric] if r['n'] else np.nan for r in rr]
            bars = ax.bar(positions+(shift-1)*.25, heights, width=.24, color=COLORS[group], label=ROLES[group].split(',')[0])
            if metric == 'mae_ug_ml':
                for bar, r in zip(bars, rr):
                    if r['n']:
                        ax.annotate(f"n={r['n']}", (bar.get_x()+bar.get_width()/2, bar.get_height()),
                                    xytext=(0, 3), textcoords='offset points', ha='center', fontsize=8)
    axes[0].set(ylabel='MAE (µg/mL)', title='Error absoluto medio por rango; n indica el número de muestras')
    axes[1].set(ylabel='Error relativo absoluto medio (%)', xlabel='Concentración de referencia (µg/mL)',
                title='MAPE por rango; no es incertidumbre ni error máximo')
    for ax in axes:
        ax.set_xticks(positions, LABELS)
        ax.grid(axis='y', alpha=.15)
        ax.set_axisbelow(True)
        ax.legend(fontsize=9)
        ax.margins(y=.17)
    fig.savefig(OUT/'03_errores_por_rango.png', dpi=180)
    plt.close(fig)

    def format_rows(rr, with_r2=False):
        values = []
        for r in rr:
            row = [r.get('range_ug_ml', r['evaluation']), r['n']]
            if with_r2:
                row.append(f"{r['r2_predictive']:.5f}")
            row += [f"{r[k]:.5f}" if r[k] is not None else '—'
                    for k in ('rmse_ug_ml', 'mae_ug_ml', 'bias_ug_ml', 'max_abs_error_ug_ml')]
            row.append(f"{r['mape_percent']:.2f}" if r['mape_percent'] is not None else '—')
            values.append(row)
        return values

    headers = ['Evaluación', 'n', 'R² predictivo', 'RMSE', 'MAE', 'Sesgo', 'Error máximo', 'MAPE (%)']
    range_headers = ['Rango (µg/mL)', 'n', 'RMSE', 'MAE', 'Sesgo', 'Error máximo', 'MAPE (%)']
    report = ['# ln(I645): CV con las 85 y aplicación a las nueve y las once', '',
              'Fecha: 18 de octubre de 2026. Nueva etapa solicitada por Alex: se adopta la forma lineal en ln(I645), sin blanco. No se utiliza ND ni se reajusta con las nueve o las once.', '',
              '## Ecuación fijada con las 85', f'C (µg/mL) = {a:.10f} {b:+.10f} × ln(I645).',
              'ln es el logaritmo natural; I645 es la intensidad media suministrada en los Excel. Los coeficientes se ajustan con las 85 muestras completas. Se guarda el modelo antes de abrir los otros dos Excel. Esta ecuación completa no se utiliza para calcular la CV85.', '',
              '## Validación y comprobaciones',
              'CV85: entrenar con 84 y predecir la omitida, repitiendo 85 veces. Las métricas de las 85 usan únicamente esas predicciones fuera del entrenamiento. La CV se verificó independientemente mediante la identidad de residuos eliminados de regresión lineal.',
              'Comprobaciones 9 y 11: aplicar sin modificación los coeficientes ajustados con las 85. No son CV9 ni CV11. Esos conjuntos ya fueron examinados en la investigación, por lo que se describe una comprobación retrospectiva de transferencia, no una validación prospectiva ciega.',
              'No se corrige por blanco, no se pondera por desviaciones, no se eliminan atípicos y no se recortan predicciones negativas. Se excluyen del conjunto de 85 las filas con solo identificadores, no mediciones completas.', '',
              '## Errores globales', markdown_table(headers, format_rows(list(summary.values()), True)),
              'RMSE, MAE, sesgo y error máximo están en µg/mL. R² predictivo = 1 − Σ(predicción − referencia)² / Σ(referencia − media de referencia)². MAPE = promedio(|predicción − referencia|/referencia) × 100. Sesgo positivo significa sobreestimación.', '',
              '## Resumen por debajo y por encima de 1 µg/mL',
              markdown_table(['Evaluación']+range_headers,
                             [[r['evaluation']]+row for r, row in zip(low_high, format_rows(low_high))]), '',
              '## Errores por intervalos fijos',
              'Los intervalos se definieron antes de evaluar resultados, según la referencia, no según la predicción. Incluyen el extremo inferior y excluyen el superior, excepto el último, que incluye 8. Los guiones significan que no hay muestras, no error cero. Un intervalo con una muestra describe solo esa observación. No se calcula R² por intervalo para evitar interpretar porcentajes de varianza con muy pocos puntos.',
              'El promedio global no se obtiene promediando sin pesos los errores de los intervalos: cada muestra tiene el mismo peso dentro de su evaluación. Los recuentos y la agregación de MAE/RMSE se verifican contra las métricas globales.']
    for group in ('85', '9', '11'):
        report += ['', f'### {ROLES[group]}', markdown_table(range_headers, format_rows([r for r in range_rows if r['dataset'] == group]))]
    report += ['', '## Figuras', '![Relación, CV85 y residuales](01_cv_85.png)',
               '![Comprobaciones sobre nueve y once](02_aplicacion_9_y_11.png)',
               '![Errores por concentración](03_errores_por_rango.png)', '',
               '## Alcance',
               'La calibración cubre 0,02384–7,98964 µg/mL. Las nueve cubren 0,0244–3,9098 y las once 0,7944–3,07062. Que una señal quede dentro del intervalo de calibración no demuestra transferencia entre tandas ni elimina efectos del protocolo.',
               'Las nueve son diluciones de un mismo extracto madre. La CV85 evalúa la tanda disponible y no constituye por sí sola validación entre sesiones. Se desconoce una agrupación más detallada por extracto madre o día para las 85; no se ha hecho CV agrupada por esos factores.',
               'El MAPE puede crecer mucho cerca de cero. No representa una incertidumbre expandida ni un error máximo garantizado. No se establece un límite de cuantificación a partir del menor punto. No se han preparado extractos, medido lagos ni cambiado el firmware.', '',
               '## Archivos',
               'modelo_85_fijado.json conserva la ecuación completa previa a las comprobaciones. resultados.json conserva las métricas, los 85 ajustes por turno y la procedencia. predicciones.csv contiene 105 predicciones: 85 de CV y 20 de aplicación fija. errores_por_rango.csv conserva todos los intervalos, incluidos los vacíos. errores_menor_y_mayor_1.csv resume el rango bajo.',
               'Los resultados de esta carpeta son una etapa nueva; no sobrescriben los análisis previos. El documento articulo.md describe la propuesta anterior con ND y necesitará revisión si se incorpora esta nueva elección al manuscrito.']
    (OUT/'informe.md').write_text('\n'.join(report)+'\n', encoding='utf-8')
    print(json.dumps({'model': frozen, 'global': summary, 'low_high': low_high,
                      'ranges_nonempty': [r for r in range_rows if r['n']],
                      'checks': '85 disjoint folds, analytic deleted-residual identity, range counts and aggregates, frozen coefficients, originals unchanged'}, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
