# -*- coding: utf-8 -*-
"""Блок «Статьи по теме» на страницах товаров грунта (11 октября 2026).

Раньше страницы товаров ссылались только на два поста блога, и 53 статьи
раздела получали ссылки лишь с хаба и друг от друга. Здесь — 3-4 статьи на
товар: что спрашивают перед покупкой (чем заменить, что лучше, когда
вносить, сколько стоит). Ключ — товар (страницы городов) или slug страницы
из pages.py. Пути без /dostavka-grunta/ — статьи из articles.py, с blog/ —
посты блога.
"""

BY_PRODUCT = {
    "chernozem": ["chem-zamenit-chernozem", "peregnoy-ili-chernozem", "chernozem-ili-plodorodnyy-grunt", "skolko-stoit-chernozem"],
    "plodorodnyy-grunt": ["chernozem-ili-plodorodnyy-grunt", "kak-uluchshit-pochvu", "zemlya-pod-gazon-podgotovka", "blog/chem-podnyat-uchastok"],
    "peregnoy": ["kak-ispolzovat-peregnoy", "torf-ili-peregnoy", "kak-uluchshit-pochvu", "skolko-stoit-peregnoy"],
    "navoz": ["navoz-polza-i-vred", "kakoy-navoz-luchshe", "kogda-vnosit-navoz", "skolko-stoit-navoz"],
    "navoz-koroviy": ["kak-primenyat-koroviy-navoz", "kakoy-navoz-luchshe", "kogda-vnosit-navoz", "nastoy-iz-navoza"],
    "navoz-konskiy": ["kak-primenyat-konskiy-navoz", "konskiy-navoz-dlya-klubniki", "vysokie-i-teplye-gryadki", "zhidkiy-konskiy-navoz"],
    # 5 ноября: «торф для огорода» 1 467 и «торф или перегной» 296 в Вордстате — первыми
    "torf": ["torf-dlya-ogoroda", "torf-ili-peregnoy", "verhovoy-ili-nizinnyy-torf", "torf-dlya-rassady"],
    "kislyy-torf": ["kislyy-torf-dlya-kakih-rasteniy", "grunt-dlya-golubiki", "grunt-dlya-gortenzii", "neytralizovannyy-torf"],
    "torfogrunt": ["pochvogrunt", "torf-dlya-rassady", "kakoy-grunt-nuzhen-dlya-teplicy", "zemlya-pod-gazon-podgotovka"],
    "opilki": ["uteplenie-opilkami", "opilki-na-uchastke", "mulchirovanie", "kak-sdelat-kompost"],
    "zemlya-v-meshkah": ["pochvogrunt", "kakoy-grunt-nuzhen-dlya-teplicy", "torf-dlya-rassady", "chernozem-ili-plodorodnyy-grunt"],
}

BY_PAGE = {
    "chernozem-ekaterinburg": BY_PRODUCT["chernozem"],
    "peregnoy-ekaterinburg": BY_PRODUCT["peregnoy"],
    "peregnoy-konskiy-ekaterinburg": ["kak-primenyat-konskiy-navoz", "navoz-ili-peregnoy-chto-luchshe", "kak-ispolzovat-peregnoy", "konskiy-navoz-dlya-klubniki"],
    "torf-ekaterinburg": BY_PRODUCT["torf"],
    "torf-dlya-golubiki": ["grunt-dlya-golubiki", "kislyy-torf-dlya-kakih-rasteniy", "rasteniya-kisloy-pochvy", "kislotnost-pochvy"],
    "grunt-dlya-teplicy-ekaterinburg": ["kakoy-grunt-nuzhen-dlya-teplicy", "vysokie-i-teplye-gryadki", "chem-udobrit-ogurcy", "chem-udobrit-pomidory"],
    "zemlya-pod-gazon-ekaterinburg": ["zemlya-pod-gazon-podgotovka", "chernozem-ili-plodorodnyy-grunt", "blog/chem-podnyat-uchastok"],
    "torf-v-meshkah-ekaterinburg": BY_PRODUCT["torf"],
    "peregnoy-v-meshkah-ekaterinburg": BY_PRODUCT["peregnoy"],
    "navoz-v-meshkah-ekaterinburg": BY_PRODUCT["navoz"],
    "opilki-v-meshkah-ekaterinburg": BY_PRODUCT["opilki"],
}
