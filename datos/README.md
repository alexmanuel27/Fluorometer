# Datos y paper: empezar aquí

**Índice actualizado el 20 de noviembre de 2026.** Los originales y análisis se conservan en sus rutas para mantener la trazabilidad y la ejecución de los generadores.

## Para Daniela: entrega de noviembre

**Abrir [00_LEEME_DANIELA.md](datos%20para%20el%20paper/00_LEEME_DANIELA.md).** Contiene la selección de figuras PNG/SVG, pies propuestos en inglés, tablas, fuentes y límites para redactar el paper.

- [ZIP actual: lineal 90°/680 nm, 20 de noviembre](Paquete_Daniela_lineal_90_680_2026-11-20.zip): copia portátil del material de noviembre. No se ha enviado a Daniela.
- [Extractos y calibración](datos%20para%20el%20paper/README.md): 20 niveles de 0,15–3 µg/mL y blanco a cero; comparación de 90°/180° y revisión de residuos.
- [Caolín](datos%20para%20el%20paper/kaolin/README.md): extracto, etanol y dos cargas de partículas; respuesta relativa y correcciones exploratorias.
- [AO](datos%20para%20el%20paper/algas/README.md): cultivo intacto, medio sin algas y aplicación de la curva de extracto. CV permanece como histórico.

Alex elige **90° y 680 nm** el 16 de noviembre y confirma el **modelo lineal global con intercepto libre** el 20 de noviembre. La colección actual tiene 19 figuras PNG/SVG y pies en inglés. Esa elección no convierte la calibración en una validación externa: conserva sesgos locales y las concentraciones de AO son equivalentes exploratorios referidos al extracto vegetal. La guía identifica los resultados que pueden sostenerse y los que siguen siendo exploratorios.

El primer [análisis de geometrías del 6 de noviembre](analisis_geometrias_2026-11-06/README.md) usa la misma serie de 20 extractos. Se conserva como antecedente y no debe contarse como un conjunto experimental independiente. Su protocolo propuesto no acredita por sí solo que se ejecutaran todas las pruebas planeadas; el ensayo real de caolín se documenta en la entrega actual.

## Etapa de octubre: calibración 85 → 9

Se conserva íntegra la calibración con 85 registros y transferencia fija a nueve diluciones mediante ln(B645/I645). Las once muestras no participan en esa etapa. Sus concentraciones, función, figuras y métricas pertenecen a un conjunto diferente del de noviembre.

| Material de octubre | Contenido |
|---|---|
| [articulo.md](articulo.md) | Guía del manuscrito de esa versión, con métodos, seis figuras y pies |
| [Resumen para Daniela](RESUMEN_PARA_DANIELA.md) | Decisión 85 → 9 y alcance fechado en octubre |
| [Análisis reproducible](articulo_85_a_9/README.md) | Coeficientes, CV85, transferencia, CSV y figuras |
| Paquete del 18 de octubre (archivo histórico no presente en esta copia) | Copia para compartir de esa etapa; distinta de la entrega de noviembre |
| [Bibliografía previamente descargada](bibliografia/README.md) | Documentos y notas de comparabilidad |

Originales de octubre, sin editar:

- [Calibración de 85](calibracion_85_puntos%20%281%29.xlsx): Sheet1 A1:D86.
- [Serie de nueve](9Samples.xlsx): Sheet1 A1:AL10, una preparación madre.
- `11Samples.xlsx`: dato histórico, fuera del análisis 85 → 9 y de la entrega actual de noviembre.

Los blancos 1356 y 1214 de la etapa 85 → 9 no son constantes para otras sesiones. La selección de esa etapa fue retrospectiva y no se presenta como ensayo prospectivo ciego.

## Historial exploratorio

Las carpetas se mantienen en su ubicación. Los documentos de cada etapa se interpretan con su fecha y alcance; sus propuestas no son resultados de experimentos posteriores.

| Carpetas o archivos | Alcance histórico |
|---|---|
| `analisis_2026-10-18/`, `relacion_645_680_sin_blanco/`, `relacion_645_sin_blanco/` | Exploraciones iniciales de señales y transferencia |
| `comparacion_modelos_11_a_9/`, `validacion_solo_11/`, `cv_11_exclusivo/` | Modelos y CV del conjunto de once |
| `ajustes_1_2_sobre_85/`, `cv_9_exclusivo/` | Comparaciones previas y propuesta ND sustituida en octubre |
| `cv_85_ln645/`, `cv_85_ln645_blanco/` | Etapas previas de CV85 y corrección por blanco |
| `ajuste_85_mas_9_blanco/`, `transferencia_9_11_ln645_blanco/`, `todas_combinaciones_ln645_blanco/` | Barrido anterior a la selección 85 → 9 |
| `historial_documentos/` | Copias de versiones anteriores de los documentos de octubre |
| `Paquete_Daniela_2026-10-18.zip` | Paquete anterior de octubre, sustituido entonces por el paquete 85 → 9 |
| `analisis_geometrias_2026-11-06/` | Primera exploración de la misma serie de 20 extractos; ampliada en `datos para el paper/` |

## Firmware y análisis son versiones diferentes

La organización no modifica el firmware ni los binarios. El equipo conserva su fórmula inicial. Las funciones de investigación de 645 nm y 680 nm no se instalan al actualizar documentos o regenerar figuras. Consultar el [README del equipo](../README.md) para uso y estado del firmware.
