# Experiment 6 — Intraday event study: is there tradeable post-news drift? (2024)

The pivot from experiments 1–5. Those used **daily** bars and found sentiment
correlates with price **same-day** (FinBERT r≈0.23) but has **zero forward** power.
The interpretation: the signal is real but **absorbed intraday**. This experiment
tests that directly with **minute bars + timestamped news**.

**Hypothesis:** After a TSLA news item publishes, price **drifts** in the sentiment
direction over the following minutes — enough to be tradeable *after* the first print
(i.e. the move is not fully absorbed in the initial reaction).

## Feasibility (confirmed before building)

- **Timestamped news:** Alpaca `/v1beta1/news` (Benzinga) returns second-resolution
  `created_at` for TSLA in 2024 (e.g. the Q4 deliveries print at `2024-01-02T13:43:07Z`).
  This replaces the day-resolution CNBC scrape (`data/tsla/`), which has no publish time.
- **Minute bars:** Alpaca SIP returns clean 1-minute OHLCV for 2024 (historical SIP works;
  only *recent* data 403s → IEX fallback).

## Scope (per user)

- **2024 only** (`2024-01-01 → 2025-01-01`).
- Sentiment source: **Benzinga news via Alpaca REST** (not the CNBC files).
- Scorer: **FinBERT** (exp-2 winner) on `headline + summary`, signed score p(pos)−p(neg).

## Approach (single notebook: `experiment_6/intraday_event_study.ipynb`)

1. **Fetch news** — all 2024 TSLA items via `/v1beta1/news`, paginated (limit 50,
   `exclude_contentless=true`), reusing `../get_bars.py` auth headers.
2. **Score** — FinBERT on `headline + ". " + summary` (HTML-unescaped, truncated 512).
3. **Fetch minute bars** — 2024 TSLA `1Min` via `get_bars` (SIP→IEX). Convert bar and
   news timestamps to **US/Eastern**; work tz-naive ET so session logic is DST-correct.
4. **Align each event** — entry = first minute bar at/after publish time `t`
   (`merge_asof` forward). Session bucket from entry ET clock: pre-market (<9:30),
   regular (9:30–16:00), after-hours (>16:00).
5. **Reaction vs. drift** —
   - `reaction` = return over `[t, t+1min]` (untradeable — the first print).
   - `drift_Δ` = return over `[t+1min, t+Δ]` for **Δ = 5, 15, 30, 60 min** (tradeable:
     you enter *after* seeing the news). Exits via `merge_asof` forward with a tight
     tolerance so overnight gaps become NaN, not contaminated returns.
6. **Metrics** — per horizon: Information Coefficient (Pearson & Spearman of sentiment
   vs drift), long/short mean spread (pos-sentiment minus neg-sentiment drift), hit rate.
   Overall and **restricted to regular-hours events** (cleanest).
7. **Event-study CAR plot** — mean cumulative return path over minute offsets [−5, +60]
   relative to `t`, split by **positive vs negative** sentiment (the classic chart:
   shows the reaction jump then whether it drifts or reverts).
8. **Verdict** — is drift IC significant and the right sign? What fraction of the total
   move is captured in the first minute (absorption) vs available afterward (edge)?

## Files

- **New:** `experiment_6/intraday_event_study.ipynb`.
- **New (output):** `experiment_6/tsla_2024_events.csv` (events + sentiment + returns),
  `experiment_6/tsla_2024_drift_metrics.csv` (the IC/spread table).
- **Reads only:** Alpaca REST (news + bars), `../get_bars.py`, `../.env`.

## Verification

- Run top to bottom with `trade_venv`. Sanity: thousands of 2024 news items; ~240k
  minute bars; entry match rate high for regular-hours events; drift metrics finite.
- Confirm the CAR plot renders and the verdict states whether tradeable drift exists.

## Known limitations

- Benzinga ≠ CNBC corpus (different source than exp 1–5) — chosen because it is timestamped.
- No transaction costs / spread / slippage — a gross-return event study, not a live backtest.
- Entry at next-minute close is optimistic vs. real fill; drift edges must clear the
  bid-ask spread + fees to be real.
- Overnight/pre-market news is bucketed separately; its "next-open" behaviour is not the
  focus here (regular-hours drift is).
- Multiple near-simultaneous headlines (e.g. the deliveries multi-part print) are treated
  as independent events → mild overlap.
