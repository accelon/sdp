#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""法華合注：產生 /fahua/ 的四個頁面（繁中母本，頁內嵌繁簡詞表）。

用法（在 D:\\2026\\sdp 執行）：
    python build\\mk_site.py

管線
----
法華-教學評估.html          ──┐
deploy/fahua/src/index.html  ─┼─> deploy/fahua/{teacher,index,donor}.html
deploy/fahua/src/donor.html  ─┘
docs/measure.md             ───> deploy/fahua/measure.html

每一頁都在 `</body>` 前注入 `build/zh_convert.py` 的詞表與腳本：
繁體母本、頁內無損轉簡體、主站缺省簡體／鏡像缺省繁體、切換記在 localStorage。
詞表是常數（agent-norms 的 SAFE_PAIRS），改文章只重跑這支，不必重建詞表。
"""
import html as htmllib
import re
import sys
from pathlib import Path

ROOT = Path(r"D:\2026\sdp")
OUT = ROOT / "deploy" / "fahua"
SRC = OUT / "src"
MOTHER = ROOT / "法華-教學評估.html"
MEASURE_MD = ROOT / "docs" / "measure.md"

sys.path.insert(0, str(ROOT / "build"))
import zh_convert  # noqa: E402


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
<meta name="description" content="法華合注的語料實測：字數、句數、二十六家注疏的錨定覆蓋率、方法與限制。">
<style>
  :root{{--paper:#f6f1e7;--card:#fffdf8;--ink:#1d1a16;--soft:#3a342d;--muted:#6d6357;--line:#ddd0bc;--accent:#8c3b2c;}}
  *{{box-sizing:border-box}}
  body{{margin:0;background:var(--paper);color:var(--ink);font-family:"Noto Serif TC","Source Han Serif TC","Songti TC","Songti SC",STSong,serif;font-size:16px;line-height:1.9}}
  .topbar{{position:sticky;top:0;z-index:80;background:rgba(246,241,231,.95);border-bottom:1px solid var(--line);backdrop-filter:blur(6px)}}
  .tb-inner{{max-width:900px;margin:0 auto;padding:0 22px;height:46px;display:flex;align-items:center;justify-content:space-between;font-size:13px}}
  .tb-inner a{{color:var(--muted);text-decoration:none}}
  #simToggle{{color:var(--accent);font-weight:600;border:1px solid rgba(140,59,44,.35);padding:2px 10px;border-radius:2px}}
  .wrap{{max-width:900px;margin:0 auto;padding:26px 22px 70px}}
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
  @media(max-width:520px){{ td:first-child{{white-space:normal}} }}
</style>
</head>
<body>

<div class="topbar"><div class="tb-inner">
  <a href="index.html">← 法華合注</a>
  <a href="#" id="simToggle" aria-label="切換繁體／簡體">简体</a>
</div></div>

<div class="wrap">
{body}
</div>
</body>
</html>
"""


def build_teacher() -> None:
    html = MOTHER.read_text(encoding="utf-8")
    (OUT / "teacher.html").write_text(zh_convert.inject(html), encoding="utf-8")
    print("teacher.html", (OUT / "teacher.html").stat().st_size)


def build_page(name: str) -> None:
    html = (SRC / f"{name}.html").read_text(encoding="utf-8")
    (OUT / f"{name}.html").write_text(zh_convert.inject(html), encoding="utf-8")
    print(f"{name}.html", (OUT / f"{name}.html").stat().st_size)


def build_measure() -> None:
    md = MEASURE_MD.read_text(encoding="utf-8")
    page = md2html(md, "法華合注 · 語料實測")
    (OUT / "measure.html").write_text(zh_convert.inject(page), encoding="utf-8")
    print("measure.html", (OUT / "measure.html").stat().st_size)


def cleanup() -> None:
    for f in OUT.glob("*-hant.html"):
        f.unlink()
        print("removed", f.name)


if __name__ == "__main__":
    build_teacher()
    for page in ("index", "donor"):
        build_page(page)
    build_measure()
    cleanup()
    print("done")
