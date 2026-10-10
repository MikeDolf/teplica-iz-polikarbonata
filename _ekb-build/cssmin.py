# -*- coding: utf-8 -*-
"""Сжатие общего CSS (10 октября 2026, аудит скорости: Lighthouse «Minify CSS»).

Правим по-прежнему assets/ekb/style.css — с комментариями и переносами. Обе
сборки (грунт и дрова) берут адрес стилей из site_config, а тот вызывает
css_url(): она пишет рядом style.min.css (только если содержимое изменилось)
и возвращает адрес с хешем — после правки стилей кеш браузеров сбрасывается
сам, номер версии вручную поднимать не нужно.

Сжатие осторожное: убираются комментарии, лишние пробелы и переносы, пробелы
вокруг { } ; , и после двоеточия, последняя «;» перед «}». Строки в кавычках
не трогаются. Пробелы вокруг > + ~ и перед двоеточием остаются: в селекторах
и calc() они значимы.
"""
import hashlib, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "assets", "ekb", "style.css")
OUT = os.path.join(HERE, "..", "assets", "ekb", "style.min.css")

_TOKEN = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|/\*.*?\*/', re.S)


def minify(css):
    parts, pos = [], 0
    for m in _TOKEN.finditer(css):
        parts.append(("code", css[pos:m.start()]))
        if not m.group().startswith("/*"):
            parts.append(("str", m.group()))
        pos = m.end()
    parts.append(("code", css[pos:]))
    out = []
    for kind, s in parts:
        if kind == "str":
            out.append(s)
            continue
        s = re.sub(r"\s+", " ", s)
        s = re.sub(r" ?([{};,]) ?", r"\1", s)
        s = re.sub(r": ", ":", s)
        out.append(s)
    css = "".join(out)
    css = re.sub(r";}", "}", css)
    return css.strip() + "\n"


def css_url():
    with open(SRC, encoding="utf-8") as f:
        mini = minify(f.read())
    old = None
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            old = f.read()
    if old != mini:
        with open(OUT, "w", encoding="utf-8") as f:
            f.write(mini)
    return "/assets/ekb/style.min.css?v=" + hashlib.md5(mini.encode("utf-8")).hexdigest()[:8]
