# Google live read-only regression — 待執行核准

實作已完成離線驗證；**首輪止於 OAuth refresh，後續另行核准 OAuth-only 重新登入後，第二輪已完成三例；工具通過，但最終回答仍有語意缺陷**。pytest 只使用假的 HTTP／模型與受控資料。本套件不加入一般 CI 的 live 執行、不建立或修改活動、不改模型設定，不啟動 Judge 調校。PR #8 已合併為有已知生成缺陷的時間事實傳遞 checkpoint；本工作從該最新 main 另外開分支。

## 三個固定案例

沿用 `LIVE_CALENDAR_REVIEW.md` 已記錄的專用測試行事曆 fixture：2026-10-06 America/Los_Angeles 11:00–11:30（UTC-07:00）。歷史日期可用於 read-only 回歸，無須為每輪建立新活動。文件中的 fixture 不代表目前仍存在；查詢前必須驗證。

| ID | 查詢，2026-10-06 America/Los_Angeles | 事前條件與預期 |
| --- | --- | --- |
| live-overlap | 11:15–11:45，-07:00 | Busy；只回傳 fixture 的完整 11:00–11:30 區間 |
| live-adjacent | 11:30–12:00，-07:00 | Free；事件結束恰好等於查詢開始，不重疊 |
| live-empty | 12:00–12:30，-07:00 | Free；與 fixture 分開，且目前沒有其他忙碌活動 |

完整 prompts、新套件的預期參數／答案準則在 `calendar_live_readonly_cases.json`。既有 `calendar_cases.json`、Judge rubric 與所有 baseline 不變。若三例前提不符，停止，不修改 Calendar 來製造通過條件；缺 fixture 不算 agent 回歸失敗。

## 執行順序與呼叫預算

1. 本機確認案例格式、原 SUT 已載入 context 8192、輸出是全新私人目錄，才使用既有 OAuth connection。
2. Python adapter 直接讀取三個區間，檢查 availability 與完整 busy intervals。任一 API／解析錯誤或 fixture 不符，即停止，模型請求為零。
3. 三例各開一個真實 agent 對話；使用 `run_calendar_agent()` 與既有模型 client 設定。每例只允許一個符合原預期的已解析 Calendar 查詢；錯時間或額外查詢在傳到 Google 前阻擋，保留其嘗試參數與失敗。既有格式修正規則仍有效。
4. 將 agent 讀到的 availability／busy intervals 與直接查詢快照比較。發生差異時標記 `fixture_changed` 並停止，不把資料變動當成已證明的 agent 語意錯誤。

正常預期 **6 次 Google events 查詢＋6 次模型推論請求**。Google events HTTP 傳送嘗試與模型請求各自 **硬上限 12 次**：包含分頁、transport retry，以及 AuthorizedSession 因 401 認證重試而重新送出的 events 請求。多餘呼叫在送出前拒絕。計數代表傳送嘗試，不代表伺服器成功收到或處理。

OAuth refresh 由現有 Google auth transport 處理，可能另有認證網路請求，不計入 events 上限；summary 明示未獨立量測，不能把 events 數冒充所有 Google HTTP 流量。不新增 scope，不執行互動式重新授權，認證失敗就停止。Calendar session 的 transport 只放行固定 Calendar events endpoint 的 GET，拒絕其他 Calendar、端點、host 或寫入方法。

規劃預估 **3–10 分鐘，預留 15 分鐘**；是保守估計，不是量測或硬性總 timeout。舊五例 SUT 曾約 43 秒完成，但 live API、refresh、重試與硬體負載會增加耗時。既有模型單次 timeout 180 秒、Calendar 單次 30 秒，遇到長 timeout 總時間仍可能超過預留。此輪沒有 Judge、Calendar 寫入或失敗後補跑。

## Opt-in 與 OAuth 狀態

模組入口為 `harness.calendar_live_regression`。沒有 `--live-readonly` 時，必須在讀取案例／OAuth／模型前退出。執行還需要 Rachel 在聊天中確認本輪 Google／模型呼叫範圍；旗標本身不是人類授權的替代品。

既有 OAuth 三個檔案先前已確認存在；程式要求 `calendar.events.owned.readonly`，並拒用 primary。**未在聊天或報告查看／輸出憑證內容；首輪由 SDK 更新 OAuth 失敗；後續核准的 OAuth-only 重新登入成功，第二輪 fixture 前提已驗證**。執行核准後才由既有 `connect()` 使用憑證，必要時刷新；不得在日誌、repo 或摘要顯示憑證內容或 Calendar ID。不啟動 setup 的七日查詢或另外查 Calendar 列表。

核准後、確認模型與案例均未改動，從 repo 根目錄使用一個不存在的新目錄，例如：

```sh
.venv/bin/python -m harness.calendar_live_regression --live-readonly --private-dir reports/runs/live-readonly-session-001
```

**已執行兩次不同授權的嘗試：首輪 preflight 中止，第二輪使用全新私人目錄完成。範例第一輪目錄不得覆寫，也不是再次執行的授權。** 模型未載入或設定不符時停止，不自行載入／卸載或調整 context、Thinking、temperature、tokens。沿用原 SUT gpt-oss-20b；不以 Qwen 代跑。

## 三層結果不能混為一談

