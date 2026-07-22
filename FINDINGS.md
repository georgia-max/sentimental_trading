# TSLA Sentiment → Price: Findings

**Question:** Does sentiment about Tesla (news and social) predict TSLA stock movement?

**Answer:** No. Across nine experiments, sentiment is a **contemporaneous, aggregate
mirror** of price with **no exploitable predictive content** — not next-day, not
multi-week, not in the minutes after a headline breaks, it cannot help a feedback-loop
model reproduce the price wave, and even in the **cross-section** across 30 names it yields
only a faint, insignificant, cost-eaten signal. This holds at daily *and* minute
resolution, across **three sentiment models** (VADER, FinBERT, Qwen-3B LLM) and
**two news sources plus Reddit**, single-name *and* cross-sectional, and it survives a
system-dynamics reframing. It is textbook semi-strong market efficiency.

*Period:* 2024–2026 (experiments 6–7 are 2024 only). *Instrument:* TSLA (exp 1–8);
30 mega-caps (exp 9).
*Prices:* Alpaca (SIP, IEX fallback). *Reproducible:* each experiment is a
self-contained notebook + `CLAUDE.md` in `experiment_N/`.

---

## TL;DR table

| # | Test | Sentiment | Key result | Verdict |
|---|------|-----------|------------|---------|
| 1 | Daily correlation | VADER (news) | weak same-day r≈**+0.12** (p=0.004); next-day ≈0 | reaction only |
| 2 | Better model | FinBERT (news) | same-day r≈**+0.23** (p<0.0001); next-day ≈0 | reaction only, stronger |
| 3 | Multi-horizon | FinBERT (news) | 1d→3mo forward correlation all ≈0 | no lead at any horizon |
| 4 | Directional + backtest | FinBERT (news) | next-day hit-rate **46.6%**; L/S strategy **−84%** vs **+40%** buy-hold | no tradeable edge |
| 5 | Social source | FinBERT+VADER (Reddit) | **no** correlation at any lag, incl. same-day | social even weaker |
| 6 | Intraday event study | FinBERT (Benzinga) | post-news drift IC≈0 (p>0.3); hit-rate ~50% | no drift; daily signal was aggregation |
| 7 | Open-source LLM | Qwen2.5-3B (Benzinga) | drift IC≈0, same as FinBERT despite 25% disagreement | null is model-independent |
| 8 | System-dynamics feedback | FinBERT (Benzinga) | sentiment **degrades** OOS fit (full +0.04 vs loops-only +0.18); shuffle −0.03 | reflexivity contemporaneous, not exploitable |
| 9 | Cross-sectional (30 names) | FinBERT (Benzinga) | IC **+0.015** (t=1.49, ns); L/S Sharpe 0.92 gross → **0.08 net** (73% daily turnover) | faint signal, insignificant + cost-eaten |

---

## The core arc

**The one robust signal is same-day and it strengthens with a better model.** News
sentiment correlates with the *same day's* return: VADER r≈0.12 (exp 1), FinBERT nearly
doubles it to r≈0.23 (exp 2). A finance-tuned model extracts more return-relevant signal
from identical text — so the signal is real.

**But it is a reaction, not a forecast.** The same-day link vanishes by the next close
and never reappears: forward correlation is ≈0 at 1 day, 1 week, 2 weeks, 1 month, and
out to 3 months (exp 3). Reframed as a trade, the sign of sentiment predicts the sign of
tomorrow's move only **46.6%** of the time — worse than a coin flip — and a long/short
strategy on that signal **loses 84%** while buy-and-hold makes +40% (exp 4).

**Social sentiment is weaker still.** Reddit (r/teslamotors) posts show **no** correlation
with returns at any horizon — not even same-day (r≈0.02, p=0.55), vs news's +0.23. Retail
chatter tracks price far more loosely than professional news, and ~97% of posts are
title-only link posts (exp 5).

**Even at minute resolution, there is no edge.** Using precisely timestamped Benzinga
headlines and minute bars, sentiment carries no directional information over the 5–60
minutes *after* publication (drift IC ≈ 0, p>0.3; sub-1-bps long/short spread; ~50%
hit-rate). Notably, the *immediate* per-headline reaction IC is also ≈0 — nothing like the
daily +0.23 — which means **the daily correlation was largely an aggregation effect**:
averaging hundreds of noisy per-headline scores surfaces a weak signal that no individual
tradeable headline carries (exp 6).

**A capable LLM finds nothing either.** Swapping FinBERT for an open-source instruction
LLM (Qwen2.5-3B) on the identical events gives the same null — drift IC ≈ 0 at every
horizon — even though the LLM disagrees with FinBERT on 25% of headlines. When two very
different scorers independently find no signal, the absence is a property of the data,
not the model (exp 7).

**And it can't even help a feedback model.** Reframed as system dynamics — price as a
reflexive feedback system that sentiment couples into — the endogenous loops
(mean-reversion) track the 2026 holdout with correlation +0.18, but *adding* sentiment
**lowers** that to +0.04 (sentiment injects noise), and shuffled sentiment scores −0.03.
Reflexivity is real in-sample but sentiment is a reflection of price, not a driver of it
(exp 8).

