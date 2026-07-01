#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор статей блога Fanline.su.
Каждая статья — единая разметка (Schema.org @graph, шапка, подвал, FAQ .faq-section).
CTA-кнопки содержат data-product="KEY" и href="#" — плейсхолдеры под партнёрские
ссылки Яндекс.Маркета, которые подставляются массово позже.

Запуск:  python3 blog/_build_blog.py
Файлы пишутся в каталог blog/.
"""
import os, html, json, datetime

OUT = os.path.dirname(os.path.abspath(__file__))
DATE = "2026-06-20"

# ------------------------------------------------------------------ helpers
def esc(s):
    return html.escape(s, quote=True)

def cta(title, intro, buttons, note="Цены и наличие — на Яндекс.Маркете. Ссылки партнёрские."):
    """buttons: список (label, product_key, secondary?)"""
    btns = []
    for b in buttons:
        label = b[0]; key = b[1]; sec = b[2] if len(b) > 2 else False
        cls = "cta-btn cta-btn-secondary" if sec else "cta-btn"
        btns.append(
            f'          <a class="{cls}" data-product="{esc(key)}" href="#" '
            f'rel="sponsored nofollow noopener" target="_blank">{esc(label)}</a>'
        )
    grid = "\n".join(btns)
    return f"""      <div class="cta-block">
        <p class="cta-block__title">{esc(title)}</p>
        <p class="cta-block__intro">{esc(intro)}</p>
        <div class="cta-grid">
{grid}
        </div>
        <p class="cta-note">{esc(note)}</p>
      </div>"""

def faq_html(items):
    rows = []
    for q, a in items:
        rows.append(f"""        <details>
          <summary>{esc(q)}<svg class="faq-icon" aria-hidden="true"><use href="#icon-plus"/></svg></summary>
          <div class="faq-body"><p>{a}</p></div>
        </details>""")
    inner = "\n".join(rows)
    return f"""      <h2 id="faq">Частые вопросы</h2>
      <div class="faq-section">
{inner}
      </div>"""

def faq_schema(items):
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": _strip(a)}}
            for q, a in items
        ]
    }

def _strip(s):
    import re
    return re.sub(r"<[^>]+>", "", s).replace("&nbsp;", " ").strip()

def sidebar(blocks):
    out = []
    for h, links in blocks:
        lis = "\n".join(f'          <li><a href="{href}">{esc(t)}</a></li>' for t, href in links)
        out.append(f"""      <div class="sidebar-block">
        <h3>{esc(h)}</h3>
        <ul>
{lis}
        </ul>
      </div>""")
    return "\n".join(out)

FOOTER = """<footer class="site-footer">
  <div class="footer-inner">
    <div class="footer-col">
      <h3>Дача и огород</h3>
      <ul>
        <li><a href="/blog/">Все статьи блога</a></li>
        <li><a href="/blog/kak-vyrastit-pomidory-v-teplice.html">Помидоры в теплице</a></li>
        <li><a href="/blog/kak-vyrastit-ogurcy-v-teplice.html">Огурцы в теплице</a></li>
        <li><a href="/blog/poliv-i-provetrivanie.html">Полив и проветривание</a></li>
      </ul>
    </div>
    <div class="footer-col">
      <h3>Монтаж</h3>
      <ul>
        <li><a href="/montazh/kak-sobrat-teplicu-iz-polikarbonata.html">Как собрать теплицу</a></li>
        <li><a href="/montazh/kak-sdelat-fortochku-v-teplice.html">Форточка в теплице</a></li>
        <li><a href="/montazh/uhod-za-teplitsey-zimoy.html">Уход за теплицей зимой</a></li>
      </ul>
    </div>
    <div class="footer-col">
      <h3>Выбор поликарбоната</h3>
      <ul>
        <li><a href="/vybor/kakoy-polikarbonat-vybrat-dlya-teplicy.html">Какой поликарбонат выбрать</a></li>
        <li><a href="/vybor/tolschina-polikarbonata-dlya-teplicy.html">Толщина поликарбоната</a></li>
        <li><a href="/karta-sajta.html">Карта сайта</a></li>
      </ul>
    </div>
  </div>
  <div class="footer-bottom">
    <p>© 2026 Fanline.su &nbsp;·&nbsp; <a href="/politika-konfidentsialnosti.html">Политика конфиденциальности</a></p>
  </div>
