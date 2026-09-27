#include <Update.h>
#include <WebServer.h>
#include <WiFi.h>
#include "SparkFun_AS7265X.h"

constexpr uint8_t LED_PIN = 4;
constexpr uint16_t MAX_POINTS = 1200;
constexpr uint8_t STABILITY_SAMPLES = 21;
constexpr unsigned long SAMPLE_INTERVAL_MS = 250;
constexpr unsigned long STABILITY_MIN_MS = 5000;
constexpr unsigned long MAX_TEST_MS = 180000;
constexpr float STABILITY_BAND = 0.01f;
constexpr uint16_t SATURATION_RAW = 65000;
constexpr uint8_t SENSOR_GAIN = AS7265X_GAIN_64X;
constexpr uint8_t INTEGRATION_CYCLES = 49;
const char *AP_SSID = "LED-Stability";
const char *AP_PASSWORD = "clorofila";

AS7265X sensor;
WebServer server(80);
bool sensorOnline = false;
bool updateOk = false;
bool restartPending = false;
unsigned long restartAt = 0;
String updateError;
uint32_t timesMs[MAX_POINTS] = {};
float intensities[MAX_POINTS] = {};
uint16_t rawValues[MAX_POINTS] = {};
uint16_t pointCount = 0;
unsigned long testStarted = 0;
unsigned long lastSampleAt = 0;
enum TestState { IDLE, RUNNING, STABLE, TIMEOUT, STOPPED } testState = IDLE;

