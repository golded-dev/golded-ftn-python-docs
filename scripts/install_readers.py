"""Build the pinned public checkouts, then install their wheels in this venv."""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--local",
        action="store_true",
        help="Build sibling working checkouts instead of the pinned public commits",
    )
    args = parser.parse_args()
    refs = json.loads((ROOT / "package-refs.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="ftn-doc-readers-") as temporary:
        work = Path(temporary)
        wheels = work / "wheels"
        for name, ref in refs.items():
            checkout = (ROOT.parent if args.local else work) / (name + "-python")
            if not args.local:
                subprocess.run(
                    [
                        "git",
                        "clone",
                        "--quiet",
                        "https://github.com/golded-dev/" + checkout.name + ".git",
                        str(checkout),
                    ],
                    check=True,
                )
                subprocess.run(
                    ["git", "checkout", "--quiet", ref], cwd=checkout, check=True
                )
            subprocess.run(
                ["uv", "build", "--wheel", "--out-dir", str(wheels)],
                cwd=checkout,
                check=True,
            )
        subprocess.run(
            [
                "uv",
                "pip",
                "install",
                "--python",
                sys.executable,
                *map(str, wheels.glob("*.whl")),
            ],
            check=True,
        )


if __name__ == "__main__":
    main()
