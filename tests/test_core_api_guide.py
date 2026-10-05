"""Check the rendered public API reference and its executable examples."""

import re
from pathlib import Path

import golded_ftn
import html5lib

from scripts.build_api_guide import render
from scripts.check_examples import Examples

ROOT = Path(__file__).resolve().parents[1]


def test_core_reference_covers_public_exports():
    source = (ROOT / "docs/core-api.md").read_text(encoding="utf-8")
    headings = re.findall(r"^### `([^`]+)`$", source, re.M)
    assert sorted(headings) == sorted(golded_ftn.__all__)


def test_core_page_matches_source_and_valid_html():
    page = (ROOT / "site/core-api.html").read_text(encoding="utf-8")
    assert page == render()
    html5lib.HTMLParser(strict=True).parse(page)


def test_core_reference_examples():
    examples = Examples()
    examples.feed((ROOT / "site/core-api.html").read_text(encoding="utf-8"))
    assert examples.items
    for name, source in examples.items.items():
        exec(compile(source, name, "exec"), {})


def test_reference_internal_links_resolve():
    from html.parser import HTMLParser
    from urllib.parse import unquote, urlsplit

    class Links(HTMLParser):
        def __init__(self):
            super().__init__()
            self.targets = []
            self.ids = set()

        def handle_starttag(self, tag, attrs):
            values = dict(attrs)
            if values.get("id"):
                self.ids.add(values["id"])
            if tag == "a" and values.get("href"):
                self.targets.append(values["href"])

    pages = {}
    for name in (
        "index.html",
        "guide.html",
        "writers.html",
        "core-api.html",
        "glossary.html",
        "msg.html",
        "jam.html",
        "squish.html",
        "hudson.html",
    ):
        parsed = Links()
        parsed.feed((ROOT / "site" / name).read_text(encoding="utf-8"))
        pages[name] = parsed
    for name, page in pages.items():
        for href in page.targets:
            target = urlsplit(href)
            if target.scheme or target.netloc:
                continue
            filename = unquote(target.path) or name
            assert (ROOT / "site" / filename).is_file(), (name, href)
            if target.fragment:
                assert (
                    filename in pages
                    and unquote(target.fragment) in pages[filename].ids
                ), (name, href)
