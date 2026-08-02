import argparse
import json
import os
from datetime import datetime, timedelta

import pandas as pd
from pykrx import stock
from project_paths import MARKET_DATA_DIR


BENCHMARK_INDEX = {
    "KOSPI": "1001",
    "KOSDAQ": "2001",
}

BENCHMARK_PROXY_TICKER = {
    "KOSPI": ("KOSPI_PROXY_KODEX200", "069500"),
    "KOSDAQ": ("KOSDAQ_PROXY_KODEXKOSDAQ150", "229200"),
}


def parse_asof_date(value):
    if value is None:
        return datetime.now()
    value = value.strip()
    if len(value) == 6:
        return datetime.strptime("20" + value, "%Y%m%d")
    if len(value) == 8:
        return datetime.strptime(value, "%Y%m%d")
    raise ValueError("--date must be YYMMDD or YYYYMMDD")


def fmt_krx_date(dt):
    return dt.strftime("%Y%m%d")


def fmt_file_date(dt):
    return dt.strftime("%y%m%d")


def pct(value):
    if value is None or pd.isna(value):
        return None
    return round(float(value) * 100, 2)


def normalize_ticker(ticker):
    ticker = str(ticker).strip()
    return ticker[1:] if ticker.startswith("A") else ticker


def read_stocks(path):
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    rows = []
    for sector, items in raw.items():
        for item in items:
            rows.append(
                {
                    "sector": sector,
                    "ticker": normalize_ticker(item["ticker"]),
                    "name": item.get("name", ""),
                }
            )
    return rows


def previous_row(df, target_dt):
    if df.empty:
        return None
    target = pd.Timestamp(target_dt.date())
    eligible = df[df.index <= target]
    if eligible.empty:
        return None
    return eligible.iloc[-1]


def first_row_on_or_after(df, target_dt):
    if df.empty:
        return None
    target = pd.Timestamp(target_dt.date())
    eligible = df[df.index >= target]
    if eligible.empty:
        return None
    return eligible.iloc[0]


def return_between(current_close, row):
    if row is None:
        return None
    base = row.get("종가")
    if base is None or pd.isna(base) or float(base) == 0:
        return None
    return float(current_close) / float(base) - 1


def turnover_value(row):
    if row is None:
        return None
    if "거래대금" in row.index and not pd.isna(row["거래대금"]):
        return float(row["거래대금"])
    volume = row.get("거래량")
    close = row.get("종가")
    if volume is None or close is None or pd.isna(volume) or pd.isna(close):
        return None
    return float(volume) * float(close)


def detect_markets(asof_dt):
    date = fmt_krx_date(asof_dt)
    markets = {}
    for market in ("KOSPI", "KOSDAQ"):
        try:
            for ticker in stock.get_market_ticker_list(date, market=market):
                markets[ticker] = market
        except Exception:
            continue
    return markets


def get_ticker_name(ticker, fallback):
    try:
        name = stock.get_market_ticker_name(ticker)
        return name or fallback
    except Exception:
        return fallback


def get_benchmark_series(market, start_dt, end_dt):
    index_code = BENCHMARK_INDEX.get(market, "1001")
    label = market
    try:
        df = stock.get_index_ohlcv_by_date(
            fmt_krx_date(start_dt), fmt_krx_date(end_dt), index_code
        )
    except Exception:
        label, proxy_ticker = BENCHMARK_PROXY_TICKER.get(
            market, ("KOSPI_PROXY_KODEX200", "069500")
        )
        df = stock.get_market_ohlcv_by_date(
            fmt_krx_date(start_dt), fmt_krx_date(end_dt), proxy_ticker
        )
    if df is None or df.empty:
        return label, pd.DataFrame()
    df.index = pd.to_datetime(df.index)
    return label, df.sort_index()


def price_signal(ret_1w, ret_1m, excess_ret_1w, drawdown_52w, turnover_ratio):
    ret_1w = ret_1w if ret_1w is not None else 0
    ret_1m = ret_1m if ret_1m is not None else 0
    excess_ret_1w = excess_ret_1w if excess_ret_1w is not None else 0
    drawdown_52w = drawdown_52w if drawdown_52w is not None else -1
    turnover_ratio = turnover_ratio if turnover_ratio is not None else 0

    if ret_1m >= 0.30 and drawdown_52w >= -0.05 and turnover_ratio >= 1.5:
        return "overheated"
    if ret_1m >= 0.15 and drawdown_52w >= -0.10:
        return "extended"
    if ret_1w <= -0.08 or drawdown_52w <= -0.20:
        return "correction_watch"
    if ret_1w > 0 and excess_ret_1w > 0:
        return "positive"
    if ret_1w < 0 and excess_ret_1w < 0:
        return "negative"
    return "neutral"


