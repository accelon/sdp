# 官網文章的繁簡轉換（頁內嵌詞表）

> 2026-11-02 起，法華合注的所有頁面（`/fahua/`）都用這個做法；往後官網的文章照同一套。
> 這一頁是實作說明，規格的正本在 `agent-norms/writing-skill.md` §13。

## 1. 規則

- **繁體是母本**：HTML 用繁體寫、用繁體維護；簡體是執行時轉出來的，不另存一份檔案。
- 主站 `shutonggui.cn` 缺省簡體、鏡像 `nissaya.cn` 缺省繁體；**頂欄右側**一顆切換鈕，選擇記在 `localStorage`（`rut.sim`）。
- 只換字形與引號，**不改詞彙**（「數位」不變「数字」、「資料庫」不變「数据库」）。
- 程式碼、組字式、URL、`<code>`／`<pre>` 不轉。
- 金額一律人民幣（¥）。

## 2. 詞表從哪裡來

正本：`D:\2026\agent-norms\lossless-simplified\simplified-data.ts` 的 `SAFE_PAIRS`
（Unihan 的一對一繁→簡，2,641 對）。`build/zh_convert.py` 讀它，並且：

| 處理 | 例子 | 為什麼 |
|---|---|---|
| 排除 `著→着` | 著作 ≠ 着作 | §13.3 |
| `OVERRIDE` 改正罕見異體 | 線→线（Unihan 給「缐」）、託→托、綵→彩 | Unihan 的 kSimplifiedVariant 有幾個字給的是罕見寫法 |
| `EXTRA` 補一對多但安全的字 | 週→周、並→并、劃→划、麼→么、臺→台、於→于、佔→占 | SAFE_PAIRS 只收一對一，這些沒進來 |
| `KEEP` 不轉 | 阪（大阪）、憍（憍慢）、垵 | 轉了會壞地名／術語 |

## 3. 為什麼嵌整張表（而不是只抽本篇用到的字）

`agent-norms` §13.2 原本的建議是「只抽文章用到的字」，一頁約 800 bytes。
這裡改成**整張表內嵌**：

- 2,640 對、5,280 字、**15.8 KB**（gzip 後約 6 KB），對長文頁可以忽略。
- **改文章不必重建詞表**：詞表是常數，發布時只是把同一份字串嵌進去；不會出現「新加的字沒轉到」。
- 少一個「抽字」步驟，發布流程更短。

這是作者 2026-11-02 的指示；若日後要回到抽字版，只改 `zh_convert.py` 的 `safe_pairs()`。

## 4. 一頁是怎麼被處理的

`build/mk_site.py` 產頁時呼叫 `zh_convert.inject(html)`：

1. `<body>` 加 `style="visibility:hidden"`（避免先閃一下繁體）。
2. `</body>` 前插入 `<noscript>`（關 JS 時還原）與一段腳本：
   - `var P="繁簡繁簡…"`，載入時建 `M[繁]=簡`。
   - 走訪 `document.body` 的文字節點（跳過 SCRIPT／STYLE／CODE／PRE／TEXTAREA 與 `.mono`／`.ex-code`／`.urlbox`／`.no-sim`）。
   - `apply(sim)`：轉／還原文字、`document.title`、`<html lang>`、按鈕文字，以及 `[data-sim]` 的圖片／下載連結。
   - 判斷：`localStorage.rut.sim` → `?sim=1/0` → hostname（`shutonggui.cn` 簡體，其餘繁體）。
3. 頁面必須有 `<a id="simToggle">`；沒有就丟錯（避免悄悄漏掉切換鈕）。

圖片（長圖、封面）用：

```html
<img src="fahua-long-hant.jpg" data-sim="fahua-long.jpg" data-trad="fahua-long-hant.jpg" alt="…">
```

## 5. 新文章怎麼接（三步）

1. 寫繁體 HTML，頂欄放 `<a href="#" id="simToggle">简体</a>`（左邊放「← 法華合注」之類的回首頁）。
2. 產頁時呼叫：

   ```python
   import sys; sys.path.insert(0, r"D:\2026\sdp\build")
   from zh_convert import inject
   html = inject(html)
   ```

3. 用 headless 驗一次：主站網址要看到簡體、鏡像要看到繁體，console 0 error、390 px 不溢出。

## 6. 驗收

- [ ] `https://shutonggui.cn/…` 預設簡體、`https://nissaya.cn/…` 預設繁體
- [ ] 頂欄切換鈕有效，換頁後記得（`localStorage.rut.sim`）
- [ ] 關掉 JS 還看得到字（`<noscript>`）
- [ ] `<code>`、URL、書名原樣
- [ ] 390 px 不橫向溢出、console 0 error
- [ ] 金額是 ¥，沒有 NT$

## 7. 檔案

| 檔案 | 用途 |
|---|---|
| `build/zh_convert.py` | 讀 SAFE_PAIRS、組字串、注入頁面（唯一實作） |
| `build/mk_site.py` | 產四頁時呼叫 `inject()` |
| `build/deploy_fahua.mjs` | 上傳兩站、併孵化區清單、驗證 |
| `deploy/incubator.json` | 孵化區清單條目（交付用） |
