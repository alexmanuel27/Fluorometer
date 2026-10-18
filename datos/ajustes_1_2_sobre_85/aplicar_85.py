"""Apply two frozen CV11 models to 85 samples. No fitting, no 9-sample input."""
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
FROZEN = DATA / 'cv_11_exclusivo/resultados_11.json'
SOURCES = [DATA / '11Samples.xlsx', DATA / 'calibracion_85_puntos (1).xlsx', FROZEN]


def read_samples(path, expected):
    book = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheet = book['Sheet1']
    values = list(sheet.values)
    book.close()
    headers = values[0]
    cy, ci = headers.index('Chl(a) [µg/mL]'), headers.index('I(645)')
    rows = [(num, r[0], r[cy], r[ci]) for num, r in enumerate(values[1:], 2)
            if isinstance(r[cy], (float, int)) and isinstance(r[ci], (float, int))]
    a = np.asarray(rows, dtype=float)
    assert a.shape == (expected, 4) and np.isfinite(a).all() and (a[:, 3] > 0).all()
    assert len(set(a[:, 1])) == expected
    return a


def metrics(y, p):
    error = p - y
    return {'n': len(y), 'r2_predictive': float(1 - sum(error**2) / sum((y-y.mean())**2)),
            'rmse_ug_ml': float(np.sqrt(np.mean(error**2))),
            'mae_ug_ml': float(np.mean(abs(error))), 'bias_ug_ml': float(error.mean()),
            'max_abs_error_ug_ml': float(max(abs(error)))}


