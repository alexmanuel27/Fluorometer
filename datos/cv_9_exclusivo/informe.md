# Validación cruzada exclusivamente sobre las nueve muestras

Único Excel utilizado: 9Samples.xlsx, Sheet1, A1:AL10. No se leen los conjuntos de once ni de 85 ni sus resultados o coeficientes. Se reutilizan únicamente las definiciones matemáticas de los modelos y las funciones de ajuste.

## Método
Se comparan 55 candidatos sin blanco: lineal y logarítmico por cada canal válido, cocientes y sus transformaciones, diferencias normalizadas, modelos de dos predictores y PLS de 1–3 componentes con los 16 canales no saturados.
Cada modelo se entrena con ocho muestras y predice la omitida. Se repite nueve veces. Todas las métricas y puntos de las figuras usan esas nueve predicciones fuera del entrenamiento. PLS aprende centrado y escalado únicamente con las ocho muestras de cada turno.
R² CV9 = 1 − Σ(predicción − referencia)² / Σ(referencia − media de referencia)². No es R² de entrenamiento ni correlación al cuadrado. RMSE y MAE están en µg/mL.
Error relativo absoluto medio <1 = promedio de |predicción − referencia| / referencia × 100 en las siete referencias menores de 1 µg/mL. Ese subconjunto solo se usa para evaluar las mismas predicciones de CV9, no para recalibrar.
No se eliminan muestras, no se recortan predicciones negativas, no se fuerzan interceptos y no se usan desviaciones instrumentales como pesos. Los canales 410 y 435 se excluyen por saturación. Las variantes con blanco constante que solo cambian escala o intercepto no se duplican.

## Menor RMSE global
| Modelo | R² CV9 | RMSE CV9 (µg/mL) | MAE CV9 (µg/mL) | Error relativo medio <1 (%) | MAE <1 (µg/mL) | Error máximo CV9 (µg/mL) |
|---|---|---|---|---|---|---|
| sqrt(I680/I460) | 0.996388 | 0.073183 | 0.060536 | 46.85 | 0.061098 | 0.142355 |
| sqrt(I680/I645) | 0.996188 | 0.075185 | 0.063145 | 54.60 | 0.065742 | 0.137450 |
| ND(680,705) | 0.995095 | 0.085277 | 0.062118 | 27.99 | 0.034395 | 0.184140 |
| sqrt(I680/I860) | 0.994297 | 0.091960 | 0.082782 | 80.29 | 0.079130 | 0.143190 |
| ln(I460) | 0.993592 | 0.097474 | 0.080269 | 63.59 | 0.074656 | 0.181606 |
| ln(I900) | 0.990861 | 0.116409 | 0.097053 | 87.47 | 0.089179 | 0.234254 |
| ln(I585) | 0.990676 | 0.117581 | 0.098845 | 89.01 | 0.091069 | 0.233931 |
| ln(I560) | 0.990417 | 0.119201 | 0.099573 | 94.81 | 0.091601 | 0.238331 |
| sqrt(I680/I705) | 0.990041 | 0.121519 | 0.102064 | 95.36 | 0.094394 | 0.238656 |
| ln(I940) | 0.990038 | 0.121538 | 0.102035 | 97.58 | 0.093849 | 0.243815 |


