import json, time, math, os, statistics as st
from concurrent.futures import ThreadPoolExecutor
import requests

F = "https://fapi.binance.com"
S = "https://api.binance.com"
s = requests.Session()
s.headers.update({"User-Agent": "scan/1.0"})

def get(url, **p):
    for i in range(3):
        try:
            r = s.get(url, params=p, timeout=15)
            if r.status_code == 200:
                return r.json()
            time.sleep(0.4 * (i + 1))
        except Exception:
            time.sleep(0.4 * (i + 1))
    return None

HERE = os.path.dirname(os.path.abspath(__file__))
now = int(time.time() * 1000)

# ---------- universe ----------
ei = get(F + "/fapi/v1/exchangeInfo")
symbols = {}
for x in ei["symbols"]:
    if x["quoteAsset"] == "USDT" and x["contractType"] == "PERPETUAL" and x["status"] == "TRADING":
        if now - x["onboardDate"] > 45 * 86400_000:
            symbols[x["symbol"]] = x

t24 = {t["symbol"]: t for t in get(F + "/fapi/v1/ticker/24hr")}
bk = {b["symbol"]: b for b in get(F + "/fapi/v1/ticker/bookTicker")}
prem = {p["symbol"]: p for p in get(F + "/fapi/v1/premiumIndex")}
spot24 = {t["symbol"]: t for t in get(S + "/api/v3/ticker/24hr")}

elig = []
for sym, x in symbols.items():
    t = t24.get(sym); b = bk.get(sym)
    if not t or not b:
        continue
    qv = float(t["quoteVolume"])
    bid, ask = float(b["bidPrice"]), float(b["askPrice"])
    if qv < 5e6 or bid <= 0 or ask <= 0:
        continue
    spread = (ask - bid) / ((ask + bid) / 2) * 100
    if spread > 0.20:
        continue
    elig.append(dict(sym=sym, base=x["baseAsset"], qv=qv, px=float(t["lastPrice"]),
                     chg24=float(t["priceChangePercent"]), spread=spread,
                     funding=float(prem.get(sym, {}).get("lastFundingRate", 0)) * 100))

print("eligible after liq/spread:", len(elig), file=open(os.path.join(HERE, "elig.txt"), "w"))

def kl(sym, interval, limit):
    d = get(F + "/fapi/v1/klines", symbol=sym, interval=interval, limit=limit)
    return d or []

def rets(sym):
    d = kl(sym, "1h", 30)
    if len(d) < 26:
        return None
    c = [float(k[4]) for k in d]
    v = [float(k[5]) for k in d]
    # exclude last (unclosed) candle
    c = c[:-1]; v = v[:-1]
    r = lambda n: (c[-1] / c[-1 - n] - 1) * 100
    return dict(r1=r(1), r3=r(3), r4=r(4), r24=r(24))

def rvol(sym):
    d = kl(sym, "15m", 40)
    if len(d) < 22:
        return None
    v = [float(k[5]) for k in d][:-1]
    base = st.mean(v[-21:-1])
    return v[-1] / base if base > 0 else None

with ThreadPoolExecutor(12) as ex:
    R = list(ex.map(lambda e: rets(e["sym"]), elig))
    V = list(ex.map(lambda e: rvol(e["sym"]), elig))
for e, r, v in zip(elig, R, V):
    if r is None or v is None:
        continue
    e.update(r); e["rvol"] = v

elig = [e for e in elig if "r1" in e]

def nz(x, lo, hi):  # map x in [lo,hi] -> 0..1, clipped
    return max(0.0, min(1.0, (x - lo) / (hi - lo)))

for e in elig:
    long_ = (25 * nz(e["r1"], -1, 5) + 15 * nz(e["r3"], -2, 8) + 10 * nz(e["r4"], -3, 10)
             + 10 * nz(e["r24"], -5, 15) + 15 * nz(e["rvol"], 0.7, 2.5))
    short_ = (25 * nz(-e["r1"], -1, 5) + 15 * nz(-e["r3"], -2, 8) + 10 * nz(-e["r4"], -3, 10)
              + 10 * nz(-e["r24"], -5, 15) + 15 * nz(e["rvol"], 0.7, 2.5))
    e["side"] = "LONG" if long_ >= short_ else "SHORT"
    e["pre"] = round(max(long_, short_), 2)

# BTC/ETH benchmark
bm = {sym: (lambda r: (r or {}).get("r24"))(rets(sym)) for sym in ("BTCUSDT", "ETHUSDT")}

# spot confirmation
for e in elig:
    sp = spot24.get(e["base"] + "USDT")
    if sp:
        e["spot"] = True
        e["spot_chg24"] = float(sp["priceChangePercent"])
        e["spot_qv"] = float(sp["quoteVolume"])
    else:
        e["spot"] = False

short_a = [e for e in elig if e["side"] == "LONG"]
short_b = [e for e in elig if e["side"] == "SHORT"]
top = sorted(short_a, key=lambda e: -e["pre"])[:14] + sorted(short_b, key=lambda e: -e["pre"])[:14]

