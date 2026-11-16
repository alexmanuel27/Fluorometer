# Comparación de geometrías: índice de archivos

**Análisis inicial, conservado como antecedente.** La misma serie de 20 extractos se reanalizó y amplió posteriormente con caolín y cultivos. Alex seleccionó 90°/680 nm el 16 de noviembre. Para el paper, comenzar por la [entrega de noviembre para Daniela](../datos%20para%20el%20paper/00_LEEME_DANIELA.md); las cuestiones que figuran aquí como pendientes corresponden a la fecha de este análisis.

Esta carpeta reúne el análisis exploratorio de 20 muestras de extracto, medidas a 90° y 180°. Alex confirmó que son las mismas muestras en ambas geometrías. Las referencias de concentración aportadas están entre 0,15 y 3 µg/mL. La unidad del ajuste es la media de cada muestra, con tres réplicas por geometría.

## Lectura recomendada

1. [Análisis con concentraciones y calibraciones](resultados/informe_calibracion.md): datos, modelos, figuras, control de calidad y limitaciones.
2. [Comparación y decisión de geometría](resultados/decision_geometria.md): errores de concentración, hipótesis y cuestiones pendientes. Su aviso inicial identifica el protocolo posterior que sustituye propuestas anteriores.
3. [Protocolo unificado del 7 de noviembre](pruebas_2026-11-07.md): propuesta de ensayo con extracto, caolín, LED azul y blanco. No consta aquí que se haya realizado.
4. [Revisión preliminar](informe.md): historial anterior a incorporar las concentraciones. Sus afirmaciones sobre concentraciones pendientes están superadas por el primer documento.

## Fuentes, resultados y reproducción

- [Originales](originales/): plan recibido, archivo de lecturas y Excel con las concentraciones. Conservar sin modificar.
- [Datos integrados](resultados/datos_integrados.csv): muestras, canales, referencias y banderas de calidad. [Resumen de réplicas](resumen_replicas.csv): extracción preliminar.
- Figuras: [18 canales](resultados/18_canales.png), [comparación de ajustes](resultados/comparacion_ajustes.png) y [residuos](resultados/residuos.png).
- Resultados numéricos: [ajustes](resultados/ajustes.json), [comparación de concentración](resultados/comparacion_concentracion.json) y predicciones LOO de [180°](resultados/prediccion_concentracion_180%C2%B0.csv) y [90°](resultados/prediccion_concentracion_90%C2%B0.csv).
- [analizar.py](analizar.py) genera la tabla integrada, los ajustes y las figuras a partir de los originales; [evaluar_geometria.py](evaluar_geometria.py) usa esa tabla para calcular las predicciones de concentración. Requieren Python con NumPy, SciPy y Matplotlib; ejecutar el primero antes del segundo. **Al ejecutarlos se sobrescriben los resultados generados** en `resultados/`.

## Límites para interpretar los resultados

Las dos geometrías se midieron en sesiones sucesivas; sus diferencias no pueden atribuirse exclusivamente al ángulo. A 180°, los canales de 410 y 435 nm presentan valores anómalos próximos a 2³²; 485 nm es inestable en ambas geometrías. Los dark guardados contienen ceros, que no demuestran ausencia de ruido. La validación por muestra es interna y comparte el blanco de sesión: no equivale a una validación independiente entre días o extractos.

La selectividad frente a caolín y la elección definitiva de geometría siguen pendientes. El análisis describe respuestas ópticas; una resta de blanco o un buen ajuste no separan por sí solos fluorescencia, transmisión y dispersión.
