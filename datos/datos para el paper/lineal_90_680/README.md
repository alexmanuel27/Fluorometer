# Entrega actual: modelo lineal, 90° y 680 nm

**Elección de Alex del 20 de noviembre de 2026.** Se usa la recta global con intercepto libre que se comparó con el cuadrático; no es un ajuste local ni un ajuste obligado a pasar por cero.

- [Informe con ecuación, errores y límites](INFORME.md).
- [Galería de las 19 figuras, PNG/SVG y pies en inglés](FIGURAS_Y_PIES.md).
- [Modelo seleccionado, coeficientes completos y unidades](resultados/modelo_seleccionado.json).
- [Errores por región](resultados/errores_regiones.csv), [extractos](resultados/extractos_muestras.csv) y [AO](resultados/AO_muestras.csv).
- [Guía para Daniela y fuentes originales](../00_LEEME_DANIELA.md).

`C_eq [µg/mL] = −0,436013275475 + 0,023914842025 × (I680 − B680)`.

En extractos: RMSE interno 0,1552 µg/mL y MAPE 8,55%. La curva conserva sesgos locales. En AO, nueve de las diez medias se convierten en equivalentes negativos; se conservan y explican, sin atribuirles concentración física negativa. No se conoce la concentración absoluta de clorofila del cultivo.

Para el cuerpo del artículo se proponen F1 (calibración lineal), F2 (caolín) y F3 (respuesta medida de AO). Los residuos y errores por región deben acompañar la interpretación. La conversión AO con signo está en S06.

Desde la carpeta superior, ejecutar `python lineal_90_680/generar_entrega.py` con las dependencias de `../requirements.txt`. El generador reutiliza los lectores originales y comprueba coeficientes, predicciones y divisiones por muestra; no cambia fuentes, resultados históricos ni firmware.

LOD/LOQ, variación entre preparaciones/días y exactitud absoluta en AO siguen sin validación experimental. El ZIP del 16 de noviembre es histórico; utilizar la entrega fechada el 20 de noviembre.
