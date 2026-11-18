# Adding a new store

Copy this into `adapters/<store>/README.md` and fill it in while the user watches in their signed-in browser. Keep the same four capabilities so the skills work unchanged.

1. **Order history**: URL of the orders list, how pagination and date filters work, URL pattern of an order detail page, and how to read each item's name, quantity, paid price, struck-through (original) price and a stable id (product id or image id).
2. **Current prices**: the best page to read the user's past products with today's prices (a "buy again" page if the store has one), plus the deals and search pages. Note where unit prices ($/lb, $/oz) appear.
3. **Add to cart**: product page URL pattern, which button adds the main product, how to change quantity, and any minimum-quantity rules.
4. **Cart**: URL, how to read items, quantities and the subtotal.

Rules for every adapter:
- Read and click pages like a person, at human pace, in the user's own session.
- Don't call private APIs with the user's tokens, and don't bypass CAPTCHAs or bot checks.
- Never check out or place orders.
- Write down what you tested and when. Add helpers in `adapters/<store>/extract.js` if they help.
- Note that the plugin isn't affiliated with the store and the user is responsible for its terms.
