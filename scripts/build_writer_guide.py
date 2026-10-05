"""Render the editable writer notes with the guide's existing visual design."""

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


def render() -> str:
    guide = (ROOT / "site/guide.html").read_text(encoding="utf-8")
    style = re.search(r"<style>.*?</style>", guide, re.S)
    masthead = re.search(r"<header class=\"masthead\">.*?</header>", guide, re.S)
    script = re.search(r"<script>.*?</script>", guide, re.S)
    footer = re.search(r"<footer>.*?</footer>", guide, re.S)
    assert style and masthead and script and footer
    renderer = markdown.Markdown(extensions=["tables", "fenced_code", "toc"])
    body = renderer.convert(
        (ROOT / "docs/writers.md").read_text(encoding="utf-8"),
    )
    body = '<div class="eyebrow">Old bases. Careful edits.</div>' + body
    body = body.replace('href="core-api.md"', 'href="core-api.html"')
    body = body.replace(
        '<code class="language-python">',
        '<code id="writer_formats" data-language="python" data-mode="run">',
    )
    body = re.sub(
        r"<table>.*?</table>",
        lambda match: '<div class="table-wrap">' + match[0] + "</div>",
        body,
        flags=re.S,
    )
    body = code_panels(body, "writer")
    body = inline_code(body)
    body = layout(
        body,
        '<nav aria-label="Documentation"><a href="index.html">Documentation home</a> · '
        '<a href="guide.html">Library guide</a> · '
        '<a href="core-api.html">Core API</a></nav>',
        "writers.html",
    )
    return (
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<title>GoldED for Python · Editing message bases</title>"
        + style[0]
        + '</head><body><a class="skip" href="#start">Skip to content</a>'
        '<div class="page">'
        + masthead[0].replace('href="#start"', 'href="index.html"')
        + '<div class="shell"><div class="bar"><span>WRITER CONTRACT</span>'
        "<span>1.2.0 WORKING SOURCES · OFFLINE</span></div>"
        + body
        + "</div>"
        + footer[0]
        + "</div>"
        + script[0]
        + '<span id="copy-status" role="status" class="sr-only"></span>'
        "</body></html>\n"
    )


if __name__ == "__main__":
    (ROOT / "site/writers.html").write_text(render(), encoding="utf-8")
