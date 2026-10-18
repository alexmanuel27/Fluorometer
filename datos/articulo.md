# Artículo: ajuste propuesto, enfoque, alcance y próximos pasos

Documento de trabajo para Daniela y Alex. Fecha: 18 de octubre de 2026.

**Propuesta central:** presentar el prototipo como una prueba de concepto de estimación empírica de clorofila a en la serie de nueve diluciones disponible. Usar **ND(680,705)** como candidato principal por su equilibrio entre error global, error absoluto en bajas concentraciones y sencillez.

Esta elección es una **recomendación para consensuar**, no una decisión previamente acordada ni una validación definitiva. No se prepararán nuevos extractos ni se planteará validación en lagos dentro del alcance actual. Este documento no cambia el firmware.

## 1. Ajuste que proponemos utilizar

### Variable y ecuación

Se utilizan las intensidades medias de los canales de **680 y 705 nm**:

```text
x = ND(680,705) = (promedio_I680 − promedio_I705) / (promedio_I680 + promedio_I705)

Chl(a) [µg/mL] = 7.57720894 + 8.47406466 × x
```

Los coeficientes se calcularon para esta propuesta usando **las nueve muestras completas** de `9Samples.xlsx`, hoja `Sheet1`, filas 2–10, sin blanco, sin ponderación por desviaciones y sin incluir las once ni las 85. Se verificaron por un segundo cálculo independiente.

**Estos coeficientes finales no se usaron para calcular las métricas de CV:** en cada turno de validación se estimaron otros coeficientes utilizando solo ocho muestras y se predijo la novena. La ecuación anterior es el reajuste con toda la serie para un posible uso posterior.

En el equipo, el índice se calcularía **a partir de los dos promedios de las 10 lecturas**, como en los datos de calibración. No se sustituirá por el promedio de diez índices individuales sin estudiar si ese cambio altera el resultado.

### Por qué este candidato

| Candidato, evaluado solo mediante CV9 | R² CV9 | RMSE global (µg/mL) | MAE para referencias <1 (µg/mL) | MAPE para referencias <1 |
|---|---:|---:|---:|---:|
| √(I680/I460) | 0,99639 | 0,07318 | 0,06110 | 46,85 % |
| **ND(680,705), propuesto** | **0,99510** | **0,08528** | **0,03439** | **27,99 %** |
| ln(I645) y ln(I680), dos predictores | 0,96305 | 0,23408 | 0,03926 | 23,73 % |

ND(680,705) no gana en todos los indicadores. La raíz del cociente 680/460 gana en RMSE global; el modelo de dos logaritmos gana en porcentaje relativo bajo. Elegimos proponer ND porque conserva buen desempeño global y tiene menor MAE bajo que ambos, con **un predictor y dos coeficientes**, frente a tres coeficientes del modelo de dos logaritmos.

El índice es adimensional y no utiliza los canales saturados de 410/435 nm. Puede cancelar un factor multiplicativo idéntico en ambos canales, pero **no corrige automáticamente fondos aditivos, temperatura, cambios de matriz ni deriva diferente entre canales**. No debe presentarse como una corrección física completa.

### Desempeño observado de ND(680,705)

- CV dejar-una-fuera: nueve turnos, entrenando con ocho cada vez.
- RMSE global: **0,08528 µg/mL**; MAE global: **0,06212 µg/mL**.
- Sesgo global, predicción menos referencia: **+0,01479 µg/mL**.
- Error absoluto máximo de CV: **0,18414 µg/mL**.
- En las siete referencias inferiores a 1 µg/mL: MAE **0,03439 µg/mL**, RMSE **0,04399 µg/mL** y MAPE **27,99 %**.

El 27,99 % es un promedio de errores relativos absolutos de siete predicciones. **No significa una incertidumbre de ±28 %, un intervalo de confianza ni un error máximo garantizado** para nuevas mediciones.

### Condiciones de uso y rango

La serie de referencia cubre **0,0244–3,9098 µg/mL**. El índice observado cubre aproximadamente **−0,89152630 a −0,42870411**. Son intervalos estudiados, **no límites de cuantificación ni garantía de exactitud uniforme**.

Para aplicar la ecuación deben mantenerse montaje, cuveta, solvente, potencia, ganancia, integración y protocolo comparables a los de calibración. Se requieren valores positivos y finitos en ambos canales, denominador positivo y ausencia de saturación en los canales utilizados. Una señal fuera del intervalo observado debe marcarse como fuera del rango estudiado, no aceptarse silenciosamente como cuantificación validada.

