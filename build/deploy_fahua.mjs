// 部署 /fahua/ 到兩站，並把 fahua 排進孵化區（唯識合注之下）。
//
//   node build/deploy_fahua.mjs --check    # 只檢查連線與目錄
//   node build/deploy_fahua.mjs            # 上傳＋併 projects.json＋驗證
//
// 憑證沿用 D:\nissaya.cn\.local\server.env（不讀進版控）。
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const ENV_FILE = 'D:\\nissaya.cn\\.local\\server.env';
const SRC = 'D:\\2026\\sdp\\deploy\\fahua';
const ENTRY = 'D:\\2026\\sdp\\deploy\\incubator.json';
const PROJECTS = 'D:\\nissaya.cn\\html\\incubator\\projects.json';
const CHECKER = 'D:\\nissaya.cn\\html\\incubator\\check.mjs';
const REMOTE_DIR = '/var/www/html/fahua';
const PSCP = 'C:\\Program Files\\PuTTY\\pscp.exe';
const PLINK = 'C:\\Program Files\\PuTTY\\plink.exe';
const FILES = [
  'index.html', 'teacher.html', 'donor.html', 'measure.html',
  'fahua-long.jpg', 'fahua-long-hant.jpg', 'cover.jpg', 'cover-hant.jpg',
];
const CHECK = process.argv.includes('--check');

function die(msg) { console.error('✗ ' + msg); process.exit(1); }
function run(cmd, label) {
  const r = spawnSync(cmd[0], cmd.slice(1), { encoding: 'utf8' });
  if (r.error) die(label + '：' + r.error.message);
  if (r.status !== 0) {
    const out = (r.stdout || '').trim();
    const err = (r.stderr || '').trim();
    die(label + '（exit ' + r.status + '）' + (out ? '\n' + out : '') + (err ? '\n' + err : ''));
  }
  return (r.stdout || '').trim();
}

