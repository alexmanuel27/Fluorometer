# Modelos ajustados con 11 y aplicados a 9

Fecha: 18 de octubre de 2026. Todos los errores de concentración están en µg/mL.

## Qué significaban las tablas anteriores
R² de ajuste describe las mismas 11 muestras que fijaron los coeficientes. LOO 11 deja una muestra fuera por turno para revisar interpolación dentro de esa tanda. Predicción 9 aplica los coeficientes fijados con 11 a las nueve diluciones.
Para C = 24,62904595 − 3,46519495 ln(I645), R² de ajuste 11 = 0,9981 y RMSE ajuste 11 = 0,0325. Al aplicar a 9, R² predictivo = 0,8893 y RMSE = 0,4051. Estos valores coinciden con el informe y las gráficas previas.
La fórmula de raíz I680/I645 se exploró posteriormente y es otra relación: sobre 9 alcanza R² = 0,9906 y RMSE = 0,1181. El informe inicial comparó, entre otros, I680/I705, no su raíz ni la raíz I680/I645.

## Diseño de las pruebas
Se comparan 57 modelos: canales individuales lineales y logarítmicos, cocientes de 680 con 645/705/460/860, raíces y logaritmos de cocientes, contrastes normalizados, un cociente cuadrático, combinaciones de dos canales y PLS. 410/435 se excluyen por saturación, aceptada como condición del equipo. 485 se conserva como predictor; no se usan las desviaciones como pesos.
Los coeficientes se ajustan solo con las 11 muestras. PLS elige 1–3 componentes usando exclusivamente las 11; su LOO es anidado. No se excluyen muestras, no se usa la concentración de las nueve para calcular coeficientes y no se recortan predicciones negativas.
Las nueve se consultan repetidamente para explorar y ordenar modelos. Por tanto, el ranking es exploratorio y no es una validación ciega ni demuestra el rendimiento en sesiones nuevas.

## Blanco de sesión: qué se usa
Se usa un único blanco645 por sesión: B645=1256 para las 11 y B645=1214 para las nueve, aportados por Alex. No se solicita ni utiliza blanco por muestra. No hay blanco680 ni de otros canales: no se inventa ni se resta.
Las pruebas con blanco645 incluyen ln(B645/I645), I645/B645 y B645−I645. También se compara transformar B645·I680/I645: esto normaliza el denominador I645 por su blanco mientras mantiene I680 tal como se midió. Es una normalización parcial empírica, no una sustracción de fondo680 ni una corrección óptica completa.
Dividir ambos canales por el mismo B645 dejaría el cociente I680/I645 exactamente igual. Con un único valor de blanco en la tanda de entrenamiento tampoco se puede aprender un efecto independiente del blanco: solo probar estas normalizaciones predefinidas.

## Comparaciones principales
| Modelo | Blanco | R² ajuste 11 | RMSE ajuste 11 | RMSE LOO 11 | R² predicción 9 | RMSE predicción 9 | Sesgo 9 |
|---|---|---|---|---|---|---|---|
| ln(I645) | No | 0.9981 | 0.0325 | 0.0391 | 0.8893 | 0.4051 | +0.3254 |
| ln(B645/I645) | 645, sesión | 0.9981 | 0.0325 | 0.0391 | 0.9317 | 0.3182 | +0.2075 |
| sqrt(I680/I645) | No | 0.9976 | 0.0362 | 0.0427 | 0.9906 | 0.1181 | +0.0821 |
| sqrt(B645 × I680/I645) | 645, normalización parcial | 0.9976 | 0.0362 | 0.0427 | 0.9959 | 0.0781 | +0.0284 |
| sqrt(I680/I705) | No | 0.9961 | 0.0464 | 0.0553 | 0.9929 | 0.1028 | +0.0494 |
| sqrt(I680/I860) | No | 0.9979 | 0.0341 | 0.0460 | 0.9914 | 0.1129 | +0.0843 |
| I680 | No | 0.9770 | 0.1122 | 0.1446 | 0.7055 | 0.6608 | -0.5053 |
| ln(I645) + I680 | No | 0.9984 | 0.0295 | 0.0398 | 0.7984 | 0.5468 | +0.4482 |
| PLS 16 channels (1 component) | No | 0.9882 | 0.0802 | 0.1307 | 0.9086 | 0.3682 | +0.0955 |


