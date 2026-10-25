# GoldED for Python

A practical guide to the GoldED FTN Python suite. The existing site is published at
https://golded-dev.github.io/golded-ftn-python-docs/.

`site/index.html` is the documentation home. It links to the library guide,
complete core API, writer contract, five format references and terminology page.
Every page shares the guide shell and navigation. `scripts/page_layout.py` supplies
navigation for generated references; `DESIGN.md` defines the common presentation.

The site is plain HTML, CSS and a little JavaScript. Its layout, typography, navigation and black historical palette
are defined in [DESIGN.md](DESIGN.md). Text and code remain readable without JavaScript.
The GoldED logo is reused with Odinn's permission.

## Check the guide

```sh
uv sync --locked --python 3.14
uv run python scripts/install_readers.py --local
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run python scripts/check_examples.py
```

`package-refs.json` pins the published release commits. The installer uses the
public index by default. `--local` selects the retained release wheelhouse, or use
`--wheelhouse /path/to/reviewed/wheelhouse` explicitly. Python examples are
extracted from generated HTML and tested with synthetic message bases; private
archives are not used.

Writer contracts and verification limits live in [docs/writers.md](docs/writers.md).
Run `uv run python scripts/build_writer_guide.py` after editing them; this renders
`site/writers.html` with the existing design. Tests check the generated page and
execute its four-format CRUD example. Bounded macOS offline interoperability probes are recorded in
[docs/golded-macos-compatibility.md](docs/golded-macos-compatibility.md). All four formats
passed the described scenarios against the corrected GoldED build. Concurrent writes are qualified only under the documented bounded Linux/macOS GoldED profile; see the writer contract and release manifest.

Preview with `python -m http.server 8874 --directory site`, then open
http://localhost:8874. Check a narrow mobile viewport, keyboard navigation,
copy buttons and print presentation after layout changes.

## Publish

Work and commit on `main`. Pull requests run checks; a push to `main` checks the
examples on Python 3.12–3.14 and publishes only `site/` to GitHub Pages. All Actions
are pinned to complete commit SHAs. No custom domain is configured.

When updating the guide, change package refs deliberately and rerun the checks.
Keep documented package versions and installation wheel filenames consistent.
The documented release set is listed below.

## License

MIT for the guide and scripts. Bundled IBM Plex fonts retain their SIL Open Font
License. The JAM specification retains its own copyright notice in the guide.

## Core API reference

The canonical reference is `golded-ftn-python/docs/api.md`. Run
`uv run python scripts/build_api_guide.py --sync` to copy it to
`docs/core-api.md` and render `site/core-api.html`. Without `--sync`, the renderer
uses the documentation checkout's copy. Keep both copies in sync when core exports
change. The reference covers every public export and its examples are executed
and checked with strict mypy against installed wheels.

All pages share the guide shell and page navigation. The current page is
marked with `aria-current="page"`; section navigation uses `aria-current="location"`.
On narrow screens, the section list is a native expandable “On this page” menu.
It stays available without JavaScript.

## Format references

The format pages cover public readers, writers and sessions, base files, metadata,
archive recovery and known limits. Editable sources are `docs/msg.md`, `docs/jam.md`,
`docs/squish.md`, `docs/hudson.md` and `docs/sqlite.md`. Regenerate all five with
`uv run python scripts/build_format_guides.py`. They use the shared design,
syntax highlighting and navigation; their synthetic Python examples run in pytest
and strict mypy. The bounded macOS results and remaining gaps are recorded in the compatibility report.

`docs/glossary.md` explains FTN terminology and is rendered as `site/glossary.html`
by the format-guide renderer. Inline code uses the shared syntax palette, too.

## Published suite

The guide covers core, five base formats, packet, nodelist, binkp, tosser and
tools. Published versions are core 1.4.0, MSG 1.4.0, JAM/Squish/Hudson 1.3.0,
SQLite 1.0.0, packet/nodelist/binkp/tosser 1.0.0 and tools 1.1.0.
Linux/macOS with Python 3.12–3.14 are the test targets.

Install documented wheels with `python scripts/install_readers.py --wheelhouse
/path/to/reviewed/wheelhouse` in the documentation environment. Default installation
uses the public index.
Render packet, nodelist, binkp, tosser and CLI with `scripts/build_format_guides.py`.
For core sync use `GOLDED_CORE_SOURCE=/path/to/core` with
`scripts/build_api_guide.py --sync`; do not copy unrelated experimental docs.

`package-refs.json` records the published release commits used by this guide.

## Archive reading entry

`docs/archive.md` is the task guide for people with existing message bases who
want to read them without writing code or operating a network. It renders to
`site/archive.html` through `scripts/build_format_guides.py`. It is linked from
the home page and every sidebar. Tests execute its reading commands on synthetic
bases and compare file hashes before and after.
