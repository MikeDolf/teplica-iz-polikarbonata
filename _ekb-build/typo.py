"""Неразрывные пробелы в видимом тексте страниц грунта и дров.

На узких телефонах единица уезжала на новую строку отдельно от числа:
«до 50 / км», «700-750 / кг», «Машина 10 / м³». Склеиваем число с
единицей, предлог с числом, разряды «11 000» и диапазоны «700-750».
Правим только текст между тегами внутри <body>: скрипты, стили, поля
формы и атрибуты не трогаем — их значения уходят в заявку и в JS.
"""
import re

NB, WJ = " ", "⁠"   # неразрывный пробел; «склейка» нулевой ширины

_SKIP = re.compile(r"(<script\b.*?</script>|<style\b.*?</style>|<textarea\b.*?</textarea>"
                   r"|<select\b.*?</select>|<[^>]+>)", re.S | re.I)

_UNIT = (r"(?:₽|руб\b\.?|м³|м²|км\b|кг\b|см\b|мм\b|м\b|т\b|л\b|г\b|ч\b|%|°"
         r"|шт\b\.?|штук\w*|куб\w*|складометр\w*|мешк\w*|мешок|тонн\w*|литр\w*"
         r"|сот\w*|час\w*|минут\w*|рейс\w*|кВт\w*|ккал\b|МДж\b)")
_NUM_UNIT = re.compile(r"(\d) (?=" + _UNIT + ")")
_PREP_NUM = re.compile(r"(?<![\w-])(от|до|по|на|за|около|примерно|почти|≈|~|№) (?=\d)", re.I)
_THOUSANDS = re.compile(r"(?<![\d.,])(\d{1,3}) (?=\d{3}(?!\d))")
_THIN = re.compile(r"(\d)\u2009(?=\d{3}(?!\d))")   # тонкий пробел в «9 780» переносится
_RANGE = re.compile(r"(\d)([-–])(?=\d)")
_SLASH = re.compile(r"₽/(?=\w)")


def _text(t):
    if not any(c.isdigit() for c in t) and "₽" not in t:
        return t
    t = _THOUSANDS.sub("\\1" + NB, t)
    t = _THOUSANDS.sub("\\1" + NB, t)          # «1 200 000» — второй разряд
    t = _THIN.sub("\\1\u202f", t)
    t = _NUM_UNIT.sub("\\1" + NB, t)
    t = _PREP_NUM.sub("\\1" + NB, t)
    t = _RANGE.sub("\\1\\2" + WJ, t)
    t = _SLASH.sub("₽/" + WJ, t)
    return t


def glue(html):
    head, sep, body = html.partition("<body")
    parts = _SKIP.split(body)
    for i in range(0, len(parts), 2):
        parts[i] = _text(parts[i])
    return head + sep + "".join(parts)
