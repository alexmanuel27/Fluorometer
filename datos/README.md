# Datos y manuscrito: empezar aquí

Actualizado el 18 de octubre de 2026. Decisión vigente: **calibrar con las 85 y evaluar transferencia a las nueve, usando ln(B645/I645)**. Las once no participan en el análisis principal actual.

## Documentos vigentes

| Material | Contenido |
|---|---|
| [articulo.md](articulo.md) | Guía para Daniela: foco del paper, función, resultados, explicaciones, seis figuras y próximos pasos |
| [Resumen para Daniela](RESUMEN_PARA_DANIELA.md) | Lectura breve de la decisión y el alcance actual |
| [Análisis principal reproducible](articulo_85_a_9/README.md) | Solo 85 y 9; coeficientes, CV85, transferencia, CSV y figuras |
| [Bibliografía](bibliografia/README.md) | Artículos descargados previamente y notas de comparabilidad |

El paquete nuevo para compartir se llama **Paquete_Daniela_85_a_9_2026-10-18.zip**. Contiene estos documentos, el análisis principal, sus figuras, los dos Excel utilizados y la bibliografía previamente descargada. No contiene el conjunto de once ni sus análisis. No se ha enviado automáticamente a Daniela.

## Datos originales: conservar sin editar

- [Calibración de 85](calibracion_85_puntos%20%281%29.xlsx): Sheet1 A1:D86, 85 mediciones completas.
- [Serie de nueve diluciones](9Samples.xlsx): Sheet1 A1:AL10, una preparación madre.
- El tercer Excel permanece en el repositorio como dato histórico, fuera del alcance y del paquete actuales.

Las copias originales se verifican por SHA-256. Los blancos de sesión utilizados son 1356 para las 85 y 1214 para las nueve. No son constantes universales ni blancos por muestra.

## Historial exploratorio, no resultados principales

Las carpetas siguientes se conservan en su ubicación para no perder trazabilidad ni romper sus referencias internas. **No deben confundirse con la versión vigente del artículo y no se incluyen en el paquete nuevo.**

| Carpetas o archivos históricos | Etapa |
|---|---|
| `analisis_2026-10-18/`, `relacion_645_680_sin_blanco/`, `relacion_645_sin_blanco/` | Exploraciones iniciales de señales y transferencia |
| `comparacion_modelos_11_a_9/`, `validacion_solo_11/`, `cv_11_exclusivo/` | Modelos y CV de la tanda ahora excluida |
| `ajustes_1_2_sobre_85/`, `cv_9_exclusivo/` | Comparaciones previas y propuesta ND sustituida |
| `cv_85_ln645/`, `cv_85_ln645_blanco/` | Etapas previas de CV85 y blanco; contienen comparaciones fuera del alcance actual |
| `ajuste_85_mas_9_blanco/`, `transferencia_9_11_ln645_blanco/`, `todas_combinaciones_ln645_blanco/` | Barrido exploratorio que precedió a la decisión 85 → 9 |
| `historial_documentos/` | Copias intactas del artículo ND y del resumen anteriores a esta reorganización |
| `Paquete_Daniela_2026-10-18.zip` | Paquete anterior, sustituido para compartir la decisión actual |

La selección fue retrospectiva después de explorar los datos disponibles. Conservar ese historial no obliga a usar todas las tandas en el argumento principal, pero evita presentar la elección actual como una validación ciega prefijada.

## Firmware e investigación son versiones diferentes

Esta reorganización **no cambia el firmware ni los .bin**. La ecuación de investigación es nueva; el equipo conserva la fórmula inicial hasta que se implemente y compruebe expresamente la sustitución. Consultar [articulo.md](articulo.md) antes de utilizar coeficientes en el microcontrolador.
