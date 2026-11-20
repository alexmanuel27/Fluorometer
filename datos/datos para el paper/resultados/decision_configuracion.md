> **Selección vigente desde el 20/11/2026: 90°/680 nm y modelo lineal.** Síntesis histórica de geometría y comparación de funciones. [Abrir la versión actual](../lineal_90_680/INFORME.md).

# Elección de configuración con toda la evidencia disponible

15 de noviembre de 2026. Evaluación basada exclusivamente en las diluciones de extracto, el ensayo con caolín, los controles y la revisión del código aportado.

Actualización del 16 de noviembre: Alex confirma la elección de 90°/680 nm. La [aplicación posterior a cultivos AO/CV](../algas/resultados/informe.md) conserva los coeficientes de extracto y documenta sus límites en esas señales bajas; no constituye validación de clorofila en células intactas.

**Elegiría provisionalmente 90°, excitación azul de 430 nm y 680 nm como canal principal.** Usaría 730 nm como comprobación adicional de la respuesta roja y los canales azules válidos como diagnóstico de la interacción con partículas. La ventaja observada es obtener una respuesta del extracto estable con caolín utilizando la resta habitual del blanco, con poca respuesta del caolín sin extracto. **La revisión de los residuos impide presentar cualquiera de las calibraciones como plenamente adecuada en todo el rango:** ambas conservan estructura y tienen errores relativos grandes en el nivel inferior.

La configuración de 180° es una alternativa interesante para estudiar conjuntamente fondo y señal roja. Una corrección multicanal puede hacerla competitiva en este ensayo; su transferencia a otras concentraciones todavía no está comprobada.

## 1. Qué criterio decide la elección

El objetivo es obtener información de la fluorescencia del extracto cuando también hay partículas. Por ello doy más peso a estas preguntas que al tamaño de los picos o al ajuste en diluciones puras:

1. ¿El caolín sin extracto produce una respuesta que pueda confundirse con la del extracto?
2. ¿La respuesta se conserva al añadir caolín sin cambiar la concentración nominal de clorofila?
3. ¿El resultado requiere una hipótesis de corrección que aún no se ha contrastado fuera de estas mezclas?

El número de canales que cambian no mide por sí solo cuánta información independiente hay sobre clorofila. Una misma disminución puede responder al extracto y al caolín.

## 2. Diluciones puras: ventaja moderada para 90°

Ambas configuraciones responden a la serie de 0,15–3 µg/mL, más el blanco. Para comparar el mismo tipo de señal y función, el cuadrático de 680 nm presenta un RMSE interno dejando fuera muestras de **0,0938 µg/mL a 90° y 0,1197 a 180°**. Son errores de modelos fijados, elegidos tras revisar los datos.

La búsqueda completa, evaluada con validación anidada, da **0,0990 a 90° y 0,1209 µg/mL a 180°**. A 90° se elige finalmente 680 nm cuadrático; a 180°, ln810 como opción sencilla. Este último resultado representa una relación empírica con la concentración en extractos puros; el ensayo con partículas muestra su falta de especificidad para el extracto.

No uso esas pequeñas diferencias de RMSE como prueba de superioridad estadística. El dato más importante de esta primera fase es que 90° ofrece un predictor rojo sencillo y que añadir canales no aporta una ventaja convincente de validación.

Para evaluar también la alternativa de fondo escalado, se añadió una comprobación específica en las diluciones puras. Se reutilizaron los ajustes y particiones por muestra del análisis original; β se obtuvo del blanco de esa serie, sin utilizar las mezclas en los ajustes.

| Señal y función de concentración | RMSE LOO a 90° (µg/mL) | RMSE LOO a 180° (µg/mL) |
|---|---:|---:|
| I680−B680, cuadrático | 0,0938 | 0,1197 |
| I680−(B680/B810)·I810, cuadrático | 0,0917 | 0,1117 |
| I680−(B680/B860)·I860, cuadrático | 0,0933 | 0,1138 |

También se comprobaron las funciones lineal y de saturación; ninguna mejoró estos cuadráticos entre los candidatos ensayados. Son errores internos de candidatos fijados, sin validación anidada de esta nueva comparación ni prueba externa. No deben confundirse con los RMSE anidados de la búsqueda original.

