"""Archive-reading instructions work with synthetic bases and leave them intact."""

import hashlib
import re
import shlex
import subprocess
import sys
from pathlib import Path

import html5lib
from test_examples import archive as archive

from scripts.build_format_guides import render

ROOT = Path(__file__).resolve().parents[1]


def test_archive_page_is_generated():
    page = (ROOT / "site/archive.html").read_text()
    assert page == render("archive")
    html5lib.HTMLParser(strict=True).parse(page)


def test_archive_reading_commands(archive):
    def hashes():
        return {
            str(p): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (archive / "archives").rglob("*")
            if p.is_file()
        }

    before = hashes()
    source = (ROOT / "docs/archive.md").read_text()
    commands = re.findall(r"^ftnt (?:heads|read) .+$", source, re.M)
    assert commands
    for command in commands:
        command = command.replace("archive-copy/msg", "archives/msg/general")
        command = command.replace("archive-copy/", "archives/")
        command = command.replace(" 42 ", " 1 ")
        args = shlex.split(command)
        output = None
        if ">" in args:
            redirect = args.index(">")
            output = Path(args[redirect + 1])
            args = args[:redirect]
        result = subprocess.run(
            [sys.executable, "-m", "golded_ftn_tools", *args[1:]],
            capture_output=True,
            text=True,
            check=True,
        )
        if args[1] == "heads":
            assert '"subject":"Demo"' in result.stdout.replace(" ", "")
        else:
            assert "Hello." in result.stdout
        if output:
            output.write_text(result.stdout)
            assert "Hello." in output.read_text()
    assert hashes() == before
