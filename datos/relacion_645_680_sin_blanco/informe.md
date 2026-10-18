# Relación 645/680 sin blanco

> Informe histórico de exploración. La decisión vigente es 85 → 9 con blanco; consultar [articulo.md](../articulo.md). Este informe conserva sus resultados originales y no es la guía actual del manuscrito.

Fecha: 18 de octubre de 2026.

## Resultado
**C (µg/mL) = -2.21412414 + 9.92830753 × √(I680/I645).**
Los dos coeficientes se ajustaron exclusivamente con las 11 muestras. Se aplica la misma ecuación a las nueve diluciones, sin recalibrar, cambiar la escala, restar fondo, usar blancos o limitar las predicciones a cero.
Se adopta la raíz del cociente por su sencillez (dos coeficientes) y su transferencia razonable en ambos sentidos. La forma funcional se eligió después de explorar ambas tandas: la segunda tanda es una comprobación de transferencia exploratoria, no una validación ciega de una ecuación fijada previamente.

## Errores y ajuste
| Calibración | Evaluación | n | R² predictivo/ajuste | RMSE (µg/mL) | MAE (µg/mL) | Sesgo (µg/mL) | Error máximo (µg/mL) |
|---|---|---|---|---|---|---|---|
| 11 | calibration_fit | 11 | 0.99760 | 0.03624 | 0.02836 | -0.00000 | 0.08592 |
| 11 | within_batch_LOOCV | 11 | 0.99666 | 0.04270 | 0.03440 | -0.00166 | 0.09667 |
| 11 | transfer_check_exploratory | 9 | 0.99060 | 0.11809 | 0.09044 | +0.08211 | 0.22014 |
| 9 | calibration_fit | 9 | 0.99720 | 0.06440 | 0.05363 | +0.00000 | 0.12138 |
| 9 | within_batch_LOOCV | 9 | 0.99619 | 0.07518 | 0.06315 | -0.00170 | 0.13745 |
| 9 | transfer_check_exploratory | 11 | 0.97136 | 0.12504 | 0.11530 | -0.11530 | 0.19206 |

RMSE es la raíz del error cuadrático medio. MAE es el error absoluto medio. El sesgo usa predicción menos referencia. R² compara las predicciones con la identidad predicho=referencia, no es solo el cuadrado de una correlación.

## Las nueve diluciones predichas con la ecuación de las 11
| ID | Referencia (µg/mL) | Predicción (µg/mL) | Error (µg/mL) |
|---|---|---|---|
| 1 | 0.0244 | 0.0489 | +0.0245 |
| 2 | 0.0489 | 0.0261 | -0.0228 |
| 3 | 0.0977 | 0.0831 | -0.0146 |
| 4 | 0.1955 | 0.2295 | +0.0340 |
| 5 | 0.2932 | 0.4032 | +0.1100 |
| 6 | 0.4887 | 0.6796 | +0.1909 |
| 7 | 0.9775 | 1.1335 | +0.1560 |
| 8 | 1.9549 | 1.9959 | +0.0410 |
| 9 | 3.9098 | 4.1299 | +0.2201 |


