# Daniela: entrega actual del modelo lineal 90°/680 nm

**Actualizado el 20 de noviembre de 2026. Alex elige 90°, 680 nm y el modelo lineal global con intercepto libre.** Esta entrega sustituye la recomendación anterior del cuadrático para el material actual del paper. AO es el único cultivo activo; CV y los análisis de octubre quedan como antecedentes.

## Abrir primero

1. [Informe actual: ecuación, error por regiones, residuos y límites](lineal_90_680/INFORME.md).
2. [Galería de las 19 figuras con PNG, SVG y pies en inglés](lineal_90_680/FIGURAS_Y_PIES.md).
3. [Modelo elegido y coeficientes completos](lineal_90_680/resultados/modelo_seleccionado.json).
4. [Respuestas actualizadas a las dudas](dudas.md).

Para compartir todo junto: `datos/Paquete_Daniela_lineal_90_680_2026-11-20.zip`. Dentro del ZIP, empezar por este archivo. El contenido extraído ya incluye esta guía y los archivos enlazados internamente.

## Ecuación actual y su alcance

`C_eq [µg/mL] = −0,436013275475 + 0,023914842025 × (I680 − B680)`.

Con `u = (I680 − B680)/100`, la misma recta se presenta como `C_eq ≈ 2,391484u − 0,436013` µg/mL. Para calcular se conservan los coeficientes completos del JSON; la normalización de intensidad no divide las concentraciones entre 100.

El blanco de la calibración es 0,8821683333 u.a.; el de medio de AO, 0,4940142667 u.a. Cada serie se corrige con su propia referencia y se mantienen los coeficientes de extracto. La decisión es una elección operativa de Alex: no se afirma que la recta tenga menor RMSE que el cuadrático. Tampoco se fuerza el intercepto a cero ni se ajusta una recta solo a bajas concentraciones.

## Figuras para el manuscrito

| Uso propuesto | Figura | Archivos |
|---|---|---|
| Principal F1 | Calibración lineal, predicciones fuera del ajuste y errores | [PNG](lineal_90_680/resultados/figuras/F1_calibracion_lineal.png) · [SVG](lineal_90_680/resultados/figuras/F1_calibracion_lineal.svg) |
| Principal F2 | Controles y mezclas con caolín: 90°/180°; porcentajes de señal | [PNG](lineal_90_680/resultados/figuras/F2_caolin_geometrias.png) · [SVG](lineal_90_680/resultados/figuras/F2_caolin_geometrias.svg) |
| Principal F3 | Respuesta medida de AO; ejes de cantidad relativa lineal y logarítmico | [PNG](lineal_90_680/resultados/figuras/F3_AO_respuesta_medida.png) · [SVG](lineal_90_680/resultados/figuras/F3_AO_respuesta_medida.svg) |
| Necesaria para interpretar F1 | S02: residuos del modelo lineal | [PNG](lineal_90_680/resultados/figuras/S02_residuos_lineal.png) · [SVG](lineal_90_680/resultados/figuras/S02_residuos_lineal.svg) |
| Necesaria para interpretar F1 | S03: MAPE, RMSE y sesgo por región | [PNG](lineal_90_680/resultados/figuras/S03_errores_por_region.png) · [SVG](lineal_90_680/resultados/figuras/S03_errores_por_region.svg) |
| Suplemento de AO | S06: aplicación de la recta y nueve medias negativas conservadas | [PNG](lineal_90_680/resultados/figuras/S06_AO_conversion_lineal.png) · [SVG](lineal_90_680/resultados/figuras/S06_AO_conversion_lineal.svg) |
| Límite de transferencia | S09: comparación entre series al mismo nominal de 3 µg/mL | [PNG](lineal_90_680/resultados/figuras/S09_transferencia_entre_series.png) · [SVG](lineal_90_680/resultados/figuras/S09_transferencia_entre_series.svg) |

La [galería completa](lineal_90_680/FIGURAS_Y_PIES.md) contiene además ampliación baja, comparación con el cuadrático, repetibilidad, blancos, espectros AO de 18 canales, equivalentes exploratorios del ensayo con caolín, espectros de las seis preparaciones y los 18 canales a 90°/180°. Son **19 figuras, cada una en PNG y SVG**, con pies en inglés. Doce son nuevas y siete se conservan por describir mediciones que no dependen de la ecuación elegida.

Los resultados y figuras del cuadrático se conservan como históricos. No mezclar sus valores AO, errores o ecuaciones con los de esta entrega. La [guía del 16 de noviembre](00_LEEME_DANIELA_2026-11-16_HISTORICO.md) documenta aquella versión.

## Resultados que deben acompañar las figuras

