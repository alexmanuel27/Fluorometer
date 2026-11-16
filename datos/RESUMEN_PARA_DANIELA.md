# Resumen actual para Daniela: 85 → 9 con blanco

**Resumen de la versión de octubre.** La palabra «actual» del título se refiere a esa etapa. Para la entrega posterior de extractos, caolín y AO, abrir la [guía de noviembre](datos%20para%20el%20paper/00_LEEME_DANIELA.md).

Actualizado el 18 de octubre de 2026. Documento breve de la decisión vigente. El historial completo anterior se conserva en el repositorio, en la carpeta historial_documentos; no forma parte del paquete nuevo.

## Qué hemos decidido

Calibrar únicamente con las **85 mediciones** y aplicar esa ecuación, sin reajustarla, a las **nueve diluciones**. Usar un blanco por sesión. Las once quedan fuera del análisis principal de esta versión.

No utilizaremos ND(680,705) ni entrenaremos con las nueve. No se prepararán nuevos extractos ni se planteará cuantificación directa en lagos dentro del alcance actual.

## Función

**Chl(a) [µg/mL] = −0,0621128959 + 2,8428103277 × ln(B645 / media_I645).**

B645 es el blanco de la sesión: 1356 para la tanda de calibración y 1214 para las nueve. I645 es la intensidad media de la muestra y ln el logaritmo natural. El cociente usa la misma configuración y unidades instrumentales; B e I deben ser positivos y finitos.

La función utiliza el logaritmo del promedio de intensidad, no el promedio de logaritmos. Los canales saturados de 410/435 no participan en ella.

## Resultado

| Evaluación | n | R² predictivo | RMSE (µg/mL) | MAE (µg/mL) | MAPE |
|---|---:|---:|---:|---:|---:|
| CV85: entrenar con 84 y predecir 1 | 85 | 0,94052 | 0,45598 | 0,27406 | 20,86 % |
| Ecuación completa de 85 aplicada a nueve | 9 | 0,99424 | 0,09241 | 0,06937 | 22,80 % |

En las siete diluciones inferiores a 1 µg/mL, MAE = 0,07281 µg/mL y MAPE = 28,88 %. El MAPE es error relativo absoluto medio, no una incertidumbre de ± ese porcentaje. En CV85, las 30 referencias <1 tienen MAPE = 38,61 %.

La corrección por blanco reduce el RMSE sobre las nueve de 0,35419 a 0,09241 µg/mL. Es una mejora observada en esa transferencia concreta, no una garantía para cualquier sesión.

## Foco del paper

Desarrollo de un **instrumento multicanal basado en ESP32 para estimación empírica de clorofila a en extractos etanólicos**, con calibración reproducible, evaluación interna y transferencia retrospectiva a una serie de dilución.

La aportación reúne instrumento y adquisición accesibles, una ecuación pequeña, incorporación del blanco y análisis honesto del error por concentración.

Las nueve proceden de **un único extracto madre**. No son nueve extractos independientes ni una validación prospectiva ciega: ya se exploraron los datos antes de elegir esta estrategia. La función describe la señal de 645; los datos no separan de forma concluyente fluorescencia, fondo y efectos ópticos del montaje.

## Instrumento y estado real

El prototipo usa ESP32, LED azul nominal 430–435 nm y sensor AS7265X de 18 canales, con montaje de LED y detector de frente. El ESP32 sirve una web local en su propio punto de acceso. El firmware actual permite calentamiento programado, diez lecturas por ciclo, visualización de medias y desviaciones, blanco persistente y exportación. El enfriamiento opcional apaga el LED 60 s tras tres ciclos.

Un calentamiento programado de 10 s no acredita estabilidad óptica experimental. Existe una prueba separada de estabilidad del LED, pero no hay resultados temporales de esa prueba en los datos del paper.

**La fórmula del firmware sigue siendo la inicial: −2,7924 × ln(I645) + 20,1264.** La nueva ecuación se ha fijado para el análisis, no se ha instalado ni se han recompilado los .bin en esta entrega.

## Qué falta antes de publicar

Recuperar de los registros existentes la referencia espectrofotométrica, concentración madre y factores de dilución; documentar óptica, cuveta, LED, atenuador, ganancia, integración y blancos; revisar residuales y errores bajos; añadir fotografía y esquema real del equipo; cerrar novedad, autoría y disponibilidad de materiales.

No se afirmará LOD/LOQ, incertidumbre total, exactitud uniforme entre sesiones ni utilidad directa en lagos. Si faltan registros, se declarará en lugar de inventarlos.

## Por dónde empezar

1. [articulo.md](articulo.md): función, alcance, discusión, estructura del manuscrito, seis figuras con pies en inglés y próximos pasos.
2. [Análisis principal](articulo_85_a_9/README.md): tablas, 94 predicciones, modelo fijado y reproducción.
3. [Índice del repo](README.md): distinción entre vigente e histórico.
4. [Bibliografía](bibliografia/README.md): PDF previos y contexto.

El paquete para compartir se llama **Paquete_Daniela_85_a_9_2026-10-18.zip**. Excluye los datos y análisis de las once; conserva los dos Excel utilizados, las seis figuras en PNG/SVG y los materiales necesarios para reproducir esta versión. Está preparado para enviar, no enviado automáticamente.
