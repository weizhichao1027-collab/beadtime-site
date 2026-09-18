#!/usr/bin/env python3
"""Emit crawlable static pages for the Fuse Beads public site."""

from __future__ import annotations

import json
import sys
from html import escape
from pathlib import Path

from config import (
    APP_STORE_ID,
    APP_STORE_UNIVERSAL,
    BASE_PATH,
    BUNDLE_ID,
    COPYRIGHT_YEAR,
    LOCALE_ORDER,
    LOCALES,
    ORG_EN,
    ORG_ZH,
    SITE,
    SUPPORT_EMAIL,
    UPDATED,
    abs_url,
    asset_href,
    page_path,
    rel_href,
)
from copy_data import COPY, copy_for

ROOT = Path(__file__).resolve().parents[1]
KINDS = ("home", "support", "privacy")
CSP = (
    "default-src 'none'; script-src 'self'; style-src 'self'; "
    "img-src 'self'; font-src 'self'; connect-src 'none'; object-src 'none'; "
    "base-uri 'self'; form-action 'none'"
)
LOCALE_CLOUD = [
    "简体中文",
    "English",
    "繁體中文",
    "日本語",
    "한국어",
    "Español",
    "Français",
    "Deutsch",
    "Português (Brasil)",
    "Italiano",
    "Русский",
    "العربية",
    "हिन्दी",
]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def file_for(url_path: str) -> Path:
    if url_path == "/":
        return ROOT / "index.html"
    return ROOT / url_path.strip("/") / "index.html"


def ld_json(payload) -> str:
    blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return blob.replace("</", "<\\/")


def organization() -> dict:
    return {
        "@type": "Organization",
        "name": ORG_EN,
        "alternateName": [ORG_ZH, "Qishan"],
        "email": SUPPORT_EMAIL,
        "url": abs_url("/"),
    }


def software_app(locale: str) -> dict:
    meta = LOCALES[locale]
    names = [
        meta["store_name"],
        "拼豆时光",
        "Fuse Beads",
        "Fuse Beads: Pattern Maker",
    ]
    unique = []
    for name in names:
        if name not in unique:
            unique.append(name)
    return {
        "@type": "MobileApplication",
        "name": meta["store_name"],
        "alternateName": unique[1:],
        "operatingSystem": "iOS 17.0 or later",
        "applicationCategory": "DesignApplication",
        "applicationSubCategory": "LifestyleApplication",
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock",
        },
        "downloadUrl": meta["store"],
        "installUrl": meta["store"],
        "softwareVersion": "1.1",
        "isAccessibleForFree": True,
        "inLanguage": [LOCALES[item]["bcp47"] for item in LOCALE_ORDER],
        "author": organization(),
        "publisher": organization(),
        "identifier": BUNDLE_ID,
        "url": abs_url(page_path(locale, "home")),
    }


def hreflang_links(page: str, kind: str) -> str:
    lines = []
    for locale in LOCALE_ORDER:
        href = abs_url(page_path(locale, kind))
        lines.append(
            f'  <link rel="alternate" hreflang="{LOCALES[locale]["bcp47"]}" href="{escape(href)}">'
        )
    default = "en" if kind != "home" else "en"
    if kind == "home":
        default_href = abs_url(page_path("en", "home"))
    else:
        default_href = abs_url(page_path(default, kind))
    lines.append(f'  <link rel="alternate" hreflang="x-default" href="{escape(default_href)}">')
    return "\n".join(lines)


def og_locales(current: str) -> str:
    lines = [f'  <meta property="og:locale" content="{LOCALES[current]["og"]}">']
    for locale in LOCALE_ORDER:
        if locale == current:
            continue
        lines.append(f'  <meta property="og:locale:alternate" content="{LOCALES[locale]["og"]}">')
    return "\n".join(lines)


