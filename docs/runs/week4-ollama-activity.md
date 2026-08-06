# Week 4 Activity — Ollama as a Third Model

## Goal

I integrated a local Ollama model, `llama3.2:3b`, into the existing Week 4 LLM pipeline and compared it with `gpt-4o-mini` and `gpt-4o` on the same 10 questions.

## Setup

* Installed Ollama locally on macOS.
* Pulled the `llama3.2:3b` model.
* Added `llama3.2:3b` to `RATES` in `src/pipeline/cost.py` with input and output costs of `0.0`.
* Added an OpenAI-compatible client factory in `pipeline.py`:

  * OpenAI models use the default OpenAI API endpoint.
  * Local Llama models use Ollama at `http://localhost:11434/v1`.
* Retained tool-calling for OpenAI models.
* Added a structured JSON-output fallback for the local model when tool-calling returned an invalid schema.

## Results

| Model         | Questions | Total cost (USD) | Avg. cost/question | Avg. confidence |       Time |
| ------------- | --------: | ---------------: | -----------------: | --------------: | ---------: |
| `gpt-4o`      |        10 |        $0.014868 |          $0.001487 |            0.93 |  28.43 sec |
| `gpt-4o-mini` |        10 |        $0.000767 |          $0.000077 |            0.91 |  27.87 sec |
| `llama3.2:3b` |        10 |        $0.000000 |          $0.000000 |            0.87 | 453.74 sec |

## What I observed

1. **Local inference has zero marginal API cost.** `llama3.2:3b` completed all 10 questions at $0.00, which is useful when experimenting repeatedly with prompts or working with privacy-sensitive information.

2. **`gpt-4o` was about 19.4× more expensive than `gpt-4o-mini`.** However, both OpenAI models completed all 10 calls without retries and in about 28 seconds.

3. **Local tool-calling was unreliable.** `llama3.2:3b` needed the structured-output fallback on 8 out of 10 questions. Common failures were returning `sources` as a string instead of a list, omitting fields, or not calling the requested tool.

4. **The quality gap was visible in the schema-versioning question.** `gpt-4o` and `gpt-4o-mini` gave responses related to schema changes and backward compatibility. In contrast, `llama3.2:3b` returned unrelated examples such as timestamps, IP addresses, and order numbers instead of answering about `schema_version`.

## Conclusion

For a general-purpose production application, `gpt-4o-mini` appears to be the best balance of cost, speed, and reliability in this experiment. `gpt-4o` was the most expensive but produced the highest average confidence. `llama3.2:3b` is valuable for free local experimentation and privacy-sensitive scenarios, but the slower execution and unreliable structured-output compliance mean it needs stronger validation and fallback handling.
