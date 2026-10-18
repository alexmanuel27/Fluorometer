# Análisis de calibración de clorofila a

> Informe histórico de exploración. La decisión vigente es 85 → 9 con blanco; consultar [articulo.md](../articulo.md). Este informe conserva sus resultados originales y no es la guía actual del manuscrito.

Fecha: 18 de octubre de 2026. Unidad de concentración: µg/mL.

## Resultado principal
Hay información útil: I645 tiene una relación logarítmica fuerte con la concentración. La normalización por blanco aproxima mucho las 85 muestras y las nueve diluciones, pero no resuelve la diferencia con las 11 muestras. El modelo multicanal probado no mejora la predicción respecto al logaritmo de I645 dentro de cada tanda. 680 nm es el canal que merece estudiar como candidato de emisión.
La prioridad es controlar fondo óptico, saturación y protocolo, y validar con extractos independientes. Los resultados actuales sostienen una calibración empírica, no demuestran una medida pura de fluorescencia ni una ecuación universal.

## Qué contienen los archivos
Hay 105 registros completos: 85 con I645 y 20 con los 18 canales y sus desviaciones. No hay absorbancias 664/648, factores de dilución, concentración del extracto madre, espectros de los blancos, datos ADC crudos ni las 10 lecturas individuales. Por tanto, no se puede auditar la concentración de referencia ni recalcular las desviaciones.
El fichero de 85 también contiene 84 filas con solo un identificador, excluidas de los análisis sin modificar el original. Los rangos reales son 0,02384–7,98964 (85), 0,7944–3,07062 (11) y 0,0244–3,9098 (9). No existe una muestra cero en estas tablas.

## Calidad de los datos
410 y 435 nm valen exactamente 4294967296 (=2³²) en las 20 muestras, con desviación cero. Son datos inválidos para cuantificación. Esto es compatible con un problema de rango, saturación o conversión, pero estos Excel no permiten identificar la causa. Se excluyeron ambos canales, no las muestras.
La muestra 5 del grupo de nueve tiene desviación(485)=1589592733 (celda J6) frente a I485=1343,57367. Se conserva el original y se marca el error. No se utiliza como peso ni barra de error. 485 presenta dispersión irregular y requiere revisión de la exportación.
Las desviaciones son de repetición instrumental, no incertidumbre de extracción, dilución o referencia. No se ponderaron los ajustes por esas desviaciones. Las unidades radiométricas de intensidad no se acreditan en los archivos: se usan unidades del instrumento y cocientes adimensionales.

## Calibración con 645 nm
Modelo: C = a + b·ln(I645). ln es logaritmo natural. Se incluyen todas las muestras completas, sin eliminar atípicos.
| Grupo | Rango real | R² ajuste | RMSE ajuste | RMSE dejar-una-fuera |
|---|---|---|---|---|
| 85 | 0.0238–7.9896 | 0.9456 | 0.4359 | 0.4560 |
| 11 | 0.7944–3.0706 | 0.9981 | 0.0325 | 0.0391 |
| 9 | 0.0244–3.9098 | 0.9955 | 0.0818 | 0.1282 |

- Grupo 85: C = 20.441072 -2.842810·ln(I645). Equivalente: C = -0.062113 + 2.842810·ln(I0/I645), I0=1356. IC95% convencional de la pendiente ln(I): [-2.9916, -2.6940].
- Grupo 11: C = 24.629046 -3.465195·ln(I645). Equivalente: C = -0.097502 + 3.465195·ln(I0/I645), I0=1256. IC95% convencional de la pendiente ln(I): [-3.5803, -3.3501].
- Grupo 9: C = 20.617626 -2.919715·ln(I645). Equivalente: C = -0.117244 + 2.919715·ln(I0/I645), I0=1214. IC95% convencional de la pendiente ln(I): [-3.0955, -2.7440].

