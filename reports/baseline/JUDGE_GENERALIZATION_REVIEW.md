# 新案例推廣驗證：單項尚未達標

24 次核准的本機 Qwen 請求已完成，全部輸出有效、無重試。共同的 16 個 c6/c7 目標中，批次符合核准標籤 13/16，單項 14/16。單項只修正 N4/c6，零新增退步；未達事前「至少修正兩項」門檻，理由審查也未通過。**維持 advisory Judge 與預設 v10，不啟用單項正式模式。**

Rachel 的核准涵蓋執行前的八份完整答案、工具事實、逐準則標籤、隱含轉換解讀及 24 次執行，不涵蓋本次輸出、成本、發布或 PR 合併。以下是 Codex 輔助證據分析，待 Rachel 審閱，不是獨立人工 benchmark。

## 結果與驗收

| 事前門檻 | 本次證據 | 結果 |
| --- | --- | --- |
| 24 次有效、各完整 16 個目標 | 24/24 有效；batch 16/16 available，single 16/16 available | 通過 |
| 至少兩項改善、零新增退步 | 改善 1：N4/c6；新增退步 0 | **未通過** |
| 四個正例八項全 PASS；五個預期 FAIL 全 FAIL | 單項均符合 | 通過；不表示其餘 PASS 目標全對 |
| 全部目標理由／evidence 正確遵守準則 | 已逐項檢查 32 個；批次 4、單項 2 個理由違反範圍／目標規則 | **未通過** |
| 成本另行審閱 | 時間／tokens 完整保存；尚未由 Rachel 接受 | 待審閱 |

| 案例 | 預期 c6/c7 | 批次 c6/c7 | 單項 c6/c7 |
| --- | --- | --- | --- |
| P1 | PASS/PASS | PASS/PASS | PASS/PASS |
| P2 | PASS/PASS | PASS/PASS | PASS/PASS |
| P3 | PASS/PASS | PASS/PASS | PASS/PASS |
| P4 | PASS/PASS | PASS/PASS | PASS/PASS |
| N1 | FAIL/PASS | FAIL/FAIL | FAIL/FAIL |
| N2 | PASS/FAIL | FAIL/FAIL | FAIL/FAIL |
| N3 | FAIL/FAIL | FAIL/FAIL | FAIL/FAIL |
| N4 | PASS/FAIL | FAIL/FAIL | PASS/FAIL |

批次 false FAIL 3、單項 false FAIL 2；兩者皆沒有觀測到目標 false PASS 或有效語意 UNCERTAIN。這只描述本次 11 PASS／5 FAIL 的目標組成，不能推論一般 false-positive/negative 率。輸入、輸出、傳輸錯誤皆為 0。批次其他準則保留於原始報告，不納入共同目標分母；沒有用批次的 72 項對比單項的 16 項。

## 最大限制：仍有 c6/c7 邊界混淆

- **N1/c7，兩格式皆 false FAIL：** 宣稱轉成台北，顯示數值 22:20–22:50 正確，但附上 LA 標籤。核准規則要求 c6 FAIL、c7 PASS；兩者仍把標籤錯誤算到數值準則。單項還說「incorrect clock values」，但引用的 Python 時刻與答案相同。
- **N2/c6，兩格式皆 false FAIL：**「In Taipei local time」清楚歸屬台北，只是日期少一天，應由 c7 FAIL。批次明確把 c7 數值要求混入 c6；單項承認不能評數值，仍因日期而 FAIL。這說明單項也會忽略明確的準則邊界。
- **N3/c7，判定符合但批次理由錯：** 批次以 LA 的 00:10–00:40 作比較目標，忽略宣稱目標台北。單項使用台北 15:10–15:40，理由較好；兩者標籤同為 FAIL，不能算配對標籤改善。
- **N4/c6，唯一標籤改善：** 批次把後段數值矛盾算成時區歸屬 FAIL。單項正確辨識兩段皆歸屬台北而 PASS；c7 兩者均抓到後段 10:40–11:10 與事實 09:40–10:10 的矛盾。