def head(
    locale: str,
    kind: str,
    page: str,
    title: str,
    description: str,
    extra_ld=None,
    robots: str | None = None,
    canonical_path: str | None = None,
) -> str:
    meta = LOCALES[locale]
    copy = copy_for(locale)
    canonical = abs_url(canonical_path or page)
    image = abs_url("/assets/img/og.png")
    css = asset_href(page, "assets/css/site.css")
    icon = asset_href(page, "assets/img/favicon.svg")
    icon32 = asset_href(page, "assets/img/favicon-32.png")
    apple = asset_href(page, "assets/img/apple-touch-icon.png")
    og_type = "article" if kind == "privacy" else "website"
    schemas = [
        {
            "@context": "https://schema.org",
            "@graph": [
                organization(),
                software_app(locale),
                {
                    "@type": "WebSite",
                    "name": "拼豆时光 / Fuse Beads",
                    "url": abs_url("/"),
                    "inLanguage": [LOCALES[item]["bcp47"] for item in LOCALE_ORDER],
                    "publisher": organization(),
                },
                {
                    "@type": "WebPage",
                    "@id": canonical,
                    "url": canonical,
                    "name": title,
                    "description": description,
                    "inLanguage": meta["bcp47"],
                    "isPartOf": {"@id": abs_url("/")},
                    "dateModified": UPDATED,
                    "about": software_app(locale),
                },
            ],
        }
    ]
    if extra_ld:
        schemas.extend(extra_ld if isinstance(extra_ld, list) else [extra_ld])
    ld_tags = "\n".join(
        f'  <script type="application/ld+json">{ld_json(item)}</script>' for item in schemas
    )
    robots_tag = f'  <meta name="robots" content="{robots}">\n' if robots else ""
    root = "." if page == "/" else "/".join([".."] * (page.strip("/").count("/") + 1))
    return f"""<!DOCTYPE html>
<html lang="{escape(meta["html_lang"])}" dir="{escape(meta["dir"])}" data-root="{root}">
<head>
  <meta charset="utf-8">
  <meta http-equiv="Content-Security-Policy" content="{CSP}">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description)}">
{robots_tag}  <meta name="theme-color" content="#F4EDE3">
  <meta name="apple-itunes-app" content="app-id={APP_STORE_ID}">
  <meta name="author" content="{escape(ORG_EN)}">
  <link rel="icon" href="{escape(icon)}" type="image/svg+xml">
  <link rel="icon" href="{escape(icon32)}" sizes="32x32">
  <link rel="apple-touch-icon" href="{escape(apple)}">
  <link rel="canonical" href="{escape(canonical)}">
  <link rel="sitemap" type="application/xml" title="Sitemap" href="{SITE}/sitemap.xml">
  <link rel="alternate" type="text/plain" title="LLMs" href="{SITE}/llms.txt">
{hreflang_links(page, kind)}
  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="拼豆时光 / Fuse Beads">
  <meta property="og:title" content="{escape(title)}">
  <meta property="og:description" content="{escape(description)}">
  <meta property="og:url" content="{escape(canonical)}">
  <meta property="og:image" content="{escape(image)}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="{escape(copy["home"]["story_alt"])}">
{og_locales(locale)}
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{escape(title)}">
  <meta name="twitter:description" content="{escape(description)}">
  <meta name="twitter:image" content="{escape(image)}">
  <link rel="stylesheet" href="{escape(css)}">
{ld_tags}
</head>"""


def locale_picker(locale: str, kind: str, page: str) -> str:
    copy = copy_for(locale)
    items = []
    for other in LOCALE_ORDER:
        href = rel_href(page, page_path(other, kind))
        current = ' aria-current="true"' if other == locale else ""
        items.append(
            f'          <li><a href="{escape(href)}" hreflang="{escape(LOCALES[other]["bcp47"])}" lang="{escape(LOCALES[other]["html_lang"])}"{current}>{escape(LOCALES[other]["native"])}</a></li>'
        )
    return f"""      <nav class="locale-picker" aria-label="{escape(copy["chrome"]["lang_aria"])}">
        <details>
          <summary>{escape(LOCALES[locale]["native"])}</summary>
          <ul>
{chr(10).join(items)}
          </ul>
        </details>
      </nav>"""