La corrección mejora la predicción en extractos puros a 180°, pero sigue sin superar el cuadrático de 680 nm a 90°. La mejora mínima a 90° con S810 tampoco justifica adoptarlo por defecto: en los controles con caolín introduce respuestas de −4,3 a −6,1% donde el canal 680 directo daba aproximadamente +0,07 a +0,35%. El criterio incluye los controles de partículas, además del ajuste de las diluciones.

### Revisión de residuos: la ventaja de calibración es menos concluyente

Se revisaron la figura de errores de CV anidada del análisis actual y los residuos de los ajustes directos de saturación/Stam del análisis anterior. No son magnitudes intercambiables: los segundos expresan diferencias de intensidad observada menos ajustada; los primeros, concentración predicha menos referencia. Tampoco se puede declarar peor una geometría porque tenga residuos de intensidad mayores: la sensibilidad intensidad/concentración difiere. Además, el panel de un canal a 180° de la CV anidada cambia entre ln810 y lineal460, no representa un único ajuste de 680 nm.

Para comparar la misma señal y función en ambas geometrías, la [nueva figura de residuos](figuras/05_revision_residuos.png) utiliza cuadráticos fijados de 680 nm, con resta de blanco o fondo escalado a 810 nm. Arriba muestra el error firmado en µg/mL; abajo, el error relativo. Se deja fuera cada muestra completa, manteniendo el blanco de sesión disponible. Los resultados de 860 nm también se conservan en los CSV.

1. **Hay estructura, además de dispersión.** En los seis cuadráticos comparados aparecen solo seis tramos de signo consecutivo. Por ejemplo, entre 0,75 y 1,20 µg/mL se subestima sistemáticamente, mientras entre 1,35 y 1,80 se sobreestima. El patrón también aparece en los residuos del ajuste completo, por lo que no se debe únicamente a dejar fuera muestras. El sesgo medio casi cero oculta estos sesgos locales. La corrección a 810/860 nm no los elimina.
2. **Las desviaciones se comparten entre geometrías.** La correlación de sus errores de concentración es 0,966 para 680 nm y 0,964 al corregir con 810 nm. Esto es compatible con factores comunes de preparación, referencia u orden de lectura, o con una aproximación de modelo común. No identifica su causa ni demuestra un error de las concentraciones de referencia. No se aplican pruebas de independencia a estos errores correlacionados y con blanco compartido.
3. **El extremo bajo requiere especial cautela.** A 0,15 µg/mL, el cuadrático de 680 nm predice aproximadamente 0,248 a 90° y 0,241 a 180°: errores de +65,2% y +60,4%. A 180° con corrección a 810 nm, el error es +71,5%. Un RMSE global cercano a 0,1 µg/mL no acredita buena cuantificación relativa en todo el rango ni un límite de cuantificación de 0,15.
4. **La muestra 19 pesa mucho en la comparación.** Su concentración de referencia es 2,85 µg/mL. En 680 nm tiene errores LOO de −0,197 a 90° y −0,330 a 180°, y aporta el 22,2% y el 38,1% de la suma de errores cuadrados, respectivamente. Con fondo a 810 nm a 180°, todavía aporta el 35,4%. No hay evidencia que justifique eliminarla.

Como análisis de sensibilidad, se repitió la CV de estos candidatos fijados retirando la muestra 19 de **todos los ajustes y de la evaluación**. Esta tabla no vuelve a seleccionar canales o funciones ni sustituye los resultados principales:

| Configuración y señal, cuadrático | RMSE con las 20 muestras | RMSE reajustado sin muestra 19, solo sensibilidad |
|---|---:|---:|
| 90°, 680 nm menos blanco | 0,0938 | 0,0850 |
| 90°, fondo escalado a 810 nm | 0,0917 | 0,0833 |
| 180°, 680 nm menos blanco | 0,1197 | 0,0939 |
| 180°, fondo escalado a 810 nm | 0,1117 | 0,0897 |

Todos los valores son µg/mL. La diferencia entre 90°/680 y 180° corregida disminuye de 0,0179 a 0,0047 µg/mL en esa sensibilidad. Por tanto, **no sostendría la elección del ángulo principalmente en el RMSE de calibración**. Las curvas cuadráticas son candidatas prácticas, pero la estructura compartida y los errores del extremo bajo deben resolverse o caracterizarse con otra serie. Buscar una función más flexible sobre estas mismas 20 muestras no demostraría haber resuelto su causa.

Se mantienen todas las muestras en la recomendación y en la figura nueva. La evidencia que más inclina la preferencia hacia 90° sigue siendo la respuesta de los controles y mezclas de caolín que se detalla a continuación.