const char PAGE[] PROGMEM = R"HTML(
<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LED Stability Test</title><style>
:root{font-family:system-ui,sans-serif;color:#e8f5e9;background:#08130d}body{max-width:920px;margin:auto;padding:24px}h1{color:#76ff93}
.card{background:#12251a;border:1px solid #285238;border-radius:14px;padding:18px;margin-top:16px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
.value{font-size:1.6rem;font-weight:700;color:#a7ffb8}.muted{color:#a7b8ab}.bad{color:#ff9292}button,input::file-selector-button,a.button{border:0;border-radius:9px;padding:11px 16px;font-weight:700;background:#56d778;color:#07160b;cursor:pointer;text-decoration:none;display:inline-block}button:disabled{opacity:.5;cursor:wait}
canvas{width:100%;height:360px;background:#0a1810;border-radius:8px}input{max-width:100%}
</style></head><body><h1>LED Stability Test · 435 nm</h1>
<p id="status" class="muted">Connecting...</p><button id="start" onclick="startTest()">Start test</button> <button id="stop" onclick="command('/api/stop')" disabled>Stop</button> <a class="button" href="/data.csv">Download CSV</a>
<div class="grid"><section class="card"><div>Elapsed</div><div id="time" class="value">--</div></section><section class="card"><div>Intensity</div><div id="value" class="value">--</div></section><section class="card"><div>Raw ADC</div><div id="raw" class="value">--</div></section><section class="card"><div>Window variation</div><div id="spread" class="value">--</div></section></div>
<section class="card"><canvas id="chart"></canvas><p class="muted">Stable = 5 seconds within a 1% peak-to-peak band. Saturation threshold: raw ≥ 65000.</p></section>
<section class="card"><h2>Firmware update</h2><form id="updateForm" onsubmit="uploadFirmware(event)"><label>Firmware .bin <input type="file" name="firmware" accept=".bin" required></label> <button type="submit">Install .bin</button></form><p id="updateStatus" class="muted">Use this to return to the fluorometer firmware.</p></section>
<p class="muted">Firmware build: <span id="build">--</span></p><script>
let points=[],next=0;const canvas=document.querySelector('#chart');
function draw(){const d=devicePixelRatio||1,w=canvas.clientWidth*d,h=canvas.clientHeight*d;canvas.width=w;canvas.height=h;const x=canvas.getContext('2d');x.clearRect(0,0,w,h);if(points.length<2)return;let lo=Math.min(...points.map(p=>p.v)),hi=Math.max(...points.map(p=>p.v));if(lo===hi){lo-=1;hi+=1}const pad=45*d,tmax=points.at(-1).t;x.strokeStyle='#285238';x.strokeRect(pad,10*d,w-pad-10*d,h-pad);x.fillStyle='#a7b8ab';x.font=12*d+'px system-ui';x.fillText(hi.toFixed(4),4*d,20*d);x.fillText(lo.toFixed(4),4*d,h-pad);x.fillText('0 s',pad,h-10*d);x.fillText((tmax/1000).toFixed(1)+' s',w-55*d,h-10*d);x.beginPath();points.forEach((p,i)=>{const px=pad+(w-pad-10*d)*(tmax?p.t/tmax:0),py=10*d+(h-pad-10*d)*(hi-p.v)/(hi-lo);i?x.lineTo(px,py):x.moveTo(px,py)});x.strokeStyle='#76ff93';x.lineWidth=2*d;x.stroke()}
async function refresh(){try{const r=await fetch('/api/data?from='+next,{cache:'no-store'}),d=await r.json();d.points.forEach(p=>points.push({t:p[0],v:p[1]}));next=d.next;document.querySelector('#build').textContent=d.build;document.querySelector('#time').textContent=(d.elapsed/1000).toFixed(1)+' s';document.querySelector('#value').textContent=d.value==null?'--':d.value.toFixed(6);const raw=document.querySelector('#raw');raw.textContent=d.raw==null?'--':d.raw;raw.className=d.saturated?'value bad':'value';document.querySelector('#spread').textContent=d.spread==null?'--':d.spread.toFixed(3)+'%';const names={idle:'Ready',running:'Measuring LED stability…',stable:'Stable — LED switched off',timeout:'Timeout — LED switched off',stopped:'Stopped — LED switched off'};const s=document.querySelector('#status');s.textContent=!d.sensor?'Sensor not detected':d.saturated?'Signal saturated — add attenuation':names[d.state];s.className=d.saturated||!d.sensor?'bad':'muted';document.querySelector('#start').disabled=!d.sensor||d.running;document.querySelector('#stop').disabled=!d.running;draw()}catch(e){document.querySelector('#status').textContent='No connection'}}
async function command(path){await fetch(path,{method:'POST'});refresh()}function startTest(){points=[];next=0;command('/api/start')}
function uploadFirmware(e){e.preventDefault();const status=document.querySelector('#updateStatus'),xhr=new XMLHttpRequest();xhr.open('POST','/update');xhr.upload.onprogress=e=>{if(e.lengthComputable)status.textContent='Uploading: '+Math.round(e.loaded*100/e.total)+'%'};xhr.onload=()=>{status.textContent=xhr.responseText;if(xhr.status===200)setTimeout(()=>location.reload(),5000)};xhr.onerror=()=>status.textContent='Connection lost during upload. Wait for restart.';xhr.send(new FormData(e.target))}
refresh();setInterval(refresh,500);addEventListener('resize',draw);
</script></body></html>
)HTML";

void setLight(bool on) {
  digitalWrite(LED_PIN, on ? HIGH : LOW); // Etapa de potencia activa en HIGH.
}

const char *stateName() {
  return testState == RUNNING ? "running" : testState == STABLE ? "stable" : testState == TIMEOUT ? "timeout" : testState == STOPPED ? "stopped" : "idle";
}

float windowSpread() {
  if (pointCount < 2) return -1;
  const uint16_t start = pointCount > STABILITY_SAMPLES ? pointCount - STABILITY_SAMPLES : 0;
  float low = intensities[start], high = low, sum = 0;
  for (uint16_t i = start; i < pointCount; i++) {
    low = min(low, intensities[i]);
    high = max(high, intensities[i]);
    sum += intensities[i];
  }
  const float mean = sum / (pointCount - start);
  return mean > 0 ? (high - low) / mean : -1;
}

bool isStable() {
  if (pointCount < STABILITY_SAMPLES || timesMs[pointCount - 1] - timesMs[pointCount - STABILITY_SAMPLES] < STABILITY_MIN_MS) return false;
  for (uint16_t i = pointCount - STABILITY_SAMPLES; i < pointCount; i++) if (rawValues[i] >= SATURATION_RAW) return false;
  const float spread = windowSpread();
  return spread >= 0 && spread <= STABILITY_BAND;
}

void finishTest(TestState result) {
  testState = result;
  setLight(false);
}

void startTest() {
  pointCount = 0;
  testStarted = lastSampleAt = millis();
  testState = RUNNING;
  setLight(true);
}

void sendData() {
  uint16_t from = server.hasArg("from") ? server.arg("from").toInt() : 0;
  if (from > pointCount) from = pointCount;
  const uint16_t end = min<uint16_t>(pointCount, from + 100);
  const float spread = windowSpread();
  String json;
  json.reserve(5000);
  json = "{\"sensor\":" + String(sensorOnline ? "true" : "false") + ",\"state\":\"" + stateName() + "\",\"running\":" + String(testState == RUNNING ? "true" : "false") +
         ",\"elapsed\":" + String(pointCount ? timesMs[pointCount - 1] : 0) + ",\"value\":" + String(pointCount ? String(intensities[pointCount - 1], 6) : "null") +
         ",\"raw\":" + String(pointCount ? String(rawValues[pointCount - 1]) : "null") + ",\"saturated\":" + String(pointCount && rawValues[pointCount - 1] >= SATURATION_RAW ? "true" : "false") +
         ",\"spread\":" + String(spread >= 0 ? String(spread * 100, 4) : "null") + ",\"next\":" + end + ",\"points\":[";
  for (uint16_t i = from; i < end; i++) {
    if (i > from) json += ',';
    json += '[' + String(timesMs[i]) + ',' + String(intensities[i], 6) + ',' + String(rawValues[i]) + ']';
  }
  json += "],\"build\":\"" __DATE__ " " __TIME__ "\"}";
  server.sendHeader("Cache-Control", "no-store");
  server.send(200, "application/json", json);
}

void sendCsv() {
  server.sendHeader("Content-Disposition", "attachment; filename=led-stability.csv");
  server.setContentLength(CONTENT_LENGTH_UNKNOWN);
  server.send(200, "text/csv", "time_ms,time_s,intensity_435,raw_435,saturated\n");
  for (uint16_t i = 0; i < pointCount; i++) {
    server.sendContent(String(timesMs[i]) + ',' + String(timesMs[i] / 1000.0f, 3) + ',' + String(intensities[i], 6) + ',' + String(rawValues[i]) + ',' + String(rawValues[i] >= SATURATION_RAW ? 1 : 0) + '\n');
  }
  server.sendContent("");
}

void setupWeb() {
  server.on("/", HTTP_GET, []() { server.send_P(200, "text/html", PAGE); });
  server.on("/api/data", HTTP_GET, sendData);
  server.on("/api/start", HTTP_POST, []() {
    if (!sensorOnline) server.send(503, "text/plain", "Sensor not detected");
    else if (testState == RUNNING) server.send(409, "text/plain", "Test already running");
    else { startTest(); server.send(202, "text/plain", "Test started"); }
  });
  server.on("/api/stop", HTTP_POST, []() {
    if (testState == RUNNING) finishTest(STOPPED);
    server.send(200, "text/plain", "LED stopped");
  });
  server.on("/data.csv", HTTP_GET, sendCsv);
  server.on("/update", HTTP_POST, []() {
    server.send(updateOk ? 200 : 500, "text/plain", updateOk ? "Update complete. Restarting..." : "Update failed: " + updateError);
    if (updateOk) { restartPending = true; restartAt = millis() + 2000; }
  }, []() {
    HTTPUpload &upload = server.upload();
    if (upload.status == UPLOAD_FILE_START) {
      finishTest(STOPPED);
      updateOk = upload.filename.endsWith(".bin") && Update.begin(UPDATE_SIZE_UNKNOWN, U_FLASH);
      if (!updateOk) updateError = Update.errorString();
    } else if (upload.status == UPLOAD_FILE_WRITE && updateOk && Update.write(upload.buf, upload.currentSize) != upload.currentSize) {
      updateOk = false; updateError = Update.errorString();
    } else if (upload.status == UPLOAD_FILE_END) {
      if (updateOk && !Update.end(true)) { updateOk = false; updateError = Update.errorString(); }
      else if (!updateOk) Update.abort();
    } else if (upload.status == UPLOAD_FILE_ABORTED) {
      Update.abort(); updateOk = false; updateError = "Upload aborted";
    }
  });
  server.begin();
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  setLight(false);
  WiFi.mode(WIFI_AP);
  WiFi.softAP(AP_SSID, AP_PASSWORD);
  setupWeb();
  sensorOnline = sensor.begin();
  if (sensorOnline) {
    sensor.setGain(SENSOR_GAIN);
    sensor.setIntegrationCycles(INTEGRATION_CYCLES);
  }
  Serial.printf("AP: %s | http://%s | Sensor: %s\n", AP_SSID, WiFi.softAPIP().toString().c_str(), sensorOnline ? "OK" : "NOT FOUND");
}

void loop() {
  server.handleClient();
  const unsigned long now = millis();
  if (restartPending && static_cast<long>(now - restartAt) >= 0) ESP.restart();
  if (testState != RUNNING) return;
  if (now - testStarted >= MAX_TEST_MS || pointCount >= MAX_POINTS) {
    finishTest(TIMEOUT);
    return;
  }
  if (now - lastSampleAt < SAMPLE_INTERVAL_MS) return;
  sensor.takeMeasurements();
  lastSampleAt = millis();
  timesMs[pointCount] = lastSampleAt - testStarted;
  intensities[pointCount] = sensor.getCalibratedB();
  rawValues[pointCount] = sensor.getB();
  Serial.printf("%lu,%.6f,%u\n", timesMs[pointCount], intensities[pointCount], rawValues[pointCount]);
  pointCount++;
  if (isStable()) finishTest(STABLE);
}