## Mejores resultados de esta exploración
Sin blanco: sqrt(I680/I705), RMSE9=0.10280, R²9=0.99287.
Con blanco645: sqrt(B645 × I680/I645), RMSE9=0.07810, R²9=0.99589.
Las raíces de cocientes transfieren mejor que varios canales individuales en esta comparación. El mejor ajuste dentro de 11 no determina el mejor resultado sobre 9.

## Ecuaciones de interés (coeficientes calculados solo con 11)
- sqrt(I680/I705): C = -2.47810518 +10.24469731 × [sqrt(I680/I705)].
- sqrt(B645 × I680/I645): C = -2.21412414 +0.28014340 × [sqrt(B645 × I680/I645)].
- sqrt(I680/I645): C = -2.21412414 +9.92830753 × [sqrt(I680/I645)].
- ln(I645): C = 24.62904595 -3.46519495 × [ln(I645)].
- ln(B645/I645): C = -0.09750183 +3.46519495 × [ln(B645/I645)].

Las intensidades corresponden a los promedios suministrados en los Excel. C se expresa en µg/mL. B645 debe ser el blanco de la misma sesión, medido con la configuración del equipo correspondiente.

## Ranking completo por error en las nueve
| Modelo | Blanco | R² ajuste 11 | RMSE ajuste 11 | RMSE LOO 11 | R² predicción 9 | RMSE predicción 9 | Sesgo 9 |
|---|---|---|---|---|---|---|---|
| sqrt(B645 × I680/I645) | 645, normalización parcial | 0.9976 | 0.0362 | 0.0427 | 0.9959 | 0.0781 | +0.0284 |
| sqrt(I680/I705) | No | 0.9961 | 0.0464 | 0.0553 | 0.9929 | 0.1028 | +0.0494 |
| sqrt(I680/I860) | No | 0.9979 | 0.0341 | 0.0460 | 0.9914 | 0.1129 | +0.0843 |
| sqrt(I680/I645) | No | 0.9976 | 0.0362 | 0.0427 | 0.9906 | 0.1181 | +0.0821 |
| sqrt(I680/I460) | No | 0.9950 | 0.0523 | 0.0623 | 0.9868 | 0.1399 | +0.0677 |
| ND(680,705) | No | 0.9969 | 0.0414 | 0.0475 | 0.9833 | 0.1575 | +0.1487 |
| Quadratic I680/I645 | No | 0.9977 | 0.0353 | 0.0442 | 0.9830 | 0.1587 | +0.1498 |
| ND(680,645) | No | 0.9975 | 0.0370 | 0.0437 | 0.9702 | 0.2100 | +0.1915 |
| log(I680/I860) | No | 0.9888 | 0.0783 | 0.1052 | 0.9453 | 0.2848 | -0.1557 |
| log(I680/I645) | No | 0.9885 | 0.0793 | 0.1027 | 0.9420 | 0.2933 | -0.1748 |
| I680/I705 | No | 0.9949 | 0.0529 | 0.0664 | 0.9413 | 0.2951 | +0.2606 |
| log(I680/I460) | No | 0.9850 | 0.0906 | 0.1162 | 0.9342 | 0.3124 | -0.1904 |
| ratio(B645 × I680/I645) | 645, normalización parcial | 0.9937 | 0.0587 | 0.0772 | 0.9327 | 0.3160 | +0.2597 |
| ln(B645/I645) | 645, sesión | 0.9981 | 0.0325 | 0.0391 | 0.9317 | 0.3182 | +0.2075 |
| log(I680/I705) | No | 0.9861 | 0.0870 | 0.1116 | 0.9295 | 0.3234 | -0.1930 |
| I510 | No | 0.9822 | 0.0986 | 0.1264 | 0.9292 | 0.3240 | +0.0793 |
| I610 | No | 0.9827 | 0.0972 | 0.1304 | 0.9291 | 0.3241 | +0.0898 |
| I585 | No | 0.9855 | 0.0889 | 0.1153 | 0.9274 | 0.3281 | +0.0405 |
| I560 | No | 0.9858 | 0.0881 | 0.1131 | 0.9274 | 0.3281 | +0.0458 |
| I900 | No | 0.9853 | 0.0895 | 0.1162 | 0.9254 | 0.3325 | +0.0402 |
| I680/I860 | No | 0.9950 | 0.0522 | 0.0644 | 0.9250 | 0.3336 | +0.2948 |
| I645 | No | 0.9865 | 0.0859 | 0.1123 | 0.9246 | 0.3343 | +0.0656 |
| log(B645 × I680/I645) | 645, normalización parcial | 0.9885 | 0.0793 | 0.1027 | 0.9232 | 0.3375 | -0.2417 |
| I940 | No | 0.9859 | 0.0876 | 0.1143 | 0.9217 | 0.3408 | +0.0866 |
| I460 | No | 0.9839 | 0.0936 | 0.1198 | 0.9215 | 0.3411 | +0.0840 |
| I860 | No | 0.9811 | 0.1016 | 0.1369 | 0.9193 | 0.3459 | +0.1608 |
| I810 | No | 0.9857 | 0.0882 | 0.1187 | 0.9182 | 0.3483 | +0.1208 |
| B645 - I645 | 645, sesión | 0.9865 | 0.0859 | 0.1123 | 0.9158 | 0.3533 | -0.1319 |
| I535 | No | 0.9839 | 0.0938 | 0.1196 | 0.9150 | 0.3550 | +0.1428 |
| ln(I510) | No | 0.9938 | 0.0580 | 0.0693 | 0.9133 | 0.3586 | +0.2969 |
| I645/B645 | 645, sesión | 0.9865 | 0.0859 | 0.1123 | 0.9117 | 0.3619 | -0.0846 |
| I705 | No | 0.9866 | 0.0855 | 0.1096 | 0.9110 | 0.3632 | +0.1186 |
| PLS 16 channels (1 component) | No | 0.9882 | 0.0802 | 0.1307 | 0.9086 | 0.3682 | +0.0955 |
| I680/I645 | No | 0.9937 | 0.0587 | 0.0772 | 0.9083 | 0.3687 | +0.3080 |
| ln(I560) | No | 0.9965 | 0.0435 | 0.0505 | 0.9011 | 0.3829 | +0.3154 |
| ln(I585) | No | 0.9973 | 0.0386 | 0.0452 | 0.8999 | 0.3854 | +0.3097 |
| I680/I460 | No | 0.9938 | 0.0583 | 0.0716 | 0.8996 | 0.3858 | +0.2976 |
| ln(I900) | No | 0.9973 | 0.0385 | 0.0453 | 0.8954 | 0.3938 | +0.3146 |
| ln(I610) | No | 0.9936 | 0.0591 | 0.0755 | 0.8944 | 0.3958 | +0.3359 |
| ln(I645) | No | 0.9981 | 0.0325 | 0.0391 | 0.8893 | 0.4051 | +0.3254 |
| ln(I810) | No | 0.9965 | 0.0439 | 0.0579 | 0.8832 | 0.4161 | +0.3479 |
| I760 | No | 0.9842 | 0.0927 | 0.1240 | 0.8801 | 0.4217 | +0.1970 |
| ln(I940) | No | 0.9978 | 0.0344 | 0.0408 | 0.8759 | 0.4289 | +0.3506 |
| ln(I535) | No | 0.9948 | 0.0531 | 0.0623 | 0.8754 | 0.4299 | +0.3663 |
| ln(I860) | No | 0.9931 | 0.0614 | 0.0800 | 0.8736 | 0.4330 | +0.3827 |
| ln(I705) | No | 0.9965 | 0.0437 | 0.0513 | 0.8707 | 0.4379 | +0.3508 |
| ln(I460) | No | 0.9943 | 0.0556 | 0.0655 | 0.8493 | 0.4727 | +0.3455 |
| ln(I760) | No | 0.9936 | 0.0591 | 0.0773 | 0.8384 | 0.4895 | +0.3780 |
| ln(I645) + ln(I680) | No | 0.9983 | 0.0301 | 0.0397 | 0.8300 | 0.5021 | +0.4285 |
| ln(I645) + I680 | No | 0.9984 | 0.0295 | 0.0398 | 0.7984 | 0.5468 | +0.4482 |
| I680 | No | 0.9770 | 0.1122 | 0.1446 | 0.7055 | 0.6608 | -0.5053 |
| ln(I485) | No | 0.6725 | 0.4229 | 0.4967 | 0.5970 | 0.7730 | +0.3972 |
| I485 | No | 0.5924 | 0.4718 | 0.5638 | 0.5770 | 0.7920 | +0.1667 |
| ln(I680) | No | 0.9556 | 0.1556 | 0.1997 | 0.4458 | 0.9065 | -0.7967 |
| I645 + I680 | No | 0.9910 | 0.0701 | 0.1066 | 0.1410 | 1.1286 | +0.8200 |
| I730 | No | 0.8910 | 0.2439 | 0.3005 | -0.2000 | 1.3339 | +1.0131 |
| ln(I730) | No | 0.8953 | 0.2391 | 0.2931 | -0.4964 | 1.4895 | +1.1241 |


