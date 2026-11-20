> **Selección vigente desde el 20/11/2026: 90°/680 nm y modelo lineal.** Guía histórica del 16 de noviembre, sustituida por la entrega actual. [Abrir la versión actual](00_LEEME_DANIELA.md).

# Daniela: material para el paper

**Entrega del 16 de noviembre de 2026.** Este es el punto de entrada del estudio de noviembre: extractos a 90°/180°, ensayo con caolín y aplicación posterior a cultivo AO. Los análisis 85 → 9 de octubre se conservan como antecedentes; sus ecuaciones de 645 nm y métricas pertenecen a otro conjunto.

## 1. Decisión y lectura breve

Alex selecciona **90°, excitación azul nominal de 430 nm y canal de 680 nm**. La evidencia principal es la estabilidad relativa de la respuesta con caolín, además de la calibración en extractos. La geometría elegida no demuestra que la calibración sea exacta para cualquier matriz o concentración.

Para redactar, empezar por estos tres documentos:

1. [Síntesis de la elección de configuración](resultados/decision_configuracion.md): reúne calibración, residuos, caolín, límites y correcciones exploratorias.
2. [Informe de extractos y ecuaciones](resultados/informe.md) y [ensayo con caolín](kaolin/resultados/informe.md): métodos y resultados completos.
3. [Aplicación a AO](algas/resultados/explicacion_AO.md) y [bibliografía sobre cultivo y extracto](algas/resultados/relacion_in_vivo_extracto.md): cómo interpretar y denominar las estimaciones in vivo.

**AO es el único cultivo seleccionado para el trabajo posterior.** CV permanece en los originales y en los análisis conjuntos anteriores como histórico. El firmware conserva su fórmula inicial; el cuadrático de 680 nm se aplica en el análisis posterior de los CSV y no se ha instalado en el instrumento.

## 2. Figuras seleccionadas

Numeración propuesta para organizar la redacción; se puede adaptar a la estructura del manuscrito. Usar SVG para editar y PNG para revisar. La paleta de Alex ya está aplicada.

| Figura | Contenido y lugar recomendado | Archivos |
|---|---|---|
| **F1** | Extractos: respuesta roja y predicciones de validación interna a 90°/180°. Cuerpo del artículo | [PNG](resultados/figuras/01_figura_principal.png) · [SVG](resultados/figuras/01_figura_principal.svg) |
| **F2** | Caolín: señales originales, respuesta relativa y prueba de fondo con 810 nm. Cuerpo del artículo | [PNG](kaolin/resultados/figuras/01_figura_principal.png) · [SVG](kaolin/resultados/figuras/01_figura_principal.svg) |
| **F3** | **Solo AO**: señal medida y estimación equivalente de clorofila, con ejes lineales. Aplicación exploratoria, no validación de exactitud | [PNG](algas/resultados/figuras/03_AO_paper.png) · [SVG](algas/resultados/figuras/03_AO_paper.svg) |
| **S1, necesario junto a F1** | Residuos comparables del mismo cuadrático, errores firmados en µg/mL y relativos. Muestra 19 conservada | [PNG](resultados/figuras/05_revision_residuos.png) · [SVG](resultados/figuras/05_revision_residuos.svg) |
| **S2** | Los 18 canales de las seis preparaciones con caolín: raw arriba y resta de etanol abajo; 90° izquierda y 180° derecha | [PNG](kaolin/resultados/figuras/04_espectros_raw_y_blanco.png) · [SVG](kaolin/resultados/figuras/04_espectros_raw_y_blanco.svg) |
| **S3** | Extractos: revisión de los 18 canales | 90° [PNG](resultados/figuras/02_canales_90.png) · [SVG](resultados/figuras/02_canales_90.svg); 180° [PNG](resultados/figuras/02_canales_180.png) · [SVG](resultados/figuras/02_canales_180.svg) |
| **S4** | Caolín: revisión de los 18 canales | 90° [PNG](kaolin/resultados/figuras/03_18_canales_90.png) · [SVG](kaolin/resultados/figuras/03_18_canales_90.svg); 180° [PNG](kaolin/resultados/figuras/03_18_canales_180.png) · [SVG](kaolin/resultados/figuras/03_18_canales_180.svg) |
| **S5** | Canales rojos y contrastes emparejados con/sin caolín | [PNG](kaolin/resultados/figuras/02_canales_rojos_y_contrastes.png) · [SVG](kaolin/resultados/figuras/02_canales_rojos_y_contrastes.svg) |

