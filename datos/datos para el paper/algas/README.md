# Cultivos AO y CV: aplicación del modelo 90°/680 nm

**Foco actual: solo AO**, por indicación de Alex el 16 de noviembre de 2026. [Explicación de la conversión](resultados/explicacion_AO.md) · [Figura solo AO con ejes lineales](resultados/figuras/02_explicacion_modelo_AO.png) · [Tabla solo AO](resultados/predicciones_AO.csv). Los resultados conjuntos siguientes se conservan como histórico.

**Figura recomendada para el manuscrito:** [AO, PNG](resultados/figuras/03_AO_paper.png) · [SVG editable](resultados/figuras/03_AO_paper.svg). Muestra la señal medida y los equivalentes estimados sin incluir CV. El pie propuesto y el contexto están en la [guía para Daniela](../00_LEEME_DANIELA.md). Se regenera con `python3 mostrar_modelo_AO.py` a partir de las predicciones guardadas.

[Relación cultivo in vivo–clorofila extraída: bibliografía y forma de expresarla](resultados/relacion_in_vivo_extracto.md). Distingue la fluorescencia por unidad de clorofila del cultivo de la aplicación numérica de la curva de extracto de hoja.

La calibración con pigmento de origen vegetal y la lectura posterior de células intactas tienen precedentes bibliográficos. Las salidas actuales pueden informarse como **concentración equivalente de clorofila a estimada por fluorescencia in vivo, mediante calibración con extracto vegetal**. Extraer AO no es un requisito para presentar esas estimaciones; permitiría validar su exactitud en el cultivo.

Alex selecciona 90° y 680 nm el 16 de noviembre de 2026. Confirma que AO y CV son dos especies en cultivo con células intactas; las referencias son medio sin algas medido en las mismas condiciones que la calibración. No se conoce la concentración de clorofila de los cultivos.

Se aplica el cuadrático de extracto con sus coeficientes fijados y el blanco del medio actual. La aplicación literal con el blanco de calibración se conserva como sensibilidad. **Las salidas se expresan como concentraciones equivalentes de extracto, sin validación de concentración en cultivos.**

- [Informe y resultados por nivel](resultados/informe.md).
- Figura conjunta histórica: [AO/CV](resultados/figuras/01_aplicacion_modelo_90_680.png) · [SVG editable](resultados/figuras/01_aplicacion_modelo_90_680.svg).
- [Predicciones de las 20 muestras](resultados/predicciones.csv) y [60 adquisiciones a 680 nm](resultados/adquisiciones_680.csv).
- [Medias de los 18 canales](resultados/medias_18_canales.csv), [referencias](resultados/referencias.csv) y [trazabilidad y resumen](resultados/resumen.json).

AO10 y CV10 dan aproximadamente 0,229 y 0,0237 µg/mL equivalentes. Diecinueve de las veinte salidas quedan por debajo del menor nivel de referencia de 0,15 µg/mL. La señal de AO10 roza la del extracto calibrado más bajo; las demás están más alejadas por debajo. Las salidas negativas se conservan, sin atribuirles significado de concentración física negativa.

La tabla denominada `cultivos.xlsx` es realmente texto separado por tabulaciones. Se conserva intacta y se leen sus cantidades relativas tal como están registradas. Los 136 CSV del ZIP coinciden con los extraídos; se aplicó el modelo únicamente a 90°. Las referencias duplicadas entre AO y CV se consideran compartidas.

Ejecutar `python3 aplicar_modelo_90_680.py` en un entorno con NumPy, SciPy y Matplotlib. Solo se regeneran archivos en `resultados/`. No se ajustan modelos nuevos, no se modifica el firmware y no se aplica corrección de filtro interno.
