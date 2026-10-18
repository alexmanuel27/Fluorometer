# Selección solo con 11; evaluación posterior en 9

> Informe histórico de exploración. La decisión vigente es 85 → 9 con blanco; consultar [articulo.md](../articulo.md). Este informe conserva sus resultados originales y no es la guía actual del manuscrito.

El procedimiento de entrenamiento abre únicamente 11Samples.xlsx. Compara 59 candidatos predefinidos usando dejar-una-fuera. Las equivalencias numéricas favorecen menor complejidad y ausencia de blanco. El modelo elegido se guarda en modelo_fijado.json antes de que la etapa de evaluación abra 9Samples.xlsx.
Modelo elegido: **ln(I645)**.
C = 24.62904595 -3.46519495 × feature1; features: ln(I645)

CV del modelo elegido sobre 11: RMSE=0.03905 µg/mL, R²=0.99721.
CV anidada del procedimiento completo de selección sobre 11: RMSE=0.06634 µg/mL, R²=0.99194. En cada turno se elige el modelo usando solo las otras diez, con una validación interna.

## Mejores candidatos según las 11
| Modelo | Blanco | RMSE CV11 | R² CV11 |
|---|---|---|---|
| ln(I645) | No | 0.03905 | 0.99721 |
| ln(B645/I645) | 645, sesión | 0.03905 | 0.99721 |
| ln(I645) + ln(I680) | No | 0.03969 | 0.99712 |
| ln(I645) + I680 | No | 0.03980 | 0.99710 |
| ln(I940) | No | 0.04083 | 0.99695 |
| sqrt(I680/I645) | No | 0.04270 | 0.99666 |
| sqrt(B645 × I680/I645) | 645, normalización parcial | 0.04270 | 0.99666 |
| ND(680,645) | No | 0.04366 | 0.99651 |
| Quadratic I680/I645 | No | 0.04416 | 0.99643 |
| ln(I585) | No | 0.04523 | 0.99625 |


## Ocho finalistas: orden fijado por CV11 antes de evaluar las nueve
| Modelo | Blanco | RMSE CV11 | R² predicción 9 | RMSE predicción 9 |
|---|---|---|---|---|
| ln(I645) | No | 0.03905 | 0.88934 | 0.40507 |
| ln(B645/I645) | 645, sesión | 0.03905 | 0.93169 | 0.31824 |
| ln(I645) + ln(I680) | No | 0.03969 | 0.82998 | 0.50210 |
| ln(I645) + I680 | No | 0.03980 | 0.79838 | 0.54677 |
| ln(I940) | No | 0.04083 | 0.87593 | 0.42892 |
| sqrt(I680/I645) | No | 0.04270 | 0.99060 | 0.11809 |
| sqrt(B645 × I680/I645) | 645, normalización parcial | 0.04270 | 0.99589 | 0.07810 |
| ND(680,645) | No | 0.04366 | 0.97025 | 0.21003 |

Esta tabla mantiene el orden determinado por las 11; no se reordena por el error en nueve y no modifica la selección principal.

## Resultado en las nueve después de fijar la ecuación
| n | R² predictivo | RMSE | MAE | Sesgo | Error máximo |
|---|---|---|---|---|---|
| 9 | 0.88934 | 0.40507 | 0.32538 | +0.32538 | 0.81687 |

| ID | Referencia | Predicción | Error |
|---|---|---|---|
| 1 | 0.0244 | 0.1255 | +0.1011 |
| 2 | 0.0489 | 0.1117 | +0.0628 |
| 3 | 0.0977 | 0.1759 | +0.0782 |
| 4 | 0.1955 | 0.3590 | +0.1635 |
| 5 | 0.2932 | 0.5738 | +0.2806 |
| 6 | 0.4887 | 0.8990 | +0.4103 |
| 7 | 0.9775 | 1.4731 | +0.4956 |
| 8 | 1.9549 | 2.4744 | +0.5195 |
| 9 | 3.9098 | 4.7267 | +0.8169 |

Todos los errores de concentración están en µg/mL. No se cambia el modelo ni sus coeficientes después de este resultado.

## Interpretación
En los análisis anteriores los coeficientes también se calcularon con 11, pero las nueve se usaron para comparar y elegir formas funcionales. Este nuevo protocolo elimina ese uso de las nueve durante la selección y el ajuste de esta ejecución.
Las nueve ya fueron examinadas en análisis previos y el catálogo de candidatos fue explorado con ellas. Por tanto, esto es un reanálisis con separación del entrenamiento, no una prueba prospectiva completamente ciega. Para una evaluación ciega se necesitarían muestras nuevas después de fijar el catálogo y la ecuación.
La validación sobre 11 evalúa muestras de una única tanda. No aprende por sí misma la variación entre sesiones. Las nueve incluyen concentraciones fuera del rango 0,7944–3,07062 usado para calibrar. Se conservan todos los puntos y predicciones.
Los blancos de sesión permanecen entre las opciones del catálogo, pero la ecuación ganadora se decide solo con CV11. Un blanco constante dentro de esa sesión no permite aprender la respuesta a cambios de blanco entre sesiones.
