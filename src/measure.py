# -*- coding: utf-8 -*-
r"""法華合注 · 語料實測（給法師版的數字）

量三件事：
  1. 三種漢譯（T0262 什譯／T0263 護譯／T0264 闍笈譯）的字數、品數、句數；
  2. 各注疏的字數與卷數；
  3. 注疏對 T0262 的「自動錨定覆蓋率」——與金剛經／唯識合注同一套
     8 字窗滾動雜湊＋單調鏈（LIS）。

輸出：out/measure.json 與 out/measure.txt。

用法：
    python src/measure.py

漢字判定一律用母區共用 helper（AGENTS.md §2）。
"""
import json
import os
import re
import sys
import time

sys.path.insert(0, r'D:\2026\adb-converter\ts\tools')
from han import HAN, TAG  # noqa: E402

TAISHO = r'D:\2026\adb-converter\build\tei-all-2026R2.txt'
XUZANG = r'D:\2026\adb-converter\build\wxzj-tei-2026R2.txt'
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'out')

BOOK_RE = re.compile(r'<書 id="(n\d+)">([^<]*)</書>')
PIN_RE = re.compile(r'<品>([^<]*)</品>')
JUAN_RE = re.compile(r'<卷>([^<]*)</卷>')
PAGE_RE = re.compile(r'<頁 id="([^"]+)"/>')
SENT_SPLIT = re.compile(r'(?<=[。！？])')

# 主文與別譯
MAIN = ['n273', 'n274', 'n275']

# 注疏：(book id, 簡稱, 作者, 年代, 層級說明)
# layer: 1 = 直接註經；2 = 註「疏」（玄義／文句），不是註經
COMMENTARIES = [
    ('n1586', '法華論', '世親造·菩提流支等譯', '6C', 1),
    ('n1587', '法華論（優波提舍）', '世親造·勒那摩提等譯', '6C', 1),
    ('n1783', '法華經義記', '法雲', '梁', 1),
    ('n1784', '法華玄義', '智顗', '隋', 1),
    ('n1785', '法華玄義釋籤', '湛然', '唐', 2),
    ('n1786', '法華文句', '智顗', '隋', 1),
    ('n1787', '法華文句記', '湛然', '唐', 2),
    ('n1788', '法華玄論', '吉藏', '隋', 1),
    ('n1789', '法華義疏', '吉藏', '隋', 1),
    ('n1790', '法華遊意', '吉藏', '隋', 1),
    ('n1791', '法華玄贊', '窺基', '唐', 1),
    ('n1792', '法華玄贊義決', '慧沼', '唐', 2),
    ('n1793', '法華宗要', '元曉', '新羅', 1),
    ('n1886', '法華論疏', '吉藏', '隋', 2),
    ('n1996', '法華經安樂行義', '慧思', '陳', 1),
]

# 卍續藏：明清注疏與玄贊／文句的下位疏
# 注意：卍續藏的 <書 id> 是「每冊重新編號」，同一個 n370 在不同冊是不同書，
# 所以這裡要用（冊, id）當鍵，不能只用 id。
X_COMMENTARIES = [
    ('30:n368', '法華經合論', '戒環', '宋', 1),
    ('30:n370', '法華經科註', '一如', '元', 1),
    ('31:n371', '法華經科註（續）', '一如', '元', 1),
    ('31:n372', '法華經科註（續）', '一如', '元', 1),
    ('31:n373', '法華經知音', '如愚', '明', 1),
    ('31:n376', '法華經通義', '德清', '明', 1),
    ('32:n381', '法華經會義', '智旭', '明', 1),
    ('32:n384', '法華經大成', '淨昇', '清', 1),
    ('32:n388', '法華經授手', '智祥', '清', 1),
    ('33:n390', '法華經演義', '通理', '清', 1),
    ('33:n396', '法華經指掌疏', '通理', '清', 1),
    # 二層：註玄贊／註文句的疏
    ('28:n358', '法華經文句輔正記', '守一', '宋', 2),
    ('34:n401', '法華經玄贊要集', '栖復', '唐', 2),
]


def load_books(path, with_vol=False):
    """回傳 {key: {'title','lines','vol'}}；只留需要的書。

    with_vol=True 時（卍續藏）key 是「冊:id」，因為 id 每冊重新編號。
    """
    want = set(MAIN) | {c[0] for c in COMMENTARIES} | {c[0] for c in X_COMMENTARIES}
    books = {}
    cur = None
    vol = None
    VOL_RE = re.compile(r'<冊 id="([^"]+)">')
    with open(path, encoding='utf-8') as f:
        for line in f:
            vm = VOL_RE.search(line)
            if vm:
                vol = vm.group(1)
            m = BOOK_RE.search(line)
            if m:
                bid, title = m.group(1), m.group(2)
                key = (vol + ':' + bid) if with_vol else bid
                cur = key if key in want else None
                if cur:
                    books[cur] = {'title': title, 'lines': [], 'vol': vol}
                continue
            if cur:
                books[cur]['lines'].append(line)
    return books


