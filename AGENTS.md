# AGENTS.md — `sdp` 工作區

> 這個資料夾是 **法華合注**（`sdp.adb`）的建置工作區。`D:\2026\sdp`。
> 本檔只寫「這一庫的差異」；**共用紀律在母工作區**，先讀完再動手。

## 0. 先讀（紀律來源，必讀）

| 順序 | 文件 | 為什麼 |
|---|---|---|
| 1 | `D:\2026\adb-converter\AGENTS.md` | 母工作區規則：成品放 `D:\accelon3`、viewer 位置、發佈權限、不要 commit 等 |
| 2 | `D:\2026\adb-converter\docs\adb\adb-knowhow.md` | **共用 know-how**：容器、VA、漢字位置、缺字／字型、`glossary`／`<术>`、`<聯 j>`、建置六步 |
| 3 | `D:\2026\adb-converter\docs\adb\adb-version-log.md` | 版本紀錄（canonical）：每次建置要加一列 |
| 4 | 依需要：`han-position.md`、`terms.md`、`glossary.md`、`missing-char.md` | 座標、術語、詞彙、缺字 |

> 這四份是**母工作區的檔案**，不要複製過來；直接讀。母工作區是規則與工具的家，
> 本工作區是資料與建置的家。

## 1. 這個工作區做什麼

- 產出：
  - 教學文件包：`deploy/fahua/`（法師版、護持版、落地頁、實測頁；頁內嵌繁簡詞表）
  - `sdp.adb`（`dbname=sdp`、`dbcname=法華合注`；下一輪）
- 來源：**CBETA 2026.R2**（大正藏 T0262／T0263／T0264；注疏 26 家）＋
  辛嶋靜志詞典 KKJ／KDR（DILA 數位版，CC BY-SA 3.0）；
  研究層參照 DILA SDP（CC BY-SA 4.0，只連結、不複製）
- 成品位置：網頁已上線 `/fahua/`（主站＋鏡像）；adb 為 `D:\accelon3\sdp.adb`
- 文件：本區 `README.md`、`docs/measure.md`（數字來源）、`docs/sources.md`（授權）、
  `docs/zh-convert.md`（繁簡機制）、`docs/steps.md`（重跑步驟）
- 版控：<https://github.com/accelon/sdp>

### 1.1 現況（2026-11-02）

- 已完成：語料實測（`src/measure.py`）、法師版（`法華-教學評估.html`）、
  護持版、落地頁、實測頁、長圖與封面；**已部署兩站 `/fahua/`**，
  孵化區清單排在「唯識合注」之下。
- 繁簡：繁體母本、頁內嵌詞表（`build/zh_convert.py`）；主站缺省簡體、鏡像缺省繁體，
  頂欄切換記在 `localStorage`。改文章不必重建詞表（見 `docs/zh-convert.md`）。
- 核心結論：**法華不能照搬唯識的單層句級錨定**。夾註三家（科註 88.7／會義 88.5／
  演義 84.4）可逐句錨；隋唐逐句釋（義記／義疏／玄贊／文句）只有 2–9%，因為它們引詞
  不引句；但品級幾乎 28/28。所以資料模型是「句→品→詞」三層。
- 未做：`sdp.adb`（作者指示不必做）。
- 下一個動作：依 `docs/steps.md` 可從零重跑；要改文章先改繁中母本，再 `mk_site.py`＋
  `deploy_fahua.mjs`。

## 2. 共用程式（不要重寫一份）

| 用途 | 用哪一個 |
|---|---|
| 漢字判定／計數 | `D:\2026\adb-converter\ts\src\accelon26\han.ts`（TS）<br>`D:\2026\adb-converter\ts\tools\han.py`（Python） |
| 頁 id → VA → 頁純漢字 | `D:\2026\adb-converter\ts\src\accelon26\page-text.ts` |
| 打包容器 | `D:\2026\adb-converter\ts\src\adbauthor.ts`（`authorAdb`） |
| 術語 `<术>`／glossary | `D:\2026\adb-converter\ts\src\terms\terms.ts`（canonical 詞表 `data/terms.tsv`） |
| 詞彙閱讀端 | 母區 `ts/src/accelon26/glossary.ts`（不用改） |

Python 端的路徑寫法：

```python
import sys
sys.path.insert(0, r'D:\2026\adb-converter\ts\tools')
from han import HAN, han_chars, han_count
```

