# GoldED for Python

A practical guide to the five GoldED FTN Python libraries, published at
https://golded-dev.github.io/golded-ftn-python-docs/.

The site is plain HTML, CSS and a little JavaScript. Its black historical palette
comes from `golded-site/DESIGN.md`. Text and code remain readable without JavaScript.
The GoldED logo is reused with Odinn's permission.

## Check the guide

```sh
uv sync --locked --python 3.14
uv run python scripts/install_readers.py
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run python scripts/check_examples.py
```

`package-refs.json` pins the public reader commits. The installer clones them into
a temporary directory, builds wheels and installs those wheels in this environment.
Python examples are extracted from `site/index.html`; expected outputs and file
examples are tested with synthetic message bases. No private archives are used.

Preview with `python -m http.server 8874 --directory site`, then open
http://localhost:8874. Check a narrow mobile viewport, keyboard navigation,
copy buttons and print presentation after layout changes.

## Publish

Work and commit on `main`. Pull requests run checks; a push to `main` checks the
examples on Python 3.12–3.14 and publishes only `site/` to GitHub Pages. All Actions
are pinned to complete commit SHAs. No custom domain is configured.

When updating the guide, change package refs deliberately and rerun the checks.
Keep documented package versions and installation wheel filenames consistent.
The five library distributions have not been released on PyPI.

## License

MIT for the guide and scripts. Bundled IBM Plex fonts retain their SIL Open Font
License. The JAM specification retains its own copyright notice in the guide.
