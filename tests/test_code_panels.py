"""Code panels preserve source and wire each copy action to one code block."""

from pathlib import Path

import html5lib
import markdown
import pytest

ROOT = Path(__file__).resolve().parents[1]
NS = {"h": "http://www.w3.org/1999/xhtml"}


@pytest.mark.parametrize("name", ["core-api", "writers"])
def test_fenced_source_survives_panel_rendering(name):
    source = markdown.markdown(
        (ROOT / "docs" / f"{name}.md").read_text(),
        extensions=["tables", "fenced_code", "toc"],
    )
    original = html5lib.parseFragment(source)
    page = html5lib.HTMLParser(strict=True).parse(
        (ROOT / "site" / f"{name}.html").read_text()
    )
    expected = [
        "".join(code.itertext()) for code in original.findall(".//h:pre/h:code", NS)
    ]
    codes = page.findall('.//h:div[@class="code-pane"]/h:pre/h:code', NS)
    assert ["".join(code.itertext()) for code in codes] == expected
    buttons = page.findall('.//h:div[@class="code-head"]/h:button', NS)
    assert [button.get("data-copy") for button in buttons] == [
        code.get("id") for code in codes
    ]
    ids = [element.get("id") for element in page.iter() if element.get("id")]
    assert len(ids) == len(set(ids))
    assert page.findall('.//h:span[@class="kn"]', NS)


def test_library_guide_code_blocks_have_highlighting():
    page = html5lib.HTMLParser(strict=True).parse(
        (ROOT / "site/guide.html").read_text()
    )
    codes = page.findall(".//h:pre/h:code", NS)
    assert len(codes) == 10
    for code in codes:
        assert code.findall("h:span", NS), code.get("id")


def test_inline_highlighting_preserves_code_and_does_not_touch_blocks():
    from scripts.code_panels import inline_code

    source = "<p>Address <code>zone:net/node</code> and <code>None</code>.</p>"
    source += '<pre><code>print("unchanged")</code></pre>'
    rendered = html5lib.parseFragment(inline_code(source))
    codes = rendered.findall(".//h:code", NS)
    assert ["".join(code.itertext()) for code in codes] == [
        "zone:net/node",
        "None",
        'print("unchanged")',
    ]
    assert codes[0].get("class") == "inline-code"
    assert codes[1].find('h:span[@class="kc"]', NS) is not None
    assert list(codes[2]) == []
