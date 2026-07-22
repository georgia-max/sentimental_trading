# Experiment 9 — Cross-sectional sentiment: the one place a real edge could live

Experiments 1–8 tested **single-name TSLA** sentiment and found no forward signal. But
documented sentiment alpha (RavenPack-style) lives in the **cross-section**: a signal too
weak to trade on one stock can aggregate into a market-neutral edge across many. This is
the highest-prior remaining test.

**Hypothesis:** ranking stocks each day by news sentiment predicts the *cross-section* of
next-day returns — high-sentiment names outperform low-sentiment names (positive
Information Coefficient; profitable long-short portfolio).

## Design decisions (confirmed with user)

- **Universe:** ~30 liquid mega-caps across sectors (tech, financials, energy, consumer,
  health). Best news coverage per name; keeps runtime feasible.
- **Attribution:** an article counts for a stock **only if that stock's ticker or company
  name is in the headline** — drops the multi-tag listicle noise (Benzinga articles often
  tag 5–16 symbols; naive attribution poisons the cross-section).
- **Sentiment:** FinBERT (headline + summary), signed score.
- **Period:** 2024–2026 daily. Prices via Alpaca multi-symbol bars (SIP→IEX).

## Approach (single notebook: `experiment_9/cross_sectional.ipynb`)

1. Define universe + company-name aliases for headline matching.
2. Fetch Benzinga news for the universe (paginated `/v1beta1/news`).
3. **Attribute** each article to the universe stock(s) named in its headline; drop the rest.
4. FinBERT-score matched articles; aggregate to **daily per-ticker sentiment**.
5. Fetch daily bars for all names; compute next-day returns.
6. Build the (date × ticker) panel: `sentiment(t)`, `fwd_ret(t→t+1)`.
7. **Cross-sectional IC** — each day, Spearman rank-corr of sentiment vs next-day return
   *across names*; report mean IC, IC t-stat, % positive days, at lag 0 and +1.
8. **Long-short tercile portfolio** — long top-third sentiment, short bottom-third,
   equal-weight, market-neutral; daily returns → cumulative, Sharpe, vs equal-weight
   universe benchmark; **turnover and cost sensitivity** (net of bps/round-trip).
9. Verdict — is the IC positive & significant, and does the L/S beat the benchmark net of costs?

## Files

- **New:** `experiment_9/cross_sectional.ipynb`.
- **New (output):** `experiment_9/xs_panel.csv`, `experiment_9/xs_results.csv`.
- **Reads only:** Alpaca REST (news + bars), `../get_bars.py`, `../.env`.

## Verification

- Run with `trade_venv`. Sanity: each name gets a plausible daily sentiment series after
  headline attribution; panel has ~30 names × ~600 days; IC computed on days with ≥10 names.
- Confirm IC stats, L/S cumulative plot, and cost-sensitivity render; verdict addresses
  significance AND net-of-cost profitability.

## Known limitations

- ~30 names is small for deciles → terciles used; IC is still valid but portfolio is coarse.
- Benzinga only; headline attribution is a heuristic (may miss subsidiary/nickname mentions).
- Survivorship: fixed present-day universe (no delistings) — mild look-ahead in membership.
- Gross IC is honest, but L/S profitability must clear realistic costs; turnover reported.
- No factor neutralization (sector/beta) beyond the cross-sectional demeaning inherent to
  ranking — a positive result would warrant a proper factor-neutral follow-up.
