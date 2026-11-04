# -*- coding: utf-8 -*-
"""Честный lastmod в картах сайта (4 ноября 2026), общий для грунта, дров и щебня.

Раньше каждая сборка ставила всем URL сегодняшнюю дату — даже если на странице
не изменилось ни слова. Поисковики быстро перестают верить такому lastmod и
переобходят страницы реже. Теперь дата меняется, только когда меняется основной
текст страницы (<main> без скриптов, стилей и версий файлов). Подписи хранятся
в lastmod.json рядом; без записи берётся старая дата из карты (fallback).
"""
import os, re, json, hashlib, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STORE = os.path.join(HERE, "lastmod.json")
TODAY = datetime.date.today().isoformat()
_db = None


def _load():
    global _db
    if _db is None:
        _db = json.load(open(STORE, encoding="utf-8")) if os.path.exists(STORE) else {}
    return _db


def _sig(url):
    path = re.sub(r"^https?://[^/]+", "", url)
    f = os.path.join(ROOT, path.strip("/"), "index.html") if path.strip("/") else os.path.join(ROOT, "index.html")
    if not os.path.exists(f):
        return None
    h = open(f, encoding="utf-8").read()
    m = re.search(r"<main.*?</main>", h, re.S)
    h = m.group(0) if m else h
    h = re.sub(r"<script.*?</script>|<style.*?</style>", "", h, flags=re.S)
    h = re.sub(r"\?v=[0-9a-z]+", "", h)
    h = re.sub(r"\s+", " ", h)
    return hashlib.md5(h.encode("utf-8")).hexdigest()


def lastmod(url, fallback=None):
    db = _load(); sig = _sig(url); rec = db.get(url)
    if rec and rec["sig"] == sig:
        return rec["date"]
    date = fallback if (rec is None and fallback) else TODAY
    db[url] = {"sig": sig, "date": date}
    return date


def old_dates(sitemap_path):
    """loc → lastmod из существующей карты: дата для URL, которых ещё нет в lastmod.json."""
    if not os.path.exists(sitemap_path):
        return {}
    src = open(sitemap_path, encoding="utf-8").read()
    return dict(re.findall(r"<loc>(.*?)</loc>\s*<lastmod>(.*?)</lastmod>", src))


def save():
    if _db is not None:
        json.dump(dict(sorted(_db.items())), open(STORE, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