</footer>"""

METRIKA = """  <!-- Yandex.Metrika counter -->
  <script type="text/javascript">
     (function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
     m[i].l=1*new Date();
     for (var j = 0; j < document.scripts.length; j++) {if (document.scripts[j].src === r) { return; }}
     k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)})
     (window, document, "script", "https://mc.yandex.ru/metrika/tag.js", "ym");

     ym(110303165, "init", {
          clickmap:true,
          trackLinks:true,
          accurateTrackBounce:true,
          webvisor:true
     });
  </script>
  <noscript><div><img src="https://mc.yandex.ru/watch/110303165" style="position:absolute; left:-9999px;" alt="" /></div></noscript>
  <!-- /Yandex.Metrika counter -->"""

ICON_SPRITE = """<svg style="display:none" aria-hidden="true">
  <defs>
    <symbol id="icon-plus" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
      <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
    </symbol>
    <symbol id="icon-minus" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
      <line x1="5" y1="12" x2="19" y2="12"/>
    </symbol>
  </defs>
</svg>"""

def build(slug, title, h1, desc, og_desc, body, faq_items, side, howto=None):
    url = f"https://fanline.su/blog/{slug}.html"
    graph = [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": "https://fanline.su/"},
            {"@type": "ListItem", "position": 2, "name": "Дача и огород", "item": "https://fanline.su/blog/"},
            {"@type": "ListItem", "position": 3, "name": h1, "item": url},
        ]},
        {"@type": "Article", "headline": h1, "description": _strip(og_desc),
         "author": {"@type": "Organization", "name": "Fanline.su"},
         "publisher": {"@type": "Organization", "name": "Fanline.su", "url": "https://fanline.su/"},
         "datePublished": DATE, "dateModified": DATE, "mainEntityOfPage": url},
    ]
    if howto:
        graph.append(howto)
    if faq_items:
        graph.append(faq_schema(faq_items))
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph},
                    ensure_ascii=False, indent=2)
    faq_block = faq_html(faq_items) if faq_items else ""
    doc = f"""<!DOCTYPE html>
<html lang="ru">
<head>
{METRIKA}

  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}">
  <link rel="canonical" href="{url}">
  <meta property="og:type"        content="article">
  <meta property="og:locale"      content="ru_RU">
  <meta property="og:site_name"   content="Fanline.su">
  <meta property="og:title"       content="{esc(h1)}">
  <meta property="og:description" content="{esc(og_desc)}">
  <meta property="og:url"         content="{url}">
  <meta property="og:image"       content="https://fanline.su/img/og-cover.png">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="/img/apple-touch-icon.png">
  <link rel="stylesheet" href="../css/style.css">
  <script type="application/ld+json">
{ld}
  </script>
</head>
<body>

<header class="site-header">
  <div class="header-inner">
    <a href="/" class="site-logo">Fanli<span>ne</span>.su</a>
    <nav aria-label="Основная навигация">
      <ul class="site-nav">
        <li><a href="/montazh/">Монтаж</a></li>
        <li><a href="/komplektuyushchie/">Комплектующие</a></li>
        <li><a href="/vybor/">Выбор поликарбоната</a></li>
        <li><a href="/blog/" aria-current="page">Дача и огород</a></li>
      </ul>
    </nav>
  </div>
</header>

<nav class="breadcrumbs" aria-label="Хлебные крошки">
  <ol>
    <li><a href="/">Главная</a></li>
    <li><a href="/blog/">Дача и огород</a></li>
    <li><span aria-current="page">{esc(h1)}</span></li>
  </ol>
</nav>

<main>
  <article class="article-wrap">
    <div class="content">
      <h1>{esc(h1)}</h1>
{body}

{faq_block}
    </div>

    <aside class="sidebar">
{side}
    </aside>
  </article>
</main>

{ICON_SPRITE}

{FOOTER}

<script src="../js/main.js"></script>
</body>
</html>
"""
    path = os.path.join(OUT, f"{slug}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)
    return slug


# ================================================================== CONTENT
ARTICLES = []
def A(**kw): ARTICLES.append(kw)

# импортируем содержимое кластеров
from _content_crops import register as reg_crops
from _content_care import register as reg_care
from _content_pests import register as reg_pests
from _content_equip import register as reg_equip
reg_crops(A, cta, sidebar)
reg_care(A, cta, sidebar)
reg_pests(A, cta, sidebar)
reg_equip(A, cta, sidebar)

if __name__ == "__main__":
    for a in ARTICLES:
        build(**a)
    print(f"Сгенерировано статей: {len(ARTICLES)}")
    for a in ARTICLES:
        print("  blog/%s.html — %s" % (a["slug"], a["h1"]))