## 3. Controles y mezclas: evidencia principal para 90°/680

Defino la respuesta relativa como `100·(I_muestra − B)/(I_extracto_puro − B)`, con el blanco de etanol de cada geometría. Para las restas de fondo multicanal se normaliza su propia señal con su propio extracto puro. Son escalas de respuesta, **no porcentajes de concentración recuperada**.

| Geometría y tratamiento | Caolín b sin extracto | Caolín a sin extracto | Extracto + caolín b | Extracto + caolín a |
|---|---:|---:|---:|---:|
| **90°, 680 nm menos etanol** | **+0,07%** | **+0,35%** | **101,54%** | **101,40%** |
| 180°, 680 nm menos etanol | −78,29% | −83,93% | 76,96% | 69,20% |
| 180°, fondo escalado con 810 nm | +2,60% | +2,07% | 103,43% | 99,88% |
| 180°, fondo escalado con 860 nm | +0,83% | +0,64% | 102,38% | 98,52% |

b = 1,25 g/L; a = 2,50 g/L de caolín nominal. Clorofila nominal en extracto y mezclas: 3 µg/mL.

**A 90°, ocurren simultáneamente dos cosas favorables:** el caolín sin extracto queda cerca del blanco a 680 nm y las mezclas conservan aproximadamente la respuesta del extracto puro. El pequeño aumento de 1,4–1,5% se informa como aumento de respuesta; no se convierte en «ausencia total de interferencia».

**A 180°, ambos controles también permiten distinguir la presencia de extracto a 3 µg/mL.** No es una configuración incapaz de detectarlo. El problema para una medida directa es que el fondo cambia mucho: la misma resta de etanol produce una disminución de 23–31% en las mezclas. Los controles de caolín dan respuestas negativas respecto al etanol; esas respuestas negativas no son falsos positivos de fluorescencia.

La señal medida del etanol a 680 nm es 1,764 u.a. a 90° y 45,202 a 180°. Sus cocientes respecto a la lectura del extracto puro son aproximadamente 1,7% y 47,4%, respectivamente. Es una comparación instrumental que muestra la importancia de la referencia; no separa físicamente el fondo presente dentro de cada mezcla ni permite calcular un límite de detección.

## 4. Por qué 680 nm y no cualquier canal que se correlacione

La revisión de las bandas rojas y cercanas a ellas refuerza la elección. A la carga alta de caolín, usando la misma normalización de respuesta a 90°:

| Canal | Control de caolín a | Mezcla con caolín a |
|---|---:|---:|
| 645 nm | +46,31% | 120,27% |
| **680 nm** | **+0,35%** | **101,40%** |
| 705 nm | +14,27% | 110,27% |
| 730 nm | +2,75% | 106,35% |
| 760 nm | +8,03% | 106,34% |
| 810 nm | +26,87% | 116,42% |
| 900 nm | +100,00% | 147,62% |
| 940 nm | +200,00% | 166,67% |

Los porcentajes de los canales débiles son sensibles a que la respuesta del extracto sea pequeña y a la cuantización; no comparan potencia óptica entre bandas. Aun así, el patrón relevante es consistente: 680 nm conserva mejor la respuesta y presenta menos efecto del control de partículas. 730 nm aporta una segunda observación roja útil, pero aquí es algo más sensible al caolín.

Los cocientes 680/730 y otros indicadores ensayados no mejoran automáticamente esa estabilidad. Por ejemplo, la respuesta normalizada del cociente 680/730 a 90° queda aproximadamente en 92% y 79% en las mezclas. No adoptaría ese cociente como corrección por defecto.

Los canales azules de 90° sí aportan información adicional: 435 nm responde mucho al caolín mientras 680 nm permanece casi estable. Se pueden conservar ambos para diagnosticar la muestra sin obligar a que el canal azul corrija la señal roja. No se dispone de una calibración de turbidez en NTU/FNU.

## 5. Qué merece conservarse de 180°

La resta exploratoria `Sⱼ = I680 − (B680/Bⱼ)·Iⱼ` resulta prometedora. El coeficiente sale del etanol, sin ajustarse a los valores de las mezclas. Con 810 nm, la conservación pasa de 77/69% a 103/100%. Con 860 nm, los resultados puntuales se acercan todavía más a los de 90°; deben valorarse junto con la fuerte discretización de ese canal.

