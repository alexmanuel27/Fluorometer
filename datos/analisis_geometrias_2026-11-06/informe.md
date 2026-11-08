> Actualización: las concentraciones ya se incorporaron. Consultar [informe con calibración](resultados/informe_calibracion.md). Lo que sigue conserva la revisión preliminar anterior.

# Análisis exploratorio — 6 noviembre 2026
Se analizaron los CSV del ZIP sin modificar los originales. Las hipótesis de ActionPlan se consideran contexto, no resultados demostrados.
Correspondencia entre geometrías confirmada por Alex. No se ha localizado la asignación de concentraciones; no se calculan constantes de atenuación ni calibraciones.
La desviación entre las tres réplicas se calcula sobre sus medias; no equivale a disponer de 30 réplicas independientes.

## 180°: 20 muestras, tres archivos por muestra
- 410 nm: media de primera/última muestra 4294967296.000/36579.525; CV mediano entre réplicas 0.24%. Valores >10⁹: 30.
- 435 nm: media de primera/última muestra 4294967296.000/45280.874; CV mediano entre réplicas 0.10%. Valores >10⁹: 45.
- 485 nm: media de primera/última muestra 1038.754/345.596; CV mediano entre réplicas 32.93%. Valores >10⁹: 0.
- 510 nm: media de primera/última muestra 628.669/324.404; CV mediano entre réplicas 0.89%. Valores >10⁹: 0.
- 645 nm: media de primera/última muestra 980.041/456.512; CV mediano entre réplicas 0.67%. Valores >10⁹: 0.
- 680 nm: media de primera/última muestra 64.187/123.257; CV mediano entre réplicas 0.71%. Valores >10⁹: 0.
- 705 nm: media de primera/última muestra 868.626/433.409; CV mediano entre réplicas 0.53%. Valores >10⁹: 0.
- 900 nm: media de primera/última muestra 193.671/85.505; CV mediano entre réplicas 0.69%. Valores >10⁹: 0.

## 90°: 20 muestras, tres archivos por muestra
- 410 nm: media de primera/última muestra 402.027/307.954; CV mediano entre réplicas 0.36%. Valores >10⁹: 0.
- 435 nm: media de primera/última muestra 839.705/665.729; CV mediano entre réplicas 0.22%. Valores >10⁹: 0.
- 485 nm: media de primera/última muestra 5.093/5.361; CV mediano entre réplicas 48.30%. Valores >10⁹: 0.
- 510 nm: media de primera/última muestra 9.301/10.761; CV mediano entre réplicas 0.44%. Valores >10⁹: 0.
- 645 nm: media de primera/última muestra 6.637/22.507; CV mediano entre réplicas 0.28%. Valores >10⁹: 0.
- 680 nm: media de primera/última muestra 24.489/131.372; CV mediano entre réplicas 0.36%. Valores >10⁹: 0.
- 705 nm: media de primera/última muestra 15.695/55.487; CV mediano entre réplicas 0.35%. Valores >10⁹: 0.
- 900 nm: media de primera/última muestra 1.944/3.889; CV mediano entre réplicas 0.00%. Valores >10⁹: 0.

## Interpretación limitada
Los valores cercanos a 2³² requieren investigar la adquisición o exportación; no deben interpretarse como señal óptica válida. Los ceros y variabilidad de 485 nm requieren revisión antes de usar ese canal. No se elimina ninguna muestra automáticamente.
La comparación por número de muestra es descriptiva: no se presupone que el número represente concentración creciente. La causa física de una caída común no puede identificarse solo con correlaciones.
Siguiente paso: incorporar concentraciones, normalizar por blancos de cada geometría, contrastar pendientes logarítmicas y evaluar 680 nm con incertidumbre y diagnóstico de residuos.

## Ampliación: blancos y comparación pareada

### 180°
Blanco a 680 nm: 53.354 u.i. Media de tres blancos (10 lecturas cada uno).
Señal a 680 nm menos blanco, sample01 → sample20: 10.833 → 69.903 u.i.
Canales 510, 645, 705 y 900 nm normalizados por su blanco: correlaciones de Pearson entre 0.99951 y 0.99997. La separación máxima entre las cuatro señales normalizadas para una misma muestra es 0.0725. Correlación alta no significa curvas idénticas.
Ajuste descriptivo ΔI680 = a + b(1 − Tmedio): a=2.610, b=120.909, R²=0.99550, n=20 medias de muestra. Este ajuste no usa concentración y no demuestra un mecanismo físico; el blanco compartido introduce incertidumbre correlacionada.

### 90°
Blanco a 680 nm: 0.882 u.i. Media de tres blancos (10 lecturas cada uno).
Señal a 680 nm menos blanco, sample01 → sample20: 23.607 → 130.490 u.i.

### Alcance confirmado
Alex confirma que las 20 muestras son las mismas en ambas geometrías. Los correos de ActionPlan se refieren exclusivamente a 180°. El ZIP contiene 120 espectros de muestra, seis blancos y dos dark; la carpeta baseLine está vacía. Los dos dark contienen únicamente ceros; esto no demuestra ausencia de ruido físico.
Se revisó también la imagen incrustada del documento: presenta nueve puntos aproximados de un análisis anterior, no una correspondencia explícita de las 20 muestras actuales con concentraciones. Se pueden comparar señales y geometrías sin esa correspondencia; las constantes por unidad de concentración quedan pendientes.
Las diferencias de intensidad entre geometrías describen estas dos sesiones. Para atribuirlas exclusivamente a la geometría hay que confirmar igualdad de ajustes instrumentales y condiciones. Restar el blanco da incremento respecto al solvente; no aísla necesariamente fluorescencia pura.