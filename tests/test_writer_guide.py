"""Run the published writer example against installed package wheels."""

import contextlib
import io
from pathlib import Path

import html5lib

from scripts.build_writer_guide import render
from scripts.check_examples import Examples

ROOT = Path(__file__).resolve().parents[1]


def test_writer_page_matches_editable_source():
    page = (ROOT / "site/writers.html").read_text(encoding="utf-8")
    assert page == render()
    html5lib.HTMLParser(strict=True).parse(page)


def test_writer_html_example():
    examples = Examples()
    examples.feed((ROOT / "site/writers.html").read_text(encoding="utf-8"))
    assert set(examples.items) == {"writer_formats"}
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        exec(compile(examples.items["writer_formats"], "writer_formats", "exec"), {})
    assert stdout.getvalue().splitlines() == ["msg", "jam", "squish", "hudson"]
