# Week 5 Graded Mini Project — Prompt Lab

This project compares four prompting strategies on one structured extraction task:

- zero-shot
- few-shot
- structured / role-based
- chain-of-thought (silent reasoning, JSON-only answer)

The task is to extract a company name, job role, and minimum years of experience from 10 job postings.

## Setup

Use Python 3.10 or later. Create a file named .env in this project folder:

    OPENAI_API_KEY=your_key_here

Do not upload or commit the .env file.

Install and run:

    python -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt
    python mp1_prompt_lab.py

Windows activation:

    .venv\\Scripts\\activate

## What the program does

1. Sends 10 job snippets through each of the four strategies using gpt-4o-mini (40 calls).
2. Captures raw output, parsed output, latency, and token-based cost.
3. Scores each output against the supplied golden set.
4. Uses gpt-4o as an LLM judge for all 40 outputs.
5. Generates the required reports from the real run.

## Generated files

- results.json — every captured model result and score
- results.csv — spreadsheet-friendly output
- mp1_comparison.md — required comparison table, including J10 null-value analysis
- mp1_writeup.md — required one-page reflection based on the actual metrics

The J10 edge case has no stated experience requirement. Its correct value is null. A strategy that returns any number for J10 has hallucinated information.