- **Python adapter／實際 Google**：保留實際 timeMin/timeMax、分頁／重試的 HTTP 傳送嘗試、status 與成功 200 的 projected response（只取 items／nextPageToken），以及 adapter 解讀後的結果。不保留 Authorization headers 或認證錯誤 body。
- **Agent 工具與參數**：原工具名稱、JSON arguments、解析後查詢與實際 HTTP 結果分開。沿用 strict structure grading；沒有成功查詢時不得靠文字 busy/free 判定通過。錯誤工具／時間範圍可能被阻擋而不碰 Google，此結果仍是工具行為失敗，不是假稱查過正確區間。
- **最終回答與 scope**：保存原文與 pending review，全文審閱 query／busy event、日期、offset、來源／轉換宣稱、語言與僅專用測試行事曆範圍。工具通過不等於回答通過，不以關鍵字或 Judge 分數自動放行。

保留資料變動、操作失敗、語意失敗與未嘗試案例的分母。三例讀取不是原子快照；相同 interval 的活動被替換可能無法辨識，因為既有 fields 不讀 event ID。本輪只比較 availability 與忙碌區間，不宣稱證明活動身份或沒有任何資料變動。

## 私人證據與公開摘要

只允許在 repo 的 ignored `reports/runs/` 下建立全新目錄，拒絕 baseline、覆寫既有目錄與 symlink 逃逸。目錄 0700，JSON 檔 0600：

- `raw.json`：私人的案例快照、實際 clock、Google 查詢／結果、agent 工具 trace、原始回答、pending review 與操作錯誤類型。
- `manifest.json`：來源 hashes、案例 hash、前後模型 runtime、wall time、上限與設定來源；沒有憑證內容。
- `summary.json`：嚴格 allowlist，只含固定匿名案例 ID、階段結果、呼叫數、wall time、implementation hash、資料變動指標及 review pending／未產生答案狀態；不含日期、時間、Calendar ID、URL、例外文字或原始回答。

stdout 也只印 allowlisted summary。執行後先人工檢查摘要，再決定是否將去識別摘要另存 repo；**不自動提交或上傳任何 live raw trace**。不要把一般 `reports/baseline/` 受控案例的提交慣例套到真實 Calendar 資料。

## 離線驗證與後續

`tests/test_calendar_live_regression.py` 使用受控 Calendar、假 HTTP transport 與 scripted model，涵蓋完整 CLI、opt-in、fixture 不符、API 失敗、錯／額外查詢阻擋、fixture drift、實際傳送與推論重試上限、私人資料 canary、檔案權限、模型未載入、中斷時保存部分結果，以及未嘗試／操作錯誤不冒充已評分失敗。一般 CI 只跑這些 deterministic tests，不帶憑證，也不會啟動 live suite。

先完成 branch → push → PR → required pytest CI；本輪實作與執行核准是分開的。請 Rachel 確認三例、6＋6 預期請求、各 12 次上限與時間預算後，才執行一次 live suite。合併仍需另外明確授權。Judge 維持 advisory，暫停新增調校實驗。

## 首輪已核准嘗試：授權前置中止

Rachel 已核准三例一輪與既定呼叫預算。SUT runtime 前置檢查通過，但既有 OAuth refresh 失敗，停止於 preflight；沒有 Google events 查詢，沒有模型推論，三例均未執行，fixture 尚未驗證。OAuth auth transport 的實際網路嘗試未獨立量測，不能宣稱所有 Google HTTP 流量為零。

只發布人工檢查過的 [去識別摘要](../reports/baseline/calendar-live-readonly-attempt-v1-summary.json)，原始本機紀錄／錯誤類型不提交。這是操作阻礙，不是三例 semantic FAIL。不重新登入、不修改／刪除憑證、不修改模型、不補跑。互動式 OAuth 重新授權仍需另外確認；既有 setup 入口還會查詢未來七日行程，不能把它當成已核准三例的一部分直接執行。PR 保持未合併。

## 第二輪：OAuth-only 恢復後完成三例

Rachel 另行核准只進行 OAuth 重新登入，成功後跑原三例。使用既有 read-only scope；由 SDK 開啟同意頁面，憑證有效後才以既有 owner-only atomic helper 替換，沒有執行 setup 的七日行程查詢，沒有 Calendar 寫入。認證內容與原始本機紀錄不提交。

[第二輪去識別摘要](../reports/baseline/calendar-live-readonly-attempt-v2-summary.json) 保留原始 allowlisted summary，沒有修補或改成 semantic PASS。三個 adapter 前提、三個 agent 工具結構、各自實際 HTTP 查詢參數與 Python 事實都符合預期；六次 events HTTP 傳送皆成功、六次模型推論皆首次成功，無重試，未觀測到 interval drift，前後 SUT runtime 相同。Runner wall time 41.826 秒，不含互動 OAuth 與人工審閱；OAuth 流量另計且未獨立量測。

Codex 輔助私人審閱發現：`live-overlap` 的 busy 結論與兩個區間數值正確，卻將部分重疊描述為完全包含。Python 根據同一份事件／query 起訖事實確認不是 full containment；因此這是一個已知 SUT 語意缺陷，不能用工具 PASS 抵銷。`live-adjacent` 與 `live-empty` 本輪未觀測到特定時間錯誤；前者正確使用中文回覆，但一輪不能證明語言或一般生成可靠性已修復。未修改原始回答、準則、agent 提示或模型設定，未呼叫 Judge、未追加調校／補跑。

三例 `answer_review` 仍 pending；上述是輔助分析，不是 Rachel 輸出簽核或整體通過率。此 PR 的價值是 live read-only regression 已可執行，且能保留生成失敗證據，而不是保證 SUT 全綠。建議以此 checkpoint 審閱；合併仍需 Rachel 明確授權，區間關係回答修正另案處理。私人 raw／manifest／輔助審閱留在 ignored 目錄，公開只保存去識別摘要與上述不含活動細節的分析。
