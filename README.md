# sdp · 法華合注

《法華經》的教學層：**七卷二十八品、三種漢譯、二十六家注疏、兩部梵漢詞典**。
這一區放它的實測數據、教學文件包（法師版／護持版／落地頁）與未來的 `sdp.adb`。

- 線上（尚未部署）：`/fahua/`（主站簡體、鏡像繁體）
- 成品：`D:\2026\sdp\deploy\fahua\`（網頁）、`D:\accelon3\sdp.adb`（下一輪）
- 母工作區：`D:\2026\adb-converter`（共用工具、紀律、版本紀錄）
- 版控：<https://github.com/accelon/sdp>

## 這一輪交付（2026-11-02）

| 檔案 | 用途 |
|---|---|
| `法華-教學評估.html` | **法師版**母本：實測、成本、邊界、與 SDP 的分工；可離線、可印 A4 |
| `deploy/fahua/index.html`／`index-hant.html` | 落地頁（簡／繁） |
| `deploy/fahua/teacher.html`／`teacher-hant.html` | 法師版（由母本轉出） |
| `deploy/fahua/donor.html`／`donor-hant.html` | 護持版 |
| `deploy/fahua/measure.html`／`measure-hant.html` | 實測頁（`docs/measure.md` 轉出，公開可查） |
| `deploy/fahua/fahua-long.jpg`／`-hant.jpg` | 長圖 900×3036（約 210 KB） |
| `deploy/fahua/cover.jpg`／`cover-hant.jpg` | og:image 1200×630（約 34 KB） |
| `deploy/fahua/src/` | 落地頁、護持版的**繁體源檔**；簡體由 `build/mk_site.py` 轉出，不要手改 |
| `src/measure.py` | 語料實測（字數、句數、26 家注疏錨定）→ `out/measure.json` |
| `docs/measure.md` | 方法、數字、限制（報告的每一個百分點都在這裡） |
| `docs/sources.md` | 來源、授權、下載位置 |
| `docs/steps.md` | 從零重跑的步驟與 `sdp.adb` 的暫定規則 |

**先不放孵化區**：`incubator/projects.json` 沒有這一筆，官網也還沒上傳（等作者指示）。

## 核心數字

- 主文：T0262 72,550 字、2,848 句、七卷、二十八品；別譯 T0263 88,493 字、T0264 73,616 字。
- 注疏：26 家、28 部、**5,469,480 字**（大正藏 15 部＋卍續藏 13 部）。
- 句子級錨定：夾註三家 84–89%（科註 88.7／會義 88.5／演義 84.4）；
  隋唐逐句釋 2–9%（義記 9.1／義疏 8.5／玄贊 5.3／文句 3.6）；品級幾乎 28/28。
- 梵漢詞典：KKJ 2,409 條／31,733 引文；KDR 3,356 條／45,649 引文（CC BY-SA 3.0）。
- 工時模型：一品 60 h → 14 h；二十八品 1,680 h → 404 h（4.2×）。

**結論**：法華不能照搬唯識的單層句級模型，要用「句→品→詞」三層索引。

## 重建

```powershell
cd D:\2026\sdp
python -m pip install --target out\pylibs opencc-python-reimplemented   # 只做一次
python src\measure.py        # 量測 → out\measure.json
python build\mk_site.py      # 繁中母本 → 繁／簡六頁 ＋ measure 頁
python build\mk_images.py    # 長圖／封面的簡中 HTML（再用 Edge CDP 截圖，見 docs\steps.md）
```

截圖需要 Edge（`--remote-debugging-port=9337`）與 `build/shot.mjs`；完整指令在 `docs/steps.md` §1。

## 目錄

| 路徑 | 說明 |
|---|---|
| `AGENTS.md` | 這一區的規則；§0 要求先讀母區的紀律文件 |
| `src/` | 量測與轉檔腳本 |
| `build/` | 產頁、繁簡、長圖、截圖（`shot.mjs`） |
| `data/external/` | 辛嶋詞典 TEI（不進版控；下載位置見 `docs/sources.md`） |
| `deploy/fahua/` | 上架包 |
| `docs/` | measure／sources／steps |
| `out/` | 中間產物（不進版控） |

## 已知限制

- 「有錨」不等於「錨對」；上線前要抽樣人工核（每品 10 句，共 280 句）。
- 26 家的句級數字是按品分段、8 字窗、允許斷點的實測；不是精確率。
- 成本、工時都是模型估算；假設寫在報告 §5 與附註。
- SDP 只連結、未複製；辛嶋詞典若要併入資料庫，整個資料庫要以 CC BY-SA 釋出。

## 下一步

1. 取得作者指示後部署到兩站 `/fahua/`（先不進孵化區清單）。
2. `sdp.adb` 第一版：T0262 × 三部夾註 × 28 品（句／品兩層）。
3. 梵漢層：KKJ 2,409 條接入 `<术>` 與 `glossary`。
4. 母區記帳：`docs/adb/adb-version-log.md`、`deploy/adb-notes.json`。
