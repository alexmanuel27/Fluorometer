# Modelos 1 y 2 aplicados a las 85 muestras

> Informe histórico de exploración. La decisión vigente es 85 → 9 con blanco; consultar [articulo.md](../articulo.md). Este informe conserva sus resultados originales y no es la guía actual del manuscrito.

Coeficientes tomados del análisis exclusivo de las once muestras. No se vuelve a calibrar, no se usa blanco y no se abre el conjunto de nueve.
Las métricas siguientes corresponden a las 85 predicciones externas. No son validación cruzada ni un reajuste sobre las 85.

| Modelo | Ecuación (C en µg/mL) | R² predictivo en 85 | RMSE (µg/mL) | MAE (µg/mL) | Sesgo (µg/mL) | Error máximo (µg/mL) |
|---|---|---|---|---|---|---|
| Ajuste 1: cuadrático en ln(I645) | C = 38.758178 -7.764909 ln(I645) +0.326768 [ln(I645)]² | 0.809244 | 0.816581 | 0.444089 | +0.310070 | 3.384617 |
| Ajuste 2: lineal en ln(I645) | C = 24.629046 -3.465195 ln(I645) | 0.890570 | 0.618485 | 0.360767 | +0.184479 | 2.944114 |

R² predictivo = 1 − Σ(predicción − referencia)² / Σ(referencia − media de referencia)². Sesgo = media(predicción − referencia). Se conservan las 85 muestras y las predicciones negativas.

## Alcance
La calibración cubre 0.79440–3.07062 µg/mL y las 85 cubren 0.02384–7.98964 µg/mL. 44 de las 85 tienen I645 fuera del intervalo usado para calibrar. La línea discontinua muestra esa extrapolación; la zona sombreada indica el intervalo de señal de las once.
El desempeño anterior de CV sobre once corresponde a una sola tanda y a un rango menor. Estas cifras describen la transferencia a otra tanda y otro rango, y no sustituyen aquel resultado.
Se leen las 85 filas completas. Las filas adicionales que solo contienen identificadores no son mediciones y se excluyen. No se eliminan atípicos, no se usan desviaciones instrumentales como pesos y no se recortan resultados.

## Archivos
ajuste_1_85.png y ajuste_2_85.png muestran los datos sobre cada curva y las predicciones frente a la referencia. predicciones_85.csv contiene las 85 predicciones de ambos modelos. resultados_85.json conserva las métricas y la procedencia.
