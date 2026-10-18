# Relación con 645 nm, sin blanco

> Informe histórico de exploración. La decisión vigente es 85 → 9 con blanco; consultar [articulo.md](../articulo.md). Este informe conserva sus resultados originales y no es la guía actual del manuscrito.

C (µg/mL) = 24.62904595 -3.46519495 × ln(I645).
ln es el logaritmo natural. Los coeficientes se ajustan solo con las 11 muestras y se aplican sin cambios a las nueve y las 85. No se utiliza blanco ni I680. Las predicciones negativas se conservan para mostrar el comportamiento real de la ecuación.

| Grupo de comprobación | R² predictivo | RMSE (µg/mL) | MAE (µg/mL) | Sesgo (µg/mL) | Error máximo (µg/mL) |
|---|---|---|---|---|---|
| 9 | 0.88934 | 0.40507 | 0.32538 | +0.32538 | 0.81687 |
| 85 | 0.89057 | 0.61848 | 0.36077 | +0.18448 | 2.94411 |


Cada figura muestra los puntos de referencia sobre la curva y la concentración predicha frente a la referencia. La diagonal representa predicción perfecta. La línea discontinua de la curva marca su extensión fuera del intervalo de I645 usado para calibrar.
La calibración de 11 cubre 0,7944–3,07062 µg/mL. Las nueve cubren 0,0244–3,9098 y las 85 cubren 0,02384–7,98964. Hay extrapolación de la calibración en ambos grupos, especialmente a concentraciones altas del grupo de 85. El ajuste sobre las 11 no establece exactitud sobre esos otros rangos.
La transferencia con I645 sola es peor que con el cociente de dos canales en las nueve muestras. El error calculado corresponde a todos los puntos completos, sin eliminar atípicos ni reajustar en las tandas de comparación. Los tres Excel originales se verifican con SHA-256 y permanecen intactos.
