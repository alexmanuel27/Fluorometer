"""Exercise reference storage, CSV and dark acquisition using the production C++."""
from pathlib import Path
import subprocess
import tempfile

firmware = Path(__file__).resolve().parents[1] / "Spectro18_V_Flu"
source = (firmware / "Spectro18_V_Flu.ino").read_text()
storage = "void loadWhite() {" + source.split("void loadWhite() {", 1)[1].split("void startReadings(", 1)[0]
controls = "void setLight(bool on) {" + source.split("void setLight(bool on) {", 1)[1].split("void sendData()", 1)[0]
controls += "void startReadings(MeasurementMode mode) {" + source.split("void startReadings(MeasurementMode mode) {", 1)[1].split("void setupWebServer()", 1)[0]
controls += "void requestDark() {" + source.split('server.on("/api/dark", HTTP_POST, []() {', 1)[1].split("\n  });", 1)[0] + "\n}\n"
controls += "void loop() {" + source.split("void loop() {", 1)[1]
enums = "\n".join(line for line in source.splitlines() if line.startswith(("enum MeasurementMode", "enum MeasurementState")))
harness = r'''
#include "WhiteReference.h"
#include <cassert>
#include <cmath>
#include <cstring>
#include <limits>
#include <iomanip>
#include <map>
#include <sstream>
#include <string>
#include <vector>

class String : public std::string {
public:
  using std::string::string;
  String(int value) : std::string(std::to_string(value)) {}
  String(float value, int decimals) {
    std::ostringstream stream;
    stream << std::fixed << std::setprecision(decimals) << value;
    assign(stream.str());
  }
};

struct FakeServer {
  int status = 0;
  std::string body;
  void sendHeader(const char *, const char *) {}
  void handleClient() {}
  void send(int code, const char *, const std::string &value) { status = code; body = value; }
} server;
const uint16_t wavelengths[CHANNEL_COUNT] = {410,435,460,485,510,535,560,585,610,645,680,705,730,760,810,860,900,940};

struct FakePreferences {
  std::map<std::string, std::vector<unsigned char>> data;
  bool failOpen = false, failWrite = false;
  bool begin(const char *, bool) { return !failOpen; }
  void end() {}
  size_t getBytesLength(const char *key) { return data.count(key) ? data.at(key).size() : 0; }
  size_t getBytes(const char *key, void *destination, size_t size) {
    if (getBytesLength(key) != size) return 0;
    std::memcpy(destination, data.at(key).data(), size);
    return size;
  }
  size_t putBytes(const char *key, const void *value, size_t size) {
    if (failWrite) return 0;
    const auto *bytes = static_cast<const unsigned char *>(value);
    data[key] = std::vector<unsigned char>(bytes, bytes + size);
    return size;
  }
  bool getBool(const char *key, bool fallback) {
    return getBytesLength(key) == 1 ? data.at(key)[0] != 0 : fallback;
  }
} preferences;

bool whiteSaved = false, whiteSpectrumSaved = false, whiteSaveFailed = false;
bool darkSaved = false, darkSaveFailed = false;
WhiteReference whiteReference, darkReference, pendingReference;
float whiteAverage435 = 0, whiteAverage645 = 0;
// PRODUCTION_ENUMS
bool sensorOnline = true, lightOn = false, hasMeasurement = false, coolingEnabled = true, restartPending = false;
unsigned long restartAt = 0, cooldownStarted = 0, clockMs = 0;
uint8_t samplesTaken = 0, readingsSinceCooldown = 0;
uint32_t whiteRevision = 0, darkRevision = 0;
constexpr uint8_t LED_PIN = 4, READINGS_BEFORE_COOLDOWN = 3;
constexpr unsigned long LED_COOLDOWN_MS = 60000;
constexpr float CALIBRATION_435 = 1, CALIBRATION_645 = 1;
float sum435 = 0, sum645 = 0, average435 = 0, average645 = 0, chlorophyllA = 0;
float readings435[SAMPLE_COUNT] = {}, readings645[SAMPLE_COUNT] = {};
SpectrumStats spectrum[CHANNEL_COUNT];
constexpr int HIGH = 1, LOW = 0;
int gpioLevel = LOW;
void digitalWrite(uint8_t pin, int level) { assert(pin == LED_PIN); gpioLevel = level; }
unsigned long millis() { return clockMs; }
struct { void restart() { assert(false); } } ESP;
struct { void printf(const char *, ...) {} } Serial;
struct FakeSensor {
  unsigned count = 0;
  bool indicator = true;
  WhiteReference values;
  void takeMeasurements() {
    assert(count < SAMPLE_COUNT);
    if (measurementMode == DARK_MEASUREMENT) assert(!lightOn && gpioLevel == LOW && !indicator);
    count++;
  }
  void disableIndicator() { indicator = false; }
  void enableIndicator() { indicator = true; }
  #define CHANNEL(name, index) float getCalibrated##name() { return values.readings[count - 1][index]; }
  CHANNEL(A, 0) CHANNEL(B, 1) CHANNEL(C, 2) CHANNEL(D, 3) CHANNEL(E, 4) CHANNEL(F, 5)
  CHANNEL(G, 6) CHANNEL(H, 7) CHANNEL(R, 8) CHANNEL(I, 9) CHANNEL(S, 10) CHANNEL(J, 11)
  CHANNEL(T, 12) CHANNEL(U, 13) CHANNEL(V, 14) CHANNEL(W, 15) CHANNEL(K, 16) CHANNEL(L, 17)
  #undef CHANNEL
} sensor;

// PRODUCTION_STORAGE_FUNCTIONS
// PRODUCTION_CONTROLS

std::vector<std::vector<std::string>> csvRows() {
  std::vector<std::vector<std::string>> rows;
  std::istringstream stream(server.body);
  for (std::string line; std::getline(stream, line);) {
    rows.emplace_back();
    std::istringstream row(line);
    for (std::string cell; std::getline(row, cell, ',');) rows.back().push_back(cell);
  }
  return rows;
}

int main() {
  loadWhite();
  assert(!whiteSaved && !whiteSpectrumSaved);
  sendWhiteCsv();
  assert(server.status == 404);
  assert(!pendingReference.valid());
  assert(pendingReference.valid(false)); // All-zero readings are a valid dark, but not a white.
  for (unsigned row = 0; row < SAMPLE_COUNT; row++)
    for (unsigned channel = 0; channel < CHANNEL_COUNT; channel++)
      pendingReference.readings[row][channel] = (row + 1) * 100 + channel;
  assert(saveWhite());
  const WhiteReference saved = whiteReference;
  assert(whiteSaved && whiteSpectrumSaved);
  assert(preferences.getBytesLength("whiteSpectrum") == 10 * 18 * sizeof(float));
  whiteReference = WhiteReference{};
  loadWhite();
  assert(whiteSaved && whiteSpectrumSaved);
  assert(std::memcmp(&whiteReference, &saved, sizeof(saved)) == 0);
  for (unsigned channel = 0; channel < CHANNEL_COUNT; channel++) {
    const SpectrumStats stats = whiteReference.stats(channel);
    assert(stats.count == 10);
    assert(std::fabs(stats.mean - (550 + channel)) < 0.0001f);
    assert(std::fabs(stats.sd() - std::sqrt(825000.0f / 9)) < 0.0001f);
  }
  assert(whiteAverage435 == 551 && whiteAverage645 == 559);
  sendWhiteCsv();
  assert(server.status == 200);
  const auto rows = csvRows();
  assert(rows.size() == 13); // Header, ten readings, mean, sample SD.
  for (const auto &row : rows) assert(row.size() == 19);
  assert(rows[0][0] == "reading" && rows[11][0] == "average" && rows[12][0] == "standard_deviation");
  for (unsigned channel = 0; channel < CHANNEL_COUNT; channel++) {
    assert(rows[0][channel + 1] == std::to_string(wavelengths[channel]) + "_nm");
    for (unsigned reading = 0; reading < SAMPLE_COUNT; reading++)
      assert(std::stof(rows[reading + 1][channel + 1]) == saved.readings[reading][channel]);
    assert(std::stof(rows[11][channel + 1]) == saved.stats(channel).mean);
    assert(std::fabs(std::stof(rows[12][channel + 1]) - saved.stats(channel).sd()) < 0.0001f);
  }

  // Invalid readings and failed writes must not overwrite a saved reference.
  for (float invalid : {-1.0f, std::numeric_limits<float>::infinity(), std::numeric_limits<float>::quiet_NaN()}) {
    pendingReference = saved;
    pendingReference.readings[5][17] = invalid;
    assert(!saveWhite());
    assert(std::memcmp(&whiteReference, &saved, sizeof(saved)) == 0);
  }
  pendingReference = saved;
  for (unsigned row = 0; row < SAMPLE_COUNT; row++) pendingReference.readings[row][9] = 0;
  assert(!saveWhite());
  pendingReference = saved;
  pendingReference.readings[0][0] = 1234;
  preferences.failWrite = true;
  assert(!saveWhite());
  preferences.failWrite = false;
  loadWhite();
  assert(std::memcmp(&whiteReference, &saved, sizeof(saved)) == 0);
  preferences.failOpen = true;
  assert(!saveWhite());
  preferences.failOpen = false;

  // Old references remain usable, but must not claim to contain all channels.
  preferences.data.clear();
  float legacy435[SAMPLE_COUNT], legacy645[SAMPLE_COUNT];
  for (unsigned i = 0; i < SAMPLE_COUNT; i++) {
    legacy435[i] = 100 + i;
    legacy645[i] = 200 + i;
  }
  preferences.data["whiteValid"] = {1};
  preferences.putBytes("white435", legacy435, sizeof(legacy435));
  preferences.putBytes("white645", legacy645, sizeof(legacy645));
  loadWhite();
  assert(whiteSaved && !whiteSpectrumSaved);
  assert(whiteAverage435 == 104.5f && whiteAverage645 == 204.5f);
  assert(whiteReference.readings[9][1] == 109 && whiteReference.readings[9][9] == 209);
  sendWhiteCsv();
  const auto legacyRows = csvRows();
  assert(legacyRows.size() == 13);
  for (const auto &row : legacyRows) assert(row.size() == 3);
  assert(legacyRows[0][1] == "435_nm" && legacyRows[0][2] == "645_nm");
  pendingReference = saved;
  assert(saveWhite());
  loadWhite();
  assert(whiteSpectrumSaved && whiteAverage645 == 559);

  // Reject corrupt full-channel records; never expose their values as valid.
  preferences.data["whiteSpectrum"] = std::vector<unsigned char>(sizeof(WhiteReference), 0);
  loadWhite();
  assert(!whiteSaved && !whiteSpectrumSaved);

  // Dark must not overwrite white or any previous sample result.
  pendingReference = saved;
  assert(saveWhite());
  const auto whiteBytes = preferences.data.at("whiteSpectrum");
  hasMeasurement = true;
  average435 = 123; average645 = 456; chlorophyllA = 7;
  readings435[0] = 321;
  spectrum[0].add(654);
  loadDark();
  assert(!darkSaved);
  sendDarkCsv();
  assert(server.status == 404);
  sensorOnline = false;
  requestDark();
  assert(server.status == 503 && measurementState == IDLE);
  sensorOnline = true;
  for (MeasurementState busy : {READING, COOLDOWN}) {
    measurementState = busy;
    requestDark();
    assert(server.status == 409 && measurementState == busy && sensor.count == 0);
  }
  measurementState = READY;
  setLight(true);
  readingsSinceCooldown = 2;
  whiteSaved = false; // Dark does not require a white reference or Start.
  requestDark();
  assert(server.status == 202 && measurementState == READING && !lightOn && !sensor.indicator);
  for (unsigned i = 0; i < SAMPLE_COUNT; i++) loop();
  assert(darkSaved && !darkSaveFailed && darkRevision == 1);
  assert(measurementState == IDLE && !lightOn && gpioLevel == LOW && sensor.indicator);
  assert(readingsSinceCooldown == 2 && !whiteSaved);
  assert(hasMeasurement && average435 == 123 && average645 == 456 && chlorophyllA == 7);
  assert(readings435[0] == 321 && spectrum[0].mean == 654);
  assert(preferences.data.at("whiteSpectrum") == whiteBytes);
  darkReference = saved;
  loadDark();
  loadWhite();
  assert(darkSaved && whiteSaved && whiteAverage645 == 559);
  for (unsigned channel = 0; channel < CHANNEL_COUNT; channel++) {
    assert(darkReference.stats(channel).mean == 0 && darkReference.stats(channel).sd() == 0);
  }
  sendDarkCsv();
  auto darkRows = csvRows();
  assert(server.status == 200 && darkRows.size() == 13);
  for (const auto &row : darkRows) assert(row.size() == 19);
  for (unsigned channel = 0; channel < CHANNEL_COUNT; channel++) {
    assert(darkRows[0][channel + 1] == std::to_string(wavelengths[channel]) + "_nm");
    for (unsigned row = 1; row < darkRows.size(); row++) assert(std::stof(darkRows[row][channel + 1]) == 0);
  }

  // An incomplete capture must leave the stored dark untouched.
  sensor.values = saved;
  sensor.count = 0;
  requestDark();
  for (unsigned i = 0; i < 5; i++) loop();
  const auto firstDarkBytes = preferences.data.at("darkSpectrum");
  loadDark();
  assert(darkSaved && darkReference.stats(9).mean == 0 && darkRevision == 1);
  assert(preferences.data.at("darkSpectrum") == firstDarkBytes);
  for (unsigned i = 5; i < SAMPLE_COUNT; i++) loop();
  assert(darkRevision == 2 && darkReference.stats(9).mean == 559 && readingsSinceCooldown == 2);
  const auto darkBytes = preferences.data.at("darkSpectrum");
  sendDarkCsv();
  darkRows = csvRows();
  for (unsigned channel = 0; channel < CHANNEL_COUNT; channel++) {
    assert(std::stof(darkRows[11][channel + 1]) == saved.stats(channel).mean);
    assert(std::fabs(std::stof(darkRows[12][channel + 1]) - saved.stats(channel).sd()) < 0.0001f);
  }

  // Invalid data or failed writes preserve the previous dark, with LED off on exit.
  for (float invalid : {-1.0f, std::numeric_limits<float>::infinity(), std::numeric_limits<float>::quiet_NaN()}) {
    sensor.values = saved;
    sensor.values.readings[4][17] = invalid;
    sensor.count = 0;
    requestDark();
    for (unsigned i = 0; i < SAMPLE_COUNT; i++) loop();
    assert(darkSaveFailed && darkRevision == 2 && !lightOn && measurementState == IDLE);
    assert(preferences.data.at("darkSpectrum") == darkBytes);
  }
  sensor.values = saved;
  sensor.count = 0;
  preferences.failWrite = true;
  requestDark();
  for (unsigned i = 0; i < SAMPLE_COUNT; i++) loop();
  preferences.failWrite = false;
  assert(darkSaveFailed && darkRevision == 2 && preferences.data.at("darkSpectrum") == darkBytes);
  assert(preferences.data.at("whiteSpectrum") == whiteBytes);

  // The existing cooling counter is unchanged by dark and still triggers on the next lit capture.
  sensor.count = 0;
  setLight(true);
  startReadings(SAMPLE_MEASUREMENT);
  for (unsigned i = 0; i < SAMPLE_COUNT; i++) loop();
  assert(hasMeasurement && average645 == 559 && measurementState == COOLDOWN && !lightOn);
  assert(readingsSinceCooldown == 3);
  clockMs = LED_COOLDOWN_MS - 1;
  loop();
  assert(measurementState == COOLDOWN);
  clockMs++;
  loop();
  assert(measurementState == IDLE && readingsSinceCooldown == 0 && !lightOn);
}
'''
with tempfile.TemporaryDirectory(prefix="fluorometer-white-") as directory:
    executable = str(Path(directory) / "check_white")
    subprocess.run(
        ["c++", "-std=c++11", "-Wall", "-Wextra", "-Werror", "-I", str(firmware), "-x", "c++", "-", "-o", executable],
        input=harness.replace("// PRODUCTION_ENUMS", enums).replace("// PRODUCTION_STORAGE_FUNCTIONS", storage).replace("// PRODUCTION_CONTROLS", controls), text=True, check=True,
    )
    subprocess.run([executable], check=True)
print("White/dark: 18 channels, means, SD, CSV, reload, legacy migration, zero dark, LED-off capture, cooling and failed saves OK")
