# Calendar 時區回答改善：SUT 執行前審閱

狀態：程式與 deterministic tests 已完成；**真實 SUT 評估尚未執行，等待 Rachel 核准下列五個案例與時間預算。** 無 Google 呼叫、無 Judge 模型呼叫。PR #7 仍為另一個未合併草稿，本分支來自 main `8c2e854`，沒有取用其 runner、案例、標籤或 rubric。

## 已確認問題與修正

舊 baseline `reports/baseline/calendar-baseline-v7-retry-20261007.json`：cal-03 工具正確使用 -07:00，但回答稱為太平洋標準時；cal-08 工具正確回傳原始 LA 事件，回答卻將它描述為已轉成台北。兩者原始 strict structure 都 PASS，並不代表最終回答正確。

`trace_facts.interval()` 已有可信任的 Python ZoneInfo 轉換，但原先只交給事後 Judge。新增 `with_availability_time_facts()` 重用該函式，讓 Python agent 與 MCP 在工具結果中提供：

- `time_facts.query_interval`：實際傳入 Calendar 的查詢區間。
- `time_facts.busy_intervals[busy_index].in_query_timezone`：整個忙碌事件在使用者時區的起訖日期與時間，ISO datetime 內含明確 UTC offset；沒有把事件裁成查詢範圍。
- 原始 `busy_intervals`、available、scope、source 保留。All-day、缺 offset 或不合法事件不猜測時刻，只標記轉換不可用。

Agent 提示明確區分 QUERY／ORIGINAL／CONVERTED，要求依事實呈現 IANA 時區與 numeric offset，避免自行使用 PST/PDT／標準時／夏令時。轉換事件須清楚標示原始與轉換值。Offset 本身不能證明來源 IANA 地區；來源沒有提供 region 時不得猜測。MCP 共用同一份事實與工具說明，但本次真實模型候選評估只涵蓋 Python agent，不宣稱 MCP 生成品質已驗證。

既有 `interval()`、`derive_trace_facts()` 行為、Judge rubric／預設、原始案例 expected labels 與舊 baseline 均未修改。

## 待核准的五個模型案例

| ID | 輸入與情境 | 工具／Python 預期 | 最終回答檢查 |
| --- | --- | --- | --- |
| cal-03 | 原題：2026-10-06 LA 11:30–12:00，緊鄰事件結束 | Free；查詢 UTC-07:00；沒有 busy event | 不得稱 PST／太平洋標準時；保留原日期、時間、scope |
| cal-08 | 原題：2026-10-07 台北 02:15–02:45 | Busy；原始事件 10/06 11:00–11:30 -07:00；轉換事件 10/07 02:00–02:30 +08:00 | 區分查詢與事件；不可聲稱已轉換卻仍只展示原始值 |
| tz-new-01 | 2027-01-18 LA 09:00–09:30，冬季空區間 | Free；查詢 -08:00；無事件 | 不得沿用夏季 offset 或編造衝突 |
| tz-new-02 | 2026-10-06 Honolulu 08:10–08:40 | Busy；整個事件為 Honolulu 08:00–08:30 -10:00 | 非台北目標；不可把 query 08:10–08:40 當事件 |
| tz-new-03 | 2026-10-07 Auckland 07:15–07:45 | Busy；事件由 LA 10/06 11:00–11:30 -07:00 轉為 Auckland 10/07 07:00–07:30 +13:00 | 正確跨日、目標 offset、原始與轉換歸屬 |

原題完整文字保留在 `calendar_cases.json`，三個新題的完整文字與預期在 `calendar_timezone_transfer_cases.json`。新題在本次實作完成後才撰寫，未用來調整提示，也未交給真實 SUT；只核對資料格式與 Python 事實。它們仍由同一開發者設計，不能稱獨立盲測或一般準確率證據。

**原標籤限制保留：** cal-08 原本第二條仍要求描述事件時使用原始 LA 時間；不會為了讓轉換後答案通過而改寫。審閱時同時保留原條文結果與額外的轉換事實檢查；若回答只展示轉換值而未滿足原條文，照實記錄，不以新檢查覆蓋既有標籤。

## 時間預估與執行範圍

五個全新對話，一輪；通常每題一次工具請求加一次最終回答，約 **10 次模型請求，預估 10–20 分鐘，預留 30 分鐘**。這是規劃估計，不是此次量測：舊 SUT baseline 未保存逐請求耗時；工具修正、既有 transport retry、硬體負載與 runtime 都可能增加時間。既有 LocalClient 單次 timeout 180 秒與重試規則不變，不保證 30 分鐘內完成。

沿用既有 SUT `openai/gpt-oss-20b` 與原有 runtime／模型設定。執行前先確認實際設定；不自行載入／卸載模型或調整 context、Thinking、tokens。若目前只有 Qwen Judge 載入或設定不符，先回報阻礙，不能換模型代跑。此輪使用 ControlledCalendar，**不呼叫真實 Google API**，也不執行 Judge 推論。未另行核准不補跑、調參後重跑或擴成全套。

核准後使用既有 runner，分別保存兩份新檔，執行前確認不存在，禁止覆寫舊檔：

```sh
.venv/bin/python -m harness.calendar_evaluate --ids cal-03 cal-08 --output reports/runs/calendar-timezone-sut-known-v1.json
.venv/bin/python -m harness.calendar_evaluate --cases evals/calendar_timezone_transfer_cases.json --output reports/runs/calendar-timezone-sut-transfer-v1.json
```

保存 code／cases hashes、模型與 runtime 觀測值、每組 wall time、工具與重試紀錄、原始回答；若未完成，保留 partial report 並回報。受控工具資料可整理成新 baseline，原始舊報告不改寫。

## 驗證分層與驗收

1. **工具執行：** 沿用原 exact arguments、API interval、available、scope 檢查；原 strict 結果照存。首輪成功、修正恢復、讀取失敗分開報告。
2. **Python 計算：** 依 offset／ZoneInfo 核對 query 與整個 busy event，原始值保留、轉換正確、事實確實傳進模型工具訊息。這層可用離線測試證明，不代表回答正確。
3. **最終回答：** 全文核對日期、clock、IANA／offset、來源與轉換宣稱、查詢／事件區別、scope；不得僅以 busy/free 或關鍵字評分。保留所有失敗，不要求全綠。Judge 維持 advisory；本次不修改 rubric，也不以 Judge 分數代替人工審閱。

cal-03／cal-08 的已知文字錯誤須不再出現，新題不得出現錯誤轉換或區間混淆，才有初步生成品質改善證據。一輪結果仍不足以證明重複性或普遍可靠。模型結果、成本與 merge 授權另行回報；CI 綠燈只代表 deterministic checks 通過。

已保存的 [離線工具／Python 證據](../reports/baseline/calendar-timezone-facts-offline-v1.json) 沒有模型答案；不得當作 SUT 評估通過。
