#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 /fahua/ 的繁體（源）與簡體（無損轉出）頁面。

用法（在 D:\\2026\\sdp 執行）：
    python build/mk_site.py

管線（繁體為源，簡體由 OpenCC t2s 無損轉出，不改詞彙）
----
繁中母本 法華-教學評估.html ───────────> teacher-hant.html ──(t2s)──> teacher.html
deploy/fahua/src/index.html  ─────────> index-hant.html   ──(t2s)──> index.html
deploy/fahua/src/donor.html  ─────────> donor-hant.html   ──(t2s)──> donor.html
docs/measure.md              ─────────> measure-hant.html ──(t2s)──> measure.html

每頁都插入：
  * hreflang：zh-Hans 指主站、zh-Hant 指鏡像
  * hostname 切換：shutonggui.cn 缺省簡體、nissaya.cn 缺省繁體
  * 右下角「簡／繁」無損轉換按鈕（僅字形，不改詞彙；以 cookie 記住選擇）
切換區塊以 <!--lang-switch--> 標記，可重複執行。
"""
import html as htmllib
import os
import re
import sys
from pathlib import Path

# OpenCC：用 `python -m pip install --target out/pylibs opencc-python-reimplemented`
# 裝在工作區內（out/ 不進版控）；沒裝就給出清楚指示。
sys.path.insert(0, str(Path(r"D:\2026\sdp\out\pylibs")))
try:
    import opencc
except ImportError:  # pragma: no cover
    raise SystemExit("需要 opencc：python -m pip install --target out/pylibs opencc-python-reimplemented")

ROOT = Path(r"D:\2026\sdp")
OUT = ROOT / "deploy" / "fahua"
SRC = OUT / "src"
MOTHER = ROOT / "法華-教學評估.html"
MEASURE_MD = ROOT / "docs" / "measure.md"

MAIN = "https://shutonggui.cn/fahua/"
MIRROR = "https://nissaya.cn/fahua/"

cc_t2s = opencc.OpenCC("t2s")

FONTS_TC = [
    ('"Noto Serif SC","Source Han Serif SC","Songti SC",STSong,"SimSun",serif',
     '"Noto Serif TC","Source Han Serif TC","Songti TC","Songti SC",STSong,serif'),
    ('"Noto Sans SC","Source Han Sans SC","PingFang SC","Microsoft YaHei"',
     '"Noto Sans TC","Source Han Sans TC","PingFang TC","Microsoft JhengHei"'),
]
FONTS_SC = [(b, a) for a, b in FONTS_TC]

SWITCH_HEAD = """<!--lang-switch-->
<script>
/* 主站 shutonggui.cn 缺省簡體、鏡像 nissaya.cn 缺省繁體；右下角按鈕可無損切換，選擇記在 cookie */
(function () {
  if (location.protocol === 'file:') return;
  var host = location.hostname.replace(/^www\\./, '');
  var m = document.cookie.match(/(?:^|;\\s*)fahua-lang=(zh-Hans|zh-Hant)/);
  var want = m ? m[1] : (/(^|\\.)nissaya\\.cn$/.test(host) ? 'zh-Hant' : 'zh-Hans');
  var path = location.pathname;
  var isHant = /-hant\\.html$/.test(path);
  var other;
  if (isHant) {
    other = path.replace(/-hant\\.html$/, '.html');
  } else if (/\\/$/.test(path)) {
    other = path + 'index-hant.html';
  } else if (/\\/index\\.html$/.test(path)) {
    other = path.replace(/index\\.html$/, 'index-hant.html');
  } else {
    other = path.replace(/\\.html$/, '-hant.html');
  }
  if (want === 'zh-Hant' && !isHant) location.replace(other + location.search + location.hash);
  else if (want === 'zh-Hans' && isHant) location.replace(other + location.search + location.hash);
})();
</script>
<!--/lang-switch-->"""

TOGGLE_HTML = """<!--lang-toggle-->
<a id="lang-toggle" href="#" hidden
   style="position:fixed;right:14px;bottom:14px;z-index:60;background:var(--card,#fffdf8);color:var(--accent,#8c3b2c);border:1px solid var(--line,#ddd0bc);font:600 13px/1.2 system-ui,-apple-system,'Segoe UI',sans-serif;padding:9px 12px;border-radius:3px;text-decoration:none;box-shadow:0 2px 8px rgba(0,0,0,.14)">简</a>
