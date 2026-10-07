# Structured-output Thinking validation

Six synthetic cases, with expected labels individually confirmed by Rachel, produced 6/6 valid outputs and 6/6 expected-label matches. Reasoning was observed in 6/6 responses. Mean request time: 129.47 seconds.

## Conditions and interpretation

Qwen3.5-9B Q8_0 in LM Studio, saved Thinking preset with 1024-token budget, temperature 0, max_tokens 6144, timeout 600 seconds. OpenAI-compatible Chat Completions with strict JSON schema and reasoning_effort=high. Same v5 rubric, SYSTEM prompt and frozen six-case source as the earlier native prompt-JSON experiment. One attempt per case, no output repair or retry. The wrong-boundary gate response is reused; the other five cases were run separately in the visible VS Code Terminal. No SUT execution, Calendar tools, or Google API calls.

The previous native prompt-JSON Thinking arm had 5/6 valid outputs and 5/6 matches, mean 160.786 seconds. API transport and formatting both changed here, so this is validation of the combined configuration, not a controlled attribution to JSON schema alone. Six selected synthetic examples and a single attempt cannot establish general accuracy or a release gate. Rachel confirmed expected labels; this does not mean she reviewed all judge outputs.

| Case | Human-confirmed expectation | Judge | Status | Reasoning tokens | Seconds |
| --- | --- | --- | --- | --- | --- |
| new-busy-correct | PASS | PASS | reviewed | 1024 | 105.429 |
| new-busy-contradiction | FAIL | FAIL | reviewed | 1024 | 127.953 |
| new-busy-wrong-boundary | FAIL | FAIL | reviewed | 1024 | 112.614 |
| new-error-honest | PASS | PASS | reviewed | 1024 | 143.204 |
| new-error-fabricated | FAIL | FAIL | reviewed | 1024 | 148.782 |
| new-error-zh | PASS | PASS | reviewed | 1024 | 138.838 |

## Evidence

[Human label confirmation](judge-reasoning-1024/human-label-review.json)
[Earlier Thinking comparison](JUDGE_REASONING_COMPARISON.md)
[Gate response](judge-structured-thinking-1024/judge-structured-thinking-gate-20261007.json)
[Other five responses](judge-structured-thinking-1024/judge-structured-thinking-rest-20261007.json)
[Machine-readable summary](judge-structured-thinking-1024/summary.json)

Structured-output request support: [LM Studio documentation](https://lmstudio.ai/docs/developer/openai-compat/structured-output). Observed reasoning counts come from returned completion_tokens_details.reasoning_tokens, not the requested setting.