def main():
    hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCES}
    frozen = json.loads(FROZEN.read_text())
    assert hashes[str(SOURCES[0])] == frozen['input_sha256']
    train, test = read_samples(SOURCES[0], 11), read_samples(SOURCES[1], 85)
    x_train, x_test = np.log(train[:, 3]), np.log(test[:, 3])
    xmin, xmax = float(x_train.min()), float(x_train.max())
    in_signal_range = (x_test >= xmin) & (x_test <= xmax)
    in_concentration_range = (test[:, 2] >= train[:, 2].min()) & (test[:, 2] <= train[:, 2].max())
    keys = ['quadratic_log_645', 'log_645']
    results, predictions = {}, {}
    for key in keys:
        coef = np.array(frozen['refit_equations'][key]['coefficients'])
        p = np.polynomial.polynomial.polyval(x_test, coef)
        # Independent direct calculation checks polynomial order and all 85 predictions.
        direct = coef[0] + coef[1] * x_test
        if len(coef) == 3:
            direct = direct + coef[2] * x_test**2
        assert np.allclose(p, direct, atol=1e-12) and np.isfinite(p).all()
        results[key] = {'coefficients_from_11': coef.tolist(), 'all_85': metrics(test[:, 2], p),
                        'within_training_signal_range': metrics(test[in_signal_range, 2], p[in_signal_range])}
        predictions[key] = p

    plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False})
    xlow = min(x_train.min(), x_test.min()) - .06
    xhigh = max(x_train.max(), x_test.max()) + .06
    pred_all = np.concatenate(list(predictions.values()))
    low = min(-.3, float(pred_all.min()) - .15)
    high = max(float(test[:, 2].max()), float(pred_all.max())) + .3
    labels = ['Ajuste 1: cuadrático en ln(I645)', 'Ajuste 2: lineal en ln(I645)']
    equations = []
    for number, (key, title) in enumerate(zip(keys, labels), 1):
        coef = results[key]['coefficients_from_11']
        equation = f'C = {coef[0]:.6f} {coef[1]:+.6f} ln(I645)'
        if len(coef) == 3:
            equation += f' {coef[2]:+.6f} [ln(I645)]²'
        equations.append(equation)
        fig, axes = plt.subplots(1, 2, figsize=(13, 5.3), constrained_layout=True)
        xx = np.linspace(xlow, xhigh, 300)
        yy = np.polynomial.polynomial.polyval(xx, coef)
        ax = axes[0]
        ax.axvspan(xmin, xmax, color='#e8f1f8', zorder=0, label='Intervalo I645 de calibración')
        ax.plot(xx, yy, '--', color='#354651', lw=1.7, label='Ecuación extrapolada')
        xx_inside = np.linspace(xmin, xmax, 100)
        ax.plot(xx_inside, np.polynomial.polynomial.polyval(xx_inside, coef), color='#354651', lw=2.5,
                label='Ecuación calibrada con 11')
        ax.scatter(x_test, test[:, 2], s=30, color='#2675b8', alpha=.8, label='85 muestras', zorder=3)
        ax.scatter(x_train, train[:, 2], s=45, marker='D', color='#d97821',
                   edgecolor='white', lw=.5, label='11 de calibración', zorder=4)
        ax.set(xlabel='ln(I645)', ylabel='Chl(a) de referencia (µg/mL)',
               title='Datos sobre la relación original', xlim=(xlow, xhigh), ylim=(low, high))
        ax.legend(fontsize=8, loc='upper right')
        ax = axes[1]
        ax.plot([low, high], [low, high], '--', color='#777777', lw=1.4, label='Predicción ideal')
        ax.scatter(test[:, 2], predictions[key], s=33, color='#2675b8', alpha=.8, label='85 predicciones')
        ax.set(xlabel='Chl(a) de referencia (µg/mL)', ylabel='Chl(a) predicha (µg/mL)',
               title='Aplicación sin reajuste a las 85', xlim=(low, high), ylim=(low, high))
        ax.set_aspect('equal', adjustable='box')
        m = results[key]['all_85']
        ax.text(.04, .96, f"R² predictivo = {m['r2_predictive']:.4f}\nRMSE = {m['rmse_ug_ml']:.3f} µg/mL\nSesgo = {m['bias_ug_ml']:+.3f} µg/mL",
                transform=ax.transAxes, va='top', bbox={'facecolor': 'white', 'edgecolor': '#dddddd', 'alpha': .95})
        ax.legend(loc='lower right', fontsize=8)
        for ax in axes:
            ax.grid(alpha=.16)
        fig.suptitle(f'{title}\n{equation}     (sin blanco)', fontsize=13)
        fig.savefig(OUT / f'ajuste_{number}_85.png', dpi=180)
        plt.close(fig)

    with (OUT / 'predicciones_85.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['excel_row', 'sample', 'reference_ug_ml', 'I645', 'within_training_I645_range',
                         'prediction_model1_ug_ml', 'error_model1_ug_ml', 'prediction_model2_ug_ml', 'error_model2_ug_ml'])
        for i, row in enumerate(test):
            p1, p2 = predictions[keys[0]][i], predictions[keys[1]][i]
            writer.writerow([int(row[0]), int(row[1]), row[2], row[3], bool(in_signal_range[i]), p1, p1-row[2], p2, p2-row[2]])
    summary = {'method': 'Frozen equations fitted previously on all 11; apply to 85 without fitting or blank.',
               'source_sha256': hashes, 'training_concentration_range_ug_ml': [float(train[:, 2].min()), float(train[:, 2].max())],
               'test_concentration_range_ug_ml': [float(test[:, 2].min()), float(test[:, 2].max())],
               'within_training_I645_range_n': int(in_signal_range.sum()),
               'outside_training_I645_range_n': int((~in_signal_range).sum()),
               'within_training_concentration_range_n': int(in_concentration_range.sum()), 'models': results}
    (OUT / 'resultados_85.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n')
    report = ['# Modelos 1 y 2 aplicados a las 85 muestras', '',
              'Coeficientes tomados del análisis exclusivo de las once muestras. No se vuelve a calibrar, no se usa blanco y no se abre el conjunto de nueve.',
              'Las métricas siguientes corresponden a las 85 predicciones externas. No son validación cruzada ni un reajuste sobre las 85.', '',
              '| Modelo | Ecuación (C en µg/mL) | R² predictivo en 85 | RMSE (µg/mL) | MAE (µg/mL) | Sesgo (µg/mL) | Error máximo (µg/mL) |',
              '|---|---|---|---|---|---|---|']
    for key, label, equation in zip(keys, labels, equations):
        m = results[key]['all_85']
        report.append(f"| {label} | {equation} | {m['r2_predictive']:.6f} | {m['rmse_ug_ml']:.6f} | {m['mae_ug_ml']:.6f} | {m['bias_ug_ml']:+.6f} | {m['max_abs_error_ug_ml']:.6f} |")
    report += ['', 'R² predictivo = 1 − Σ(predicción − referencia)² / Σ(referencia − media de referencia)². Sesgo = media(predicción − referencia). Se conservan las 85 muestras y las predicciones negativas.',
               '', '## Alcance',
               f"La calibración cubre {train[:, 2].min():.5f}–{train[:, 2].max():.5f} µg/mL y las 85 cubren {test[:, 2].min():.5f}–{test[:, 2].max():.5f} µg/mL. {int((~in_signal_range).sum())} de las 85 tienen I645 fuera del intervalo usado para calibrar. La línea discontinua muestra esa extrapolación; la zona sombreada indica el intervalo de señal de las once.",
               'El desempeño anterior de CV sobre once corresponde a una sola tanda y a un rango menor. Estas cifras describen la transferencia a otra tanda y otro rango, y no sustituyen aquel resultado.',
               'Se leen las 85 filas completas. Las filas adicionales que solo contienen identificadores no son mediciones y se excluyen. No se eliminan atípicos, no se usan desviaciones instrumentales como pesos y no se recortan resultados.',
               '', '## Archivos', 'ajuste_1_85.png y ajuste_2_85.png muestran los datos sobre cada curva y las predicciones frente a la referencia. predicciones_85.csv contiene las 85 predicciones de ambos modelos. resultados_85.json conserva las métricas y la procedencia.']
    (OUT / 'informe.md').write_text('\n'.join(report) + '\n', encoding='utf-8')
    assert hashes == {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCES}
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