| Región de referencia (µg/mL) | n | RMSE lineal (µg/mL) | Error relativo absoluto medio, MAPE (%) |
|---|---:|---:|---:|
| 0,15–0,60 | 4 | 0,0415 | 11,49 |
| 0,75–1,20 | 4 | 0,0787 | 8,15 |
| 1,35–1,80 | 4 | 0,2095 | 13,49 |
| 1,95–2,40 | 4 | 0,0513 | 2,05 |
| 2,55–3,00 | 4 | 0,2569 | 7,60 |
| **Global: 0,15–3,00** | **20** | **0,1552** | **8,55** |

Son errores de validación interna dejando fuera muestras completas, con blanco de sesión disponible. El MAPE no es un intervalo «±8,55%» ni un error garantizado de cualquier muestra. Los residuos conservan estructura. En 0,15 µg/mL, el error relativo LOO es −17,03%; el blanco nominal cero no tiene error relativo definido. La recta predice −0,436013 µg/mL en intensidad neta cero: se muestra, no se oculta.

**AO:** nueve de las diez medias dan equivalentes negativos y AO10 da 0,126852 µg/mL equivalentes. Todas las salidas son inferiores a 0,15; todas las señales netas medias son positivas pero inferiores al menor patrón positivo de extracto. No hay referencia absoluta de clorofila del cultivo. Se usa la respuesta medida como figura principal y la aplicación con signo como suplemento; no se sustituyen negativos por cero ni se etiquetan como ausencia de clorofila, no detección o <LOQ.

**Caolín:** las mezclas conservan aproximadamente 101,54/101,40% de señal neta a 90°, frente a 76,96/69,20% a 180°. Los porcentajes no son recuperación de concentración. La corrección a 810 nm continúa siendo exploratoria; la aplicación de la recta a otra serie se muestra como comprobación de transferencia.

## Tablas actuales y trazabilidad

- [Extractos: medias, blanco y predicciones](lineal_90_680/resultados/extractos_muestras.csv) y [adquisiciones](lineal_90_680/resultados/extractos_adquisiciones.csv).
- [Errores por región](lineal_90_680/resultados/errores_regiones.csv) y [comparación lineal/cuadrático](lineal_90_680/resultados/comparacion_modelos.csv).
- [AO: diez niveles](lineal_90_680/resultados/AO_muestras.csv) y [treinta adquisiciones](lineal_90_680/resultados/AO_adquisiciones.csv).
- [Caolín a 90°: señal y equivalentes exploratorios](lineal_90_680/resultados/kaolin_90_muestras.csv).
- [Blancos de 680 nm](lineal_90_680/resultados/blancos_680.csv), [índice de figuras](lineal_90_680/resultados/indice_figuras.csv) y [resumen con huellas de fuentes](lineal_90_680/resultados/resumen.json).
- [Manifiesto de esta entrega](MANIFIESTO_ENTREGA.csv): rutas, tamaños y SHA-256 de los archivos incluidos, salvo el propio manifiesto.

Fuentes sin modificar: [extractos](dataCruda.zip), [referencias externas de concentración](reCalibration_20samples.xlsx), [caolín](kaolin/kaolin+extracto.zip), [cultivos](algas/cultivos.zip) y [tabla relativa](algas/cultivos.xlsx). La tabla denominada `cultivos.xlsx` es TSV; conservar el original. Las carpetas extraídas también permanecen para inspección directa. Los datos CV originales se incluyen por trazabilidad y no generan nuevas conclusiones.

## Reproducción y antecedentes

Conservar la estructura y ejecutar desde esta carpeta:

```bash
python lineal_90_680/generar_entrega.py
```

Usar las [dependencias fijadas](requirements.txt): Python 3.14.7, NumPy 2.5.4, SciPy 1.18.1 y Matplotlib 3.11.2. El generador reutiliza los lectores y ajustes originales, verifica la recta contra el resultado ya comparado y contrasta LOO con reajustes explícitos. No vuelve a seleccionar entre todos los candidatos. El comando escribe únicamente la entrega `lineal_90_680/`. Los generadores anteriores producen sus análisis históricos y no sustituyen esta selección actual. Windows: POR CONFIRMAR.

Antes de cerrar métodos, confirmar nombre completo de AO, ganancia e integración numéricas, solvente/preparación del extracto de calibración y tiempo entre agitación y lectura. Alex confirma excitación y ajustes iguales y agitación previa. Falta una serie baja densa con preparaciones independientes para evaluar una calibración local, LOD/LOQ y variación entre días. La bibliografía de la [relación in vivo–extracto](algas/resultados/relacion_in_vivo_extracto.md) se conserva como contexto, con su aplicación numérica previa identificada como histórica.

El análisis 85 → 9 de octubre corresponde a otro conjunto y a 645 nm. El firmware mantiene su fórmula inicial: esta actualización corresponde al análisis del paper y no instala la recta en el equipo. No se ha enviado ningún archivo a Daniela.
