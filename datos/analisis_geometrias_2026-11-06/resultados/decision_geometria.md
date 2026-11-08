> Para la jornada del 7 de noviembre, seguir el [protocolo unificado](../pruebas_2026-11-07.md), que sustituye los planes de adquisición anteriores de este documento.

# Decisión de desarrollo — 6 noviembre 2026

Actualización tras aclaración de Alex: la elección entre 90° y 180° queda pendiente de una prueba de selectividad frente a caolín. La recomendación previa de priorizar 90° se basó en extracto puro y no basta para decidir sobre muestras con partículas. Alex no dispone de filtros ópticos; el ensayo inmediato no requiere filtros.

## Evidencia de las sesiones disponibles

| Medida | 180° | 90° |
|---|---:|---:|
| Blanco a 680 nm, u.i. | 53,354 | 0,882 |
| Incremento sobre blanco, sample01, u.i. | 10,833 | 23,607 |
| Incremento sobre blanco, sample20, u.i. | 69,903 | 130,490 |
| RMSE de concentración, validación interna, µg/mL | 0,136 | 0,110 |
| MAE de concentración, µg/mL | 0,102 | 0,088 |
| Mayor error absoluto de concentración, µg/mL | 0,369 | 0,302 |

Método: canal 680 nm, media de las tres réplicas, resta del blanco de sesión. Se retiene una muestra completa, se ajusta ΔI=A(1−exp(−kC)) a las otras 19 y se invierte para la muestra retenida. Se repite para las 20. Mismo modelo en ambas geometrías. El modelo ya fue explorado con esta serie, por lo que no constituye un test externo intacto. Las concentraciones de referencia proceden del Excel suministrado. No hay validación entre días ni incertidumbre de la referencia. La comparación no examina todas las combinaciones multicanal posibles.

La reducción de RMSE es aproximadamente 19 %, sin demostración de superioridad estadística. La caída del blanco es aproximadamente 60 veces, pero un fondo menor no equivale por sí solo a un límite de detección 60 veces menor. No se dispone de información suficiente para atribuir toda la diferencia a geometría frente a ajustes/sesión. Las anomalías azules de 180° requieren revisión instrumental, no prueban por sí mismas un defecto inevitable de esa geometría.