Por tanto, **una configuración de 180° corregida puede llegar a ser competitiva**. No baso la elección de 90° en ignorar ese resultado. La preferencia actual se debe a que su señal principal ya funciona bien con menos supuestos de corrección, mientras la selección de bandas auxiliares de 180° se ha explorado en esta misma serie y solo a una concentración no nula de clorofila.

Normalizar la mezcla con el extracto puro de la misma sesión demuestra estabilidad relativa en ese punto. No demuestra que S conserve la sensibilidad ni la relación con concentración al bajar de 3 µg/mL. La relación fondo/canal auxiliar puede cambiar, y una conservación aparente puede incluir compensación entre efectos ópticos.

El comportamiento de 730 nm a 180° es informativo: el extracto puro reduce su lectura respecto al etanol, pero en presencia de caolín las mezclas superan ampliamente a sus controles de partículas. Esto respalda estudiar una contribución roja superpuesta a un fondo cambiante. No autoriza a identificar toda diferencia como fluorescencia pura.

Además, ln810 solo, buen predictor en diluciones puras, responde intensamente al caolín sin extracto. Por ello no lo usaría como señal principal de clorofila en una matriz con partículas. Su uso como variable de fondo en una corrección es una función distinta.

## 6. Qué cambia la revisión del código de Daniela

La reproducción con los CSV locales confirmó que lectura, medias y resta de etanol coinciden hasta redondeo numérico. Las diferencias de apariencia se explican principalmente por la escala de los ejes. Las inconsistencias entre porcentajes raw/netos y las etiquetas con doble signo deben corregirse antes de interpretar esas etiquetas.

Los valores anómalos de 410/435 nm a 180° afectan a la representación y al procesamiento de esas bandas. No los utilizo como prueba de que el ángulo de 180° sea intrínsecamente peor: su causa instrumental no está resuelta y podría corregirse. La preferencia por 90° se mantiene usando 680 nm y los controles de partículas, sin depender de esas bandas anómalas. 485 nm es inestable en ambas configuraciones.

## 7. Hasta dónde llega esta elección

- El caolín se ensayó solo con clorofila nominal de **3 µg/mL**, el extremo alto de la calibración. No se ha demostrado el mismo comportamiento en muestras de baja concentración.
- Tres adquisiciones de una preparación describen repetibilidad de lectura; no sustituyen preparaciones independientes. Las condiciones se midieron por bloques y las geometrías en sesiones sucesivas.
- Alex confirma mismos ajustes entre las geometrías y agitación antes de leer. El tiempo de espera, la concentración real de clorofila después del contacto con caolín y los blancos intercalados no están documentados.
- Las respuestas del extracto nominal de 3 µg/mL cambian entre conjuntos: −22,8% a 90° y −28,4% a 180° a 680 nm después del blanco. No se conoce la causa. Esta diferencia impide presentar cualquiera de las calibraciones como validada entre sesiones/preparaciones.
- La estabilidad de una banda y sus controles respalda su utilidad, pero no demuestra que toda la señal de la mezcla sea exclusivamente fluorescencia de clorofila a. La serie es un extracto, no una prueba de especificidad frente a todos sus pigmentos ni frente a partículas naturales.
- Los dark nulos no permiten comparar límites de detección físicos entre geometrías. La menor señal de blanco de 90° no basta para calcularlos.

## Recomendación práctica

**Si hay que elegir una sola configuración con lo medido, elegir provisionalmente 90°/430 nm de excitación/680 nm de lectura principal.** Conservar los 18 canales, usando 730 como apoyo y el azul como diagnóstico. Esta elección se apoya principalmente en la estabilidad relativa frente al caolín a 3 µg/mL. La calibración cuadrática de 680 es una candidata empírica que aún presenta residuos estructurados y errores relativos grandes a baja concentración; no aplicar sus coeficientes a estas mezclas como si ya existiera una calibración externa.

180° queda como línea de desarrollo para señal roja y fondo conjuntos. La comparación decisiva siguiente sería varias concentraciones no nulas de extracto cruzadas con caolín, preparaciones independientes, orden de lectura equilibrado, espera fija tras agitación, referencia de concentración comprobada y coeficientes de corrección bloqueados antes de ver las muestras nuevas. Deben repetirse en especial los niveles bajos y 2,70–3,00 µg/mL. El criterio sería conservar predicciones de concentración y controles adecuados a lo largo de esa matriz, no obtener un ajuste mejor sobre las mismas mezclas.

