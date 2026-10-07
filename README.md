# Rachel's Agentic AI Quality & Test Harness — v0.1

學習目標：以 Senior QA 的角度，測試一個會選擇工具的 local AI agent。
Development target：Rachel 的 M5 MacBook Air，32GB memory / 4TB SSD。

## 最新目標：Calendar Scheduling Assistant

本專案的 System Under Test 改為有實際用途的行事曆排程助理。使用者用自然語言要求安排時間；本機模型理解任務、選擇工具，Python 查詢及寫入 Google Calendar。Quality harness 驗證它是否正確理解時間、避開衝突、適當追問、遵守確認流程，以及如實回報結果。

**狀態：這是已確認的目標架構，Calendar 功能尚未實作。** 現有程式仍是 QA mock 原型，不能建立行事曆活動。下方執行指令用來理解與驗證既有原型。

例如：「幫我在週五下午找一個沒有衝突的 30 分鐘，安排 Python 練習。」

目標流程：

1. 確定活動名稱、日期、時間範圍、長度和時區；缺資訊時追問。
2. 使用 `check_availability` 查詢指定 Google Calendar 的忙碌時段。
3. 提出空檔，顯示確切的活動標題、日期、開始與結束時間及時區。
4. 使用者明確確認後，由 Python 驗證確認的內容與建立請求一致，再允許 `create_event` 寫入。
5. 依據 API 實際結果回傳活動連結；失敗時如實回報。

第一版只使用專用測試行事曆，建立使用者自己的單次活動。Google OAuth 與 Calendar API 設定尚待完成。模型推論在 Mac；Calendar 查詢與寫入會連到 Google。模型權重只有一份，位於 repo 外。

沿用 custom Python loop、tool allowlist、參數驗證、執行上限與 JSON trace。確認流程必須由程式控制，不能只依賴 system prompt。防止重複建立及處理不確定的 API 結果是實作需求，尚未完成。

暫不加入：邀請別人、週期活動、改期／刪除、LangGraph、RAG、vector DB、Jenkins、真實 Jira、LLM judge、複雜 CI/CD 或自動 RCA。

### 三層品質驗證

| 層級 | 驗證目標 |
|---|---|
| Deterministic tests | 固定模型回覆與 mock API，驗證 loop、參數、錯誤處理、確認與重複請求邏輯 |
| Integration tests | 使用真實 Calendar API 和專用測試行事曆，驗證授權、查空檔、建立並讀回活動 |
| Agent evaluations | 使用真實本機模型，驗證日期／時區、衝突、追問、確認、重複建立與成功／失敗回報；檢查 trace 和實際活動 |

保留 mock 作為可重現的測試資料；真實 API 用於 integration tests。Calendar evaluation 預設不應自動寫入個人行事曆；寫入測試需有明確測試授權及限定的測試行事曆。

### 既有原型

現有 `get_requirement` 回傳固定需求；`run_test_suite` 回傳固定模擬結果，不執行 pytest。Python 控制 loop，模型提出工具呼叫。

21 個 deterministic tests 曾通過，真實模型也已完成 REQ-2 → reset 的工具流程。這些結果證明既有原型可運作，不能視為 Calendar 功能已通過。

詳細目標架構見 [ARCHITECTURE.md](ARCHITECTURE.md)，範圍與驗收條件見 [PROJECT_SCOPE.md](PROJECT_SCOPE.md)，實際進度見 [SETUP_STATUS.md](SETUP_STATUS.md)。

## 現有原型的 Repo 結構

- `src/harness/agent.py`：最小 custom loop，先讀這個檔案。
- `src/harness/tools.py`：兩個 mock tools 與驗證。
- `src/harness/client.py`：只有 Python standard library 的 local HTTP adapter。
- `src/harness/evaluate.py`：簡單而透明的 graders。
- `src/harness/__main__.py`：doctor / run / eval 入口。
- `tests/test_harness.py`：不用 LLM 的 deterministic tests。
- `evals/cases.json`：15 個英文／中文初始 cases。
- `reports/runs/`：例行執行輸出，不加入 Git；`reports/baseline/`：選定、已檢查的回歸證據，可加入 Git。

## 1. Python environment

需要 Python 3.12+。這次使用 Codex 已有的 Python 3.12 建立 `.venv`，沒有更動 macOS 系統 Python。
目前專案位置：`/Users/rachelwu/dev/agentic-ai-quality-harness`。
先在 terminal 進入專案：

```sh
cd ~/dev/agentic-ai-quality-harness
```

然後執行：

```sh
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
```

在另一台機器 clone repo 後，先用自己的 Python 3.12+ 建立環境：

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

沒有 runtime pip dependencies；pytest 是唯一直接的 test dependency。
Editable install 讓修改 source 後直接看到效果，不必重新安裝。

## 2. LM Studio 與第一個 model