S1 debe acompañar la interpretación de F1, en el cuerpo o en el suplemento: el RMSE global oculta errores locales. La [figura anterior de CV anidada](resultados/figuras/03_residuos.png) evalúa procedimientos de selección; a 180° su serie de un canal alterna modelos y no es el cuadrático fijo de 680 nm de S1.

La [explicación gráfica AO](algas/resultados/figuras/02_explicacion_modelo_AO.png) sirve como apoyo a la redacción. Sus puntos calculados sobre la curva no representan una validación independiente y no sustituyen F3. La [figura conjunta AO/CV anterior](algas/resultados/figuras/01_aplicacion_modelo_90_680.png) es histórica.

### Pies propuestos en inglés

**F1.** Optical response and internally validated concentration prediction for plant extracts under nominal 430 nm excitation. (A, B) Session-blank-subtracted signals at 680 and 730 nm for the 90° and 180° configurations. Symbols show means of three acquisitions and error bars their standard deviations. The measured blank is assigned a reference concentration of zero. Lines show the 680 nm quadratic calibration fitted to all calibration points. (C, D) Held-out predictions from nested leave-one-sample-out selection of single-channel and multichannel models. Each held-out unit comprises a complete dilution sample; the session blank remains available. The single-channel procedure at 180° may select different channels across folds. Dashed lines indicate identity. Validation is internal to the supplied series and sessions; structured residuals and low-concentration errors are shown in S1.

**F2.** Effect of nominal kaolin loading on the optical response of plant extract at 90° and 180°. Nominal chlorophyll a concentration was 3 µg/mL in the extract-containing preparations and zero in the controls. (A, B) Measured 680 nm signals. (C) Ethanol-referenced signals normalized to the pure-extract response within each geometry. (D) Corresponding responses after the exploratory transformation S = I680 − βI810, with β calculated from ethanol alone for each geometry. Markers distinguish preparations with and without extract. Error bars describe acquisition variability with the reference scale held fixed. Percentages express optical response, not concentration recovery. Three acquisitions were available per preparation; independent preparation replicates were not documented.

**F3.** In vivo fluorescence response of the AO culture measured at 90°, with nominal 430 nm excitation and the 680 nm channel. (A) Medium-subtracted intensity at the ten relative culture levels supplied in the reference table. (B) Chlorophyll a equivalents calculated using the fixed quadratic extract calibration and the session-medium blank. Points are predictions from the existing extract calibration, without fitting to AO. Error bars describe variation among three acquisitions only. Negative estimates are retained. Shading marks estimates below the lowest positive calibration reference of 0.15 µg/mL and does not define a detection limit. AO chlorophyll concentrations were not measured independently.

## 3. Tablas y valores que sustentan el texto

| Bloque | Tablas que debe consultar Daniela | Interpretación |
|---|---|---|
| Referencias de extractos | [Concentraciones](resultados/concentraciones.csv), [medias y DE](resultados/medias.csv), [canales y calidad](resultados/canales.csv) | 20 niveles de 0,15–3 µg/mL, más blanco asignado a cero; Excel externo como referencia |
| Modelos y validación | [Coeficientes](resultados/coeficientes.json), [todos los candidatos](resultados/modelos.csv), [predicciones internas](resultados/predicciones.csv), [resumen](resultados/resumen.json) | Distinguir modelo fijado de selección anidada; las adquisiciones no son concentraciones independientes |
| Residuos | [Errores por muestra](resultados/residuos_correccion_fondo.csv), [diagnósticos y sensibilidad](resultados/diagnostico_residuos.csv), [correlación entre geometrías](resultados/correlacion_residuos_geometrias.csv) | La sensibilidad sin muestra 19 no sustituye los resultados principales con todas las muestras |
| Caolín | [Preparaciones](kaolin/resultados/preparaciones.csv), [medias](kaolin/resultados/medias.csv), [contrastes](kaolin/resultados/contrastes.csv), [indicadores normalizados](kaolin/resultados/diagnosticos.csv), [coeficientes de fondo](kaolin/resultados/coeficientes_fondo.csv) | b = 1,25 g/L; a = 2,50 g/L; un solo nivel no nulo de clorofila |
| Transferencia entre sesiones | [Comparación de señales](kaolin/resultados/comparacion_entre_sesiones.csv) | No trasladar coeficientes entre sesiones como si estuvieran validados |
| **AO** | [Predicciones solo AO](algas/resultados/predicciones_AO.csv) | Diez niveles; cantidad relativa conocida, concentración real de clorofila desconocida |
| Adquisiciones y espectros de cultivos | [Lecturas a 680 nm](algas/resultados/adquisiciones_680.csv), [18 canales](algas/resultados/medias_18_canales.csv), [referencias](algas/resultados/referencias.csv) | Filtrar `serie=AO`; los archivos conjuntos conservan CV como histórico |

