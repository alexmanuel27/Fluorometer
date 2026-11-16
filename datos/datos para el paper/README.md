# Extractos: datos y análisis para el paper

**Para preparar el manuscrito, empezar por [00_LEEME_DANIELA.md](00_LEEME_DANIELA.md):** figuras seleccionadas, pies en inglés, tablas, fuentes, reproducción y límites. Este índice conserva el detalle del análisis de extractos.

El rango de referencia es **0,15–3 µg/mL**, más el **blanco medido a 0 µg/mL**. Las concentraciones se toman del Excel externo al ZIP, sin recalcularlas. Excitación indicada por Alex: LED azul de 430 nm. Se analizan por separado 90° y 180°.

- [Informe y ecuaciones](resultados/informe.md): selección de canales, comparación de modelos, validación por muestra y límites.
- [Elección de configuración con toda la evidencia](resultados/decision_configuracion.md): integra diluciones, partículas, correcciones multicanal y revisión de Daniela.
- [Figura principal](resultados/figuras/01_figura_principal.png) · [SVG editable](resultados/figuras/01_figura_principal.svg): respuesta roja y predicción de concentración con validación anidada.
- [Residuos de la selección anidada](resultados/figuras/03_residuos.png) y [revisión comparando los mismos cuadráticos](resultados/figuras/05_revision_residuos.png): errores en µg/mL y relativos, sin eliminar muestras. La [síntesis](resultados/decision_configuracion.md) explica el patrón compartido y la sensibilidad a la muestra 19.
- Los 18 canales: [90°](resultados/figuras/02_canales_90.png) · [180°](resultados/figuras/02_canales_180.png).
- [Datos procesados](resultados/medias.csv), [referencias y blanco](resultados/concentraciones.csv), [modelos y parámetros](resultados/modelos.csv), [predicciones fuera del ajuste](resultados/predicciones.csv).

Alex selecciona **90° y 680 nm** el 16 de noviembre de 2026; la calibración cuadrática de extracto sigue siendo una candidata empírica con residuos estructurados y errores relativos grandes en el extremo inferior. A 180°, el modelo sencillo elegido para concentración usa ln(I810/B810), una señal decreciente que no se identifica como fluorescencia. El informe distingue este resultado de la alternativa roja de 680 nm. Añadir canales no aporta una mejora convincente en la validación anidada.

## Reproducir

Ejecutar `python3 analizar_extractos.py` desde esta carpeta, en un entorno con NumPy, SciPy y Matplotlib. Se regeneran únicamente los resultados en `resultados/`. La interpretación del informe corresponde a esta serie concreta de noviembre; revisarla antes de sustituir las fuentes por otra serie.

La comprobación posterior de fondo escalado, residuos y sensibilidad se reproduce con `python3 comparar_correccion_fondo.py`; reutiliza los ajustes originales y escribe sus tablas y `05_revision_residuos`, sin repetir la selección de modelos ni sustituir las salidas anteriores.

Se conservan sin modificar `dataCruda.zip`, `dataCruda/` y `reCalibration_20samples.xlsx`. Las huellas de las fuentes y las versiones usadas están en [trazabilidad](resultados/trazabilidad.json).

La validación es interna y comparte el blanco de sesión. No valida nuevas sesiones o extractos, selectividad química ni límites de detección.

## Ensayo posterior con caolín

El [análisis de extracto con partículas](kaolin/README.md) compara las dos geometrías con controles de etanol, extracto puro y dos cargas nominales de caolín. Favorece 90°/680 nm como respuesta directa estable; 180° aporta información del fondo y permite probar una corrección multicanal exploratoria. Sus resultados y figuras están separados del análisis de diluciones puras.

## Cultivos de algas

La [aplicación a cultivos](algas/README.md) mantiene los coeficientes de 90°/680 nm y utiliza el medio sin algas como blanco de sesión. **El foco actual es solo AO**; CV se conserva como histórico. La [figura AO para el paper](algas/resultados/figuras/03_AO_paper.png) y la [tabla AO](algas/resultados/predicciones_AO.csv) recogen diez niveles. Sin concentraciones independientes de clorofila, se informan equivalentes de extracto; nueve de las diez salidas AO quedan por debajo de 0,15 µg/mL.