## Comparación de relaciones exploradas
Todas las opciones usan exclusivamente 645/680; ln(I645) se conserva como control de un solo canal. Cada ajuste usa únicamente la tanda indicada como calibración. Las columnas de comprobación no se usaron para ajustar coeficientes, pero sí se consultaron para escoger la forma funcional.
| Relación | Calibración | Comprobación | R² | RMSE (µg/mL) | Error máximo (µg/mL) |
|---|---|---|---|---|---|
| raw_pair | 11 | 9 | 0.14102 | 1.12857 | 1.95955 |
| log_pair | 11 | 9 | 0.82998 | 0.50210 | 1.02815 |
| ratio | 11 | 9 | 0.90833 | 0.36868 | 0.78830 |
| log_ratio | 11 | 9 | 0.94199 | 0.29328 | 0.47548 |
| ND | 11 | 9 | 0.97025 | 0.21003 | 0.36411 |
| log645_plus_680 | 11 | 9 | 0.79838 | 0.54677 | 1.17032 |
| 645_plus_log680 | 11 | 9 | 0.39070 | 0.95049 | 1.40911 |
| log645_baseline | 11 | 9 | 0.88934 | 0.40507 | 0.81687 |
| ratio_quadratic | 11 | 9 | 0.98301 | 0.15874 | 0.22549 |
| log_ratio_quadratic | 11 | 9 | 0.97849 | 0.17861 | 0.23926 |
| sqrt_ratio | 11 | 9 | 0.99060 | 0.11809 | 0.22014 |
| log_contrast | 11 | 9 | 0.90816 | 0.36902 | 0.58337 |
| ratio_plus_logratio | 11 | 9 | 0.98194 | 0.16364 | 0.39122 |
| raw_pair | 9 | 11 | -102.91009 | 7.53238 | 10.43935 |
| log_pair | 9 | 11 | 0.16941 | 0.67344 | 0.89842 |
| ratio | 9 | 11 | 0.75280 | 0.36739 | 0.47437 |
| log_ratio | 9 | 11 | 0.96603 | 0.13618 | 0.20139 |
| ND | 9 | 11 | 0.91666 | 0.21332 | 0.27201 |
| log645_plus_680 | 9 | 11 | -0.11867 | 0.78155 | 1.09473 |
| 645_plus_log680 | 9 | 11 | -8.01491 | 2.21863 | 2.59610 |
| log645_baseline | 9 | 11 | 0.66961 | 0.42473 | 0.63847 |
| ratio_quadratic | 9 | 11 | 0.97924 | 0.10647 | 0.17462 |
| log_ratio_quadratic | 9 | 11 | 0.96548 | 0.13728 | 0.17918 |
| sqrt_ratio | 9 | 11 | 0.97136 | 0.12504 | 0.19206 |
| log_contrast | 9 | 11 | 0.93905 | 0.18243 | 0.25716 |
| ratio_plus_logratio | 9 | 11 | 0.95071 | 0.16405 | 0.24802 |

Definiciones: ratio=I680/I645; log_ratio=ln(ratio); ND=(I680−I645)/(I680+I645); sqrt_ratio=√ratio. Los modelos pair ajustan intercepto y ambos canales o sus logaritmos; quadratic agrega el cuadrado de la variable; ratio_plus_logratio combina ratio y ln(ratio); log_contrast=ln(I680/(I645+I680)).

## Alcance
- La calibración de 11 cubre 0,7944–3,07062 µg/mL. La comprobación de nueve cubre 0,0244–3,9098 µg/mL, con extrapolación a ambos extremos. No hay muestra cero medida.
- El intervalo observado del cociente en ambas tandas es aproximadamente 0,051–0,408. No se establece validez fuera de él. Para usar la ecuación se requieren intensidades positivas, ganancia/integración y montaje comparables.
- El cociente puede cancelar cambios que multipliquen ambos canales por el mismo factor. No corrige automáticamente fondos aditivos ni cambios diferentes entre canales. La raíz es una transformación empírica y no se presenta como ley física.
- El error absoluto del modelo debe considerarse cerca de concentraciones bajas. Un R² alto no acredita precisión relativa alta cerca de cero ni establece un límite de detección.
- Las nueve diluciones comparten un extracto madre. Una nueva sesión o un nuevo extracto permitirán comprobar la fórmula ya fijada sin volver a escogerla.
- Los canales saturados 410/435 y sus datos no participan. Se reconoce que el sensor lleva filtros espectrales incorporados. El análisis no exige modificar la óptica ni medir blanco por muestra; no usa ningún blanco, ni siquiera el de sesión.
- Las concentraciones se toman de los Excel como referencia suministrada. Los archivos no permiten auditar las absorbancias ni factores de dilución. El firmware no se ha modificado.

## Archivos
La figura muestra la relación y los errores de transferencia. Los CSV contienen las predicciones por muestra en ambos sentidos y la comparación completa. Los hashes SHA-256 de los originales y los coeficientes completos quedan en resultados.json.

Fuentes: 11Samples.xlsx y 9Samples.xlsx, Sheet1. B=concentración, U=I645, W=I680.
