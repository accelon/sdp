#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""長圖與封面：繁中母本 → 簡中輸出，交給 CDP 截圖。

用法（在 D:\\2026\\sdp 執行，Edge 需以 --remote-debugging-port=9337 啟動）：
    python build/mk_images.py           # 產生 html（繁／簡）
    node build/shot.mjs ...             # 再截圖（見 README）
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(r"D:\2026\sdp\out\pylibs")))
try:
    import opencc
except ImportError:  # pragma: no cover
    raise SystemExit("需要 opencc：python -m pip install --target out/pylibs opencc-python-reimplemented")

ROOT = Path(r"D:\2026\sdp")
BUILD = ROOT / "build"
cc = opencc.OpenCC("t2s")


def t2s(text: str) -> str:
    text = cc.convert(text)
    return (text.replace("「", "“").replace("」", "”")
                .replace("『", "‘").replace("』", "’"))


def main() -> None:
    for name in ("long", "cover"):
        src = (BUILD / f"{name}-hant.html").read_text(encoding="utf-8")
        han = src
        sim = t2s(src).replace('lang="zh-Hant"', 'lang="zh-Hans"')
        sim = sim.replace(
            '"Noto Serif TC","Source Han Serif TC","Songti TC","Songti SC",STSong,serif',
            '"Noto Serif SC","Source Han Serif SC","Songti SC",STSong,"SimSun",serif')
        (BUILD / f"{name}-s.html").write_text(sim, encoding="utf-8")
        print(name, "hant", len(han), "simp", len(sim))


if __name__ == "__main__":
    main()
