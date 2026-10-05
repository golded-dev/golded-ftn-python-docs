# GoldED for Python documentation design

This file defines the design for this repository. Read it before changing page
layout, navigation, typography, colors or responsive behavior. Update it when an
intentional design decision changes. Apply shared changes to all pages.

The palette descends from GoldED.dev’s historical mode. This documentation has
its own layout and interaction rules; another repository’s design changes do not
silently change these rules.

## Character

A reading tool: dark, rectangular, quiet and precise. The yellow GoldED logo,
red masthead rules and blue shell establish its identity. Content gets the space.
Keep surfaces flat, motion minimal and links recognizable. Use local IBM Plex
fonts and the existing logo asset.

## Colors

| Role | Value |
| --- | --- |
| Canvas | `#05070B` |
| Reading surface | `#0B0F18` |
| Raised / current navigation surface | `#101624` |
| Primary text | `#F5F7FF` |
| Secondary text | `#BCC5D9` |
| Shell frame | `#4F6DFF` |
| Blue status bar | `#2D47C7` |
| Yellow signal / section number | `#FFE45A` |
| Links | `#8FB2FF` |
| Dividers | `#273149` |
| Masthead rules / syntax operators and flags | `#FF6868` |
| Syntax numbers and Python constants | `#55FF55` |

Yellow marks location, numbering and identity. Body text uses primary or secondary
text colors. Preserve the black historical palette across the whole site.

## Shared page shell

All pages use the same masthead, blue status bar, two-column shell and footer.
The home page is the entry to the three shared guides, four format references and terminology;
its main content remains a short index with descriptions and quick links.

- Page: maximum width 1260px, centered, 40px vertical margin, 24px horizontal padding.
- Masthead: 1px red top and bottom rules, 7px vertical padding, 24px bottom margin.
- Logo: 210px wide on desktop; subtitle uses Sans and aligns to the logo’s right.
  Preserve the existing optical offset and subtitle placement.
- Shell: 1px blue frame, dark reading surface, square corners.
- Columns: 230px sidebar and a flexible main column that can shrink.
- Sidebar: 32px vertical / 20px horizontal padding, muted right divider.
- Main: 42px top, 48px horizontal, 36px bottom padding.
- Footer: outside the shell, aligned with its outer edges, 18px vertical padding.

Use the spacing scale `4, 8, 12, 16, 24, 32, 48, 64` for new spacing. Preserve the
specific shell and masthead values above rather than rounding them incidentally.

## Page eyebrows

Place a short yellow Mono eyebrow immediately above each page heading, using the
shared `.eyebrow` style. Keep the two-part phrasing tied to the page’s purpose:

- Home: “Old messages. New possibilities.”
- Library guide: “Old messages. Ordinary Python.”
- Core API reference: “Old formats. Shared values.”
- Editing message bases: “Old bases. Careful edits.”
- Terminology: “Old jargon. Plain explanations.”
- MSG / Opus: “Individual files. Complete messages.”
- JAM: “Indexed messages. Preserved metadata.”
- Squish: “Linked frames. Stable identities.”
- Hudson: “Shared files. Explicit boards.”

## Typography and section numbering

| Element | Font | Size / line height | Weight |
| --- | --- | --- | --- |
| Body / introductory text | IBM Plex Sans | 17px / 1.65 | 400 |
| Section paragraphs, lists, definition lists and leads | IBM Plex Sans | 15px / 1.65 | 400 |
| Page heading | IBM Plex Sans | 44px / 1.1 | 600 |
| Section heading | IBM Plex Sans | 24px / 1.2 | 500 |
| Yellow section number (`.section-title span`) | IBM Plex Mono | **20px / 1.2** | **500** |
| Sidebar page links | IBM Plex Sans | 14px | 400 |
| Sidebar section numbers | IBM Plex Mono | 11px | 400 |
| Code blocks | IBM Plex Mono | 13px / 1.85 | 400 |

Section numbers are part of the heading, not miniature labels. Keep them at 20px
on desktop and mobile, yellow, non-shrinking and baseline-aligned with the heading.
The heading row has a 12px gap. Keep sidebar numbers smaller: they serve a separate
indexing role. Numbering stays consistent between each guide’s headings and index.

Balance page and section headings with `text-wrap: balance`. Use `text-wrap: pretty`
for paragraphs and macOS font smoothing on the body. Code preserves its spacing.

## Code panels

