# Design notes — written before implementation

## Goal
Build a small, runnable support-answer CLI. Read the knowledge base on each request, retrieve evidence, check support, then answer or abstain. The evaluator can replace kb.json without changing code.

## Flow
LOAD_KB -> RETRIEVE -> CHECK_SUPPORT -> ANSWER or ABSTAIN

## Decisions
- Python standard library for the default path; no installation or secrets required.
- Keep each short FAQ as one passage, preserving qualifications and exceptions.
- Rank passages using normalized keyword overlap and inverse document frequency.
- Require strong coverage of question keywords in one passage. Missing numbers, requested guarantees, and advice requests need conservative handling.
- Compose answers by quoting a supported passage verbatim. Citations use original IDs, titles, and exact text. This avoids invented steps or timings.
- Keep composition separate from retrieval and support checks so a different composer can be injected later.
- CLI prints structured JSON and accepts a positional question or a JSON object on stdin.
- Invalid files fail with a clear error; empty valid knowledge bases abstain.

## Validation plan
Test supported/unsupported questions, citation grounding, JSON shape, replacement knowledge bases, empty/invalid files, and retrieval-before-composition. Include a separate eight-question evaluation.

## Scope and risks
Conservative English lexical retrieval can reject valid paraphrases; keyword coverage is not semantic proof. Quoted evidence prevents new claims but cannot certify the truth of the source. No external web search or account actions. Optional LLM integration only after the default path is validated.
