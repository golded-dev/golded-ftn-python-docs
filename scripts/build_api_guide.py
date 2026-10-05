"""Copy the canonical core reference and render it with the guide's design."""

import argparse
import re
from pathlib import Path

import markdown

if __package__:
    from .code_panels import code_panels, inline_code
    from .page_layout import layout
else:
    from code_panels import code_panels, inline_code
    from page_layout import layout

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "golded-ftn-python/docs/api.md"


def render() -> str:
    guide = (ROOT / "site/guide.html").read_text(encoding="utf-8")
    style = re.search(r"<style>.*?</style>", guide, re.S)
    masthead = re.search(r'<header class="masthead">.*?</header>', guide, re.S)
    script = re.search(r"<script>.*?</script>", guide, re.S)
    footer = re.search(r"<footer>.*?</footer>", guide, re.S)
    assert style and masthead and script and footer
    renderer = markdown.Markdown(extensions=["tables", "fenced_code", "toc"])
    body = renderer.convert((ROOT / "docs/core-api.md").read_text(encoding="utf-8"))
    body = body.replace(
        'href="php-api.md"',
        'href="https://github.com/golded-dev/golded-ftn-python/blob/main/docs/php-api.md"',
    ).replace(
        'href="../../golded-ftn-python-docs/docs/writers.md"', 'href="writers.html"'
    )
    body = body.replace("\\|", "|")
    body = '<div class="eyebrow">Old formats. Shared values.</div>' + body
    counter = 0

    def example(match: re.Match[str]) -> str:
        nonlocal counter
        counter += 1
        return f'<code id="core_api_{counter}" data-language="python" data-mode="run">'

    body = re.sub(r'<code class="language-python">', example, body)
    body = re.sub(
        r"<table>.*?</table>",
        lambda match: '<div class="table-wrap">' + match[0] + "</div>",
        body,
        flags=re.S,
    )
    body = code_panels(body, "core_api")
    body = inline_code(body)
    body = layout(
        body,
        '<nav aria-label="Documentation"><a href="index.html">Documentation home</a> · '
        '<a href="guide.html">Library guide</a> · '
        '<a href="writers.html">Writer contract</a></nav>',
        "core-api.html",
    )
    return (
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<title>GoldED for Python · Core API reference</title>"
        + style[0]
        + '</head><body><a class="skip" href="#start">Skip to content</a>'
        '<div class="page">'
        + masthead[0].replace('href="#start"', 'href="index.html"')
        + '<div class="shell"><div class="bar"><span>CORE API REFERENCE</span>'
        "<span>1.2.0 WORKING SOURCES</span></div>"
        + body
        + "</div>"
        + footer[0]
        + "</div>"
        + script[0]
        + '<span id="copy-status" role="status" class="sr-only"></span>'
        "</body></html>\n"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sync", action="store_true", help="Copy docs/api.md from the sibling core"
    )
    args = parser.parse_args()
    if args.sync:
        (ROOT / "docs/core-api.md").write_text(
            SOURCE.read_text(encoding="utf-8"), encoding="utf-8"
        )
    (ROOT / "site/core-api.html").write_text(render(), encoding="utf-8")
