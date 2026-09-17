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
    # Появилась в сентябре 2026. Отгружает весь ассортимент, поэтому для
    # северного куста (сама Пышма, Балтым, Среднеуральск, Монетный) плечо
    # считается отсюда, а не через Курганово в объезд всего Екатеринбурга.
    # Именно ради таких случаев база и заводилась: до неё чернозём в Балтым
    # считался за 50 км вместо десяти.
    "verhnyaya-pyshma": {
        "name": "Верхняя Пышма",
        "iz": "из Верхней Пышмы",
        "v": "в Верхней Пышме",
        "where": "район Верхней Пышмы",
        "what": "весь ассортимент",
    },
}

# Товар -> базы, где он есть, в порядке приоритета при равном плече.
# Плечо считается от ближайшей из них к городу (см. base_of в build.py):
# один и тот же чернозём в Полевской едет из Курганово, а в Балтым из
# Верхней Пышмы, и цена рейса у них разная. Так оно и есть на самом деле.
PRODUCT_BASES = {
    "chernozem": ["kurganovo", "verhnyaya-pyshma"],
    "plodorodnyy-grunt": ["kurganovo", "verhnyaya-pyshma"],
    "zemlya-v-meshkah": ["kurganovo", "verhnyaya-pyshma"],
    "torfogrunt": ["kurganovo", "verhnyaya-pyshma"],
    "torf": ["kurganovo", "verhnyaya-pyshma"],
    "kislyy-torf": ["kurganovo", "verhnyaya-pyshma"],
    "peregnoy": ["sadovyy", "verhnyaya-pyshma"],
    "navoz": ["sadovyy", "verhnyaya-pyshma"],
    "navoz-koroviy": ["sadovyy", "verhnyaya-pyshma"],
    "navoz-konskiy": ["sadovyy", "verhnyaya-pyshma"],
}

# Основная база товара: та же, что и раньше. Нужна там, где город неизвестен
# (статьи, хаб) и выбирать ближайшую не из чего.
PRODUCT_BASE = {k: v[0] for k, v in PRODUCT_BASES.items()}

# Города, которые реально обслуживает площадка в Верхней Пышме. Список
# закрытый, а не «у кого плечо короче»: до востока области (Белоярский,
# Косулино, Арамиль) от Пышмы и от Курганово выходит примерно одинаково,
# разница в пределах точности наших оценок, и гонять туда машину с севера
# никто не собирается. Северный куст — другое дело: там разница в разы.
PYSHMA_CITIES = {
    "verhnyaya-pyshma", "baltym", "sredneuralsk",
    "berezovskiy", "monetnyy", "ekaterinburg",
}

# База по умолчанию: для страниц без товара (хаб, статьи, направления) и
# для нерудных материалов, которые возит профильный проект. Курганово —
# потому что оттуда идёт самый частый товар раздела, чернозём.
DEFAULT_BASE = "kurganovo"

