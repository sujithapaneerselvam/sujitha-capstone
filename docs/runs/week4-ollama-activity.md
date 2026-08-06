# Week 4 Activity — Comparing Ollama with OpenAI Models

For this activity, I added a local LLM option to my existing Week 4 pipeline using Ollama. I used the `llama3.2:3b` model on my MacBook and compared its performance with `gpt-4o-mini` and `gpt-4o` using the same set of 10 questions.

I first installed Ollama locally and downloaded the `llama3.2:3b` model. In my pipeline, I added this model to the cost configuration with a cost of `$0.00`, since it runs locally and does not make paid API calls. I also updated the client setup so that OpenAI models continue to use the OpenAI API, while the Llama model connects to the local Ollama endpoint.

While testing, I found that the local model did not always follow the tool-calling output format correctly. For example, it sometimes returned `sources` as text instead of a list, skipped required fields, or did not call the required tool. To handle this, I added a structured JSON-output fallback. This allowed the pipeline to validate the response and still return a properly structured answer.

## Results

| Model         | Questions | Total Cost | Average Cost per Question | Average Confidence |       Time |
| ------------- | --------: | ---------: | ------------------------: | -----------------: | ---------: |
| `gpt-4o`      |        10 |  $0.014868 |                 $0.001487 |               0.93 |  28.43 sec |
| `gpt-4o-mini` |        10 |  $0.000767 |                 $0.000077 |               0.91 |  27.87 sec |
| `llama3.2:3b` |        10 |  $0.000000 |                 $0.000000 |               0.87 | 453.74 sec |

The biggest benefit of the local Llama model was cost. It completed all 10 questions without any API cost, which makes it useful for experimenting with prompts, learning, and privacy-sensitive use cases.

However, the local model was much slower. It took about 7.5 minutes to complete the 10 questions, while both OpenAI models completed in less than 30 seconds. It also needed the structured-output fallback for 8 out of 10 questions.

The quality difference was especially clear in the question about `schema_version`. Both OpenAI models gave answers related to schema changes, compatibility, and versioning. In contrast, the Llama model returned unrelated examples such as timestamps, IP addresses, and order numbers. This showed that a small local model may perform reasonably well for simple questions but can struggle with questions that require more context and reasoning.

Overall, `gpt-4o-mini` gave the best balance in this experiment. It was much cheaper than `gpt-4o`, fast, and completed all questions without retries. `gpt-4o` gave the highest average confidence but was around 19 times more expensive than `gpt-4o-mini`.

This activity helped me understand that local models are useful when cost and privacy are important, but they need stronger validation and fallback handling. For a general production use case, I would prefer `gpt-4o-mini` because it provides a good mix of reliability, speed, and cost.