def chrome_header(locale: str, kind: str, page: str) -> str:
    copy = copy_for(locale)["chrome"]
    home = rel_href(page, page_path(locale, "home"))
    support = rel_href(page, page_path(locale, "support"))
    privacy = rel_href(page, page_path(locale, "privacy"))
    store = LOCALES[locale]["store"]
    mark = asset_href(page, "assets/img/favicon.svg")

    def nav_link(href: str, key: str, target: str) -> str:
        current = ' aria-current="page"' if kind == target else ""
        return f'<a href="{escape(href)}" data-nav="{target}"{current}>{escape(copy[key])}</a>'

    return f"""  <a class="skip-link" href="#main">{escape(copy["skip"])}</a>
  <header class="site-header">
    <div class="wrap header-inner">
      <a class="brand" href="{escape(home)}">
        <img class="brand-mark" src="{escape(mark)}" alt="" width="36" height="36">
        <span class="brand-name">
          <strong>{escape(copy["brand_zh"])}</strong>
          <span>{escape(copy["brand_en"])}</span>
        </span>
      </a>
      <div class="nav-cluster" id="nav-cluster">
        <nav class="site-nav" aria-label="{escape(copy["nav_aria"])}">
          {nav_link(home, "nav_home", "home")}
          {nav_link(support, "nav_support", "support")}
          {nav_link(privacy, "nav_privacy", "privacy")}
        </nav>
      </div>
      <div class="header-tools">
{locale_picker(locale, kind, page)}
        <a class="btn btn-store" href="{escape(store)}">{escape(copy["cta_store"])}</a>
        <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="nav-cluster" data-open-label="{escape(copy["nav_open"])}" data-close-label="{escape(copy["nav_close"])}">
          <span class="nav-toggle-bars" aria-hidden="true"></span>
          <span class="nav-toggle-text">{escape(copy["nav_open"])}</span>
        </button>
      </div>
    </div>
    <div class="nav-backdrop" id="nav-backdrop" hidden></div>
  </header>"""


def chrome_footer(locale: str, page: str) -> str:
    copy = copy_for(locale)["chrome"]
    home = rel_href(page, page_path(locale, "home"))
    support = rel_href(page, page_path(locale, "support"))
    privacy = rel_href(page, page_path(locale, "privacy"))
    store = LOCALES[locale]["store"]
    js = asset_href(page, "assets/js/site.js")
    return f"""  <footer class="site-footer">
    <div class="wrap footer-grid">
      <div>
        <strong>{escape(copy["brand_zh"])}</strong>
        <p>{escape(copy["brand_en"])}</p>
      </div>
      <div>
        <h2>{escape(copy["footer_explore"])}</h2>
        <ul>
          <li><a href="{escape(home)}">{escape(copy["nav_home"])}</a></li>
          <li><a href="{escape(store)}">{escape(copy["cta_store"])}</a></li>
        </ul>
      </div>
      <div>
        <h2>{escape(copy["footer_help"])}</h2>
        <ul>
          <li><a href="{escape(support)}">{escape(copy["nav_support"])}</a></li>
          <li><a href="{escape(privacy)}">{escape(copy["nav_privacy"])}</a></li>
          <li><a href="mailto:{SUPPORT_EMAIL}">{SUPPORT_EMAIL}</a></li>
        </ul>
      </div>
    </div>
    <p class="wrap legal-note">{escape(copy["footer_copy"])}</p>
  </footer>
  <script src="{escape(js)}"></script>
</body>
</html>
"""


def page_shell(
    locale: str,
    kind: str,
    page: str,
    title: str,
    description: str,
    main: str,
    extra_ld=None,
    robots: str | None = None,
    canonical: str | None = None,
) -> str:
    return "\n".join(
        [
            head(locale, kind, page, title, description, extra_ld, robots, canonical),
            f'<body data-page="{kind}" data-locale="{locale}">',
            chrome_header(locale, kind, page),
            main,
            chrome_footer(locale, page),
        ]
    )