Valores útiles, con su alcance:

- **Calibración fija del mismo cuadrático de 680 nm:** RMSE LOO 0,0938 µg/mL a 90° y 0,1197 a 180°. La búsqueda completa con selección anidada da 0,0990 y 0,1209; son evaluaciones distintas. La selección anidada de un canal mostrada en F1 da 0,0938 y 0,1209.
- **Residuos:** en el primer extracto, Cref = 0,15 µg/mL y la curva completa devuelve 0,229986. El error LOO de ese nivel es distinto del error del ajuste completo. La muestra 19 se mantiene; explica una parte importante de la diferencia entre geometrías. No presentar el buen aspecto global como ausencia de sesgo bajo.
- **Caolín, 680 nm menos etanol:** las mezclas b/a conservan 101,54/101,40% de respuesta a 90°, frente a 76,96/69,20% a 180°. Los controles de caolín a 90° cambian +0,07/+0,35% respecto al etanol.
- **180° con fondo escalado a 810 nm:** 103,43/99,88% en las mezclas. Es una alternativa exploratoria competitiva al único nivel de clorofila ensayado; no se ha demostrado su transferencia a otras concentraciones.
- **AO10:** señal neta 23,536244 u.a.; equivalente calculado 0,229063 µg/mL. Su señal se parece a la del primer extracto de 0,15 µg/mL. La misma ecuación da prácticamente 0,230 para ambos; no se ha medido una diferencia de concentración entre AO10 y ese extracto. Nueve de las diez salidas AO quedan por debajo de 0,15; no se recortan los valores negativos.

## 4. Métodos y límites que deben conservarse

La adquisición guarda 18 canales. Cada CSV espectral de muestra contiene media, DE y n = 10; se combinan tres adquisiciones por condición o nivel. Esas tres adquisiciones describen repetibilidad instrumental y no equivalen a tres preparaciones independientes. Los blancos se comparten dentro de la sesión. Las barras no incluyen toda la incertidumbre de calibración, referencia o transferencia.

La función elegida es `C_eq = −0,0171463960831 + 0,00784968891805·x + 0,000110942424661·x²`, con `x = I680 − B680`. Para la calibración original B680 = 0,8821683333 u.a.; para AO se utilizó el medio propio, B680 = 0,4940142667. Las dos aplicaciones de blanco se conservan en la tabla de AO. El intercepto es libre: no imponer cero ni modificar coeficientes para hacer pasar la curva por AO10 o por el primer extracto.

La denominación para AO es **«concentración equivalente de clorofila a estimada por fluorescencia in vivo, mediante calibración con extracto vegetal»**. La estrategia de patrón vegetal seguida de lectura de células intactas tiene precedentes. Una extracción pareada del propio AO permitiría evaluar exactitud; no es requisito para presentar los equivalentes como estimaciones. Nuestro patrón es un extracto vegetal, no un estándar purificado acreditado.

No afirmar LOD/LOQ a partir de dark nulos, fluorescencia exclusivamente aislada, recuperación de concentración a partir de los porcentajes de caolín, validación externa de los cultivos o superioridad universal de 90°. A 180° los canales 410/435 presentan anomalías próximas a 2³²; 485 es inestable en ambas geometrías. Se conservan las fuentes y las banderas de calidad.

