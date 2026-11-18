# Weee! adapter

Notes for driving weee.com (also sayweee.com) in the user's signed-in browser. Tested November 2026; site layouts change, so re-check if something stops matching.

Not affiliated with Weee! Inc. The user is responsible for following Weee!'s terms of service.

## URLs
| What | URL |
|---|---|
| Orders list | `https://www.weee.com/en/account/my_orders?page_no=<n>&period=<p>` |
| Order detail | `https://www.weee.com/en/order/detail/<order_id>` |
| Cart | `https://www.weee.com/<lang>/cart` |
| Buy again (past products with current prices) | `https://www.weee.com/<lang>/account/buy_again` |
| Deals | `https://www.weee.com/<lang>/category/sale?filter_sub_category=sale` |
| Search | `https://www.weee.com/<lang>/search?keyword=<query>` |
| Product page | `https://www.weee.com/<lang>/product/x/<product_id>` |

`<lang>` is `en` or `zh` (Simplified Chinese). Switch language with the language control in the header; the user's choice decides what the cart shows.

`period` on the orders list: 1 = last 30 days, 2 = 3 months, 3 = 6 months, 4 = current year, 5 = previous year, and so on. Ten orders per page.

## Reading order history
1. Open the orders list with the year filter and run `listOrders()` from `extract.js` on each page. It returns `{date, id, items, total, status}` per order.
2. Run `scrapeOrderDetails(ids)` from `extract.js` on any weee.com page. It opens each order detail page in a hidden frame, reads the items (name, unit price, qty, struck-through price, image id) and returns them. Do batches of about 20 orders.
3. Check the per-order item counts against the list page; re-run any order that came back short.
4. Order detail item names come out in the account's language (often Chinese), which matches the cart and buy-again pages when the site is in the same language.

The "Details" button on the orders list may not navigate when a survey banner covers it; open the detail URL directly instead.

## Current prices
Open Buy again, scroll to the bottom (about 60 items load), and run `readProductCards()` from `extract.js`. Each card gives product id, price, original price and discount %, unit price, and labels such as "everyday value". The same function works on search and deals pages.

## Adding to the cart
On a product page the first "加入购物车" / "Add to cart" button belongs to the product itself; the rest are recommendations. `addToCart(productIds)` in `extract.js` opens each product page in a hidden frame and clicks that first button. Raise quantities on the cart page with the "+" next to the item.

Some items are sold in a minimum of two ("2件起卖"): the cart sets the quantity to 2 automatically. Include that in the total.

## Things that don't work (on purpose)
Calling Weee's private JSON endpoints with the user's session token is blocked by Claude's safety checks, and the skill shouldn't do it anyway. Everything here reads and clicks pages the way the user would.
