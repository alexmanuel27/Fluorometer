"""Compare concentration prediction using a fixed 680-nm saturation model.

Leave out each sample (all its replicates), fit forward on 19 sample means,
then invert for the held-out sample. Session blanks remain shared.
Requires numpy and scipy. Run analizar.py first.
"""
from pathlib import Path
import csv
import json
import numpy as np
from scipy.optimize import curve_fit

root = Path(__file__).resolve().parent / 'resultados'
rows = list(csv.DictReader((root / 'datos_integrados.csv').open()))
summary = []

def saturation(c, amplitude, k):
    return amplitude * (-np.expm1(-k * c))

for geometry in ['180°', '90°']:
    r = sorted((x for x in rows if x['geometria'] == geometry and x['nm'] == '680'), key=lambda x: int(x['muestra']))
    c = np.array([float(x['Chla_ug_mL']) for x in r])
    y = np.array([float(x['incremento_sobre_blanco']) for x in r])
    predictions = []
    for i in range(len(c)):
        keep = np.arange(len(c)) != i
        p, _ = curve_fit(saturation, c[keep], y[keep], p0=[150, .4], bounds=([0, 0], [1e6, 10]), maxfev=20000)
        if not 0 < y[i] < p[0]:
            raise ValueError(f'Cannot invert held-out sample {i+1} at {geometry}')
        predictions.append(-np.log1p(-y[i] / p[0]) / p[1])
    predictions = np.array(predictions)
    error = predictions - c
    summary.append(dict(geometria=geometry, RMSE_ug_mL=float(np.sqrt(np.mean(error**2))), MAE_ug_mL=float(np.mean(abs(error))), sesgo_ug_mL=float(np.mean(error)), max_error_ug_mL=float(np.max(abs(error)))))
    with (root / f'prediccion_concentracion_{geometry}.csv').open('w') as f:
        writer = csv.writer(f)
        writer.writerow(['muestra', 'referencia_ug_mL', 'prediccion_LOO_ug_mL', 'error_ug_mL'])
        writer.writerows(zip(range(1, len(c)+1), c, predictions, error))
(root / 'comparacion_concentracion.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False))
print(json.dumps(summary, indent=2, ensure_ascii=False))
