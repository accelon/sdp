# sdp 建置步驟

> 這一區做兩件事：**① 法華合注的教學文件包**（法師版、護持版、落地頁、實測頁；已上線）
> 與 **② `sdp.adb`**（離線閱讀器；作者 2026-11-02 指示不必做，暫停）。
>
> 文件包用的實測數字，也正是未來 adb 的資料模型；兩者共用 `src/measure.py` 與
> `docs/measure.md`。

## 0. 這一輪（2026-11-02）做了什麼

```text
① 量測    CBETA 2026.R2 → 主文三譯、注疏 26 家 → out/measure.json
② 文件    法師版（法華-教學評估.html）、護持版、落地頁（deploy/fahua/src/）
③ 繁簡    繁體母本 → 頁內嵌詞表（build/zh_convert.py）；不另存簡體檔
④ 圖      長圖 900×3036、封面 1200×630（build/long-hant.html、build/cover-hant.html）
⑤ 檢查    390／1200 截圖、console 0 error、無橫向溢出
⑥ 上架    build/deploy_fahua.mjs → 兩站 /fahua/ ＋孵化區（weishi 之後）
```

成品：

| 路徑 | 說明 |
|---|---|
| `法華-教學評估.html` | 法師版母本（繁中，可離線、可印 A4） |
| `deploy/fahua/` | 上架包：index／teacher／donor／measure 四頁＋長圖、封面 |
| `deploy/fahua/src/` | 落地頁、護持版的**繁體源檔**；產出的 `index.html`、`donor.html` 不要手改 |
| `deploy/incubator.json` | 孵化區清單條目（已併進兩站 `projects.json`） |
| `docs/measure.md` | 實測方法、數字、限制（報告的每一個百分點都在這裡） |
| `docs/sources.md` | 來源、授權、下載位置 |
| `docs/zh-convert.md` | 頁內嵌繁簡詞表的做法（官網文章的統一標準） |
| `out/` | 中間產物（截圖、measure.json），不進版控 |

線上：

- <https://shutonggui.cn/fahua/>（主站，缺省簡體）
- <https://nissaya.cn/fahua/>（鏡像，缺省繁體）
- 孵化區：<https://shutonggui.cn/incubator/>（法華合注排在唯識合注之下）

## 1. 從零重跑

```powershell
cd D:\2026\sdp

# 0) 只有重做長圖／封面才需要 OpenCC（純 Python，裝在工作區內）
python -m pip install --target out\pylibs opencc-python-reimplemented

# 1) 量測（需要母區的 CBETA 語料，見下）
python src\measure.py                 # → out\measure.json、out\measure.txt

# 2) 產頁（繁中母本 → 四頁；每頁內嵌繁簡詞表）
python build\mk_site.py

# 3) 長圖與封面（需要 Edge 以 CDP 啟動）
python build\mk_images.py
start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" `
  --headless=new --disable-gpu --remote-debugging-port=9337 `
  --user-data-dir=out\edge-profile about:blank
node build\shot.mjs "file:///D:/2026/sdp/build/long-hant.html"  "out\shot\long-hant.png"  900 1
node build\shot.mjs "file:///D:/2026/sdp/build/long-s.html"     "out\shot\long-s.png"     900 1
node build\shot.mjs "file:///D:/2026/sdp/build/cover-hant.html" "out\shot\cover-hant.png" 1200 1
node build\shot.mjs "file:///D:/2026/sdp/build/cover-s.html"    "out\shot\cover-s.png"    1200 1
# 再依 docs\zh-convert.md 的說明轉 JPG（PIL，q78；長圖 <220 KB、封面 <40 KB）

# 4) 上架（先 --check 看連線與權限）
node build\deploy_fahua.mjs --check
node build\deploy_fahua.mjs
```

語料（唯讀，不在本區）：

```text
D:\2026\adb-converter\build\tei-all-2026R2.txt    大正藏（377 MB）
D:\2026\adb-converter\build\wxzj-tei-2026R2.txt   卍續藏（261 MB）
```

## 2. 繁簡（官網統一做法）

- 繁體母本；簡體由**頁內嵌詞表**在瀏覽器轉（`build/zh_convert.py`）。
- 主站缺省簡體、鏡像缺省繁體；頂欄 `#simToggle` 切換，記在 `localStorage.rut.sim`。
- 詞表是常數（`agent-norms` 的 `SAFE_PAIRS`，2,640 對、15.8 KB）；**改文章不必重建詞表**。
- 圖片用 `data-sim`／`data-trad` 跟著切換；`<code>`、URL 不轉。
- 新文章的接法、驗收清單：`docs/zh-convert.md`。

## 3. `sdp.adb`（暫停）

作者 2026-11-02 指示不做；若日後重啟，規則如下：

- 底本：CBETA 大正藏 T0262（羅什），別譯 T0263、T0264。
- 頁 id：暫定沿用大正藏頁碼 `9p1a`；梵本另用 `sa-<寫本>-<頁>`。
- 資料模型：「句→品→詞」三層（見 `docs/measure.md` §3）。

## 4. 待辦

- [x] 底本與來源（CBETA 2026.R2；T0262 主文＋T0263／T0264 別譯＋26 家注疏）
- [x] 實測與文件包（法師版、護持版、落地頁、實測頁）
- [x] 繁簡：頁內嵌詞表（不再產簡體檔）
- [x] 上架兩站／孵化區（weishi 之後）
- [ ] 把 `docs/zh-convert.md` 的做法推廣到官網其他文章
- [ ] （暫停）`sdp.adb`
