# Altcoin Momentum Scan — 2026-11-23 11:19 UTC

Institutional-style intraday momentum scan. **Analysis only — no orders executed.** Every setup requires explicit manual approval.

- **Primary data:** Binance USDT-M perpetuals (`fapi.binance.com`)
- **Spot confirmation:** Binance Spot (`api.binance.com`)
- **Cross-check:** Bybit linear tickers (price/funding delta < 0.06% on all picks — no feed discrepancy)
- **Universe:** 151 symbols passed liquidity + spread gate → 28 fully profiled → **5 qualify**
- **Regime:** BTC 61,274 — below EMA20 61,395, above EMA200 60,383, 4H −0.37%. ETH 1,721 mixed. **Range/neutral** → pullback entries only, no breakout chasing.

Filters applied: USDT perpetual, listed > 45 days, 24h quote volume ≥ $5M, L1 spread ≤ 0.20%, closed candles only, UTC timestamps.

---

## Ranking

| # | Pair | Side | Score | 1H | 3H | 4H | 24H | RVOL | ADX15 | RSI15 | TF alignment |
|---|------|------|-------|----|----|----|-----|------|-------|-------|--------------|
| 1 | PIPPINUSDT | LONG | 47.9 | +1.17% | +4.39% | +6.85% | +8.39% | 3.24 | 33.4 | 69.8 | 15M+1H+4H BULL |
| 2 | ALGOUSDT | LONG | 38.6 | +0.30% | +3.34% | +4.08% | +7.66% | 2.31 | 64.4 | 83.1 | 15M+1H BULL, 4H MIXED |
| 3 | VELVETUSDT | LONG | 70.1 | +4.33% | +11.70% | +12.34% | +10.86% | 2.76 | 45.0 | 79.4 | all BULL (extended) |
| 4 | LSKUSDT | LONG | 42.1 | +1.82% | +3.70% | +4.61% | +6.99% | 1.90 | 67.0 | 73.1 | 15M+1H BULL, 4H MIXED |
| 5 | SKYUSDT | SHORT | 45.3 | +0.13% | −5.23% | −6.07% | −12.68% | 18.4 | 45.6 | 26.5 | all BEAR (oversold) |

---

## 1. PIPPINUSDT — LONG (best alignment)

Price 0.01835 · 24h vol $11.1M · spread 0.054% · depth $97k · L2 imbalance **+19.4% bid** · funding +0.006% · OI 4H **+11.1%** · no Binance spot pair (perp-native move, weaker confirmation).

- **Entry zone:** 0.01776–0.01802 (EMA20 0.01776 / just above VWAP 0.01757) — limit only
- **Stop:** 0.01746 (below swing low 0.01754 − 0.25 ATR) = 2.35% risk
- **TP1:** 0.01887 (24h high) → 2.4R
- **TP2:** 0.01960 → 4.1R
- **Invalidate:** 15M close below VWAP 0.01757 with RVOL > 1.5, or OI turns negative while price stalls

## 2. ALGOUSDT — LONG (cleanest structure, needs RSI reset)

Price 0.08237 · vol $9.3M · spread **0.012%** · depth $117k · spot **+9.71%** confirms · funding +0.001% · OI 4H +11.8% · RSI 83 overbought — **do not buy here**.

- **Entry zone:** 0.0795–0.0803 (EMA20 0.07956, above VWAP 0.07878)
- **Stop:** 0.07870 (below VWAP/EMA50) = 1.50% risk
- **TP1:** 0.08235 → 2.0R
- **TP2:** 0.08480 → 4.1R
- **Invalidate:** RSI fails to hold > 50 on pullback, or 4H closes back under EMA20

## 3. VELVETUSDT — LONG (strongest raw momentum, weakest book)

Price 0.07993 · vol $11.0M · spread 0.063% · **depth only $16.6k** · funding +0.018% · OI 4H +10.7% · 15M MACD histogram −0.0727 (decelerating) · perp-only, no spot.

- **Entry zone:** 0.0752–0.0762 (EMA20 0.07521) — 5.7% below spot, no chase
- **Stop:** 0.07370 (below VWAP 0.07385) = 2.64% risk
- **TP1:** 0.08028 → 2.3R
- **TP2:** 0.08430 → 4.3R
- **Size cap:** ~$400 notional (thin book; > $1k = visible slippage)

## 4. LSKUSDT — LONG (tightest pullback geometry)

Price 0.15007 · vol $5.8M (at floor) · spread 0.033% · depth $55k · L2 **+55% bid** · spot +6.07% confirms · funding **−0.074%** (shorts paying; Bybit −0.128% agrees) · OI +3.4% · 4H ADX 17 = weak higher-TF.

- **Entry zone:** 0.1468–0.1480 (EMA20 0.14753 / VWAP 0.14652)
- **Stop:** 0.14560 (below EMA50 0.14501) = 1.22% risk
- **TP1:** 0.15220 → 2.7R
- **TP2:** 0.15500 → 4.2R
- **Invalidate:** volume fails to hold > 1.5× on reclaim, or 24h volume drops under $5M

## 5. SKYUSDT — SHORT (only valid bearish, bounce-entry required)

Price 0.03996 · vol $24.8M · spread 0.051% · depth $200k · spot **−12.15%** confirms · funding −0.018% · OI 4H +5.4% (shorts adding) · **RSI 26.5 oversold, RVOL 18.4** = capitulation risk.

- **Entry zone:** 0.04000–0.04060 (EMA20 0.03969 → EMA50 0.04058); trigger = 5M bearish rejection close, **not** a market sell
- **Stop:** 0.04110 (above EMA50 + 0.8 ATR) = 1.99% risk
- **TP1:** 0.03750 → 3.5R
- **TP2:** 0.03610 → 5.2R
- **Skip if:** 0.04110 taken on volume, or funding flips positive fast (short squeeze)

---

## Rejected

| Symbol | Reason |
|--------|--------|
| PROM | 1H +17.8% vertical, RSI 82, 12.8% above EMA20, RVOL 0.997 (no volume), L2 −55.8% asks stacked, 4H BEAR → exhaustion trap |
| BULLA | +51.9% 24H but RVOL 0.64, 10.2% above EMA20 → no volume confirmation |
| BLESS | ADX 14.9 = CHOPPY/WAIT per rule, despite +50% 24H |
| MUBARAK (watchlist) | Spot +16.7% confirms, OI +18.4%, but 4H BEAR = counter-trend bounce; revisit on 4H close above EMA50 0.02162 |
| BTW (watchlist short) | OI −4.5% (short covering, not new selling), depth $18k, 1H mixed |
| CYS | RVOL 0.90, 4H BEAR, 5M −2.25% fading |

---

## Execution rules

- All 5 are resting-limit / pullback setups. If the zone is not tagged by end of the current UTC session, **cancel**.
- No chase, no market orders, no FOMO entries.
- 4 of 5 require price to return to EMA20/VWAP; only SKY is immediately proximal.
- Manual approval required before any order is placed.

---

*Generated from live exchange APIs at 2026-11-23 11:19 UTC. Not financial advice. No automated execution.*
