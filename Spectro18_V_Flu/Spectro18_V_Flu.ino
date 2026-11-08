#include <Update.h>
#include <WebServer.h>
#include <WiFi.h>
#include <Preferences.h>
#include <math.h>
#include "SparkFun_AS7265X.h"
#include "WhiteReference.h"

constexpr uint8_t LED_PIN = 4;
const uint16_t wavelengths[CHANNEL_COUNT] = {410,435,460,485,510,535,560,585,610,645,680,705,730,760,810,860,900,940};
SpectrumStats spectrum[CHANNEL_COUNT];
constexpr uint8_t READINGS_BEFORE_COOLDOWN = 3;
constexpr unsigned long LED_COOLDOWN_MS = 60000;
constexpr float CALIBRATION_435 = 1.0f;
constexpr float CALIBRATION_645 = 1.0f;
const char *AP_SSID = "Fluorometer";
const char *AP_PASSWORD = "clorofila";

AS7265X sensor;
WebServer server(80);
Preferences preferences;
bool sensorOnline = false;
bool lightOn = false;
bool updateOk = false;
bool restartPending = false;
unsigned long restartAt = 0;
String updateError;
bool hasMeasurement = false;
bool whiteSaved = false;
bool whiteSpectrumSaved = false;
bool whiteSaveFailed = false;
bool darkSaved = false;
bool darkSaveFailed = false;
enum MeasurementMode { SAMPLE_MEASUREMENT, WHITE_MEASUREMENT, DARK_MEASUREMENT } measurementMode = SAMPLE_MEASUREMENT;
void startReadings(MeasurementMode mode);
float readings435[SAMPLE_COUNT] = {};
float readings645[SAMPLE_COUNT] = {};
WhiteReference whiteReference;
WhiteReference darkReference;
WhiteReference pendingReference;
float average435 = 0;
float average645 = 0;
float whiteAverage435 = 0;
float whiteAverage645 = 0;
float chlorophyllA = 0;
float sum435 = 0;
float sum645 = 0;
uint8_t samplesTaken = 0;
uint8_t readingsSinceCooldown = 0;
uint32_t whiteRevision = 0;
uint32_t darkRevision = 0;
bool coolingEnabled = true;
unsigned long cooldownStarted = 0;
enum MeasurementState { IDLE, READY, READING, COOLDOWN } measurementState = IDLE;

