#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""無損簡體：把繁簡詞表嵌進頁面（官網文章的統一做法）。

正本在 `D:\\2026\\agent-norms\\lossless-simplified\\simplified-data.ts` 的
`SAFE_PAIRS`（一對一、無損；2,641 對）。本模組：

  1. 讀 SAFE_PAIRS，排除 `著→着`（會把「著作」變成「着作」）。
  2. 把整張表串成 `"繁簡繁簡…"` 字串（約 5,280 字、16 KB），嵌進頁面。
  3. 頁面 `body` 先隱藏，轉完再顯示；`<noscript>` 還原。
  4. 右下／頂欄切換鈕 `#simToggle`；主站缺省簡體、鏡像缺繁體，選擇記在 localStorage。
  5. 圖片（長圖）可用 `data-sim`／`data-trad` 跟著切換。

用法（由 `build/mk_site.py` 呼叫）：

    from zh_convert import inject
    html = inject(html)

**詞表是常數**：改文章只重跑發布，不必重建詞表；只有 agent-norms 的
SAFE_PAIRS 更新時才需要重跑（本模組每次發布都直接讀正本，沒有中間檔）。
"""
import re
from pathlib import Path

DATA = Path(r"D:\2026\agent-norms\lossless-simplified\simplified-data.ts")
SKIP_PAIRS = {"著"}          # 著→着 會壞詞，依 §13.3 排除

# Unihan 的 kSimplifiedVariant 有幾個字給的是罕見異體（例：線→缐），
# 與 OpenCC t2s 逐字比對後，這裡改正；KEEP 則是不該轉的（阪＝大阪、憍＝憍慢）。
OVERRIDE = {
    "線": "线", "綵": "彩", "託": "托", "鉅": "巨", "麴": "曲", "諮": "咨",
    "儁": "俊", "彞": "彝", "靦": "腼", "钁": "镢", "嶴": "岙",
}
KEEP = {"著", "阪", "垵", "憍"}

# SAFE_PAIRS 只收「一對一」的字，所以 週／並／劃／麼／臺／於／佔 這類
# 「簡體只有一個寫法、繁體是異體」的字沒有進來；它們轉了不會誤解，補上。
EXTRA = {
    "週": "周", "並": "并", "劃": "划", "麼": "么", "臺": "台",
    "於": "于", "佔": "占",
}

_cache = None


def safe_pairs() -> str:
    """回傳 `繁簡繁簡…` 字串（不含 著）。"""
    global _cache
    if _cache is not None:
        return _cache
    src = DATA.read_text(encoding="utf-8")
    lit = re.search(r'export const SAFE_PAIRS\s*=\s*((?:"[^"]*"\s*\+?\s*)+)', src).group(1)
    pairs = "".join(re.findall(r'"([^"]*)"', lit))
    out = []
    for i in range(0, len(pairs) - 1, 2):
        a, b = pairs[i], pairs[i + 1]
        if a in SKIP_PAIRS or a in KEEP:
            continue
        b = OVERRIDE.get(a, b)
        if a != b:
            out.append(a + b)
    for a, b in EXTRA.items():
        if a not in SKIP_PAIRS and a not in KEEP:
            out.append(a + b)
    _cache = "".join(out)
    return _cache


def script(p: str) -> str:
    return """
<noscript><style>body{visibility:visible!important}</style></noscript>
<script>
/* 無損簡體：詞表內嵌，不連外；主站缺省簡體、鏡像缺省繁體，切換記在 localStorage */
(function () {
  var P = "%s", M = {};
  for (var i = 0; i < P.length; i += 2) M[P.charAt(i)] = P.charAt(i + 1);
  var SKIP_TAG = /^(SCRIPT|STYLE|CODE|PRE|TEXTAREA)$/;
  var SKIP_CLASS = /(^|\\s)(mono|ex-code|urlbox|no-sim)(\\s|$)/;
  var nodes = [], orig = [];
  try {
    var w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false), n;
    while ((n = w.nextNode())) {
      var p = n.parentNode; if (!p) continue;
      if (SKIP_TAG.test(p.nodeName)) continue;
      var cn = p.className;
      if (typeof cn === "string" && SKIP_CLASS.test(cn)) continue;
      var v = n.nodeValue;
      if (!v || !v.replace(/\\s/g, "")) continue;
      nodes.push(n); orig.push(v);
    }
  } catch (e) { /* 沒有 TreeWalker 就原樣顯示 */ }

  var titleOrig = document.title;
  function conv(s) {
    var o = "", i;
    for (i = 0; i < s.length; i++) { var c = s.charAt(i); o += M[c] || c; }
    return o;
  }
  function apply(sim) {
    var i;
    for (i = 0; i < nodes.length; i++) nodes[i].nodeValue = sim ? conv(orig[i]) : orig[i];
    document.title = sim ? conv(titleOrig) : titleOrig;
    document.documentElement.lang = sim ? "zh-Hans" : "zh-Hant";
    var b = document.getElementById("simToggle");
    if (b) b.textContent = sim ? "繁體" : "简体";
    var els = document.querySelectorAll("[data-sim]");
    for (i = 0; i < els.length; i++) {
      var el = els[i], a = el.getAttribute(sim ? "data-sim" : "data-trad");
      if (a) { if (el.tagName === "IMG") el.src = a; else el.href = a; }
    }
  }

  var host = location.hostname.toLowerCase();
  var q = new URLSearchParams(location.search);
  var saved = null;
  try { saved = localStorage.getItem("rut.sim"); } catch (e) {}
  var sim = saved
    ? saved === "s"
    : (q.get("sim") === "1" ? true
      : q.get("sim") === "0" ? false
      : (host === "shutonggui.cn" || host === "www.shutonggui.cn"));

  try { apply(sim); } catch (e) {}
  document.body.style.visibility = "visible";

  var btn = document.getElementById("simToggle");
  if (btn) btn.addEventListener("click", function (e) {
    e.preventDefault();
    sim = !sim;
    apply(sim);
    try { localStorage.setItem("rut.sim", sim ? "s" : "t"); } catch (e2) {}
  });
}());
</script>
""" % p


def inject(html: str) -> str:
    """body 先隱藏、尾巴加詞表與腳本；已有切換鈕則沿用。"""
    if 'id="simToggle"' not in html:
        raise ValueError("頁面沒有 #simToggle，先加頂欄切換鈕")
    if "<body" not in html:
        raise ValueError("找不到 <body>")
    html = re.sub(r"<body([^>]*)>", r'<body\1 style="visibility:hidden">', html, count=1)
    p = safe_pairs()
    html = html.replace("</body>", script(p) + "</body>", 1)
    return html


if __name__ == "__main__":
    p = safe_pairs()
    print("pairs:", len(p) // 2, "chars:", len(p), "bytes:", len(p.encode("utf-8")))
