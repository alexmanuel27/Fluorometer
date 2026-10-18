# Validación cruzada exclusivamente sobre las 11 muestras

Fecha: 18 de octubre de 2026. Único archivo de entrada: 11Samples.xlsx, Sheet1. No se abre ni se utiliza ningún otro conjunto de muestras.

## Método
Se comparan 57 modelos con el mismo procedimiento: dejar una muestra fuera, ajustar con las otras diez y predecir la omitida; repetir once veces. Cada muestra tiene exactamente una predicción de validación por modelo. Todas las gráficas y métricas de este informe se calculan con esas predicciones, no con el ajuste sobre las once a la vez.
R² CV = 1 − suma de errores de predicción al cuadrado / variación total de las concentraciones de referencia. RMSE CV es la raíz del error cuadrático medio, en µg/mL. Mayor R² y menor RMSE indican mejor resultado para esta misma validación.
Los modelos OLS tienen intercepto y uno o dos predictores. PLS utiliza los 16 canales no saturados, con 1, 2 o 3 componentes como candidatos fijos; la escala y el centrado se calculan dentro de cada turno exclusivamente con sus diez muestras de entrenamiento. Se conserva cada muestra, sin eliminar atípicos ni recortar predicciones.

## Comparación principal
| Modelo | Blanco645 | R² CV11 | RMSE CV11 (µg/mL) | MAE CV11 | Error máximo CV11 |
|---|---|---|---|---|---|
| Quadratic ln(I645) | No | 0.99736 | 0.03799 | 0.03072 | 0.08561 |
| ln(I645) | No | 0.99721 | 0.03905 | 0.03223 | 0.09156 |
| ln(I645) + ln(I680) | No | 0.99712 | 0.03969 | 0.03308 | 0.08641 |
| ln(I645) + I680 | No | 0.99710 | 0.03980 | 0.03254 | 0.08524 |
| ln(I940) | No | 0.99695 | 0.04083 | 0.03229 | 0.10266 |
| sqrt(I680/I645) | No | 0.99666 | 0.04270 | 0.03440 | 0.09667 |
| ND(680,645) | No | 0.99651 | 0.04366 | 0.03594 | 0.07019 |
| Quadratic I680/I645 | No | 0.99643 | 0.04416 | 0.03116 | 0.09739 |


## Blanco de sesión
Se considera el valor aportado por Alex: B645=1256. Es constante para las once muestras. Con intercepto, usar ln(B645/I645) es matemáticamente equivalente a usar ln(I645); sus predicciones de validación coinciden. Lo mismo ocurre entre sqrt(B645·I680/I645) y sqrt(I680/I645): solo cambia la escala del predictor.
Por eso esta validación de una sola sesión no puede cuantificar la mejora de un blanco ante cambios entre sesiones. Las variantes se incluyen en la tabla completa, pero no se duplican en la gráfica principal. No se supone blanco de 680 ni de otros canales.

## Ecuaciones reajustadas con las once para posible uso posterior
Los coeficientes de abajo se calculan con las once muestras juntas. No se usaron para calcular los resultados de validación de la tabla anterior: en validación se vuelve a ajustar cada modelo con diez muestras en cada turno.
| Modelo | Predictores x1; x2 | a (intercepto) | b1 | b2 |
|---|---|---|---|---|
| Quadratic ln(I645) | ln(I645); ln(I645)² | 38.75817833 | -7.76490941 | 0.32676847 |
| ln(I645) | ln(I645) | 24.62904595 | -3.46519495 | — |
| ln(I645) + ln(I680) | ln(I645); ln(I680) | 28.51440479 | -3.76559471 | -0.40198496 |
| ln(I645) + I680 | ln(I645); I680 | 28.58503500 | -3.96220806 | -0.00586820 |
| ln(I940) | ln(I940) | 21.97940324 | -3.35870439 | — |
| sqrt(I680/I645) | sqrt(I680/I645) | -2.21412414 | 9.92830753 | — |
| ND(680,645) | (I680-I645)/(I680+I645) | 7.79394064 | 8.37808912 | — |
| Quadratic I680/I645 | r=I680/I645; r² | -0.63085248 | 16.99428614 | -13.66302729 |

Forma de la ecuación: C = a + b1·x1 + b2·x2, omitiendo x2 cuando solo existe un predictor. ln es logaritmo natural; C está en µg/mL. ND(680,645)=(I680−I645)/(I680+I645).

