# Informe actual · modelo lineal 90°/680 nm

**Decisión explícita de Alex: 20 de noviembre de 2026.** Modelo global con intercepto libre; no se obliga a pasar por cero y no se ajusta una recta local.

`C_eq [µg/mL] = -0.436013275475 + 0.023914842025 × (I680 − B680)`.

Presentación normalizada: `u = (I680 − B680)/100`; `C_eq = 2.391484u -0.436013` en µg/mL. Escalar la variable no divide la concentración entre 100.

## Extractos: error interno

| Referencias (µg/mL) | n | RMSE (µg/mL) | MAPE (%) | Sesgo (µg/mL) |
|---|---:|---:|---:|---:|
| 0.15–3.00 | 20 | 0.1552 | 8.55 | +0.0203 |
| 0.15–0.60 | 4 | 0.0415 | 11.49 | +0.0262 |
| 0.75–1.20 | 4 | 0.0787 | 8.15 | +0.0783 |
| 1.35–1.80 | 4 | 0.2095 | 13.49 | +0.2065 |
| 1.95–2.40 | 4 | 0.0513 | 2.05 | +0.0077 |
| 2.55–3.00 | 4 | 0.2569 | 7.60 | -0.2175 |

Se mantienen las 20 referencias positivas y el blanco. Las tres adquisiciones se promedian antes de cualquier división. Cada predicción LOO se obtiene sin esa muestra, con blanco de sesión disponible. El error relativo se calcula contra la referencia de cada muestra y no se define para el blanco cero.

La selección de la recta es operativa. Su MAPE global es similar al del cuadrático, pero su RMSE es mayor y conserva sesgos locales. En 1,35–1,80 sobreestima; en 2,55–3,00 subestima. Estas métricas no son un error garantizado ni un intervalo de incertidumbre para cualquier muestra.

## AO: aplicación y negativos

Con el blanco de medio de AO, B680 = 0.494014267 u.a., **9 de las diez medias son negativas**. AO10 da **0.126852 µg/mL equivalentes**. Todos los resultados son inferiores a 0,15 µg/mL. La respuesta neta medida sigue siendo positiva.

La recta predice -0.436013 µg/mL para intensidad neta cero y cruza cero en 18.231911 u.a. Esa raíz no es un límite de detección. El cambio de cuatro negativos del cuadrático a nueve de la recta se debe al cambio del modelo, sin alterar intensidades. No se recortan las salidas ni se interpretan como concentraciones físicas negativas.

Todas las medias AO quedan entre el blanco y el menor patrón positivo de extracto. AO no dispone de una referencia absoluta de clorofila; por tanto, no se puede calcular su error de concentración o validar estos equivalentes. F3 muestra la respuesta medida y S06 conserva la conversión con signo. CV permanece únicamente como antecedente y fuente original.

## Caolín y transferencia

La comparación de señales con partículas conserva su interpretación: a 90° las mezclas mantienen aproximadamente 101,54/101,40% de la respuesta neta del extracto puro; a 180°, 76,96/69,20%. Son porcentajes de señal, no recuperación de concentración. La corrección a 810 nm es exploratoria.

Aplicar la recta a las muestras de caolín es una comprobación de transferencia, documentada separadamente en S09/S10 y en la tabla correspondiente. Las concentraciones nominales y la conservación relativa de señal no validan automáticamente concentraciones obtenidas con coeficientes de otra serie.

## Límites y próximos experimentos

LOD/LOQ no establecidos. Tres archivos de blanco con diez lecturas internas no equivalen a treinta preparaciones independientes; dark nulos no acreditan ruido cero. Faltan validación del extremo bajo, variación entre días/preparaciones y, si se pretende exactitud absoluta en AO, referencia independiente de clorofila. No se aplicó corrección de filtro interno ni se modificó el firmware.

## Archivos

- [Modelo elegido](resultados/modelo_seleccionado.json).
- [Resultados y huellas](resultados/resumen.json).
- [Extractos y errores por muestra](resultados/extractos_muestras.csv).
- [Errores por región](resultados/errores_regiones.csv).
- [AO](resultados/AO_muestras.csv) y [adquisiciones](resultados/AO_adquisiciones.csv).
- [Caolín a 90°](resultados/kaolin_90_muestras.csv).
- [Todas las figuras y pies](FIGURAS_Y_PIES.md).

Reproducir desde la carpeta superior con `python lineal_90_680/generar_entrega.py`, usando su `requirements.txt`. Se escriben solo resultados de esta entrega y sus índices.
