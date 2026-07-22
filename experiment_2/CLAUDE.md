# Experiment 2 — Does a finance-tuned model (FinBERT) strengthen the sentiment signal?

Follow-up to [experiment 1](../experiment_1/CLAUDE.md), which found a **weak but
significant same-day** correlation between TSLA news sentiment (VADER) and daily
returns (Pearson r ≈ +0.12, p ≈ 0.004), and **no predictive** (next-day) signal.

**Hypothesis:** Swapping VADER (general-purpose lexicon) for **FinBERT**
(`ProsusAI/finbert`, tuned on financial text) strengthens the correlation between
news sentiment and TSLA stock movement.

## Design decisions (confirmed with user)

- **Model:** FinBERT (`ProsusAI/finbert`) via `transformers` + `torch` (uses MPS
  on this Mac). 3-class output → signed score `p(positive) − p(negative)` ∈ [−1, 1],
  directly comparable to VADER's compound score.
- **Text scope:** **headline + first 512 tokens of body**, averaged (user choice —
  the fast, standard-truncation approach). ~9,540 inferences.
- **Fair comparison:** reuse experiment 1's price data **and** its VADER daily
  scores from `../experiment_1/tsla_daily_merged.csv`, so VADER and FinBERT are
  correlated against the *identical* returns and shown side by side.

## Approach (single notebook: `experiment_2/finbert_correlation.ipynb`)

1. **Setup** — load FinBERT tokenizer + model, pick `mps`/`cpu`.
2. **Load experiment 1 output** — read `../experiment_1/tsla_daily_merged.csv`
   for `date`, `c`, `daily_return`, `next_return`, and VADER `mean_sentiment`
   (renamed `vader_sentiment`). Its `date` column is the trading-day grid.
3. **Re-parse & clean articles** — same frontmatter parse + body cleaning as
   experiment 1 (`../data/tsla/{year}/*.md`).
4. **FinBERT score** — batched (`batch_size=32`, `truncation=True,
   max_length=512`): `headline_finbert` from the title, `body_finbert` from the
   truncated cleaned body; `article_finbert = mean(headline, body)`.
5. **Daily aggregate + align** — article-count-weighted daily mean, mapped to the
   next trading day (same rule as experiment 1), merged onto the price table.
6. **Correlate** — Pearson + Spearman for **both** methods at **lag 0** and
   **lag +1** → one tidy comparison table.
7. **Plots** — (a) bar chart of |Pearson r| VADER vs FinBERT × lag; (b) price vs
   FinBERT rolling sentiment; (c) VADER-vs-FinBERT daily-score agreement scatter.
8. **Verdict** — did FinBERT strengthen the signal (larger |r|, smaller p)?

## Files

- **New:** `experiment_2/finbert_correlation.ipynb` — the experiment.
- **New (output):** `experiment_2/tsla_daily_finbert.csv` — merged table with both scores.
- **Reads only:** `../experiment_1/tsla_daily_merged.csv`, `../data/tsla/{year}/*.md`.
- **Modify:** `../requirements.txt` — add `torch`, `transformers` (done).

## Verification

- Run top to bottom with the `trade_venv` kernel (FinBERT model auto-downloads/caches).
- Sanity: ~4,770 articles scored; FinBERT scores in [−1, 1]; merged ≈ 565 trading days.
- Confirm the comparison table prints finite r/p for both methods and all plots render.

## Known limitations

- Same as experiment 1 (correlation ≠ causation; CNBC-only; 2026 partial).
- FinBERT truncates each body to 512 tokens — the tail of long articles is dropped.
- FinBERT is trained on financial *sentences/headlines*; scoring a whole truncated
  body is slightly out of distribution (a reason headline-only was offered).