## Tabla completa: todos los valores son validación cruzada sobre 11
| Modelo | Blanco645 | R² CV11 | RMSE CV11 (µg/mL) | MAE CV11 | Error máximo CV11 |
|---|---|---|---|---|---|
| Quadratic ln(I645) | No | 0.99736 | 0.03799 | 0.03072 | 0.08561 |
| ln(I645) | No | 0.99721 | 0.03905 | 0.03223 | 0.09156 |
| ln(B645/I645) | Sesión, constante | 0.99721 | 0.03905 | 0.03223 | 0.09156 |
| ln(I645) + ln(I680) | No | 0.99712 | 0.03969 | 0.03308 | 0.08641 |
| ln(I645) + I680 | No | 0.99710 | 0.03980 | 0.03254 | 0.08524 |
| ln(I940) | No | 0.99695 | 0.04083 | 0.03229 | 0.10266 |
| sqrt(I680/I645) | No | 0.99666 | 0.04270 | 0.03440 | 0.09667 |
| sqrt(B645 × I680/I645) | Sesión, constante | 0.99666 | 0.04270 | 0.03440 | 0.09667 |
| ND(680,645) | No | 0.99651 | 0.04366 | 0.03594 | 0.07019 |
| Quadratic I680/I645 | No | 0.99643 | 0.04416 | 0.03116 | 0.09739 |
| ln(I585) | No | 0.99625 | 0.04523 | 0.03402 | 0.12112 |
| ln(I900) | No | 0.99624 | 0.04533 | 0.03510 | 0.11891 |
| sqrt(I680/I860) | No | 0.99612 | 0.04605 | 0.03810 | 0.09908 |
| ND(680,705) | No | 0.99586 | 0.04752 | 0.03128 | 0.11448 |
| ln(I560) | No | 0.99532 | 0.05055 | 0.03626 | 0.13410 |
| ln(I705) | No | 0.99518 | 0.05132 | 0.03495 | 0.14199 |
| sqrt(I680/I705) | No | 0.99440 | 0.05528 | 0.04469 | 0.13589 |
| ln(I810) | No | 0.99386 | 0.05788 | 0.04802 | 0.09830 |
| ln(I535) | No | 0.99290 | 0.06226 | 0.04047 | 0.17803 |
| sqrt(I680/I460) | No | 0.99289 | 0.06230 | 0.04826 | 0.15726 |
| I680/I860 | No | 0.99241 | 0.06438 | 0.05773 | 0.10378 |
| ln(I460) | No | 0.99214 | 0.06551 | 0.04650 | 0.17956 |
| I680/I705 | No | 0.99192 | 0.06643 | 0.06036 | 0.11262 |
| ln(I510) | No | 0.99121 | 0.06929 | 0.04448 | 0.19167 |
| I680/I460 | No | 0.99062 | 0.07156 | 0.06530 | 0.10647 |
| ln(I610) | No | 0.98955 | 0.07555 | 0.06373 | 0.10606 |
| Quadratic ln(I680) | No | 0.98917 | 0.07691 | 0.05739 | 0.14659 |
| I680/I645 | No | 0.98908 | 0.07720 | 0.06660 | 0.15489 |
| ln(I760) | No | 0.98905 | 0.07731 | 0.06472 | 0.13505 |
| ln(I860) | No | 0.98829 | 0.07995 | 0.06612 | 0.14844 |
| log(I680/I645) | No | 0.98069 | 0.10267 | 0.08569 | 0.20355 |
| log(I680/I860) | No | 0.97974 | 0.10518 | 0.07773 | 0.24604 |
| I645 + I680 | No | 0.97921 | 0.10655 | 0.09342 | 0.18889 |
| PLS, 1 components (16 channels) | No | 0.97881 | 0.10756 | 0.08435 | 0.23756 |
| I705 | No | 0.97799 | 0.10962 | 0.08668 | 0.22576 |
| log(I680/I705) | No | 0.97718 | 0.11163 | 0.09168 | 0.21880 |
| I645 | No | 0.97691 | 0.11227 | 0.08900 | 0.23893 |
| I560 | No | 0.97658 | 0.11309 | 0.08885 | 0.22689 |
| I940 | No | 0.97608 | 0.11427 | 0.08969 | 0.24283 |
| I585 | No | 0.97567 | 0.11525 | 0.09041 | 0.24227 |
| log(I680/I460) | No | 0.97529 | 0.11617 | 0.09400 | 0.22400 |
| I900 | No | 0.97528 | 0.11617 | 0.09020 | 0.24572 |
| I810 | No | 0.97418 | 0.11873 | 0.09457 | 0.26177 |
| PLS, 2 components (16 channels) | No | 0.97391 | 0.11936 | 0.09365 | 0.24254 |
| I535 | No | 0.97378 | 0.11965 | 0.09109 | 0.23816 |
| I460 | No | 0.97370 | 0.11984 | 0.09015 | 0.23870 |
| I760 | No | 0.97185 | 0.12398 | 0.10007 | 0.25591 |
| I510 | No | 0.97075 | 0.12638 | 0.09641 | 0.24712 |
| I610 | No | 0.96888 | 0.13036 | 0.09947 | 0.27643 |
| I860 | No | 0.96570 | 0.13686 | 0.11017 | 0.29043 |
| I680 | No | 0.96171 | 0.14459 | 0.12051 | 0.30388 |
| PLS, 3 components (16 channels) | No | 0.96160 | 0.14480 | 0.12219 | 0.28453 |
| ln(I680) | No | 0.92698 | 0.19967 | 0.16886 | 0.41940 |
| ln(I730) | No | 0.84271 | 0.29306 | 0.23076 | 0.50147 |
| I730 | No | 0.83461 | 0.30051 | 0.23798 | 0.51939 |
| ln(I485) | No | 0.54821 | 0.49668 | 0.36261 | 1.09752 |
| I485 | No | 0.41778 | 0.56383 | 0.43143 | 1.16012 |