Esta es una preferencia operativa para la evidencia disponible; no una demostración de superioridad universal en agua natural.

## Evidencia utilizada

- [Calibración de extractos puros](informe.md) y [métricas de validación](resumen.json).
- [Comprobación adicional de las correcciones en extractos puros](comprobacion_correccion_fondo.csv), reproducible con `../comparar_correccion_fondo.py`.
- [Residuos comparables, PNG](figuras/05_revision_residuos.png) · [SVG](figuras/05_revision_residuos.svg); [errores de cada muestra](residuos_correccion_fondo.csv), [diagnósticos y sensibilidad](diagnostico_residuos.csv), [correlación entre geometrías](correlacion_residuos_geometrias.csv).
- [Ensayo con caolín](../kaolin/resultados/informe.md), [contrastes de todos los canales](../kaolin/resultados/contrastes.csv) y [diagnósticos y correcciones exploratorias](../kaolin/resultados/diagnosticos.csv).
- [Comparación entre sesiones](../kaolin/resultados/comparacion_entre_sesiones.csv).
- [Revisión del código de Daniela](../kaolin/resultados/revision_daniela/revision.md).

Se añadieron la comprobación de candidatos de fondo escalado, los diagnósticos de residuos y el reajuste de sensibilidad descritos en la sección 2. La elección anterior se apoya en los datos experimentales disponibles. La consulta bibliográfica posterior que sigue no modifica las métricas ni aplica una corrección nueva.

## Anexo: ecuación de filtro interno propuesta por Daniela

Consulta del 15 de noviembre de 2026. La ecuación aportada, `Fcorr = Fobs · 10^[(Aex+Aem)/2]`, es una aproximación conocida para corregir el efecto de filtro interno: absorción de la excitación antes de alcanzar el volumen observado y reabsorción de la emisión antes de llegar al detector. HORIBA la incluye en su [manual de Aqualog](https://www.horiba.com/fileadmin/uploads/Scientific/Downloads/UserArea/Fluorescence/Manuals/AquaLog-User-Guide.pdf), con absorbancias medidas y cubeta convencional de 1 × 1 cm.

El factor ½ representa recorridos aproximados de media cubeta para excitación y emisión al observar el centro. No basta que el ángulo sea 90°: el volumen observado y los recorridos efectivos también importan. No se traslada automáticamente a la configuración denominada 180° del equipo. La dependencia de la corrección respecto de la geometría y su calibración instrumental está documentada por [Kubista et al. (1994)](https://doi.org/10.1039/AN9941900417).

Para este ensayo, `Aex` correspondería aproximadamente a 430 nm y `Aem` a 680 nm, con longitudes ópticas conocidas. El Excel suministrado contiene A664 y A648, además de la concentración de referencia; no contiene A430 ni A680. Las intensidades a 435/680 nm bajo LED azul no sustituyen esas absorbancias. En particular, la lectura roja excitada con azul incluye emisión y fondo; no es una medición de transmisión roja. Tampoco se puede sustituir A430 o A680 por ln(I810/B810).

Con caolín, la atenuación de un haz directo incluye dispersión y la detección de fluorescencia puede recoger fotones redirigidos. Aplicar la ecuación utilizando esa atenuación como si toda fuera absorción puede sobrecorregir. [Ranganathan et al. (2023)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9974911/) analizan explícitamente esta misma ecuación y esta limitación en suspensiones coloidales. Esto exige validación en la matriz; no significa que toda corrección del efecto de filtro interno en medios turbios sea imposible.

La ecuación es multiplicativa y no separa un fondo aditivo de la fluorescencia. Por tanto, no sustituye la revisión del blanco ni equivale a `I680−βI810`. Tampoco corrige por sí sola cambios químicos del pigmento. Los residuos estructurados observados no demuestran que su causa sea el filtro interno.

La propuesta merece ensayarse midiendo absorbancia en las mismas preparaciones —idealmente el espectro, incluyendo 430, 680 y 730 nm—, caracterizando los recorridos ópticos y contrastando el resultado en muestras nuevas con caolín y sin él. Una fuente de luz con emisión roja, medida en transmisión, sería necesaria para estimar A680 con el propio equipo; el LED azul no proporciona esa medida. No se ha aplicado esta ecuación a los CSV actuales ni cambia por sí sola la preferencia provisional de geometría.
