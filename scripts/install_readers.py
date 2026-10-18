"""Install the documented candidates from a wheelhouse or the public index."""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSIONS = {
    "golded-ftn": "1.3.0",
    "golded-ftn-msg": "1.4.0",
    "golded-ftn-jam": "1.3.0",
    "golded-ftn-squish": "1.3.0",
    "golded-ftn-hudson": "1.3.0",
    "golded-ftn-packet": "0.1.0",
    "golded-ftn-nodelist": "0.1.0",
    "golded-ftn-binkp": "0.1.0",
    "golded-ftn-tosser": "0.1.0",
    "golded-ftn-tools": "1.1.0",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheelhouse", type=Path)
    parser.add_argument(
        "--local", action="store_true", help="Use the suite candidate wheelhouse"
    )
    args = parser.parse_args()
    wheelhouse = args.wheelhouse
    if args.local:
        wheelhouse = ROOT.parent / "ftn-node-work/release/wheelhouse"
    command = [
        "uv",
        "pip",
        "install",
        "--python",
        sys.executable,
        "--no-cache",
        "--reinstall",
    ]
    if wheelhouse is not None:
        command += ["--no-index", "--find-links", str(wheelhouse.resolve())]
    command += [f"{name}=={version}" for name, version in VERSIONS.items()]
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
