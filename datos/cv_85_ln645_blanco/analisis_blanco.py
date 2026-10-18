"""Session-blank normalization of ln645: train/CV85, then frozen transfer to 9/11."""
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
sys.path.insert(0, str(DATA/'cv_85_ln645'))
from analisis_85 import load, fit, errors, BINS, LABELS, ROLES, markdown_table

# Fixed session means supplied by Alex, not optimized against reference concentrations.
BLANKS = {'85': 1356.0, '9': 1214.0, '11': 1256.0}
VARIANTS = {'sin_blanco': 'Sin blanco', 'con_blanco': 'Con blanco de sesión'}
COLORS = {'sin_blanco': '#d66c1d', 'con_blanco': '#2675b8'}


def feature(intensity, blank):
    intensity = np.asarray(intensity, dtype=float)
    if not np.isfinite(blank) or blank <= 0 or not np.isfinite(intensity).all() or (intensity <= 0).any():
        raise ValueError('Blank and I645 must be finite and strictly positive.')
    return np.log(blank/intensity)


def write_csv(name, rows):
    with (OUT/name).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    train, path, digest = load('85')
    y, z = train[:, 2], feature(train[:, 3], BLANKS['85'])
    alpha, beta = map(float, fit(z, y))
    previous = json.loads((DATA/'cv_85_ln645/modelo_85_fijado.json').read_text())
    a, b = previous['intercept'], previous['slope_lnI645']
    assert previous['training_sha256'] == digest
    assert np.allclose([alpha, beta], [a+b*np.log(BLANKS['85']), -b], atol=1e-10)
    cv, folds = np.full(len(y), np.nan), []
    for i in range(len(y)):
        keep = np.arange(len(y)) != i
        assert keep.sum() == 84 and not keep[i]
        aa, bb = fit(z[keep], y[keep])
        cv[i] = aa+bb*z[i]
        folds.append({'held_out_sample': int(train[i, 0]), 'training_n': 84,
                      'intercept': float(aa), 'slope_ln_blank_over_I645': float(bb)})
    full = alpha+beta*z
    h = 1/len(y)+(z-z.mean())**2/np.sum((z-z.mean())**2)
    assert np.allclose(cv, y-(y-full)/(1-h), atol=1e-10)
    with (DATA/'cv_85_ln645/predicciones.csv').open(encoding='utf-8-sig', newline='') as f:
        old_cv = np.array([float(r['prediction_ug_ml']) for r in csv.DictReader(f) if r['dataset'] == '85'])
    assert old_cv.shape == cv.shape and np.allclose(cv, old_cv, atol=1e-10)
    for invalid_i, invalid_b in [([0], 1), ([-1], 1), ([np.nan], 1), ([1], 0), ([1], np.inf)]:
        try:
            feature(invalid_i, invalid_b)
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid signal was accepted')

    model = {'equation': 'C_ug_ml = intercept + slope_ln_blank_over_I645 * ln(B645_session/I645)',
             'intercept': alpha, 'slope_ln_blank_over_I645': beta, 'fit_n': 85,
             'training_source': str(path), 'training_sha256': digest,
             'session_blanks_I645': BLANKS, 'blank_source': 'Session means provided by Alex; no repeat data supplied',
             'training_concentration_range_ug_ml': [float(y.min()), float(y.max())],
             'training_feature_range': [float(z.min()), float(z.max())],
             'baseline_equation': previous,
             'purpose': 'Fit on 85 only. Separate 84-point fits for CV85. No concentration-based correction using 9/11.'}
    # Freeze coefficients before reading either comparison workbook.
    (OUT/'modelo_85_fijado.json').write_text(json.dumps(model, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    snapshot = alpha, beta
    loaded = {'85': (train, path, digest)}
    predictions = {'85': {'sin_blanco': old_cv, 'con_blanco': cv}}
    for group in ('9', '11'):
        loaded[group] = load(group)
        intensity = loaded[group][0][:, 3]
        raw = a+b*np.log(intensity)
        corrected = alpha+beta*feature(intensity, BLANKS[group])
        shift = b*np.log(BLANKS['85']/BLANKS[group])
        assert np.allclose(corrected, raw+shift, atol=1e-10)
        assert np.allclose(corrected, a+b*np.log(intensity*BLANKS['85']/BLANKS[group]), atol=1e-10)
        predictions[group] = {'sin_blanco': raw, 'con_blanco': corrected}
    assert (alpha, beta) == snapshot

    global_rows, ranges, low_high, points = [], [], [], []
    for group, (data, source, source_hash) in loaded.items():
        yy = data[:, 2]
        for variant, pp in predictions[group].items():
            identity = {'dataset': group, 'evaluation': ROLES[group], 'variant': variant}
            score = errors(yy, pp)
            global_rows.append({**identity, **score, 'r2_predictive': float(1-np.sum((pp-yy)**2)/np.sum((yy-yy.mean())**2))})
            seen = np.zeros(len(yy), dtype=int)
            for j, (left, right, label) in enumerate(zip(BINS[:-1], BINS[1:], LABELS)):
                mask = (yy >= left) & ((yy <= right) if j == len(LABELS)-1 else (yy < right))
                seen += mask
                ranges.append({**identity, 'range_ug_ml': label, 'lower_ug_ml': left, 'upper_ug_ml': right,
                               'upper_inclusive': j == len(LABELS)-1, **errors(yy[mask], pp[mask])})
            assert np.all(seen == 1)
            rr = [r for r in ranges if r['dataset'] == group and r['variant'] == variant and r['n']]
            assert np.isclose(sum(r['n']*r['mae_ug_ml'] for r in rr)/len(yy), score['mae_ug_ml'])
            assert np.isclose(sum(r['n']*r['rmse_ug_ml']**2 for r in rr)/len(yy), score['rmse_ug_ml']**2)
            for label, mask in [('<1', yy < 1), ('>=1', yy >= 1)]:
                low_high.append({**identity, 'range_ug_ml': label, **errors(yy[mask], pp[mask])})
        for i, row in enumerate(data):
            raw, corrected = (predictions[group][v][i] for v in VARIANTS)
            points.append({'dataset': group, 'evaluation': ROLES[group], 'source': source.name,
                           'sample': int(row[0]), 'excel_row': int(row[1]), 'reference_ug_ml': row[2],
                           'I645': row[3], 'B645_session': BLANKS[group],
                           'ln_blank_over_I645': float(feature(row[3], BLANKS[group])),
                           'prediction_without_blank_ug_ml': raw, 'prediction_with_blank_ug_ml': corrected,
                           'error_without_blank_ug_ml': raw-row[2], 'error_with_blank_ug_ml': corrected-row[2]})
        assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
    write_csv('comparacion_global.csv', global_rows)
    write_csv('errores_por_rango.csv', ranges)
    write_csv('errores_menor_y_mayor_1.csv', low_high)
    write_csv('predicciones.csv', points)
    result = {'model': model, 'global_metrics': global_rows, 'ranges': ranges, 'below_above_1': low_high,
              'cv85_folds': folds, 'source_sha256': {g: d[2] for g, d in loaded.items()},
              'range_definition': 'Reference concentration; lower inclusive, upper exclusive except final 5–8 bin.'}
    (OUT/'resultados.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(2, 2, figsize=(12, 9), constrained_layout=True)
    for col, group in enumerate(('9', '11')):
        yy = loaded[group][0][:, 2]
        ax, residual = axes[0, col], axes[1, col]
        limits = (-.1, max(yy.max(), max(p.max() for p in predictions[group].values()))+.25)
        ax.plot(limits, limits, '--', color='#777777', label='Predicción ideal')
        residual.axhline(0, ls='--', color='#777777')
        for variant, pp in predictions[group].items():
            m = next(r for r in global_rows if r['dataset'] == group and r['variant'] == variant)
            label = f"{VARIANTS[variant]} · RMSE {m['rmse_ug_ml']:.3f}"
            ax.scatter(yy, pp, s=42, color=COLORS[variant], label=label, alpha=.85)
            residual.scatter(yy, pp-yy, s=42, color=COLORS[variant], label=VARIANTS[variant], alpha=.85)
        ax.set(xlabel='Referencia (µg/mL)', ylabel='Predicción (µg/mL)', title=f'{group} muestras · B645 = {BLANKS[group]:.0f}',
               xlim=limits, ylim=limits)
        ax.set_aspect('equal', adjustable='box')
        residual.set(xlabel='Referencia (µg/mL)', ylabel='Predicción − referencia (µg/mL)', title='Error antes y después de normalizar')
        for panel in (ax, residual):
            panel.legend(fontsize=8)
            panel.grid(alpha=.15)
    fig.suptitle('Calibración solo con 85 · blanco de sesión fijo · sin reajuste con 9 ni 11', fontsize=13)
    fig.savefig(OUT/'01_comparacion_9_y_11.png', dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(3, 2, figsize=(14, 10), constrained_layout=True)
    positions = np.arange(len(LABELS))
    for row, group in enumerate(('85', '9', '11')):
        for col, metric in enumerate(('mae_ug_ml', 'mape_percent')):
            ax = axes[row, col]
            for shift, variant in enumerate(VARIANTS):
                rr = [r for r in ranges if r['dataset'] == group and r['variant'] == variant]
                heights = [r[metric] if r['n'] else np.nan for r in rr]
                ax.bar(positions+(shift-.5)*.36, heights, width=.35, color=COLORS[variant], label=VARIANTS[variant])
            for pos, r in zip(positions, rr):
                if r['n']:
                    height = max(s[metric] for s in ranges if s['dataset'] == group and s['range_ug_ml'] == r['range_ug_ml'])
                    ax.annotate(f"n={r['n']}", (pos, height), xytext=(0, 4), textcoords='offset points', ha='center', fontsize=8)
            ax.set(title=f"{'CV85' if group == '85' else group+' muestras, ecuación fija'} · {'MAE' if col == 0 else 'MAPE'}",
                   ylabel='µg/mL' if col == 0 else '%')
            ax.set_xticks(positions, LABELS, rotation=25, ha='right')
            ax.set_axisbelow(True)
            ax.grid(axis='y', alpha=.15)
            ax.margins(y=.22)
            ax.legend(fontsize=8)
    fig.suptitle('Errores por concentración de referencia · intervalos vacíos sin barra', fontsize=13)
    fig.savefig(OUT/'02_errores_por_rango.png', dpi=180)
    plt.close(fig)

    def table(rows, range_table=False):
        headers = ['Grupo', 'Modelo']+(['Rango (µg/mL)'] if range_table else [])+['n', 'RMSE', 'MAE', 'Sesgo', 'MAPE (%)']
        values = [[r['dataset'], VARIANTS[r['variant']]]+([r['range_ug_ml']] if range_table else [])+
                  [r['n']]+[f"{r[k]:.5f}" if r[k] is not None else '—' for k in ('rmse_ug_ml', 'mae_ug_ml', 'bias_ug_ml')]+
                  [f"{r['mape_percent']:.2f}" if r['mape_percent'] is not None else '—'] for r in rows]
        return markdown_table(headers, values)

    report = ['# Calibración ln645 con blanco de sesión: CV85 y transferencia a 9 y 11', '',
              'Fecha: 18 de octubre de 2026. Continuación autorizada por Alex para incorporar el blanco; los análisis anteriores se conservan.', '',
              '## Resultado principal',
              'El blanco mejora mucho las nueve, pero empeora las once. Por tanto, no puede presentarse como una corrección universal entre tandas. En las 85, normalizar con un único blanco constante no cambia ninguna predicción de CV: solo cambia cómo se escribe la ecuación.', '',
              '## Ecuación y blancos', f'**C (µg/mL) = {alpha:.10f} + {beta:.10f} × ln(B645 / I645).**',
              'I645 es la intensidad media de la muestra y B645 el blanco de su sesión, en las mismas unidades instrumentales y configuración. ln es el logaritmo natural. Se usa cociente, no resta I−B. Ambos valores deben ser positivos y finitos.',
              'Blancos de sesión proporcionados por Alex: 85 → 1356; 9 → 1214; 11 → 1256. No se estiman ni optimizan con las concentraciones de las nueve o las once.',
              'Equivalencia: I equivalente = I645 × 1356/B645; se aplica a esta señal la ecuación sin blanco C = 20,4410723055 − 2,8428103277 × ln(I equivalente). La corrección resultante es un desplazamiento constante por sesión: nueve −0,3144674054 µg/mL; once −0,2177795161 µg/mL.',
              'Cuando I645 = B645, esta ecuación devuelve −0,0621128959 µg/mL, no cero. No se ha forzado el paso por el blanco ni recortado valores negativos: eso sería otro modelo y requeriría evaluarlo por separado.', '',
              '## Separación entre calibración y comprobaciones',
              'Los dos coeficientes se ajustan solo con las 85 muestras completas. CV85 deja una fuera cada vez: 85 entrenamientos de 84 muestras. Se verifica la CV con la identidad de residuos eliminados de regresión lineal y contra las 85 predicciones sin blanco ya guardadas.',
              'La ecuación completa de las 85 se guarda antes de abrir los Excel de nueve y once. Después se aplica fija a ambos, con sus blancos de sesión. No se añade offset ni pendiente aprendida de sus concentraciones. Esas 20 predicciones no son CV9/CV11.',
              'Como las tandas ya se han explorado y la normalización se evalúa después de observar diferencias, esta comparación es retrospectiva, no validación prospectiva ciega. Las nueve son diluciones de un mismo extracto, no nueve extractos independientes.', '',
              '## Errores globales', table(global_rows),
              'RMSE, MAE y sesgo están en µg/mL. Sesgo = promedio(predicción − referencia); MAPE = promedio(|predicción − referencia|/referencia) × 100. R² predictivo, error máximo y recuentos de negativos se incluyen en comparacion_global.csv. No se combinan los tres grupos en una única cifra.', '',
              '## Por debajo y por encima de 1 µg/mL', table(low_high, True), '',
              '## Errores por intervalos fijos',
              'Se conservan los intervalos del análisis anterior, definidos según la referencia. Extremo inferior incluido y superior excluido, excepto el último que incluye 8. — significa que no hay muestras, no error cero. n=1 no permite caracterizar la variabilidad de ese rango. MAPE es muy sensible a referencias pequeñas y no es una incertidumbre ni un error máximo garantizado.']
    for group in ('85', '9', '11'):
        report += ['', f'### Grupo {group}', table([r for r in ranges if r['dataset'] == group], True)]
    report += ['', '## Gráficas', '![Antes/después en nueve y once](01_comparacion_9_y_11.png)',
               '![Errores por intervalo](02_errores_por_rango.png)', '', '## Interpretación y límites',
               'En las nueve, la corrección elimina gran parte de la sobreestimación. En las once, donde la predicción sin blanco ya tenía sesgo negativo, desplazarla hacia abajo agrava el error. Los blancos no explican por sí solos todas las diferencias entre estas tandas; estos datos no identifican la causa restante.',
               'El ajuste con ln(B/I) presupone que el blanco sirve para normalizar una variación multiplicativa de la intensidad. Esta comparación prueba su resultado empírico, no demuestra ese mecanismo. La CV85 no valida dicha hipótesis entre sesiones, porque usa el mismo blanco constante en todos sus turnos.',
               'No se dispone de réplicas del blanco para propagar su incertidumbre. Tampoco se establece LOD/LOQ, capacidad en lagos, incertidumbre total o exactitud en sesiones nuevas. Se conserva todo punto completo sin eliminar atípicos ni ponderar por las desviaciones proporcionadas.',
               'No se han cambiado el firmware, la fórmula del equipo ni los .bin. Este es un análisis comparativo, no una nueva calibración desplegada. articulo.md y el ZIP para Daniela son de etapas anteriores y no se han modificado.', '',
               '## Procedencia y reproducibilidad',
               'Fuentes: calibracion_85_puntos (1).xlsx, Sheet1 A1:D86; 9Samples.xlsx, Sheet1 A1:AL10; 11Samples.xlsx, Sheet1 A1:AL12. Se usan identificador, concentración de referencia e I645. Las filas adicionales con solo identificador en el primer libro no son mediciones. Los tres originales se verifican por SHA-256 y no se modifican.',
               'modelo_85_fijado.json guarda la ecuación y blancos; resultados.json incluye métricas, procedencia y coeficientes de los 85 turnos; predicciones.csv contiene 105 filas con ambas predicciones; comparacion_global.csv tiene 6 evaluaciones; errores_por_rango.csv contiene 48 filas, incluidos intervalos vacíos; errores_menor_y_mayor_1.csv tiene 12 filas.',
               'analisis_blanco.py reproduce el análisis con numpy, openpyxl y matplotlib, reutilizando las funciones de lectura y métricas de la etapa sin blanco. Las comprobaciones verifican entradas, equivalencia algebraica, CV sin fuga del punto omitido, cobertura de rangos, agregación de errores y conservación de originales.']
    (OUT/'informe.md').write_text('\n'.join(report)+'\n', encoding='utf-8')
    print(json.dumps({'model': {'alpha': alpha, 'beta': beta}, 'global': global_rows, 'low_high': low_high,
                      'checks': 'passed; originals unchanged'}, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