## Predicciones de las nueve con los mejores modelos
| ID | Referencia | sqrt(I680/I705) | sqrt(B645 × I680/I645) | sqrt(I680/I645) |
|---|---|---|---|---|
| 1 | 0.0244 | -0.0064 | 0.0107 | 0.0489 |
| 2 | 0.0489 | -0.0248 | -0.0117 | 0.0261 |
| 3 | 0.0977 | 0.0394 | 0.0443 | 0.0831 |
| 4 | 0.1955 | 0.1975 | 0.1882 | 0.2295 |
| 5 | 0.2932 | 0.3815 | 0.3590 | 0.4032 |
| 6 | 0.4887 | 0.6792 | 0.6308 | 0.6796 |
| 7 | 0.9775 | 1.1464 | 1.0771 | 1.1335 |
| 8 | 1.9549 | 2.0225 | 1.9249 | 1.9959 |
| 9 | 3.9098 | 4.0002 | 4.0230 | 4.1299 |


## Límites concretos
Las 11 cubren 0,7944–3,07062 µg/mL y las nueve 0,0244–3,9098. Por tanto, las nueve incluyen extrapolación a ambos extremos. Las nueve proceden de un mismo extracto madre. La incertidumbre compartida de esa referencia no se conoce. R² alto no equivale a precisión relativa alta cerca de cero.
Las predicciones negativas cerca de cero y todos los errores por muestra se conservan en los CSV. Las figuras muestran concentraciones predichas, no intervalos de confianza: no se presenta la desviación de repetición instrumental como incertidumbre total del modelo.
Se reconoce la presencia de filtros espectrales incorporados en el sensor. Estas pruebas no cambian el montaje ni el firmware.

## Archivos
01: comparación principal con y sin blanco. 02: nueve mejores modelos sobre las nueve muestras (selección exploratoria). 03: todos los canales individuales en forma logarítmica. 04: error dentro de 11 frente al error sobre 9. Los CSV guardan todos los resultados y predicciones; ecuaciones.json guarda coeficientes y procedencia.
Fuentes: 11Samples.xlsx y 9Samples.xlsx, Sheet1. Blancos645 procedentes del mensaje de Alex, no de los Excel. Los originales permanecen intactos.
