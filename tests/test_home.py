"""The documentation home selects a guide rather than duplicating it."""

from pathlib import Path

import html5lib

ROOT = Path(__file__).resolve().parents[1]
NS = {"h": "http://www.w3.org/1999/xhtml"}


def test_home_links_to_each_documentation_page():
    page = (ROOT / "site/index.html").read_text(encoding="utf-8")
    tree = html5lib.HTMLParser(strict=True).parse(page)
    nav = tree.find('.//h:nav[@aria-label="Documentation pages"]', NS)
    assert nav is not None
    links = nav.findall("h:a", NS)
    assert [link.get("href") for link in links] == [
        "guide.html",
        "core-api.html",
        "writers.html",
    ]
    assert [link.find("h:div/h:h2", NS).text for link in links] == [
        "Library guide",
        "Core API reference",
        "Editing message bases",
    ]
    assert tree.find(".//h:pre", NS) is None


def test_subpages_link_home():
    for name in ("guide.html", "core-api.html", "writers.html"):
        tree = html5lib.HTMLParser(strict=True).parse(
            (ROOT / "site" / name).read_text(encoding="utf-8")
        )
        assert tree.find('.//h:main//h:a[@href="index.html"]', NS) is not None
        assert tree.find('.//h:div[@class="layout"]/h:aside', NS) is not None
        assert tree.find('.//h:nav[@aria-label="Guide sections"]', NS) is not None
        assert tree.find(".//h:footer", NS) is not None


def test_shared_navigation_marks_each_current_page():
    pages = (
        "index.html",
        "guide.html",
        "core-api.html",
        "writers.html",
        "glossary.html",
        "msg.html",
        "jam.html",
        "squish.html",
        "hudson.html",
    )
    for name in pages:
        tree = html5lib.HTMLParser(strict=True).parse(
            (ROOT / "site" / name).read_text(encoding="utf-8")
        )
        assert tree.find('.//h:div[@class="layout"]/h:aside', NS) is not None
        nav = tree.find('.//h:nav[@class="page-nav"]', NS)
        assert nav is not None
        all_links = tree.findall(".//h:aside//h:nav/h:a", NS)
        page_links = [
            link for link in all_links if not link.get("href").startswith("#")
        ]
        assert [link.get("href") for link in page_links] == list(pages)
        current = [link for link in page_links if link.get("aria-current") == "page"]
        assert len(current) == 1 and current[0].get("href") == name
        if name != "index.html":
            assert (
                tree.find('.//h:details[@class="contents"]/h:summary', NS).text
                == "On this page"
            )


def test_home_links_to_formats_and_terminology():
    tree = html5lib.HTMLParser(strict=True).parse(
        (ROOT / "site/index.html").read_text(encoding="utf-8")
    )
    nav = tree.find('.//h:nav[@aria-label="Format references"]', NS)
    assert [link.get("href") for link in nav.findall("h:a", NS)] == [
        "msg.html",
        "jam.html",
        "squish.html",
        "hudson.html",
    ]
    assert tree.find('.//h:main//h:a[@href="glossary.html"]', NS) is not None
