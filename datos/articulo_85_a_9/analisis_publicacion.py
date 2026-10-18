"""Selected manuscript analysis: fit/CV85 and fixed transfer to 9 with session blanks.

Self-contained: numpy, openpyxl, matplotlib. Does not open the 11-sample workbook.
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
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent
DATA = OUT.parent
FIGURES = OUT/'figuras'
SOURCES = {'85': 'calibracion_85_puntos (1).xlsx', '9': '9Samples.xlsx'}
BLANKS = {'85': 1356.0, '9': 1214.0}
HASHES = {'85': '2fde9fbda48ce1ad920386fdc754a0181fc80f09944e3a4ca91569b01490e4e8',
          '9': 'd2f13be46fa8b396155f44a8f9bc08c27b6d141eaa5950b29883d78062696000'}
BINS = [0, .1, .25, .5, 1, 2, 3, 5, 8]
LABELS = ['0–<0.1', '0.1–<0.25', '0.25–<0.5', '0.5–<1', '1–<2', '2–<3', '3–<5', '5–8']
BLUE, ORANGE, GREY = '#2369a3', '#c96c24', '#656565'


def load(group):
    path = DATA/SOURCES[group]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == HASHES[group]
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    assert wb.active.title == 'Sheet1'
    rows = list(wb.active.values)
    wb.close()
    ci, ii = rows[0].index('Chl(a) [µg/mL]'), rows[0].index('I(645)')
    values = np.array([[r[0], n, r[ci], r[ii]] for n, r in enumerate(rows[1:], 2)
                       if isinstance(r[ci], (int, float)) and isinstance(r[ii], (int, float))], dtype=float)
    assert values.shape == (int(group), 4) and np.isfinite(values).all()
    assert (values[:, 2:] > 0).all()
    return values


def feature(intensity, blank):
    intensity = np.asarray(intensity, dtype=float)
    if not np.isfinite(blank) or blank <= 0 or not np.isfinite(intensity).all() or (intensity <= 0).any():
        raise ValueError('I645 and session blank must be positive and finite')
    return np.log(blank/intensity)


def fit(x, y):
    return np.linalg.lstsq(np.c_[np.ones(len(x)), x], y, rcond=None)[0]


def metrics(y, p):
    if not len(y):
        return {'n': 0, **{k: None for k in ('r2', 'rmse', 'mae', 'bias', 'max_abs_error', 'mape_percent', 'negative_n')}}
    e = p-y
    variance = np.sum((y-y.mean())**2)
    return {'n': len(y), 'r2': float(1-np.sum(e**2)/variance) if variance > 0 else None,
            'rmse': float(np.sqrt(np.mean(e**2))), 'mae': float(np.mean(abs(e))),
            'bias': float(e.mean()), 'max_abs_error': float(max(abs(e))),
            'mape_percent': float(np.mean(abs(e)/y)*100), 'negative_n': int((p < 0).sum())}


def csv_output(name, rows):
    with (OUT/name).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def save_figure(fig, name):
    for extension in ('png', 'svg'):
        fig.savefig(FIGURES/f'{name}.{extension}', dpi=220)
    plt.close(fig)


def grid(ax):
    ax.grid(alpha=.15)
    ax.set_axisbelow(True)


def identity(ax, y, p):
    limits = (min(-.1, float(p.min())-.1), max(float(y.max()), float(p.max()))+.2)
    ax.plot(limits, limits, '--', color=GREY, lw=1.2)
    ax.set(xlim=limits, ylim=limits, xlabel='Reference Chl(a) (µg/mL)', ylabel='Predicted Chl(a) (µg/mL)')
    ax.set_aspect('equal', adjustable='box')
    grid(ax)


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)
    train = load('85')
    x, y = feature(train[:, 3], BLANKS['85']), train[:, 2]
    a, b = map(float, fit(x, y))
    slope = np.sum((x-x.mean())*(y-y.mean()))/np.sum((x-x.mean())**2)
    assert np.allclose([a, b], [y.mean()-slope*x.mean(), slope], atol=1e-10)
    cv, folds, cv_inside = np.full(85, np.nan), [], np.zeros(85, dtype=bool)
    for i in range(85):
        keep = np.arange(85) != i
        assert keep.sum() == 84 and not keep[i]
        aa, bb = fit(x[keep], y[keep])
        cv[i] = aa+bb*x[i]
        cv_inside[i] = x[keep].min() <= x[i] <= x[keep].max()
        folds.append({'sample': int(train[i, 0]), 'training_n': 84, 'intercept': float(aa), 'slope': float(bb)})
    leverage = 1/85+(x-x.mean())**2/np.sum((x-x.mean())**2)
    assert np.allclose(cv, y-(y-(a+b*x))/(1-leverage), atol=1e-10)
    model = {'calibration_id': 'ln645_blank_85_to_9_2026-10-18',
             'equation': 'Chl_a_ug_ml = intercept + slope * ln(B645_session/mean_I645)',
             'intercept': a, 'slope': b, 'training_n': 85, 'training_dataset': SOURCES['85'],
             'transfer_n': 9, 'transfer_dataset': SOURCES['9'], 'session_blanks_I645': BLANKS,
             'training_feature_range': [float(x.min()), float(x.max())],
             'training_concentration_range_ug_ml': [float(y.min()), float(y.max())],
             'source_sha256': HASHES, 'fit_method': 'Unweighted OLS with free intercept',
             'selection_status': 'Retrospective exploratory selection; not prospectively blind',
             'blank_source': 'Session means supplied by Alex; no blank replicate series available',
             'firmware_updated': False}
    (OUT/'modelo_final.json').write_text(json.dumps(model, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    test = load('9')
    xt, yt = feature(test[:, 3], BLANKS['9']), test[:, 2]
    p = a+b*xt
    # Control: the same 85-point calibration in the original intensity scale, no session correction.
    raw_intercept, raw_slope = a+b*np.log(BLANKS['85']), -b
    p_without_blank = raw_intercept+raw_slope*np.log(test[:, 3])
    assert np.allclose(p-p_without_blank, -b*np.log(BLANKS['85']/BLANKS['9']), atol=1e-10)
    assert np.allclose(p, raw_intercept+raw_slope*np.log(test[:, 3]*BLANKS['85']/BLANKS['9']), atol=1e-10)
    evaluated = {'85': (train, cv, cv_inside), '9': (test, p, (xt >= x.min()) & (xt <= x.max()))}
    global_metrics, low_high, ranges, predictions = [], [], [], []
    for group, (data, pp, inside) in evaluated.items():
        yy = data[:, 2]
        role = 'LOOCV85: fit 84, predict omitted sample' if group == '85' else '85-to-9 fixed transfer, not CV9'
        global_metrics.append({'dataset': group, 'evaluation': role, **metrics(yy, pp),
                               'outside_training_signal_n': int((~inside).sum())})
        for label, mask in [('<1', yy < 1), ('>=1', yy >= 1)]:
            range_score = metrics(yy[mask], pp[mask])
            range_score.pop('r2')
            low_high.append({'dataset': group, 'range_ug_ml': label, **range_score})
        coverage = np.zeros(len(data), dtype=int)
        for j, (left, right, label) in enumerate(zip(BINS[:-1], BINS[1:], LABELS)):
            mask = (yy >= left) & ((yy <= right) if j == len(LABELS)-1 else (yy < right))
            coverage += mask
            range_score = metrics(yy[mask], pp[mask])
            range_score.pop('r2')
            ranges.append({'dataset': group, 'range_ug_ml': label, 'lower_ug_ml': left, 'upper_ug_ml': right,
                           'upper_inclusive': j == len(LABELS)-1, **range_score})
        assert np.all(coverage == 1)
        nonempty = [r for r in ranges if r['dataset'] == group and r['n']]
        assert np.isclose(sum(r['n']*r['mae'] for r in nonempty)/len(yy), metrics(yy, pp)['mae'])
        assert np.isclose(sum(r['n']*r['rmse']**2 for r in nonempty)/len(yy), metrics(yy, pp)['rmse']**2)
        for i, row in enumerate(data):
            predictions.append({'dataset': group, 'evaluation': role, 'source': SOURCES[group],
                                'sample': int(row[0]), 'excel_row': int(row[1]), 'reference_ug_ml': row[2],
                                'I645': row[3], 'B645_session': BLANKS[group],
                                'ln_B645_over_I645': float(feature(row[3], BLANKS[group])),
                                'prediction_ug_ml': float(pp[i]), 'error_ug_ml': float(pp[i]-yy[i]),
                                'absolute_relative_error_percent': float(abs(pp[i]-yy[i])/yy[i]*100),
                                'inside_training_signal_range': bool(inside[i])})
    assert len(predictions) == 94 and len(ranges) == 16 and len(low_high) == 4
    blank_comparison = [{'variant': name, **metrics(yt, pred)} for name, pred in [('without_session_blank', p_without_blank), ('with_session_blank', p)]]
    csv_output('predicciones.csv', predictions)
    csv_output('tabla_resultados.csv', global_metrics)
    csv_output('errores_por_rango.csv', ranges)
    csv_output('errores_menor_y_mayor_1.csv', low_high)
    csv_output('comparacion_blanco_9.csv', blank_comparison)
    csv_output('predicciones_blanco_9.csv', [{'sample': int(test[i, 0]), 'reference_ug_ml': yt[i],
               'without_blank_ug_ml': p_without_blank[i], 'with_blank_ug_ml': p[i]} for i in range(9)])
    result = {'model': model, 'global_metrics': global_metrics, 'below_above_1': low_high, 'ranges': ranges,
              'blank_comparison_9': blank_comparison, 'cv85_folds': folds,
              'training_fit_for_curve_only_not_cv': metrics(y, a+b*x),
              'versions': {'python': sys.version.split()[0], 'numpy': np.__version__,
                           'openpyxl': openpyxl.__version__, 'matplotlib': matplotlib.__version__}}
    (OUT/'resultados.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.spines.top': False,
                         'axes.spines.right': False, 'svg.fonttype': 'none'})
    figures(train, test, x, y, xt, yt, a, b, cv, p, p_without_blank, global_metrics, low_high, ranges)
    for group, name in SOURCES.items():
        assert hashlib.sha256((DATA/name).read_bytes()).hexdigest() == HASHES[group]
    print(json.dumps({'equation': [a, b], 'global_metrics': global_metrics,
                      'below_above_1': low_high, 'figures': 6, 'checks': 'passed; only 85 and 9 used'}, indent=2))


def figures(train, test, x, y, xt, yt, a, b, cv, p, raw, scores, low_high, ranges):
    fig, ax = plt.subplots(figsize=(10.5, 5.2), constrained_layout=True)
    ax.set(xlim=(0, 10.5), ylim=(0, 5.2))
    ax.axis('off')
    def box(pos, size, title, body, color):
        xx, yy = pos
        width, height = size
        ax.add_patch(FancyBboxPatch(pos, width, height, boxstyle='round,pad=0.10',
                                   facecolor=color, edgecolor='#98a6b2', linewidth=1))
        ax.text(xx+width/2, yy+height-.30, title, ha='center', va='top', weight='bold', fontsize=11)
        ax.text(xx+width/2, yy+height/2-.15, body, ha='center', va='center', fontsize=10, linespacing=1.5)
    box((.2, 2.9), (3, 1.9), '85 calibration records', '0.02384–7.98964 µg/mL\nSession blank: 1356\nx = ln(B645 / mean I645)', '#e9f1f8')
    box((3.85, 2.9), (2.8, 1.9), 'Fit only on the 85', 'OLS: C = a + b x\nFreeze a and b\nNo dilution-point refit', '#e9f1f8')
    box((7.3, 2.9), (2.95, 1.9), 'Fixed transfer to 9', '0.0244–3.9098 µg/mL\nSession blank: 1214\nPredict without refitting', '#fbefe4')
    box((.4, .4), (5.8, 1.65), 'Internal assessment: LOOCV85', '85 folds: train on 84, predict the omitted record\nSeparate fold coefficients; not the full-fit predictions', '#f4f6f8')
    box((7.3, .4), (2.95, 1.65), 'One mother extract', '9 dilution points\nShared concentration reference\nNot 9 independent extracts', '#fbefe4')
    for start, end in [((3.3, 3.85), (3.75, 3.85)), ((6.75, 3.85), (7.2, 3.85)),
                       ((1.7, 2.8), (1.7, 2.15)), ((8.8, 2.8), (8.8, 2.15))]:
        ax.annotate('', xy=end, xytext=start, arrowprops={'arrowstyle': '->', 'color': GREY, 'lw': 1.5})
    save_figure(fig, 'figura_01_diseno')

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8), constrained_layout=True)
    cc = np.linspace(y.min(), y.max(), 250)
    axes[0].scatter(y, train[:, 3]/BLANKS['85'], s=25, color=BLUE, alpha=.8)
    axes[0].plot(cc, np.exp((a-cc)/b), color='#333333', label='Equivalent empirical curve')
    axes[0].set(xlabel='Reference Chl(a) (µg/mL)', ylabel='I645 / session blank', title='A  Normalized optical response')
    axes[0].legend(fontsize=9)
    xx = np.linspace(x.min(), x.max(), 200)
    axes[1].scatter(x, y, s=25, color=BLUE, alpha=.8, label='85 calibration records')
    axes[1].plot(xx, a+b*xx, color='#333333', label='Full 85-point fit, not CV')
    axes[1].set(xlabel='ln(B645 / I645)', ylabel='Reference Chl(a) (µg/mL)', title='B  Logarithmic calibration')
    axes[1].legend(fontsize=9)
    for ax in axes:
        grid(ax)
    fig.suptitle(f'C = {a:.6f} + {b:.6f} ln(B645 / I645)', fontsize=12)
    save_figure(fig, 'figura_02_calibracion')

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8), constrained_layout=True)
    identity(axes[0], y, cv)
    axes[0].scatter(y, cv, s=25, color=BLUE, alpha=.8)
    axes[0].set_title('A  LOOCV85 predictions')
    axes[0].text(.04, .96, f"R² = {scores[0]['r2']:.4f}\nRMSE = {scores[0]['rmse']:.4f} µg/mL\nMAE = {scores[0]['mae']:.4f} µg/mL",
                 transform=axes[0].transAxes, va='top', fontsize=9, bbox={'facecolor': 'white', 'edgecolor': '#dddddd'})
    axes[1].axhline(0, ls='--', color=GREY)
    axes[1].scatter(y, cv-y, s=25, color=BLUE, alpha=.8)
    for i in np.argsort(abs(cv-y))[-3:]:
        axes[1].annotate(str(int(train[i, 0])), (y[i], cv[i]-y[i]), xytext=(4, 4), textcoords='offset points', fontsize=8)
    axes[1].set(xlabel='Reference Chl(a) (µg/mL)', ylabel='CV prediction − reference (µg/mL)', title='B  Out-of-fold residuals')
    grid(axes[1])
    save_figure(fig, 'figura_03_cv85')

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8), constrained_layout=True)
    low = yt < 1
    lm = next(r for r in low_high if r['dataset'] == '9' and r['range_ug_ml'] == '<1')
    for ax, mask, title, annotation in [
            (axes[0], np.ones(9, dtype=bool), 'A  Fixed 85-to-9 transfer',
             f"n = 9; R² = {scores[1]['r2']:.4f}\nRMSE = {scores[1]['rmse']:.4f} µg/mL\nMAPE = {scores[1]['mape_percent']:.2f}%"),
            (axes[1], low, 'B  Low-concentration detail',
             f"n = 7; reference <1 µg/mL\nMAE = {lm['mae']:.4f} µg/mL\nMAPE = {lm['mape_percent']:.2f}%")]:
        identity(ax, yt[mask], p[mask])
        ax.scatter(yt[mask], p[mask], color=ORANGE, s=45)
        ax.set_title(title)
        ax.text(.04, .96, annotation, transform=ax.transAxes, va='top', fontsize=9,
                bbox={'facecolor': 'white', 'edgecolor': '#dddddd'})
    save_figure(fig, 'figura_04_transferencia9')

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8), constrained_layout=True)
    identity(axes[0], yt, np.r_[raw, p])
    for predicted, color, label in [(raw, GREY, 'Without session correction'), (p, ORANGE, 'With session blank')]:
        axes[0].scatter(yt, predicted, color=color, s=40, label=label, alpha=.85)
        axes[1].scatter(yt, predicted-yt, color=color, s=40, label=label, alpha=.85)
    axes[0].set_title('A  Same 85-point coefficients')
    axes[0].legend(fontsize=8, loc='lower right')
    axes[1].axhline(0, ls='--', color=GREY)
    axes[1].set(xlabel='Reference Chl(a) (µg/mL)', ylabel='Prediction − reference (µg/mL)', title='B  Effect of session normalization')
    axes[1].legend(fontsize=8)
    grid(axes[1])
    fig.suptitle(f'Session blanks 1356 → 1214: constant prediction shift {float((p-raw).mean()):+.4f} µg/mL', fontsize=11)
    save_figure(fig, 'figura_05_efecto_blanco')

    fig, axes = plt.subplots(2, 1, figsize=(11.5, 7.2), constrained_layout=True)
    positions = np.arange(len(LABELS))
    for shift, group, color, label in [(-.18, '85', BLUE, 'LOOCV85'), (.18, '9', ORANGE, '85-to-9 transfer')]:
        rr = [r for r in ranges if r['dataset'] == group]
        for ax, key in zip(axes, ('mae', 'mape_percent')):
            bars = ax.bar(positions+shift, [r[key] if r['n'] else np.nan for r in rr], width=.35, color=color, label=label)
            if key == 'mae':
                for bar, r in zip(bars, rr):
                    if r['n']:
                        ax.annotate(f"n={r['n']}", (bar.get_x()+bar.get_width()/2, bar.get_height()),
                                    xytext=(0, 4), textcoords='offset points', ha='center', fontsize=8)
    axes[0].set(ylabel='MAE (µg/mL)', title='A  Absolute error by reference-concentration range')
    axes[1].set(ylabel='MAPE (%)', xlabel='Reference Chl(a) range (µg/mL)', title='B  Relative error by reference-concentration range')
    for ax in axes:
        ax.set_xticks(positions, LABELS, rotation=20, ha='right')
        ax.legend(fontsize=9)
        ax.margins(y=.22)
        grid(ax)
    save_figure(fig, 'figura_06_errores_por_rango')


if __name__ == '__main__':
    main()
