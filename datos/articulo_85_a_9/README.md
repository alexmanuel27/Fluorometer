# Resultados principales del artículo: 85 → 9

Versión fijada el 18 de octubre de 2026. Esta carpeta es la referencia vigente para el manuscrito y no depende de los scripts exploratorios anteriores.

**Función:** Chl(a) [µg/mL] = −0,0621128959 + 2,8428103277 × ln(B645 / media_I645).

Entrenamiento con las 85, blanco 1356. Transferencia a nueve diluciones, blanco 1214. Las nueve no fijan los coeficientes. No se lee el Excel de once.

## Resultados y figuras

| Archivo | Uso |
|---|---|
| [modelo_final.json](modelo_final.json) | Coeficientes, rango, blancos, identificación y procedencia |
| [tabla_resultados.csv](tabla_resultados.csv) | CV85 y transferencia a nueve, separadas |
| [predicciones.csv](predicciones.csv) | 85 predicciones fuera de su entrenamiento y nueve de aplicación fija |
| [errores_menor_y_mayor_1.csv](errores_menor_y_mayor_1.csv) | Errores globales del rango bajo y alto, con recuentos |
| [errores_por_rango.csv](errores_por_rango.csv) | Dieciséis intervalos, incluidos los vacíos |
| [comparacion_blanco_9.csv](comparacion_blanco_9.csv) | Misma calibración de 85, con/sin corrección entre sesiones |
| [predicciones_blanco_9.csv](predicciones_blanco_9.csv) | Comparación individual del efecto del blanco |
| [resultados.json](resultados.json) | Métricas completas, 85 ajustes por turno y versiones |

Las seis figuras tienen PNG para revisión y SVG editable. Los pies propuestos y el papel de cada una están en [articulo.md](../articulo.md).

1. [Diseño del análisis](figuras/figura_01_diseno.png) — [SVG](figuras/figura_01_diseno.svg).
2. [Calibración](figuras/figura_02_calibracion.png) — [SVG](figuras/figura_02_calibracion.svg).
3. [CV85 y residuales](figuras/figura_03_cv85.png) — [SVG](figuras/figura_03_cv85.svg).
4. [Transferencia a nueve y rango bajo](figuras/figura_04_transferencia9.png) — [SVG](figuras/figura_04_transferencia9.svg).
5. [Efecto del blanco](figuras/figura_05_efecto_blanco.png) — [SVG](figuras/figura_05_efecto_blanco.svg).
6. [Errores por concentración](figuras/figura_06_errores_por_rango.png) — [SVG](figuras/figura_06_errores_por_rango.svg).

## Reproducir

Desde la raíz del repositorio, o desde la raíz del paquete descomprimido que contiene la carpeta datos:

```sh
python3 -m pip install -r datos/articulo_85_a_9/requirements.txt
python3 datos/articulo_85_a_9/analisis_publicacion.py
```

El script vuelve a generar únicamente las tablas, el modelo y las figuras de esta carpeta. No modifica los Excel ni el manuscrito. Las dependencias están fijadas a las versiones con las que se verificó esta entrega. Los originales deben conservar sus nombres y permanecer en la carpeta datos, un nivel por encima de esta.

Comprobaciones incluidas: SHA-256 de originales, 85 registros completos y nueve diluciones, coeficientes mediante covarianza, CV por identidad de residuos eliminados, exclusión del punto omitido, equivalencia de normalización por blanco, cobertura y agregación de rangos y recuento de 94 predicciones.

## Interpretación

- CV85 no usa las predicciones del ajuste completo sobre sí mismo. Sus 85 modelos se ajustan con 84 registros por turno.
- La evaluación de nueve es transferencia fija, no CV9. La ecuación final no se recalibra con ellas.
- Las nueve son diluciones de una única preparación. La selección de esta estrategia fue retrospectiva; los indicadores no estiman sin sesgo todo el proceso previo de elegir el modelo.
- Una desviación de las diez lecturas instrumentales no equivale a incertidumbre de concentración. No se han inventado barras de error para las figuras.
- Los rangos sin muestras no tienen error cero. Los dos puntos ≥1 de las nueve no permiten afirmar exactitud uniforme en todo ese intervalo.
- No se determina LOD/LOQ ni desempeño en lagos o sesiones nuevas. La fórmula aún no está desplegada en el firmware.

Las 85 cubren 0,02384–7,98964 µg/mL y las nueve 0,0244–3,9098. La discusión completa y los pendientes editoriales están en [articulo.md](../articulo.md).
