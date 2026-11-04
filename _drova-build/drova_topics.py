# -*- coding: utf-8 -*-
"""«Статьи по теме» на коммерческих страницах дров (4 ноября 2026).

Владелец: «статьи плохо ранжируются». На странице брикетов, пеллет, угля,
горбыля и большинства пород не было ни одной ссылки на профильные статьи —
только на общий блог. Поисковик оценивает статью и по тому, ссылаются ли на
неё важные страницы сайта, а человеку со страницы брикетов полезно сразу
открыть «Как топить брикетами». Ссылки, которые на странице уже есть,
build.py отбрасывает, чтобы не дублировать.
"""

B = "/dostavka-drov/blog/"
A = "/dostavka-drov/"

TOPIC = {
    "/drova-berezovye-ekaterinburg/": [A + "kakie-drova-luchshe-dlya-otopleniya/", A + "skolko-stoit-kub-drov/", A + "skolko-vesit-kub-drov/", B + "udelnaya-teplota-sgoraniya-drov/"],
    "/drova-smeshannye-ekaterinburg/": [A + "kakie-drova-luchshe-dlya-otopleniya/", A + "skolko-drov-nuzhno-na-zimu/", A + "skladometr-ili-nasypnoy-kub/"],
    "/drova-hvoynye-ekaterinburg/": [A + "kakie-drova-luchshe-dlya-bani/", B + "kreozot-v-dymohode/", B + "kak-pochistit-dymohod/"],
    "/drova-osinovye-ekaterinburg/": [A + "kakie-drova-luchshe-dlya-bani/", B + "kak-pochistit-dymohod/", B + "temperatura-goreniya-drov/"],
    "/drova-olhovye-ekaterinburg/": [A + "kakie-drova-luchshe-dlya-bani/", B + "drova-dlya-shashlyka-i-pitstsy/", B + "temperatura-goreniya-drov/"],
    "/drova-suhie-ekaterinburg/": [A + "vlazhnost-drov/", B + "kak-pravilno-topit-pech/", B + "kak-slozhit-polennitsu/"],
    "/drova-churkami-ekaterinburg/": [B + "kak-pravilno-kolot-drova/", B + "kakoy-kolun-vybrat/", B + "skolko-stoit-raskolot-drova/", B + "drovokol-svoimi-rukami/"],
    "/gorbyl-ekaterinburg/": [B + "chto-sdelat-iz-gorbylya/", B + "kak-pilit-drova-benzopiloy/", B + "kozly-dlya-drov/"],
    "/drova-kolotye-ekaterinburg/": [B + "kak-slozhit-polennitsu/", B + "kak-poschitat-drova-v-polennitse/", B + "drovnik-svoimi-rukami/"],
    "/drova-dlya-kamina-ekaterinburg/": [B + "kak-topit-kamin/", B + "kak-razzhech-pech-i-kamin/", B + "pochemu-dymit-pech/"],
    "/drova-dlya-pechi-ekaterinburg/": [B + "kak-pravilno-topit-pech/", B + "pochemu-dymit-pech/", B + "kak-pochistit-dymohod/"],
    "/drova-dlya-bani-ekaterinburg/": [A + "kakie-drova-luchshe-dlya-bani/", B + "kak-razzhech-pech-i-kamin/", A + "skolko-drov-nuzhno-na-zimu/"],
    "/drova-dlya-kotla-ekaterinburg/": [A + "vlazhnost-drov/", B + "udelnaya-teplota-sgoraniya-drov/", A + "skolko-drov-nuzhno-na-zimu/"],
    "/toplivnye-brikety-ekaterinburg/": [B + "kak-topit-briketami/", B + "skolko-briketov-na-zimu/", B + "toplivnye-brikety-ili-drova/"],
    "/pellety-ekaterinburg/": [B + "rashod-pellet-na-zimu/", B + "pellety-kak-delayut/"],
    "/ugol-kamennyy-ekaterinburg/": [B + "kakoy-ugol-luchshe-dlya-otopleniya/", B + "udelnaya-teplota-sgoraniya-kamennogo-uglya/"],
    "/ugol-drevesnyy-ekaterinburg/": [B + "kak-razzhech-mangal/", B + "kak-sdelat-drevesnyy-ugol/", B + "drova-dlya-shashlyka-i-pitstsy/"],
    "/kolka-drov-ekaterinburg/": [B + "kak-pravilno-kolot-drova/", B + "kakoy-kolun-vybrat/"],
    "/drova-ekaterinburg/": [B + "kak-pravilno-topit-pech/", B + "kak-slozhit-polennitsu/", B + "udelnaya-teplota-sgoraniya-drov/"],
}
