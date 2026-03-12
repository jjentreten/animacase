#!/usr/bin/env python3
"""Aplica o header global (igual à home) em todas as páginas de produto."""
import re
import os

PRODUTO_DIR = os.path.join(os.path.dirname(__file__), '..', 'produto')

# Bloco CSS a remover (desde HEADER até antes de PDP CONTENT)
CSS_HEADER_START = re.compile(
    r'\s*/\* =+ HEADER \(igual à home[^*]*\*/\s*'
    r'\s*\.announcement-bar \{[^}]+\}[^}]*(?:\}[^}]*)*\s*'
    r'(?:\s*/\* Barra de oferta[^*]*\*/\s*\.header-promo \{[^}]+\}[^*]*)*'
    r'\s*\.header \{[^}]+\}',
    re.DOTALL
)

# Marca início e fim do bloco CSS a remover
CSS_START = '    /* ========== HEADER (igual à home'
CSS_END = '    /* ========== PDP CONTENT ========== */'

REPLACEMENT_CSS = '''    .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 0 16px;
    }

    '''

# HTML do header global para produto (com paths ../)
HEADER_HTML = '''  <!-- Header global (igual à home) -->
  <div class="header-sticky" id="header-sticky">
    <div class="header-promo" role="status" aria-live="polite">
      <span class="header-promo__icon" aria-hidden="true">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 2"/></svg>
      </span>
      <span class="header-promo__text">Essa oferta termina em <strong class="header-promo__timer js-offer-timer">15:00</strong></span>
    </div>
    <header class="header">
      <div class="container header__container">
        <div class="header__nav">
          <div class="header__nav-left">
            <a href="#" rel="nofollow" aria-label="Menu" class="header__item header__item--hamburger header__item--mobile">
              <div class="icon-hamburger">
                <span class="icon-hamburger__lines"></span>
              </div>
            </a>
          </div>
          <div class="header__nav-center">
            <a href="../index.html" aria-label="Home" class="header__item header__item--logo header__item--logo-sudden">
              <div class="logo__wrapper">
                <img src="../assets/logoanimacase-deitado.png" alt="animacase." class="logo logo--img" width="160" height="45" loading="eager">
              </div>
            </a>
          </div>
          <div class="header__nav-right">
            <a href="../checkout.html" aria-label="Conta" class="header__item header__item--icon user-widget__icon">
              <svg viewBox="0 0 24 24" width="24" height="24"><path fill="currentColor" d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
            </a>
            <a href="../checkout.html" id="cart-toggle" aria-label="Carrinho" class="header__item header__item--icon">
              <div class="cart-widget">
                <span class="cart-count" id="cart-count-badge" aria-hidden="true" style="display:none">0</span>
                <svg viewBox="0 0 24 24" width="24" height="24"><g fill="currentColor"><path d="M19 6h-2c0-2.76-2.24-5-5-5S7 3.24 7 6H5c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm-7-3c1.66 0 3 1.34 3 3H9c0-1.66 1.34-3 3-3zm7 16H5V8h2v2c0 .55.45 1 1 1s1-.45 1-1V8h6v2c0 .55.45 1 1 1s1-.45 1-1V8h2v11z"/></g></svg>
              </div>
            </a>
          </div>
        </div>
        <div class="header__search" id="header-search">
          <div class="search-wrapper">
            <input type="search" class="search-input" placeholder="O que você está procurando?" aria-label="Pesquisar">
            <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/>
              <path d="m21 21-4.35-4.35"/>
            </svg>
          </div>
        </div>
      </div>
    </header>
  </div>

  <main class="pdp">'''

# Padrão do body: desde <body> até <main class="pdp">
BODY_OLD_PATTERN = re.compile(
    r'<body>\s*'
    r'<!-- Cronômetro de oferta[^>]*>.*?</div>\s*'
    r'<!-- \(A\) ANNOUNCEMENT BAR[^>]*>.*?</div>\s*'
    r'<!-- \(B\)\(C\) HEADER[^>]*>.*?'
    r'</header>\s*'
    r'<main class="pdp">',
    re.DOTALL
)

SCROLL_SCRIPT = '''  <script>
  (function(){ var h=document.getElementById('header-sticky'); if(!h)return; function up(){ h.classList.toggle('is-scrolled', window.scrollY>60); }
  window.addEventListener('scroll',function(){ requestAnimationFrame(up); },{passive:true}); up(); })();
  </script>
  '''

def process_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    orig = content

    # Já tem header global?
    if 'header-sticky' in content and 'id="header-sticky"' in content:
        return False, 'already done'

    # 1) Adicionar link header-global.css
    if 'header-global.css' not in content:
        content = content.replace(
            '<link rel="stylesheet" href="../css/cart.css">',
            '<link rel="stylesheet" href="../css/cart.css">\n  <link rel="stylesheet" href="../css/header-global.css">'
        )

    # 2) Remover bloco CSS do header (entre HEADER e PDP CONTENT)
    if CSS_START in content and CSS_END in content:
        start = content.index(CSS_START)
        end = content.index(CSS_END)
        content = content[:start] + REPLACEMENT_CSS + content[end:]

    # 3) Substituir bloco HTML do body
    content = BODY_OLD_PATTERN.sub('<body>\n' + HEADER_HTML, content)

    # 4) Adicionar scroll script antes de cart.js (se ainda não tiver)
    if 'header-sticky' in content and 'is-scrolled' not in content:
        content = content.replace(
            '<script src="../js/offer-timer.js"></script>\n  <script src="../js/cart.js"></script>',
            '<script src="../js/offer-timer.js"></script>\n' + SCROLL_SCRIPT + '  <script src="../js/cart.js"></script>'
        )

    if content != orig:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, 'updated'
    return False, 'no change'

def main():
    updated = 0
    for name in sorted(os.listdir(PRODUTO_DIR)):
        if not name.endswith('.html'):
            continue
        path = os.path.join(PRODUTO_DIR, name)
        try:
            changed, msg = process_file(path)
            if changed:
                updated += 1
                print(name, msg)
        except Exception as e:
            print(name, 'ERROR', e)
    print('Total updated:', updated)

if __name__ == '__main__':
    main()
