# Experiment 8 — System-dynamics feedback loops: can sentiment + loops mimic the price wave?

A "wild" reframe of the whole investigation. Experiments 1–7 asked *is sentiment
linearly correlated with future returns?* (consistent no). This asks a **reflexivity**
question (à la Soros): **is price a feedback system that news sentiment couples into**,
and can a small causal-loop model driven by sentiment **reproduce TSLA's price waves**?

## Aggregated causal loop diagram (from the news themes)

Variables the TSLA news maps onto, and the loops they form:

- **R1 — reflexive hype (reinforcing):** sentiment → buying → price → media attention → sentiment.
- **R2 — momentum / FOMO (reinforcing):** price → extrapolative expectations → buying → price.
- **B1 — valuation anchor (balancing):** price → valuation gap vs fundamentals → value selling → price.

Reinforcing loops make trends/bubbles; the balancing loop makes reversals; their tug-of-war
makes "waves." Exogenous shocks (Musk, macro, BYD) and fundamentals inject into the loops.

## Model (CLD → difference equations)

```
r(t)   = α·S(t)            # R1: sentiment push
       + β·M(t)            # R2: momentum,     M(t) = λ·M(t−1) + (1−λ)·r(t−1)
       − γ·G(t)            # B1: mean-reversion, G(t) = logP(t) − log(EMA_20(P))
P(t+1) = P(t)·exp(r(t))
```

Free parameters `{α, β, γ, λ}`, fit by minimizing one-step-ahead return error on the
training window; EMA span (20) is a fixed structural choice.

## Design decisions (confirmed with user)

- **Sentiment input:** fresh **Benzinga** `/v1beta1/news` for **2024–2026**, FinBERT-scored,
  aggregated to a daily signed sentiment series.
- **Validation: rigorous.** Fit on **2024–2025**, then **free-run simulate the 2026 holdout**
  (states evolve from the model's own simulated price, fed the real exogenous sentiment).
  Plus two controls:
  - **Ablation:** set `α = 0` (no sentiment; pure price feedback), refit, compare holdout.
  - **Shuffle:** randomly permute the sentiment series, refit, compare — a real sentiment
    signal should beat its shuffled version.

## Approach (single notebook: `experiment_8/feedback_loops.ipynb`)

1. Setup + render the CLD (mermaid) and loop explanation.
2. Fetch Benzinga news 2024–2026 (paginated REST); tag each item to a theme
   (deliveries / Musk / competition / product / macro-regulation) → show theme volume over
   time (news → CLD variables).
3. FinBERT-score headline+summary → daily sentiment `S(t)`, aligned to trading days.
4. Fetch daily prices (Alpaca), build returns, momentum `M`, valuation gap `G`.
5. Fit `{α,β,γ,λ}` on 2024–2025 (scipy one-step MSE).
6. Free-run simulate full range; evaluate 2026 **holdout**: corr(sim vs actual returns),
   directional hit-rate, RMSE. Repeat for **ablation (α=0)** and **shuffled sentiment**.
7. Plots: simulated-vs-actual price overlay (train/test marked); holdout metric comparison
   full vs ablation vs shuffle; news-theme volume.
8. Verdict — does the loop structure mimic the wave, and does *sentiment* add value
   out-of-sample beyond pure price feedback?

## Files

- **New:** `experiment_8/feedback_loops.ipynb`.
- **New (output):** `experiment_8/tsla_sd_daily.csv`, `experiment_8/tsla_sd_results.csv`.
- **Reads only:** Alpaca REST (news + bars), `../get_bars.py`, `../.env`.

## Verification

- Run with `trade_venv`. Sanity: thousands of 2024–2026 news items; sim price path finite
  (no blow-up); holdout metrics computed for all three variants.
- Confirm overlay + comparison plots render and the verdict addresses reflexivity.

## Honest caveats (stated in the notebook)

- **In-sample fit is not evidence.** 4 parameters can trace many curves; only the 2026
  **holdout** + ablation + shuffle are informative.
- Expected result given exp 1–7: pure price feedback (momentum + reversion) likely mimics
  the wave shape (price is autocorrelated), while sentiment forcing adds little out-of-sample.
- Free-running simulation is sensitive to initial conditions; this is a stylized model of
  the *structure*, not a calibrated forecasting system. No transaction costs; not a strategy.
- Benzinga ≠ CNBC corpus; 2026 is partial.
