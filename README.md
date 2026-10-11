# Evidence-first support-answer service

A small Python CLI that reads `kb.json`, retrieves local FAQ passages, checks support, and returns either a cited extractive answer or a clear abstention. No API key, installation, server, or generated index is needed for the default mode.

## Quick start

Requires Python 3.10 or newer. Open a terminal in this directory.

```bash
python app.py "How do I reset my password?"
python app.py "Can support change my email address for me?"
python validate.py
python evaluate.py
```

The first query returns `decision: answer` and a citation. The second returns `decision: abstain` and an empty citations array. Validation exits with status 0 on success. On systems where Python is named `python3`, replace `python` with `python3`.

JSON input is also supported. In PowerShell:

```powershell
'{"question":"How do I reset my password?"}' | python app.py
```

On bash:

```bash
echo '{"question":"How do I reset my password?"}' | python app.py
```

Output has exactly the required top-level keys: `question`, `decision`, `answer`, `citations`, and `debug`. Each citation contains `id`, `title`, and `snippet`. Debug contains `retrieved_ids` and `support_score`. JSON goes to stdout; invalid input/file errors go to stderr with exit status 2. Invalid input is an error, not an unsupported valid question.

## Design and execution order

See `SPECS.md` for the initial design notes, created before source implementation.

1. **LOAD_KB:** Read UTF-8 JSON from disk on every request. Validate an array of entries with non-empty string `id`, `title`, and `text`; reject duplicate IDs.
2. **RETRIEVE:** Normalize English query words and a small set of common word forms. Rank up to three passages with inverse-document-frequency-weighted query overlap, plus a small title boost. Ignore zero-overlap passages.
3. **CHECK_SUPPORT:** Apply the deterministic gate below before invoking any composer.
4. **ANSWER or ABSTAIN:** Quote the supported FAQ text with its original ID/title/text citation, or return the fallback and no citations.

There are no embedded knowledge-base answers or sample document IDs in `app.py`. The normalization dictionary contains language mappings, not policies. Replace `kb.json` with any other file following the schema, or use:

```bash
python app.py --kb replacement.json "What is the Zeta warranty period?"
```

The default file path is relative to `app.py`, so running the script from another working directory still loads the correct KB. An explicit relative `--kb` path is relative to the current working directory.

## Explicit support rule

The best-ranked passage must cover the meaningful query words in its **body**, not merely its title. Coverage is the fraction of normalized query tokens found in the passage. An explicit time unit also supports a generic duration token.

- No retrieved evidence, or fewer than two meaningful query words: abstain.
- Tax/legal questions and requests for guarantees: abstain under this application's conservative scope policy, even if a replacement KB mentions those topics.
- Recognized instruction-override/secret requests: abstain.
- Coverage below 0.85: abstain.
- Missing requested numbers, actions, or any remaining meaningful query token: abstain. This final check makes effective accepted coverage **1.0**; the earlier threshold is an initial weak-evidence filter.
- Otherwise answer from the top passage. No cross-document synthesis is attempted.

`support_score` reports raw top-passage query coverage, **not a probability that the answer is correct**. A scope-blocked query can have a high score and still abstain. Similar-topic retrieval is insufficient when the requested detail is missing. In particular, residential-address instructions do not support changing an email address.

## Grounding and chunking

Each short FAQ stays as one chunk. This preserves nearby conditions, exceptions, and negation, such as weekend delays or identity verification requirements. Both the answer and citation snippet are exact source text, so no new steps, numbers, or policies can be introduced. Returning the whole short article may include some extra relevant context; long documents would need more careful chunking.

The final output guard accepts only the complete supported passage as the answer. Even a custom composer returning invented text is replaced by the grounded rule-based answer. A citation establishes provenance, not the truth of the underlying KB.

## Optional LLM-backed mode and fallback

Retrieval (`retrieve`), support checking (`check_support`), and composition (`RuleComposer` / `LLMComposer`) are separate. Default mode is `rule`.

```bash
python app.py --mode llm "How do I reset my password?"
```

To call Gemini, configure `GEMINI_API_KEY` and `GEMINI_MODEL` as environment variables before running. Choose a model actually available to your account. This version does not read `apikey.env` automatically. Do not type/show a secret while screen sharing or commit one to Git.

The adapter uses Python's standard-library HTTPS client and Google's documented `generateContent` REST API. It requests extractive JSON output from the already approved context. The response is accepted only if it equals the complete source passage: a shortened answer could omit a critical exception. Missing configuration, a timeout, API failure, malformed JSON, or changed source wording triggers the rule-based fallback. The LLM cannot override the retrieval/support decision. Timeout is 12 seconds, with no retries.

This is deliberately constrained LLM-backed extraction, **not free-form summarization**. Its value is demonstrating a replaceable answering layer while retaining the same grounding invariant. The hosted success path has not been live-tested with credentials; offline fallback paths are tested. Reference: https://ai.google.dev/api/generate-content

## Tests and small evaluation

```bash
python validate.py
python evaluate.py
```

The regression suite checks disk loading, answer/abstain behavior, exact citation grounding, JSON keys, new document IDs/content, changing file contents between requests, empty/invalid files, invalid questions, ordering before composition, injection requests, untrusted composer output, CLI stdin, and LLM fallback without secrets or on timeout.

The eight-question evaluation reports decision accuracy and citation presence among answered questions. The shipped sample yielded 8/8 expected decisions and citations for 5/5 answered questions. This is a smoke test, not a claim about unseen-query accuracy. Sample-query regression tests and evaluation assume the shipped sample KB; the dedicated replacement test creates an independent temporary KB and checks changed answers.

## Known limits and next steps

- English lexical matching can abstain on valid paraphrases, typos, broad questions, and questions spanning multiple articles. This intentionally favors caution.
- Word coverage cannot prove semantic entailment or detect every subject/relationship mismatch. Exact quotation prevents invented claims but may still retrieve context that does not fully resolve a question.
- Conflicting or malicious KB entries are not comprehensively detected; treat the local KB as curated content. Text is never executed as code.
- Scope guards and injection patterns are narrow rules, not a complete security boundary.
- Default rule mode is deterministic, offline, and fast for a small FAQ. IDF computation is rebuilt per query for simplicity.
- Next steps: collect labeled paraphrases/negative examples, tune retrieval, detect conflicting evidence, and introduce a validated semantic support checker before relaxing the extractive constraint.

## Files

| File | Purpose |
| --- | --- |
| `SPECS.md` | Initial design notes |
| `kb.json` | Replaceable sample knowledge base |
| `app.py` | Loader, retrieval, support gate, composers, CLI |
| `test_app.py` | Offline regression suite |
| `validate.py` | One-command test runner |
| `evaluate.py` | Eight-question smoke evaluation |
| `requirements.txt` | Documents zero third-party dependencies |
| `.gitignore` | Excludes secrets, environments, Python cache |

No generated artifacts are needed to reproduce outputs. Run the commands above after a clean checkout. AI assistance was used to develop the design, implementation, and tests; review the code and rerun validation before submission.
