"""Network examples run against installed candidates; HTML stays reproducible."""

import importlib
from pathlib import Path

import html5lib
import pytest

from scripts.build_format_guides import NETWORK, render
from scripts.check_examples import Examples

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("name", NETWORK)
def test_network_guide(name):
    page = (ROOT / f"site/{name}.html").read_text()
    assert page == render(name)
    html5lib.HTMLParser(strict=True).parse(page)
    if name == "cli":
        return
    source = (ROOT / f"docs/{name}.md").read_text()
    module = importlib.import_module(f"golded_ftn_{name}")
    for exported in module.__all__:
        assert f"### `{exported}`" in source
    examples = Examples()
    examples.feed(page)
    assert examples.items
    for identity, code in examples.items.items():
        exec(compile(code, identity, "exec"), {})
