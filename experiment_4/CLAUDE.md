# Experiment 4 — Does sentiment *sign* predict the move's sign better than a coin flip?

Follow-up to experiments 1–3. Correlation was strong same-day (FinBERT r ≈ +0.23)
but zero at every forward horizon (exp 3). This experiment reframes the question in
**directional / tradable** terms.

**Hypothesis:** The *sign* of sentiment on day *t* predicts the *sign* of the forward
price move better than a coin flip (and better than the naive "always up" baseline),
and a simple sentiment-sign strategy beats buy-and-hold.

## Design decisions

- **Sentiment:** reuse FinBERT (exp 2 winner) + VADER daily scores from
  `../experiment_2/tsla_daily_finbert.csv`.
- **Prices / forward returns:** refetch daily bars through today via `../get_bars.py`
  (SIP → IEX fallback), forward cumulative returns as in exp 3.
- **Directional metric:** `hit_rate = mean( sign(sentiment(t)) == sign(fwd_return) )`.
- **Two baselines:**
  1. **Coin flip = 50%.**
  2. **Majority class** = `max(P(up), P(down))` — the "always predict the more common
     direction" accuracy. Sentiment must beat this to be useful, because TSLA drifted.
- **Significance:** two-sided binomial test (`scipy.stats.binomtest`) of hit-rate vs 0.5.
- **Backtest (no look-ahead):** decide at close of day *t* from sentiment known by *t*,
  hold to *t+1*. Long if sentiment>0, short if <0 (±1). Compare equity curve, total
  return, annualized Sharpe, and hit-rate to **buy-and-hold**. A same-day
  (look-ahead) curve is shown too, **clearly labeled as not tradable**, to size the
  contemporaneous signal.

## Approach (single notebook: `experiment_4/directional_accuracy.ipynb`)

1. Setup.
2. Load sentiment (exp 2 csv).
3. Fetch prices; build forward returns `fwd_h` for `h ∈ {1, 5, 10, 21}` + `same_day`.
4. Merge sentiment onto returns.
5. **Hit-rate table** — per model × horizon: n, hit_rate, base_rate_up, majority
   baseline, edge-vs-majority, binomial p vs 0.5.
6. **Conditional accuracy** — FinBERT: P(up | sent>0), P(down | sent<0), with counts
   (a 2×2 directional confusion view).
7. **Backtest** — long/short from `sign(sentiment(t))` held to `t+1`; equity vs
   buy-and-hold; plus illustrative look-ahead same-day curve.
8. **Verdict** — beats coin flip? beats majority? beats buy-and-hold?

## Files

- **New:** `experiment_4/directional_accuracy.ipynb`.
- **New (output):** `experiment_4/tsla_hitrate.csv` — the hit-rate table.
- **Reads only:** `../experiment_2/tsla_daily_finbert.csv`, `../get_bars.py`, `../.env`.

## Verification

- Run top to bottom with `trade_venv`. Sanity: hit rates in [0,1]; backtest equity
  curves finite; buy-and-hold return matches TSLA's actual 2024→2026 move roughly.
- Confirm hit-rate table, both plots, and the verdict render.

## Known limitations

- No transaction costs / slippage / borrow fees for shorts — an idealized backtest.
- Forward-horizon hit rates use overlapping windows (autocorrelated) → optimistic p-values.
- Single name (TSLA), CNBC-only news, 2026 sentiment ends ~April.
- Sentiment *level* sign only; a magnitude/threshold or surprise signal is not tested here.
