---
name: grocery-autopilot
description: Weekly grocery run. Builds this week's list from the user's staples and habits plus this week's real prices (unit-price checked, fake deals skipped, 1-2 new things to try), shows it for approval, then adds it to the online cart. Never checks out. Use when the user says "run grocery autopilot", "make my grocery list", or on their scheduled shopping day.
---

# Grocery Autopilot: weekly run

Talk to the user in their language. If there is no profile yet (no `settings.json` / staples list), run `grocery-autopilot-setup` first.

## Hard rules
- Show the list first. Add to the cart only after the user approves it.
- Never check out, place an order, change address, payment method or account settings.
- Work only in the user's own signed-in browser, at human pace. No private API calls with their session tokens, no CAPTCHA bypassing.
- Keep whatever is already in the cart. Items left from an unplaced previous cart are hints for this week.
- Stay within the budget in `settings.json`.

## Steps
1. Load `settings.json`, the staples list (with each item's setting), `profile.md` and the last entries of `runs.md`.
2. Ask the user in one short message which categories they want this week (e.g. vegetables, meat, snacks) and how last week's "new to try" items were. Start preparing the default list while you wait; if they don't answer, use the default.
3. Following the store adapter:
   - Read orders placed since the last run and update each staple's "last bought" date.
   - Read the current cart.
   - Read current prices from the store's "Buy again" page (price, original price / discount, unit price, stock). Search for anything not there.
   - Glance at the store's deals page for the categories in play.
4. Pick items:
   - Due = days since last bought ≥ 80% of the item's usual gap.
   - `auto`: add when due. `deal-only`: add when due and the price is ≥10% below the user's median price or carries a real discount. `never`: skip. `pantry`: never add; list under "Might be running low?" at the end.
   - Not due but cheaper than the lowest price the user ever paid: may add, marked "lowest price you've seen".
   - **Real-price check:** compare unit prices ($/lb, $/oz), not discount labels. A "deal" whose unit price is still clearly higher (about 20%+) than a comparable non-deal item, or higher than what the user usually pays, is a fake deal: skip it or swap it and say why.
   - If a due item is much pricier than usual this week, prefer a comparable item the user has bought before that is on sale.
   - Add 1–2 **new things to try** (count from settings): something in a brand or category the user buys often, never bought before, on sale and well rated or best-selling. Mark them clearly.
   - If the user named categories, only pick within them.
   - Trim to budget: drop deal-only and nice-to-haves first, then the least overdue.
5. Show the list as a table: item, qty, price, on sale?, vs. their usual price (cheaper / same / pricier), reason. Then: total, free-delivery status, and what you skipped (too pricey, fake deal, out of stock, out of season), and the pantry reminders.
6. When the user approves (with edits), switch the site to their preferred language if the adapter supports it, add each item following the adapter, adjust quantities, then re-read the cart and report items, quantities and total. Watch for minimum quantities (e.g. "2-pack minimum") and include them in the total. Tell them the cart is ready for them to check out.
7. Learn from feedback: if the user says "never buy X", "X isn't weekly", "more variety", update the staples list or settings immediately. Append to `runs.md`: date, item count, total, new tries, feedback.
