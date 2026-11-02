# sdp · 法華合注

《法華經》的教學層：**七卷二十八品、三種漢譯、二十六家注疏、兩部梵漢詞典**。
這一區放它的實測數據、教學文件包（法師版／護持版／落地頁）與官網上架包。

- 線上：<https://shutonggui.cn/fahua/>（主站，缺省簡體）· <https://nissaya.cn/fahua/>（鏡像，缺省繁體）
- 孵化區：<https://shutonggui.cn/incubator/>（排在「唯識合注」之下）
- 母工作區：`D:\2026\adb-converter`（共用工具、紀律、版本紀錄）
- 版控：<https://github.com/accelon/sdp>

## 這一輪交付（2026-11-02）

| 檔案 | 用途 |
|---|---|
| `法華-教學評估.html` | **法師版**母本：實測、成本、邊界、與 SDP 的分工；可離線、可印 A4 |
| `deploy/fahua/index.html` | 落地頁（法師版／護持版兩個入口） |
| `deploy/fahua/teacher.html` | 法師版（由母本產出） |
| `deploy/fahua/donor.html` | 護持版 |
| `deploy/fahua/measure.html` | 實測頁（`docs/measure.md` 轉出，公開可查） |
| `deploy/fahua/fahua-long.jpg`／`-hant.jpg` | 長圖 900×3036（約 210 KB） |
| `deploy/fahua/cover.jpg`／`cover-hant.jpg` | og:image 1200×630（約 34 KB） |
| `deploy/fahua/src/` | 落地頁、護持版的**繁體源檔**；產出的 `index.html`、`donor.html` 不要手改 |
| `deploy/incubator.json` | 孵化區清單條目（已併進兩站 `projects.json`） |
| `src/measure.py` | 語料實測（字數、句數、26 家注疏錨定）→ `out/measure.json` |
| `build/mk_site.py`、`build/zh_convert.py` | 繁中母本 → 四頁；頁內嵌繁簡詞表 |
| `build/deploy_fahua.mjs` | 上傳兩站、併孵化區清單、驗證 |
| `docs/measure.md` | 方法、數字、限制（報告的每一個百分點都在這裡） |
| `docs/sources.md` | 來源、授權、下載位置 |
| `docs/zh-convert.md` | 頁內嵌繁簡詞表的做法（官網文章的統一標準） |
| `docs/steps.md` | 從零重跑的步驟 |

## 繁簡（重要）

- **繁體是母本**，簡體是執行時用**頁內嵌詞表**轉的；不另存簡體檔。
- 主站缺省簡體、鏡像缺省繁體；頂欄右側有「簡／繁」切換，選擇記在 `localStorage`，換頁仍記得。
- 詞表是常數（`agent-norms` 的 `SAFE_PAIRS`，2,640 對、15.8 KB）；**改文章不必重建詞表**，發布前重跑 `mk_site.py` 即可。
- 細節與新文章接法：`docs/zh-convert.md`。

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
python src\measure.py        # 量測 → out\measure.json（需要母區 CBETA 語料）
python build\mk_site.py      # 繁中母本 → 四頁（自動嵌入繁簡詞表）
node build\deploy_fahua.mjs --check   # 連線與權限
node build\deploy_fahua.mjs           # 上傳兩站＋併孵化區＋驗證
```

長圖與封面的簡中版用 `build/mk_images.py` ＋ Edge CDP 截圖，指令見 `docs/steps.md`。

## 目錄

| 路徑 | 說明 |
|---|---|
| `AGENTS.md` | 這一區的規則；§0 要求先讀母區的紀律文件 |
| `src/` | 量測腳本 |
| `build/` | 產頁、繁簡、長圖、截圖、部署（`deploy_fahua.mjs`） |
| `data/external/` | 辛嶋詞典 TEI（不進版控；下載位置見 `docs/sources.md`） |
| `deploy/fahua/` | 上架包（四頁＋四張圖） |
| `docs/` | measure／sources／zh-convert／steps |
| `out/` | 中間產物（不進版控） |

## 已知限制

- 「有錨」不等於「錨對」；上線前要抽樣人工核（每品 10 句，共 280 句）。
- 26 家的句級數字是按品分段、8 字窗、允許斷點的實測；不是精確率。
- 成本、工時都是模型估算；假設寫在報告 §5 與附註。
- 繁簡是字形轉換，不改詞彙（「數位」「資料庫」在簡體頁仍是台灣用語）；`SAFE_PAIRS` 對少數字取保守策略，已在 `zh_convert.py` 補了幾個常見字。
- SDP 只連結、未複製；辛嶋詞典若要併入資料庫，整個資料庫要以 CC BY-SA 釋出。

## 下一步

1. 「法華合注」閱讀器（`sdp.adb`）尚未開始；`docs/steps.md` §2 已寫頁 id 與流程。
2. 梵漢層：KKJ 2,409 條接入 `<术>` 與 `glossary`。
3. 把 `docs/zh-convert.md` 的做法推廣到官網其他文章（作者 2026-11-02 指示）。
