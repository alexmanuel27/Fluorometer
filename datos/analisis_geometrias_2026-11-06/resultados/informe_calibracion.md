# Comparación de geometrías con concentraciones

Fecha: 6 noviembre 2026.

## Datos y método

Fuente de concentraciones: originales/reCalibration_20samples.xlsx, Sheet1!A3:D22. Veinte muestras de extracto de clorofila de hoja de arbusto (según título), de 0,15 a 3,00 µg/mL. La columna D contiene valores escritos, no fórmulas: se usa como referencia proporcionada, sin recalcular a partir de A664 y A648. No consta incertidumbre de concentración ni ecuación/solvente de su determinación.

Alex confirma las mismas muestras en ambas geometrías. Se utilizan 120 archivos de muestra, seis blancos y dos dark. Cada muestra tiene tres medias, cada una de diez lecturas. La unidad del ajuste es la media de muestra (n=20 por geometría), no 600 observaciones independientes. Barras: DE entre tres réplicas; no incluyen incertidumbre de concentración o blanco.

Los correos de ActionPlan se refieren a 180° y contienen hipótesis y resultados aproximados previos. No se reutilizan como mediciones ni se ejecutan sus solicitudes de envío.

## Calidad

A 180°, 410 y 435 nm contienen valores próximos a 2³² (30 y 45 medias de réplica respectivamente). Se conservan en tabla; se omiten de la figura ambos canales completos a 180° porque también hay valores parciales contaminados inferiores a 10⁹. No se emplean en ajustes. El canal 485 nm es inestable en ambas geometrías y tampoco se usa en ajustes. No se ha determinado la causa instrumental.

Los dos dark registran cero en todos sus valores. No permiten concluir que el ruido físico sea cero. Los canales de baja señal presentan cuantización: una DE de cero no significa precisión perfecta.

## Canales decrecientes a 180°

T = (I − dark)/(blanco − dark). El blanco es la media de tres series de diez lecturas. Ajuste ordinario ln(T) = −k C, intercepto fijado a cero por normalización. Se incluye una alternativa con intercepto libre para diagnosticar sensibilidad. k se expresa en mL/µg.

| Canal (nm) | k, origen | k, intercepto libre | Intercepto libre | R² log, origen |
|---|---:|---:|---:|---:|
| 510 | 0.2556 | 0.2452 | -0.0213 | 0.9852 |
| 645 | 0.2914 | 0.2837 | -0.0159 | 0.9862 |
| 705 | 0.2725 | 0.2572 | -0.0314 | 0.9831 |
| 900 | 0.3103 | 0.3028 | -0.0153 | 0.9864 |

Las correlaciones entre las cuatro curvas son muy altas, pero no demuestran igualdad de pendientes. Comparar las pendientes y sus residuos evita confundir covariación con curvas idénticas. Estos ajustes descriptivos no distinguen absorción, dispersión, luz parásita ni deriva.

## Respuesta a 680 nm

Se ajusta ΔI = I680 − blanco680 con tres alternativas: lineal a·C; saturación A·(1−exp(−kC)); Stam a·C·exp(−kC). Todas pasan por cero tras restar el blanco. Ajustes ordinarios sin ponderación para evitar pesos infinitos en canales cuantizados. Se compara el error en la misma escala de señal.

La validación deja fuera una muestra completa por vez (20 ajustes). RMSE LOO evalúa predicción de señal, no de concentración; utiliza el blanco de la misma sesión. Es validación interna, no validación con un nuevo extracto o día.

| Geometría | Modelo | Parámetros en orden a o A, k | RMSE (u.i.) | RMSE LOO (u.i.) | R² |
|---|---|---|---:|---:|---:|
| 180° | Lineal | 26.4444 | 5.959 | 6.323 | 0.8956 |
| 180° | Saturación | 94.9688, 0.4384 | 2.194 | 2.419 | 0.9859 |
| 180° | Stam | 40.4650, 0.1874 | 2.228 | 2.446 | 0.9854 |
| 90° | Lineal | 50.3279 | 12.901 | 13.592 | 0.8513 |
| 90° | Saturación | 163.0851, 0.5257 | 4.000 | 4.257 | 0.9857 |
| 90° | Stam | 82.2195, 0.2168 | 4.185 | 4.426 | 0.9844 |

## Resultados principales

A 180°, los cuatro k están entre 0,2556 y 0,3103 mL/µg: tendencias muy correlacionadas, pero pendientes distintas. Los residuos contienen desviaciones compartidas, incluida sample19 (2,85 µg/mL). No deben interpretarse los R² altos como ajuste perfecto.

A 680 nm, saturación y Stam predicen la señal con errores internos muy próximos: RMSE LOO 2,42 y 2,45 u.i. a 180°, y 4,26 y 4,43 u.i. a 90°. La diferencia es demasiado pequeña para identificar un mecanismo. Los errores son mayores que muchas barras entre réplicas, especialmente a baja concentración: queda estructura sin explicar.

El blanco a 680 nm baja de 53,35 u.i. a 180° a 0,88 u.i. a 90°. El incremento neto en sample20 es 69,90 y 130,49 u.i., respectivamente. Esto describe mayor señal sobre blanco en la sesión a 90°, no demuestra por sí solo mayor exactitud de concentración.

El canal 730 nm también aumenta marcadamente a 90°. Por ello no conviene reducir de antemano esta geometría al canal 680. La magnitud instrumental de canales diferentes no equivale a una comparación de potencia óptica.

## Interpretación y límites

La comparación de modelos permite describir la curvatura, pero no identificar por sí sola un mecanismo físico. Restar el blanco produce un incremento neto; no garantiza aislar fluorescencia pura. No se debe llamar turbidez a toda atenuación en un extracto de hoja.

La geometría y la sesión están confundidas: se adquirieron secuencialmente. La concentración también sigue el orden de adquisición aparente. Los blancos disponibles preceden las muestras según las marcas temporales del ZIP; faltan blancos intercalados para separar deriva. Las marcas del ZIP no sustituyen un registro de adquisición.

Antes de concluir que una geometría tiene mejor sensibilidad analítica o menor límite de detección, confirmar mismos ajustes de ganancia, integración y excitación, y validar con blancos y muestras independientes. No se calcula un límite de detección robusto con estos archivos.

No se extrapolan los ajustes fuera de 0,15–3,00 µg/mL. Para calibración predictiva final de concentración se necesita evaluar el modelo inverso con validación agrupada e independiente; el R² de señal no es una medida de exactitud de concentración.

## Archivos

- comparacion_ajustes.png: diagnóstico de cuatro canales y modelos a 680 nm.

- 18_canales.png: todas las respuestas por concentración.

- residuos.png: desviaciones de los ajustes frente a concentración.

- datos_integrados.csv: datos unidos, blancos, DE y banderas.

- ajustes.json: parámetros y errores sin redondeo.

- ../analizar.py: análisis reproducible con numpy, scipy y matplotlib.