def sector_price_signal(row):
    count = row["constituent_count"]
    if count and row["overheated_count"] / count >= 0.30:
        return "overheated"
    if row["avg_ret_1m"] >= 20 and row["avg_drawdown_52w"] >= -7:
        return "overheated"
    if row["avg_ret_1m"] >= 12 or row["avg_excess_ret_1w"] >= 5:
        return "extended"
    if row["avg_ret_1w"] <= -5 or row["avg_drawdown_52w"] <= -18:
        return "correction_watch"
    if row["avg_ret_1w"] > 0 and row["avg_excess_ret_1w"] > 0:
        return "constructive"
    return "neutral"


def collect_one(item, asof_dt, market_lookup, benchmark_cache):
    ticker = item["ticker"]
    end_dt = asof_dt
    start_dt = asof_dt - timedelta(days=400)

    try:
        df = stock.get_market_ohlcv_by_date(
            fmt_krx_date(start_dt), fmt_krx_date(end_dt), ticker
        )
        if df is None or df.empty:
            raise ValueError("empty price data")

        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        current = previous_row(df, asof_dt)
        if current is None:
            raise ValueError("no trading row on or before as-of date")

        market = market_lookup.get(ticker, "KOSPI")
        name = get_ticker_name(ticker, item["name"])
        current_date = current.name.to_pydatetime()
        current_close = float(current["종가"])

        row_1w = previous_row(df, current_date - timedelta(days=7))
        row_1m = previous_row(df, current_date - timedelta(days=30))
        row_3m = previous_row(df, current_date - timedelta(days=90))
        row_ytd = first_row_on_or_after(df, datetime(current_date.year, 1, 1))

        ret_1w = return_between(current_close, row_1w)
        ret_1m = return_between(current_close, row_1m)
        ret_3m = return_between(current_close, row_3m)
        ret_ytd = return_between(current_close, row_ytd)

        high_52w = float(df.loc[df.index <= current.name]["고가"].tail(260).max())
        drawdown = current_close / high_52w - 1 if high_52w else None

        current_turnover = turnover_value(current)
        recent_turnover = [
            turnover_value(row) for _, row in df.loc[df.index <= current.name].tail(20).iterrows()
        ]
        recent_turnover = [v for v in recent_turnover if v is not None]
        avg_turnover = sum(recent_turnover) / len(recent_turnover) if recent_turnover else None
        turnover_ratio = (
            current_turnover / avg_turnover
            if current_turnover is not None and avg_turnover not in (None, 0)
            else None
        )

        benchmark_label = market
        benchmark_ret_1w = None
        try:
            if market not in benchmark_cache:
                benchmark_cache[market] = get_benchmark_series(market, start_dt, end_dt)
            benchmark_label, bdf = benchmark_cache[market]
            brow_current = previous_row(bdf, current_date)
            brow_1w = previous_row(bdf, current_date - timedelta(days=7))
            benchmark_ret_1w = (
                return_between(float(brow_current["종가"]), brow_1w)
                if brow_current is not None
                else None
            )
        except Exception:
            benchmark_ret_1w = None
        excess_ret_1w = (
            ret_1w - benchmark_ret_1w
            if ret_1w is not None and benchmark_ret_1w is not None
            else None
        )

        signal = price_signal(ret_1w, ret_1m, excess_ret_1w, drawdown, turnover_ratio)

        return {
            "date": current.name.strftime("%Y-%m-%d"),
            "sector": item["sector"],
            "ticker": ticker,
            "name": name,
            "market": market,
            "close": int(current_close),
            "ret_1w": pct(ret_1w),
            "ret_1m": pct(ret_1m),
            "ret_3m": pct(ret_3m),
            "ret_ytd": pct(ret_ytd),
            "benchmark": benchmark_label,
            "benchmark_ret_1w": pct(benchmark_ret_1w),
            "excess_ret_1w": pct(excess_ret_1w),
            "drawdown_52w": pct(drawdown),
            "turnover_value": round(current_turnover) if current_turnover is not None else None,
            "turnover_value_20d_avg": round(avg_turnover) if avg_turnover is not None else None,
            "turnover_ratio_20d": round(turnover_ratio, 2) if turnover_ratio is not None else None,
            "price_signal": signal,
            "error": "",
        }
    except Exception as exc:
        return {
            "date": asof_dt.strftime("%Y-%m-%d"),
            "sector": item["sector"],
            "ticker": ticker,
            "name": item["name"],
            "market": market_lookup.get(ticker, ""),
            "close": None,
            "ret_1w": None,
            "ret_1m": None,
            "ret_3m": None,
            "ret_ytd": None,
            "benchmark": market_lookup.get(ticker, ""),
            "benchmark_ret_1w": None,
            "excess_ret_1w": None,
            "drawdown_52w": None,
            "turnover_value": None,
            "turnover_value_20d_avg": None,
            "turnover_ratio_20d": None,
            "price_signal": "error",
            "error": str(exc),
        }


