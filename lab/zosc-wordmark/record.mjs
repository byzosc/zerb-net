// Deterministic Chromium screenshots of the native SVG study; no external packages.
// Run: node lab/zosc-wordmark/record.mjs [stills|all]
// Output stays on the data disk under .render-tmp/zosc-wordmark/.
import {spawn,execFileSync} from 'node:child_process';
import {createServer} from 'node:http';
import {readFileSync,writeFileSync,mkdirSync,existsSync,statSync} from 'node:fs';
import {join,resolve,extname} from 'node:path';
import {homedir} from 'node:os';
import {fileURLToPath} from 'node:url';

const repo=fileURLToPath(new URL('../../',import.meta.url));
const output=join(repo,'.render-tmp/zosc-wordmark');
mkdirSync(output,{recursive:true});
const server=createServer((req,res)=>{
  const path=resolve(repo,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));
  if(!path.startsWith(repo)||!existsSync(path)||!statSync(path).isFile()){res.writeHead(404);res.end();return}
  const types={'.html':'text/html; charset=utf-8','.js':'text/javascript','.woff2':'font/woff2','.svg':'image/svg+xml'};
  res.writeHead(200,{'content-type':types[extname(path)]||'application/octet-stream','cache-control':'no-store'});res.end(readFileSync(path));
});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const url=`http://127.0.0.1:${server.address().port}/lab/zosc-wordmark/index.html?capture=1`;
const chrome=spawn('chromium',['--headless=new','--no-sandbox','--disable-gpu','--hide-scrollbars','--no-first-run','--force-color-profile=srgb',`--user-data-dir=${join(homedir(),'render-tmp',`zosc-wordmark-${process.pid}`)}`,'--remote-debugging-port=0','about:blank'],{stdio:['ignore','ignore','pipe']});
let ws;
try{
  const wsUrl=await new Promise((res,rej)=>{
    let log='';const timer=setTimeout(()=>rej(new Error('Chromium startup timeout')),25000);
    chrome.stderr.on('data',d=>{log+=d;const match=log.match(/DevTools listening on (ws:\/\/\S+)/);if(match){clearTimeout(timer);res(match[1])}});
    chrome.on('exit',c=>{clearTimeout(timer);rej(new Error(`Chromium exited ${c}: ${log.slice(-500)}`))});
  });
  ws=new WebSocket(wsUrl);await new Promise((res,rej)=>{ws.onopen=res;ws.onerror=rej});
  let seq=0;const pending=new Map();const errors=[];
  ws.onmessage=event=>{const message=JSON.parse(event.data);if(message.id&&pending.has(message.id)){const p=pending.get(message.id);clearTimeout(p.timer);pending.delete(message.id);message.error?p.reject(new Error(JSON.stringify(message.error))):p.resolve(message.result)}else if(message.method==='Runtime.exceptionThrown')errors.push(message.params.exceptionDetails.text)};
  const send=(method,params={},sessionId)=>new Promise((resolve,reject)=>{const id=++seq;const timer=setTimeout(()=>{pending.delete(id);reject(new Error(`CDP timeout: ${method}`))},20000);pending.set(id,{resolve,reject,timer});ws.send(JSON.stringify({id,method,params,...(sessionId?{sessionId}:{})}))});
  const{targetId}=await send('Target.createTarget',{url:'about:blank'});
  const{sessionId}=await send('Target.attachToTarget',{targetId,flatten:true});
  await send('Page.enable',{},sessionId);await send('Runtime.enable',{},sessionId);
  const evaluate=async expression=>{const result=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true},sessionId);if(result.exceptionDetails)throw new Error(JSON.stringify(result.exceptionDetails));return result.result.value};
  const size=(width,height)=>send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:false},sessionId);
  const paint=()=>evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(()=>r(true))))');
  const screenshot=async file=>{await paint();const{data}=await send('Page.captureScreenshot',{format:'png'},sessionId);writeFileSync(join(output,file),Buffer.from(data,'base64'))};
  await size(1600,1280);await send('Page.navigate',{url},sessionId);
  for(let i=0;i<80;i++){if(await evaluate('!!window.wordmark'))break;await new Promise(r=>setTimeout(r,100))}
  await evaluate('document.fonts.ready.then(()=>true)');
  await evaluate("document.body.dataset.view='board'");await screenshot('zosc-02-static-board.png');
  await size(1440,980);await evaluate("document.body.dataset.view='header'");await screenshot('zosc-02-header-desktop.png');
  await size(390,870);await screenshot('zosc-02-header-mobile.png');
  await size(1200,675);await evaluate("document.body.dataset.view='motion'");
  for(const t of [0,120,260,440,680,1040]){await evaluate(`wordmark.seek(${t})`);await screenshot(`zosc-02-frame-${t}.png`)}

  // Verify live rAF completion as well as frozen export frames.
  await evaluate('wordmark.replay()');await new Promise(r=>setTimeout(r,1300));
  const completed=await evaluate("document.querySelector('[data-animated] path').getAttribute('d')");
  await evaluate('wordmark.seek(1040)');
  const settled=await evaluate("document.querySelector('[data-animated] path').getAttribute('d')");
  if(completed!==settled)throw new Error('Live animation did not reach exact rest');
  await send('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:'reduce'}]},sessionId);
  await evaluate('wordmark.replay()');
  const reduced=await evaluate("document.querySelector('[data-animated] path').getAttribute('d')");
  if(reduced!==settled)throw new Error('Reduced motion did not show static identity');
  await send('Emulation.setEmulatedMedia',{features:[]},sessionId);
  if(errors.length)throw new Error(errors.join('\n'));
  console.log(JSON.stringify({liveAnimation:'exact rest',reducedMotion:'static',consoleErrors:errors.length}));

  if(process.argv[2]!=='stills'){
    const frames=join(output,'frames');mkdirSync(frames,{recursive:true});
    const count=105;
    for(let i=0;i<count;i++){await evaluate(`wordmark.seek(${i*40-240})`);await screenshot(`frames/frame-${String(i).padStart(3,'0')}.png`)}
    // Keep ImageMagick cache off the system disk and cap memory; the rest is exact duplicates.
    const cache=join(output,'magick-cache');mkdirSync(cache,{recursive:true});
    execFileSync('convert',['-limit','memory','128MiB','-limit','map','256MiB','-delay','4','-loop','0',join(frames,'frame-*.png'),'+dither','-colors','64','-layers','Optimize',join(output,'zosc-02-motion.gif')],{env:{...process.env,MAGICK_TMPDIR:cache},stdio:'inherit'});
    execFileSync('ffmpeg',['-y','-framerate','25','-i',join(frames,'frame-%03d.png'),'-c:v','libx264','-pix_fmt','yuv420p','-vf','pad=ceil(iw/2)*2:ceil(ih/2)*2','-movflags','+faststart',join(output,'zosc-02-motion.mp4')],{stdio:'ignore'});
    console.log(JSON.stringify({frames:count,durationSeconds:count*.04,gifBytes:statSync(join(output,'zosc-02-motion.gif')).size}));
  }
  console.log(output);
}finally{if(ws)ws.close();chrome.kill();server.close()}
