"""Public site constants. App Store URLs must keep working."""

from __future__ import annotations

SITE = "https://weizhichao1027-collab.github.io/beadtime-site"
BASE_PATH = "/beadtime-site"
APP_STORE_ID = "6799906107"
APP_STORE_UNIVERSAL = f"https://apps.apple.com/app/id{APP_STORE_ID}"
SUPPORT_EMAIL = "281916057@qq.com"
ORG_ZH = "上海岐山文化传播有限公司"
ORG_EN = "Shanghai Qishan Cultural Communication Co., Ltd."
BUNDLE_ID = "com.weizhichao.beadday"
IOS_MIN = "17.0"
UPDATED = "2026-09-18"
COPYRIGHT_YEAR = "2026"

# GitHub Pages serves these paths. Do not rename the zh-Hans public hubs
# or the per-locale support/privacy prefixes; App Store Connect points here.
LOCALES = {
    "zh-Hans": {
        "html_lang": "zh-Hans",
        "bcp47": "zh-Hans",
        "og": "zh_CN",
        "dir": "ltr",
        "store": f"https://apps.apple.com/cn/app/id{APP_STORE_ID}",
        "listing": "zh-Hans",
        "native": "简体中文",
        "store_name": "拼豆时光",
    },
    "en": {
        "html_lang": "en",
        "bcp47": "en",
        "og": "en_US",
        "dir": "ltr",
        "store": f"https://apps.apple.com/us/app/id{APP_STORE_ID}",
        "listing": "en-US",
        "native": "English",
        "store_name": "Fuse Beads: Pattern Maker",
    },
    "zh-Hant": {
        "html_lang": "zh-Hant",
        "bcp47": "zh-Hant",
        "og": "zh_TW",
        "dir": "ltr",
        "store": f"https://apps.apple.com/tw/app/id{APP_STORE_ID}",
        "listing": "zh-Hant",
        "native": "繁體中文",
        "store_name": "拼豆時光",
    },
    "ja": {
        "html_lang": "ja",
        "bcp47": "ja",
        "og": "ja_JP",
        "dir": "ltr",
        "store": f"https://apps.apple.com/jp/app/id{APP_STORE_ID}",
        "listing": "ja",
        "native": "日本語",
        "store_name": "ビーズタイム",
    },
    "ko": {
        "html_lang": "ko",
        "bcp47": "ko",
        "og": "ko_KR",
        "dir": "ltr",
        "store": f"https://apps.apple.com/kr/app/id{APP_STORE_ID}",
        "listing": "ko",
        "native": "한국어",
        "store_name": "비드 타임",
    },
    "de": {
        "html_lang": "de",
        "bcp47": "de",
        "og": "de_DE",
        "dir": "ltr",
        "store": f"https://apps.apple.com/de/app/id{APP_STORE_ID}",
        "listing": "de-DE",
        "native": "Deutsch",
        "store_name": "Fuse Beads: Bügelperlen",
    },
    "fr": {
        "html_lang": "fr",
        "bcp47": "fr",
        "og": "fr_FR",
        "dir": "ltr",
        "store": f"https://apps.apple.com/fr/app/id{APP_STORE_ID}",
        "listing": "fr-FR",
        "native": "Français",
        "store_name": "Fuse Beads: Motifs",
    },
    "es": {
        "html_lang": "es",
        "bcp47": "es",
        "og": "es_ES",
        "dir": "ltr",
        "store": f"https://apps.apple.com/es/app/id{APP_STORE_ID}",
        "listing": "es-ES",
        "native": "Español",
        "store_name": "Fuse Beads: Patrones",
    },
    "it": {
        "html_lang": "it",
        "bcp47": "it",
        "og": "it_IT",
        "dir": "ltr",
        "store": f"https://apps.apple.com/it/app/id{APP_STORE_ID}",
        "listing": "it",
        "native": "Italiano",
        "store_name": "Fuse Beads: Schemi",
    },
    "pt-BR": {
        "html_lang": "pt-BR",
        "bcp47": "pt-BR",
        "og": "pt_BR",
        "dir": "ltr",
        "store": f"https://apps.apple.com/br/app/id{APP_STORE_ID}",
        "listing": "pt-BR",
        "native": "Português (Brasil)",
        "store_name": "Fuse Beads: Padrões",
    },
    "ru": {
        "html_lang": "ru",
        "bcp47": "ru",
        "og": "ru_RU",
        "dir": "ltr",
        "store": f"https://apps.apple.com/ru/app/id{APP_STORE_ID}",
        "listing": "ru",
        "native": "Русский",
        "store_name": "Fuse Beads: схемы",
    },
    "ar": {
        "html_lang": "ar",
        "bcp47": "ar",
        "og": "ar_SA",
        "dir": "rtl",
        "store": f"https://apps.apple.com/sa/app/id{APP_STORE_ID}",
        "listing": "ar-SA",
        "native": "العربية",
        "store_name": "بيد تايم",
    },
    "hi": {
        "html_lang": "hi",
        "bcp47": "hi",
        "og": "hi_IN",
        "dir": "ltr",
        "store": f"https://apps.apple.com/in/app/id{APP_STORE_ID}",
        "listing": "hi",
        "native": "हिन्दी",
        "store_name": "बीड टाइम",
    },
}

LOCALE_ORDER = [
    "zh-Hans",
    "en",
    "zh-Hant",
    "ja",
    "ko",
    "es",
    "fr",
    "de",
    "pt-BR",
    "it",
    "ru",
    "ar",
    "hi",
]


def page_path(locale: str, kind: str) -> str:
    if kind == "home":
        return "/" if locale == "zh-Hans" else f"/{locale}/home/"
    if kind == "support":
        return "/support/" if locale == "zh-Hans" else f"/{locale}/"
    if kind == "privacy":
        return "/privacy/" if locale == "zh-Hans" else f"/{locale}/privacy/"
    raise ValueError(kind)


def abs_url(path: str) -> str:
    if path == "/":
        return SITE + "/"
    return SITE.rstrip("/") + path


def depth(path: str) -> int:
    if path == "/":
        return 0
    return path.strip("/").count("/") + 1


def asset_href(page: str, resource: str) -> str:
    return "../" * depth(page) + resource.lstrip("/")


def rel_href(from_path: str, to_path: str) -> str:
    if from_path == to_path:
        return "./"
    from posixpath import relpath

    src = "/" if from_path == "/" else from_path.rstrip("/") + "/"
    dst = "/" if to_path == "/" else to_path
    relative = relpath(dst, src)
    if relative in {".", "./"}:
        return "./"
    if to_path.endswith("/") and not relative.endswith("/"):
        return relative + "/"
    if to_path == "/" and not relative.endswith("/"):
        return relative + "/" if relative != "." else "./"
    return relative
