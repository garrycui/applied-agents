#!/usr/bin/env python3
"""Grocery Autopilot: learn shopping habits from normalized order history.

Usage: python3 analyze.py orders.json --out ./data [--today YYYY-MM-DD]

orders.json format:
[{"order_id": "...", "date": "YYYY-MM-DD",
  "items": [{"name": "...", "qty": 1, "line_total": 2.29, "unit_price": 2.29,
             "strike_price": null, "image_id": "...", "product_id": null}]}]

Writes:
  staples.csv  items bought 3+ times, with usual gap, last bought, price range, deal share, tier, default setting
  profile.md   a short readable summary of the user's habits
Standard library only.
"""
import argparse
import collections
import csv
import datetime as dt
import json
import os
import statistics as st

# Keyword -> category. Chinese and English; extend for your store.
CATEGORIES = [
    ("fruit", ["梨", "桃", "橘", "柚", "葡萄", "荔枝", "苹果", "芒果", "莓", "西瓜", "香蕉", "柿", "奇异果", "枣", "樱桃",
               "pear", "peach", "mandarin", "orange", "grape", "lychee", "apple", "mango", "berry", "banana", "kiwi"]),
    ("pantry", ["料酒", "酱油", "醋", "蚝油", "豆瓣酱", "辣酱", "拌饭酱", "底料", "大米", "谷米", "粉丝", "花生", "食用油",
                "sauce", "vinegar", "cooking oil", "rice 4", "rice 5", "vermicelli", "peanut", "seasoning"]),
    ("frozen & ready meals", ["饺", "包", "烧麦", "粽", "肠粉", "汤圆", "馄饨", "柴米", "饼",
                              "dumpling", "bun", "shumai", "wonton", "frozen meal"]),
    ("seafood", ["鱼", "虾", "蟹", "鲈", "贝", "鱿", "fish", "shrimp", "crab", "seabass", "squid", "clam"]),
    ("meat", ["猪", "鸡", "牛", "羊", "排骨", "五花", "火腿", "肉", "pork", "chicken", "beef", "lamb", "rib", "ham"]),
    ("tofu, eggs & dairy", ["豆腐", "豆浆", "豆皮", "腐竹", "蛋", "奶", "千页", "豆干", "tofu", "soy milk", "egg", "milk"]),
    ("snacks", ["薯", "胡豆", "虾条", "果丹皮", "饼干", "糖", "巧克力", "瓜子", "海苔", "蛋糕",
                "chips", "cracker", "candy", "chocolate", "cake", "snack"]),
    ("vegetables", ["菜", "葱", "蒜", "姜", "豆角", "豇豆", "茄", "西葫芦", "番茄", "西红柿", "土豆", "笋", "瓜", "芽", "菇",
                    "椒", "玉米", "牛油果", "秋葵", "木耳", "芥兰", "苗", "萝卜", "藕",
                    "choy", "onion", "garlic", "ginger", "bean", "eggplant", "squash", "tomato", "potato", "mushroom",
                    "pepper", "corn", "avocado", "cabbage", "spinach", "radish", "lotus", "sprout"]),
]
PANTRY_GAP_DAYS = 90
STOPPED_DAYS = 150


