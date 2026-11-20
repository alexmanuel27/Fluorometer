> **Selección vigente desde el 20/11/2026: 90°/680 nm y modelo lineal.** Explicación histórica de la conversión cuadrática AO. [Abrir la versión actual](../../lineal_90_680/INFORME.md).

# Cómo leer el resultado del modelo: solo AO

Desde el 16 de noviembre de 2026, Alex limita el trabajo posterior a AO. Se mantienen los resultados AO/CV anteriores como histórico. No se modifican coeficientes ni lecturas.

La [revisión bibliográfica posterior sobre la relación in vivo–extracto](relacion_in_vivo_extracto.md) aborda una cuestión distinta de esta conversión numérica: cómo relacionar la respuesta del cultivo con la clorofila determinada mediante extracción en muestras del mismo cultivo.

La figura anterior mostraba dos magnitudes distintas: intensidad en unidades del sensor y concentración equivalente en µg/mL. La curva de la derecha representaba la salida de la ecuación frente a la cantidad relativa; no era un nuevo ajuste a concentraciones conocidas de AO. Además, el eje horizontal era logarítmico. El valor relativo 1 no significa 1 µg/mL.

## Conversión de AO10 paso a paso

1. Intensidad medida media a 680 nm: **24,0303 u.a.**
2. Referencia del medio sin algas: **0,4940 u.a.**
3. Intensidad neta: `x = 24,0303 − 0,4940 = 23,5362 u.a.`
4. Ecuación fijada: `C_eq = −0,0171464 + 0,00784969·x + 0,000110942·x²`.
5. Sustituyendo: `C_eq = −0,0171464 + 0,1847522 + 0,0614571 = 0,2290629 µg/mL`.

La semejanza con dividir entre 100 es casual para AO10: esa división daría 0,2353624. No existe un divisor constante:

| Muestra | Cantidad relativa | Intensidad neta (u.a.) | Intensidad / 100 | Resultado del modelo (µg/mL) |
|---|---:|---:|---:|---:|
| AO08 | 0,25 | 8,5041 | 0,0850 | 0,0576 |
| AO09 | 0,50 | 16,8318 | 0,1683 | 0,1464 |
| AO10 | 1,00 | 23,5362 | 0,2354 | 0,2291 |

La columna «intensidad / 100» es solo una comparación aritmética para explicar la escala; no tiene una conversión física a µg/mL justificada.

## Nueva figura

[PNG](figuras/02_explicacion_modelo_AO.png) · [SVG](figuras/02_explicacion_modelo_AO.svg) · [Tabla solo AO](predicciones_AO.csv).

El panel A utiliza ejes lineales y muestra la intensidad AO frente a la cantidad relativa. El panel B muestra directamente la función que transforma una intensidad en concentración equivalente. Los puntos AO se colocan sobre la curva porque se calcularon con ella, no porque se hayan contrastado con concentraciones conocidas de AO.

El cuadrado coral corresponde al primer extracto de referencia: señal neta de 23,6068 u.a. y concentración asignada de 0,15 µg/mL. AO10 tiene casi esa misma intensidad, pero la ecuación devuelve aproximadamente 0,229. Esto refleja el desajuste de la calibración en su extremo inferior ya documentado en los residuos; la curva no pasa exactamente por cada extracto medido. La línea discontinua señala la zona entre el blanco y el primer extracto positivo.

Aplicar la misma ecuación a **ambas** intensidades aclara el origen de la diferencia:

| Muestra | Intensidad neta (u.a.) | Concentración de referencia conocida (µg/mL) | Salida de la misma ecuación (µg/mL) |
|---|---:|---:|---:|
| Primer extracto | 23,606818 | 0,150 | 0,229986 |
| AO10 | 23,536244 | No disponible | 0,229063 |

Las dos predicciones difieren solo 0,000923 µg/mL. El contraste entre 0,15 y 0,229 no es una diferencia de concentración observada entre extracto y cultivo: mezcla la referencia conocida del extracto con la salida del ajuste. En el propio extracto de referencia, la curva global sobreestima en 0,079986 µg/mL. Es un error del ajuste completo en ese nivel, no un error de AO cuantificado ni una corrección por medir células intactas. El valor 0,15 nunca fue una concentración de referencia de AO10.

El resultado equivale a lo que devuelve la calibración de extracto para esa intensidad. La concentración real de clorofila de AO sigue sin conocerse; no se puede determinar la exactitud de la conversión. Las salidas negativas de AO01–AO04 se conservan y no significan concentraciones físicas negativas.

Reproducir esta vista desde la carpeta `algas` con `python3 mostrar_modelo_AO.py`. Lee las predicciones guardadas y los coeficientes fijados; no recalcula CV, no ajusta modelos ni altera resultados previos.
