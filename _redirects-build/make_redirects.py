# -*- coding: utf-8 -*-
"""Страницы-редиректы для старых URL, на которые есть внешние ссылки.

GitHub Pages не умеет 301 на стороне сервера, поэтому единственный способ
не терять вес со старых ссылок — положить по старому адресу настоящую
страницу (HTTP 200), которая:
  * объявляет canonical на актуальный URL, это и есть сигнал склейки;
  * делает meta refresh 0 и JS-переход, чтобы человек попал куда надо;
  * показывает видимую ссылку, если и то и другое отключено.

Список собран из выгрузки внешних ссылок Яндекс.Вебмастера: взяты только
те адреса, на которые есть ссылки с чужих сайтов и которые сейчас отдают
404. Куда вести, выбрано по смыслу: та же модель, соседняя модель или
категория.
"""
import os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = "https://fanline.su"

REDIRECTS = {
    # Fanline PRO 900 снят, ближайшая живая модель линейки — PRO 905.
    "item/53-ochistitel-uvlazhnitel-fanline-pro-900":
        ("/item/54-ochistitel-uvlazhnitel-fanline-pro-905/",
         "Очиститель-увлажнитель Fanline PRO 905"),
    # VE500 не выпускается, ближайшая по производительности — VE400.
    "item/23-ochistitel-uvlazhnitel-fanline-aqua-ve500":
        ("/item/28-ochistitel-uvlazhnitel-fanline-aqua-ve400/",
         "Очиститель-увлажнитель Fanline Aqua VE400"),
    # Чужой бренд, своей замены нет — ведём в категорию.
    "item/115-klimaticheskijj-kompleks-zenet-zet-483":
        ("/catalog/uvlazhniteli-vozdukha/",
         "Увлажнители и очистители воздуха"),
    # Рециркулятор снят — ведём в категорию бактерицидных облучателей.
    "item/69-recirkulyator-baktericidnyjj-ob-02-foton":
        ("/catalog/baktericidnye-obluchateli/",
         "Бактерицидные облучатели и рециркуляторы"),
}

TPL = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Страница переехала — {anchor}</title>
<link rel="canonical" href="{domain}{url}">
<meta http-equiv="refresh" content="0; url={url}">
<meta name="description" content="Этот товар больше не выпускается. Актуальная страница: {anchor}.">
<style>
body{{font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;
color:#16241b;background:#fff;margin:0;padding:48px 20px;display:flex;justify-content:center}}
.b{{max-width:520px}}
h1{{font-size:22px;margin:0 0 12px}}
a{{color:#2f7d4f}}
.btn{{display:inline-block;margin-top:18px;padding:12px 20px;background:#2f7d4f;color:#fff;
border-radius:10px;text-decoration:none}}
</style>
<script>location.replace("{url}");</script>
</head>
<body>
<div class="b">
<h1>Страница переехала</h1>
<p>Этот товар снят с продажи. Мы перенаправляем вас на актуальную страницу.</p>
<p>Если переход не произошёл, откройте её вручную:</p>
<a class="btn" href="{url}">{anchor}</a>
</div>
</body>
</html>
"""

def main():
    made = []
    for old, (url, anchor) in REDIRECTS.items():
        target = os.path.join(ROOT, url.strip("/"), "index.html")
        if not os.path.exists(target):
            raise SystemExit(f"ЦЕЛЬ НЕ СУЩЕСТВУЕТ: {url} (для {old})")
        outdir = os.path.join(ROOT, old)
        os.makedirs(outdir, exist_ok=True)
        with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(TPL.format(url=url, anchor=html.escape(anchor), domain=DOMAIN))
        made.append((old, url))
    for a, b in made:
        print(f"  /{a}/  ->  {b}")
    print(f"Готово: {len(made)} редиректов")

if __name__ == "__main__":
    main()