## Predicciones de validación de los modelos principales
| ID | Referencia | Quadratic ln(I645) | ln(I645) | ln(I645) + ln(I680) | ln(I645) + I680 |
|---|---|---|---|---|---|
| 1 | 1.28065 | 1.23509 | 1.24273 | 1.23787 | 1.24180 |
| 2 | 0.79440 | 0.76262 | 0.74690 | 0.76024 | 0.76046 |
| 3 | 1.41502 | 1.38475 | 1.39782 | 1.37635 | 1.37490 |
| 4 | 0.81814 | 0.85426 | 0.83498 | 0.87252 | 0.87833 |
| 5 | 0.91762 | 0.95759 | 0.94857 | 0.94940 | 0.94878 |
| 6 | 1.64964 | 1.64486 | 1.66117 | 1.64281 | 1.64049 |
| 7 | 2.09360 | 2.06234 | 2.08071 | 2.07097 | 2.07198 |
| 8 | 2.29035 | 2.29670 | 2.30690 | 2.30088 | 2.29965 |
| 9 | 1.99633 | 2.08194 | 2.08789 | 2.08274 | 2.08157 |
| 10 | 2.73873 | 2.71427 | 2.70669 | 2.71404 | 2.71325 |
| 11 | 3.07062 | 3.07238 | 3.03108 | 3.05965 | 3.06777 |


## Alcance
El rango de referencia es 0,7944–3,07062 µg/mL. Son once muestras de una única tanda. El ranking describe este conjunto y estas condiciones. Diferencias pequeñas de CV no demuestran superioridad en otras sesiones. Elegir el mínimo entre muchos modelos introduce optimismo de selección; las métricas aquí son por candidato, no una estimación anidada del proceso de elegir el mejor.
Los canales 410/435 se mantienen excluidos por saturación. Las desviaciones instrumentales no se usan como pesos ni se confunden con incertidumbre de la concentración de referencia. Los filtros incorporados del sensor y el montaje no se modifican.

## Resultados guardados
01_modelos_cv_11.png contiene ocho relaciones distintas con predicciones dejar-una-fuera. 02_errores_cv_11.png compara sus errores y varios controles. 03_canales_cv_11.png muestra los dieciséis canales individuales con transformación logarítmica. Los CSV contienen el ranking completo y cada predicción de validación. resultados_11.json guarda procedencia y ecuaciones reajustadas con las once para posible uso posterior; estas ecuaciones completas no se utilizaron para generar las predicciones de validación.
SHA-256 de la entrada: 47ea24812c3912aef8265ffa5647bca06c60a32d1f507f50d096b026b8513e58. El Excel original permanece intacto.