<script>
(function () {
  var btn = document.getElementById('lang-toggle');
  if (!btn) return;
  var path = location.pathname;
  var isHant = /-hant\\.html$/.test(path);
  var other, otherLang;
  if (isHant) {
    other = path.replace(/-hant\\.html$/, '.html'); otherLang = 'zh-Hans';
  } else if (/\\/$/.test(path)) {
    other = path + 'index-hant.html'; otherLang = 'zh-Hant';
  } else if (/\\/index\\.html$/.test(path)) {
    other = path.replace(/index\\.html$/, 'index-hant.html'); otherLang = 'zh-Hant';
  } else {
    other = path.replace(/\\.html$/, '-hant.html'); otherLang = 'zh-Hant';
  }
  btn.href = other + location.search + location.hash;
  btn.textContent = otherLang === 'zh-Hant' ? '繁' : '简';
  btn.title = otherLang === 'zh-Hant' ? '無損轉為繁體（僅字形，不改詞彙）' : '無損轉為簡體（僅字形，不改詞彙）';
  btn.addEventListener('click', function () {
    document.cookie = 'fahua-lang=' + otherLang + ';path=/;max-age=31536000;samesite=lax';
  });
  btn.hidden = false;
})();
</script>
<!--/lang-toggle-->"""


def t2s(text: str) -> str:
    """字形層的無損轉換：OpenCC t2s，外加引號（“”）。不替換詞彙。"""
    text = cc_t2s.convert(text)
    return (text.replace("「", "“").replace("」", "”")
                .replace("『", "‘").replace("』", "’"))


def strip_chrome(html: str) -> str:
    html = re.sub(r"<!--lang-switch-->.*?<!--/lang-switch-->\s*", "", html, flags=re.S)
    html = re.sub(r"<!--lang-toggle-->.*?<!--/lang-toggle-->\s*", "", html, flags=re.S)
    html = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">\s*', "", html)
    return html


def hreflang(page: str) -> str:
    if page == "index":
        hans, hant = MAIN, MIRROR + "index-hant.html"
    else:
        hans, hant = MAIN + page + ".html", MIRROR + page + "-hant.html"
    return (
        f'<link rel="alternate" hreflang="zh-Hans" href="{hans}">\n'
        f'<link rel="alternate" hreflang="zh-Hant" href="{hant}">\n'
        f'<link rel="alternate" hreflang="x-default" href="{hans}">\n'
    )


def finalize(html: str, hant: bool, page: str) -> str:
    html = strip_chrome(html)
    lang = "zh-Hant" if hant else "zh-Hans"
    html = re.sub(r'<html lang="[^"]*">', f'<html lang="{lang}">', html, count=1)
    for a, b in (FONTS_TC if hant else FONTS_SC):
        html = html.replace(a, b)
    for name in ("index", "teacher", "donor", "measure"):
        if hant:
            html = re.sub(rf'href="{name}\.html', f'href="{name}-hant.html', html)
        else:
            html = re.sub(rf'href="{name}-hant\.html', f'href="{name}.html', html)
    if hant:
        html = html.replace("fahua-long.jpg", "fahua-long-hant.jpg")

    page_url = (MIRROR if hant else MAIN) + (
        "index-hant.html" if hant and page == "index" else
        "index.html" if not hant and page == "index" else
        f"{page}-hant.html" if hant else f"{page}.html")
    if '<meta property="og:url"' in html:
        html = re.sub(r'<meta property="og:url" content="[^"]*">',
                      f'<meta property="og:url" content="{page_url}">', html, count=1)
    if '<meta property="og:image"' in html:
        html = re.sub(r'<meta property="og:image" content="[^"]*">',
                      f'<meta property="og:image" content="{(MIRROR + "cover-hant.jpg") if hant else (MAIN + "cover.jpg")}">',
                      html, count=1)

    assert "</head>" in html and "</body>" in html
    html = html.replace("</head>", hreflang(page) + SWITCH_HEAD + "\n</head>", 1)
    html = html.replace("</body>", TOGGLE_HTML + "</body>", 1)
    return html


def inline(s: str) -> str:
    s = htmllib.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    s = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', s)
    return s


def md2html(md: str, title: str) -> str:
    """夠用的 markdown：標題、段落、清單、表格、粗體、行內 code。"""
    lines = md.split("\n")
    out, i = [], 0
    para = []

    def flush():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    while i < len(lines):
        ln = lines[i]
        if ln.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[-: |]+\|$", lines[i + 1]):
            flush()
            head = [c.strip() for c in ln.strip("|").split("|")]
            out.append('<div class="tw"><table><thead><tr>' + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>")
            i += 2
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip("|").split("|")]
                out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
                i += 1
            out.append("</tbody></table></div>")
            continue
        if ln.startswith("> "):
            flush()
            quote = []
            while i < len(lines) and lines[i].startswith(">"):
                quote.append(lines[i].lstrip(">").strip())
                i += 1
            out.append("<blockquote><p>" + inline(" ".join(q for q in quote if q)) + "</p></blockquote>")
            continue
        if ln.startswith("### "):
            flush(); out.append(f"<h3>{inline(ln[4:])}</h3>")
        elif ln.startswith("## "):
            flush(); out.append(f"<h2>{inline(ln[3:])}</h2>")
        elif ln.startswith("# "):
            flush(); out.append(f"<h1>{inline(ln[2:])}</h1>")
        elif re.match(r"^[-*] ", ln):
            flush()
            items = []
            while i < len(lines) and lines[i].strip():
                if re.match(r"^[-*] ", lines[i]):
                    items.append(inline(lines[i][2:]))
                elif re.match(r"^\d+\. ", lines[i]) or lines[i].startswith("#") or lines[i].startswith("|"):
                    break
                else:
                    items[-1] += inline(" " + lines[i].strip())
                i += 1
            out.append("<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>")
            continue
        elif re.match(r"^\d+\. ", ln):
            flush()
            items = []
            while i < len(lines) and lines[i].strip():
                if re.match(r"^\d+\. ", lines[i]):
                    items.append(inline(re.sub(r"^\d+\. ", "", lines[i])))
                elif re.match(r"^[-*] ", lines[i]) or lines[i].startswith("#") or lines[i].startswith("|"):
                    break
                else:
                    items[-1] += inline(" " + lines[i].strip())
                i += 1
            out.append("<ol>" + "".join(f"<li>{x}</li>" for x in items) + "</ol>")
            continue
        elif ln.strip() == "":
            flush()
        else:
            para.append(ln.strip())
        i += 1
    flush()
    body = "\n".join(out)
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>{htmllib.escape(title)}</title>
<style>
  :root{{--paper:#f6f1e7;--card:#fffdf8;--ink:#1d1a16;--soft:#3a342d;--muted:#6d6357;--line:#ddd0bc;--accent:#8c3b2c;}}
  *{{box-sizing:border-box}}
  body{{margin:0;background:var(--paper);color:var(--ink);font-family:"Noto Serif TC","Source Han Serif TC","Songti TC","Songti SC",STSong,serif;font-size:16px;line-height:1.9}}
  .wrap{{max-width:900px;margin:0 auto;padding:34px 22px 70px}}
  a{{color:var(--accent)}}
  h1{{font-size:30px;line-height:1.35;margin:0 0 8px}}
  h2{{font-size:23px;margin:38px 0 12px;padding-top:14px;border-top:1px solid var(--line)}}
  h3{{font-size:18px;margin:24px 0 8px}}
  p,li{{color:var(--soft)}}
  code{{background:#efe6d5;padding:1px 4px;border-radius:2px;font-size:.9em}}
  .tw{{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:18px 0}}
  table{{width:100%;border-collapse:collapse;font-size:14px;background:var(--card)}}
  th{{text-align:left;font-size:12px;letter-spacing:.06em;color:var(--muted);border-bottom:1.5px solid var(--ink);padding:8px 10px;white-space:nowrap}}
  td{{padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top}}
  td:first-child{{white-space:nowrap}}
  blockquote{{margin:18px 0;padding:6px 0 6px 16px;border-left:3px solid var(--accent);color:var(--soft)}}
  .back{{font-size:13px;margin-bottom:18px;display:inline-block}}
</style>
</head>
<body>
<div class="wrap">
<a class="back" href="index.html">← 法華合注</a>
{body}
</div>
</body>
</html>
"""


