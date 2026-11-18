---
name: grocery-autopilot-setup
description: First-time setup for Grocery Autopilot. Reads the user's own past grocery orders in their logged-in browser, learns what they buy and how often, and creates their personal staples list and settings. Use when the user says "set up grocery autopilot" or runs the weekly skill without a profile.
---

# Grocery Autopilot: first-time setup

Goal: turn the user's own order history into a personal profile that the weekly skill uses. Talk to the user in their language.

## What you need
- A browser you can drive where the user is already signed in to their grocery site: Claude in Chrome, or the built-in browser of the Claude desktop app. If neither is available, say so and stop.
- A store adapter in `../../adapters/<store>/`. Ask which store they use. Today only `weee` exists; for another store, follow `../../adapters/TEMPLATE.md` with the user first.

## Where the user's data lives
Personal data never goes into this plugin's folder or any repository. Ask the user where to keep it and tell them what you chose:
- Claude Code: a local folder, default `~/grocery-autopilot/` (files: `orders.json`, `staples.csv`, `profile.md`, `settings.json`, `runs.md`).
- claude.ai / Cowork: Project documents with the same names, or an editable doc/sheet for the staples list.

## Steps
1. Ask (one message): which store; budget cap per order; which weekday to shop (many stores have weekly deals); language for the cart and list; how many "new things to try" per week (default 1–2); anything they never buy.
2. Open the store in the browser and confirm the user is signed in. If not, ask them to sign in themselves. Never type passwords.
3. Collect order history following the adapter's `README.md` (default: last 12–18 months). Use the adapter's extraction script by running it in the page. Read at human pace, one page at a time. Do not call the site's private APIs with the user's session tokens.
4. Save the normalized orders to `orders.json`:
   `[{"order_id": "...", "date": "YYYY-MM-DD", "items": [{"name": "...", "qty": 1, "line_total": 2.29, "unit_price": 2.29, "strike_price": null, "image_id": "...", "product_id": null}]}]`
5. Run `python3 ../../scripts/analyze.py orders.json --out <data folder>` (or do the same calculation yourself if you cannot run Python). It writes `staples.csv` and `profile.md`.
6. Show the user a short summary from `profile.md`: order frequency, typical basket, categories they are price-sensitive in, brands they are loyal to, items they stopped buying. Ask them to correct anything wrong.
7. Turn `staples.csv` into their editable staples list. Every item gets one setting: `auto` (add when due), `deal-only` (add when due and on a real discount), or `never`. Defaults: core items `auto`; price-sensitive or seasonal items `deal-only`; items not bought in 5+ months `never`. Pantry items (sauces, oils, rice, dry goods, or a usual gap of 90+ days) are marked `pantry`: they are only ever reminded, never auto-added.
8. Map staples to the store's product IDs using the adapter (usually its "Buy again" page), and save the mapping in `staples.csv`.
9. Write `settings.json` with the answers from step 1 and the data locations.
10. Offer to schedule a weekly run on their shopping day if their Claude app supports scheduled tasks. The scheduled prompt should invoke the `grocery-autopilot` skill and point to the data folder.

Finish with one line: where the profile lives and how to run the weekly list ("run grocery autopilot").