def plain(lines):
    """去標籤、保留標點（切句要用）；回傳 (text, meta)。

    text 是「可讀文字」，漢字數用 HAN 另外算；T0263／T0264 的 <卷> 同時
    拿來標品，所以卷、品要看得標籤的內容才分得清。
    """
    raw = ''.join(lines)
    heads = JUAN_RE.findall(raw) + PIN_RE.findall(raw)
    # 「添品妙法蓮華經卷第一」也含「品」字，所以品要看「品第」；卷則是含「卷」
    # 但不含「品第」的標題（有的本子作「卷一」、有的作「卷第一」）。
    meta = {
        'pages': len(PAGE_RE.findall(raw)),
        'pins': [h for h in heads if '品第' in h],
        'juans': [h for h in heads if '卷' in h and '品第' not in h],
    }
    return TAG.sub('', raw), meta


def sentences(text, minlen=4):
    out = []
    for s in SENT_SPLIT.split(text):
        h = ''.join(HAN.findall(s))
        if len(h) >= minlen:
            out.append(h)
    return out


def grams(text, n=8):
    """8 字窗 → {gram: [pos, ...]}（只留前 200 個位置）。"""
    idx = {}
    for i in range(len(text) - n + 1):
        g = text[i:i + n]
        lst = idx.get(g)
        if lst is None:
            idx[g] = [i]
        elif len(lst) < 200:
            lst.append(i)
    return idx


