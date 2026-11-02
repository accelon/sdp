# 法華合注 · 來源與授權

> 這一頁記「資料從哪裡來、能不能用、要不要標」。數字與方法的細節見 `measure.md`；
> 建置步驟見 `steps.md`。

## 1. 一次看

| 類別 | 來源 | 授權 | 狀態 |
|---|---|---|---|
| 主文 T0262 妙法蓮華經 | CBETA 2026.R2（大正藏 T09 No.262） | CBETA 授權，非營利使用；引用須標 | 已用（實測） |
| 別譯 T0263 正法華經 | 同上（T09 No.263） | 同上 | 已用（實測） |
| 別譯 T0264 添品妙法蓮華經 | 同上（T09 No.264） | 同上 | 已用（實測） |
| 注疏 15 部 | 大正藏 T09（T1519、T1520、T1715–T1725、T1817、T1818 等） | 同上 | 已用（實測） |
| 注疏 11 家／13 部 | 卍續藏 X27–X34（法華部） | 同上 | 已用（實測） |
| 辛嶋靜志《妙法蓮華經詞典》KKJ | DILA Glossaries（2001 原書數位化） | **CC BY-SA 3.0** | 已下載、已統計 |
| 辛嶋靜志《正法華經詞典》KDR | 同上（1998 原書數位化） | **CC BY-SA 3.0** | 已下載、已統計 |
| DILA SDP 法華經數位資料庫 | <https://sdp.dila.edu.tw/> | **CC BY-SA 4.0**（網站宣告） | 只連結、未複製 |
| 梵本（Kern-Nanjio、Toda 校訂、旅順殘片） | 見 SDP「梵本法華經」頁 | 原書多為公有領域；校訂本另計 | 未使用，只引用 |

## 2. 下載位置（不進版控）

`data/external/` 已被 `.gitignore` 忽略；換機器時重下：

```text
https://glossaries.dila.edu.tw/data/kumarajiva.dila.tei.p5.xml.zip     # 647,191 bytes
https://glossaries.dila.edu.tw/data/dharmaraksa.dila.tei.p5.xml.zip    # 853,160 bytes
```

解壓後：

```text
data/external/kkj/kumarajiva.dila.tei.p5.xml     2,409 條、31,733 引文
data/external/kdr/dharmaraksa.dila.tei.p5.xml    3,356 條、45,649 引文
```

統計方式（`<entry>`、`<cit>` 計數）寫在 `measure.md` §4。

## 3. 使用時要標什麼

- **CBETA**：頁腳與關於頁寫「資料來源：CBETA 大正藏／卍續藏（2026.R2），
  中華電子佛典協會授權非營利使用」；引用時附大正藏／卍續藏頁碼。
- **辛嶋詞典**：CC BY-SA 3.0 → 姓名標示（辛嶋靜志、DILA 數位化）、
  相同方式分享；若把詞條資料併入資料庫，整個資料庫要以 CC BY-SA 釋出。
- **SDP**：CC BY-SA 4.0；在合作之前只做連結與引用，不整批複製對讀資料。
  若日後接入，要標「法鼓文理學院 SDP」並以相同方式分享。

## 4. 不要做

- 不要把 SDP 的對讀資料整批爬下來放進 repo（即使授權允許，也要先談合作）。
- 不要把 DILA 的教學講義、法師稿件當成可自由使用的素材。
- 不要把 CBETA 文本當成公有領域；它是有條件授權。

## 5. 數字的出處

| 數字 | 出處 |
|---|---|
| 72,550 字、2,848 句、28 品、7 卷 | `src/measure.py` → `out/measure.json` |
| 26 家、28 部、5,469,480 字 | 同上（注疏清單見 `src/measure.py` 的 `COMMENTARIES`／`X_COMMENTARIES`） |
| 89%／88.5%／84.4%（夾註） | 同上（按品分段、8 字窗、允許斷點） |
| 5,765 條、77,382 引文 | KKJ＋KDR 的 `<entry>`／`<cit>` 計數 |
| 60h→14h、4.2×、¥18.2 萬／¥10.0 萬 | 模型估算，假設見法師版報告 §5 與附註 |
