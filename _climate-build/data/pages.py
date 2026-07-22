# -*- coding: utf-8 -*-
# Анти-дорвейная структура: 5 pillar-категорий в индексе (canon=None),
# карточки моделей канонизированы на свой pillar (живут как 200, ведут на маркетплейс).
D="https://fanline.su/"
PILLAR={
 "mojka":D+"catalog/uvlazhniteli-vozdukha/",
 "dush":D+"catalog/dush_dlja_dachi/",
 "vodonagrevatel":D+"catalog/vodonagrevateli/",
 "obluchatel":D+"catalog/baktericidnye-obluchateli/",
 "gippokrat":D+"catalog/ionizatory-vozdukha/",
}
def _p(url,kind,fam,h1,model,affil,pillar_self=False):
    # pillar_self=True -> это pillar (canon=None); иначе canon=pillar
    return (url,kind,fam,h1,model,affil,None if pillar_self else PILLAR[fam])

PAGES=[
# === 5 PILLAR (в индекс) ===
_p("catalog/uvlazhniteli-vozdukha","category","mojka","Увлажнители и мойки воздуха","","A9oiN8",True),
_p("catalog/dush_dlja_dachi","category","dush","Летний душ для дачи","","A9oeSD",True),
_p("catalog/vodonagrevateli","category","vodonagrevatel","Наливные водонагреватели для дачи","","A9opXF",True),
_p("catalog/baktericidnye-obluchateli","category","obluchatel","Бактерицидные облучатели","","A9p3jK",True),
_p("catalog/ionizatory-vozdukha","category","gippokrat","Ионизаторы и очистители воздуха","","A9p6hh",True),
# === карточки моделей -> canonical на pillar ===
# мойки
_p("item/108-uvlazhnitel-fanline-aqua-ve-400-1","product","mojka","Увлажнитель-мойка воздуха Fanline Aqua VE-400-1","Fanline Aqua VE-400-1","A9hfke"),
_p("item/111-uvlazhnitel-ochistitel-fanline-aqua-ve200-4uf","product","mojka","Мойка воздуха Fanline Aqua VE200-4UF","Fanline Aqua VE200-4UF","A9hqg5"),
_p("item/38-ochistitel-uvlazhnitel-fanline-aqua-ve200-4","product","mojka","Мойка воздуха Fanline Aqua VE200-4","Fanline Aqua VE200-4","A9oiN8"),
_p("item/28-ochistitel-uvlazhnitel-fanline-aqua-ve400","product","mojka","Мойка воздуха Fanline Aqua VE400","Fanline Aqua VE400","A9hioy"),
_p("item/28-ochistitel-uvlazhnitel-fanline-ve400","product","mojka","Мойка воздуха Fanline Aqua VE400","Fanline Aqua VE400","A9hioy"),
_p("item/45-ochistitel-uvlazhnitel-fanline-aqua-ve400-2","product","mojka","Мойка воздуха Fanline Aqua VE400-2","Fanline Aqua VE400-2","A9hioy"),
_p("item/56-ochistitel-uvlazhnitel-fanline-aqua-ve400-3","product","mojka","Мойка воздуха Fanline Aqua VE400-3","Fanline Aqua VE400-3","A9hfke"),
_p("item/47-ochistitel-uvlazhnitel-fanline-aqua-ve400-8","product","mojka","Мойка воздуха Fanline Aqua VE400-8","Fanline Aqua VE400-8","A9hcve"),
_p("item/88-ochistitel-uvlazhnitel-fanline-aqua-ve400-s-ultrafioletovymi-lampami","product","mojka","Мойка воздуха Fanline Aqua VE400 с УФ-лампами","Fanline Aqua VE400 с УФ-лампами","A9hioy"),
_p("item/54-ochistitel-uvlazhnitel-fanline-pro-905","product","mojka","Мойка воздуха Fanline PRO 905","Fanline PRO 905","A9oiN8"),
_p("item/55-ochistitel-uvlazhnitel-supra-sawc-130","product","mojka","Мойка воздуха Supra SAWC-130","Supra SAWC-130","A9oiN8"),
_p("item/126-ugolnyjj-filtr-dlya-mojjki-vozdukha-fanline-aqua-ve400-1","accessory","mojka","Угольный фильтр для мойки воздуха Fanline Aqua VE400-1","","A9hcve"),
# души
_p("item/27-dush-dlya-dachi-fanline-jr-2000lv","product","dush","Летний душ для дачи Fanline JR-2000LV","Fanline JR-2000LV","A9hioy"),
_p("item/30-dush-dlya-dachi-fanline-jr-3000-k1","product","dush","Летний душ для дачи Fanline JR-3000-K1","Fanline JR-3000-K1","A9hfke"),
_p("item/41-shlang-dlya-dusha","accessory","dush","Шланг для дачного душа","","A9pCcx"),
_p("item/101-lejjka-dlya-dusha-2","accessory","dush","Лейка для дачного душа","","A9oeSD"),
# водонагреватели
_p("item/125-vodonagrevatel-ehnergiya-2000-bn-bz","product","vodonagrevatel","Водонагреватель «Энергия 2000 БН-БЗ»","«Энергия 2000 БН-БЗ»","A9oT9r"),
_p("item/62-dush-dlya-dachi-ehnergiya-1300-bz","product","vodonagrevatel","Дачный водонагреватель «Энергия 1300 БЗ»","«Энергия 1300 БЗ»","A9oeSD"),
_p("item/95-perenosnojj-vodonagrevatel-dush-ehnergiya-3400","product","vodonagrevatel","Переносной водонагреватель-душ «Энергия 3400»","«Энергия 3400»","A9oeSD"),
("catalog/vodonagrevateli-s-dushevojj-nasadkojj","category","vodonagrevatel","Водонагреватели с душевой насадкой","","A9oeSD",D+"catalog/vodonagrevateli/"),
# облучатели
_p("item/67-obluchatel-baktericidnyjj-obn-150-azov-bez-provoda","product","obluchatel","Облучатель бактерицидный ОБН-150 «Азов»","ОБН-150 «Азов»","A9oPgr"),
_p("item/71-obluchatel-baktericidnyjj-cbb-35-azov","product","obluchatel","Облучатель бактерицидный СББ-35 «Азов»","СББ-35 «Азов»","A9p3jK"),
_p("item/75-obluchatel-recirkulyator-obrn-1kh15-azov","product","obluchatel","Облучатель-рециркулятор ОБРН-1х15 «Азов»","ОБРН-1х15 «Азов»","A9oPgr"),
# ионизатор
_p("item/35-ochistitel-vozdukha-gippokrat-ofis-iv-2","product","gippokrat","Очиститель-ионизатор «Гиппократ Офис ИВ-2»","«Гиппократ Офис ИВ-2»","A9oM62"),
]
