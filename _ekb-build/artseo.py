# -*- coding: utf-8 -*-
"""Оглавление статей (4 ноября 2026), общее для грунта, дров и щебня.

Владелец: «статьи плохо ранжируются». Ни у одной из 179 статей не было
оглавления и якорей у подзаголовков. Яндекс и Google берут такие якоря
в быстрые ссылки сниппета («Содержание»), а длинную статью с оглавлением
дочитывают чаще. add_toc() ставит id каждому H2 статьи и вставляет
«Содержание» сразу после вводного абзаца (.art__lede). Служебные H2
(«Читайте также», «Частые вопросы» и т. п.) в оглавление не попадают.
"""
import re

_TR = dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
               ["a", "b", "v", "g", "d", "e", "e", "zh", "z", "i", "y", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f",
                "h", "c", "ch", "sh", "shch", "", "y", "", "e", "yu", "ya"]))
SKIP = ("читайте также", "частые вопросы", "ещё возим", "еще возим", "похожие", "калькулятор", "рассчитаем", "статьи по теме")
MIN_H2 = 3


def slug(text):
    t = re.sub(r"<[^>]+>", "", text).lower()
    t = "".join(_TR.get(ch, ch) for ch in t)
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t[:60].rstrip("-") or "razdel"


def add_toc(html):
    m = re.search(r'<article class="art[^"]*">(.*?)</article>', html, re.S)
    if not m or 'class="toc"' in html:
        return html
    art = m.group(1)
    lede = re.search(r'<p class="art__lede">.*?</p>', art, re.S)
    if not lede:
        return html
    used, items = set(), []

    def repl(h):
        attrs, inner = h.group(1), h.group(2)
        text = re.sub(r"<[^>]+>", "", inner).strip()
        if "id=" in attrs or any(text.lower().startswith(s) for s in SKIP):
            return h.group(0)
        sid = base = slug(text); n = 2
        while sid in used:
            sid = f"{base}-{n}"; n += 1
        used.add(sid); items.append((sid, text))
        return f'<h2{attrs} id="{sid}">{inner}</h2>'

    new_art = re.sub(r"<h2([^>]*)>(.*?)</h2>", repl, art, flags=re.S)
    if len(items) < MIN_H2:
        return html
    toc = ('\n    <nav class="toc" aria-label="Содержание статьи"><p class="toc__t">Содержание</p><ol>'
           + "".join(f'<li><a href="#{sid}">{text}</a></li>' for sid, text in items) + "</ol></nav>")
    new_lede = re.search(r'<p class="art__lede">.*?</p>', new_art, re.S)
    new_art = new_art[:new_lede.end()] + toc + new_art[new_lede.end():]
    return html[:m.start(1)] + new_art + html[m.end(1):]
