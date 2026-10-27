"""Install the documented releases from a wheelhouse or the public index."""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSIONS = {
    "golded-ftn": "1.5.0",
    "golded-ftn-msg": "1.4.0",
    "golded-ftn-jam": "1.3.0",
    "golded-ftn-squish": "1.3.0",
    "golded-ftn-hudson": "1.4.0",
    "golded-ftn-sqlite": "1.1.0",
    "golded-ftn-packet": "1.0.0",
    "golded-ftn-nodelist": "1.0.0",
    "golded-ftn-binkp": "1.0.0",
    "golded-ftn-tosser": "1.0.0",
    "golded-ftn-tools": "1.2.0",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheelhouse", type=Path)
    parser.add_argument(
        "--local", action="store_true", help="Use the retained suite wheelhouse"
    )
    args = parser.parse_args()
    wheelhouses = [args.wheelhouse] if args.wheelhouse is not None else []
    if args.local:
        wheelhouses = [
            ROOT.parent / "ftn-node-work/release/wheelhouse",
            ROOT.parent / "golded-ftn-sqlite-python/dist",
        ]
    command = [
        "uv",
        "pip",
        "install",
        "--python",
        sys.executable,
        "--no-cache",
        "--reinstall",
    ]
    if wheelhouses:
        command.append("--no-index")
        for wheelhouse in wheelhouses:
            command += ["--find-links", str(wheelhouse.resolve())]
    command += [f"{name}=={version}" for name, version in VERSIONS.items()]
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