const env = {};
for (const line of fs.readFileSync(ENV_FILE, 'utf8').split(/\r?\n/)) {
  const m = /^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$/.exec(line);
  if (m) env[m[1].toUpperCase()] = m[2].trim().replace(/^["']|["']$/g, '');
}
if (!env.HOST || !env.USER || !env.PASS) die('server.env 缺少 HOST／USER／PASS');

const targets = [{
  id: 'primary', label: '主站', host: env.HOST, port: env.PORT || '22',
  user: env.USER, pass: env.PASS,
  hostkey: 'D:\\2026\\zhu-combined\\.local\\hostkey.txt',
  base: 'https://shutonggui.cn',
}];
if (env.MIRROR_HOST) {
  targets.push({
    id: 'mirror', label: '鏡像', host: env.MIRROR_HOST, port: env.MIRROR_PORT || env.PORT || '22',
    user: env.MIRROR_USER || env.USER, pass: env.MIRROR_PASS || env.PASS,
    hostkey: 'D:\\2026\\zhu-combined\\.local\\hostkey-nissaya.cn.txt',
    base: 'https://nissaya.cn',
  });
}

for (const f of FILES) if (!fs.existsSync(path.join(SRC, f))) die('找不到 ' + f);
if (!fs.existsSync(ENTRY)) die('找不到 deploy/incubator.json');

// ---- 併 projects.json（記憶體中做，不寫 D:\nissaya.cn）----
const entry = JSON.parse(fs.readFileSync(ENTRY, 'utf8'));
const projects = JSON.parse(fs.readFileSync(PROJECTS, 'utf8'));
const at = projects.projects.findIndex((p) => p.id === entry.id);
if (at >= 0) projects.projects[at] = entry;
else {
  const w = projects.projects.findIndex((p) => p.id === 'weishi');
  if (w < 0) die('projects.json 找不到 weishi，停止');
  projects.projects.splice(w + 1, 0, entry);
}
projects.updated = new Date().toISOString().slice(0, 10);
const mergedPath = path.join(os.tmpdir(), `.fahua-projects-${process.pid}.json`);
fs.writeFileSync(mergedPath, JSON.stringify(projects, null, 2) + '\n', 'utf8');

const check = spawnSync(process.execPath, [CHECKER, mergedPath], { encoding: 'utf8' });
if (check.status !== 0) die('孵化區檢查器不合格：\n' + (check.stdout || '') + (check.stderr || ''));
console.log('✓ incubator/check.mjs 通過（' + projects.projects.map((p) => p.id).join(' → ') + '）');

function shq(s) { return "'" + String(s).replace(/'/g, "'\\''") + "'"; }

function makeTransport(t) {
  if (!fs.existsSync(t.hostkey)) die('找不到 ' + t.hostkey);
  const fp = fs.readFileSync(t.hostkey, 'utf8').trim();
  if (!/^SHA256:/.test(fp)) die(t.hostkey + ' 格式不正確');
  const pwFile = path.join(os.tmpdir(), `.fahua-pw-${process.pid}-${t.id}.tmp`);
  fs.writeFileSync(pwFile, t.pass + '\n', { mode: 0o600 });
  const upload = (localPath, remotePath) => run(
    [PSCP, '-batch', '-P', t.port, '-hostkey', fp, '-pwfile', pwFile, localPath, t.user + '@' + t.host + ':' + remotePath],
    `[${t.label}] 上傳 ${path.basename(remotePath)}`,
  );
  const remote = (script, label) => {
    const f = path.join(os.tmpdir(), `.fahua-${process.pid}-${t.id}.sh`);
    fs.writeFileSync(f, script);
    try {
      return run([PLINK, '-batch', '-ssh', '-P', t.port, '-l', t.user, '-hostkey', fp, '-pwfile', pwFile, '-m', f, t.host], `[${t.label}] ${label}`);
    } finally {
      fs.rmSync(f, { force: true });
    }
  };
  const done = () => fs.rmSync(pwFile, { force: true });
  return { upload, remote, done };
}

async function req(url, opts = {}, tries = 4) {
  let last;
  for (let i = 0; i < tries; i++) {
    try {
      return await fetch(url, { cache: 'no-store', ...opts });
    } catch (e) {
      last = e;
      await new Promise((r) => setTimeout(r, 1200 * (i + 1)));
    }
  }
  throw last;
}

async function verify(t) {
  const stamp = Date.now();
  const checks = [
    ['/fahua/', (s) => s.includes('法華合注') && s.includes('id="simToggle"') && s.includes('var P = "')],
    ['/fahua/teacher.html', (s) => s.includes('教學評估') && s.includes('89') && s.includes('¥') && s.includes('id="simToggle"')],
    ['/fahua/donor.html', (s) => s.includes('一句經文') && s.includes('26 家') && s.includes('id="simToggle"')],
    ['/fahua/measure.html', (s) => s.includes('語料實測') && s.includes('2,848') && s.includes('id="simToggle"')],
  ];
  for (const [p, ok] of checks) {
    const url = t.base + p + '?v=' + stamp;
    const r = await req(url);
    const s = await r.text();
    if (!r.ok) die('驗證失敗 ' + url + ' → HTTP ' + r.status);
    if (!ok(s)) die('內容不正確 ' + url + '（' + Buffer.byteLength(s) + ' bytes）');
    console.log('✓ ' + url + '  HTTP ' + r.status + '  ' + Buffer.byteLength(s) + ' bytes');
  }
  for (const f of ['fahua-long.jpg', 'fahua-long-hant.jpg', 'cover.jpg', 'cover-hant.jpg']) {
    const url = t.base + '/fahua/' + f + '?v=' + stamp;
    const r = await req(url);
    const buf = await r.arrayBuffer();
    if (!r.ok) die('圖檔失敗 ' + url + ' → HTTP ' + r.status);
    console.log('✓ ' + url + '  HTTP ' + r.status + '  ' + buf.byteLength + ' bytes');
  }
  const pj = await (await req(t.base + '/incubator/projects.json?v=' + stamp)).json();
  const ids = pj.projects.map((p) => p.id);
  const wi = ids.indexOf('weishi'), fi = ids.indexOf('fahua');
  if (fi < 0) die('projects.json 沒有 fahua');
  if (fi !== wi + 1) die('fahua 不在 weishi 之下：' + ids.join(' → '));
  if (pj.projects.find((p) => p.id === 'fahua').url !== '/fahua/') die('fahua url 不對');
  console.log('✓ /incubator/projects.json  順序 ' + ids.join(' → '));
}

for (const t of targets) {
  console.log(`\n== ${t.label} ${t.host}`);
  const tr = makeTransport(t);
  try {
    if (CHECK) {
      console.log(tr.remote([
        'set -e',
        'id',
        `ls -ld ${REMOTE_DIR} 2>/dev/null || echo NO_FAHUA_DIR`,
        'test -w /var/www/html && echo HTML_WRITABLE=yes || echo HTML_WRITABLE=no',
        'test -w /var/www/html/incubator && echo INCUBATOR_WRITABLE=yes || echo INCUBATOR_WRITABLE=no',
      ].join('\n'), '檢查'));
      continue;
    }

    tr.remote(`set -e\nmkdir -p ${REMOTE_DIR}\nchmod a+rx ${REMOTE_DIR}`, '建立目錄');
    for (const f of FILES) tr.upload(path.join(SRC, f), REMOTE_DIR + '/.tmp-' + f);
    tr.upload(mergedPath, '/var/www/html/incubator/.tmp-projects.json');

    const moves = ['set -e', 'cd ' + REMOTE_DIR];
    for (const f of FILES) {
      moves.push(`[ -f ${shq(f)} ] && cp -f ${shq(f)} ${shq(f + '.prev')} || true`);
      moves.push(`mv -f ${shq('.tmp-' + f)} ${shq(f)}`);
    }
    moves.push('chmod -R a+rX ' + REMOTE_DIR);
    moves.push('cd /var/www/html/incubator');
    moves.push('[ -f projects.json ] && cp -f projects.json projects.json.prev || true');
    moves.push('mv -f .tmp-projects.json projects.json');
    moves.push('chmod a+r projects.json');
    moves.push('echo DEPLOYED');
    console.log(tr.remote(moves.join('\n'), '切換檔案'));
  } finally {
    tr.done();
  }
  if (!CHECK) await verify(t);
}
fs.rmSync(mergedPath, { force: true });
console.log('\n完成。');
