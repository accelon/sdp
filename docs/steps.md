# sdp 建置步驟

> 2026-11-02 起，這一區同時做兩件事：
> **① 法華合注的教學文件包**（法師版、護持版、落地頁、長圖；本輪完成）
> **② `sdp.adb`**（離線閱讀器；下一輪）
>
> 文件包先做，是因為它要用的「實測數字」正是 adb 的資料模型；
> 兩者共用同一份 `src/measure.py` 與 `docs/measure.md`。

## 0. 這一輪（2026-11-02）做了什麼

```text
① 量測    CBETA 2026.R2 → 主文三譯、注疏 26 家 → out/measure.json
② 文件    法師版（法華-教學評估.html）、護持版、落地頁（deploy/fahua/src/）
③ 繁簡    繁體母本 → OpenCC t2s 無損轉出（build/mk_site.py）
④ 圖      長圖 900×3036、封面 1200×630（build/long-hant.html、build/cover-hant.html）
⑤ 檢查    390／900／1200 截圖、console 0 error、無橫向溢出
⑥ 未做    官網部署、孵化區清單（作者指示「先不放孵化區」）
```

成品：

| 路徑 | 說明 |
|---|---|
| `法華-教學評估.html` | 法師版母本（繁中，可離線、可印 A4） |
| `deploy/fahua/` | 上架包：六頁（index／teacher／donor × 繁簡）＋ measure 頁＋長圖＋封面 |
| `deploy/fahua/src/` | 落地頁、護持版的**繁體源檔**；`index.html`、`donor.html` 由它轉出，不要手改 |
| `docs/measure.md` | 實測方法、數字、限制（報告的每一個百分點都在這裡） |
| `docs/sources.md` | 來源、授權、下載位置 |
| `out/` | 中間產物（截圖、measure.json），不進版控 |

## 1. 從零重跑

```powershell
cd D:\2026\sdp

# 0) 依賴（只做一次）：OpenCC 純 Python 版，裝在工作區內
python -m pip install --target out\pylibs opencc-python-reimplemented

# 1) 量測（需要母區的 CBETA 語料，見下）
python src\measure.py                 # → out\measure.json、out\measure.txt

# 2) 產頁（繁中母本 → 繁／簡六頁 ＋ measure 頁）
python build\mk_site.py

# 3) 長圖與封面（需要 Edge 以 CDP 啟動）
python build\mk_images.py             # → build\long-s.html、build\cover-s.html
start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" `
  --headless=new --disable-gpu --remote-debugging-port=9337 `
  --user-data-dir=out\edge-profile about:blank
node build\shot.mjs "file:///D:/2026/sdp/build/long-hant.html"  "out\shot\long-hant.png"  900 1
node build\shot.mjs "file:///D:/2026/sdp/build/long-s.html"     "out\shot\long-s.png"     900 1
node build\shot.mjs "file:///D:/2026/sdp/build/cover-hant.html" "out\shot\cover-hant.png" 1200 1
node build\shot.mjs "file:///D:/2026/sdp/build/cover-s.html"    "out\shot\cover-s.png"    1200 1
# 再依 docs\sources.md 的說明轉 JPG（PIL，q78；長圖 <220 KB、封面 <40 KB）
```

語料（唯讀，不在本區）：

```text
D:\2026\adb-converter\build\tei-all-2026R2.txt    大正藏（377 MB）
D:\2026\adb-converter\build\wxzj-tei-2026R2.txt   卍續藏（261 MB）
```

## 2. 文字與頁 id（`sdp.adb`，下一輪）

- 底本：CBETA 大正藏 T0262（羅什），別譯 T0263、T0264。
- 頁 id：**暫定沿用大正藏頁碼 `9p1a`**（`<冊>p<頁><欄>`），因為三譯與注疏都回查同一套頁碼；
  若 adb 要放梵本對讀，梵本另用 `sa-<寫本>-<頁>`，不要混進 `9p..`。
- 卷／品：`<卷>`、`<品>` 標籤；`t=`／`s=` 宣告照母區慣例。
- VA：以漢字為單位；梵文、藏文用 PUA（見母區 `missing-char.md`），不要自己寫規則。

## 3. `sdp.adb` 的建置流程（暫定）

```text
① 取源（TEI XML → 文字；或直接用母區的 tei-all 轉出的頁文字）
② 轉文字（一行一個 lb；超過 4,000 字要切）
③ 補資料（缺字、術語、頁碼、品名；外部檔，不改原始檔）
④ 連結（<聯> 到 SDP／CBETA；j 最後跑）
⑤ 打包（母區 ts/src/adbauthor.ts 的 authorAdb）
⑥ 驗證＋記帳（母區 adb-version-log.md、deploy/adb-notes.json）
```

- 搜尋：法華正文有 tokenizer 可用（漢字），不必 `--no-index`。
- 梵漢：`<术 sk="…">` 只標有把握的詞；詞表用 KKJ／KDR（CC BY-SA 3.0），
  產生的 `glossary` 容器也要以 CC BY-SA 釋出。

## 4. 待辦

- [x] 底本與來源（CBETA 2026.R2；T0262 主文＋T0263／T0264 別譯＋26 家注疏）
- [x] 實測與文件包（法師版、護持版、落地頁、長圖、封面）
- [x] 繁簡六頁與檢查（390／900／1200 截圖）
- [ ] 官網部署（作者指示前不做；孵化區先不放）
- [ ] `sdp.adb` 第一版：T0262 × 三部夾註 × 28 品（句／品兩層）
- [ ] 梵漢層：KKJ 2,409 條接入 `<术>` 與 `glossary`
- [ ] 母區記帳（`adb-version-log.md`、`adb-notes.json`）
