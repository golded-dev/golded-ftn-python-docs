"""Render Markdown fences as the library guide's copyable code panels."""

import html
import re

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexer import inherit
from pygments.lexers import BashLexer, PythonLexer
from pygments.token import Name, Operator


class TerminalLexer(BashLexer):
    """Make command starts and option flags visible in our terminal examples."""

    tokens = {
        "root": [
            (r"(?m)^\s*[a-zA-Z_][\w.-]*(?=\s|$)", Name.Function),
            (r"(?<!\S)--?[a-zA-Z][\w-]*", Operator),
            inherit,
        ]
    }


def code_panels(body: str, prefix: str) -> str:
    count = 0

    def panel(match: re.Match[str]) -> str:
        nonlocal count
        count += 1
        attributes, source = match.groups()
        language = re.search(r'class="language-([^\"]+)"', attributes)
        runnable = re.search(r'data-language="([^\"]+)"', attributes)
        language_name = runnable[1] if runnable else language[1] if language else "text"
        identity = re.search(r'id="([^\"]+)"', attributes)
        code_id = identity[1] if identity else f"{prefix}_block_{count}"
        text = html.unescape(source)
        lexer = {"python": PythonLexer, "text": PythonLexer, "sh": TerminalLexer}.get(
            language_name
        )
        rendered = (
            highlight(
                text, lexer(stripnl=False, ensurenl=False), HtmlFormatter(nowrap=True)
            )
            if lexer
            else source
        )
        # Signatures and shell commands are copyable, but not runnable Python tests.
        label = {"python": "Python · RUNNABLE", "sh": "Shell commands"}.get(
            language_name, "API signature"
        )
        if identity is None:
            attributes += f' id="{code_id}"'
        return (
            '<div class="code-pane"><div class="code-head"><span>'
            + label
            + f'</span><button type="button" data-copy="{code_id}" hidden>'
            "Copy code</button></div><pre><code"
            + attributes
            + ">"
            + rendered
            + "</code></pre></div>"
        )

    return re.sub(r"<pre><code([^>]*)>(.*?)</code></pre>", panel, body, flags=re.S)


def inline_code(body: str) -> str:
    """Highlight inline code while leaving fenced panels untouched."""

    def render(match: re.Match[str]) -> str:
        if match[0].startswith("<pre"):
            return match[0]
        source = html.unescape(re.sub(r"<[^>]+>", "", match[1]))
        colored = highlight(
            source,
            PythonLexer(stripnl=False, ensurenl=False),
            HtmlFormatter(nowrap=True),
        )
        if not source.endswith("\n") and colored.endswith("\n"):
            colored = colored[:-1]
        return '<code class="inline-code">' + colored + "</code>"

    return re.sub(r"<pre\b.*?</pre>|<code>(.*?)</code>", render, body, flags=re.S)