Se conserva un blanco por sesión en el flujo del equipo, pero **este ajuste no lo incorpora matemáticamente**. Introducir una corrección por blanco produciría otra calibración y necesitaría una evaluación separada. No se impondrá blanco por muestra.

## 2. Enfoque del paper

### Mensaje central

**Desarrollo de un instrumento portátil, controlado desde una web servida por el propio ESP32, y evaluación exploratoria de calibraciones espectrales sencillas para estimar clorofila a en una serie de dilución.**

La aportación propuesta combina descripción reproducible del prototipo, adquisición promediada, comparación transparente de modelos, análisis del rango bajo y una ecuación pequeña que pueda implementarse en el microcontrolador. La novedad frente a instrumentos ya publicados debe argumentarse mediante comparación bibliográfica; no se afirmará que es el primer fluorómetro de este tipo.

Título provisional en inglés:

> An ESP32-based fluorometer with an embedded web interface: empirical calibration using a chlorophyll-a dilution series

Pregunta de investigación:

> ¿Qué desempeño de validación cruzada ofrecen calibraciones espectrales sencillas en esta serie de dilución y qué limitaciones aparecen a concentraciones bajas?

### Estructura propuesta

1. **Introducción:** motivación, instrumentos de bajo coste relacionados y objetivo acotado.
2. **Instrumento y adquisición:** electrónica, óptica frontal, filtros incorporados del sensor, calentamiento, enfriamiento, canales, promedios, exportación y OTA.
3. **Muestras y referencia:** extracto madre, diluciones, asignación de concentración, solvente y condiciones efectivamente documentadas.
4. **Análisis:** 55 candidatos explorados, exclusión de 410/435 por saturación, CV9 y criterios para proponer ND(680,705).
5. **Resultados:** predicciones fuera del entrenamiento, errores por concentración, comparación con controles y ecuación reajustada con nueve.
6. **Discusión:** comportamiento en bajas, selección exploratoria, dependencia del extracto madre, mecanismo óptico y límites del estudio.
7. **Conclusión y disponibilidad:** resultado demostrado, límites y materiales necesarios para reproducirlo.

Las once y las 85 pueden mencionarse como antecedentes o análisis exploratorios suplementarios, claramente separados. **No se mezclarán con la CV9 ni se presentarán retrospectivamente como una validación externa ciega**, porque ya se examinaron durante la exploración.

## 3. Alcance que defenderemos

### Incluido

- Prototipo ESP32 y sensor de 18 canales; los ajustes utilizan únicamente canales válidos no saturados.
- Serie de **nueve diluciones de un único extracto madre** y concentraciones asignadas por el procedimiento descrito.
- Calibración empírica sin blanco matemático, validación interna y comparación de errores globales y bajos.
- Propuesta de funcionamiento reproducible dentro de las condiciones estudiadas.

### No demostrado y, por tanto, no prometido

- Cuantificación directa de agua de lago o transferencia entre lagos, extractos, especies, días o equipos.
- Validación externa independiente de ND(680,705) como modelo elegido.
- Exactitud de laboratorio de referencia en todo el rango bajo.
- Límite de detección, límite de cuantificación o incertidumbre expandida establecidos.
- Separación completa entre fluorescencia, transmisión, fondo y dispersión en el montaje frontal.

Las nueve diluciones no son nueve extractos independientes; las diez lecturas del sensor tampoco añaden independencia a la preparación. Al omitir la concentración más alta, se entrena hasta 1,9549 y se predice 3,9098 µg/mL: ese turno implica extrapolación y se conserva en las métricas.

Además, el candidato se propuso **después de explorar 55 modelos con estos datos**. Sus métricas de CV son exploratorias por candidato y no estiman sin optimismo todo el proceso de selección. Esta advertencia debe figurar en el manuscrito, incluso si el R² resulta alto.

## 4. Próximos pasos antes de enviar a publicar

### A. Cerrar la referencia y el protocolo con los registros existentes

- [ ] Confirmar con Daniela la concentración del extracto madre, la ecuación de referencia apropiada para el solvente y los cálculos de dilución. Recuperar absorbancias y factores ya medidos si están disponibles; no preparar nuevos extractos.
- [ ] Identificar qué incertidumbres o registros faltan. Si no pueden reconstruirse, declararlo y describir las concentraciones como valores asignados por el procedimiento, sin atribuirles trazabilidad que no se haya demostrado.
- [ ] Documentar cuveta, solvente, trayectoria, geometría, ganancia, integración, atenuador, potencia y secuencia de medición realmente utilizados.
- [ ] Registrar la anomalía de desviación en 485 sin borrar el original ni corregirla por suposición. No afecta directamente a la fórmula propuesta, que utiliza 680/705.

