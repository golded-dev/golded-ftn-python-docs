"""Use the library guide's section navigation for rendered references."""

import html
import re


def page_navigation(current: str) -> str:
    pages = [
        ("index.html", "Home"),
        ("guide.html", "Library guide"),
        ("core-api.html", "Core API reference"),
        ("writers.html", "Editing message bases"),
        ("glossary.html", "Terminology"),
    ]
    formats = [
        ("msg.html", "MSG / Opus"),
        ("jam.html", "JAM"),
        ("squish.html", "Squish"),
        ("hudson.html", "Hudson"),
    ]
    return (
        '<nav class="page-nav" aria-label="Documentation">'
        + "".join(
            f'<a href="{url}"'
            + (' aria-current="page"' if url == current else "")
            + f">{title}</a>"
            for url, title in pages
        )
        + '</nav><div class="label">Formats</div>'
        + '<nav class="page-nav format-nav" aria-label="Formats">'
        + "".join(
            f'<a href="{url}"'
            + (' aria-current="page"' if url == current else "")
            + f">{title}</a>"
            for url, title in formats
        )
        + "</nav>"
    )


def layout(body: str, breadcrumbs: str, current: str) -> str:
    headings = list(re.finditer(r'<h2 id="([^"]+)">(.*?)</h2>', body, re.S))
    assert headings
    links = [
        '<a class="active" aria-current="location" href="#start">'
        '<span class="num">00</span>Overview</a>'
    ]
    content = body[: headings[0].start()]
    for number, heading in enumerate(headings, 1):
        anchor, title = heading.groups()
        text = html.unescape(re.sub(r"<[^>]+>", "", title))
        links.append(
            f'<a href="#{html.escape(anchor, quote=True)}">'
            f'<span class="num">{number:02d}</span>{html.escape(text)}</a>'
        )
        end = headings[number].start() if number < len(headings) else len(body)
        content += (
            f'<section id="{anchor}" class="guide-section">'
            f'<div class="section-title"><span>{number:02d}</span>'
            f"<h2>{title}</h2></div>" + body[heading.end() : end] + "</section>"
        )
    return (
        '<div class="layout"><aside><div class="sidebar">'
        + page_navigation(current)
        + '<details class="contents" open><summary>On this page</summary>'
        '<nav class="nav" aria-label="Guide sections">'
        + "".join(links)
        + '</nav></details><div class="aside-note"><a href="index.html">'
        "Documentation home</a>"
        '</div></div></aside><main id="start">'
        + breadcrumbs
        + content
        + "</main></div>"
    )
