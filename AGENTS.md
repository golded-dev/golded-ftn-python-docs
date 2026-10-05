# GoldED for Python documentation

This repository publishes a static English guide to five FTN Python packages.
Before changing layout, navigation, typography, colors or responsive behavior,
read DESIGN.md. It is this repository’s design authority. Keep the guide readable
without JavaScript.

The published artifact is site/ only. Never include message archives or private
consumer data. Test the Python code extracted from HTML with synthetic fixtures;
package-refs.json pins public package commits. Use scripts/install_readers.py --local
to verify unpublished sibling writers as built wheels. Keep public pins unchanged
until the corresponding commits exist; local checks do not establish publication.
Render site/writers.html from docs/writers.md with scripts/build_writer_guide.py.
Render format references from docs/{msg,jam,squish,hudson}.md with
scripts/build_format_guides.py.
Run uv run pytest, Ruff lint/format checks and scripts/check_examples.py before
publishing. Check desktop, mobile and print presentation after layout changes.

Work and commit on main. Publication is through the Pages workflow after checks.
Edit this fragment or agent-compose.toml, then preview, build and check.