## Menor error relativo en concentraciones inferiores a 1 µg/mL
| Modelo | R² CV9 | RMSE CV9 (µg/mL) | MAE CV9 (µg/mL) | Error relativo medio <1 (%) | MAE <1 (µg/mL) | Error máximo CV9 (µg/mL) |
|---|---|---|---|---|---|---|
| ln(I645) + ln(I680) | 0.963046 | 0.234080 | 0.123917 | 23.73 | 0.039264 | 0.669967 |
| ND(680,705) | 0.995095 | 0.085277 | 0.062118 | 27.99 | 0.034395 | 0.184140 |
| Quadratic I680/I645 | 0.717653 | 0.647033 | 0.263509 | 32.06 | 0.040854 | 1.930874 |
| ln(I645) + I680 | 0.898477 | 0.387987 | 0.189040 | 35.66 | 0.050199 | 1.133084 |
| Quadratic ln(I645) | 0.869152 | 0.440472 | 0.209685 | 37.74 | 0.053372 | 1.292197 |
| ND(680,645) | 0.973427 | 0.198498 | 0.111982 | 43.65 | 0.033342 | 0.533243 |
| sqrt(I680/I460) | 0.996388 | 0.073183 | 0.060536 | 46.85 | 0.061098 | 0.142355 |
| sqrt(I680/I645) | 0.996188 | 0.075185 | 0.063145 | 54.60 | 0.065742 | 0.137450 |
| ln(I460) | 0.993592 | 0.097474 | 0.080269 | 63.59 | 0.074656 | 0.181606 |
| sqrt(I680/I860) | 0.994297 | 0.091960 | 0.082782 | 80.29 | 0.079130 | 0.143190 |


## Formas comparables con los modelos anteriores, ahora calibradas solo con ocho por turno
| Modelo | R² CV9 | RMSE CV9 (µg/mL) | MAE CV9 (µg/mL) | Error relativo medio <1 (%) | MAE <1 (µg/mL) | Error máximo CV9 (µg/mL) |
|---|---|---|---|---|---|---|
| ln(I645) | 0.988918 | 0.128188 | 0.104704 | 96.07 | 0.095443 | 0.268707 |
| Quadratic ln(I645) | 0.869152 | 0.440472 | 0.209685 | 37.74 | 0.053372 | 1.292197 |
| sqrt(I680/I645) | 0.996188 | 0.075185 | 0.063145 | 54.60 | 0.065742 | 0.137450 |
| sqrt(I680/I705) | 0.990041 | 0.121519 | 0.102064 | 95.36 | 0.094394 | 0.238656 |


## Predicciones de validación de los tres primeros por RMSE global
| ID | Referencia (µg/mL) | sqrt(I680/I460) | sqrt(I680/I645) | ND(680,705) |
|---|---|---|---|---|
| 1 | 0.02440 | 0.01326 | 0.00320 | 0.03761 |
| 2 | 0.04890 | -0.02203 | -0.02830 | 0.01702 |
| 3 | 0.09770 | 0.02358 | 0.02800 | 0.06266 |
| 4 | 0.19550 | 0.17874 | 0.17674 | 0.18359 |
| 5 | 0.29320 | 0.34425 | 0.35377 | 0.33363 |
| 6 | 0.48870 | 0.63105 | 0.62615 | 0.58460 |
| 7 | 0.97750 | 1.03883 | 1.05282 | 0.98990 |
| 8 | 1.95490 | 1.85286 | 1.84996 | 1.82075 |
| 9 | 3.90980 | 3.92490 | 3.91298 | 4.09394 |


## Alcance de la comparación
Rango de referencia: 0,0244–3,9098 µg/mL. Hay siete muestras por debajo de 1 µg/mL. Las nueve son diluciones de un mismo extracto madre, no nueve extractos independientes. La CV evalúa puntos de esta misma serie y no demuestra exactitud entre extractos, sesiones o protocolos.
Al omitir el extremo superior, se entrena hasta 1,9549 y se predice 3,9098 µg/mL: ese turno requiere extrapolación. Esto se mantiene para todos los candidatos, sin excluirlo de las métricas.
Comparar muchos candidatos con solo nueve puntos puede favorecer por azar al mínimo. Las métricas son CV por candidato, no una validación anidada del proceso de selección ni una validación externa de un ganador. No se atribuye superioridad definitiva al primero. Los porcentajes relativos son sensibles a las referencias cercanas a cero.

