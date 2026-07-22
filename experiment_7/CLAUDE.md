# Experiment 7 — Experiment 6, but with an open-source LLM instead of FinBERT

Re-run of the [experiment 6](../experiment_6/CLAUDE.md) intraday event study, swapping the
sentiment model from **FinBERT** to an **open-source instruction-tuned LLM**
(`Qwen/Qwen2.5-3B-Instruct`). Everything else — the events, timestamps, minute-bar
returns — is held identical, so any difference is purely the scorer.

**Question:** Does a general-purpose LLM (which can read context/nuance a fixed
classifier can't) extract intraday post-news signal that FinBERT missed?

## Design decisions (confirmed with user)

- **Model:** `Qwen2.5-3B-Instruct` (Apache-2.0, runs locally on MPS, no gated access).
- **Scoring method:** zero-shot **label-logit** — prompt the model to answer
  positive/negative/neutral, then read the softmax over those three label tokens at the
  first output position. Signed score = `p(positive) − p(negative)` ∈ [−1, 1]. One forward
  pass per item (no autoregression) → fast, and directly comparable to FinBERT's score.
- **Controlled comparison:** load `../experiment_6/tsla_2024_events.csv`, which already
  holds each event's `headline`, `summary`, session, and precomputed `reaction`/`drift_*`
  returns **plus** FinBERT's score. Re-score with Qwen; recompute the same metrics for
  both models against the identical return columns.

## Approach (single notebook: `experiment_7/llm_event_study.ipynb`)

1. Setup — load Qwen (fp16, MPS); define prompt + label-token ids + batched scorer
   (left-padding so the last-token logits align).
2. Load exp 6 events (text + returns + FinBERT `sentiment` → `finbert_sentiment`).
3. Score `headline + summary` with Qwen → `qwen_sentiment` (batched forward passes).
4. Metrics — IC (Spearman), long/short spread, hit-rate for **both** models vs
   `reaction` and `drift_{5,15,30,60}m`, all-events and regular-hours. Side-by-side.
5. Model agreement — correlation of `qwen_sentiment` vs `finbert_sentiment`.
6. Refetch 2024 minute bars; event-study **CAR plot** grouped by Qwen sentiment sign.
7. Verdict — did the LLM find drift/reaction signal FinBERT didn't?

## Files

- **New:** `experiment_7/llm_event_study.ipynb`.
- **New (output):** `experiment_7/tsla_2024_llm_events.csv`, `experiment_7/tsla_2024_llm_vs_finbert.csv`.
- **Reads only:** `../experiment_6/tsla_2024_events.csv`, `../get_bars.py`, `../.env`.

## Verification

- Run top to bottom with `trade_venv` (Qwen auto-downloads/caches, ~6GB). Sanity: ~4,200
  events scored; `qwen_sentiment` ∈ [−1, 1]; metrics finite; CAR plot renders.
- Confirm the side-by-side table and verdict compare Qwen vs FinBERT.

## Known limitations

- Qwen's label-logit score is near-discrete (~±1/0) — lower resolution than FinBERT's
  continuous probability, which can affect correlation magnitude.
- Same as exp 6: Benzinga (not CNBC) source, gross-of-cost returns, overnight/pre-market
  events bucketed separately, near-simultaneous headlines treated independently.
- A 3B model is small; a larger LLM might read nuance better (runtime trade-off).
