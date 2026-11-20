# Datos para el paper · selección actual lineal 90°/680 nm

**Actualizado el 20 de noviembre de 2026. Alex selecciona 90°, 680 nm y la recta global con intercepto libre.**

- [Empezar por la guía de Daniela](00_LEEME_DANIELA.md).
- [Informe actual](lineal_90_680/INFORME.md), [19 figuras y pies en inglés](lineal_90_680/FIGURAS_Y_PIES.md) y [modelo elegido](lineal_90_680/resultados/modelo_seleccionado.json).
- [Error por región](lineal_90_680/resultados/errores_regiones.csv), [extractos](lineal_90_680/resultados/extractos_muestras.csv) y [AO](lineal_90_680/resultados/AO_muestras.csv).
- [Dudas resueltas y límites pendientes de experimento](dudas.md).

La recta tiene RMSE LOO interno 0,1552 µg/mL y MAPE 8,55%; conserva sesgos locales y no es el mínimo de RMSE entre las funciones ensayadas. En AO da nueve medias equivalentes negativas, conservadas y explicadas sin atribuirles significado de concentración física negativa. CV permanece como histórico.

## Fuentes y ejecución

20 referencias positivas de 0,15–3 µg/mL más blanco a 0, extraídas del Excel externo al ZIP; LED azul de 430 nm. Se conservan `dataCruda.zip`, `dataCruda/` y `reCalibration_20samples.xlsx` sin modificar. Ensayo con [caolín](kaolin/README.md) y [cultivo AO](algas/README.md).

Para la entrega actual: `python lineal_90_680/generar_entrega.py`, con [requirements.txt](requirements.txt). Los resultados actuales quedan en `lineal_90_680/` y no sobrescriben salidas históricas.

## Análisis anteriores, conservados como antecedentes

- [Búsqueda original de funciones y ecuaciones](resultados/informe.md), [elección previa de configuración](resultados/decision_configuracion.md), [modelos ensayados](resultados/modelos.csv) y [predicciones originales](resultados/predicciones.csv).
- [Comparación gráfica lineal/cuadrático del 20 de noviembre](resultados/dudas/04_lineal_vs_cuadratico_curvas.png) y [errores por región de ambos](resultados/dudas/05_lineal_vs_cuadratico_regiones.png). Sus colores históricos no sustituyen la convención de la nueva colección.
- [Guía del 16 de noviembre](00_LEEME_DANIELA_2026-11-16_HISTORICO.md). La anterior aplicación cuadrática de AO está en `algas/resultados/`; sus coeficientes y salidas no son los elegidos ahora.

`analizar_extractos.py`, `comparar_correccion_fondo.py`, `resolver_dudas.py` y los generadores antiguos de algas reproducen sus versiones históricas. No usarlos para sustituir el modelo actual. La validación sigue siendo interna; LOD/LOQ y exactitud absoluta en cultivos no están establecidos. El firmware no cambia.
