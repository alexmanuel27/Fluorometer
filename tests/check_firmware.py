from pathlib import Path
from math import e, log

firmware = Path(__file__).parents[1] / "Spectro18_V_Flu"
source = (firmware / "Spectro18_V_Flu.ino").read_text()
definitions = source + (firmware / "WhiteReference.h").read_text()

for expected in (
    "LED_PIN = 4",
    "SAMPLE_COUNT = 10",
    "READINGS_BEFORE_COOLDOWN = 3",
    "LED_COOLDOWN_MS = 60000",
    "CALIBRATION_435 = 1.0f",
    "CALIBRATION_645 = 1.0f",
    "WiFi.softAP(AP_SSID, AP_PASSWORD)",
    'server.on("/api/data"',
    'server.on("/api/start"',
    'server.on("/api/stop"',
    'server.on("/api/cooling"',
    'server.on("/api/white"',
    'server.on("/white.csv"',
    'server.on("/api/dark"',
    'server.on("/dark.csv"',
    'server.on("/api/measure"',
    "enum MeasurementState { IDLE, READY, READING, COOLDOWN }",
    "average435 = sum435 / SAMPLE_COUNT",
    "average645 = sum645 / SAMPLE_COUNT",
    "chlorophyllA = -2.7924f * logf(average645) + 20.1264f",
    '#include <Preferences.h>',
    'preferences.begin("fluorometer", true)',
    'preferences.putBytes("whiteSpectrum"',
    'preferences.getBytes("whiteSpectrum"',
    'preferences.getBytes("white435"',
    'preferences.getBytes("white645"',
    'pendingReference.readings[samplesTaken][i] = values[i]',
    'if (saveWhite()) whiteRevision++',
    'if (saveDark()) darkRevision++',
    'preferences.putBytes("darkSpectrum"',
    'darkReference.valid(false)',
    'sensor.disableIndicator()',
    'sensor.enableIndicator()',
    '"standard_deviation"',
    'reference.readings[i][channel]',
    'id="whiteSpectrumChart"',
    'id="whiteSpectrumRows"',
    "renderSpectrum(d.whiteSpectrum,'whiteSpectrum')",
    "d.whiteSaveFailed",
    'id="dark"',
    'id="darkSpectrumChart"',
    'id="darkSpectrumRows"',
    "renderSpectrum(d.darkSpectrum,'darkSpectrum')",
    "d.darkSaveFailed",
    'id="start"',
    'id="cooling"',
    '<details class="card"',
    '<summary>Individual readings (10)</summary>',
    'id="white"',
    "d.whiteSaved",
    "d.whiteRevision",
    '\"chlorophyll\"',
    'id="chlorophyll"',
    "cell('Chlorophyll A','String')",
    "setLight(false)",
    "digitalWrite(LED_PIN, on ? HIGH : LOW)",
    'server.on("/update"',
    'upload.filename.endsWith(".bin")',
    "if (updateOk)",
    "Update.errorString()",
    "restartAt = millis() + 2000",
    "if (restartPending",
    "new XMLHttpRequest()",
    "xhr.upload.onprogress",
    "setTimeout(reconnect,3000)",
    'lang="en"',
    "Save Excel",
    "application/vnd.ms-excel",
    "Average 435 nm",
    "Average 645 nm",
    "a.download=name+'.xls'",
    "a.download=kind+'-reference-'",
    'server.sendHeader("Cache-Control", "no-store, no-cache, must-revalidate")',
    "Firmware build:",
    "__DATE__",
    "__TIME__",
):
    assert expected in definitions, f"Falta en el firmware: {expected}"

assert 'server.on("/api/led"' not in source
assert "Array.from({length:10}" in source
assert "whiteRevision++" in source
assert 'if (!whiteSaved) server.send(404' in source
assert 'measurementMode != DARK_MEASUREMENT && coolingEnabled' in source
assert "measurementState = READY;" in source
assert "coolingEnabled && readingsSinceCooldown >= READINGS_BEFORE_COOLDOWN" in source
assert "if (!coolingEnabled && measurementState == COOLDOWN) measurementState = IDLE" in source
assert "measurementState == COOLDOWN && now - cooldownStarted >= LED_COOLDOWN_MS" in source
assert "The 60-second cooling cycle cannot be interrupted" in source
assert "d.state==='cooldown'?'Cooling...':d.state==='idle'?'Start':'Stop'" in source
for removed in ("WARMUP", "WARMING", "warm-up", "warm up", "warming", "startWarmup", "measurementStarted"):
    assert removed not in source, f"Queda una referencia al calentamiento: {removed}"
start_route = source.split('server.on("/api/start"', 1)[1].split('server.on("/api/stop"', 1)[0]
assert "setLight(true);" in start_route and "measurementState = READY;" in start_route
assert "millis()" not in start_route and "delay(" not in start_route
assert 'server.send(200, "text/plain", "LED on. Ready to measure")' in start_route
assert source.index("average645 = sum645 / SAMPLE_COUNT") < source.index("logf(average645)")
assert source.index("whiteSaved") < source.index('server.on("/api/measure"')
assert source.count('<form id="updateForm"') == source.count("</form>") == 1
assert source.index("setupWebServer();") < source.index("sensorOnline = sensor.begin();")
chlorophyll = lambda red: -2.7924 * log(red) + 20.1264
assert abs(chlorophyll(1) - 20.1264) < 1e-9
assert abs(chlorophyll(e) - 17.334) < 1e-9
print("Firmware check: OK")
