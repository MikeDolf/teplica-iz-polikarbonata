# -*- coding: utf-8 -*-
# ЕДИНЫЙ конфиг лид-ген раздела. Всё, что меняется при запуске, лежит здесь.
# Сейчас значения-плейсхолдеры. Заменить перед публикацией.

SITE = {
    "brand": "Грунт Доставка",           # рабочее имя раздела (плейсхолдер)
    "domain": "https://fanline.su",
    "region": "Екатеринбург и Свердловская область",
    "region_po": "Екатеринбургу и Свердловской области",   # форма после предлога "по"
    "contact_email": "mezdudelom73@gmail.com",
    # Связь только через MAX: телефон на страницах не публикуем, чтобы
    # обращения приходили в мессенджер. Шаблоны выводят телефон только
    # при непустом phone_display, поэтому достаточно очистить его.
    "phone_display": "",
    "phone_tel": "",
    "phone_internal": "+7 950 646-09-53",   # для прайса и своих нужд, на сайт не идёт
    "has_max": True,                    # мессенджер MAX подключён на этом номере
    "max_url": "https://max.ru/u/f9LHodD0cOIgiq2N2buCj7oU32e1sbUDdW834GzM718dViUBpco7KXS8n10",  # ссылка-профиль MAX
    "legal_status": "",
    "payment": "Оплата любая: наличными, картой или переводом, после выгрузки.",
    "samovyvoz": True,
    "skidki_obem": True,
    "hours": "Круглосуточно, без выходных",
    "callback_promise": "ответим в MAX за 15 минут",
    "min_volume": "3 м\u00b3",              # минимальный объём заказа
    "min_volume_note": "меньший объём возможен самовывозом",
    "form_endpoint": "https://api.web3forms.com/submit",
    "web3forms_key": "4c17cc27-0b22-40b7-bea5-47ff348ef6c8",  # бесплатный ключ на web3forms.com, привязать к mezdudelom73@gmail.com
    "privacy_url": "/politika-konfidentsialnosti.html",
    "metrika_id": "110303165",                      # оставлено пустым намеренно (место под счётчик)
    "css": "/assets/ekb/style.css?v=40",
}
