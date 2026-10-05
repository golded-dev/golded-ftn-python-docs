"""Render the four format references using the library guide's shared shell."""

import html
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
FORMATS = {
    "msg": ("MSG and Opus", "Individual files. Complete messages."),
    "jam": ("JAM", "Indexed messages. Preserved metadata."),
    "squish": ("Squish", "Linked frames. Stable identities."),
    "hudson": ("Hudson", "Shared files. Explicit boards."),
}

REFERENCES = FORMATS | {"glossary": ("Terminology", "Old jargon. Plain explanations.")}


def render(name: str) -> str:
    title, eyebrow = REFERENCES[name]
    reference_label = "DOCUMENTATION" if name == "glossary" else "FORMAT REFERENCE"
    guide = (ROOT / "site/guide.html").read_text(encoding="utf-8")
    pieces = {}
    for key, pattern in {
        "style": r"<style>.*?</style>",
        "masthead": r'<header class="masthead">.*?</header>',
        "footer": r"<footer>.*?</footer>",
        "script": r"<script>.*?</script>",
    }.items():
        match = re.search(pattern, guide, re.S)
        assert match
        pieces[key] = match[0]
    body = markdown.markdown(
        (ROOT / "docs" / f"{name}.md").read_text(encoding="utf-8"),
        extensions=["tables", "fenced_code", "toc"],
    )
    counter = 0

    def example(match: re.Match[str]) -> str:
        nonlocal counter
        counter += 1
        return (
            f'<code id="{name}_example_{counter}" '
            'data-language="python" data-mode="run">'
        )

    body = re.sub(r'<code class="language-python">', example, body)
    body = re.sub(
        r"<table>.*?</table>",
        lambda match: '<div class="table-wrap">' + match[0] + "</div>",
        body,
        flags=re.S,
    )
    body = code_panels(body, name)
    body = inline_code(body)
    body = layout(
        f'<div class="eyebrow">{html.escape(eyebrow)}</div>' + body,
        '<nav aria-label="Documentation"><a href="index.html">Documentation home</a>'
        "</nav>",
        f"{name}.html",
    )
    return (
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>GoldED for Python · {html.escape(title)} reference</title>"
        + pieces["style"]
        + '</head><body><a class="skip" href="#start">Skip to content</a>'
        '<div class="page">'
        + pieces["masthead"]
        + '<div class="shell"><div class="bar">'
        f"<span>{html.escape(title.upper())} / {reference_label}</span>"
        "<span>1.2.0 WORKING SOURCES · OFFLINE WRITERS</span></div>"
        + body
        + "</div>"
        + pieces["footer"]
        + "</div>"
        + pieces["script"]
        + '<span id="copy-status" role="status" class="sr-only"></span>'
        "</body></html>\n"
    )


if __name__ == "__main__":
    for name in REFERENCES:
        (ROOT / "site" / f"{name}.html").write_text(render(name), encoding="utf-8")