## Comparación completa
| Modelo | R² CV9 | RMSE CV9 (µg/mL) | MAE CV9 (µg/mL) | Error relativo medio <1 (%) | MAE <1 (µg/mL) | Error máximo CV9 (µg/mL) |
|---|---|---|---|---|---|---|
| sqrt(I680/I460) | 0.996388 | 0.073183 | 0.060536 | 46.85 | 0.061098 | 0.142355 |
| sqrt(I680/I645) | 0.996188 | 0.075185 | 0.063145 | 54.60 | 0.065742 | 0.137450 |
| ND(680,705) | 0.995095 | 0.085277 | 0.062118 | 27.99 | 0.034395 | 0.184140 |
| sqrt(I680/I860) | 0.994297 | 0.091960 | 0.082782 | 80.29 | 0.079130 | 0.143190 |
| ln(I460) | 0.993592 | 0.097474 | 0.080269 | 63.59 | 0.074656 | 0.181606 |
| ln(I900) | 0.990861 | 0.116409 | 0.097053 | 87.47 | 0.089179 | 0.234254 |
| ln(I585) | 0.990676 | 0.117581 | 0.098845 | 89.01 | 0.091069 | 0.233931 |
| ln(I560) | 0.990417 | 0.119201 | 0.099573 | 94.81 | 0.091601 | 0.238331 |
| sqrt(I680/I705) | 0.990041 | 0.121519 | 0.102064 | 95.36 | 0.094394 | 0.238656 |
| ln(I940) | 0.990038 | 0.121538 | 0.102035 | 97.58 | 0.093849 | 0.243815 |
| ln(I610) | 0.989226 | 0.126391 | 0.106652 | 111.35 | 0.097459 | 0.251511 |
| ln(I645) | 0.988918 | 0.128188 | 0.104704 | 96.07 | 0.095443 | 0.268707 |
| ln(I860) | 0.984590 | 0.151161 | 0.118474 | 124.20 | 0.102377 | 0.336978 |
| ln(I810) | 0.979056 | 0.176222 | 0.137706 | 131.35 | 0.112279 | 0.410363 |
| ln(I535) | 0.978606 | 0.178107 | 0.140379 | 130.21 | 0.114208 | 0.412641 |
| ln(I705) | 0.977592 | 0.182279 | 0.144619 | 134.14 | 0.118334 | 0.424390 |
| ln(I510) | 0.976515 | 0.186608 | 0.145570 | 118.06 | 0.112791 | 0.444676 |
| ND(680,645) | 0.973427 | 0.198498 | 0.111982 | 43.65 | 0.033342 | 0.533243 |
| ln(I645) + ln(I680) | 0.963046 | 0.234080 | 0.123917 | 23.73 | 0.039264 | 0.669967 |
| Quadratic ln(I680) | 0.947222 | 0.279744 | 0.183400 | 119.86 | 0.087762 | 0.737877 |
| ln(I760) | 0.945753 | 0.283611 | 0.215348 | 187.67 | 0.155503 | 0.698642 |
| I680/I705 | 0.921786 | 0.340547 | 0.191359 | 86.36 | 0.061132 | 0.942175 |
| log(I680/I460) | 0.905904 | 0.373527 | 0.286189 | 224.07 | 0.205214 | 0.919630 |
| log(I680/I645) | 0.899734 | 0.385577 | 0.296486 | 238.99 | 0.214379 | 0.948088 |
| ln(I645) + I680 | 0.898477 | 0.387987 | 0.189040 | 35.66 | 0.050199 | 1.133084 |
| log(I680/I860) | 0.888272 | 0.407019 | 0.309588 | 259.23 | 0.220805 | 1.002423 |
| I680/I860 | 0.884114 | 0.414524 | 0.229218 | 105.17 | 0.071390 | 1.156183 |
| log(I680/I705) | 0.876206 | 0.428435 | 0.328290 | 266.39 | 0.233598 | 1.056010 |
| Quadratic ln(I645) | 0.869152 | 0.440472 | 0.209685 | 37.74 | 0.053372 | 1.292197 |
| PLS, 3 components (16 channels) | 0.850905 | 0.470183 | 0.348588 | 173.89 | 0.215729 | 1.134676 |
| I460 | 0.846433 | 0.477181 | 0.356911 | 250.26 | 0.234844 | 1.189016 |
| ln(I730) | 0.833381 | 0.497047 | 0.379371 | 329.02 | 0.266384 | 1.224525 |
| I680/I460 | 0.829232 | 0.503197 | 0.277753 | 135.88 | 0.089843 | 1.412140 |
| I610 | 0.824958 | 0.509456 | 0.383966 | 319.42 | 0.262878 | 1.259454 |
| I680/I645 | 0.823685 | 0.511305 | 0.280731 | 134.78 | 0.089023 | 1.436138 |
| I510 | 0.822925 | 0.512406 | 0.385773 | 286.31 | 0.257785 | 1.271301 |
| I860 | 0.821391 | 0.514619 | 0.385131 | 324.01 | 0.260197 | 1.274171 |
| I645 | 0.820695 | 0.515621 | 0.390445 | 296.67 | 0.264544 | 1.278636 |
| I585 | 0.820278 | 0.516221 | 0.390883 | 294.31 | 0.264633 | 1.280340 |
| PLS, 2 components (16 channels) | 0.818307 | 0.519043 | 0.389808 | 304.68 | 0.242831 | 1.258754 |
| I900 | 0.817422 | 0.520307 | 0.393102 | 295.14 | 0.264620 | 1.291316 |
| I560 | 0.816966 | 0.520956 | 0.393985 | 305.36 | 0.266675 | 1.291185 |
| I810 | 0.816032 | 0.522284 | 0.392163 | 319.46 | 0.265258 | 1.293055 |
| I940 | 0.815901 | 0.522469 | 0.395932 | 308.61 | 0.269177 | 1.294290 |
| I705 | 0.813629 | 0.525684 | 0.398573 | 320.41 | 0.272201 | 1.300631 |
| I535 | 0.812980 | 0.526597 | 0.397745 | 318.12 | 0.269813 | 1.301995 |
| I760 | 0.805067 | 0.537623 | 0.403854 | 332.07 | 0.274802 | 1.328641 |
| PLS, 1 components (16 channels) | 0.804773 | 0.538028 | 0.413187 | 326.16 | 0.293478 | 1.313877 |
| I680 | 0.790642 | 0.557159 | 0.418753 | 294.79 | 0.272897 | 1.383694 |
| I730 | 0.766079 | 0.588938 | 0.453986 | 392.30 | 0.322201 | 1.443665 |
| I645 + I680 | 0.751862 | 0.606571 | 0.405688 | 271.88 | 0.211953 | 1.606005 |
| Quadratic I680/I645 | 0.717653 | 0.647033 | 0.263509 | 32.06 | 0.040854 | 1.930874 |
| ln(I680) | 0.662336 | 0.707583 | 0.535921 | 391.95 | 0.367780 | 1.736368 |
| ln(I485) | 0.537843 | 0.827808 | 0.693992 | 490.64 | 0.524440 | 1.681899 |
| I485 | 0.072471 | 1.172732 | 0.975134 | 874.67 | 0.802080 | 2.508646 |


## Resultados
01_mejores_rmse_cv_9.png compara los seis menores RMSE globales. 02_bajas_concentraciones_cv_9.png muestra los seis menores errores relativos por debajo de 1. 03_modelos_comparables_cv_9.png muestra cuatro formas conocidas, reentrenadas exclusivamente con estas muestras.
comparacion_cv_9.csv contiene las 55 comparaciones. predicciones_cv_9.csv contiene las 495 predicciones de validación con sus referencias y errores. resultados_9.json documenta todos los turnos y la procedencia.
SHA-256 de la entrada: d2f13be46fa8b396155f44a8f9bc08c27b6d141eaa5950b29883d78062696000. El Excel original permanece intacto.
