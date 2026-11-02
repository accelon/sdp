// 全頁截圖（CDP）：node build/shot.mjs <url> <out.png> [width] [scale]
// 需要 Edge/Chrome 以 --remote-debugging-port=9337 啟動。
import { writeFileSync } from 'node:fs';

const [, , url, out, w = '1200', scale = '1'] = process.argv;
const width = Number(w);
const dpr = Number(scale);

const list = await (await fetch('http://127.0.0.1:9337/json/list')).json();
const target = list.find(t => t.type === 'page');
if (!target) throw new Error('no page target');

const ws = new WebSocket(target.webSocketDebuggerUrl);
let id = 0;
const pending = new Map();
const send = (method, params = {}) => new Promise((res, rej) => {
  const n = ++id;
  const timer = setTimeout(() => {
    pending.delete(n);
    rej(new Error('timeout: ' + method));
  }, 15000);
  pending.set(n, { res: v => { clearTimeout(timer); res(v); }, rej });
  ws.send(JSON.stringify({ id: n, method, params }));
});
ws.addEventListener('message', ev => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) {
    const { res, rej } = pending.get(m.id);
    pending.delete(m.id);
    m.error ? rej(new Error(m.error.message)) : res(m.result);
  }
});
await new Promise(r => ws.addEventListener('open', r, { once: true }));

await send('Page.enable');
await send('Emulation.setDeviceMetricsOverride', {
  width, height: 900, deviceScaleFactor: dpr, mobile: false
});
await send('Page.navigate', { url });
await new Promise(r => setTimeout(r, 1500));

const m1 = await send('Page.getLayoutMetrics');
const height = Math.ceil((m1.cssContentSize || m1.contentSize).height);
await send('Emulation.setDeviceMetricsOverride', {
  width, height, deviceScaleFactor: dpr, mobile: false
});
await new Promise(r => setTimeout(r, 600));
const shot = await send('Page.captureScreenshot', {
  format: 'png',
  captureBeyondViewport: true,
  fromSurface: true,
  clip: { x: 0, y: 0, width, height, scale: 1 }
});
writeFileSync(out, Buffer.from(shot.data, 'base64'));
console.log(out, width + 'x' + height, 'dpr', dpr, Buffer.from(shot.data, 'base64').length, 'bytes');
ws.close();
process.exit(0);
