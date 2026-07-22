# Experiment 5 — Re-run experiment 3 with Reddit sentiment instead of news

Identical design to [experiment 3](../experiment_3/CLAUDE.md) — correlate sentiment(t)
against TSLA forward cumulative returns across horizons — but the **sentiment source
changes from CNBC news articles to Reddit (r/teslamotors)**.

**Question:** Which forward horizon of TSLA price movement (if any) correlates with
*Reddit* sentiment — and does retail social sentiment behave differently from the
professional news sentiment tested in experiments 1–4?

## Data check (why this dataset, not `data/tsla-reddit/`)

The first Reddit dump (`data/tsla-reddit/`) was 2011–2018 — no overlap with the price
window. `data/tsla-reddit-2024/` fits:

- **Posts:** 21,135, **2024-01-01 → 2026-07-22** (full window). ← used
- Comments: 109,492 but only **2024-01-01 → 2024-05-20** → **excluded** (would make
  early-2024 comment-heavy and inconsistent with the posts-only rest of the timeline).

## Design decisions (confirmed with user)

- **Source:** Reddit **posts only** (`title` + `selftext`), full 2024–2026 range.
- **Scorer:** **FinBERT + VADER**, mirroring exp 3, so the only change vs exp 3 is
  the text corpus. Per-post: headline score + body score (if `selftext` present),
  averaged — same structure as exp 1/2.
- **Everything else identical to exp 3:** forward cumulative returns
  `close(t+h)/close(t) − 1` at `h = 1, 3, 5 (≈1wk), 10 (≈2wk), 15, 21 (≈1mo), 42, 63`;
  next-trading-day alignment; Alpaca prices via `../get_bars.py` (SIP→IEX fallback).

## Approach (single notebook: `experiment_5/reddit_horizon_correlation.ipynb`)

1. Setup — load FinBERT + VADER.
2. Parse posts JSONL → `[date, title, selftext]` (date from `created_utc`).
3. Clean text — unescape HTML, strip URLs/markdown; drop `[removed]`/`[deleted]`/empty
   selftext (title-only for those posts).
4. Score — FinBERT (headline + 512-token body) and VADER (headline + body sentences),
   each averaged to a per-post score.
5. Daily aggregate — post-count-weighted daily mean, mapped to next trading day.
6. Prices + forward returns (as exp 3).
7. Merge; correlate FinBERT & VADER vs each horizon (Pearson + Spearman + p).
8. Plots — correlation vs horizon (both models); requested-horizons bar (FinBERT).
9. Verdict — strongest horizon; explicit comparison to exp 3's news-based numbers.

## Files

- **New:** `experiment_5/reddit_horizon_correlation.ipynb`.
- **New (output):** `experiment_5/tsla_reddit_daily.csv`, `experiment_5/tsla_reddit_horizon_correlations.csv`.
- **Reads only:** `../data/tsla-reddit-2024/r_teslamotors_posts.jsonl`, `../get_bars.py`, `../.env`.

## Verification

- Run top to bottom with `trade_venv`. Sanity: ~21k posts parsed; FinBERT/VADER scores
  in [−1, 1]; merged ≈ number of trading days with posts; `fwd_63` non-NaN for merged rows.
- Confirm correlation table + plots render and the verdict compares to exp 3.

## Known limitations

- Same autocorrelation caveat as exp 3 (overlapping forward windows → optimistic long-horizon p).
- Reddit posts skew retail/enthusiast and many are link posts with empty bodies (title-only).
- FinBERT is tuned on formal financial text; Reddit slang is out-of-distribution (VADER,
  built for social media, is the more natural fit and is reported alongside).
- Post volume thins in 2026 (2,319 posts) vs 2024 (11,906).