KM = {
    #                        Курганово  Садовый  Ключевск
    "ekaterinburg":          {"kurganovo": 30, "sadovyy": 10,  "klyuchevsk": 40, "verhnyaya-pyshma": 15},
    "verhnyaya-pyshma":      {"kurganovo": 45, "sadovyy": 10,  "klyuchevsk": 30, "verhnyaya-pyshma": 5},
    "baltym":                {"kurganovo": 50, "sadovyy": 12,  "klyuchevsk": 28, "verhnyaya-pyshma": 10},
    "sredneuralsk":          {"kurganovo": 50, "sadovyy": 15,  "klyuchevsk": 40, "verhnyaya-pyshma": 10},
    "berezovskiy":           {"kurganovo": 45, "sadovyy": 20,  "klyuchevsk": 25, "verhnyaya-pyshma": 20},
    "gornyy-shchit":         {"kurganovo": 15, "sadovyy": 25,  "klyuchevsk": 55, "verhnyaya-pyshma": 35},
    "bolshoy-istok":         {"kurganovo": 40, "sadovyy": 25,  "klyuchevsk": 50, "verhnyaya-pyshma": 35},
    "kosulino":              {"kurganovo": 45, "sadovyy": 30,  "klyuchevsk": 45, "verhnyaya-pyshma": 40},
    "monetnyy":              {"kurganovo": 60, "sadovyy": 35,  "klyuchevsk": 35, "verhnyaya-pyshma": 30},
    "oktyabrskiy":           {"kurganovo": 40, "sadovyy": 45,  "klyuchevsk": 60, "verhnyaya-pyshma": 45},
    "aramil":                {"kurganovo": 45, "sadovyy": 30,  "klyuchevsk": 55, "verhnyaya-pyshma": 40},
    "patrushi":              {"kurganovo": 40, "sadovyy": 30,  "klyuchevsk": 60, "verhnyaya-pyshma": 40},
    "bobrovskiy":            {"kurganovo": 50, "sadovyy": 40,  "klyuchevsk": 55, "verhnyaya-pyshma": 50},
    "verhnee-dubrovo":       {"kurganovo": 55, "sadovyy": 40,  "klyuchevsk": 50, "verhnyaya-pyshma": 45},
    "beloyarskiy":           {"kurganovo": 65, "sadovyy": 50,  "klyuchevsk": 50, "verhnyaya-pyshma": 55},
    "zarechnyy":             {"kurganovo": 65, "sadovyy": 50,  "klyuchevsk": 55, "verhnyaya-pyshma": 55},
    "dvurechensk":           {"kurganovo": 60, "sadovyy": 55,  "klyuchevsk": 70, "verhnyaya-pyshma": 60},
    "sysert":                {"kurganovo": 35, "sadovyy": 50,  "klyuchevsk": 75, "verhnyaya-pyshma": 55},
    "kashino":               {"kurganovo": 30, "sadovyy": 55,  "klyuchevsk": 80, "verhnyaya-pyshma": 60},
    "cherdantsevo":          {"kurganovo": 30, "sadovyy": 50,  "klyuchevsk": 75, "verhnyaya-pyshma": 55},
    "verhnyaya-sysert":      {"kurganovo": 35, "sadovyy": 65,  "klyuchevsk": 90, "verhnyaya-pyshma": 70},
    "kurganovo":             {"kurganovo": 5,  "sadovyy": 40,  "klyuchevsk": 70, "verhnyaya-pyshma": 50},
    "polevskoy":             {"kurganovo": 25, "sadovyy": 60,  "klyuchevsk": 100, "verhnyaya-pyshma": 65},
    "severskiy":             {"kurganovo": 20, "sadovyy": 55,  "klyuchevsk": 95, "verhnyaya-pyshma": 60},
    "degtyarsk":             {"kurganovo": 35, "sadovyy": 60,  "klyuchevsk": 95, "verhnyaya-pyshma": 60},
    "revda":                 {"kurganovo": 45, "sadovyy": 55,  "klyuchevsk": 85, "verhnyaya-pyshma": 60},
    "pervouralsk":           {"kurganovo": 55, "sadovyy": 50,  "klyuchevsk": 80, "verhnyaya-pyshma": 55},
    "kamensk-uralskiy":      {"kurganovo": 120, "sadovyy": 105, "klyuchevsk": 110, "verhnyaya-pyshma": 115},
    "nizhniy-tagil":         {"kurganovo": 165, "sadovyy": 125, "klyuchevsk": 145, "verhnyaya-pyshma": 115},
    # Хабы направлений: середина тракта, а не конкретный посёлок.
    "polevskoy-trakt":       {"kurganovo": 10, "sadovyy": 45,  "klyuchevsk": 75, "verhnyaya-pyshma": 55},
    "chelyabinskiy-trakt":   {"kurganovo": 45, "sadovyy": 40,  "klyuchevsk": 55, "verhnyaya-pyshma": 50},
}
