> **Selección vigente desde el 20/11/2026: 90°/680 nm y modelo lineal.** Aplicación histórica del cuadrático a cultivos. [Abrir la versión actual](../../lineal_90_680/INFORME.md).

# Aplicación de la calibración de extracto a cultivos AO y CV

16 de noviembre de 2026. Alex elige 90°/680 nm y confirma dos especies en cultivo con células intactas, referencia de medio sin algas y las mismas condiciones instrumentales. No se conocen concentraciones de clorofila de estos cultivos.

## Resultado

La ecuación se puede evaluar, pero sus salidas no validan una concentración de clorofila en células intactas. 19 de las 20 salidas quedan por debajo de 0,15 µg/mL. AO10 da aproximadamente 0,229 µg/mL equivalentes y CV10 0,0237. Todas las medias de señal neta están por debajo de la menor señal de un extracto no blanco calibrado; AO10 queda apenas un 0,3% por debajo, por lo que esta frontera no debe tratarse como un umbral físico.

## Método y referencias

Se aplican los coeficientes originales de `../../resultados/coeficientes.json`, sin ajustar ningún parámetro con AO/CV. Con x = I680 − B680: C_eq = -0.0171463960831 + 0.00784968891805·x + 0.000110942424661·x². Primero se promedian las tres intensidades de cada nivel y después se aplica la ecuación, como en la calibración original.

El análisis principal sustituye únicamente la referencia por el medio actual: B680 = 0,4940142667 u.a. La aplicación literal de la ecuación anterior utiliza B680 = 0,8821683333 u.a.; ambas se guardan en la tabla. El cambio máximo entre estas dos aplicaciones es 0,0051 µg/mL en AO y 0,0035 en CV. La elección del blanco no resuelve que las señales son bajas respecto a la calibración.

Las tres referencias de medio y el dark están duplicados de forma idéntica entre AO y CV; se consideran compartidos, no seis referencias independientes. Los dark son nulos y no aportan una estimación física del ruido.

## Resultados por nivel

La cantidad relativa se transcribe tal como aparece en la tabla; no se transforma en µg/mL ni se presupone la concentración del nivel 1. Las salidas negativas se conservan y no representan cantidades físicas negativas de pigmento.

| Serie | Muestra | Cantidad relativa | ΔI680 (u.a.) | C equivalente (µg/mL) | DE solo adquisiciones | C con blanco original |
|---|---|---:|---:|---:|---:|---:|
| AO | AO01 | 0.002 | 1.7996 | -0.0027 | 0.0013 | -0.0058 |
| AO | AO02 | 0.004 | 1.6938 | -0.0035 | 0.0022 | -0.0067 |
| AO | AO03 | 0.008 | 1.6938 | -0.0035 | 0.0005 | -0.0067 |
| AO | AO04 | 0.02 | 1.9408 | -0.0015 | 0.0035 | -0.0047 |
| AO | AO05 | 0.03 | 2.2936 | 0.0014 | 0.0027 | -0.0018 |
| AO | AO06 | 0.06 | 2.8935 | 0.0065 | 0.0009 | 0.0032 |
| AO | AO07 | 0.2 | 3.5640 | 0.0122 | 0.0103 | 0.0089 |
| AO | AO08 | 0.25 | 8.5041 | 0.0576 | 0.0211 | 0.0539 |
| AO | AO09 | 0.5 | 16.8318 | 0.1464 | 0.0159 | 0.1419 |
| AO | AO10 | 1 | 23.5362 | 0.2291 | 0.0037 | 0.2240 |
| CV | CV01 | 0.002 | 0.3529 | -0.0144 | 0.0017 | -0.0174 |
| CV | CV02 | 0.004 | 0.2823 | -0.0149 | 0.0013 | -0.0180 |
| CV | CV03 | 0.008 | 0.2470 | -0.0152 | 0.0000 | -0.0183 |
| CV | CV04 | 0.02 | 0.3882 | -0.0141 | 0.0005 | -0.0171 |
| CV | CV05 | 0.03 | 0.3529 | -0.0144 | 0.0008 | -0.0174 |
| CV | CV06 | 0.06 | 0.3882 | -0.0141 | 0.0010 | -0.0171 |
| CV | CV07 | 0.2 | 0.5293 | -0.0130 | 0.0005 | -0.0160 |
| CV | CV08 | 0.25 | 1.6232 | -0.0041 | 0.0000 | -0.0073 |
| CV | CV09 | 0.5 | 2.8935 | 0.0065 | 0.0009 | 0.0032 |
| CV | CV10 | 1 | 4.8696 | 0.0237 | 0.0005 | 0.0203 |

