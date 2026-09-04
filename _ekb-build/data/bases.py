# -*- coding: utf-8 -*-
"""Базы отгрузки и плечо до каждого города.

До этого файла в разделе была одна база (Верхняя Пышма), и рейс до любого
адреса считался от неё. Это было неверно и било по цене там, где мы как раз
и хотим продавать: земля лежит на Полевском тракте, а клиенту в Полевской
доставка считалась через весь Екатеринбург — 70 км вместо 25, то есть
13 300 ₽ вместо 4 750 ₽ за тот же рейс. Люди получали цену и уходили.

Теперь база своя у каждого товара, и плечо считается от неё.

KM — расстояния по дорогам, в один конец, округлены до пяти километров.
Это оценка по маршрутам, а не выгрузка из навигатора: на сайте цифры
подписаны как «около» и «примерно», точную стоимость называем по заявке.
Юг (Полевской, Северский, Дегтярск, Сысерть) считается от Курганово,
север и восток — от Садового и Ключевска, поэтому один и тот же город
стоит по-разному в зависимости от того, что везём. Так оно и есть.
"""

BASES = {
    "kurganovo": {
        "name": "Курганово",
        "iz": "из Курганово",
        "v": "в Курганово",
        "where": "Полевской тракт",
        "what": "земля, торф и торфогрунт",
    },
    "sadovyy": {
        "name": "Садовый",
        "iz": "из Садового",
        "v": "в Садовом",
        "where": "север Екатеринбурга",
        "what": "перегной и навоз",
    },
    # Фрезерованный торф партнёр отгружает из Ключевска. Отдельного товара
    # под него в разделе пока нет: страницы торфа описывают низинный и
    # верховой, и оба идут из Курганово. База описана здесь, чтобы её не
    # искать заново, когда фрезерованный торф появится в каталоге.
    "klyuchevsk": {
        "name": "Ключевск",
        "iz": "из Ключевска",
        "v": "в Ключевске",
        "where": "Режевской тракт",
        "what": "фрезерованный торф",
    },
}

# Товар -> база. Ключи те же, что у PRODUCTS.
PRODUCT_BASE = {
    "chernozem": "kurganovo",
    "plodorodnyy-grunt": "kurganovo",
    "zemlya-v-meshkah": "kurganovo",
    "torfogrunt": "kurganovo",
    "torf": "kurganovo",
    "kislyy-torf": "kurganovo",
    "peregnoy": "sadovyy",
    "navoz": "sadovyy",
    "navoz-koroviy": "sadovyy",
    "navoz-konskiy": "sadovyy",
}

# База по умолчанию: для страниц без товара (хаб, статьи, направления) и
# для нерудных материалов, которые возит профильный проект. Курганово —
# потому что оттуда идёт самый частый товар раздела, чернозём.
DEFAULT_BASE = "kurganovo"

KM = {
    #                        Курганово  Садовый  Ключевск
    "ekaterinburg":          {"kurganovo": 30, "sadovyy": 10,  "klyuchevsk": 40},
    "verhnyaya-pyshma":      {"kurganovo": 45, "sadovyy": 10,  "klyuchevsk": 30},
    "baltym":                {"kurganovo": 50, "sadovyy": 12,  "klyuchevsk": 28},
    "sredneuralsk":          {"kurganovo": 50, "sadovyy": 15,  "klyuchevsk": 40},
    "berezovskiy":           {"kurganovo": 45, "sadovyy": 20,  "klyuchevsk": 25},
    "gornyy-shchit":         {"kurganovo": 15, "sadovyy": 25,  "klyuchevsk": 55},
    "bolshoy-istok":         {"kurganovo": 40, "sadovyy": 25,  "klyuchevsk": 50},
    "aramil":                {"kurganovo": 45, "sadovyy": 30,  "klyuchevsk": 55},
    "patrushi":              {"kurganovo": 40, "sadovyy": 30,  "klyuchevsk": 60},
    "bobrovskiy":            {"kurganovo": 50, "sadovyy": 40,  "klyuchevsk": 55},
    "verhnee-dubrovo":       {"kurganovo": 55, "sadovyy": 40,  "klyuchevsk": 50},
    "beloyarskiy":           {"kurganovo": 65, "sadovyy": 50,  "klyuchevsk": 50},
    "zarechnyy":             {"kurganovo": 65, "sadovyy": 50,  "klyuchevsk": 55},
    "dvurechensk":           {"kurganovo": 60, "sadovyy": 55,  "klyuchevsk": 70},
    "sysert":                {"kurganovo": 35, "sadovyy": 50,  "klyuchevsk": 75},
    "kashino":               {"kurganovo": 30, "sadovyy": 55,  "klyuchevsk": 80},
    "verhnyaya-sysert":      {"kurganovo": 35, "sadovyy": 65,  "klyuchevsk": 90},
    "kurganovo":             {"kurganovo": 5,  "sadovyy": 40,  "klyuchevsk": 70},
    "polevskoy":             {"kurganovo": 25, "sadovyy": 60,  "klyuchevsk": 100},
    "severskiy":             {"kurganovo": 20, "sadovyy": 55,  "klyuchevsk": 95},
    "degtyarsk":             {"kurganovo": 35, "sadovyy": 60,  "klyuchevsk": 95},
    "revda":                 {"kurganovo": 45, "sadovyy": 55,  "klyuchevsk": 85},
    "pervouralsk":           {"kurganovo": 55, "sadovyy": 50,  "klyuchevsk": 80},
    "kamensk-uralskiy":      {"kurganovo": 120, "sadovyy": 105, "klyuchevsk": 110},
    "nizhniy-tagil":         {"kurganovo": 165, "sadovyy": 125, "klyuchevsk": 145},
    # Хабы направлений: середина тракта, а не конкретный посёлок.
    "polevskoy-trakt":       {"kurganovo": 10, "sadovyy": 45,  "klyuchevsk": 75},
    "chelyabinskiy-trakt":   {"kurganovo": 45, "sadovyy": 40,  "klyuchevsk": 55},
}
