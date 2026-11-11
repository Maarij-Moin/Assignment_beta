"""
SaafHawa - tool latency measurement script (Assignment Beta, Q1, Section 2 item 6)
Student ID: 22K-8706

Measures wall-clock latency of the four agent tools:
  1. air_quality  -> Open-Meteo Air-Quality API (PM2.5 / PM10, CAMS data, no API key).
                     (OpenAQ v3 now requires an API key; Open-Meteo air-quality is used as the
                     open-source air-quality tool. If OPENAQ_API_KEY is set, OpenAQ is also timed.)
  2. weather      -> Open-Meteo Forecast API (temperature, humidity, wind)
  3. heat_index   -> local NOAA Rothfusz heat-index computation
  4. kb_lookup    -> local TF-IDF style keyword retrieval over a small advisory knowledge base

Every measurement is appended to raw_tool_latency_log.csv (raw timing log for submission).
Usage:  python measure_tool_latency.py --calls 12
Run on at least two different days so that >= 20 calls per API are spread over 2 days.
"""
import argparse
import csv
import datetime as dt
import math
import os
import re
import time
from collections import Counter

import requests

KARACHI = {"lat": 24.8607, "lon": 67.0011}
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw_tool_latency_log.csv")

AQ_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
WX_URL = "https://api.open-meteo.com/v1/forecast"
OPENAQ_URL = "https://api.openaq.org/v3/locations"

# ---------------- tools ----------------

def air_quality_tool():
    r = requests.get(AQ_URL, params={"latitude": KARACHI["lat"], "longitude": KARACHI["lon"],
                                     "current": "pm2_5,pm10", "timezone": "Asia/Karachi"}, timeout=30)
    r.raise_for_status()
    c = r.json()["current"]
    return f"PM2.5={c['pm2_5']} PM10={c['pm10']}"


def openaq_tool(key):
    r = requests.get(OPENAQ_URL, params={"coordinates": f"{KARACHI['lat']},{KARACHI['lon']}",
                                         "radius": 25000, "limit": 5},
                     headers={"X-API-Key": key}, timeout=30)
    r.raise_for_status()
    return f"locations={len(r.json().get('results', []))}"


def weather_tool():
    r = requests.get(WX_URL, params={"latitude": KARACHI["lat"], "longitude": KARACHI["lon"],
                                     "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
                                     "timezone": "Asia/Karachi"}, timeout=30)
    r.raise_for_status()
    c = r.json()["current"]
    return c["temperature_2m"], c["relative_humidity_2m"], c["wind_speed_10m"]


def heat_index_tool(t_c, rh):
    """NOAA Rothfusz regression (with Steadman simple formula below 80 F)."""
    t = t_c * 9 / 5 + 32
    hi = 0.5 * (t + 61.0 + (t - 68.0) * 1.2 + rh * 0.094)
    if (hi + t) / 2 >= 80:
        hi = (-42.379 + 2.04901523 * t + 10.14333127 * rh - 0.22475541 * t * rh
              - 6.83783e-3 * t * t - 5.481717e-2 * rh * rh + 1.22874e-3 * t * t * rh
              + 8.5282e-4 * t * rh * rh - 1.99e-6 * t * t * rh * rh)
        if rh < 13 and 80 <= t <= 112:
            hi -= ((13 - rh) / 4) * math.sqrt((17 - abs(t - 95)) / 17)
        elif rh > 85 and 80 <= t <= 87:
            hi += ((rh - 85) / 10) * ((87 - t) / 5)
    return (hi - 32) * 5 / 9


KB = [
    "Heatwave advisory: avoid outdoor activity between 12 pm and 4 pm, drink water every 20 minutes, wear light cotton clothes.",
    "Children and elderly are most vulnerable to heatstroke; keep them indoors during peak heat and watch for dizziness and vomiting.",
    "Asthma patients should carry inhalers and avoid outdoor exercise when PM2.5 exceeds 35 ug/m3.",
    "When PM2.5 is above 55 ug/m3 wear an N95 mask outdoors and keep windows closed.",
    "Outdoor labourers should take shaded breaks every hour and use oral rehydration salts during heatwaves.",
    "Heat index above 41 C is dangerous; above 54 C heatstroke is highly likely with prolonged exposure.",
    "Schools may close or shorten timings during declared heatwaves by the Sindh government.",
    "Evening sea breeze lowers temperature near the coast, but humidity raises the heat index.",
    "Symptoms of heat exhaustion: heavy sweating, weakness, cold clammy skin, fast weak pulse, nausea.",
    "WHO 2021 air quality guideline: PM2.5 24-hour mean 15 ug/m3, PM10 24-hour mean 45 ug/m3.",
]
_TOK = lambda s: re.findall(r"[a-z0-9.]+", s.lower())
_DOCS = [Counter(_TOK(d)) for d in KB]
_DF = Counter(w for d in _DOCS for w in d)


def kb_lookup_tool(query, k=2):
    q = Counter(_TOK(query))
    n = len(_DOCS)
    scores = []
    for i, d in enumerate(_DOCS):
        s = sum(q[w] * d[w] * math.log((n + 1) / (_DF[w] + 0.5)) for w in q if w in d)
        scores.append((s, i))
    scores.sort(reverse=True)
    return [KB[i] for _, i in scores[:k]]


# ---------------- timing ----------------

def timed(fn, *a):
    t0 = time.perf_counter()
    status, out = "ok", ""
    try:
        out = fn(*a)
    except Exception as e:  # noqa
        status, out = "error", repr(e)[:120]
    return (time.perf_counter() - t0) * 1000.0, status, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--calls", type=int, default=12)
    ap.add_argument("--gap", type=float, default=2.0, help="seconds between rounds")
    args = ap.parse_args()
    key = os.environ.get("OPENAQ_API_KEY")
    new = not os.path.exists(LOG)
    with open(LOG, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["timestamp_local", "date", "round", "tool", "latency_ms", "status", "output"])
        for i in range(1, args.calls + 1):
            now = dt.datetime.now()
            rows = []
            ms, st, out = timed(air_quality_tool); rows.append(("air_quality_open_meteo", ms, st, out))
            if key:
                ms, st, out = timed(openaq_tool, key); rows.append(("air_quality_openaq", ms, st, out))
            ms, st, wx = timed(weather_tool); rows.append(("weather_open_meteo", ms, st, wx))
            t_c, rh = (wx[0], wx[1]) if st == "ok" else (38.0, 60.0)
            # local tools are very fast -> time 1,000 repetitions and report per-call mean
            t0 = time.perf_counter()
            for _ in range(1000):
                hi = heat_index_tool(t_c, rh)
            rows.append(("heat_index_local", (time.perf_counter() - t0), "ok", f"HI={hi:.1f}C (mean of 1000)"))
            t0 = time.perf_counter()
            for _ in range(1000):
                docs = kb_lookup_tool("is it safe for my asthma child to go outside in heatwave pm2.5")
            rows.append(("kb_lookup_local", (time.perf_counter() - t0), "ok", docs[0][:50] + " (mean of 1000)"))
            for tool, ms, st, out in rows:
                w.writerow([now.isoformat(timespec="seconds"), now.date().isoformat(), i, tool, f"{ms:.3f}", st, out])
                print(f"{now:%Y-%m-%d %H:%M:%S} r{i:02d} {tool:24s} {ms:9.3f} ms {st}")
            f.flush()
            time.sleep(args.gap)


if __name__ == "__main__":
    main()
