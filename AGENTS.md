# GoldED for Python documentation

This repository publishes a static English guide to five FTN Python packages.
Use the approved black historical palette from golded-site/DESIGN.md. Preserve
the yellow GoldED logo, right-aligned Sans subtitle, red masthead borders and
7px vertical masthead padding. Keep the guide readable without JavaScript.

The published artifact is site/ only. Never include message archives or private
consumer data. Test the Python code extracted from HTML with synthetic fixtures;
package-refs.json pins the public package commits used by scripts/install_readers.py.
Run uv run pytest, Ruff lint/format checks and scripts/check_examples.py before
publishing. Check desktop, mobile and print presentation after layout changes.

Work and commit on main. Publication is through the Pages workflow after checks.
Edit this fragment or agent-compose.toml, then preview, build and check.