官方 GUI 安裝入口：[LM Studio download](https://lmstudio.ai/download)。
GUI 中搜尋 `openai/gpt-oss-20b`，先下載量化版本、載入模型，再於 Developer 啟動 local server。
初始 context 建議 4096；實際 memory 與速度要以本機測量為準。
32GB 不代表任何 context／quantization 都能載入；記錄版本、model artifact 和設定再比較結果。

此工作也準備官方 headless runtime **llmster**，使用相同 LM Studio API。
若已安裝 CLI，完整路徑可避免修改 shell profile：

```sh
~/.lmstudio/bin/lms --help
~/.lmstudio/bin/lms daemon up
~/.lmstudio/bin/lms get openai/gpt-oss-20b
~/.lmstudio/bin/lms load openai/gpt-oss-20b --identifier openai/gpt-oss-20b --context-length 4096
~/.lmstudio/bin/lms server start --port 1234
```

GUI 與 headless 選一個 server 即可。v0.1 只允許 loopback HTTP。
API 依據：[LM Studio tool-use docs](https://lmstudio.ai/docs/developer/openai-compat/tools)。

```sh
python -m harness doctor
```

確認回傳模型列表，並確認包含 gpt-oss-20b（只有 embedding model 不算完成）。如果 identifier 不同，設定成 doctor 顯示的值：

```sh
export LM_MODEL='openai/gpt-oss-20b'
export LM_BASE_URL='http://127.0.0.1:1234/v1'
```

不需要雲端 API key。這個 CLI 不讀 `.env`；使用 shell environment variables。
Connection refused 通常是 server 未啟動；model not found 要核對 identifier；timeout 要檢查是否載入成功與 memory。

## 3. 跑既有 QA 原型的真實模型案例

```sh
python -m harness run 'First read REQ-2, then run the reset mock suite. Report failed=N.' --output reports/first-run.json
```

打開 trace，依序檢查：模型是否要求 `get_requirement` → Python 是否回傳需求 → 模型是否要求 `run_test_suite` → 最後有沒有說出 failed=1。
Agent 不會強制每個任務都照這個順序；正是 evaluation 要驗證的行為。

## 4. 既有 QA 原型的 evaluation cases

```sh
python -m harness eval --output reports/eval.json
```

15 cases 包括需求查詢、中英文 test summary、兩步工具使用、unknown requirement、無需工具的 greeting，以及不可把失敗結果說成全部通過。
每個 grader 檢查完成狀態、**精確工具順序與參數**、答案必要字串與禁止字串。
這些是 starter checks，可能因正確的不同措辭／多餘查詢而 false fail，也可能讓帶錯誤敘述的答案 false pass。
必須人工 review trace；通過率不等於語意品質或 production readiness。
Temperature=0 仍不保證模型每次回應相同；pytest 的固定回應才是 deterministic。

`run` 成功 exit 0；step limit／錯誤 exit 1。`eval` 全部通過才 exit 0，任何 fail exit 1。
即使某 case exception，evaluation 也會記錄並繼續下一個 case。
報告保留 UTC timestamp、model identifier、endpoint、tool arguments、tool results、final answer。
第一次 baseline 另記 LM Studio / runtime version、實際 model artifact、quantization、context、日期，方便之後比較。

## Rachel 的閱讀順序

1. 先執行 pytest：理解 login 是全通過，reset 故意有一個 failure。
2. 看 `tools.py`：理解 mock 返回的是證據，不是真實服務。
3. 看 `agent.py` 的 for loop：每次把工具結果回送模型，模型才決定下一步。
4. 跑單一真實 run，看 trace，而不是只看 final answer。
5. 跑 15 cases，挑一個失敗案例，區分 tool selection、arguments、順序、final answer 或 runtime 問題。

## GitHub-ready

這是一個獨立 local Git repository，branch `main`。尚未建立 remote 或公開發布。
`.venv`、reports 與 `.env` 被排除；model weights 位於 repo 外。
Review 後可建立自己的 GitHub repository，再設定 remote 並 push。
下一步先設定 Google Calendar API 與專用測試行事曆，再逐步實作兩個真實工具、程式控制的確認流程與 Calendar 測試案例。既有 15 個 QA cases 不代表 Calendar coverage。


## Google Calendar: first read-only connection

This setup command authorizes Google access and reads only the configured test calendar. It does not call the local model or create events. The OAuth scope `calendar.events.owned.readonly` permits reading events on all calendars you own; the application restricts this check to the configured calendar.

Store private configuration outside the repository in `~/.config/agentic-ai-quality-harness/`:
- `google-client.json`: downloaded Desktop OAuth client JSON.
- `calendar.json`: `{"calendar_id": "YOUR_TEST_CALENDAR_ID"}` (never use `primary`).
- `google-readonly-token.json`: generated after you approve Google consent; keep private.

Run in the VS Code Terminal from the project folder:

```sh
.venv/bin/python -m pip install -e '.[calendar]'
.venv/bin/python -m harness.calendar_setup
```

Approve the Google consent yourself. A successful result says `PASS: Connected to the dedicated test calendar`. Denial, timeout, or API errors are failures, not successful integration tests. This is a connection check; the Calendar agent and confirmed event creation are still planned.


## Check a real time slot (read only)

```sh
.venv/bin/python -m harness.calendar_tools --start '2026-10-06T10:00:00-07:00' --end '2026-10-06T10:30:00-07:00'
```

`available: true` means no busy events overlap this interval on the configured test calendar only. This is not a check of your other calendars and does not reserve the slot. Timestamps require seconds and an explicit UTC offset; checks are limited to 31 days. Google filters overlaps using an exclusive lower bound on event end and an exclusive upper bound on event start, so back-to-back events do not conflict. The tool expands recurring instances, includes busy all-day events, ignores transparent/cancelled events, and follows pagination. Failed or incomplete reads produce an error instead of reporting free time. No event titles or descriptions are requested.

Reference: [Google events.list API](https://developers.google.com/workspace/calendar/api/v3/reference/events/list).

`tests/test_calendar_tools.py` simulates API results for deterministic coverage. Run `.venv/bin/python -m pytest -q`. These tests do not access Google or run the model. The command above accesses real Google data, but does not use the local LLM. Connecting this tool to the scheduling agent is the next step.


## Ask the local model about availability

```sh
.venv/bin/python -m harness.calendar_agent 'Check October 6, 2026, 10:00–10:30 AM in America/Los_Angeles on the test calendar.'
```

The flow is: your request → local model → validated `check_availability` arguments → real Google Calendar read → tool observation → model answer. The terminal prints the tool arguments and result. A JSON trace is saved to `reports/calendar-agent-latest.json`; use `--output` to preserve separate runs. Google receives the time interval; model inference remains on the loopback LM Studio server.

`calendar_agent.py` supplies the Calendar prompt, tool schema, and executor to the shared custom loop in `agent.py`. The original QA CLI remains available for its existing tests. This Calendar assistant is read only: no event creation tool is exposed. Missing-information clarification and truthful answers are model behaviors to evaluate, not guarantees enforced by the prompt. The Python tool enforces allowed arguments, interval validation, and the configured calendar. A completed loop means the model returned an answer, not that its interpretation or answer automatically passed evaluation.


## Use the tools in LM Studio chat

An optional stdio MCP adapter in `src/harness/calendar_mcp.py` exposes `check_availability` and `get_current_time`. Install with `.venv/bin/python -m pip install -e '.[mcp]'`. LM Studio launches the adapter using the project's virtual environment; Google configuration and tokens remain outside the repository.

In LM Studio, open a chat and enable `mcp/rachel-calendar-readonly` in the right-side Integrations panel. Ask for a specific date/time/timezone, for example:

> Use check_availability to check October 6, 2026, 10:00–10:30 AM Los Angeles time on the test calendar. Do not create an event.

Review the tool arguments and click **Proceed** for the read-only call. Per-call approval remains enabled. Other calendars are not checked, and the slot is not reserved. For relative dates, ask the model to use `get_current_time` first.

Local configuration in `~/.lmstudio/mcp.json`:

```json
{
  "mcpServers": {
    "rachel-calendar-readonly": {
      "command": "/Users/rachelwu/dev/agentic-ai-quality-harness/.venv/bin/python",
      "args": ["-m", "harness.calendar_mcp"]
    }
  }
}
```

Adjust the absolute Python path on other machines. The LM Studio UI manages its own conversation/tool loop; it does not run `agent.py` or produce the Python agent JSON trace. Both entry points reuse the same Calendar implementation. Keep Python agent runs for repeatable harness evaluation and LM Studio chat for manual exploration.

Verified October 5, 2026: LM Studio chat called the MCP tool with 17:00–17:30 UTC (10:00–10:30 Los Angeles); the tool returned availability and the model answered in Traditional Chinese. No events were created or modified.

References: [LM Studio MCP setup](https://lmstudio.ai/docs/app/mcp), [official MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk).


### Calendar time-zone handling

The agent and MCP tool accept local start/end timestamps without UTC offsets, plus an IANA time zone such as `America/Los_Angeles`. Python resolves daylight-saving offsets. Nonexistent or ambiguous local times require clarification. After updating the MCP server, restart its integration or LM Studio and start a new chat to reload the schema. See [LIVE_CALENDAR_REVIEW.md](LIVE_CALENDAR_REVIEW.md) for the regression and live verification.


### Calendar evaluation dataset

15 read-only Calendar cases are defined in [evals/calendar_cases.json](evals/calendar_cases.json), with execution and grading guidance in [evals/CALENDAR_EVALUATIONS.md](evals/CALENDAR_EVALUATIONS.md). Use `python -m harness.calendar_evaluate` for the controlled Calendar baseline; see the evaluation guide for a three-case smoke run. This uses the real local model with simulated Calendar responses and requires manual answer review. The original prototype evaluator does not support this Calendar schema.

## Local answer judge

A separate tool-free local model reviews saved Calendar answers and evidence. Start with the four human-labeled calibration cases before all 15. See [Calendar judge guide](evals/CALENDAR_JUDGE.md). Configure `SUT_MODEL`, `JUDGE_MODEL`, and `LM_STUDIO_BASE_URL`; `.env.example` documents values but is not automatically loaded. Legacy `LM_MODEL`/`LM_BASE_URL` remain compatible during migration.
