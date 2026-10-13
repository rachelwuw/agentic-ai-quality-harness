# Calendar 時區回答：五例真實 SUT 審閱 v1

五個已核准案例完成一輪真實 `openai/gpt-oss-20b` 評估。**工具結構 5/5、Python 時間事實 5/5；cal-03／cal-08 的指定舊問題本次未再出現，但整體回答仍有缺陷，不能宣稱五例語意全過。** 沒有 Judge 推論、Google 請求、事件寫入、補跑或調整提示後重跑。PR #8 保持未合併，結果待 Rachel 審閱。

## 授權、設定與時間

Rachel 先核准五例，接著授權由 agent 代為載入原 SUT。先前僅載入 Qwen 的阻礙已解除；這個後續授權允許載入，沒有改用 Qwen 代跑。載入既有 gpt-oss MXFP4，context 8192、完整 GPU offload，約 28.23 秒。Qwen 未卸載，沒有對它送出推論。

執行程式版本 `d505eb713cc32dcb6f1c4bd106013f07e567a809`。沿用既有 client：temperature 0、max_tokens 2048、timeout 180 秒、既有最多兩次 transport retries；未覆寫 reasoning 設定。Native metadata 保存初始與結束 runtime，兩者相同；其 reasoning capability default 不構成實際逐請求 reasoning 設定的獨立驗證。不能據此聲稱與歷史 runtime 的每個隱含設定完全相同。

| 組別 | 案例 | runner wall time |
| --- | --- | --- |
| 原始回歸 | cal-03、cal-08 | 14.432 秒 |
| 新題轉移 | tz-new-01、02、03 | 28.230 秒 |
| 合計 | 五例、10 次模型請求 | **42.662 秒**，不含載入、檢查與人工分析 |

事前 10–20 分鐘／預留 30 分鐘是保守規劃估計；實測顯著較快，不是將 Judge 延遲套用成 SUT 量測。既有 runner 不保存 token usage 或逐請求耗時，因此不報告 token 成本，也不把組別 wall time 當純生成時間。全部模型 transport 皆首次成功，無重試、參數修正或失敗後補跑。

## 分層結果

| 案例 | 工具／Python | 本次最終回答與剩餘問題 |
| --- | --- | --- |
| cal-03 | PASS／PASS | Free、日期與 LA 時間正確；不再誤稱太平洋標準時。回答省略 numeric offset，且中文問題仍用英文回答。這是未再觀測到舊錯誤，不代表已證明會正確使用 PDT。 |
| cal-08 | PASS／PASS | 正確區分台北 query 02:15–02:45、event 02:00–02:30，原始 10/06 11:00–11:30 -07:00 與跨日轉換分欄，舊「原始值稱為已轉換」問題未見。仍使用 PDT／CST，未遵循避免縮寫指示；數值和 fixture 的 PDT 正確、CST 由台北欄位消歧。沒有明確重申僅專用測試行事曆。 |
| tz-new-01 | PASS／PASS | 冬季 LA 09:00–09:30、UTC-08:00、free 正確；中文問題仍用英文回答。 |
| tz-new-02 | PASS／PASS | Honolulu query 08:10–08:40、正文 event 08:00–08:30 正確；但表格 Start 欄填整個區間，End 欄寫 **08:30–08:30 HST**，端點呈現混亂。還把未提供類型的事件稱為 meeting，未重申專用行事曆 scope。不能因正文正確而忽略表格缺陷。 |
| tz-new-03 | PASS／PASS | 原始 10/06 至 Auckland 10/07 +13:00 跨日、event 07:00–07:30 與 query 07:15–07:45 正確；卻自行補上來源 America/Los_Angeles。這與受控 fixture 相符，但工具只提供來源 -07:00，模型面前的證據沒有建立來源 IANA 地區；也未重申專用行事曆 scope。 |

**工具層**：五例各一次工具調用／一次受控 Calendar 請求；exact arguments、API interval、available 與完成狀態全部符合原預期。`api_calls` 是模擬記錄，不是真實 Google 呼叫。工具結構 PASS 不包含最終回答、語言、scope 或轉換表格品質。

**Python 層**：實際工具訊息中 query／busy interval 分開，原始事件保留；三個 busy 案例分別與事前台北、Honolulu、Auckland 起訖常數核對。冬季 -08:00、夏季 -07:00 與 +08/+13/-10 目標 offset 正確。兩個 free 案例沒有虛構 busy facts。離線測試已證明模型下一輪收到相同工具資料；這輪原始 trace 保存生成前的工具訊息內容。

**回答層**：上述是 Codex 輔助逐句證據審閱，不是 Rachel 的輸出簽核，也不是 LLM Judge 分數。cal-03／cal-08 舊特定錯誤未見，仍有語言、縮寫遵循、scope、來源推論及表格問題。沒有計算或宣稱總語意通過率。

## 原標籤保持不變

原始案例 JSON、expected calls／API interval、answer criteria、forbidden behaviors、舊 baseline、Judge rubric 與 client 均保持原檔；執行前後 hashes 一致。原始 runner 的 `answer_review.status` 仍為 pending，沒有用輔助分析覆寫它。

cal-08 四個原準則分開記錄：

1. Busy：符合。
2. 原始事件的日期、11:00–11:30 與 PDT 符合；表格未明寫 Los Angeles。是否足以滿足原條文的地區歸屬要求，標為 **NEEDS_REVIEW**，交由 Rachel 解讀；不自行放寬或宣稱該項通過。
3. 可選的 query-window-to-LA 轉換省略：符合原條文。
4. 台北原 query 保留：符合。

五例的既有準則與逐項輔助結果見 [assisted_review.json](calendar-timezone-sut-v1/assisted_review.json)。新題定義保留原先 not_run／pending 的模板狀態，實際授權和執行狀態以新 manifest／reports 為準。

## 證據與限制

- [原始兩例輸出](calendar-timezone-sut-v1/known.json)、[三個新例輸出](calendar-timezone-sut-v1/transfer.json)：與 ignored runs 原始檔 byte-for-byte 相同。
- [執行 manifest](calendar-timezone-sut-v1/execution_manifest.json)：程式與輸入 hashes、模型／runtime、各組起訖與 wall time、原始輸出 hashes。
- [輔助審閱](calendar-timezone-sut-v1/assisted_review.json)：工具、Python 與最終答案分開；不修補原輸出。
- [事前計畫](../../evals/CALENDAR_TIMEZONE_ANSWER_REVIEW_PLAN.md)、[保留的舊 baseline](calendar-baseline-v7-retry-20261007.json)。

這是一輪、同作者受控資料、歷史比較，非同時隨機 A/B、非獨立 benchmark，不證明因果、repeatability、一般可靠性、MCP 生成品質或真實 Google 整合。未用本輪結果調整程式／提示，也未改標籤或重跑。

建議先由 Rachel 審閱 cal-08 原準則的地區要求與 Honolulu 表格缺陷，再決定此 PR 是否以「時間事實傳遞改善、尚有生成缺陷」合併。若後續要處理呈現品質，另提小範圍方案與驗收案例；不在本輪未經核准反覆調提示跑到全綠。Judge 保持 advisory，merge 仍需另行授權。
