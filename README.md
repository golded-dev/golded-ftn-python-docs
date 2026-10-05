# GoldED for Python

A practical guide to the five GoldED FTN Python libraries, published at
https://golded-dev.github.io/golded-ftn-python-docs/.

`site/index.html` is the documentation home. It links to the library guide,
complete core API, writer contract, four format references and terminology page.
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

`package-refs.json` pins the public reader commits. The installer clones them into
a temporary directory, builds wheels and installs those wheels in this environment.
Python examples are extracted from the generated HTML pages; expected outputs and file
examples are tested with synthetic message bases. No private archives are used.

All five packages are released on PyPI at 1.2.0. The default installer tests
the public release commits pinned in `package-refs.json`. Use `--local` only
when checking changes in sibling development checkouts.

Writer contracts and verification limits live in [docs/writers.md](docs/writers.md).
Run `uv run python scripts/build_writer_guide.py` after editing them; this renders
`site/writers.html` with the existing design. Tests check the generated page and
execute its four-format CRUD example. GoldED build and interoperability checks
are deferred; concurrent mode remains disabled on all platforms.

Preview with `python -m http.server 8874 --directory site`, then open
http://localhost:8874. Check a narrow mobile viewport, keyboard navigation,
copy buttons and print presentation after layout changes.

## Publish

Work and commit on `main`. Pull requests run checks; a push to `main` checks the
examples on Python 3.12–3.14 and publishes only `site/` to GitHub Pages. All Actions
are pinned to complete commit SHAs. No custom domain is configured.

When updating the guide, change package refs deliberately and rerun the checks.
Keep documented package versions and installation wheel filenames consistent.
The five library distributions are available on PyPI at 1.2.0.

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
`docs/squish.md` and `docs/hudson.md`. Regenerate all four with
`uv run python scripts/build_format_guides.py`. They use the shared design,
syntax highlighting and navigation; their synthetic Python examples run in pytest
and strict mypy. GoldED interoperability remains unverified.

`docs/glossary.md` explains FTN terminology and is rendered as `site/glossary.html`
by the format-guide renderer. Inline code uses the shared syntax palette, too.