def render_home(locale: str, page: str, canonical: str | None = None) -> str:
    copy = copy_for(locale)
    home = copy["home"]
    chrome = copy["chrome"]
    store = LOCALES[locale]["store"]
    craft = asset_href(page, "assets/img/hero-craft.jpg")
    cat = asset_href(page, "assets/img/cat-project.jpg")
    daisy = asset_href(page, "assets/img/daisy-idea.jpg")
    cloud = "".join(f"<span>{escape(name)}</span>" for name in LOCALE_CLOUD)
    main = f"""  <main id="main">
    <section class="wrap hero">
      <div>
        <p class="live-flag">{escape(home["live"])}</p>
        <h1>{escape(home["hero_title"])}</h1>
        <p class="lede">{escape(home["hero_lede"])}</p>
        <div class="hero-actions">
          <a class="btn btn-primary" href="{escape(store)}">{escape(chrome["cta_store"])}</a>
          <a class="text-link" href="#loop">{escape(home["cta_how"])}</a>
        </div>
        <div class="hero-meta">
          <span>{escape(home["meta1"])}</span>
          <span>{escape(home["meta2"])}</span>
          <span>{escape(home["meta3"])}</span>
        </div>
      </div>
      <div class="pegboard" id="pegboard" aria-hidden="true"></div>
    </section>

    <section class="section">
      <div class="wrap entity">
        <h2>{escape(home["def_title"])}</h2>
        <p>{escape(home["def_body"])}</p>
      </div>
    </section>

    <section class="section">
      <div class="wrap story-grid">
        <div>
          <h2>{escape(home["story_title"])}</h2>
          <p class="prose">{escape(home["story_body"])}</p>
        </div>
        <figure class="story-photo">
          <img src="{escape(craft)}" alt="{escape(home["story_alt"])}" width="1400" height="1077">
        </figure>
      </div>
    </section>

    <section class="section" id="loop">
      <div class="wrap">
        <h2>{escape(home["loop_title"])}</h2>
        <div class="loop">
          <article class="loop-row">
            <figure class="loop-visual loop-art" aria-hidden="true">
              <div class="crop-frame">
                <div class="pegboard pegboard--loop" id="loop-board"></div>
              </div>
            </figure>
            <div class="loop-copy">
              <h3>{escape(home["loop1_title"])}</h3>
              <p>{escape(home["loop1_body"])}</p>
            </div>
          </article>
          <article class="loop-row">
            <figure class="loop-visual">
              <img src="{escape(cat)}" alt="{escape(home["loop2_alt"])}" width="1100" height="1100">
            </figure>
            <div class="loop-copy">
              <h3>{escape(home["loop2_title"])}</h3>
              <p>{escape(home["loop2_body"])}</p>
            </div>
          </article>
          <article class="loop-row">
            <figure class="loop-visual">
              <img src="{escape(daisy)}" alt="{escape(home["loop3_alt"])}" width="1100" height="1100">
            </figure>
            <div class="loop-copy">
              <h3>{escape(home["loop3_title"])}</h3>
              <p>{escape(home["loop3_body"])}</p>
            </div>
          </article>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap spec-band">
        <div>
          <h2>{escape(home["spec_title"])}</h2>
          <p>{escape(home["spec_body"])}</p>
        </div>
        <dl class="spec-list">
          <div><dt>{escape(home["spec_boards"])}</dt><dd>{escape(home["spec_boards_val"])}</dd></div>
          <div><dt>{escape(home["spec_colors"])}</dt><dd>{escape(home["spec_colors_val"])}</dd></div>
          <div><dt>{escape(home["spec_library"])}</dt><dd>{escape(home["spec_library_val"])}</dd></div>
          <div><dt>{escape(home["spec_locales"])}</dt><dd>{escape(home["spec_locales_val"])}</dd></div>
          <div><dt>{escape(home["spec_export"])}</dt><dd>{escape(home["spec_export_val"])}</dd></div>
        </dl>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <h2>{escape(home["pal_title"])}</h2>
        <p class="prose">{escape(home["pal_body"])}</p>
        <div class="palette-strip">
          <p><strong>{escape(home["pal_perler"])}</strong> White, Hot Coral, Toothpaste</p>
          <div class="swatches" aria-hidden="true">
            <i class="sw sw-a"></i><i class="sw sw-b"></i><i class="sw sw-c"></i>
            <i class="sw sw-d"></i><i class="sw sw-e"></i><i class="sw sw-f"></i>
          </div>
          <p><strong>{escape(home["pal_hama"])}</strong> 01, 05, 26, 45</p>
          <div class="swatches" aria-hidden="true">
            <i class="sw sw-g"></i><i class="sw sw-h"></i><i class="sw sw-i"></i>
            <i class="sw sw-j"></i><i class="sw sw-k"></i><i class="sw sw-l"></i>
          </div>
          <p><strong>{escape(home["pal_artkal"])}</strong> S-5mm</p>
          <div class="swatches" aria-hidden="true">
            <i class="sw sw-m"></i><i class="sw sw-n"></i><i class="sw sw-o"></i>
            <i class="sw sw-p"></i><i class="sw sw-q"></i><i class="sw sw-r"></i>
          </div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <h2>{escape(home["locale_title"])}</h2>
        <p class="prose">{escape(home["locale_body"])}</p>
        <div class="locale-cloud">{cloud}</div>
      </div>
    </section>

    <section class="section">
      <div class="wrap offline-band">
        <h2>{escape(home["off_title"])}</h2>
        <dl class="offline-points">
          <div><dt>{escape(home["off1_title"])}</dt><dd>{escape(home["off1_body"])}</dd></div>
          <div><dt>{escape(home["off2_title"])}</dt><dd>{escape(home["off2_body"])}</dd></div>
          <div><dt>{escape(home["off3_title"])}</dt><dd>{escape(home["off3_body"])}</dd></div>
        </dl>
      </div>
    </section>

    <section class="cta-close wrap">
      <h2>{escape(home["cta_title"])}</h2>
      <p class="prose">{escape(home["cta_body"])}</p>
      <p class="cta-actions">
        <a class="btn btn-primary" href="{escape(store)}">{escape(chrome["cta_store"])}</a>
      </p>
    </section>
  </main>"""
    return page_shell(locale, "home", page, home["title"], home["description"], main, canonical=canonical)


