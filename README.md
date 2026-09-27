# Fluorometer ESP32

El ESP32 crea su propia red Wi-Fi, ejecuta mediciones de 435 nm y 645 nm con el
LED activo en LOW conectado a GPIO4 y acepta firmware OTA desde el navegador.

## Primera carga por USB

1. Instala el soporte **ESP32 by Espressif Systems** y la librería
   **SparkFun AS7265X Spectral Sensor** en Arduino IDE.
2. Abre `Spectro18_V_Flu/Spectro18_V_Flu.ino` y selecciona tu modelo de ESP32.
3. Elige una tabla de particiones que incluya OTA (la opción predeterminada sirve;
   no uses una opción marcada como "No OTA").
4. Compila y carga el sketch por USB.

## Uso

1. Conecta el teléfono u ordenador a la red `Fluorometer` con contraseña
   `clorofila`.
2. Abre <http://192.168.4.1>.
3. Pulsa **Start**. El LED se enciende y tarda 10 segundos en estabilizarse.
4. Con el LED listo, pulsa **Measure White** para guardar una referencia blanca,
   o **Measure** para medir una muestra. Ambos toman 10 lecturas y apagan el LED.
5. **Measure** solo está disponible cuando el LED está listo y existe un blanco.
6. La tabla muestra las 10 lecturas de la muestra y el resultado final es su promedio.
7. Escribe un nombre y pulsa **Save Excel** para descargar un archivo `.xls`
   con las dos columnas, las 10 lecturas, ambos promedios y el resultado Chl(A).

El blanco guarda sus 10 lecturas y ambos promedios en la memoria no volátil del
ESP32. Sobrevive apagados y solo se reemplaza al completar otro **Measure White**.

El cálculo usa el promedio de 645 nm y el logaritmo natural:

`Chl(A) = -2.7924 × ln(promedio 645 nm) + 20.1264`

Si el promedio de 645 nm es cero o negativo, Chl(A) se muestra como no disponible.

La interfaz web está en inglés.

El panel y la actualización OTA siguen disponibles si el sensor no es detectado.
Los factores `CALIBRATION_435` y `CALIBRATION_645`, al principio del sketch,
permiten ajustar cada canal frente a un patrón de referencia sin cambiar la web.

## Actualizaciones OTA posteriores

En Arduino IDE usa **Sketch > Export Compiled Binary**. En el panel del
fluorómetro, selecciona el archivo `.bin` generado y pulsa **Install .bin**.
No desconectes la alimentación durante la carga; al terminar, el ESP32 se
reinicia automáticamente. La página muestra el progreso, espera el reinicio y
vuelve a conectarse. Si aparece `No suitable partition found`, la tabla de
particiones instalada no admite OTA y debes cargar primero el firmware completo
por USB usando la partición predeterminada.

## Comprobación rápida

Ejecuta `python3 tests/check_firmware.py`. La compilación final debe hacerse en
Arduino IDE o, desde la raíz del proyecto, con:

```sh
arduino-cli compile --fqbn esp32:esp32:esp32 --clean --output-dir output Spectro18_V_Flu
```

Para actualizar desde la web usa `output/Fluorometer-OTA.bin`. El archivo
`*.merged.bin` contiene la imagen completa para una carga inicial por cable, no
para OTA.