RMSE es la raíz del error cuadrático medio de concentración, en µg/mL. R² de ajuste describe los mismos puntos usados para calibrar; no es validación externa. Los intervalos convencionales suponen errores de referencia independientes y no incluyen incertidumbre común del extracto madre.
Sensibilidad al rango: usando solo las 38 muestras del grupo 85 que caen en el intervalo del grupo 11, la pendiente frente a ln(I0/I) pasa de 2,843 a 2.024. La diferencia de pendientes no permite aislar un efecto de protocolo: también influyen rango, dispersión y error de referencia. No se ha descartado ninguna muestra por su residual.
Mayores residuales por tanda (para revisar registros, no para eliminarlos automáticamente):
| Grupo | ID | C referencia | I645 | Predicción − referencia |
|---|---|---|---|---|
| 85 | 62 | 2.97854 | 221.045 | +2.1160 |
| 85 | 82 | 6.50859 | 224.910 | -1.4633 |
| 85 | 70 | 3.85665 | 226.650 | +1.1667 |
| 11 | 9 | 1.99633 | 670.447 | +0.0814 |
| 11 | 2 | 0.79440 | 981.016 | -0.0357 |
| 11 | 1 | 1.28065 | 851.919 | -0.0330 |
| 9 | 6 | 0.48870 | 942.105 | +0.1344 |
| 9 | 7 | 0.97750 | 798.270 | +0.1293 |
| 9 | 2 | 0.04890 | 1182.401 | -0.0891 |


Los blancos (dato aportado por Alex) son 1356, 1256 y 1214. Respecto al de 85, cambian −7,37% y −10,47%. Normalizar por blanco corrige una escala multiplicativa, pero no elimina diferencias de pendiente, composición, geometría o protocolo. Restar el blanco produce valores negativos en I645 y no debe interpretarse como fluorescencia neta positiva.

### Transferencia de la calibración de 85
| Test | Modelo | RMSE | Sesgo predicho − referencia |
|---|---|---|---|
| 11 | lnI645 | 0.1561 | -0.0756 |
| 11 | ln_blank_ratio | 0.3236 | -0.2934 |
| 9 | lnI645 | 0.3542 | +0.3431 |
| 9 | ln_blank_ratio | 0.0924 | +0.0287 |

La fórmula ya usada en el firmware, C = −2,7924·ln(I645)+20,1264, evaluada sin reajustar:
| Grupo | RMSE | Sesgo |
|---|---|---|
| 85 | 0.4372 | +0.0096 |
| 11 | 0.1577 | -0.0572 |
| 9 | 0.3818 | +0.3691 |


## ¿Es fluorescencia?
Según Alex, LED y detector están de frente y la excitación es aproximadamente 430–435 nm. Esa disposición puede captar emisión, transmisión y luz dispersada. No se ha confirmado la presencia de filtro óptico. El blanco de etanol ya tiene I645 alta, y I645 cae al aumentar C. Por tanto, no está demostrado que la señal total a 645 sea fluorescencia de clorofila a. Puede servir como calibración empírica de atenuación, pero el origen físico exige un control experimental.
680 nm es el único de los 16 canales utilizables que crece sistemáticamente con C en ambas tandas. Es un candidato más coherente con emisión de clorofila a. Los datos no prueban que sea fluorescencia pura: falta el blanco espectral de 680 y un control con filtro. La literatura sitúa una banda de Chl a en etanol alrededor de 671 nm, dentro de la proximidad espectral de este canal [1].

## Modelos espectrales exploratorios
Se compararon alternativas pequeñas: I680, I680/I705 y ln(I645)+I680. PLS emplea 16 canales (se excluyen 410/435) y elige 1–3 componentes dentro de validación anidada. Los modelos individuales usan dejar-una-fuera con variables fijas. La observación de estos espectros motivó evaluar 680 y su cociente: su selección no es una prueba independiente. La comparación entre alternativas sigue siendo exploratoria y necesita una prueba nueva. La validación anidada reduce el optimismo de elegir componentes PLS sobre los mismos puntos que se usan para evaluar [2].
| Grupo | Modelo | RMSE validación | R² validación |
|---|---|---|---|
| 11 | lnI645 | 0.0391 | 0.9972 |
| 11 | I680 | 0.1446 | 0.9617 |
| 11 | I680_over_I705 | 0.0664 | 0.9919 |
| 11 | lnI645_and_I680 | 0.0398 | 0.9971 |
| 9 | lnI645 | 0.1282 | 0.9889 |
| 9 | I680 | 0.5572 | 0.7906 |
| 9 | I680_over_I705 | 0.3405 | 0.9218 |
| 9 | lnI645_and_I680 | 0.3880 | 0.8985 |
| 11 | PLS_16_valid_channels | 0.1307 | 0.9687 |
| 9 | PLS_16_valid_channels | 0.4702 | 0.8509 |

