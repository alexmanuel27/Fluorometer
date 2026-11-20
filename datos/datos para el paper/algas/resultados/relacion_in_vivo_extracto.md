> **Selección vigente desde el 20/11/2026: 90°/680 nm y modelo lineal.** El contexto bibliográfico se conserva; las conversiones cuadráticas descritas son históricas. [Abrir la versión actual](../../lineal_90_680/INFORME.md).

# Cómo expresar la relación entre cultivo in vivo y clorofila extraída

Consulta bibliográfica del 16 de noviembre de 2026, a petición de Alex. Foco experimental: AO, 90° y canal de 680 nm. Esta nota no ajusta una ecuación ni modifica predicciones.

## Aclaración: calibrar con espinaca y medir cultivos sí tiene precedentes

La indicación anterior de que «falta extraer AO» fue demasiado absoluta si se interpreta como requisito para usar el instrumento o presentar estimaciones. **Se puede aplicar una calibración externa con pigmento vegetal a las lecturas in vivo e informar estimaciones o equivalentes referidos a ese patrón.** Determinar independientemente la clorofila del cultivo permite evaluar el sesgo y la exactitud de esa transferencia; es un objetivo de validación distinto.

Ejemplos comprobados:

- **Leeuw, Boss y Wright (2013)** desarrollaron un fluorómetro económico con LED de 425 nm y geometría de 90°. Ensayaron por separado extracto de espinaca y células vivas de *Thalassiosira weissflogii*, comparando con un WETStar. Las pendientes diferían; los autores no presentaron esa intercomparación como calibración absoluta y consideraron útil la señal para seguir variación aun sin calibración de campo. Es un precedente cercano al equipo, no una demostración de transferencia idéntica entre extracto y cultivo. [Artículo, métodos y sección 3.2](https://pmc.ncbi.nlm.nih.gov/articles/PMC3715229/).
- **Cultivos del estudio sobre limitación de hierro y relación fluorescencia/clorofila**, documentados por la Universidad de Tasmania: las mediciones in vivo se hicieron con un Turner 10-AU y los extractos con 10-AU o Trilogy. Ambos fluorómetros estaban calibrados con patrones de clorofila a de espinaca cuya concentración se midió espectrofotométricamente. Se obtuvieron además pares in vivo–extraído para estudiar la relación. Confirma el uso del patrón vegetal en el instrumento in vivo, compatible con una validación adicional. [Metadatos experimentales del conjunto asociado a 10.1029/2021GL097616](https://researchdata.edu.au/table-s2-iron-paper-2021gl097616/1883610).

Debe describirse qué patrón se utilizó: varios trabajos emplean clorofila a comercial procedente de espinaca; no se debe llamar patrón purificado a nuestro extracto de hoja sin demostrar esa pureza. La estrategia de calibración externa es pertinente, pero el origen vegetal no garantiza la misma respuesta por concentración que la célula intacta.

También se comprobó que González-Olalla et al. (2018), cuyo texto menciona calibración con espinaca, midieron pigmentos previamente extraídos en metanol. Por ello ese artículo no se usa aquí como prueba de medición directa de cultivos intactos con esa curva. [Métodos](https://www.nature.com/articles/s41598-018-28543-2).

## La relación que se quiere estudiar

La literatura compara la **fluorescencia in vivo del cultivo** con la **concentración de clorofila a determinada mediante extracción en muestras del mismo cultivo**. Roesler et al. describen la calibración a partir de medidas pareadas y de series de dilución de fitoplancton, e identifican la relación fluorescencia/clorofila como magnitud relevante para calibrar el sensor. [Roesler et al., 2017](https://doi.org/10.1002/lom3.10185).

La curva de extracto que ya existe caracteriza la respuesta del instrumento a un extracto de hoja. Es una referencia óptica útil; no caracteriza por sí sola la relación fisiológica y óptica de AO vivo con su propio pigmento extraído. Comparar intensidades parecidas no requiere que ambas muestras tengan la misma concentración de clorofila.

## Formas de expresarla

| Expresión | Qué comunica | Cómo se informaría para este equipo |
|---|---|---|
| **Relación fluorescencia in vivo–clorofila a extraída** | Asociación entre la señal del cultivo y la cantidad de pigmento determinada independientemente | Gráfico con clorofila de referencia del cultivo en el eje horizontal y señal neta in vivo a 680 nm en el vertical; indicar número de pares, asociación y dispersión |
| **Fluorescencia in vivo normalizada por clorofila a**, o fluorescencia específica de clorofila | Cuánta señal produce el cultivo por unidad de clorofila | Señal neta a 680 nm por concentración de clorofila del cultivo; si se usa µg/L, unidades operativas u.a.·L/µg |
| **Factor clorofila/fluorescencia** | La conversión inversa: cuánta clorofila corresponde a una unidad de señal en ese cultivo y condiciones | (µg/L)/u.a.; describir blanco, instrumento, excitación, emisión y condiciones del cultivo |

Estas denominaciones y unidades describen una sensibilidad o rendimiento instrumental aparente. No son una medición del rendimiento cuántico de fluorescencia, que requiere relacionar fotones emitidos con fotones absorbidos. Tampoco corresponden al parámetro fotosintético Fv/Fm. Roesler et al. distinguen la señal observada, la absorción específica y el rendimiento cuántico como factores diferentes del problema. [Roesler et al., 2017](https://doi.org/10.1002/lom3.10185).

Proctor y Roesler midieron trece cultivos monoespecíficos con tres excitaciones, incluida 435 nm, y emisión a 695 nm. Encontraron que la respuesta in vivo por clorofila extraída dependía de la especie, la luz de crecimiento y la fase del cultivo. Es evidencia de la existencia de relaciones medibles y variables; no proporciona un factor universal ni un factor ya válido para nuestro LED de 430 nm y canal de 680 nm. [Proctor y Roesler, 2010](https://doi.org/10.4319/lom.2010.8.0695).

## Si se quiere validar la concentración o medir la relación propia de AO

La recomendación instrumental es registrar la fluorescencia in vivo y analizar después la clorofila extraída de una porción representativa de esa misma muestra. Turner Designs lo indica explícitamente para evitar correlacionar el sensor con una muestra de distinta composición. [Manual SCUFA, apéndice C, p. 32](https://docs.turnerdesigns.com/t2/doc/manuals/998-2002.pdf#page=32).

Para nuestro estudio, la concentración obtenida en el disolvente debe referirse al volumen de cultivo original, considerando volumen extraído, volumen de disolvente y diluciones. Así se comparan señal del cultivo y contenido de pigmento del cultivo en una base coherente. Los µg/mL del líquido de extracción no se equiparan automáticamente a los µg/mL del cultivo.

Con varios pares AO puede evaluarse si la señal por clorofila permanece aproximadamente constante o cambia con la densidad o las condiciones. La correlación describe asociación; un factor de conversión requiere valorar también sesgo, dispersión y dominio de uso. La respuesta no tiene por qué ser uno a uno.

## Qué se puede afirmar con las medidas actuales

**AO10 produce una señal neta a 680 nm semejante a la del extracto de referencia de 0,15 µg/mL.** Es una comparación de respuesta óptica bajo los ajustes utilizados. No determina la concentración real de AO10 ni su fluorescencia por unidad de clorofila, porque falta la determinación de clorofila en ese cultivo. El valor 0,229 µg/mL del análisis anterior es la salida de la curva ajustada de extracto; no es una correlación in vivo–in vitro medida.

Para una validación con muestras pareadas, una denominación adecuada es:

**«Relación entre la fluorescencia in vivo a 680 nm y la concentración de clorofila a determinada por extracción en el cultivo AO».**

Para las estimaciones actuales, referidas a la curva de extracto vegetal, una denominación adecuada es:

**«Concentración equivalente de clorofila a estimada por fluorescencia in vivo, mediante calibración con extracto vegetal».**

Para informar solo la señal, también es correcto «Respuesta fluorescente in vivo del cultivo AO, comparada con la respuesta de extractos de concentración conocida». Los equivalentes pueden presentarse sin una nueva extracción AO, declarando patrón, rango y falta de validación de exactitud en el cultivo. En nuestra serie, la mayoría de las salidas están además por debajo de 0,15 µg/mL, una limitación del rango positivo calibrado que debe indicarse independientemente del origen del patrón.

Se conserva la calibración anterior como referencia instrumental. Esta consulta cambia la interpretación y la forma de expresar el objetivo; no demuestra un factor de relación ni una correlación de AO que aún no se hayan medido.