const char PAGE[] PROGMEM = R"HTML(
<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Fluorometer</title><style>
:root{font-family:system-ui,sans-serif;color:#e8f5e9;background:#08130d}
body{max-width:720px;margin:auto;padding:24px}h1{color:#76ff93}.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}
.card{background:#12251a;border:1px solid #285238;border-radius:14px;padding:20px}.value{font-size:2rem;font-weight:700;color:#a7ffb8}
button,input,input::file-selector-button{border:0;border-radius:9px;padding:11px 16px;font-weight:700}button,input::file-selector-button{cursor:pointer}button{background:#56d778;color:#07160b}
button:disabled{opacity:.5;cursor:wait}input{max-width:100%}.muted{color:#a7b8ab}#status.bad{color:#ff9292}
table{width:100%;border-collapse:collapse;text-align:center}th,td{padding:9px;border-bottom:1px solid #285238}th{color:#a7ffb8}
summary{cursor:pointer;font-weight:700;color:#a7ffb8}details[open] summary{margin-bottom:12px}
</style></head><body><h1>Fluorometer</h1>
<p id="status" class="muted">Connecting...</p>
<button id="start" onclick="toggleLight()">Start</button>
<button id="white" onclick="measureWhite()" disabled>Measure White</button>
<button id="dark" onclick="measureDark()" disabled>Measure Dark</button>
<button id="measure" onclick="measure()" disabled>Measure</button>
<label style="display:block;margin-top:14px"><input id="cooling" type="checkbox" checked onchange="setCooling()"> Enable cooling cycle (60 s after 3 readings)</label>
<section class="card" style="margin-top:16px"><div>White reference</div><div id="whiteStatus" class="value">Not saved</div><div id="whiteValues" class="muted">435 nm: -- · 645 nm: --</div>
<details style="margin-top:14px"><summary>18-channel white spectrum · mean ± SD</summary>
<svg id="whiteSpectrumChart" viewBox="0 0 700 360" style="width:100%;height:auto" role="img" aria-label="White reference spectrum with standard deviation error bars"></svg>
<table><thead><tr><th>Wavelength (nm)</th><th>Mean intensity</th><th>SD (n = 10)</th></tr></thead><tbody id="whiteSpectrumRows"></tbody></table></details></section>
<section class="card" style="margin-top:16px"><div>Dark reference · LED off</div><div id="darkStatus" class="value">Not saved</div>
<p class="muted">Close the optical chamber to exclude ambient light. Dark values are saved separately and are not subtracted from measurements.</p>
<details><summary>18-channel dark spectrum · mean ± SD</summary>
<svg id="darkSpectrumChart" viewBox="0 0 700 360" style="width:100%;height:auto" role="img" aria-label="Dark reference spectrum with standard deviation error bars"></svg>
<table><thead><tr><th>Wavelength (nm)</th><th>Mean intensity</th><th>SD (n = 10)</th></tr></thead><tbody id="darkSpectrumRows"></tbody></table></details></section>
<details class="card" style="margin-top:16px" open><summary>Individual readings (10)</summary><table id="results"><thead><tr><th>435 nm</th><th>645 nm</th></tr></thead><tbody id="rows"></tbody></table></details>
<h2>Average result</h2><div class="grid">
<section class="card"><div>435 nm</div><div id="avg435" class="value">--</div></section>
<section class="card"><div>645 nm</div><div id="avg645" class="value">--</div></section></div>
<section class="card" style="margin-top:16px"><div>Chlorophyll A · Chl(A)</div><div id="chlorophyll" class="value">--</div></section>
<details class="card" style="margin-top:16px"><summary>18-channel spectrum · mean ± SD</summary>
<p class="muted">Each point is the mean of 10 readings. Error bars show the standard deviation calculated from those 10 readings.</p>
<svg id="spectrumChart" viewBox="0 0 700 360" style="width:100%;height:auto" role="img" aria-label="Spectrum with mean intensity and standard deviation error bars"></svg>
<table><thead><tr><th>Wavelength (nm)</th><th>Mean intensity</th><th>SD (n = 10)</th></tr></thead><tbody id="spectrumRows"></tbody></table></details>
<section class="card" style="margin-top:16px"><h2>Save measurement</h2>
<label>File name <input id="filename" value="fluorometer-measurement" maxlength="80"></label>
<button id="save" onclick="saveExcel()" disabled>Save Excel + spectrum CSV</button><p class="muted">Downloads two files. Allow multiple downloads in your browser if prompted.</p></section>
<section class="card" style="margin-top:16px"><h2>Firmware update</h2>
<form id="updateForm" onsubmit="uploadFirmware(event)">
<label>Firmware .bin <input type="file" name="firmware" accept=".bin" required></label> <button type="submit">Install .bin</button>
</form><p id="updateStatus" class="muted">The device restarts after a successful update.</p></section>
<p class="muted">Firmware build: <span id="build">--</span></p>
<script>
let latest=null,whiteDownloadPending=false,lastWhiteRevision=0,darkDownloadPending=false,lastDarkRevision=0;
const rows=document.querySelector('#rows');rows.innerHTML=Array.from({length:10},()=>'<tr><td>--</td><td>--</td></tr>').join('');
async function refresh(){try{const r=await fetch('/api/data');const d=await r.json();
latest=d;
renderSpectrum(d.spectrum);
renderSpectrum(d.whiteSpectrum,'whiteSpectrum');
renderSpectrum(d.darkSpectrum,'darkSpectrum');
document.querySelector('#build').textContent=d.build;
rows.querySelectorAll('tr').forEach((row,i)=>{row.cells[0].textContent=d.nm435[i]==null?'--':d.nm435[i].toFixed(6);row.cells[1].textContent=d.nm645[i]==null?'--':d.nm645[i].toFixed(6);});
document.querySelector('#avg435').textContent=d.avg435==null?'--':d.avg435.toFixed(6);document.querySelector('#avg645').textContent=d.avg645==null?'--':d.avg645.toFixed(6);
document.querySelector('#chlorophyll').textContent=d.chlorophyll==null?'--':d.chlorophyll.toFixed(2);
document.querySelector('#whiteStatus').textContent=d.whiteSaved?'Saved':'Not saved';document.querySelector('#whiteValues').textContent=d.whiteSaved?'435 nm: '+d.white435.toFixed(6)+' · 645 nm: '+d.white645.toFixed(6):'435 nm: -- · 645 nm: --';
if(d.whiteSaved&&!d.whiteSpectrumSaved)document.querySelector('#whiteValues').textContent+=' · Legacy reference: measure white again to save all 18 channels.';
if(d.whiteSaveFailed){whiteDownloadPending=false;document.querySelector('#whiteStatus').textContent='Save failed';}
if(whiteDownloadPending&&d.whiteRevision!==lastWhiteRevision){whiteDownloadPending=false;downloadReference('white');}lastWhiteRevision=d.whiteRevision;
document.querySelector('#darkStatus').textContent=d.darkSaveFailed?'Save failed':d.darkSaved?'Saved':'Not saved';
if(d.darkSaveFailed)darkDownloadPending=false;
if(darkDownloadPending&&d.darkRevision!==lastDarkRevision){darkDownloadPending=false;downloadReference('dark');}lastDarkRevision=d.darkRevision;
document.querySelector('#cooling').checked=d.coolingEnabled;
const s=document.querySelector('#status');s.className=d.sensor?'muted':'bad';
s.textContent=!d.sensor?'Sensor not detected':d.state==='cooldown'?'LED cooling: '+d.remaining+' s':d.state==='ready'?'LED ready · '+(d.coolingEnabled?d.readings+'/3 readings':'cooling disabled'):d.state==='reading'?(d.mode==='dark'?'Measuring dark (LED off): ':d.mode==='white'?'Measuring white: ':'Taking readings: ')+d.count+'/10':d.mode==='dark'&&d.darkSaved?'Dark measurement complete · LED off':d.avg435==null?'Press Start':'Measurement complete';
if(d.whiteSaveFailed)s.textContent+=' · White reference could not be saved; the previous reference was kept.';
if(d.darkSaveFailed)s.textContent+=' · Dark reference could not be saved; the previous reference was kept.';
const start=document.querySelector('#start');start.textContent=d.state==='cooldown'?'Cooling...':d.state==='idle'?'Start':'Stop';start.disabled=!d.sensor||d.state==='reading'||d.state==='cooldown';document.querySelector('#white').disabled=d.state!=='ready';document.querySelector('#dark').disabled=!d.sensor||(d.state!=='idle'&&d.state!=='ready');document.querySelector('#measure').disabled=d.state!=='ready'||!d.whiteSaved;document.querySelector('#save').disabled=d.avg435==null;}catch(e){document.querySelector('#status').textContent='No connection';}}
async function command(path){const r=await fetch(path,{method:'POST'});if(!r.ok)document.querySelector('#status').textContent=await r.text();refresh();return r.ok;}
function toggleLight(){command(document.querySelector('#start').textContent==='Stop'?'/api/stop':'/api/start');}async function measureWhite(){whiteDownloadPending=await command('/api/white');}function measure(){command('/api/measure');}
async function measureDark(){darkDownloadPending=await command('/api/dark');}
function setCooling(){command('/api/cooling?enabled='+(document.querySelector('#cooling').checked?'1':'0'));}
function renderSpectrum(data,prefix='spectrum'){
document.querySelector('#'+prefix+'Rows').innerHTML=data.map(p=>'<tr><td>'+p[0]+'</td><td>'+(p[1]==null?'--':p[1].toFixed(6))+'</td><td>'+(p[2]==null?'--':p[2].toFixed(6))+'</td></tr>').join('');
const chart=document.querySelector('#'+prefix+'Chart');if(!data.length||data.some(p=>p[1]==null)){chart.innerHTML='<text x="70" y="160" fill="#a7b8ab">Take a measurement to display all 18 channels.</text>';return;}
const lo=Math.min(0,...data.map(p=>p[1]-p[2])),hi=Math.max(...data.map(p=>p[1]+p[2])),range=hi-lo||1;
const x=nm=>75+(nm-410)*600/530,y=v=>300-(v-lo)*260/range;
let svg='<g font-family="system-ui" font-size="12" fill="#a7b8ab"><text x="75" y="18">Calibrated intensity</text><text x="330" y="352">Wavelength (nm)</text>';
for(let i=0;i<=4;i++){const v=lo+range*i/4,py=y(v);svg+='<path d="M75 '+py+' H675" stroke="#285238"/><text x="2" y="'+(py+4)+'">'+v.toPrecision(3)+'</text>';}
for(const nm of [410,510,610,710,810,940])svg+='<text x="'+(x(nm)-12)+'" y="325">'+nm+'</text>';
svg+='<polyline fill="none" stroke="#76ff93" stroke-width="2" points="'+data.map(p=>x(p[0])+','+y(p[1])).join(' ')+'"/>';
for(const [nm,mean,sd] of data){const px=x(nm),top=y(mean+sd),bottom=y(mean-sd);svg+='<g><title>'+nm+' nm: '+mean.toFixed(6)+' ± '+sd.toFixed(6)+'</title><path d="M'+px+' '+top+' V'+bottom+' M'+(px-4)+' '+top+' H'+(px+4)+' M'+(px-4)+' '+bottom+' H'+(px+4)+'" stroke="#ffd479" stroke-width="2"/><circle cx="'+px+'" cy="'+y(mean)+'" r="3" fill="#76ff93"/></g>';}
chart.innerHTML=svg+'</g>';}
function saveSpectrumCsv(){const csv='wavelength_nm,mean_intensity,standard_deviation,n\n'+latest.spectrum.map(p=>p.join(',')+',10').join('\n')+'\n',url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'})),a=document.createElement('a');const name=document.querySelector('#filename').value.trim().replace(/[\\/:*?"<>|]/g,'_')||'fluorometer-measurement';a.href=url;a.download=name+'-spectrum.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
async function downloadReference(kind){try{const r=await fetch('/'+kind+'.csv',{cache:'no-store'});if(!r.ok){document.querySelector('#status').textContent=await r.text();return;}const url=URL.createObjectURL(await r.blob()),a=document.createElement('a'),stamp=new Date().toISOString().slice(0,19).replace(/[:T]/g,'-');a.href=url;a.download=kind+'-reference-'+stamp+'.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch(e){document.querySelector('#status').textContent='Reference download failed. Check the connection.';}}
function saveExcel(){if(!latest||latest.avg435==null)return;saveSpectrumCsv();const cell=(v,t='Number')=>'<Cell><Data ss:Type="'+t+'">'+v+'</Data></Cell>';
const data=latest.nm435.map((v,i)=>'<Row>'+cell(v)+cell(latest.nm645[i])+'</Row>').join('');
const chl=latest.chlorophyll==null?cell('Not available','String'):cell(latest.chlorophyll);const xml='<?xml version="1.0"?><Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet" xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet"><Worksheet ss:Name="Measurement"><Table><Row>'+cell('435 nm','String')+cell('645 nm','String')+'</Row>'+data+'<Row>'+cell('Average 435 nm','String')+cell('Average 645 nm','String')+'</Row><Row>'+cell(latest.avg435)+cell(latest.avg645)+'</Row><Row>'+cell('Chlorophyll A','String')+chl+'</Row></Table></Worksheet></Workbook>';
const url=URL.createObjectURL(new Blob([xml],{type:'application/vnd.ms-excel'}));const a=document.createElement('a');const name=document.querySelector('#filename').value.trim().replace(/[\\/:*?"<>|]/g,'_')||'fluorometer-measurement';a.href=url;a.download=name+'.xls';a.click();URL.revokeObjectURL(url);}
function uploadFirmware(e){e.preventDefault();const status=document.querySelector('#updateStatus');const xhr=new XMLHttpRequest();xhr.open('POST','/update');
xhr.upload.onprogress=e=>{if(e.lengthComputable)status.textContent='Uploading: '+Math.round(e.loaded*100/e.total)+'%';};
xhr.onload=()=>{status.textContent=xhr.responseText;if(xhr.status===200)setTimeout(reconnect,3000);};xhr.onerror=()=>status.textContent='Connection lost during upload. Do not power off; wait and reconnect.';xhr.send(new FormData(e.target));}
async function reconnect(){try{await fetch('/api/data',{cache:'no-store'});location.reload();}catch(e){setTimeout(reconnect,1000);}}
refresh();setInterval(refresh,500);
</script></body></html>
)HTML";

void setLight(bool on) {
  lightOn = on;
  digitalWrite(LED_PIN, on ? HIGH : LOW); // Electrónica activa en HIGH.
}

void sendData() {
  const char *state = measurementState == READY ? "ready" : measurementState == READING ? "reading" : measurementState == COOLDOWN ? "cooldown" : "idle";
  const unsigned long elapsed = millis() - cooldownStarted;
  const unsigned long remaining = measurementState == COOLDOWN && elapsed < LED_COOLDOWN_MS ? (LED_COOLDOWN_MS - elapsed + 999) / 1000 : 0;
  const uint8_t visibleSamples = hasMeasurement ? SAMPLE_COUNT : measurementState == READING && measurementMode == SAMPLE_MEASUREMENT ? samplesTaken : 0;
  String json;
  json.reserve(4500);
  json = "{\"sensor\":" + String(sensorOnline ? "true" : "false") + ",\"state\":\"" + state +
         "\",\"mode\":\"" + (measurementMode == DARK_MEASUREMENT ? "dark" : measurementMode == WHITE_MEASUREMENT ? "white" : "sample") + "\",\"remaining\":" + remaining +
         ",\"count\":" + samplesTaken + ",\"readings\":" + readingsSinceCooldown + ",\"coolingEnabled\":" + String(coolingEnabled ? "true" : "false") + ",\"whiteRevision\":" + whiteRevision + ",\"whiteSaved\":" + String(whiteSaved ? "true" : "false") +
         ",\"whiteSpectrumSaved\":" + String(whiteSpectrumSaved ? "true" : "false") + ",\"whiteSaveFailed\":" + String(whiteSaveFailed ? "true" : "false") +
         ",\"darkSaved\":" + String(darkSaved ? "true" : "false") + ",\"darkSaveFailed\":" + String(darkSaveFailed ? "true" : "false") + ",\"darkRevision\":" + darkRevision +
         ",\"white435\":" + String(whiteSaved ? String(whiteAverage435, 6) : "null") +
         ",\"white645\":" + String(whiteSaved ? String(whiteAverage645, 6) : "null") + ",\"nm435\":[";
  for (uint8_t i = 0; i < SAMPLE_COUNT; i++) {
    if (i) json += ',';
    json += i < visibleSamples ? String(readings435[i], 6) : "null";
  }
  json += "],\"nm645\":[";
  for (uint8_t i = 0; i < SAMPLE_COUNT; i++) {
    if (i) json += ',';
    json += i < visibleSamples ? String(readings645[i], 6) : "null";
  }
  json += "],\"avg435\":" + String(hasMeasurement ? String(average435, 6) : "null") +
          ",\"avg645\":" + String(hasMeasurement ? String(average645, 6) : "null");
  json += ",\"chlorophyll\":" + String(hasMeasurement && average645 > 0 ? String(chlorophyllA, 3) : "null");
  json += ",\"spectrum\":[";
  for (uint8_t i = 0; i < CHANNEL_COUNT; i++) {
    if (i) json += ',';
    json += '[' + String(wavelengths[i]) + ',' + (hasMeasurement ? String(spectrum[i].mean, 6) : String("null")) + ',' + (hasMeasurement ? String(spectrum[i].sd(), 6) : String("null")) + ']';
  }
  json += ']';
  json += ",\"darkSpectrum\":[";
  for (uint8_t i = 0; i < CHANNEL_COUNT; i++) {
    if (i) json += ',';
    const SpectrumStats stats = darkReference.stats(i);
    json += '[' + String(wavelengths[i]) + ',' + (darkSaved ? String(stats.mean, 6) : String("null")) + ',' + (darkSaved ? String(stats.sd(), 6) : String("null")) + ']';
  }
  json += ']';
  json += ",\"whiteSpectrum\":[";
  for (uint8_t i = 0; i < CHANNEL_COUNT; i++) {
    if (i) json += ',';
    const SpectrumStats stats = whiteReference.stats(i);
    json += '[' + String(wavelengths[i]) + ',' + (whiteSpectrumSaved ? String(stats.mean, 6) : String("null")) + ',' + (whiteSpectrumSaved ? String(stats.sd(), 6) : String("null")) + ']';
  }
  json += ']';
  json += ",\"build\":\"" __DATE__ " " __TIME__ "\"}";
  server.sendHeader("Cache-Control", "no-store");
  server.send(200, "application/json", json);
}

void loadWhite() {
  whiteSaved = whiteSpectrumSaved = false;
  whiteReference = WhiteReference{};
  if (!preferences.begin("fluorometer", true)) return;
  if (preferences.getBytesLength("whiteSpectrum") == sizeof(whiteReference)) {
    whiteSaved = whiteSpectrumSaved = preferences.getBytes("whiteSpectrum", &whiteReference, sizeof(whiteReference)) == sizeof(whiteReference) && whiteReference.valid();
  } else {
    // Keep legacy two-channel references usable without inventing the missing channels.
    float legacy435[SAMPLE_COUNT] = {}, legacy645[SAMPLE_COUNT] = {};
    if (preferences.getBool("whiteValid", false) &&
        preferences.getBytesLength("white435") == sizeof(legacy435) &&
        preferences.getBytesLength("white645") == sizeof(legacy645) &&
        preferences.getBytes("white435", legacy435, sizeof(legacy435)) == sizeof(legacy435) &&
        preferences.getBytes("white645", legacy645, sizeof(legacy645)) == sizeof(legacy645)) {
      for (uint8_t i = 0; i < SAMPLE_COUNT; i++) {
        whiteReference.readings[i][1] = legacy435[i];
        whiteReference.readings[i][9] = legacy645[i];
      }
      whiteSaved = whiteReference.valid();
    }
  }
  if (whiteSaved) {
    whiteAverage435 = whiteReference.stats(1).mean;
    whiteAverage645 = whiteReference.stats(9).mean;
  }
  preferences.end();
}

bool saveWhite() {
  if (!pendingReference.valid() || !preferences.begin("fluorometer", false)) return false;
  // One NVS blob keeps all channels and readings in the same saved reference.
  const bool saved = preferences.putBytes("whiteSpectrum", &pendingReference, sizeof(pendingReference)) == sizeof(pendingReference);
  preferences.end();
  if (saved) {
    whiteReference = pendingReference;
    whiteAverage435 = whiteReference.stats(1).mean;
    whiteAverage645 = whiteReference.stats(9).mean;
    whiteSaved = whiteSpectrumSaved = true;
  }
  return saved;
}

void loadDark() {
  darkSaved = false;
  darkReference = WhiteReference{};
  if (!preferences.begin("fluorometer", true)) return;
  darkSaved = preferences.getBytesLength("darkSpectrum") == sizeof(darkReference) &&
              preferences.getBytes("darkSpectrum", &darkReference, sizeof(darkReference)) == sizeof(darkReference) && darkReference.valid(false);
  preferences.end();
}

bool saveDark() {
  if (!pendingReference.valid(false) || !preferences.begin("fluorometer", false)) return false;
  const bool saved = preferences.putBytes("darkSpectrum", &pendingReference, sizeof(pendingReference)) == sizeof(pendingReference);
  preferences.end();
  if (saved) {
    darkReference = pendingReference;
    darkSaved = true;
  }
  return saved;
}

void sendReferenceCsv(const WhiteReference &reference, bool allChannels) {
  String csv;
  csv.reserve(4000);
  csv = "reading";
  for (uint8_t channel = 0; channel < CHANNEL_COUNT; channel++) {
    if (allChannels || channel == 1 || channel == 9) csv += ',' + String(wavelengths[channel]) + "_nm";
  }
  csv += '\n';
  for (uint8_t i = 0; i < SAMPLE_COUNT; i++) {
    csv += String(i + 1);
    for (uint8_t channel = 0; channel < CHANNEL_COUNT; channel++) {
      if (allChannels || channel == 1 || channel == 9) csv += ',' + String(reference.readings[i][channel], 6);
    }
    csv += '\n';
  }
  for (uint8_t row = 0; row < 2; row++) {
    csv += row == 0 ? "average" : "standard_deviation";
    for (uint8_t channel = 0; channel < CHANNEL_COUNT; channel++) {
      if (allChannels || channel == 1 || channel == 9) {
        const SpectrumStats stats = reference.stats(channel);
        csv += ',' + String(row == 0 ? stats.mean : stats.sd(), 6);
      }
    }
    csv += '\n';
  }
  server.sendHeader("Cache-Control", "no-store");
  server.send(200, "text/csv", csv);
}

void sendWhiteCsv() {
  if (!whiteSaved) server.send(404, "text/plain", "No saved white reference");
  else sendReferenceCsv(whiteReference, whiteSpectrumSaved);
}

void sendDarkCsv() {
  if (!darkSaved) server.send(404, "text/plain", "No saved dark reference");
  else sendReferenceCsv(darkReference, true);
}

void startReadings(MeasurementMode mode) {
  samplesTaken = 0;
  sum435 = sum645 = 0;
  measurementMode = mode;
  whiteSaveFailed = false;
  darkSaveFailed = false;
  if (mode != SAMPLE_MEASUREMENT) pendingReference = WhiteReference{};
  if (mode == DARK_MEASUREMENT) {
    setLight(false);
    sensor.disableIndicator();
  } else if (mode == SAMPLE_MEASUREMENT) {
    hasMeasurement = false;
    for (uint8_t i = 0; i < CHANNEL_COUNT; i++) spectrum[i] = SpectrumStats{};
    average435 = average645 = chlorophyllA = 0;
  }
  measurementState = READING;
}

void setupWebServer() {
  server.on("/", HTTP_GET, []() {
    server.sendHeader("Cache-Control", "no-store, no-cache, must-revalidate");
    server.sendHeader("Pragma", "no-cache");
    server.send_P(200, "text/html", PAGE);
  });
  server.on("/api/data", HTTP_GET, sendData);
  server.on("/white.csv", HTTP_GET, sendWhiteCsv);
  server.on("/dark.csv", HTTP_GET, sendDarkCsv);
  server.on("/api/start", HTTP_POST, []() {
    if (!sensorOnline) server.send(503, "text/plain", "Sensor not detected");
    else if (measurementState != IDLE) server.send(409, "text/plain", "Device is busy");
    else {
      setLight(true);
      measurementState = READY;
      server.send(200, "text/plain", "LED on. Ready to measure");
    }
  });
  server.on("/api/stop", HTTP_POST, []() {
    if (measurementState == READING) server.send(409, "text/plain", "Wait for the current reading to finish");
    else if (measurementState == COOLDOWN) server.send(409, "text/plain", "The 60-second cooling cycle cannot be interrupted");
    else {
      measurementState = IDLE;
      setLight(false);
      server.send(200, "text/plain", "LED stopped");
    }
  });
  server.on("/api/cooling", HTTP_POST, []() {
    coolingEnabled = server.arg("enabled") != "0";
    readingsSinceCooldown = 0;
    if (!coolingEnabled && measurementState == COOLDOWN) measurementState = IDLE;
    server.send(200, "text/plain", coolingEnabled ? "Cooling enabled" : "Cooling disabled");
  });
  server.on("/api/white", HTTP_POST, []() {
    if (measurementState != READY) server.send(409, "text/plain", "LED must be on and ready");
    else {
      startReadings(WHITE_MEASUREMENT);
      server.send(202, "text/plain", "White measurement started");
    }
  });
  server.on("/api/dark", HTTP_POST, []() {
    if (!sensorOnline) server.send(503, "text/plain", "Sensor not detected");
    else if (measurementState != IDLE && measurementState != READY) server.send(409, "text/plain", "Device is busy");
    else {
      startReadings(DARK_MEASUREMENT);
      server.send(202, "text/plain", "Dark measurement started. LED off");
    }
  });
  server.on("/api/measure", HTTP_POST, []() {
    if (!sensorOnline) server.send(503, "text/plain", "Sensor not detected");
    else if (!whiteSaved) server.send(428, "text/plain", "Measure and save a white reference first");
    else if (measurementState != READY) server.send(409, "text/plain", "LED must be on and ready");
    else {
      startReadings(SAMPLE_MEASUREMENT);
      server.send(202, "text/plain", "Measurement started");
    }
  });
  server.on("/update", HTTP_POST, []() {
    server.sendHeader("Cache-Control", "no-store");
    server.send(updateOk ? 200 : 500, "text/plain", updateOk ? "Update complete. Restarting..." : "Update failed: " + updateError);
    if (updateOk) {
      restartPending = true;
      restartAt = millis() + 2000;
    }
  }, []() {
    HTTPUpload &upload = server.upload();
    if (upload.status == UPLOAD_FILE_START) {
      updateError = "Invalid .bin file";
      updateOk = upload.filename.endsWith(".bin");
      if (updateOk && !Update.begin(UPDATE_SIZE_UNKNOWN, U_FLASH)) {
        updateOk = false;
        updateError = Update.errorString();
      }
    } else if (upload.status == UPLOAD_FILE_WRITE) {
      if (updateOk && Update.write(upload.buf, upload.currentSize) != upload.currentSize) {
        updateOk = false;
        updateError = Update.errorString();
      }
    } else if (upload.status == UPLOAD_FILE_END) {
      if (updateOk && !Update.end(true)) {
        updateOk = false;
        updateError = Update.errorString();
      } else if (!updateOk) Update.abort();
    } else if (upload.status == UPLOAD_FILE_ABORTED) {
      Update.abort();
      updateOk = false;
      updateError = "Upload aborted";
    }
  });
  server.onNotFound([]() { server.send(404, "text/plain", "Not found"); });
  server.begin();
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  setLight(false);

  WiFi.mode(WIFI_AP);
  WiFi.softAP(AP_SSID, AP_PASSWORD);
  loadWhite();
  loadDark();
  setupWebServer();

  sensorOnline = sensor.begin();
  Serial.printf("AP: %s\nWeb: http://%s\nSensor: %s\n", AP_SSID,
                WiFi.softAPIP().toString().c_str(), sensorOnline ? "OK" : "NO DETECTADO");
}

void loop() {
  server.handleClient();
  const unsigned long now = millis();
  if (restartPending && static_cast<long>(now - restartAt) >= 0) ESP.restart();
  if (measurementState == COOLDOWN && now - cooldownStarted >= LED_COOLDOWN_MS) {
    readingsSinceCooldown = 0;
    measurementState = IDLE;
  }
  if (measurementState == READING) {
    sensor.takeMeasurements();
    // Wavelength order differs from the sensor's letter order (R=610, I=645).
    const float values[CHANNEL_COUNT] = {
      sensor.getCalibratedA(), sensor.getCalibratedB() * CALIBRATION_435,
      sensor.getCalibratedC(), sensor.getCalibratedD(), sensor.getCalibratedE(), sensor.getCalibratedF(),
      sensor.getCalibratedG(), sensor.getCalibratedH(), sensor.getCalibratedR(),
      sensor.getCalibratedI() * CALIBRATION_645, sensor.getCalibratedS(), sensor.getCalibratedJ(),
      sensor.getCalibratedT(), sensor.getCalibratedU(), sensor.getCalibratedV(), sensor.getCalibratedW(),
      sensor.getCalibratedK(), sensor.getCalibratedL()
    };
    const float value435 = values[1];
    const float value645 = values[9];
    if (measurementMode != SAMPLE_MEASUREMENT) {
      for (uint8_t i = 0; i < CHANNEL_COUNT; i++) pendingReference.readings[samplesTaken][i] = values[i];
    } else {
      for (uint8_t i = 0; i < CHANNEL_COUNT; i++) spectrum[i].add(values[i]);
      readings435[samplesTaken] = value435;
      readings645[samplesTaken] = value645;
    }
    sum435 += value435;
    sum645 += value645;
    Serial.printf("Reading %u - 435:%.3f, 645:%.3f\n", samplesTaken + 1, value435, value645);
    if (++samplesTaken == SAMPLE_COUNT) {
      if (measurementMode == DARK_MEASUREMENT) {
        if (saveDark()) darkRevision++;
        else darkSaveFailed = true;
      } else if (measurementMode == WHITE_MEASUREMENT) {
        if (saveWhite()) whiteRevision++;
        else whiteSaveFailed = true;
      } else {
        average435 = sum435 / SAMPLE_COUNT;
        average645 = sum645 / SAMPLE_COUNT;
        if (average645 > 0) chlorophyllA = -2.7924f * logf(average645) + 20.1264f;
        hasMeasurement = true;
      }
      if (measurementMode != DARK_MEASUREMENT && coolingEnabled) readingsSinceCooldown++;
      if (measurementMode == DARK_MEASUREMENT) {
        setLight(false);
        sensor.enableIndicator();
        measurementState = IDLE;
      } else if (coolingEnabled && readingsSinceCooldown >= READINGS_BEFORE_COOLDOWN) {
        cooldownStarted = millis();
        measurementState = COOLDOWN;
        setLight(false);
      } else measurementState = READY;
      Serial.printf("%s complete - 435:%.3f, 645:%.3f\n", measurementMode == DARK_MEASUREMENT ? "Dark" : measurementMode == WHITE_MEASUREMENT ? "White" : "Measurement",
                    measurementMode != SAMPLE_MEASUREMENT ? sum435 / SAMPLE_COUNT : average435, measurementMode != SAMPLE_MEASUREMENT ? sum645 / SAMPLE_COUNT : average645);
    }
  }
}