**禁止**在這一區再寫一份 `[\u3400-\u9fff…]` 或 `\p{Script=Han}` 的規則；
發現共用 helper 有問題，回母工作區修，不要就地分叉。

## 3. 建置

```text
① 取源（原始檔放 raw/ 或 data/，唯讀）
② 轉文字（一行一個 adb 行；超過 4,000 字要切）
③ 補資料（缺字、術語、頁碼、圖片；外部檔，不改原始檔）
④ 連結（<聯>、<嵌>、j；patch 要最後跑，重轉文字後要再 patch）
⑤ 打包（pack.ts → authorAdb）
⑥ 驗證＋記帳
```

- 建置腳本放 `src/`，中間產物放 `out/`（不進版控），成品 copy 到 `D:\accelon3`。
- 建置要能**從零重跑**：來源、指令、版本寫在 `README.md` 或 `docs/steps.md`。
- 頁 id 格式一旦定好就不要改；VA 若變，記錄「哪一頁之後、差幾個」。

### 3.1 網頁文件包（本輪）

```text
① 量測（src/measure.py → out/measure.json）
② 繁體母本（法華-教學評估.html、deploy/fahua/src/{index,donor}.html）
③ 產頁＋嵌詞表（build/mk_site.py → build/zh_convert.py → deploy/fahua/*.html）
④ 圖（build/mk_images.py → build/long*.html、cover*.html → Edge CDP → JPG）
⑤ 檢查（390／1200 截圖、console 0 error、無橫向溢出）
⑥ 上架（build/deploy_fahua.mjs → 兩站 /fahua/ ＋孵化區 projects.json）
```

- 繁體是母本，**不再產簡體檔**：每頁內嵌繁簡詞表，執行時無損轉換；詳見 `docs/zh-convert.md`。
- 詞表是常數（`agent-norms` 的 `SAFE_PAIRS`）；**改文章不必重建詞表**，重跑 `mk_site.py` 即可。
- 主站缺省簡體、鏡像缺省繁體；頂欄要有 `<a id="simToggle">`，否則 `mk_site.py` 會丟錯。
- 改了文字要重跑 `mk_site.py` 再 `deploy_fahua.mjs`，否則線上與母本不一致。
- `measure.html` 由 `docs/measure.md` 轉出；改數字先改量測與 `measure.md`。
- 孵化區清單條目在 `deploy/incubator.json`；部署時併進兩站 `projects.json`（排在 weishi 之後）。

## 4. 版本、發布、記帳

1. 建置完成 → 在**母工作區** `deploy/adb-notes.json` 寫這個 sha 的說明（由本區提供文字）。
2. 在**母工作區** `docs/adb/adb-version-log.md` 加一列：
   日期／`sdp`／sha 前 12／大小／buildTime／工作區／說明。
3. 發布由**本工作區**執行（`publish-adb.ts`，大檔加 `--allow-large`）；
   官網 release（exe）仍由母工作區。
4. 發布後確認兩站 sha 與 manifest 一致。

> 工作區日後可能停用；沒有版本紀錄，後人只能猜。**這一列不是可選項。**

- 本輪只有網頁、還沒有 `sdp.adb`：**不記 adb 帳**；等 adb 建好再補。
- `/fahua/` 已於 2026-11-02 依作者指示上線兩站，並列入孵化區（weishi 之後）；
  往後改版仍要作者說「發布／上線」才動兩站。

## 5. 文件

- 本區 `README.md`：來源、指令、成品、限制（給下一個接手的人）。
- 母區 `docs/adb/`：對外說明頁（about）與索引；細節放本區。
- 新增或改名時，順手更新母區 `docs/README.md` 的索引。

## 6. 不要做的事

- 不要改母工作區的閱讀器程式（`ts/src/accelon26/*`）；共用 helper 的 bug 回母區修。
- 不要自寫漢字範圍、頁座標、VA 規則、缺字公式。
- 不要同時由兩個工作區重建同一個 adb。
- 不要把 `.adb`、`.zip` 等產物 commit 進 git；成品在 `D:\accelon3`。
- 不要在未經作者指示時發布官網 exe／改 `deploy/adb-status.json`。

## 7. 交接（工作區停用前）

- [ ] 最後一次建置指令可以從零重跑（來源、版本、參數）
- [ ] `adb-version-log.md` 有最後一列（sha／大小／buildTime／說明）
- [ ] `deploy/adb-notes.json` 的說明是最新的
- [ ] `README.md` 寫清楚「這個工作區已停用，維護看母區哪一份文件」