def category(name):
    low = name.lower()
    for cat, words in CATEGORIES:
        if any(w.lower() in low for w in words):
            return cat
    return "other"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("orders")
    ap.add_argument("--out", default=".")
    ap.add_argument("--today", default=dt.date.today().isoformat())
    a = ap.parse_args()
    today = dt.date.fromisoformat(a.today)
    orders = json.load(open(a.orders, encoding="utf-8"))
    os.makedirs(a.out, exist_ok=True)

    lines = []
    for o in orders:
        d = dt.date.fromisoformat(o["date"])
        for it in o["items"]:
            qty = int(it.get("qty") or 1)
            total = float(it.get("line_total") or 0)
            unit = float(it.get("unit_price") or (total / qty if qty else total))
            key = it.get("product_id") or it.get("image_id") or it["name"]
            lines.append(dict(order=o["order_id"], date=d, name=it["name"], qty=qty, total=total, unit=unit,
                              strike=it.get("strike_price"), key=key, cat=category(it["name"])))
    if not lines:
        raise SystemExit("no items found")

    by_item = collections.defaultdict(list)
    for r in lines:
        by_item[r["key"]].append(r)
    # A purchase counts as "on a deal" if it had a struck-through price or was 10%+ below the highest price paid.
    for rs in by_item.values():
        top = max(r["unit"] for r in rs)
        for r in rs:
            r["deal"] = bool(r["strike"]) or (len(rs) > 1 and r["unit"] < top * 0.9)

    staples = []
    for key, rs in by_item.items():
        dates = sorted({r["date"] for r in rs})
        if len(dates) < 3:
            continue
        gaps = [(b - a).days for a, b in zip(dates, dates[1:])]
        gap = round(st.median(gaps))
        since = (today - dates[-1]).days
        recent = sum(1 for d in dates if (today - d).days <= 180)
        units = [r["unit"] for r in rs]
        deal_share = sum(r["deal"] for r in rs) / len(rs)
        cat = rs[-1]["cat"]
        if since > STOPPED_DAYS:
            tier, setting = "stopped", "never"
        elif cat == "pantry" or gap >= PANTRY_GAP_DAYS:
            tier, setting = "pantry", "pantry"
        elif recent >= 3:
            tier, setting = "core", "auto"
        else:
            tier, setting = "periodic", "deal-only" if deal_share >= 0.6 else "auto"
        staples.append(dict(name=rs[-1]["name"], key=key, category=cat, tier=tier, setting=setting,
                            times=len(dates), usual_gap_days=gap, last_bought=dates[-1].isoformat(),
                            qty=round(st.median([r["qty"] for r in rs])),
                            min_price=round(min(units), 2), median_price=round(st.median(units), 2),
                            max_price=round(max(units), 2), deal_share=round(deal_share, 2), product_id=""))
    order = {"core": 0, "periodic": 1, "pantry": 2, "stopped": 3}
    staples.sort(key=lambda x: (order[x["tier"]], -x["times"]))
    with open(os.path.join(a.out, "staples.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(staples[0].keys()) if staples else ["name"])
        w.writeheader()
        w.writerows(staples)

    # Profile summary
    order_dates = sorted({(r["order"], r["date"]) for r in lines}, key=lambda x: x[1])
    days = sorted({d for _, d in order_dates})
    gap_orders = st.median([(b - a).days for a, b in zip(days, days[1:])]) if len(days) > 1 else None
    per_order = collections.Counter()
    for r in lines:
        per_order[r["order"]] += r["total"]
    cat_n, cat_deal, cat_spend = collections.Counter(), collections.Counter(), collections.Counter()
    for r in lines:
        cat_n[r["cat"]] += 1
        cat_deal[r["cat"]] += r["deal"]
        cat_spend[r["cat"]] += r["total"]
    once = sum(1 for rs in by_item.values() if len({r["date"] for r in rs}) == 1)
    md = ["# Your grocery profile", "",
          f"- {len(per_order)} orders from {days[0]} to {days[-1]}, {len(lines)} line items, {len(by_item)} different products.",
          f"- You order about every {gap_orders} days; median order ${st.median(per_order.values()):.2f}." if gap_orders else "",
          f"- {once} of {len(by_item)} products were bought only once (how much you like to try new things).",
          "", "| Category | Lines | Spend ($) | Bought on a deal |", "|---|---|---|---|"]
    for c, n in cat_spend.most_common():
        md.append(f"| {c} | {cat_n[c]} | {n:,.0f} | {cat_deal[c] / cat_n[c]:.0%} |")
    tiers = collections.Counter(s["tier"] for s in staples)
    md += ["", f"Staples: {tiers['core']} core, {tiers['periodic']} periodic, {tiers['pantry']} pantry (reminder only), "
               f"{tiers['stopped']} you seem to have stopped buying.",
           "", "Stopped buying (check these):"]
    md += [f"- {s['name']} ({s['times']} times, last {s['last_bought']})" for s in staples if s["tier"] == "stopped"][:15]
    open(os.path.join(a.out, "profile.md"), "w", encoding="utf-8").write("\n".join(x for x in md if x is not None) + "\n")
    print(f"wrote {len(staples)} staples to {a.out}/staples.csv and profile.md")


if __name__ == "__main__":
    main()
