from pathlib import Path

source = (Path(__file__).parents[1] / "LED_Stability_Test" / "LED_Stability_Test.ino").read_text()

for expected in (
    "LED_PIN = 4",
    "STABILITY_MIN_MS = 5000",
    "MAX_TEST_MS = 180000",
    "STABILITY_BAND = 0.01f",
    "SATURATION_RAW = 65000",
    "digitalWrite(LED_PIN, on ? HIGH : LOW)",
    "sensor.getCalibratedB()",
    "sensor.getB()",
    "if (isStable()) finishTest(STABLE)",
    "finishTest(TIMEOUT)",
    'server.on("/data.csv"',
    'server.on("/update"',
    "Signal saturated",
):
    assert expected in source, f"Missing stability-test feature: {expected}"

assert source.index("rawValues[i] >= SATURATION_RAW") < source.index("spread <= STABILITY_BAND")
print("LED stability check: OK")
