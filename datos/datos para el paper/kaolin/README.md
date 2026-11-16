# Extracto y caolín

Comparación de 90° y 180° con LED azul de 430 nm, mismos ajustes y agitación antes de cada lectura, según confirma Alex. Seis preparaciones, tres adquisiciones por preparación y geometría. Clorofila nominal: 0 o 3 µg/mL; caolín nominal: 0, 1,25 g/L (b) o 2,50 g/L (a).

**Para la señal principal elegiría 90° y 680 nm:** con blanco habitual, las mezclas conservan 101,5% y 101,4% de la respuesta del extracto puro. El caolín sin extracto produce un cambio neto de solo 0,07–0,35% de esa respuesta.

**180° ofrece información complementaria del fondo:** su señal neta de 680 nm conserva 77,0% y 69,2% con blanco fijo. La prueba exploratoria `S = I680 − 0,239205582·I810`, con coeficiente calculado solo del etanol, mejora esa conservación a 103,4% y 99,9%. No se considera una corrección de fluorescencia ya validada.

- [Informe completo, comparaciones y límites](resultados/informe.md).
- [Elección integrada de configuración](../resultados/decision_configuracion.md): valoración conjunta del ensayo con caolín y de las diluciones puras.
- [Revisión del código de Daniela](resultados/revision_daniela/revision.md): comparación numérica de la lectura y del blanco, escalas y porcentajes.
- Figura principal recomendada para el paper: [PNG](resultados/figuras/01_figura_principal.png) · [SVG editable](resultados/figuras/01_figura_principal.svg).
- [730 nm y contrastes entre mezclas y controles](resultados/figuras/02_canales_rojos_y_contrastes.png).
- Espectros de las seis preparaciones, con las 18 longitudes: [PNG](resultados/figuras/04_espectros_raw_y_blanco.png) · [SVG](resultados/figuras/04_espectros_raw_y_blanco.svg). Izquierda 90°, derecha 180°; arriba intensidades originales, abajo I menos el blanco de etanol. Incluye las lecturas anómalas señaladas y usa escalas que permiten verlas junto con el resto.
- Todos los canales: [90°](resultados/figuras/03_18_canales_90.png) · [180°](resultados/figuras/03_18_canales_180.png).
- [Medias y DE](resultados/medias.csv), [contrastes](resultados/contrastes.csv), [diagnósticos de canales y fórmulas](resultados/diagnosticos.csv) y [coeficientes de fondo](resultados/coeficientes_fondo.csv).

Los porcentajes comparan respuestas ópticas con el extracto puro de la misma sesión; **no son recuperaciones de concentración**. Hay una sola concentración no nula de clorofila y no constan preparaciones independientes. Hace falta otra serie para validar la corrección y su uso a concentraciones bajas.

## Reproducir

Ejecutar `python3 analizar_kaolin.py` desde esta carpeta, con NumPy y Matplotlib. Se regeneran únicamente los archivos de `resultados/`; las fuentes quedan intactas. Se lee también la tabla del análisis previo de extractos para documentar las diferencias entre sesiones, sin aplicar sus ecuaciones de concentración.

La interpretación del informe corresponde a estas seis preparaciones concretas. Revisarla antes de sustituir las fuentes por un experimento nuevo.

Las composiciones, confirmaciones de Alex, fuentes y versiones están guardadas en [preparaciones](resultados/preparaciones.csv), [inventario](resultados/inventario_fuentes.csv) y [trazabilidad](resultados/trazabilidad.json).