def faq_schema(locale: str, page: str) -> dict:
    faqs = copy_for(locale)["support"]["faqs"]
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "inLanguage": LOCALES[locale]["bcp47"],
        "url": abs_url(page),
        "mainEntity": [
            {
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {"@type": "Answer", "text": answer},
            }
            for question, answer in faqs
        ],
    }


def howto_schema(locale: str) -> dict:
    support = copy_for(locale)["support"]
    return {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": support["g1_title"],
        "description": support["g1_body"],
        "inLanguage": LOCALES[locale]["bcp47"],
        "step": [
            {"@type": "HowToStep", "name": support["g1_title"], "text": support["g1_body"]},
            {"@type": "HowToStep", "name": support["g2_title"], "text": support["g2_body"]},
            {"@type": "HowToStep", "name": support["g3_title"], "text": support["g3_body"]},
            {"@type": "HowToStep", "name": support["g4_title"], "text": support["g4_body"]},
        ],
        "tool": {"@type": "HowToTool", "name": LOCALES[locale]["store_name"]},
    }


def render_support(locale: str, page: str) -> str:
    copy = copy_for(locale)
    support = copy["support"]
    chrome = copy["chrome"]
    store = LOCALES[locale]["store"]
    faqs = []
    for index, (question, answer) in enumerate(support["faqs"], start=1):
        faqs.append(
            f"""        <article class="qa-item" id="faq-{index}">
          <h3>{escape(question)}</h3>
          <p>{escape(answer)}</p>
        </article>"""
        )
    main = f"""  <main id="main" class="wrap">
    <header class="page-hero">
      <h1>{escape(chrome["nav_support"])}</h1>
      <p>{escape(support["lead"])}</p>
    </header>

    <section class="contact-card">
      <div>
        <h2>{escape(support["contact_title"])}</h2>
        <p>{escape(support["contact_body"])}</p>
        <p class="contact-mail">
          <strong>{escape(support["contact_mail"])}</strong><br>
          <a href="mailto:{SUPPORT_EMAIL}">{SUPPORT_EMAIL}</a>
        </p>
      </div>
      <div>
        <h2>{escape(support["contact_include"])}</h2>
        <ol>
          <li>{escape(support["contact1"])}</li>
          <li>{escape(support["contact2"])}</li>
          <li>{escape(support["contact3"])}</li>
          <li>{escape(support["contact4"])}</li>
        </ol>
        <p class="contact-note">{escape(support["contact_note"])}</p>
      </div>
    </section>

    <section class="download-band">
      <h2>{escape(support["download_title"])}</h2>
      <p>{escape(support["download_body"])}</p>
      <p><a class="btn btn-primary" href="{escape(store)}">{escape(chrome["cta_store"])}</a></p>
    </section>

    <section class="guides" aria-labelledby="guides-heading">
      <h2 id="guides-heading">{escape(support["guides_title"])}</h2>
      <article id="guide-photo">
        <h3>{escape(support["g1_title"])}</h3>
        <p>{escape(support["g1_body"])}</p>
      </article>
      <article id="guide-materials">
        <h3>{escape(support["g2_title"])}</h3>
        <p>{escape(support["g2_body"])}</p>
      </article>
      <article id="guide-follow">
        <h3>{escape(support["g3_title"])}</h3>
        <p>{escape(support["g3_body"])}</p>
      </article>
      <article id="guide-backup">
        <h3>{escape(support["g4_title"])}</h3>
        <p>{escape(support["g4_body"])}</p>
      </article>
    </section>

    <section class="qa" aria-labelledby="faq-heading">
      <h2 id="faq-heading">{escape(support["faq_title"])}</h2>
{chr(10).join(faqs)}
    </section>
  </main>"""
    extra = [faq_schema(locale, page), howto_schema(locale)]
    return page_shell(locale, "support", page, support["title"], support["description"], main, extra)