Every fenced code block uses the library guide’s `.code-pane` wrapper,
`.code-head` label row and a `Copy code` button targeting a unique code ID.
Label Python examples as runnable, shell commands as commands and reference
signatures as signatures. Only runnable Python examples carry the test-extraction
attributes. Use the existing blue keyword, yellow string and muted comment colors.
Operators and terminal option flags use GoldED red (`#FF6868`), matching the
masthead rules. Numbers and Python constants (`True`, `False`, `None`) use
GoldED green (`#55FF55`). Keywords and types remain blue; strings and terminal
command names use yellow; comments remain muted. Green is a syntax accent, not a
new surface or body-text color. Print renders all syntax tokens in black. Copy the plain source text, preserving whitespace. Hide copy buttons without
JavaScript and in print. Inline code stays inline and uses the same syntax palette. Give paragraph, list
and definition-text code a raised surface with 2px vertical / 4px horizontal
padding and 2px corners. Preserve exact text and allow natural wrapping; use no
copy button for inline snippets.

## Navigation and interaction

The sidebar has three distinct groups:

1. **Documentation:** Home, Library guide, Core API reference, Editing message bases, Terminology.
   Use those labels and order on every page. Mark exactly one link with
   `aria-current="page"`, yellow text and a yellow inset left rule.
2. **Formats:** MSG / Opus, JAM, Squish, Hudson. Use those labels and order.
   Current-page styling is identical to Documentation; exactly one current page
   exists across both groups. Keep the Formats label visible on mobile.
3. **On this page:** the current guide’s section links, starting at Overview (00).
   Use a native `details` / `summary` control. Mark the current section with
   `aria-current="location"` and the existing active surface and left rule.

Keep navigation usable without JavaScript. Section tracking may enhance it, using
actual section positions and an update on anchor changes. Do not substitute page
state for section state. Avoid a second visible page-link group above the article.

Navigation links and the disclosure control have at least 40px height. Keyboard
focus uses a visible 2px yellow outline with clear separation. Hover uses the raised
surface and primary text only on devices with a fine pointer and hover support.
Keep navigation transitions immediate; reading needs no entrance animation.

On desktop, the sidebar sticks 24px below the viewport top. Its contents may scroll
when taller than the viewport, with a stable scrollbar gutter and contained vertical
overscroll. Keep full link labels visible and reachable; do not truncate them.

## Mobile

At 800px and below:

- Use one column, with navigation above the article and a bottom divider.
- Page: 20px vertical margin and 20px horizontal padding.
- Main: 28px vertical / 20px horizontal padding. Page headings become 34px.
- Logo becomes 160px wide; subtitle becomes 10px. Hide the redundant masthead label.
- Page navigation uses two columns. Section links use two columns and wrap naturally.
- Collapse “On this page” initially when JavaScript is available. Without JavaScript,
  leave it expanded and operable. Users can always open or close it themselves.
- Remove sticky positioning and sidebar scrolling. Hide the sidebar note.
- Code blocks become 12px; retain horizontal scrolling for long lines.
- Keep the yellow section numbers at 20px. Let footers wrap.

Wide tables and code blocks may scroll inside their own containers. The page itself
must fit the viewport. Do not replace the section menu with horizontal scrolling tabs.

## Print

Print declares a light color scheme with a white surface and black reading text. Hide the masthead, sidebar,
footer, skip link, copy buttons and sidebar navigation. Keep the home’s guide index
and quick links: they are its reading content. Remove the shell frame and main
padding. Wrap code, expose table overflow and keep code panes and standalone code blocks together where possible.
Check actual print output after substantial layout changes; print CSS alone is not
proof of a readable printed page.

## Where changes belong

`site/guide.html` currently supplies the shared CSS, masthead, footer and script to
the API, writer and format renderers. `scripts/page_layout.py` supplies their page and
section navigation. The home page keeps its own HTML and a copy of the shared CSS.

For shared styling changes, edit the library guide and the home page, then regenerate:

```sh
uv run python scripts/build_api_guide.py
uv run python scripts/build_writer_guide.py
uv run python scripts/build_format_guides.py
```

Edit reference content in its Markdown source, not the generated HTML. Follow the
README’s core-reference sync workflow when public API content changes.

Check desktop and mobile, section jumps, current-page markers, keyboard focus and
long navigation labels. Run pytest, Ruff, the HTML example checker and
`git diff --check`. Record what was actually checked; keep unverified presentation
or publication separate from local results.
