// 頁面檢查：console 錯誤、水平溢出、圖片載入、標題。
// node build/check.mjs <width> <url...>
const [, , w = '1200', ...urls] = process.argv;
const width = Number(w);

const list = await (await fetch('http://127.0.0.1:9337/json/list')).json();
const target = list.find(t => t.type === 'page');
const ws = new WebSocket(target.webSocketDebuggerUrl);
let id = 0;
const pending = new Map();
const events = [];
const send = (m, p = {}) => new Promise((res, rej) => {
  const n = ++id; pending.set(n, { res, rej });
  ws.send(JSON.stringify({ id: n, method: m, params: p }));
});
ws.addEventListener('message', ev => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) {
    const { res, rej } = pending.get(m.id); pending.delete(m.id);
    m.error ? rej(new Error(m.error.message)) : res(m.result);
  } else if (m.method === 'Runtime.exceptionThrown') {
    events.push('exception: ' + (m.params.exceptionDetails.text || ''));
  } else if (m.method === 'Log.entryAdded' && m.params.entry.level === 'error') {
    events.push('log: ' + m.params.entry.text);
  }
});
await new Promise(r => ws.addEventListener('open', r, { once: true }));
await send('Runtime.enable');
await send('Log.enable');
await send('Emulation.setDeviceMetricsOverride', { width, height: 900, deviceScaleFactor: 1, mobile: width < 600 });

for (const url of urls) {
  events.length = 0;
  await send('Page.navigate', { url });
  await new Promise(r => setTimeout(r, 1400));
  const r = await send('Runtime.evaluate', {
    returnByValue: true,
    expression: `(() => {
      const de = document.documentElement;
      const imgs = [...document.images].map(i => ({src: i.getAttribute('src'), ok: i.complete && i.naturalWidth > 0}));
      return {
        title: document.title,
        scrollW: de.scrollWidth,
        clientW: de.clientWidth,
        h: de.scrollHeight,
        imgs,
        svgs: document.querySelectorAll('svg').length
      };
    })()`
  });
  const v = r.result.value;
  const bad = v.imgs.filter(i => !i.ok);
  console.log(`[${width}] ${url.split('/').pop()} | title=${v.title} | ${v.clientW}w scroll=${v.scrollW} h=${v.h} | svg=${v.svgs} | imgs=${v.imgs.length} bad=${bad.length}${bad.length ? ' ' + JSON.stringify(bad) : ''} | errors=${events.length}${events.length ? ' ' + events.join(' ; ') : ''}`);
}
ws.close();
process.exit(0);
