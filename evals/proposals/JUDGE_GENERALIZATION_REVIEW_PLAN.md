# Judge 新案例推廣驗證 — 審閱草稿

**狀態：僅設計，尚未執行模型。** 八份答案及預期標籤由 Codex 撰寫，待 Rachel 審閱；不是獨立 benchmark，也不是新的 SUT 回答。

PR #6 已合併為研究 checkpoint；PR #4、#5 關閉但分支與原始證據保留。預設 v10 不變。

## 要驗證的問題

單項格式在這八個新答案上，是否比九項批次格式更能遵守 c6（轉換時區歸屬）與 c7（轉換日期／時間數值）的邊界？不推論其他準則或完整答案準確率。

沿用 #6 所用的修正版準則原文。所有案例的九項文字均相同，沒有加入日期特例或結果導向修改。此研究不修改 Python 事實、system prompt 或正式評分模式。

## 案例與擬議標籤

| 案例 | 主要特徵 | c6 | c7 | 完整九項預期 |
| --- | --- | --- | --- | --- |
| P1 | 保留原始 LA 時間、無轉換宣稱 | PASS | PASS | PASS |
| P2 | 明確而正確的冬季轉換 | PASS | PASS | PASS |
| P3 | 正確的隱含轉換表達 | PASS | PASS | PASS |
| P4 | 來源跨午夜、資訊順序改變、轉換正確 | PASS | PASS | PASS |
| N1 | 轉換數值正確，目標標籤錯誤 | FAIL | PASS | FAIL |
| N2 | 隱含轉換，台北日期少一天 | PASS | FAIL | FAIL |
| N3 | 時區標籤與數值都錯 | FAIL | FAIL | FAIL |
| N4 | 正確開頭、後段隱含重述矛盾 | PASS | FAIL | FAIL |

P1–P4 九項皆擬議 PASS；N1–N4 的 c2 皆 FAIL，另有上表 c6/c7 的 FAIL。其他準則擬議 PASS。全體有 16 個目標準則標籤，其中 11 PASS、5 FAIL。這些仍是草稿，沒有 human sign-off。

**需明確審閱 N2：**「In Taipei local time」視為事件轉換表達，即使沒有 converted 字樣；錯誤日期因此應使 c7 FAIL。P3 同樣表達正確的隱含轉換。此解讀及 N1 的 c7 PASS 分配須在執行前核准，不能看結果後改標籤。

以下為完整模型候選答案；只把這些固定答案與工具證據送入 Judge，不生成新 SUT 回覆。

### P1

**使用者輸入：** Check 2029-07-09 09:50–10:20 Asia/Taipei on the dedicated test calendar.

**工具記錄的衝突事件：** `2029-07-08T18:40:00-07:00` 至 `2029-07-08T19:10:00-07:00`。

**Python 台北事實：** `2029-07-09T09:40:00+08:00` 至 `2029-07-09T10:10:00+08:00`；與查詢區間重疊，available=false。

```text
The dedicated test calendar has a conflict overlapping 2029-07-09 09:50–10:20 Asia/Taipei, so that requested slot is busy. The recorded event runs from 2029-07-08 18:40 to 19:10 America/Los_Angeles. This result covers the test calendar only.
```

### P2

**使用者輸入：** Check 2029-02-03 22:30–23:00 Asia/Taipei on the dedicated test calendar.

**工具記錄的衝突事件：** `2029-02-03T06:20:00-08:00` 至 `2029-02-03T06:50:00-08:00`。

**Python 台北事實：** `2029-02-03T22:20:00+08:00` 至 `2029-02-03T22:50:00+08:00`；與查詢區間重疊，available=false。

```text
Your requested test-calendar interval, 2029-02-03 22:30–23:00 Asia/Taipei, overlaps an event and is unavailable. After conversion to Asia/Taipei, that event runs on 2029-02-03 from 22:20 to 22:50. Only the dedicated test calendar was queried.
```

### P3

**使用者輸入：** Check 2029-08-12 15:20–15:50 Asia/Taipei on the dedicated test calendar.

**工具記錄的衝突事件：** `2029-08-12T00:10:00-07:00` 至 `2029-08-12T00:40:00-07:00`。

**Python 台北事實：** `2029-08-12T15:10:00+08:00` 至 `2029-08-12T15:40:00+08:00`；與查詢區間重疊，available=false。

```text
There is an overlapping event on the dedicated test calendar, so 2029-08-12 15:20–15:50 Asia/Taipei is busy. In Taipei local time, the conflicting event runs on 2029-08-12 from 15:10 to 15:40. Other calendars are outside this check.
```

### P4

**使用者輸入：** Check 2029-12-16 16:00–16:30 Asia/Taipei on the dedicated test calendar.

**工具記錄的衝突事件：** `2029-12-15T23:50:00-08:00` 至 `2029-12-16T00:20:00-08:00`。

**Python 台北事實：** `2029-12-16T15:50:00+08:00` 至 `2029-12-16T16:20:00+08:00`；與查詢區間重疊，available=false。

```text
The conflicting event starts at 2029-12-15 23:50 America/Los_Angeles and ends at 2029-12-16 00:20 America/Los_Angeles. Converted to Asia/Taipei, its interval is 2029-12-16 15:50–16:20. It overlaps your requested 2029-12-16 16:00–16:30 Asia/Taipei slot, which is busy on the dedicated test calendar. This check covers that calendar only.
```

### N1

**使用者輸入：** Check 2029-02-03 22:30–23:00 Asia/Taipei on the dedicated test calendar.

**工具記錄的衝突事件：** `2029-02-03T06:20:00-08:00` 至 `2029-02-03T06:50:00-08:00`。