### B. Cerrar el análisis estadístico

- [ ] Consensuar ND(680,705) como candidato principal y fijar por escrito el compromiso entre MAE bajo y error global. No afirmar que es el mínimo de todas las métricas.
- [ ] Presentar las nueve predicciones de CV y sus errores, junto con los dos controles de la tabla anterior. Separar siempre CV, ajuste completo y antecedentes de transferencia.
- [ ] Examinar residuales y sensibilidad a los extremos sin eliminar muestras para mejorar el resultado. Explicar especialmente el turno que extrapola a 3,9098 µg/mL.
- [ ] Si se quiere cuantificar el rendimiento del procedimiento automático de selección, evaluar ese procedimiento mediante CV anidada. Si no se hace, mantener explícito el carácter exploratorio; la CV anidada tampoco convertiría una única serie en varios extractos independientes.
- [ ] Delimitar qué uso práctico permite el error observado. No convertir automáticamente el menor punto de la serie en límite de cuantificación ni seleccionar a posteriori un intervalo favorable sin declararlo exploratorio.

### C. Preparar figuras y materiales reproducibles

- [ ] Esquema óptico/electrónico, fotografía del prototipo y lista de componentes con costes documentados.
- [ ] Relación ND–concentración, predicción de CV frente a referencia y errores absolutos/relativos frente a concentración. La curva reajustada y los puntos de CV deben distinguirse visualmente.
- [ ] Tabla completa de modelos o suplemento, datos y código de análisis con instrucciones y versiones, en un formato reproducible.
- [ ] Verificar que cada tabla y figura se corresponda con los datos y que se conserven los originales. No sustituir los errores calculados por desviaciones instrumentales.
- [ ] Acordar autoría, contribuciones, repositorio público y revista adecuada al alcance de prueba de concepto. La aceptación no puede garantizarse con estos datos.

### D. Implementación, solo después de confirmar la propuesta

- [ ] Sustituir la fórmula de I645 por la ecuación de ND, utilizando los promedios de 680/705, y conservar esos valores en la exportación junto con la versión de calibración.
- [ ] Comprobar que el cálculo del ESP32 coincide con el cálculo de referencia, dentro del redondeo numérico esperado, usando los nueve vectores existentes y casos de entrada inválida.
- [ ] Mostrar advertencias por saturación, señales inválidas y fuera de rango; no ocultarlas mediante recorte automático a cero.
- [ ] Compilar nuevos binarios e identificar claramente su versión. **Nada de esto está implementado en el firmware por este documento.**

No se establece como condición preparar más extractos o medir lagos. Si no hay más mediciones, la publicación debe conservar el alcance exploratorio y dejar pendientes repetibilidad entre sesiones, deriva experimental y límites metrológicos. La comparación entre cálculo y firmware sería una verificación numérica, no una nueva validación experimental de concentración.

## 5. Estado y referencias para trabajar

**Ya disponible:** CV9 de los 55 candidatos, predicciones por muestra, gráficos, resumen histórico y bibliografía descargada. **Calculado para esta propuesta:** ecuación ND reajustada con las nueve y comprobación de que su CV reproduce las predicciones guardadas. **Pendiente:** consenso sobre el modelo, cierre del protocolo y referencia, figuras finales, manuscrito e implementación.

- [Informe de CV9](cv_9_exclusivo/informe.md).
- [Predicciones individuales de CV9](cv_9_exclusivo/predicciones_cv_9.csv).
- [Resumen completo para Daniela](RESUMEN_PARA_DANIELA.md).
- [Bibliografía y PDF descargados](bibliografia/README.md).

El artículo de Sensors 2026 es una comparación conceptual útil, pero sus concentraciones se refieren al agua original tras la extracción. Su MAPE no constituye un umbral de aceptación para nuestra serie. El estudio de Hydrobiologia queda como contexto futuro, no como validación de correcciones en estos extractos.

**Decisión que necesitamos de Daniela y Alex:** confirmar si aceptamos ND(680,705) como ajuste principal de trabajo y el alcance de prueba de concepto descrito aquí.
