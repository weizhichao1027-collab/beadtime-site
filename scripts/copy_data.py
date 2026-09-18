"""Merged site copy for every public locale."""

from copy_asia import JA, KO, ZH_HANT
from copy_eu import DE, ES, FR, IT, PT, RU
from copy_rtl import AR, HI
from copy_zh_en import EN, ZH

COPY = {
    "zh-Hans": ZH,
    "en": EN,
    "zh-Hant": ZH_HANT,
    "ja": JA,
    "ko": KO,
    "de": DE,
    "fr": FR,
    "es": ES,
    "it": IT,
    "pt-BR": PT,
    "ru": RU,
    "ar": AR,
    "hi": HI,
}


def copy_for(locale: str) -> dict:
    return COPY[locale]