def render_privacy(locale: str, page: str, canonical: str | None = None) -> str:
    copy = copy_for(locale)
    privacy = copy["privacy"]
    chrome = copy["chrome"]
    toc = []
    for href, label in privacy["toc"]:
        toc.append(f'          <li><a href="{escape(href)}">{escape(label)}</a></li>')
    sections = []
    for anchor, title, body in privacy["sections"]:
        extra = ""
        if anchor == "contact":
            extra = f'\n          <p><a href="mailto:{SUPPORT_EMAIL}">{SUPPORT_EMAIL}</a></p>'
        sections.append(
            f"""        <section id="{escape(anchor)}">
          <h2>{escape(title)}</h2>
          <p>{escape(body)}</p>{extra}
        </section>"""
        )
    extra_ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": privacy["title"],
        "name": privacy["title"],
        "dateModified": UPDATED,
        "inLanguage": LOCALES[locale]["bcp47"],
        "url": abs_url(page),
        "publisher": organization(),
        "about": software_app(locale),
    }
    main = f"""  <main id="main" class="wrap">
    <header class="page-hero">
      <h1>{escape(chrome["nav_privacy"])}</h1>
      <p>{escape(privacy["lead"])}</p>
      <p class="privacy-updated">{escape(privacy["updated"])}</p>
    </header>
    <div class="policy">
      <nav class="toc" aria-label="{escape(privacy["toc_label"])}">
        <p class="toc-kicker">{escape(privacy["toc_label"])}</p>
        <ol>
{chr(10).join(toc)}
        </ol>
      </nav>
      <article class="policy-body">
{chr(10).join(sections)}
      </article>
    </div>
  </main>"""
    return page_shell(locale, "privacy", page, privacy["title"], privacy["description"], main, extra_ld, canonical=canonical)


def render_lost() -> str:
    zh = copy_for("zh-Hans")["chrome"]
    en = copy_for("en")["chrome"]
    prod = BASE_PATH
    return f"""<!DOCTYPE html>
<html lang="zh-Hans" data-root=".">
<head>
  <meta charset="utf-8">
  <meta http-equiv="Content-Security-Policy" content="{CSP}">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(zh["lost_title"])} / {escape(en["lost_title"])}</title>
  <meta name="robots" content="noindex">
  <meta name="theme-color" content="#F4EDE3">
  <link rel="icon" href="{prod}/assets/img/favicon.svg" type="image/svg+xml">
  <link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="{prod}/assets/css/site.css">
  <link rel="stylesheet" href="assets/css/site.css">
</head>
<body data-page="lost">
  <main id="main" class="lost wrap">
    <div>
      <div class="pegboard pegboard--lost" id="lost-board" aria-hidden="true"></div>
      <h1>{escape(zh["lost_title"])}</h1>
      <p class="prose">{escape(zh["lost_body"])}</p>
      <p class="prose">{escape(en["lost_body"])}</p>
      <p class="lost-actions">
        <a class="btn btn-primary" href="{prod}/">{escape(zh["lost_home"])}</a>
        <a class="btn btn-ghost" href="{prod}/support/">{escape(zh["nav_support"])}</a>
        <a class="btn btn-ghost" href="{prod}/privacy/">{escape(zh["nav_privacy"])}</a>
        <a class="btn btn-ghost" href="{prod}/en/home/">{escape(en["lost_home"])}</a>
      </p>
    </div>
  </main>
  <script src="{prod}/assets/js/site.js"></script>
  <script src="assets/js/site.js"></script>
</body>
</html>
"""