**Python 台北事實：** `2029-02-03T22:20:00+08:00` 至 `2029-02-03T22:50:00+08:00`；與查詢區間重疊，available=false。

```text
Your requested test-calendar interval, 2029-02-03 22:30–23:00 Asia/Taipei, overlaps an event and is unavailable. After conversion to Asia/Taipei, that event runs on 2029-02-03 from 22:20 to 22:50 America/Los_Angeles. Only the dedicated test calendar was queried.
```

### N2

**使用者輸入：** Check 2029-12-16 16:00–16:30 Asia/Taipei on the dedicated test calendar.

**工具記錄的衝突事件：** `2029-12-15T23:50:00-08:00` 至 `2029-12-16T00:20:00-08:00`。

**Python 台北事實：** `2029-12-16T15:50:00+08:00` 至 `2029-12-16T16:20:00+08:00`；與查詢區間重疊，available=false。

```text
The dedicated test calendar contains an event overlapping your requested 2029-12-16 16:00–16:30 Asia/Taipei slot, so it is busy. In Taipei local time, the conflicting event runs on 2029-12-15 from 15:50 to 16:20. This check covers that calendar only.
```

### N3

**使用者輸入：** Check 2029-08-12 15:20–15:50 Asia/Taipei on the dedicated test calendar.

**工具記錄的衝突事件：** `2029-08-12T00:10:00-07:00` 至 `2029-08-12T00:40:00-07:00`。

**Python 台北事實：** `2029-08-12T15:10:00+08:00` 至 `2029-08-12T15:40:00+08:00`；與查詢區間重疊，available=false。

```text
There is an overlapping event on the dedicated test calendar, so 2029-08-12 15:20–15:50 Asia/Taipei is busy. Converted to Asia/Taipei, the conflicting event runs on 2029-08-12 from 14:10 to 14:40 America/Los_Angeles. Other calendars are outside this check.
```

### N4

**使用者輸入：** Check 2029-07-09 09:50–10:20 Asia/Taipei on the dedicated test calendar.

**工具記錄的衝突事件：** `2029-07-08T18:40:00-07:00` 至 `2029-07-08T19:10:00-07:00`。

**Python 台北事實：** `2029-07-09T09:40:00+08:00` 至 `2029-07-09T10:10:00+08:00`；與查詢區間重疊，available=false。

```text
The dedicated test calendar has a conflict overlapping 2029-07-09 09:50–10:20 Asia/Taipei, so that requested slot is busy. Converted to Asia/Taipei, the event runs on 2029-07-09 from 09:40 to 10:10. In Taipei local time, that same event is also 2029-07-09 10:40–11:10. This result covers the test calendar only.
```

## 執行設計：待另行核准

- 一輪共 24 個單次請求：八個答案各有一次九項批次、一次 c6 單項、一次 c7 單項。
- 各案例交錯格式順序：依固定順序 P1/P2/P3/P4/N1/N2/N3/N4，輪替 batch→c6→c7、c6→c7→batch、c7→batch→c6。事先固定、不依結果改變；非隨機化且只跑一輪。
- 兩格式使用相同答案、工具記錄、Python 事實、準則原文與模型設定。既有 runner 的單項輸出仍會重新編號 c1；保留原 c6/c7 對應。count/context/schema/ID 一起改變，不單獨歸因於項目數。
- Qwen Q8_0、context 8192、Thinking on、勾選 budget 1024、temperature 0、strict JSON、max output 6144、timeout 600。執行前重新核對實際 runtime，保存觀測值與 hashes。
- 不重試、不更換錯誤輸出、不在途中修改準則／標籤；runtime 阻礙即停止並回報。Google API 和 SUT 生成皆不在範圍內。
- 只比較兩格式共同的 16 個 c6/c7 判定；其餘批次準則保留作證據，不納入目標準確率分母。輸入、輸出、傳輸錯誤與有效語意 UNCERTAIN 分開報告。
- 已見過的 #6 四項作既有開發回歸證據，不混入這輪新案例成績。

## 擬議驗收標準

此標準只決定是否值得繼續驗證單項候選模式，不批准部署或改預設。

1. 24 次皆有有效輸出、兩格式各有完整 16 個目標判定；缺失時報告 planned/available 分母，結論標為不完整，不補跑。
2. 單項至少修正兩個批次目標錯誤，且沒有新增目標錯誤。有效 UNCERTAIN 不算正確。
3. 單項的四份正確答案共八個目標判定全部 PASS；五個預期 FAIL 目標全部 FAIL。
4. 人工檢查全部目標理由／evidence；不得有未解決的明確理由–標籤矛盾，或靠錯誤理由得到相符標籤。特別檢查 implicit-conversion 是否被誤當無宣稱。
5. 報告兩格式總時間、每個答案成本、token usage、操作錯誤與語意錯誤；品質達標後，由 Rachel 決定成本是否可接受，沒有預設成本簽核。

若批次已全部判對，結果是沒有改善空間／推廣證據不足，不代表單項失敗。即使達標，也不是一般準確率或發布簽核；還需依實際風險擴大驗證。

## 授權與後續

目前只授權準備可審閱設計。完整答案、參考事實、逐準則標籤、驗收標準仍待 Rachel 確認；24 次模型執行需另外明確核准。沒有啟用新模式或新增自動模型 CI。

來源：[候選輸入 JSON](judge_generalization_cases_draft.json)、[候選標籤 JSON](judge_generalization_labels_draft.json)、[已合併的診斷方法](../JUDGE_SINGLE_BOUNDARY_DIAGNOSTIC.md)。