## Interpretación y límites

A 680 nm, la intensidad tiende a aumentar con la cantidad relativa en ambas series, sobre todo en los niveles altos. En los niveles bajos hay mesetas y variaciones que impiden distinguir todos los pasos de dilución. La respuesta positiva de varios niveles por encima del medio no implica que el modelo pueda cuantificarlos con exactitud.

El paso entre los niveles relativos 0,20 y 0,25 merece revisar la preparación y las etiquetas: la señal neta aumenta aproximadamente 2,39 veces en AO y 3,07 en CV, frente a un factor de 1,25 en la cantidad relativa. Es un patrón compartido que no demuestra un error de preparación; se conserva sin corregir ni eliminar muestras.

AO tiene una respuesta roja mayor que CV a igual etiqueta de cantidad relativa. No se conoce una concentración común de referencia para ambas especies; por tanto, ese contraste no demuestra mayor concentración de clorofila ni mayor rendimiento fluorescente de una especie.

El dominio original comprende referencias de 0,15–3 µg/mL y un blanco en cero, sin validación del intervalo entre cero y 0,15. La señal neta mínima observada en los extractos no blancos es 23,606818 u.a.; AO10 alcanza 23,536244 y CV10 4,869568. AO10 produce una C equivalente dentro del rango nominal a pesar de estar ligeramente por debajo de esa señal: el modelo ya sobreestimaba el nivel inferior de la serie original, según la revisión de residuos.

La DE comunicada recoge únicamente la variación entre adquisiciones, usando blanco y coeficientes fijos. No es un intervalo de predicción ni incluye incertidumbre del blanco compartido, la calibración o su transferencia a cultivos. Una DE nula en algunos niveles refleja repetición exacta de valores registrados, no incertidumbre total nula. Las tres adquisiciones no se tratan como preparaciones independientes. Sin concentraciones de referencia no se calculan residuos de concentración, RMSE externo, recuperación ni exactitud absoluta. No se inventa una concentración esperada a partir de la cantidad relativa.

Para validar el uso cuantitativo en cultivos, hace falta una determinación independiente de clorofila en muestras emparejadas y comprobar una calibración que cubra estas señales bajas. La geometría y el canal seleccionados pueden mantenerse; la transferencia de la ecuación de extracto queda sin validar.

## Archivos y reproducibilidad

- [Figura principal](figuras/01_aplicacion_modelo_90_680.png) · [SVG](figuras/01_aplicacion_modelo_90_680.svg).
- [Predicciones de las 20 muestras](predicciones.csv), [60 adquisiciones](adquisiciones_680.csv), [18 canales procesados](medias_18_canales.csv) y [referencias compartidas](referencias.csv).
- [Resumen, coeficientes y huellas de fuentes](resumen.json) e [inventario](inventario_fuentes.csv).

Reproducir con `python3 ../aplicar_modelo_90_680.py` en un entorno con NumPy, SciPy y Matplotlib. El archivo fuente llamado `cultivos.xlsx` es en realidad una tabla TSV con comas decimales; se lee sin modificarlo. Los 136 CSV del ZIP coinciden con la carpeta extraída. Se modelan solo las 60 adquisiciones a 90°; no se reabre la comparación con 180° ni se modifican calibraciones, datos fuente o firmware.