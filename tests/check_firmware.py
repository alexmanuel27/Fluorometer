from pathlib import Path
from math import e, log

source = (Path(__file__).parents[1] / "Spectro18_V_Flu" / "Spectro18_V_Flu.ino").read_text()

for expected in (
    "LED_PIN = 4",
    "SAMPLE_COUNT = 10",
    "READINGS_BEFORE_COOLDOWN = 3",
    "LED_WARMUP_MS = 10000",
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
    'server.on("/api/measure"',
    "enum MeasurementState { IDLE, WARMING, READY, READING, COOLDOWN }",
    "average435 = sum435 / SAMPLE_COUNT",
    "average645 = sum645 / SAMPLE_COUNT",
    "chlorophyllA = -2.7924f * logf(average645) + 20.1264f",
    '#include <Preferences.h>',
    'preferences.begin("fluorometer", true)',
    'preferences.putBytes("white435"',
    'preferences.putBytes("white645"',
    'preferences.putBool("whiteValid", true)',
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
    "a.download='white-reference-'",
    'server.sendHeader("Cache-Control", "no-store, no-cache, must-revalidate")',
    "Firmware build:",
    "__DATE__",
    "__TIME__",
):
    assert expected in source, f"Falta en el firmware: {expected}"

assert 'server.on("/api/led"' not in source
assert "Array.from({length:10}" in source
assert "whiteRevision++" in source
assert "lastWhiteAverage435 = sum435 / SAMPLE_COUNT" in source
assert "measurementState = READY;" in source
assert "coolingEnabled && readingsSinceCooldown >= READINGS_BEFORE_COOLDOWN" in source
assert "if (!coolingEnabled && measurementState == COOLDOWN) measurementState = IDLE" in source
assert "measurementState == COOLDOWN && now - measurementStarted >= LED_COOLDOWN_MS" in source
assert "The 60-second cooling cycle cannot be interrupted" in source
assert "d.state==='warming'?'Warming...':d.state==='idle'?'Start':'Stop'" in source
assert source.index("average645 = sum645 / SAMPLE_COUNT") < source.index("logf(average645)")
assert source.index("whiteSaved") < source.index('server.on("/api/measure"')
assert source.count('<form id="updateForm"') == source.count("</form>") == 1
assert source.index("setupWebServer();") < source.index("sensorOnline = sensor.begin();")
chlorophyll = lambda red: -2.7924 * log(red) + 20.1264
assert abs(chlorophyll(1) - 20.1264) < 1e-9
assert abs(chlorophyll(e) - 17.334) < 1e-9
print("Firmware check: OK")
