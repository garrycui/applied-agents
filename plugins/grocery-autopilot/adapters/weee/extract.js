// Grocery Autopilot: Weee! page helpers.
// Paste a function into the page (via the browser tool's JavaScript runner) on a weee.com tab
// where the user is signed in, then call it. Everything reads or clicks pages the way a person would.

// 1) On an orders-list page: returns [{date, id, items, total, status}]
function listOrders() {
  const t = document.body.innerText;
  const re = /(?:Delivery date|送达日期|配送日期)\n(.+?)\n(?:Order number|订单号)\n(\d+)\n(?:Items|商品)\n(\d+)\n(?:Total|总计|合计)\n\$([\d.,]+)\n([^\n]+)/g;
  const out = [];
  let m;
  while ((m = re.exec(t))) out.push({ date: m[1], id: m[2], items: +m[3], total: m[4], status: m[5].trim() });
  return out;
}

// Opens a same-origin page in a hidden frame and waits until `ready(doc)` is true.
async function withFrame(path, ready, timeoutMs = 16000) {
  const f = document.createElement('iframe');
  f.style.cssText = 'position:fixed;left:-5000px;width:1300px;height:900px';
  f.src = path;
  document.body.appendChild(f);
  let doc = null;
  for (let waited = 0; waited < timeoutMs; waited += 400) {
    await new Promise(r => setTimeout(r, 400));
    try { doc = f.contentDocument; if (doc && ready(doc)) break; } catch (e) { /* not ready */ }
  }
  await new Promise(r => setTimeout(r, 800));
  return { f, doc };
}

// 2) Reads order detail pages. Returns {order_id: {order_date, items: [{name, line_total, qty, strike_price, image_id}]}}
async function scrapeOrderDetails(ids) {
  const result = {};
  for (const id of ids) {
    const { f, doc } = await withFrame('/en/order/detail/' + id,
      d => d.querySelector('[data-testid="wid-order-detail-product-item"]'));
    const items = [...(doc?.querySelectorAll('[data-testid="wid-order-detail-product-item"]') || [])].map(e => {
      const g = s => e.querySelector('[data-testid="' + s + '"]')?.innerText.trim() || '';
      const strike = e.querySelector('.line-through');
      const img = (e.querySelector('img')?.src.match(/image\/(.+?)!/) || [])[1] || '';
      return {
        name: g('wid-order-detail-product-title'),
        line_total: parseFloat(g('wid-order-detail-product-actual-price-value').replace(/[$,]/g, '')) || 0,
        qty: parseInt(g('wid-order-detail-product-quantity').replace(/\D/g, ''), 10) || 1,
        strike_price: strike ? parseFloat(strike.innerText.replace(/[$,]/g, '')) : null,
        image_id: img
      };
    });
    const text = doc?.body?.innerText || '';
    result[id] = { order_date: (text.match(/(?:Order date|下单日期)\n(.+)/) || [])[1] || null, items };
    f.remove();
  }
  return result;
}

// 3) On buy-again, search or deals pages (scroll to the bottom first):
//    returns [{product_id, text}] where text holds price, original price, discount, unit price, name, labels.
function readProductCards() {
  const seen = new Set();
  const out = [];
  for (const a of document.querySelectorAll('a[href*="/product/"]')) {
    const id = (a.getAttribute('href').match(/\/(\d+)(\?|$)/) || [])[1];
    if (!id || seen.has(id)) continue;
    seen.add(id);
    let card = a;
    for (let k = 0; k < 6 && card && !/加入购物车|Add to cart/.test(card.innerText); k++) card = card.parentElement;
    const text = (card?.innerText || '').replace(/\n(SNAP|EBT|加入购物车|Add to cart)/g, '').replace(/\n/g, ' | ');
    out.push({ product_id: id, text });
  }
  return out;
}

// 4) Adds products to the cart (quantity 1 each; raise quantities on the cart page).
//    Only call this after the user approved the list.
async function addToCart(productIds, lang = 'zh') {
  const log = [];
  for (const id of productIds) {
    const isAdd = b => /^(加入购物车|Add to cart)$/.test(b.innerText.trim());
    const { f, doc } = await withFrame('/' + lang + '/product/x/' + id,
      d => [...d.querySelectorAll('button')].some(isAdd));
    const btn = doc && [...doc.querySelectorAll('button')].find(isAdd);
    const title = (doc?.title || '').replace(' - Weee!', '');
    if (btn) { btn.click(); await new Promise(r => setTimeout(r, 1800)); log.push(id + ' added: ' + title); }
    else log.push(id + ' NOT added (no button, maybe sold out): ' + title);
    f.remove();
  }
  return log.join('\n');
}
