#!/usr/bin/env python3
"""Check generated site metadata, crawl paths, structured data and local links.

Run after build.py. Add --base-url to compare a served/deployed copy byte for byte.
Only Python's standard library is required; external websites are not requested.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

import config

ROOT = Path(__file__).resolve().parents[1]
KINDS = ("home", "support", "privacy")
EXPECTED_VERSION = getattr(config, "APP_VERSION", "1.1.2")
SITEMAP_NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9", "x": "http://www.w3.org/1999/xhtml"}


def normalized(text: str) -> str:
    return " ".join(text.split())


class Page(HTMLParser):
    def __init__(self, source: str):
        super().__init__(convert_charrefs=True)
        self.html: dict[str, str] = {}
        self.meta: dict[str, str] = {}
        self.canonicals: list[str] = []
        self.alternates: list[tuple[str, str]] = []
        self.references: list[str] = []
        self.ids: list[str] = []
        self.h1_count = 0
        self.title = ""
        self.visible: list[str] = []
        self.ld_sources: list[str] = []
        self.faqs: list[tuple[str, str]] = []
        self._in_title = False
        self._ignored: str | None = None
        self._ld: list[str] | None = None
        self._faq: dict[str, list[str]] | None = None
        self._faq_field: str | None = None
        self.feed(source)
        self.close()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {key: value or "" for key, value in attrs}
        if tag == "html":
            self.html = a
        if tag == "title":
            self._in_title = True
        if tag in {"script", "style"}:
            self._ignored = tag
            if tag == "script" and a.get("type") == "application/ld+json":
                self._ld = []
        if tag == "meta":
            self.meta[a.get("name", a.get("property", ""))] = a.get("content", "")
        if tag == "link":
            rel = a.get("rel", "").split()
            if "canonical" in rel:
                self.canonicals.append(a.get("href", ""))
            if "alternate" in rel and a.get("hreflang"):
                self.alternates.append((a["hreflang"], a.get("href", "")))
        if tag == "h1":
            self.h1_count += 1
        if "id" in a:
            self.ids.append(a["id"])
        for name in ("href", "src", "poster"):
            if a.get(name):
                self.references.append(a[name])
        if a.get("srcset"):
            self.references.extend(item.strip().split()[0] for item in a["srcset"].split(",") if item.strip())
        if tag == "article" and "qa-item" in a.get("class", "").split():
            self._faq = {"question": [], "answer": []}
        if self._faq is not None and tag in {"h3", "p"}:
            self._faq_field = "question" if tag == "h3" else "answer"

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag == "script" and self._ld is not None:
            self.ld_sources.append("".join(self._ld))
            self._ld = None
        if tag == self._ignored:
            self._ignored = None
        if tag in {"h3", "p"}:
            self._faq_field = None
        if tag == "article" and self._faq is not None:
            self.faqs.append(tuple(normalized(" ".join(self._faq[key])) for key in ("question", "answer")))
            self._faq = None

    def handle_data(self, data: str) -> None:
        if self._ld is not None:
            self._ld.append(data)
        if self._in_title:
            self.title += data
        if self._ignored is None:
            self.visible.append(data)
            if self._faq is not None and self._faq_field:
                self._faq[self._faq_field].append(data)


def schema_nodes(value):
    if isinstance(value, dict):
        if "@type" in value:
            yield value
        for child in value.values():
            yield from schema_nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from schema_nodes(child)


def has_type(node: dict, kind: str) -> bool:
    types = node.get("@type", [])
    return kind in (types if isinstance(types, list) else [types])


def local_file(path: str) -> Path:
    return ROOT / path.lstrip("/") / "index.html" if path.endswith("/") else ROOT / path.lstrip("/")


def resolve_reference(page_path: str, reference: str) -> tuple[Path, str] | None:
    absolute = urlsplit(urljoin(config.abs_url(page_path), reference))
    site = urlsplit(config.SITE)
    if absolute.scheme not in {"http", "https"} or absolute.netloc != site.netloc:
        return None
    prefix = site.path.rstrip("/")
    decoded = unquote(absolute.path)
    if prefix and decoded != prefix and not decoded.startswith(prefix + "/"):
        return None
    relative = decoded[len(prefix):] or "/"
    target = local_file(relative)
    if target.is_dir():
        target = target / "index.html"
    return target, unquote(absolute.fragment)


def run_checks(base_url: str | None) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    counters: Counter = Counter()
    parsed: dict[Path, Page] = {}
    canonical_pages: dict[str, tuple[str, str, Path]] = {}
    fetch_files: set[Path] = set()
    titles: Counter = Counter()
    descriptions: Counter = Counter()

    def require(condition: bool, message: str) -> None:
        counters["assertions"] += 1
        if not condition:
            errors.append(message)

    def parse(path: Path) -> Page | None:
        if path in parsed:
            return parsed[path]
        if not path.is_file():
            errors.append(f"Missing file: {path.relative_to(ROOT)}")
            return None
        try:
            page = Page(path.read_text(encoding="utf-8"))
            parsed[path] = page
            fetch_files.add(path)
            return page
        except (OSError, UnicodeError) as exc:
            errors.append(f"Cannot parse {path.relative_to(ROOT)}: {exc}")
            return None

    for kind in KINDS:
        for locale in config.LOCALE_ORDER:
            route = config.page_path(locale, kind)
            canonical_pages[config.abs_url(route)] = (locale, kind, local_file(route))

    for url, (locale, kind, path) in canonical_pages.items():
        page = parse(path)
        if page is None:
            continue
        label = str(path.relative_to(ROOT))
        counters["canonical_pages"] += 1
        titles[normalized(page.title)] += 1
        descriptions[normalized(page.meta.get("description", ""))] += 1
        require(bool(normalized(page.title)), f"{label}: empty title")
        require(bool(normalized(page.meta.get("description", ""))), f"{label}: empty description")
        require(page.h1_count == 1, f"{label}: expected one h1, got {page.h1_count}")
        require(page.html.get("lang") == config.LOCALES[locale]["html_lang"], f"{label}: incorrect html lang")
        require(page.html.get("dir") == config.LOCALES[locale]["dir"], f"{label}: incorrect direction")
        require(page.canonicals == [url], f"{label}: incorrect canonical: {page.canonicals}")
        require("noindex" not in page.meta.get("robots", ""), f"{label}: canonical page must be indexable")
        require(page.meta.get("og:url") == url, f"{label}: og:url differs from canonical")
        expected_alternates = {config.LOCALES[other]["bcp47"]: config.abs_url(config.page_path(other, kind)) for other in config.LOCALE_ORDER}
        expected_alternates["x-default"] = config.abs_url(config.page_path("en", kind))
        require(len(page.alternates) == 14 and dict(page.alternates) == expected_alternates, f"{label}: expected all 13 locale alternates and x-default")
        for lang, alternate in page.alternates:
            target = canonical_pages.get(alternate)
            require(target is not None, f"{label}: alternate {lang} does not point to a canonical page")
            if target:
                target_page = parse(target[2])
                if target_page:
                    require((config.LOCALES[locale]["bcp47"], url) in target_page.alternates, f"{label}: alternate {lang} is not reciprocal")
        nodes = []
        require(bool(page.ld_sources), f"{label}: missing JSON-LD")
        for raw in page.ld_sources:
            try:
                nodes.extend(schema_nodes(json.loads(raw)))
                counters["json_ld_blocks"] += 1
            except json.JSONDecodeError as exc:
                errors.append(f"{label}: invalid JSON-LD: {exc}")
        apps = [node for node in nodes if has_type(node, "MobileApplication") or has_type(node, "SoftwareApplication")]
        require(bool(apps), f"{label}: missing app structured data")
        for app in apps:
            require(app.get("softwareVersion") == EXPECTED_VERSION, f"{label}: stale softwareVersion {app.get('softwareVersion')}")
            device_text = json.dumps({key: app.get(key, "") for key in ("operatingSystem", "availableOnDevice", "supportedDevice")})
            require("iPhone" in device_text and "iPad" in device_text, f"{label}: app structured data must state iPhone and iPad support")
        webpage_nodes = [node for node in nodes if has_type(node, "WebPage")]
        require(any(node.get("dateModified") == config.UPDATED for node in webpage_nodes), f"{label}: missing current WebPage dateModified")
        if kind == "support":
            faq_nodes = [node for node in nodes if has_type(node, "FAQPage")]
            require(len(faq_nodes) == 1, f"{label}: expected one FAQPage")
            if faq_nodes:
                schema_faqs = [(normalized(item.get("name", "")), normalized(item.get("acceptedAnswer", {}).get("text", ""))) for item in faq_nodes[0].get("mainEntity", [])]
                require(bool(page.faqs) and page.faqs == schema_faqs, f"{label}: visible FAQ questions/answers differ from FAQPage")
                counters["faq_pairs"] += len(page.faqs)

    for label, counts in (("title", titles), ("description", descriptions)):
        for value, count in counts.items():
            require(count == 1, f"Duplicate canonical {label} ({count} pages): {value}")

    for alias, canonical in (("/zh-Hans/", "/"), ("/zh-Hans/privacy/", "/privacy/")):
        page = parse(local_file(alias))
        if page:
            require(page.canonicals == [config.abs_url(canonical)], f"{alias}: incorrect alias canonical")
            require("noindex" in page.meta.get("robots", ""), f"{alias}: alias should have noindex")
            counters["alias_pages"] += 1
    lost = parse(ROOT / "404.html")
    if lost:
        require("noindex" in lost.meta.get("robots", ""), "404.html: missing noindex")

    try:
        sitemap_file = ROOT / "sitemap.xml"
        xml = ET.parse(sitemap_file).getroot()
        fetch_files.add(sitemap_file)
        entries = xml.findall("s:url", SITEMAP_NS)
        locations = [entry.findtext("s:loc", namespaces=SITEMAP_NS) for entry in entries]
        require(len(locations) == 39 and set(locations) == set(canonical_pages), "sitemap.xml: expected exactly the 39 canonical pages")
        for entry in entries:
            location = entry.findtext("s:loc", namespaces=SITEMAP_NS)
            require(entry.findtext("s:lastmod", namespaces=SITEMAP_NS) == config.UPDATED, f"sitemap.xml: incorrect lastmod for {location}")
            alternates = [(item.get("hreflang"), item.get("href")) for item in entry.findall("x:link", SITEMAP_NS)]
            target = canonical_pages.get(location)
            if target and parse(target[2]):
                require(alternates == parse(target[2]).alternates, f"sitemap.xml: alternates disagree with HTML for {location}")
        counters["sitemap_urls"] = len(locations)
    except (OSError, ET.ParseError) as exc:
        errors.append(f"sitemap.xml: {exc}")

    for filename in ("robots.txt", "llms.txt", "llms-full.txt", "humans.txt", ".well-known/security.txt"):
        path = ROOT / filename
        require(path.is_file(), f"Missing discovery file: {filename}")
        if not path.is_file():
            continue
        fetch_files.add(path)
        text = path.read_text(encoding="utf-8")
        if filename.startswith("llms"):
            require(config.UPDATED in text, f"{filename}: missing current date")
            require("iPhone" in text and "iPad" in text, f"{filename}: missing supported devices")
            for stale in ("Not listed for iPad", "iPhone-only", "Offline iPhone app", "Sold in 175", "175 countries or regions"):
                require(stale.lower() not in text.lower(), f"{filename}: stale claim: {stale}")
        if filename == "robots.txt":
            require(f"Sitemap: {config.SITE}/sitemap.xml" in text, "robots.txt: incorrect sitemap URL")
            require("Disallow: /\n" not in text, "robots.txt: site-wide block")

    # Check references after all pages have been read, including cross-page anchors.
    for path, page in list(parsed.items()):
        relative_path = path.relative_to(ROOT).as_posix()
        route = "/" + relative_path.removesuffix("index.html")
        if not relative_path.endswith("index.html"):
            route = "/" + relative_path
        require(len(page.ids) == len(set(page.ids)), f"{relative_path}: duplicate id attributes")
        for reference in page.references:
            resolved = resolve_reference(route, reference)
            if not resolved:
                continue
            target, fragment = resolved
            require(target.is_file(), f"{relative_path}: broken local reference {reference}")
            if not target.is_file():
                continue
            fetch_files.add(target)
            if fragment and target.suffix == ".html":
                target_page = parse(target)
                if target_page:
                    require(fragment in target_page.ids, f"{relative_path}: missing anchor {reference}")
            counters["local_references"] += 1
        for image in re.findall(r'<img\b[^>]*>', path.read_text(encoding="utf-8"), flags=re.I):
            require(bool(re.search(r'\balt\s*=', image, re.I)), f"{relative_path}: image missing alt attribute")
            require(bool(re.search(r'\bwidth\s*=', image, re.I)) and bool(re.search(r'\bheight\s*=', image, re.I)), f"{relative_path}: image missing intrinsic dimensions")

    # CSS font/image URLs are not represented in HTML and must also resolve locally.
    for css in ROOT.glob("assets/**/*.css"):
        fetch_files.add(css)
        for reference in re.findall(r'url\(\s*[\'\"]?([^\'\"\)]+)', css.read_text(encoding="utf-8")):
            resolved = resolve_reference("/" + css.relative_to(ROOT).as_posix(), reference.strip())
            if resolved:
                target, _ = resolved
                require(target.is_file(), f"{css.relative_to(ROOT)}: broken resource {reference}")
                if target.is_file():
                    fetch_files.add(target)
    # Verify all delivered assets, including lazily referenced gallery assets.
    fetch_files.update(path for path in (ROOT / "assets").rglob("*") if path.is_file())
    counters["local_files"] = len(fetch_files)

    remote = []
    if base_url:
        def fetch(path: Path) -> dict:
            relative = path.relative_to(ROOT).as_posix()
            served_path = relative.removesuffix("index.html") if relative.endswith("index.html") else relative
            url = base_url.rstrip("/") + "/" + served_path
            try:
                request = Request(url, headers={"User-Agent": "BeadTime-Site-Check/1.0"})
                with urlopen(request, timeout=25) as response:
                    body = response.read()
                    status = response.status
                expected = hashlib.sha256(path.read_bytes()).hexdigest()
                actual = hashlib.sha256(body).hexdigest()
                return {"path": served_path or "/", "status": status, "matches": expected == actual, "sha256": actual}
            except (HTTPError, URLError, OSError, TimeoutError) as exc:
                return {"path": served_path or "/", "matches": False, "error": str(exc)}

        with ThreadPoolExecutor(max_workers=6) as pool:
            futures = {pool.submit(fetch, path): path for path in sorted(fetch_files)}
            for future in as_completed(futures):
                result = future.result()
                remote.append(result)
                require(result["matches"], f"Served copy mismatch: {result['path']} ({result.get('error', result.get('status'))})")
        counters["remote_files"] = len(remote)
        remote.sort(key=lambda item: item["path"])

    return {"ok": not errors, "checked_at": datetime.now(timezone.utc).isoformat(), "version": EXPECTED_VERSION, "content_updated": config.UPDATED, "base_url": base_url, "counts": dict(counters), "errors": errors, "warnings": warnings, **({"remote": remote} if base_url else {})}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", help="Optional served site root, e.g. http://127.0.0.1:4173 or the GitHub Pages URL")
    parser.add_argument("--output", type=Path, help="Also save the complete JSON report to this path")
    args = parser.parse_args()
    report = run_checks(args.base_url)
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