def build_sector_summary(snapshot_df, asof_dt):
    valid = snapshot_df[snapshot_df["price_signal"] != "error"].copy()
    if valid.empty:
        return pd.DataFrame(
            columns=[
                "date",
                "sector",
                "constituent_count",
                "avg_ret_1w",
                "median_ret_1w",
                "avg_ret_1m",
                "avg_excess_ret_1w",
                "avg_drawdown_52w",
                "overheated_count",
                "extended_count",
                "correction_watch_count",
                "positive_count",
                "negative_count",
                "sector_price_signal",
            ]
        )
    rows = []
    for sector, group in valid.groupby("sector"):
        signals = group["price_signal"].value_counts().to_dict()
        row = {
            "date": asof_dt.strftime("%Y-%m-%d"),
            "sector": sector,
            "constituent_count": len(group),
            "avg_ret_1w": round(group["ret_1w"].mean(), 2),
            "median_ret_1w": round(group["ret_1w"].median(), 2),
            "avg_ret_1m": round(group["ret_1m"].mean(), 2),
            "avg_excess_ret_1w": round(group["excess_ret_1w"].mean(), 2),
            "avg_drawdown_52w": round(group["drawdown_52w"].mean(), 2),
            "overheated_count": signals.get("overheated", 0),
            "extended_count": signals.get("extended", 0),
            "correction_watch_count": signals.get("correction_watch", 0),
            "positive_count": signals.get("positive", 0),
            "negative_count": signals.get("negative", 0),
        }
        row["sector_price_signal"] = sector_price_signal(row)
        rows.append(row)
    return pd.DataFrame(rows).sort_values("sector")


def main():
    parser = argparse.ArgumentParser(description="Collect weekly market snapshot for tracked Korean stocks.")
    parser.add_argument("--date", default=None, help="As-of date in YYMMDD or YYYYMMDD. Defaults to today.")
    parser.add_argument("--stocks", default="stocks.json", help="Path to stocks.json.")
    parser.add_argument("--out-dir", default=str(MARKET_DATA_DIR), help="Output directory.")
    args = parser.parse_args()

    asof_dt = parse_asof_date(args.date)
    os.makedirs(args.out_dir, exist_ok=True)

    items = read_stocks(args.stocks)
    market_lookup = detect_markets(asof_dt)
    benchmark_cache = {}

    rows = []
    for item in items:
        print(f"Collecting {item['sector']} {item['name']} ({item['ticker']})")
        rows.append(collect_one(item, asof_dt, market_lookup, benchmark_cache))

    snapshot_df = pd.DataFrame(rows)
    summary_df = build_sector_summary(snapshot_df, asof_dt)

    prefix = fmt_file_date(asof_dt)
    snapshot_path = os.path.join(args.out_dir, f"{prefix}_market_snapshot.csv")
    summary_path = os.path.join(args.out_dir, f"{prefix}_sector_market_summary.csv")

    snapshot_df.to_csv(snapshot_path, index=False, encoding="utf-8-sig")
    summary_df.to_csv(summary_path, index=False, encoding="utf-8-sig")

    errors = snapshot_df[snapshot_df["price_signal"] == "error"]
    print(f"Saved {snapshot_path}")
    print(f"Saved {summary_path}")
    if not errors.empty:
        print("Rows with errors:")
        print(errors[["sector", "ticker", "name", "error"]].to_string(index=False))


if __name__ == "__main__":
    main()
