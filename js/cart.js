/**
 * Carrinho flutuante - Animacase
 * Promo: Frete grátis (1) | 1 GRÁTIS ao levar 3 (3º) | 2 GRÁTIS ao levar 5 (3º e 5º)
 * Estrutura pronta para order bumpers no futuro.
 */
(function () {
  // Script de UTMs Utmify (carregado uma única vez)
  try {
    if (!window.__utmifyUtmsLoaded) {
      window.__utmifyUtmsLoaded = true;
      var u = document.createElement("script");
      u.setAttribute("src", "https://cdn.utmify.com.br/scripts/utms/latest.js");
      u.setAttribute("data-utmify-prevent-xcod-sck", "");
      u.setAttribute("data-utmify-prevent-subids", "");
      u.setAttribute("async", "");
      u.setAttribute("defer", "");
      (document.head || document.documentElement).appendChild(u);
    }
  } catch (e) {}
  const STORAGE_KEY = 'animacase_cart';
  const PRICE_SALE = 34.90;
  const PRICE_REGULAR = 47.90;

  function getCart() {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    } catch {
      return [];
    }
  }

  function saveCart(items) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
    updateCartUI();
  }

  function parsePrice(val) {
    if (typeof val === 'number') return val;
    const n = String(val || '').replace(/[^\d,]/g, '').replace(',', '.');
    return parseFloat(n) || PRICE_SALE;
  }

  function formatPrice(n) {
    return 'R$ ' + n.toFixed(2).replace('.', ',');
  }

  function getItemPrice(item) {
    return parsePrice(item?.priceSale) || PRICE_SALE;
  }

  /** Formata o variant (ex: "iphone-iphone-17-pro-max") para exibição: "Modelo: iPhone 17 Pro Max" */
  function formatVariantDisplay(variant) {
    if (!variant || typeof variant !== 'string') return '';
    const raw = variant.trim();
    if (!raw) return '';
    const brands = { iphone: 'iPhone', samsung: 'Samsung', motorola: 'Motorola', xiaomi: 'Xiaomi' };
    if (raw.indexOf('-') !== -1) {
      const parts = raw.split('-');
      const brandKey = parts[0] && parts[0].toLowerCase();
      const brandLabel = brands[brandKey] || (parts[0].charAt(0).toUpperCase() + parts[0].slice(1).toLowerCase());
      const rest = (parts[0] === parts[1] ? parts.slice(2) : parts.slice(1))
        .map(function (w) {
          if (/^\d+$/.test(w)) return w;
          return w.charAt(0).toUpperCase() + w.slice(1).toLowerCase();
        })
        .join(' ');
      return rest ? (brandLabel + ' ' + rest).trim() : brandLabel;
    }
    return raw;
  }

  /** Desconto promo: 3º grátis ao ter 3+, 5º grátis ao ter 5+ */
  function getPromoDiscount(items) {
    const total = items.length;
    if (total < 3) return 0;
    let discount = 0;
    if (total >= 3) discount += getItemPrice(items[2]);
    if (total >= 5) discount += getItemPrice(items[4]);
    return discount;
  }

  function getSubtotal(items) {
    const sum = items.reduce((acc, i) => acc + getItemPrice(i), 0);
    return sum - getPromoDiscount(items);
  }

  /** Níveis: 0 nenhum, 1 frete grátis, 2 = 1 grátis, 3 = 2 grátis */
  function getProgress(items) {
    const n = items.length;
    let nextMsg;
    if (n < 1) nextMsg = 'Adicione 1 para ganhar frete grátis!';
    else if (n < 3) nextMsg = n === 2 ? 'A próxima capa será GRÁTIS!' : 'Adicione mais 2 para ganhar 1 GRÁTIS!';
    else if (n < 5) nextMsg = 'Adicione mais ' + (5 - n) + ' para ganhar 2 GRÁTIS!';
    else nextMsg = 'Você desbloqueou todas as promoções!';
    return {
      level: n >= 5 ? 3 : n >= 3 ? 2 : n >= 1 ? 1 : 0,
      nextMsg: nextMsg
    };
  }

  function escapeAttr(str) {
    if (str == null) return '';
    return String(str).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');
  }

  function createCartDrawer() {
    const html = `
      <div class="cart-drawer__overlay" id="cart-overlay" aria-hidden="true"></div>
      <aside class="cart-drawer" id="cart-drawer" role="dialog" aria-label="Carrinho" aria-hidden="true">
        <div class="cart-drawer__inner">
          <header class="cart-drawer__header">
            <h2 class="cart-drawer__title">Meu carrinho <span class="cart-drawer__count" id="cart-count-label">• 0 itens</span></h2>
            <button type="button" class="cart-drawer__close" id="cart-close" aria-label="Fechar">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 18 17" width="20" height="20"><path d="M.865 15.978a.5.5 0 00.707.707l7.433-7.431 7.579 7.282a.501.501 0 00.846-.37.5.5 0 00-.153-.351L9.712 8.546l7.417-7.416a.5.5 0 10-.707-.708L8.991 7.853 1.413.573a.5.5 0 10-.693.72l7.563 7.268-7.418 7.417z" fill="currentColor"/></svg>
            </button>
          </header>

          <div class="cart-drawer__promo-area">
            <div class="cart-drawer__progress" id="cart-progress-wrap">
              <p class="cart-drawer__progress-msg" id="cart-progress-msg">Adicione 1 para ganhar frete grátis!</p>
              <div class="cart-drawer__progress-bar">
                <div class="cart-drawer__progress-fill" id="cart-progress-fill"></div>
                <span class="cart-drawer__progress-dot cart-drawer__progress-dot--1" data-level="1"></span>
                <span class="cart-drawer__progress-dot cart-drawer__progress-dot--2" data-level="2"></span>
                <span class="cart-drawer__progress-dot cart-drawer__progress-dot--3" data-level="3"></span>
              </div>
              <div class="cart-drawer__progress-labels">
                <span data-level="1">Frete grátis 🚚</span>
                <span data-level="2">1 GRÁTIS 🎁</span>
                <span data-level="3">2 GRÁTIS 🎁</span>
              </div>
            </div>
          </div>

          <div class="cart-drawer__items-wrap">
            <ul class="cart-drawer__items" id="cart-items-list"></ul>
          </div>

          <section class="cart-drawer__recommendations cart-drawer__recommendations--hidden" id="cart-recommendations-section" aria-hidden="true">
            <h3>Leve um quadro do seu anime favorito!</h3>
            <div class="cart-recommendation">
              <div class="cart-recommendation__track" id="cart-recommendation-track">
                <!-- Order bumpers serão injetados aqui no futuro -->
                <div class="cart-recommendation__slide cart-recommendation__placeholder">
                  <div class="cart-recommendation__info" style="flex:1;">
                    <p style="font-size:0.875rem;color:#6b7280;">Em breve: sugestões de quadros e acessórios aqui.</p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <footer class="cart-drawer__footer">
            <div class="cart-drawer__discount" id="cart-discount-row" style="display:none">
              <span>Descontos promo</span>
              <span id="cart-discount-value">-R$ 0,00</span>
            </div>
            <div class="cart-drawer__subtotal">
              <span>Subtotal</span>
              <span id="cart-subtotal-value">R$ 0,00</span>
            </div>
            <button type="button" class="cart-drawer__checkout" id="cart-checkout">Finalizar Compra</button>
          </footer>
        </div>
      </aside>
    `;
    const wrap = document.createElement('div');
    wrap.innerHTML = html;
    document.body.appendChild(wrap.firstElementChild);
    document.body.appendChild(wrap.lastElementChild);
  }

  function renderCartItems(items) {
    const list = document.getElementById('cart-items-list');
    if (!list) return;

    if (items.length === 0) {
      list.innerHTML = '<li class="cart-drawer__empty">Seu carrinho está vazio. Adicione capinhas!</li>';
      return;
    }

    list.innerHTML = items.map((item, i) => {
      const isFree = i === 2 || i === 4;
      const priceSale = getItemPrice(item);
      const priceRegular = parsePrice(item.priceRegular);
      const singlePrice = priceSale === priceRegular;
      const priceHtml = isFree
        ? '<span class="cart-drawer__item-free">Grátis</span>'
        : singlePrice
          ? '<span>' + formatPrice(priceSale) + '</span>'
          : '<span>' + formatPrice(priceSale) + '</span><s>' + formatPrice(priceRegular) + '</s>';
      const variantRaw = item.variant ? String(item.variant).trim() : '';
      const variantLabel = variantRaw ? ('Modelo: ' + formatVariantDisplay(variantRaw)) : 'Capa Refletiva 3M';
      return (
        '<li class="cart-drawer__item" data-id="' + escapeAttr(item.id) + '">' +
          '<img src="' + escapeAttr(item.image) + '" alt="' + escapeAttr(item.name) + '" class="cart-drawer__item-img">' +
          '<div class="cart-drawer__item-info">' +
            '<h4>' + escapeAttr(item.name) + '</h4>' +
            '<p class="cart-drawer__item-variant">' + escapeAttr(variantLabel) + '</p>' +
            '<div class="cart-drawer__item-price">' + priceHtml + '</div>' +
          '</div>' +
          '<button type="button" class="cart-drawer__item-remove" data-id="' + escapeAttr(item.id) + '" aria-label="Remover"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2m3 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6h14z"/><path d="M10 11v6M14 11v6"/></svg></button>' +
        '</li>'
      );
    }).join('');

    list.querySelectorAll('.cart-drawer__item-remove').forEach(btn => {
      btn.addEventListener('click', () => removeFromCart(btn.dataset.id));
    });
  }

  function updateCartUI() {
    const items = getCart();

    const countEls = document.querySelectorAll('.cart-count');
    countEls.forEach(el => {
      el.textContent = items.length;
      el.style.display = items.length ? 'flex' : 'none';
      el.setAttribute('aria-hidden', items.length ? 'false' : 'true');
    });

    const label = document.getElementById('cart-count-label');
    if (label) label.textContent = '• ' + items.length + (items.length === 1 ? ' item' : ' itens');

    const progress = getProgress(items);
    const fill = document.getElementById('cart-progress-fill');
    const msg = document.getElementById('cart-progress-msg');
    if (msg) msg.textContent = progress.nextMsg;
    if (fill) fill.style.width = (progress.level / 3 * 100) + '%';
    document.querySelectorAll('.cart-drawer__progress-dot').forEach(dot => {
      const l = parseInt(dot.dataset.level, 10);
      dot.classList.toggle('is-unlocked', progress.level >= l);
    });
    document.querySelectorAll('.cart-drawer__progress-labels span').forEach((span, i) => {
      const l = i + 1;
      span.classList.toggle('is-unlocked', progress.level >= l);
    });

    const discount = getPromoDiscount(items);
    const subtotal = getSubtotal(items);
    const discountRow = document.getElementById('cart-discount-row');
    const discountVal = document.getElementById('cart-discount-value');
    const subtotalVal = document.getElementById('cart-subtotal-value');
    const checkoutBtn = document.getElementById('cart-checkout');

    if (discountRow) discountRow.style.display = discount > 0 ? 'flex' : 'none';
    if (discountVal) discountVal.textContent = '-' + formatPrice(discount);
    if (subtotalVal) subtotalVal.textContent = formatPrice(subtotal);
    if (checkoutBtn) checkoutBtn.textContent = 'Finalizar Compra';

    renderCartItems(items);
  }

  function openCart() {
    const drawer = document.getElementById('cart-drawer');
    const overlay = document.getElementById('cart-overlay');
    if (drawer) { drawer.classList.add('is-open'); drawer.setAttribute('aria-hidden', 'false'); }
    if (overlay) { overlay.classList.add('is-visible'); overlay.setAttribute('aria-hidden', 'false'); }
    document.body.style.overflow = 'hidden';
  }

  function closeCart() {
    const drawer = document.getElementById('cart-drawer');
    const overlay = document.getElementById('cart-overlay');
    if (drawer) { drawer.classList.remove('is-open'); drawer.setAttribute('aria-hidden', 'true'); }
    if (overlay) { overlay.classList.remove('is-visible'); overlay.setAttribute('aria-hidden', 'true'); }
    document.body.style.overflow = '';
  }

  /** Adicionar ao carrinho (chamado pelas PDPs ou botões). */
  function addToCart(product) {
    const items = getCart();
    const id = 'item_' + Date.now() + '_' + Math.random().toString(36).slice(2);
    const item = {
      id,
      name: product.name || 'Capa Refletiva 3M',
      image: product.image || '',
      url: product.url || '',
      priceSale: product.priceSale != null ? parsePrice(product.priceSale) : PRICE_SALE,
      priceRegular: product.priceRegular != null ? parsePrice(product.priceRegular) : PRICE_REGULAR,
      variant: product.variant || null
    };
    items.push(item);
    saveCart(items);
    openCart();
  }

  function removeFromCart(id) {
    const items = getCart().filter(i => i.id !== id);
    saveCart(items);
  }

  function init() {
    createCartDrawer();
    updateCartUI();

    const cartIcon = document.querySelector('#cart-toggle, a[href="/cart"]');
    if (cartIcon) {
      cartIcon.addEventListener('click', function (e) {
        e.preventDefault();
        openCart();
      });
      if (cartIcon.tagName === 'A') cartIcon.setAttribute('href', '#');
    }

    document.getElementById('cart-close')?.addEventListener('click', closeCart);
    document.getElementById('cart-overlay')?.addEventListener('click', closeCart);
    document.getElementById('cart-checkout')?.addEventListener('click', function () {
      const items = getCart();
      if (items.length === 0) return;
      var path = window.location.pathname || '';
      var checkoutUrl = (path.indexOf('/produto/') !== -1 || path.indexOf('/animes/') !== -1) ? '../checkout.html' : 'checkout.html';
      window.location.href = checkoutUrl;
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeCart();
    });
  }

  window.animacaseCart = {
    addToCart: addToCart,
    getCart: getCart,
    openCart: openCart,
    closeCart: closeCart
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