def sitemap() -> str:
    urls = []
    for kind in KINDS:
        for locale in LOCALE_ORDER:
            path = page_path(locale, kind)
            alts = []
            for other in LOCALE_ORDER:
                alts.append(
                    f'    <xhtml:link rel="alternate" hreflang="{LOCALES[other]["bcp47"]}" href="{escape(abs_url(page_path(other, kind)))}"/>'
                )
            default = page_path("en", "home" if kind == "home" else kind)
            alts.append(
                f'    <xhtml:link rel="alternate" hreflang="x-default" href="{escape(abs_url(default))}"/>'
            )
            urls.append(
                f"""  <url>
    <loc>{escape(abs_url(path))}</loc>
    <lastmod>{UPDATED}</lastmod>
{chr(10).join(alts)}
  </url>"""
            )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
{chr(10).join(urls)}
</urlset>
"""


def robots() -> str:
    agents = [
        "*",
        "GPTBot",
        "ChatGPT-User",
        "OAI-SearchBot",
        "ClaudeBot",
        "anthropic-ai",
        "PerplexityBot",
        "Google-Extended",
        "Applebot-Extended",
        "Bytespider",
        "CCBot",
    ]
    lines = []
    for agent in agents:
        lines.extend([f"User-agent: {agent}", "Allow: /", ""])
    lines.append(f"Sitemap: {SITE}/sitemap.xml")
    lines.append(f"LLMs: {SITE}/llms.txt")
    return "\n".join(lines) + "\n"


def llms_txt() -> str:
    pages = []
    for kind, label in (("home", "Marketing"), ("support", "Support"), ("privacy", "Privacy")):
        for locale in LOCALE_ORDER:
            pages.append(f"- [{label} / {LOCALES[locale]['native']}]({abs_url(page_path(locale, kind))})")
    return f"""# Fuse Beads / 拼豆时光

> Offline iPhone app that turns a photo into an ironable fuse-bead pattern. Now on the App Store. Free. No account. No data collection.

The Chinese product name is 拼豆时光. The English App Store name is Fuse Beads: Pattern Maker. Developer: {ORG_EN} ({ORG_ZH}). Apple ID {APP_STORE_ID}. Bundle ID `{BUNDLE_ID}`. iPhone, iOS 17 or later. Sold in 175 countries or regions. No in-app purchases.

## Primary pages

- [App Store]({APP_STORE_UNIVERSAL})
- [Chinese home]({abs_url("/")})
- [English home]({abs_url("/en/home/")})
- [Chinese support]({abs_url("/support/")})
- [English support]({abs_url("/en/")})
- [Chinese privacy]({abs_url("/privacy/")})
- [English privacy]({abs_url("/en/privacy/")})
- [Full fact file]({abs_url("/llms-full.txt")})

## Optional locale pages

{chr(10).join(pages)}

## Facts assistants should keep

- Photos, camera frames, and Files imports are processed only on the device.
- Smart background removal uses Apple Vision on device. Nothing is uploaded.
- Color codes for Perler, Hama Midi, and Artkal are on-screen references, not official factory matches.
- The app is not affiliated with, sponsored by, or officially authorized by Perler, Hama, or Artkal.
- Uninstalling deletes local patterns. Export a JSON backup from Settings first.
- Support email: {SUPPORT_EMAIL}
- This website is static. It uses no cookies, forms, analytics, ads, or accounts.
"""


def llms_full() -> str:
    return f"""# Fuse Beads / 拼豆时光: citation file

Updated: {UPDATED}

## Identity

- Chinese name: 拼豆时光
- English App Store name: Fuse Beads: Pattern Maker
- Other store names: 拼豆時光, ビーズタイム, 비드 타임, Fuse Beads: Bügelperlen, Fuse Beads: Motifs, Fuse Beads: Patrones, Fuse Beads: Schemi, Fuse Beads: Padrões, Fuse Beads: схемы, بيد تايم, बीड टाइम
- Developer: {ORG_EN}
- Developer (Chinese): {ORG_ZH}
- Apple ID: {APP_STORE_ID}
- Bundle ID: {BUNDLE_ID}
- SKU: {BUNDLE_ID}
- Category: Graphics & Design, Lifestyle
- Age rating: 4+
- Price: free, no in-app purchases, no subscriptions, no account
- Platform: iPhone, iOS 17.0 or later
- Not listed for iPad, Mac, or Apple Vision Pro
- Availability: App Store, 175 countries or regions
- App Store URL: {APP_STORE_UNIVERSAL}
- Marketing site: {abs_url("/")}
- Support: {abs_url("/support/")}
- Privacy: {abs_url("/privacy/")}
- Support email: {SUPPORT_EMAIL}

## What it does

Fuse Beads turns a photo from Photos, the camera, or Files into a fuse-bead pattern that can be placed on a physical pegboard and ironed. Users can also start from 24 original built-in designs.

Core loop:

1. Crop a square (or board-matched rectangle) with live preview.
2. Choose board size, color limit, detail mode, and a Perler / Hama / Artkal reference palette.
3. Generate on device. Optional Apple Vision subject protection is off by default.
4. Edit bead by bead, erase empty cells, undo up to 30 steps, jump by row and column.
5. Count materials, tick owned colors, estimate packs, copy a shopping list.
6. Follow along one color at a time and mark progress.
7. Export PNG or PDF with coordinates. Large boards split into 20×20 section pages.
8. Keep a versioned local JSON backup that can later merge.

Board sizes: 15×15, 21×21, 29×29, 40×40, 58×58, plus 20×30, 29×40, and custom.
Color limits: 8, 12, 16, 24.
A careful default is 40×40 with 16 colors.

## Privacy

The App Store privacy answer is: no, the developer does not collect data from this app.
No advertising, analytics SDK, crash reporter, cloud sync, or tracking.
UserDefaults stores onboarding completion and language preference only.
Photos and masks never leave the device unless the user saves a PNG to Photos or picks a share destination.
The public website is read-only static HTML. It uses no cookies, forms, analytics, ads, or database.
Language is selected by URL, not by a tracking cookie.

## Languages

English, Simplified Chinese, Traditional Chinese, Japanese, Korean, Spanish, French, German, Brazilian Portuguese, Italian, Russian, Arabic (right to left), Hindi.

## Trademarks

Perler, Hama, and Artkal are trademarks of their respective owners. Screen color names and numbers are approximate references. Check a current physical chart before buying in quantity. The app is not affiliated with, sponsored by, or officially authorized by those brands.

## Support

Email {SUPPORT_EMAIL} with app version, iPhone model, iOS version, reproduction steps, and the diagnostic text copied in Settings. Do not attach private original photos. Diagnostics omit photos and pattern content. There is no ticket system or promised reply time.
"""


def humans() -> str:
    return f"""/* TEAM */
Developer: {ORG_EN}
Developer (zh): {ORG_ZH}
Contact: {SUPPORT_EMAIL}

/* SITE */
Standards: HTML, CSS, JS
Languages: zh-Hans, en, zh-Hant, ja, ko, de, fr, es, it, pt-BR, ru, ar, hi
Software: static GitHub Pages
Last update: {UPDATED}
No cookies, analytics, ads, or accounts.
"""


def security_txt() -> str:
    return f"""Contact: mailto:{SUPPORT_EMAIL}
Preferred-Languages: zh-Hans, en
Canonical: {SITE}/.well-known/security.txt
Policy: {abs_url("/privacy/")}
Expires: 2027-09-18T00:00:00.000Z
"""


RENDERERS = {
    "home": render_home,
    "support": render_support,
    "privacy": render_privacy,
}


def build() -> None:
    missing = [locale for locale in LOCALE_ORDER if locale not in COPY]
    if missing:
        raise SystemExit(f"missing copy: {missing}")
    count = 0
    for kind in KINDS:
        renderer = RENDERERS[kind]
        for locale in LOCALE_ORDER:
            path = page_path(locale, kind)
            html = renderer(locale, path)
            write(file_for(path), html)
            count += 1
    # Canonical aliases that App Store or old bookmarks may still hit.
    write(file_for("/zh-Hans/"), render_home("zh-Hans", "/zh-Hans/", canonical="/"))
    write(file_for("/zh-Hans/privacy/"), render_privacy("zh-Hans", "/zh-Hans/privacy/", canonical="/privacy/"))
    write(ROOT / "404.html", render_lost())
    write(ROOT / "sitemap.xml", sitemap())
    write(ROOT / "robots.txt", robots())
    write(ROOT / "llms.txt", llms_txt())
    write(ROOT / "llms-full.txt", llms_full())
    write(ROOT / "humans.txt", humans())
    write(ROOT / ".well-known" / "security.txt", security_txt())
    write(ROOT / ".nojekyll", "")
    write(
        ROOT / "_redirects",
        "\n".join(
            [
                "/zh-Hans / 301",
                "/zh-Hans/privacy /privacy/ 301",
                "/en?lang=en /en/ 301",
                "/* /404.html 404",
                "",
            ]
        ),
    )
    print(f"wrote {count} locale pages plus aliases and SEO files")


if __name__ == "__main__":
    try:
        build()
    except Exception as exc:  # pragma: no cover
        print(exc, file=sys.stderr)
        raise