La corrección de filtro interno aportada por Daniela está [discutida en la síntesis](resultados/decision_configuracion.md), pero no se aplicó. Una futura calibración más densa en niveles bajos y la opción de tramos son propuestas, no resultados ya obtenidos.

Datos de método que conviene confirmar al redactar: nombre taxonómico completo de AO; valores numéricos de ganancia e integración por sesión; preparación y solvente de los extractos de calibración; tiempo entre agitación y lectura. Alex confirmó igualdad de ajustes y agitación en los ensayos pertinentes, pero eso no sustituye describir los valores y tiempos en el manuscrito.

## 5. Reproducibilidad y fuentes

Desde esta carpeta, con Python y las [dependencias](requirements.txt):

```sh
python3 -m pip install -r requirements.txt
python3 analizar_extractos.py
python3 comparar_correccion_fondo.py
python3 kaolin/analizar_kaolin.py
```

Los pasos anteriores regeneran sus resultados y pueden tardar por la selección anidada. Para reproducir la aplicación histórica AO/CV, ejecutar `python3 algas/aplicar_modelo_90_680.py`. Para regenerar **solo las vistas AO**, usando las predicciones entregadas: `python3 algas/mostrar_modelo_AO.py`. En Windows, utilizar `python` si ese es el nombre del intérprete instalado. Entorno usado: Python 3.14.7; NumPy 2.5.4; SciPy 1.18.1; Matplotlib 3.11.2. No se ha comprobado aquí la ejecución en Windows.

Los generadores usan rutas relativas a su propio archivo. Conservar la estructura. Regeneran tablas/figuras; no regeneran esta guía ni las notas interpretativas posteriores. No es necesario ejecutarlos para leer la entrega.

| Original | Uso |
|---|---|
| [dataCruda.zip](dataCruda.zip), carpeta `dataCruda/` y [Excel externo](reCalibration_20samples.xlsx) | Serie de extractos y concentraciones; el blanco tiene Cref = 0 |
| [kaolin+extracto.zip](kaolin/kaolin+extracto.zip) y carpeta `kaolin/kaolin+extracto/` | Las seis preparaciones y sus lecturas |
| [cultivos.zip](algas/cultivos.zip) y carpeta `algas/cultivos/` | AO y CV originales, ambas geometrías; foco del análisis actual: AO a 90° |
| [cultivos.xlsx](algas/cultivos.xlsx) | Tabla de cantidades relativas; pese al nombre es texto TSV, no un libro XLSX. Abrir como texto tabulado, sin cambiar el original |

Las huellas y versiones originales están en [extractos](resultados/trazabilidad.json), [caolín](kaolin/resultados/trazabilidad.json) y [cultivos](algas/resultados/resumen.json). El [manifiesto de entrega](MANIFIESTO_ENTREGA_2026-11-16_HISTORICO.csv) inventaría las rutas y huellas incluidas en la copia para compartir, excepto su propia huella. El ZIP `Paquete_Daniela_noviembre_2026-11-16.zip` es una instantánea fechada; ante cambios posteriores, el repositorio contiene la versión más reciente.

## 6. Material de apoyo y antecedentes

- [Revisión del código de Daniela](kaolin/resultados/revision_daniela/revision.md): las medias/restas coinciden con los CSV; diferencias de escalas y etiquetas documentadas. El original `codifgo de daniela/plot90°.py` se conserva y no es el generador de esta entrega.
- [Bibliografía in vivo y extracto](algas/resultados/relacion_in_vivo_extracto.md): enlaces a fuentes primarias y aclaraciones sobre patrones de espinaca y validación.
- Los informes de octubre 85 → 9 y los paquetes del 18 de octubre permanecen en `datos/`, fuera de esta entrega de noviembre. No mezclar sus muestras, ecuaciones de 645 nm, métricas o numeración de figuras con F1–F3.
- El análisis inicial de geometrías del 6 de noviembre usa la misma serie de 20 extractos; no constituye otra cohorte independiente.
- El archivo redundante `kaolin.zip` contiene una copia anterior de esa carpeta y se conserva en el repositorio, pero no se añade a la entrega. Las fuentes activas del ensayo están en `kaolin/kaolin+extracto.zip` y su carpeta extraída.

Esta entrega prepara material para la redacción; no modifica el manuscrito externo ni envía archivos a Daniela.
