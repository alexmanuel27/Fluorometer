const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');

const source = fs.readFileSync(path.join(__dirname, '../Spectro18_V_Flu/Spectro18_V_Flu.ino'), 'utf8');
const script = source.match(/<script>([\s\S]*?)<\/script>/)[1];
const wavelengths = [410,435,460,485,510,535,560,585,610,645,680,705,730,760,810,860,900,940];
const nodes = new Map(), downloads = [], requests = [];
const data = {
  sensor:true, state:'idle', mode:'sample', remaining:0, count:0, readings:0, coolingEnabled:true,
  whiteSaved:false, whiteSpectrumSaved:false, whiteSaveFailed:false, whiteRevision:0,
  darkSaved:false, darkSaveFailed:false, darkRevision:0, white435:null, white645:null,
  nm435:Array(10).fill(null), nm645:Array(10).fill(null), avg435:null, avg645:null, chlorophyll:null,
  spectrum:wavelengths.map(nm=>[nm,null,null]), whiteSpectrum:wavelengths.map(nm=>[nm,null,null]),
  darkSpectrum:wavelengths.map(nm=>[nm,null,null]), build:'test',
};
const document = {
  querySelector(id) {
    if (!nodes.has(id)) nodes.set(id, {textContent:'', innerHTML:'', querySelectorAll:()=>Array.from({length:10},()=>({cells:[{},{}]}))});
    return nodes.get(id);
  },
  createElement:()=>({click(){downloads.push(this.download);}}),
};
const context = vm.createContext({
  document, Date, console,
  fetch:async url=>{
    requests.push(url);
    if (url==='/api/dark') {data.mode='dark';data.state='reading';}
    return {ok:true, json:async()=>data, blob:async()=>({})};
  },
  URL:{createObjectURL:()=> 'blob:test', revokeObjectURL(){}},
  setTimeout(){}, setInterval(){},
});

(async()=>{
  vm.runInContext(script, context);
  await context.refresh();
  assert.equal(nodes.get('#dark').disabled, false); // No Start or white required.
  assert.equal(nodes.get('#measure').disabled, true);
  assert.equal(nodes.get('#start').textContent, 'Start');
  await context.measureDark();
  await new Promise(setImmediate);
  assert.ok(requests.includes('/api/dark'));
  assert.equal(nodes.get('#dark').disabled, true);
  assert.equal(nodes.get('#start').disabled, true);
  assert.ok(nodes.get('#status').textContent.includes('Measuring dark (LED off)'));
  data.state='idle'; data.darkSaved=true; data.darkRevision=1;
  data.darkSpectrum=wavelengths.map(nm=>[nm,0,0]);
  await context.refresh();
  await new Promise(setImmediate);
  assert.ok(requests.includes('/dark.csv'));
  assert.equal(downloads.length, 1);
  assert.ok(downloads[0].startsWith('dark-reference-'));
  assert.equal(nodes.get('#darkStatus').textContent, 'Saved');
  assert.equal((nodes.get('#darkSpectrumRows').innerHTML.match(/<tr>/g)||[]).length, 18);
  assert.equal((nodes.get('#darkSpectrumChart').innerHTML.match(/<circle /g)||[]).length, 18);
  assert.ok(!nodes.get('#darkSpectrumChart').innerHTML.includes('NaN'));
  assert.equal(nodes.get('#start').textContent, 'Start');
  await context.refresh();
  await new Promise(setImmediate);
  assert.equal(downloads.length, 1); // Polling does not repeat downloads.

  data.state='ready'; data.whiteSaved=true; data.white435=100; data.white645=200;
  data.whiteSpectrumSaved=true;
  await context.refresh();
  assert.equal(nodes.get('#dark').disabled, false);
  assert.equal(nodes.get('#measure').disabled, false); // Dark is not a prerequisite.
  await context.measureWhite();
  data.whiteRevision++;
  await context.refresh();
  await new Promise(setImmediate);
  assert.equal(downloads.length, 2);
  assert.ok(downloads[1].startsWith('white-reference-'));

  await context.measureDark();
  data.state='idle'; data.darkSaveFailed=true;
  await context.refresh();
  await new Promise(setImmediate);
  assert.equal(nodes.get('#darkStatus').textContent, 'Save failed');
  assert.equal(downloads.length, 2); // Failed save must not download an old reference as new.
  assert.equal(vm.runInContext('darkDownloadPending', context), false);
  for (const state of ['reading','cooldown']) {
    data.state=state;
    await context.refresh();
    assert.equal(nodes.get('#dark').disabled, true);
  }
  data.state='idle'; data.sensor=false;
  await context.refresh();
  assert.equal(nodes.get('#dark').disabled, true);
  console.log('Web: dark controls, 18 zero-valued channels, automatic CSV, white regression and failed saves OK');
})().catch(error=>{console.error(error);process.exitCode=1;});