Transferencia entre protocolos:
| Entrena | Prueba | Modelo | RMSE | Sesgo |
|---|---|---|---|---|
| 11 | 9 | lnI645 | 0.4051 | +0.3254 |
| 11 | 9 | ln_blank_ratio | 0.3182 | +0.2075 |
| 11 | 9 | I680 | 0.6608 | -0.5053 |
| 11 | 9 | I680_over_I705 | 0.2951 | +0.2606 |
| 11 | 9 | lnI645_and_I680 | 0.5468 | +0.4482 |
| 9 | 11 | lnI645 | 0.4247 | -0.4072 |
| 9 | 11 | ln_blank_ratio | 0.3307 | -0.3079 |
| 9 | 11 | I680 | 0.9743 | +0.9390 |
| 9 | 11 | I680_over_I705 | 0.2997 | -0.2923 |
| 9 | 11 | lnI645_and_I680 | 0.7815 | -0.7523 |
| 11 | 9 | PLS_16_valid_channels | 0.3682 | +0.0955 |
| 9 | 11 | PLS_16_valid_channels | 0.6988 | +0.6019 |

Los nueve estándares proceden de un único extracto madre. Dejar una dilución fuera mide interpolación dentro de esa serie; no valida un extracto independiente y no estima la incertidumbre común de la concentración madre. Entrenar con 11 y probar con nueve incluye extrapolación por debajo de 0,7944 y por encima de 3,07062. Entrenar con nueve y probar con 11 no extrapola en concentración, pero sí cambia protocolo/matriz. Las mejoras multicanal no acreditan todavía una calibración universal.

## Acciones concretas
1. Guardar los 18 canales del etanol, del sistema con LED apagado y de una muestra con LED encendido. Revisar el origen de 4294967296 con ADC crudo y ganancia/integración registrados. Reducir ganancia, aumentar atenuación o bajar potencia hasta que el ADC no sature.
2. Comparar la medida frontal con una geometría a 90° y un filtro de emisión adecuado para bloquear excitación. Un blanco medido en idénticas condiciones permitirá separar fondo y señal.
3. Preparar varios extractos madre independientes y varias diluciones de cada uno. Aleatorizar el orden, medir el blanco por tanda y controlar calentamiento y posición. Reservar extractos completos, no lecturas repetidas, para validación externa.
4. Recuperar Abs664, Abs648, ecuación de referencia, factor de dilución y concentración madre para auditar la referencia. Registrar etanol %, cuveta, trayectoria, filtros, integración, ganancia y potencia.
5. Mantener como candidato la calibración logarítmica I645 y evaluar en paralelo 680 y cocientes espectrales. No reemplazar todavía la ecuación del firmware a partir de estos 20 espectros.
No es posible calcular un límite de detección defendible con un solo valor medio de blanco por tanda y sin réplicas independientes del blanco.

## Archivos y reproducibilidad
Los tres gráficos muestran calibración/transferencia a 645, comportamiento de 680/canales y comparación de validación. CSV adicionales contienen métricas, predicciones por muestra y los datos unidos con procedencia. `resultados.json` guarda ecuaciones y hashes SHA-256 de los originales.

## Referencias
[1] Kinetics of Chlorophyll Degradation in Japanese Maple Leaves with In Situ Heating Visible and Near-Infrared Spectroscopic Monitoring (2025). https://www.mdpi.com/2075-1729/15/3/335
[2] Scikit-learn: Nested versus non-nested cross-validation. https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html
[3] ams AS7265x datasheet. https://cdn.sparkfun.com/assets/c/2/9/0/a/AS7265x_Datasheet.pdf
