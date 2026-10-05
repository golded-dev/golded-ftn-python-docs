# Writer verification — 2026-10-05

These results describe the unpublished local 1.2.0 working trees. They do not
establish compatibility with a running GoldED build or publication of a package.

The checks ran on macOS 27.0 (26A428), using Python 3.14.6. No Linux or Windows
runtime check was performed. GoldED build integration was deferred by request.
All four writers reject `WriterOptions(concurrent=True)` on every platform.

| Repository | pytest passed | skipped |
| --- | ---: | ---: |
| golded-ftn-python | 127 | 0 |
| golded-ftn-msg-python | 111 | 0 |
| golded-ftn-jam-python | 127 | 1 |
| golded-ftn-hudson-python | 156 | 1 |
| golded-ftn-squish-python | 159 | 1 |
| golded-ftn-python-docs | 44 | 0 |

The three skips are filename-case ambiguity fixtures on the case-insensitive
local filesystem. They are not evidence that this behaviour passes on a
case-sensitive filesystem.

Each package passed Ruff lint and format checks, strict mypy, public API stubtest
and its distribution verification script. Core stubtest uses the repository's
existing allowlist. Distribution verification checks metadata and archive
contents, rebuilds the sdist and tests both original and rebuilt wheels in clean
environments outside the source checkout. No commit or publication was made.

The documentation check built and installed all five local wheels with
`scripts/install_readers.py --local`. The expanded documentation suite ran 44 tests
against those installed wheels. These include actual
CRUD calls for each format and revision conflicts across independent sessions.
`scripts/check_examples.py` parsed sixteen HTML examples and checked them with strict
mypy. The generated writer page also passed its HTML parser and source comparison
checks. Desktop presentation was inspected; the API reference was also inspected at 390-pixel width. Print presentation was
not visually verified.

Fault injection covers rollback and poisoned sessions. Controlled process tests
cover lock conflicts and MSG publication without clobbering. Forced-exit probes
observe unpublished MSG temporary files, unindexed JAM text, Hudson orphan text
and Squish frames outside the committed base boundary. These observations are
specific interruption points, not a general crash-safety guarantee.

`git diff --check` and `agent-compose check` passed in all six changed repositories.
Public package pins remain unchanged until corresponding public commits exist.
Read [the writer guide](writers.md) for the API, format limits and source notes.

## Review corrections

Regression probes reproduced the review findings before correction. The updated
MSG validation rejects contradictory REPLY controls before append or update
changes any bytes. Squish body patches preserve omitted routing bytes and reject
conflicting explicit reply-list and first-reply values. Core always releases its
process mutex when record unlock raises. A separate agent checked these last two
corrections and ran their five targeted regression cases.

Hudson controls replacement now retains omitted MSGID and address controls.
JAM controls and external-ID changes reconcile header and inline text storage,
including duplicate physical representations. Independent fixtures cover these
placements and preservation of omitted routing.

Documentation review also reproduced a Squish controls-only patch dropping an
omitted external ID. Its independent fixture regression now preserves the raw
MSGID and rejects a conflicting explicit MSGID control before mutation.

## API documentation check

The canonical core reference covers all 40 public exports. A runtime inventory
comparison checked 113 dataclass field names, types and defaults. Its six Python
examples executed and passed strict mypy; the protocol lifecycle example was
also called with the concrete MSG writer and reader. The shared guide copies
the canonical Markdown and renders a standalone core API page. Tests compare
the generated HTML to the Markdown, execute its examples, parse strict HTML and
check links/anchors across the home and three guide pages.

The documentation home now links to the library guide, core API reference and
writer contract. The library guide lives at `site/guide.html`; example extraction
and generated-page renderers use that source. Navigation tests check all four
pages. An independent review checked 89 local link/asset targets and their
fragment anchors without finding a broken target or duplicate ID. The home was
visually inspected at ordinary desktop width and 390 pixels.

## Format references and terminology

The documentation now includes separate MSG/Opus, JAM, Squish and Hudson pages,
plus an FTN glossary. Format contracts were checked against each package’s current
exports, reader/writer source and README. The four isolated CRUD examples run
against installed local package wheels. Their HTML examples join the existing
strict-mypy check (20 Python examples in total). The glossary received a separate
agent source review.

The final layout additions have HTML, navigation and local-link checks. Visual
verification of these new pages was blocked: the browser connection was unavailable
and native Chrome access timed out. Earlier desktop/mobile checks of the shared
shell do not establish a fresh visual check of the format pages. Print remains
unverified visually.


## Public release source checks — 2026-10-05

`package-refs.json` now pins the five public 1.2.0 release commits. Running
`scripts/install_readers.py` without `--local` cloned those GitHub commits, built
their wheels and installed them. The guide then passed 44 pytest tests and
strict mypy on all 20 HTML examples. This establishes public-source installation,
not package-index availability. The subsequent PyPI upload and clean-index
installation are recorded in [the release report](release-1.2.0.md). The documentation checkout has not been published in this release.
