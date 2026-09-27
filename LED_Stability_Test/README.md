# Prueba de estabilidad del LED

Firmware independiente para medir cuánto tarda en estabilizarse el LED usando el canal de **435 nm** del AS7265X.

## Uso

1. Carga `LED-Stability-OTA.bin` desde la interfaz OTA actual, o `LED-Stability-USB.bin` por USB.
2. Conéctate a la red Wi-Fi `LED-Stability` con contraseña `clorofila`.
3. Abre `http://192.168.4.1` y pulsa **Start test**.
4. El LED se apaga automáticamente cuando la señal permanece estable durante 5 segundos, o después de 180 segundos por seguridad.
5. Descarga `led-stability.csv` desde **Download CSV**. La gráfica permanece visible en el navegador.

Una lectura cruda igual o superior a `65000` se considera saturada y nunca puede declarar estabilidad. Ajusta el atenuador hasta eliminar el aviso de saturación.

Los parámetros editables están al inicio del `.ino`: intervalo de muestreo, duración estable, banda de estabilidad, tiempo máximo, ganancia e integración del sensor.