La detección perpendicular evita el trayecto directo de la excitación transmitida y es una base razonable para desarrollar fluorescencia. Esto no elimina dispersión ni efectos de filtro interno. Referencia: [Virtual Labs, IIIT Hyderabad, efectos de filtro interno](https://mfs-iiith.vlabs.ac.in/exp/inner-filter-effects/theory.html). El montaje enfrentado a 180° de este proyecto no debe confundirse con la geometría de reflexión «front-face» de la bibliografía.

## Prueba mínima propuesta para confirmar la elección

1. Registrar solvente, cubeta/paso óptico, ganancia, integración y corriente LED de ambas sesiones. En la comparación nueva, usar los mismos ajustes y el mismo sensor si es viable. Fijar mecánicamente posición y orientación de cubeta. Mantener constante el tiempo de exposición al LED y comprobar estabilidad con blancos.
2. Preparar seis muestras nuevas de un extracto nuevo, con concentraciones objetivo 0,15; 0,30; 0,60; 1,20; 2,00; 3,00 µg/mL. Determinar las concentraciones reales con el método de referencia y usar esos valores en la evaluación, no únicamente los nominales de dilución.
3. Medir cada muestra en ambas geometrías, tres veces retirando y recolocando la cubeta. Guardar los 18 canales y las lecturas internas. Aleatorizar el orden de concentración. Alternar qué geometría se mide primero; si requiere remontar el equipo, usar bloques cortos y comprobar el blanco después de cada remontaje.
4. Registrar dark y blanco al inicio; intercalar un blanco tras cada tres muestras y al final. Repetir el protocolo otro día con preparación nueva. Son 72 adquisiciones de muestra en total: 6 concentraciones × 3 recolocaciones × 2 geometrías × 2 días, más controles.
5. Para el primer test externo, bloquear las calibraciones actuales antes de leer las nuevas muestras. No reajustar con los datos que se usarán para evaluar. Conservar resultados por muestra y día, y errores en µg/mL, además de CV de señal y deriva del blanco.

## Regla operativa propuesta, a acordar según el uso

Umbral de desarrollo sugerido, no norma metrológica: al menos cinco de las seis medias de muestra de cada día con error absoluto ≤ max(0,10 µg/mL, 10 % de la concentración de referencia), y CV de señal neta entre recolocaciones ≤ 5 % por muestra. La tolerancia absoluta evita exigir porcentajes irreales cerca del blanco. Evaluar por separado las muestras de 0,15 y 0,30 µg/mL.

Si 90° cumple en ambos días y 180° no ofrece una mejora reproducible en el error, continuar con 90°. Si ambas cumplen, mantener 90° como opción de fluorometría por su menor fondo observado y menor exposición directa al haz. Si 90° falla y 180° cumple, conservar 180° provisionalmente para esa matriz mientras se diagnostica el problema. Si ambas fallan, revisar preparación/referencia, estabilidad, geometría y calibración antes de cambiar de arquitectura.

Para uso en agua natural o fitoplancton vivo, repetir la validación en esa matriz antes de adoptar una calibración: los resultados del extracto de hoja no establecen selectividad frente a partículas, otros pigmentos o materia disuelta. El canal a 180° podría estudiarse después como medición complementaria; estos datos no validan una corrección universal de turbidez.

## Siguiente información necesaria

- ¿Uso final: extractos en solvente o fitoplancton directamente en agua?
- ¿Ganancia, integración y corriente LED fueron iguales en los dos conjuntos? ¿Qué solvente se utilizó?

Archivos de cálculo: ../evaluar_geometria.py, comparacion_concentracion.json y prediccion_concentracion_*.csv.


## Diferencia de signo entre canales: comprobación adicional

Alex destaca que varios canales aumentan a 90°, mientras que a 180° solo aumenta 680 nm en tendencia general. El signo de la señal total no demuestra exclusividad espectral: una contribución creciente puede quedar oculta por un fondo decreciente.

Ejemplo en sample20 (3 µg/mL), a 180°: blanco730=257,936 u.i.; I730=211,262 u.i.; T900=85,505/213,438=0,4006. Bajo la hipótesis exploratoria de que el fondo de 730 se atenúa con T900, su fondo esperado es 103,331 u.i. y el exceso residual es 107,931 u.i. Por tanto, una señal total que cae de 258 a 211 puede contener una contribución positiva importante. No es una separación física validada: las pendientes de los canales no son idénticas, y tomar 900 como trazador puro del fondo es una hipótesis.

A 90°, la señal de 730 nm menos blanco en sample20 es 125,914 u.i. y la de 680 nm es 130,490 u.i. Las correlaciones entre las medias de 680 y 645/705/730/760/810 superan 0,998. Esto muestra covariación, no independencia ni prueba de emisión real en cada banda. No comparar unidades entre canales como potencias ópticas sin respuesta espectral conocida.

Prueba óptica discriminante propuesta: repetir blanco y dos concentraciones con y sin un filtro de emisión de curva conocida que bloquee el azul y transmita 680–730 nm, en ambas geometrías y con ajustes fijos. Confirmar transmisión en rojo para interpretar pérdidas. Una caída del blanco azul acompañada de persistencia de la señal roja apoyaría una contribución emitida en rojo, sin excluir toda interferencia. Una caída de la respuesta roja mucho mayor que la atenuación esperada por el filtro exigiría revisar fuga de excitación, dispersión y alineación. No se ha comprado ni instalado filtro.

La recomendación de 90° sigue siendo provisional; que solo 680 nm crezca a 180° no basta para preferir esa geometría como más selectiva. La observación de Alex prioriza este diagnóstico óptico antes de cerrar el diseño.


## Prioridad actual: control de caolín sin filtros ópticos

Hipótesis de Alex: a 90° el caolín podría producir aumentos en varios canales y confundirse con extracto; a 180° podría reducir la transmisión sin reproducir el aumento específico de 680 nm. Es una hipótesis razonable y comprobable, pero todavía no hay mediciones de caolín. No está demostrado que los aumentos actuales a 90° se deban a dispersión.

Ensayo de cribado mínimo: cuatro preparaciones en la misma matriz y al mismo volumen final: blanco; extracto; caolín; extracto + caolín. Mantener igual concentración de extracto en las dos preparaciones que lo contienen e igual concentración de caolín en las dos que lo contienen. Elegir una concentración intermedia del intervalo ya medido (por ejemplo 1,20 µg/mL) y una carga de caolín conocida, sin asignarle NTU si no se mide con un instrumento de referencia. La compatibilidad de matriz/solvente y la suspensión deben comprobarse antes de interpretar el ensayo.

Medir 18 canales en ambas geometrías, tres recolocaciones por preparación: 24 adquisiciones, más dark y controles. Mantener ganancia, integración, excitación, orientación y tiempos constantes; homogeneizar sin burbujas y medir tras el mismo intervalo para controlar sedimentación. Alternar orden de geometrías. Registrar masa/concentración de caolín y solvente. Sin compra ni uso requerido de filtros ópticos.

Criterios: (1) caolín solo no debe producir una estimación falsa de pigmento; (2) al añadir caolín manteniendo el pigmento fijo, la respuesta/estimación no debe cambiar más que la tolerancia de desarrollo y la repetibilidad. Examinar la firma de los 18 canales, no solo el signo de 680. Si 180° distingue el extracto del caolín y conserva mejor la estimación en la mezcla, hay evidencia para preferir 180°. Si el caolín no imita el aumento pero oculta el pigmento en la mezcla, hay selectividad cualitativa, pero aún no cuantificación robusta. Un único nivel de caolín es cribado; después repetir con al menos otro nivel y muestras independientes.

Referencia: USGS, interferencias por dispersión y atenuación en fluorómetros de campo: https://pubs.usgs.gov/publication/tm1D11/full . La guía no determina el comportamiento específico de este prototipo.


## Arquitectura que Alex propone evaluar

Alex plantea aprovechar los filtros integrados del AS7265x para medir conjuntamente transmisión y emisión a 180°, con referencia de blanco, y usar el patrón multicanal para distinguir pigmento de partículas. La evaluación debe comparar la selectividad de esa arquitectura completa, no decidir solamente por menor fondo o mayor señal en un canal a 90°.

La ficha oficial de ams OSRAM confirma 18 bandas con filtros de interferencia integrados y FWHM de 20 nm: https://ams-osram.com/products/sensor-solutions/ambient-light-color-spectral-proximity-sensors/ams-as7265x-smart-spectral-sensor . La anchura de banda no demuestra rechazo absoluto fuera de banda ni identifica el origen (transmisión, dispersión o emisión) de los fotones. La magnitud de posibles fugas bajo el LED real no está determinada en este estudio.

El blanco permite referenciar la señal, pero no elimina automáticamente el fondo transmitido que cambia al introducir la muestra. En un modelo simplificado, tras corregir dark: I=B·T+F y por tanto I−B=F−B·(1−T). El análisis multicanal podría estimar T y separar contribuciones; no está validado todavía que un único canal como 900 nm suministre esa corrección para cualquier matriz. Mantener como prueba inmediata los cuatro controles con caolín, sin filtros externos.