def enrich(e):
    sym = e["sym"]
    oi = get(F + "/futures/data/openInterestHist", symbol=sym, period="15m", limit=17)
    if oi and len(oi) > 4:
        a, b, c = float(oi[0]["sumOpenInterestValue"]), float(oi[-1]["sumOpenInterestValue"]), float(oi[-4]["sumOpenInterestValue"])
        e["oi_1h"] = (b / c - 1) * 100
        e["oi_4h"] = (b / a - 1) * 100
        e["oi_usd"] = b
    d = get(F + "/fapi/v1/depth", symbol=sym, limit=50)
    if d:
        bp = float(d["bids"][0][0]); ap = float(d["asks"][0][0])
        bidv = sum(float(p) * float(q) for p, q in d["bids"])
        askv = sum(float(p) * float(q) for p, q in d["asks"])
        e["ob_imb"] = (bidv - askv) / (bidv + askv) * 100
        e["ob_depth_usd"] = round((bidv + askv) / 2)
        e["spread_l2"] = (ap - bp) / ((ap + bp) / 2) * 100
    return e

def ind(d, closed=True):
    """d: klines list; returns dict of indicators on closed candles"""
    k = d[:-1] if closed else d
    c = [float(x[4]) for x in k]; h = [float(x[2]) for x in k]; l = [float(x[3]) for x in k]
    v = [float(x[5]) for x in k]; o = [float(x[1]) for x in k]
    def ema(vals, n):
        a = 2 / (n + 1); e = vals[0]
        out = [e]
        for x in vals[1:]:
            e = x * a + e * (1 - a); out.append(e)
        return out
    e20, e50, e200 = ema(c, 20), ema(c, 50), ema(c, 200)
    # RSI Wilder
    def rsi(vals, n=14):
        g = [max(vals[i] - vals[i - 1], 0) for i in range(1, len(vals))]
        ls = [max(vals[i - 1] - vals[i], 0) for i in range(1, len(vals))]
        ag, al = st.mean(g[:n]), st.mean(ls[:n])
        for i in range(n, len(g)):
            ag = (ag * (n - 1) + g[i]) / n; al = (al * (n - 1) + ls[i]) / n
        return 100 - 100 / (1 + ag / al) if al else 100
    # ATR/ADX
    def atr_adx(h, l, c, n=14):
        tr = [h[0] - l[0]]
        pdm = [0]; ndm = [0]
        for i in range(1, len(c)):
            tr.append(max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])))
            up = h[i] - h[i - 1]; dn = l[i - 1] - l[i]
            pdm.append(up if up > dn and up > 0 else 0)
            ndm.append(dn if dn > up and dn > 0 else 0)
        atrr = st.mean(tr[:n]); p = st.mean(pdm[:n]); q = st.mean(ndm[:n])
        atrs = [atrr]; ps = [p]; qs = [q]
        for i in range(n, len(tr)):
            atrr = (atrr * (n - 1) + tr[i]) / n; atrs.append(atrr)
            p = (p * (n - 1) + pdm[i]) / n; ps.append(p)
            q = (q * (n - 1) + ndm[i]) / n; qs.append(q)
        pdi = [100 * ps[i] / atrs[i] if atrs[i] else 0 for i in range(len(ps))]
        ndi = [100 * qs[i] / atrs[i] if atrs[i] else 0 for i in range(len(qs))]
        dx = [100 * abs(pdi[i] - ndi[i]) / (pdi[i] + ndi[i]) if pdi[i] + ndi[i] else 0 for i in range(len(pdi))]
        adx = st.mean(dx[:n])
        for i in range(n, len(dx)):
            adx = (adx * (n - 1) + dx[i]) / n
        return atrs[-1], pdi[-1], ndi[-1], adx
    atr, pdi, ndi, adx = atr_adx(h, l, c)
    m = ema(c, 12); sg = ema(c, 26)
    macd = m[-1] - sg[-1]
    macdl = []
    for i in range(len(c)):
        pass
    # vwap: UTC day session
    day0 = (int(k[-1][0]) // 86400_000) * 86400_000
    tp = 0.0; tv = 0.0
    for x in k:
        if int(x[0]) >= day0:
            p_ = (float(x[2]) + float(x[3]) + float(x[4])) / 3
            tv_ = float(x[5])
            tp += p_ * tv_; tv += tv_
    vwap = tp / tv if tv else c[-1]
    return dict(px=c[-1], ema20=e20[-1], ema50=e50[-1], ema200=e200[-1],
                rsi=rsi(c), atr=atr, atr_pct=atr / c[-1] * 100, adx=adx, pdi=pdi, ndi=ndi,
                macd=macd, macd_sig=sg[-1], vwap=vwap,
                hi50=max(h[-50:]), lo50=min(l[-50:]),
                sw8hi=max(h[-8:]), sw8lo=min(l[-8:]),
                sw32hi=max(h[-32:]), sw32lo=min(l[-32:]))

with ThreadPoolExecutor(8) as ex:
    list(ex.map(enrich, top))

for e in top:
    d15 = kl(e["sym"], "15m", 300)
    d5 = kl(e["sym"], "5m", 200)
    d1h = kl(e["sym"], "1h", 200)
    d4h = kl(e["sym"], "4h", 250)
    if not (d15 and d5 and d1h and d4h):
        continue
    e["i15"] = ind(d15); e["i5"] = ind(d5); e["i1h"] = ind(d1h); e["i4h"] = ind(d4h)
    e["r1_5m"] = (float(d5[-2][4]) / float(d5[-7][4]) - 1) * 100

out = []
for e in top:
    if "i15" not in e:
        continue
    i = e["i15"]; i5 = e["i5"]; ih = e["i1h"]; i4 = e["i4h"]
    bull15 = i["px"] > i["ema200"] and i["px"] > i["vwap"] and i["ema20"] > i["ema50"]
    bear15 = i["px"] < i["ema200"] and i["px"] < i["vwap"] and i["ema20"] < i["ema50"]
    dist20 = (i["px"] / i["ema20"] - 1) * 100
    distvwap = (i["px"] / i["vwap"] - 1) * 100
    prof = dict(
        sym=e["sym"], side=e["side"], pre=e["pre"], px=e["px"], chg24=e["chg24"],
        r1=e["r1"], r3=e["r3"], r4=e["r4"], r24=e["r24"], r1_5m=e["r1_5m"],
        qv=round(e["qv"] / 1e6, 1), spread=e["spread"], spread_l2=e.get("spread_l2"),
        depth=e.get("ob_depth_usd"), imb=e.get("ob_imb"), rvol=e["rvol"],
        funding=e["funding"], oi1=e.get("oi_1h"), oi4=e.get("oi_4h"),
        spot=e["spot"], spot_chg=e.get("spot_chg24"),
        adx=i["adx"], pdi=i["pdi"], ndi=i["ndi"], rsi=i["rsi"], macd=i["macd"] - i["macd_sig"],
        atrp=i["atr_pct"], dist20=dist20, distvwap=distvwap,
        t15="BULL" if bull15 else ("BEAR" if bear15 else "MIXED"),
        e200_15="above" if i["px"] > i["ema200"] else "below",
        adx_h=ih["adx"], adx_4= i4["adx"],
        h4="BULL" if i4["px"] > i4["ema50"] > i4["ema200"] else ("BEAR" if i4["px"] < i4["ema50"] < i4["ema200"] else "MIXED"),
        h1="BULL" if ih["px"] > ih["ema20"] > ih["ema50"] else ("BEAR" if ih["px"] < ih["ema20"] < ih["ema50"] else "MIXED"),
        rsi5=i5["rsi"], hi50=i["hi50"], lo50=i["lo50"],
        macd_h=ih["macd"] - ih["macd_sig"],
        atr_usd=i["atr"], vwap=i["vwap"], ema20=i["ema20"], ema50=i["ema50"],
        sw8hi=i["sw8hi"], sw8lo=i["sw8lo"],
    )
    out.append(prof)

json.dump(dict(ts=now, btc=bm, n_elig=len(elig), rows=out), open(os.path.join(HERE, "scan.json"), "w"), indent=1)
print("BTC24", bm.get("BTCUSDT"), "ETH24", bm.get("ETHUSDT"), "elig", len(elig), "profiled", len(out))

out.sort(key=lambda r: -r["pre"])
print("\n| # | Pair | Side | Score | 1H | 3H | 4H | 24H | RVOL | ADX15 | RSI15 | TF |")
print("|---|------|------|-------|----|----|----|-----|------|-------|-------|----|")
for n, r in enumerate(out[:15], 1):
    print(f"| {n} | {r['sym']} | {r['side']} | {r['pre']:.1f} | {r['r1']:+.2f} | {r['r3']:+.2f} | {r['r4']:+.2f} | "
          f"{r['r24']:+.2f} | {r['rvol']:.2f} | {r['adx']:.1f} | {r['rsi']:.1f} | {r['t15']}/{r['h1']}/{r['h4']} |")
print("\nlevels: sym px atr ema20 ema50 vwap sw8lo sw8hi 24hhi 24hlo funding% oi4h% spread% depth$")
for r in out[:15]:
    print(f"{r['sym']} {r['px']:.6g} {r['atr_usd']:.6g} {r['ema20']:.6g} {r['ema50']:.6g} {r['vwap']:.6g} "
          f"{r['sw8lo']:.6g} {r['sw8hi']:.6g} {r['hi50']:.6g} {r['lo50']:.6g} {r['funding']:+.3f} "
          f"{r['oi4'] if r['oi4'] is not None else 0:+.2f} {r['spread']:.3f} {r['depth']}")