def build_teacher() -> None:
    base = MOTHER.read_text(encoding="utf-8")
    hant = finalize(base, True, "teacher")
    hans = finalize(t2s(base), False, "teacher")
    (OUT / "teacher-hant.html").write_text(hant, encoding="utf-8")
    (OUT / "teacher.html").write_text(hans, encoding="utf-8")
    print("teacher-hant.html", len(hant), "\tteacher.html", len(hans))


def build_page(name: str) -> None:
    src = (SRC / f"{name}.html").read_text(encoding="utf-8")
    hant = finalize(src, True, name)
    hans = finalize(t2s(src), False, name)
    (OUT / f"{name}-hant.html").write_text(hant, encoding="utf-8")
    (OUT / f"{name}.html").write_text(hans, encoding="utf-8")
    print(f"{name}-hant.html", len(hant), f"\t{name}.html", len(hans))


def build_measure() -> None:
    md = MEASURE_MD.read_text(encoding="utf-8")
    title = "法華合注 · 語料實測"
    page = md2html(md, title)
    hant = finalize(page, True, "measure")
    hans = finalize(t2s(page), False, "measure")
    (OUT / "measure-hant.html").write_text(hant, encoding="utf-8")
    (OUT / "measure.html").write_text(hans, encoding="utf-8")
    print("measure-hant.html", len(hant), "\tmeasure.html", len(hans))


if __name__ == "__main__":
    build_teacher()
    for page in ("index", "donor"):
        build_page(page)
    build_measure()
    print("done")
