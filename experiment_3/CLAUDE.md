# Experiment 3 — Which time lag of price movement correlates with news sentiment?

Follow-up to [experiment 1](../experiment_1/CLAUDE.md) and
[experiment 2](../experiment_2/CLAUDE.md). Those tested only same-day and next-day
returns and found a strong **same-day** correlation (FinBERT r ≈ +0.23) but **no
next-day** signal. This experiment asks: does sentiment relate to price movement
over **longer** horizons — a week, two weeks, a month later?

**Question:** For sentiment on day *t*, which forward horizon *h* of TSLA price
movement is most correlated with it?

## Design decisions

- **Sentiment:** reuse the **FinBERT** (winner of exp 2) and VADER daily scores
  already saved in `../experiment_2/tsla_daily_finbert.csv` — no re-scoring.
- **"Price movement h later" = forward cumulative return** `close(t+h)/close(t) − 1`
  over *h* trading days (the natural reading of "how much it moved over the next
  week/month"). Same-day contemporaneous return is shown as a reference point.
- **Horizons (trading days):** `1, 3, 5 (≈1 week), 10 (≈2 weeks), 15 (≈3 weeks),
  21 (≈1 month)`, plus `42 (≈2 mo)` and `63 (≈3 mo)` as context to see the curve's shape.
- **Prices:** refetch daily bars through *today* (reusing `../get_bars.py`) so the
  latest sentiment dates (through ~2026-04-08) have complete forward windows.

## Approach (single notebook: `experiment_3/horizon_correlation.ipynb`)

1. **Setup** — imports, paths.
2. **Load sentiment** — read `../experiment_2/tsla_daily_finbert.csv` →
   `date`, `finbert_sentiment`, `vader_sentiment`.
3. **Fetch full price series** — daily bars `2024-01-01 → today` via
   `get_bars`; sort; build a contiguous close series.
4. **Forward returns** — for each horizon *h*, `fwd_h = close.shift(-h)/close − 1`
   on the full series (correct across the trading-day sequence).
5. **Merge** sentiment onto prices by date (inner join; ~565 rows).
6. **Correlate** — for each model × horizon, Pearson + Spearman + p-value of
   `sentiment(t)` vs `fwd_h`. Build a tidy table.
7. **Plot** — correlation (Pearson r) **vs. horizon** as a line chart for FinBERT
   and VADER, with significance markers and guide lines at 5/10/21 days; plus a
   bar chart of the requested horizons (1wk / 2wk / 1mo).
8. **Verdict** — which horizon has the strongest / most significant correlation,
   its sign (momentum vs. mean-reversion), and whether any predictive horizon beats
   the same-day reaction.

## Files

- **New:** `experiment_3/horizon_correlation.ipynb`.
- **New (output):** `experiment_3/tsla_horizon_correlations.csv` — the r/p table.
- **Reads only:** `../experiment_2/tsla_daily_finbert.csv`, `../get_bars.py`, `../.env`.

## Verification

- Run top to bottom with `trade_venv`. Sanity: full price series extends past the
  sentiment dates so `fwd_21` (and longer) are non-NaN for all merged rows.
- Confirm the correlation table + horizon plot render and the verdict names a lag.

## Known limitations

- Longer horizons overlap heavily (sentiment days are ~1 apart, windows are 5–63
  days), so successive observations are **autocorrelated** — p-values at long
  horizons are optimistic; treat them as descriptive, not a clean significance test.
- Corpus is CNBC-only; 2026 sentiment ends ~April, so the longest horizons lean on
  2024–2025 dates.
- A raw sentiment *level* is used (not surprise/Δ); a level-vs-forward-return link
  can reflect slow trends as much as prediction.
