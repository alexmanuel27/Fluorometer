# AO · aplicación actual del modelo lineal 90°/680 nm

**Actualizado el 20 de noviembre de 2026. Solo AO; CV queda como histórico.** Alex elige la recta global de extracto, con intercepto libre y resta del medio de la sesión de cultivo.

- [Informe actual](../lineal_90_680/INFORME.md) y [modelo seleccionado](../lineal_90_680/resultados/modelo_seleccionado.json).
- [Figura principal: respuesta medida AO](../lineal_90_680/resultados/figuras/F3_AO_respuesta_medida.png) · [SVG](../lineal_90_680/resultados/figuras/F3_AO_respuesta_medida.svg).
- [Aplicación lineal con signo y negativos](../lineal_90_680/resultados/figuras/S06_AO_conversion_lineal.png) · [tabla actual de AO](../lineal_90_680/resultados/AO_muestras.csv).
- [19 figuras y pies](../lineal_90_680/FIGURAS_Y_PIES.md) y [guía de Daniela](../00_LEEME_DANIELA.md).

El medio sin algas se midió con el mismo LED azul y ajustes, según Alex. AO y CV son especies en cultivo con células intactas; no se conoce la concentración absoluta de clorofila. La tabla de cantidades relativas se usa tal como está registrada, sin convertirla en concentración de clorofila.

**Con la recta elegida, nueve de las diez medias AO producen equivalentes negativos y AO10 da 0,126852 µg/mL equivalentes.** Todas las señales netas medias son positivas y menores que la del primer patrón positivo. No recortar salidas ni interpretar su signo como concentración física negativa; tampoco afirmar ausencia de clorofila, no detección o <LOQ. F3 muestra la respuesta medida; S06 documenta la conversión exploratoria.

Para regenerar lo actual, ejecutar `python lineal_90_680/generar_entrega.py` desde la carpeta superior. `aplicar_modelo_90_680.py`, `mostrar_modelo_AO.py` y los archivos de `resultados/` conservan la aplicación cuadrática anterior como histórico; no son el modelo actual. Las fuentes `cultivos.zip`, sus CSV extraídos y `cultivos.xlsx` (realmente TSV) permanecen sin editar.

La [bibliografía in vivo–extracto](resultados/relacion_in_vivo_extracto.md) se conserva como contexto. Validar la exactitud de las concentraciones AO requeriría una referencia independiente; actualmente se informan señales y equivalentes exploratorios. El firmware no cambia.
