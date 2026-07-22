# Experiment 1 — Does TSLA news sentiment correlate with TSLA stock movement (2024–2026)?

This folder contains a single, self-contained experiment. This `CLAUDE.md` is the
plan and working guide for it.

## Context

The project (`sentimental_trading`) has two halves that have never been connected:
a **news corpus** (`../data/tsla/` — ~4,770 CNBC article `.md` files spanning
2024-01-01 → 2026-04-08, each with YAML frontmatter `date`/`title`/`url` + a
Markdown body) and **price tooling** (`../get_bars.py`, which pulls TSLA OHLCV
bars from Alpaca). No sentiment scores and no correlation code exist yet.

**Hypothesis to answer:** *TSLA news sentiment is correlated with TSLA's daily
stock movement over 2024–2026* — tested both **contemporaneously** (sentiment
day *t* vs. return day *t*) and **predictively** (sentiment day *t* vs. return
day *t+1*).

Goal: the **simplest, most straightforward** pipeline that produces a clear
yes/no verdict with a correlation coefficient, a p-value, and two plots.

## Design decisions (confirmed with user)

- **Sentiment method:** VADER (rule-based, free, deterministic, offline).
- **Text scored:** headline **and** article body, with body cleaned to remove
  image links, video captions, and promo lines.
- **Deliverable:** a single Jupyter notebook.

## Approach (single Jupyter notebook: `experiment_1/sentiment_correlation.ipynb`)

Run top to bottom. Cells:

1. **Setup** — imports (`pandas`, `numpy`, `matplotlib`, `re`, `pathlib`,
   `scipy.stats`, `vaderSentiment`), `load_dotenv()`, one
   `SentimentIntensityAnalyzer`.

2. **Load & parse news** — walk `../data/tsla/{2024,2025,2026}/*.md`. Parse the
   YAML frontmatter by splitting on the `---` fences (5 fixed fields, no library
   needed) to get `date` + `title`; the remainder is the body. Build a
   DataFrame `[date, title, body]`. (Expect ~4,770 rows.)

3. **Clean body** — regex pipeline to drop the flagged noise:
   - images `!\[.*?\]\(.*?\)` → removed
   - links `\[([^\]]+)\]\([^)]+\)` → keep link **text** only (`\1`)
   - video/promo lines: drop lines matching `VIDEO\d`, `watch now`, and the
     trailing CNBC promo line; strip `#`/`##` heading markers
   - collapse whitespace.

4. **Score sentiment (VADER)** — per article:
   `headline_score` = VADER compound of the title; `body_score` = mean of VADER
   compound over body sentences (simple regex split on `.?!` to avoid
   long-document saturation and skip the `nltk` download); `article_score` =
   mean(headline_score, body_score).

5. **Aggregate to daily** — `groupby(date)` → `mean_sentiment` and
   `article_count` (kept as a "news volume" covariate).

6. **Fetch prices** — reuse the existing generator: `from get_bars import
   get_bars` (add repo root to `sys.path`), call with daily params
   (`timeframe="1Day"`, `start=2024-01-01`, `end=2026-04-09`,
   `adjustment="split"`, `sort="asc"`). Try `feed="sip"`; on a `403` (free
   tier), fall back to `feed="iex"` and note it. Compute `daily_return` =
   close-to-close `pct_change()`.

7. **Align by trading day** — map each news `date` to the first **trading day
   ≥ that date** (Fri/weekend news lands on the next session), re-aggregate
   sentiment onto trading days, merge with returns on date.

8. **Correlate** — `scipy.stats.pearsonr` and `spearmanr` at **lag 0**
   (same-day) and **lag +1** (next-day return). Print a table of coefficient +
   p-value for each.

9. **Plots** (matplotlib): (a) dual-axis time series — TSLA close vs. rolling
   mean daily sentiment; (b) scatter of sentiment vs. next-day return with a
   fitted regression line.

10. **Verdict** — a cell interpreting coefficients & p-values: is the hypothesis
    supported, at which lag, how strong. Save the merged daily table to
    `experiment_1/tsla_daily_merged.csv`.

## Files

- **New:** `experiment_1/sentiment_correlation.ipynb` — the entire experiment.
- **New (output):** `experiment_1/tsla_daily_merged.csv` — merged daily table.
- **Reuse:** `../get_bars.py` → `get_bars(params)` generator (already paginated,
  reads `.env` via the `ALPACA_PAPER_*` convention). No change needed.
- **Modify:** `../requirements.txt` — add `vaderSentiment` and `scipy`.
- **Reads only:** `../data/tsla/{2024,2025,2026}/*.md`, `../.env`.

## Verification

- Run the notebook top to bottom with the `trade_venv` kernel after
  `pip install vaderSentiment scipy`.
- Sanity checks: news DataFrame ≈ 4,770 rows; trading-day series ≈ 550–570 rows
  (2024-01 → 2026-04); no NaNs in the merged frame after alignment.
- If SIP 403s, confirm the IEX fallback fetches daily bars over the full range.
- Confirm the correlation table prints finite coefficients + p-values, both
  plots render, and the verdict cell states a clear conclusion.

## Known limitations (state these in the notebook)

- Correlation ≠ causation; same-day news is partly a *reaction* to price.
- VADER is general-purpose, not finance-tuned (e.g. "plunge"/"beat" are weak in
  its lexicon) — acceptable for a simple first pass.
- Corpus is CNBC-only and 2026 is partial (through ~April), so 2026 is thinner.