def candidates(s, idx, n=8, cap=40):
    """一句話在注疏裡的所有落點。

    法華的注疏是「逐句／逐詞」體：常常只引句子中的一小段（「如是我聞」→
    一大段釋），所以不能只看句首 8 字；這一句裡任何一個 8 字窗命中都算候選。
    取候選時按視窗位置平均抽樣，避免句首的常見套語把候選全部佔滿。
    """
    if len(s) < n:
        return []
    seen = set()
    out = []
    step = max(1, (len(s) - n + 1) // 12)
    for i in range(0, len(s) - n + 1, step):
        for p in idx.get(s[i:i + n], [])[:8]:
            if p not in seen:
                seen.add(p)
                out.append(p)
        if len(out) >= cap:
            break
    out.sort()
    return out[:cap]


def anchor(main_sents, idx, n=8, mode='any'):
    """把主文句子依序錨到注疏；回傳 (命中句數, 總句數, 起訖位置)。

    做法是「貪心＋單調」：一句話在注疏裡找它所有 8 字窗的落點，取「比上一個
    錨點更後面」的第一個；找不到就跳過這一句，但**不重置**上一個錨點。
    這比全域 LIS 寬容（允許斷點），數字才是「這一句有沒有被注到」，不會因為
    中間缺一句就把後面全部歸零。mode='prefix' 只看句首 8 字（唯識的做法）。
    """
    total = len(main_sents)
    last = -1
    hit = 0
    start = end = None
    for s in main_sents:
        if mode == 'prefix':
            cands = idx.get(s[:n], []) if len(s) >= n else []
        else:
            cands = candidates(s, idx, n)
        if not cands:
            continue
        pick = None
        for p in cands:
            if p > last:
                pick = p
                break
        if pick is None:
            continue
        hit += 1
        last = pick
        if start is None:
            start = pick
        end = pick
    return hit, total, (start, end)


def main():
    t0 = time.time()
    print('讀取大正藏…', flush=True)
    taisho = load_books(TAISHO)
    print('讀取卍續藏…', flush=True)
    xuzang = load_books(XUZANG, with_vol=True)
    print('  %.1fs，大正 %d 部、卍續 %d 部' % (time.time() - t0, len(taisho), len(xuzang)),
          flush=True)

    result = {'main': [], 'commentaries': []}

    # ---- 主文 ----
    main_text = {}
    main_sents = {}
    for bid in MAIN:
        text, meta = plain(taisho[bid]['lines'])
        if bid == 'n273':
            # 去掉卷前的御製序／弘傳序
            raw = ''.join(taisho[bid]['lines'])
            i = raw.find('<卷>')
            body = raw[i:] if i > 0 else raw
            text = TAG.sub('', body)
            sent = sentences(text)
            main_sents[bid] = sent
            main_text[bid] = ''.join(HAN.findall(text))
            # 每品字數（也留每品的句子，錨定要按品分段）
            parts = re.split(r'<品>([^<]*)</品>', body)
            pins = []
            pin_groups = []
            for k in range(1, len(parts), 2):
                name, chunk = parts[k], parts[k + 1]
                pins.append({'name': name, 'chars': len(HAN.findall(TAG.sub('', chunk)))})
                pin_groups.append((name, sentences(chunk)))
            result['main'].append({
                'id': bid, 'title': taisho[bid]['title'], 'chars': len(main_text[bid]),
                'sentences': len(sent), 'pins': pins,
                'juan': len(meta['juans']), 'pages': meta['pages'],
            })
        else:
            sent = sentences(text)
            main_text[bid] = ''.join(HAN.findall(text))
            result['main'].append({
                'id': bid, 'title': taisho[bid]['title'], 'chars': len(main_text[bid]),
                'sentences': len(sent), 'pins': meta['pins'],
                'juan': len(meta['juans']), 'pages': meta['pages'],
            })

    print('主文：', [(m['id'], m['chars'], m['sentences']) for m in result['main']], flush=True)

    # ---- 注疏 ----
    print('T0262：%d 字、%d 句、%d 品'
          % (len(main_text['n273']), len(main_sents['n273']), len(pin_groups)), flush=True)

    for group, books in (('taisho', taisho), ('xuzang', xuzang)):
        rows = COMMENTARIES if group == 'taisho' else X_COMMENTARIES
        for bid, short, author, era, layer in rows:
            if bid not in books:
                print('  ! 缺 %s %s' % (bid, short), flush=True)
                continue
            b = books[bid]
            text, meta = plain(b['lines'])
            han = ''.join(HAN.findall(text))
            sent = sentences(text)
            t1 = time.time()
            idx = grams(han)
            # 按品分段錨定（跨品不共用鏈）
            hits = total = 0
            pin_hit = []
            for name, gs in pin_groups:
                h, t, _ = anchor(gs, idx, mode='any')
                hits += h
                total += t
                pin_hit.append((name, h, t))
            hits_p, total_p, _ = anchor(main_sents['n273'], idx, mode='prefix')
            result['commentaries'].append({
                'id': bid, 'title': b['title'], 'short': short,
                'author': author, 'era': era, 'layer': layer,
                'corpus': group, 'chars': len(han), 'sentences': len(sent),
                'juan': len(meta['juans']), 'pages': meta['pages'],
                'hits': hits, 'total': total, 'hits_prefix': hits_p,
                'coverage': round(hits / total * 100, 1) if total else 0,
                'coverage_prefix': round(hits_p / total_p * 100, 1) if total_p else 0,
                'pins_hit': sum(1 for _, h, _ in pin_hit if h > 0),
                'pin_detail': [{'name': n, 'hit': h, 'total': t} for n, h, t in pin_hit],
            })
            print('  %-18s %7d 字 卷%2d 錨(句內) %5.1f%%  句首 %5.1f%%  有注的品 %d/28 (%.1fs)'
                  % (short, len(han), len(meta['juans']),
                     hits / total * 100, hits_p / total_p * 100,
                     sum(1 for _, h, _ in pin_hit if h > 0), time.time() - t1),
                  flush=True)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, 'measure.json'), 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=1)

    # ---- 人看的摘要 ----
    lines = []
    lines.append('法華合注 · 語料實測 %s' % time.strftime('%Y-%m-%d %H:%M'))
    lines.append('')
    lines.append('【主文】')
    for m in result['main']:
        lines.append('  %s %s：%d 字、%d 句、%d 卷、%d 品'
                     % (m['id'], m['title'], m['chars'], m['sentences'],
                        m['juan'], len(m['pins'])))
    lines.append('')
    lines.append('【T0262 每品】')
    for p in result['main'][0]['pins']:
        lines.append('  %-28s %6d 字' % (p['name'], p['chars']))
    lines.append('')
    lines.append('【注疏 × T0262 錨定】')
    lines.append('  %-18s %-6s %3s %8s %5s %8s %8s %6s'
                 % ('注疏', '作者', '層', '字數', '卷', '錨(句內)', '錨(句首)', '有注品'))
    for c in result['commentaries']:
        lines.append('  %-18s %-6s %3d %8d %5d %7.1f%% %7.1f%% %4d/28'
                     % (c['short'], c['author'], c['layer'], c['chars'],
                        c['juan'], c['coverage'], c['coverage_prefix'],
                        c['pins_hit']))
    lines.append('')
    lines.append('注疏合計：%d 部、%d 字'
                 % (len(result['commentaries']),
                    sum(c['chars'] for c in result['commentaries'])))
    txt = '\n'.join(lines)
    with open(os.path.join(OUT, 'measure.txt'), 'w', encoding='utf-8') as f:
        f.write(txt)
    print(txt)
    print('共 %.1fs' % (time.time() - t0))


if __name__ == '__main__':
    main()