P3、N2 的隱含轉換均有被辨識，並非只檢查 converted 關鍵字。未觀測到「PASS 的理由明確指出該準則違反卻仍 PASS」的直接矛盾；但範圍違反、數值錯誤的無效論據，以及 N3 的「標籤符合、理由錯」仍使理由門檻失敗。P2 單項 c6 額外提及正確數值；N4 單項 c7 開頭使用不佳的 but 轉折，但後段提供有效的矛盾依據，兩者未列為額外錯誤。

完整的 32 項原始理由、evidence 與逐項輔助評註：[assisted_reason_review.json](judge-generalization-20261013/assisted_reason_review.json)。沒有修改、修復或替換任何原始 Judge 判定。

## 成本與執行證據

| 格式 | 請求 | 模型耗時總和 | 平均每答案成本 | prompt tokens | completion tokens | total tokens |
| --- | --- | --- | --- | --- | --- | --- |
| 九項批次 | 8 | 1,859.833 秒，約 31 分 | 232.479 秒，一次請求 | 14,704 | 14,760 | 29,464 |
| c6+c7 單項合計 | 16 | 2,364.947 秒，約 39 分 25 秒 | 295.618 秒，兩次請求 | 24,440 | 19,935 | 44,375 |

整輪模型耗時合計 4,224.780 秒，約 70 分 25 秒，不含服務查詢與離線分析。以每答案兩項單項合計比較一次批次，時間為 1.272 倍、tokens 為 1.506 倍。批次提供九項，單項只提供兩項；這不是相同完整評估能力的成本比較。此輪固定格式交錯但非隨機化，快慢也受執行環境影響，不能歸因於格式本身。

Qwen `qwen/qwen3.5-9b`、Q8_0、context 8192、temperature 0、Thinking ON、checked budget 1024、strict JSON、max output 6144、timeout 600。啟動前以 LM Studio UI 確認 Thinking／budget；之後 Mac 鎖定，無法重讀 UI。每次請求前與結束後核對的 native runtime metadata 一致，24 次皆觀測到 reasoning tokens 1024。Native metadata 本身未暴露 UI budget，因此不宣稱它可獨立驗證該設定。沒有更改 runtime、生成 SUT 回答或存取 Google。

固定輸入、標籤、rubric、system prompt、client、facts、runner、預設 v10 與原始草稿的 hashes 均在執行前保存、完成後驗證一致。原始答案、事件、準則與標籤與 Rachel 審閱的草稿逐項相同。單項保留原 c6/c7 對應，但輸出重新編號 c1；count/context/schema/ID 仍一起改變。

- [原始報告](judge-generalization-20261013/raw_report.json)：24 次原始 JSON、reasoning、generation usage、timings、runtime、hashes。
- [原始配對比較](judge-generalization-20261013/comparison.json)：planned/available 分母、改善與退步、成本；理由與成本保持原始 pending 狀態。
- [最終審查 manifest](judge-generalization-20261013/manifest.json)：原始報告／比較 byte-for-byte 保留、檔案 hashes、輔助理由審查後門檻結論；成本與輸出仍待 Rachel 審閱。
- [核准計畫](../../evals/proposals/JUDGE_GENERALIZATION_REVIEW_PLAN.md)、[執行說明](../../evals/JUDGE_GENERALIZATION_EXECUTION.md)。

## 後續判斷

#6 的局部診斷證據仍有效，本輪顯示它不能直接推廣到這八份新答案。不要以新增單項模式作為正式可靠性修復。本 PR 可保留為可重現的研究證據與離線回歸支援；是否合併由 Rachel 另外決定。

下一個實驗應先提出能處理 N1/N2 邊界問題的不同假說與獨立審閱案例，預先固定標籤與門檻；不在這輪原案例上反覆調措辭後稱為推廣成功。此輪是同作者合成 development set、一輪固定非隨機排程；不證明獨立準確率、repeatability、其他準則或真實 SUT／Google 情境可靠性。
