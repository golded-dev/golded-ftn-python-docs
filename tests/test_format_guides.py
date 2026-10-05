"""Format references render reproducibly and run their synthetic examples."""

import importlib
from pathlib import Path

import html5lib
import pytest

from scripts.build_format_guides import FORMATS, render
from scripts.check_examples import Examples

ROOT = Path(__file__).resolve().parents[1]
NS = {"h": "http://www.w3.org/1999/xhtml"}


@pytest.mark.parametrize("name", FORMATS)
def test_format_page_and_examples(name):
    source = (ROOT / "site" / f"{name}.html").read_text(encoding="utf-8")
    assert source == render(name)
    tree = html5lib.HTMLParser(strict=True).parse(source)
    assert tree.find('.//h:div[@class="eyebrow"]', NS) is not None
    examples = Examples()
    examples.feed(source)
    assert examples.items
    for identity, code in examples.items.items():
        exec(compile(code, identity, "exec"), {})
    for code in tree.findall(".//h:pre/h:code", NS):
        assert code.findall("h:span", NS)


def test_glossary_renders_and_explains_key_terms():
    source = (ROOT / "site/glossary.html").read_text(encoding="utf-8")
    assert source == render("glossary")
    tree = html5lib.HTMLParser(strict=True).parse(source)
    text = "".join(tree.itertext())
    for term in (
        "FTN",
        "Netmail",
        "Echomail",
        "MSGID",
        "UID",
        "Tosser",
        "Revision token",
    ):
        assert term in text


@pytest.mark.parametrize("name", FORMATS)
def test_format_reference_names_all_public_exports(name):
    module = importlib.import_module(f"golded_ftn_{name}")
    source = (ROOT / "docs" / f"{name}.md").read_text(encoding="utf-8")
    for exported in module.__all__:
        assert f"`{exported}`" in source