**The cross-section — the one designed to work — comes closest, and still fails.** Ranking
30 mega-caps daily by news sentiment gives a *positive* next-day IC (+0.015) and a gross
long-short Sharpe of 0.92 — the most alive any result looked. But the IC isn't significant
(t=1.49), 73% daily turnover crushes the net Sharpe to 0.08, and the market-neutral book
badly trails simply holding the universe (Sharpe 1.37). A textbook "real-but-uneconomic"
outcome: the edge that theory says should exist is too weak and too costly to trade at this
scale (exp 9).

---

## Experiment details

### Experiment 1 — Daily correlation (VADER, CNBC news)
`experiment_1/` · ~4,770 CNBC articles (2024-01→2026-04), VADER on headline + cleaned body,
correlated with daily close-to-close returns over ~565 trading days.
- Same-day: Pearson **+0.120** (p=0.004), Spearman +0.125 (p=0.003).
- Next-day: −0.024 (p=0.56), not significant.
- **Takeaway:** a weak but significant same-day relationship; nothing predictive.

### Experiment 2 — Finance-tuned model (FinBERT, CNBC news)
`experiment_2/` · same articles/returns, re-scored with FinBERT (`ProsusAI/finbert`),
compared head-to-head with VADER.
- Same-day: FinBERT **+0.227** (p<0.0001) vs VADER +0.120 — nearly **2×**.
- Next-day: FinBERT −0.035 (p=0.41), still nothing.
- **Takeaway:** the signal is real and model-dependent, but purely contemporaneous.

### Experiment 3 — Multi-horizon lag (FinBERT, CNBC news)
`experiment_3/` · sentiment(t) vs forward cumulative return at 1, 3, 5, 10, 15, 21, 42, 63
trading days.
- Every forward horizon |r| ≤ 0.05, all p > 0.27. Same-day reference +0.227.
- **Takeaway:** no lead–lag at any horizon; the relationship is same-day or nothing.

### Experiment 4 — Directional accuracy + backtest (FinBERT, CNBC news)
`experiment_4/` · does `sign(sentiment)` predict `sign(forward return)` vs coin flip and a
"majority-class" baseline; no-look-ahead long/short backtest vs buy-and-hold.
- Next-day hit-rate **46.6%** (below 50%, p=0.11); every horizon at/below baselines.
- Backtest: sentiment L/S **−83.6%** total, Sharpe −1.0 vs buy-hold +40.2%, Sharpe 0.55.
- A same-day (look-ahead, non-tradable) version returned +9,232% — sizing the signal that
  exists but can't be captured in time.
- **Takeaway:** no tradeable directional edge; the value is entirely in the untradeable
  same-day window.

### Experiment 5 — Social sentiment (Reddit, FinBERT + VADER)
`experiment_5/` · re-run of exp 3 with r/teslamotors **posts** (21,135, 2024–2026) instead
of news. (Comments excluded — they only cover Jan–May 2024. An earlier dump,
`data/tsla-reddit/`, was 2011–2018 and didn't overlap the price window.)
- Same-day: FinBERT **+0.023** (p=0.55) — essentially zero, vs news +0.227.
- All forward horizons ≈0 (weak −0.08 hint at 3 months, borderline; not robust).
- Only ~3% of posts had body text (rest are title-only link posts). VADER agreed with FinBERT.
- **Takeaway:** retail social tone is far more decoupled from price than professional news.

### Experiment 6 — Intraday event study (Benzinga, FinBERT)
`experiment_6/` · 4,209 timestamped 2024 TSLA news items + 229k minute bars; measured
**reaction** [t, +1m] vs tradeable **drift** [+1m, +Δ] for Δ = 5/15/30/60m, in ET session
buckets.
- Regular-hours drift IC ≈ 0 at every horizon (30m: +0.026, p=0.31); L/S spreads sub-1-bps;
  hit-rate ~50%.
- Absorption: only **19%** of the 30-minute move occurs in the first minute — price keeps
  moving, but **not** in the sentiment direction.
- Immediate reaction IC also ≈0 → the daily +0.23 was an **aggregation artifact**.
- **Takeaway:** no post-news drift to trade, even before costs; the daily signal does not
  survive at the single-event level.

### Experiment 7 — Open-source LLM vs FinBERT (Qwen2.5-3B, Benzinga)
`experiment_7/` · identical exp-6 events/returns, re-scored with `Qwen/Qwen2.5-3B-Instruct`
via zero-shot label-logit scoring; controlled swap of only the scorer.
- Regular-hours drift IC ≈ 0 at every horizon (30m: +0.015, p=0.55), like FinBERT.
- Qwen vs FinBERT: Spearman 0.60, sign agreement **75%** — genuinely different reads,
  same null.
- **Takeaway:** the absence of intraday signal is model-independent — a capable general
  LLM extracts no more than a small finance classifier.

### Experiment 8 — System-dynamics feedback loops (FinBERT, Benzinga)
`experiment_8/` · aggregated causal-loop diagram (R1 reflexive hype, R2 momentum, B1
valuation anchor) → next-day-return model `R=α·S+β·M−γ·G`; 9,852 news items → daily
sentiment; fit 2024–25, evaluate 2026 holdout out-of-sample with ablation + shuffle controls.
- Fitted α(sentiment) ≈ 0, β(momentum) = 0, γ(mean-reversion) > 0.
- 2026 holdout next-day-return correlation: **loops-only +0.179**, full (with sentiment)
  **+0.042**, shuffled sentiment −0.035. Adding sentiment *degrades* the fit.
- The only out-of-sample skill is the **balancing/mean-reversion loop** — a pure price
  effect — but its directional hit-rate is ~51% (magnitude, not direction; not tradeable).
- **Takeaway:** price behaves like an endogenous feedback system; sentiment is a
  contemporaneous reflection of it, not a driver — reflexivity is real in-sample but not
  exploitable forward.

### Experiment 9 — Cross-sectional sentiment IC + long-short (30 mega-caps, FinBERT)
`experiment_9/` · 30 liquid mega-caps, 2024–2026. 44,013 Benzinga articles → **66%** named a
universe stock in the headline (attribution filter drops multi-tag listicle noise) → 29,236
attributed → daily per-ticker sentiment. Cross-sectional Spearman IC of sentiment(t) vs
next-day return across names; long/short tercile portfolio vs equal-weight benchmark.
- Mean daily IC **+0.0149**, t-stat **+1.49** (not significant), 52.8% positive days.
- L/S: **+22% ann / Sharpe 0.92 gross** → **+1.7% ann / Sharpe 0.08 net** (73% daily turnover);
  equal-weight benchmark +32% ann / Sharpe 1.37.
- **Takeaway:** the cross-sectional framing turns the dead single-name signal *faintly*
  positive (the best gross result of the series) but it fails on all three bars —
  significance, transaction costs, and the market-neutral benchmark. Real-but-uneconomic.

---

## Why the negative result is credible

- **Three models** (VADER, FinBERT, Qwen-3B LLM) and **two news sources plus Reddit**
  tell the same story — not a single-model or single-source artifact. Exp 7 shows the LLM
  disagrees with FinBERT 25% of the time yet finds the same null.
- **Two resolutions** (daily close-to-close and 1-minute event-time) agree.
- **Two paradigms** agree — linear correlation/backtest (exp 1–7) *and* a generative
  system-dynamics simulation (exp 8).
- **Single-name and cross-sectional** agree — even aggregating a weak per-name signal across
  30 names (the structure real sentiment strategies use) fails significance and costs (exp 9).
- **Proper hygiene:** no-look-ahead backtest, out-of-sample holdout with ablation and
  shuffle controls, majority-class baseline (not just 50%), binomial significance, and
  honest caveats (autocorrelated long-horizon windows, gross-of-cost returns).
- The result is exactly what efficient-market theory predicts for public information on a
  mega-cap: by the time news is published, it is priced.

## Caveats / limitations

- Single name (TSLA) for exp 1–8; exp 9 uses 30 mega-caps (small for deciles → terciles).
  Findings may not generalize to less-covered stocks.
- News corpora are CNBC (exp 1–5) and Benzinga (exp 6–9); not exhaustive.
- 2026 data is partial (news to ~April; Reddit posts thin out). Exp 6–7 are 2024 only.
- FinBERT is tuned on formal financial text; Reddit slang is out-of-distribution
  (VADER, built for social media, was reported alongside and agreed). Qwen-3B is a small
  LLM; a larger model might read nuance better (exp 7 tests one point on that curve).
- Backtests are gross of transaction costs, spread, borrow, and slippage.
- Exp 8 is a stylized structural model (free-run sensitive to initial conditions), not a
  calibrated forecasting system.

## What could still work (mostly tested now)

- **Cross-sectional** was the strongest prior and is now tested (exp 9): a faint positive
  IC (+0.015) that is **not significant and does not survive costs**. The remaining threads
  to make it economic are turnover-focused, not signal-focused:
  - **Cut turnover:** weekly rebalance, signal EWMA smoothing, or turnover-penalized
    portfolio construction (73% daily turnover was the killer, not the raw signal).
  - **Larger universe (~500 names) + sector/beta neutralization:** more names ≈ more
    daily observations, which could push the IC t-stat past 2 and enable real deciles.
  - Honest prior: these may reach significance, but the costs problem is structural at this
    signal strength — likely still uneconomic at retail scale.
- **Non-tone features (untested):** attention/volume shocks (abnormal news volume),
  sentiment *surprise* (Δ vs an EWMA baseline) rather than level, options-implied moves.
- Anything above must be evaluated **out-of-sample and net of costs** before being believed.

---

*Environment: `trade_venv` (Python 3.13). Dependencies in `requirements.txt`
(pandas, numpy, matplotlib, scipy, vaderSentiment, torch, transformers, requests,
python-dotenv). Models: `ProsusAI/finbert`, `Qwen/Qwen2.5-3B-Instruct` (local, MPS).
Each `experiment_N/` folder holds its notebook, a `CLAUDE.md` plan, and its output CSVs.*
