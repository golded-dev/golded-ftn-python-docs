"""Run the actual HTML examples against independent synthetic message bases."""

import contextlib
import io
import struct
from html.parser import HTMLParser
from pathlib import Path

import html5lib
import pytest
from golded_ftn import OutgoingMessage
from golded_ftn_msg import MsgWriter

ROOT = Path(__file__).resolve().parents[1]


class Guide(HTMLParser):
    def __init__(self):
        super().__init__()
        self.examples = {}
        self.outputs = {}
        self.ids = set()
        self.links = []
        self.current = None
        self.output_for = None
        self.last_example = None

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if "id" in values:
            assert values["id"] not in self.ids, values["id"]
            self.ids.add(values["id"])
        if tag == "a":
            self.links.append(values.get("href", ""))
        if tag == "code" and values.get("data-language") == "python":
            self.current = values["id"]
            self.last_example = self.current
            self.examples[self.current] = ""
        if tag == "div" and values.get("class") == "output":
            self.output_for = self.last_example
        if tag == "pre" and self.output_for:
            self.current = "output:" + self.output_for
            self.outputs[self.output_for] = ""

    def handle_data(self, data):
        if self.current:
            if self.current.startswith("output:"):
                self.outputs[self.current[7:]] += data
            else:
                self.examples[self.current] += data

    def handle_endtag(self, tag):
        if tag in ("code", "pre"):
            self.current = None
        if tag == "div":
            self.output_for = None


def guide():
    parsed = Guide()
    parsed.feed((ROOT / "site/index.html").read_text(encoding="utf-8"))
    return parsed


def test_internal_links_and_assets():
    parsed = guide()
    for href in parsed.links:
        if href.startswith("#"):
            assert href[1:] in parsed.ids
    assert (ROOT / "site/assets/golded-logo.png").is_file()
    assert len(parsed.examples) == 9


@pytest.mark.parametrize("name", list(guide().outputs))
def test_runnable_output(name):
    parsed = guide()
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        exec(compile(parsed.examples[name], name, "exec"), {})
    assert stdout.getvalue() == parsed.outputs[name]


def field(lo, payload):
    return struct.pack("<HHI", lo, 0, len(payload)) + payload


def pascal(payload, width):
    return bytes([len(payload)]) + payload + bytes(width - len(payload) - 1)


@pytest.fixture
def archive(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for directory in ("msg", "opus", "jam", "squish", "hudson"):
        (tmp_path / "archives" / directory).mkdir(parents=True)
    message = OutgoingMessage(
        from_name="Alice", to_name="Bob", subject="Demo", body_text="Hello."
    )
    MsgWriter().write("archives/msg/general", [message])
    # Opus: names and a packed written date; other fixed fields are zero.
    opus = bytearray(190)
    opus[:5] = b"Alice"
    opus[36:39] = b"Bob"
    opus[72:76] = b"Demo"
    struct.pack_into("<HH", opus, 164, 1 | 1 << 5 | 46 << 9, 12 << 11)
    directory = Path("archives/opus/general")
    directory.mkdir()
    (directory / "1.MSG").write_bytes(opus + b"Hello.\0")
    # JAM revision 1, one indexed header at physical offset 1024.
    info = bytearray(1024)
    info[:4] = b"JAM\0"
    struct.pack_into("<I", info, 20, 1)
    fields = field(2, b"Alice") + field(3, b"Bob") + field(6, b"Demo")
    header = bytearray(76)
    header[:4] = b"JAM\0"
    struct.pack_into("<H", header, 4, 1)
    struct.pack_into("<I", header, 8, len(fields))
    struct.pack_into("<I", header, 48, 1)
    struct.pack_into("<I", header, 64, 6)
    Path("archives/jam/general.JHR").write_bytes(info + header + fields)
    Path("archives/jam/general.JDT").write_bytes(b"Hello.")
    Path("archives/jam/general.JDX").write_bytes(struct.pack("<II", 0, 1024))
    # Classic Squish, one frame and a 12-byte index entry.
    area = bytearray(256)
    struct.pack_into("<HH5I", area, 0, 256, 0, 1, 1, 0, 0, 100)
    struct.pack_into("<H", area, 130, 28)
    xmsg = bytearray(238)
    xmsg[4:9] = b"Alice"
    xmsg[40:43] = b"Bob"
    xmsg[76:80] = b"Demo"
    struct.pack_into("<I", xmsg, 214, 1)
    payload = xmsg + b"Hello.\0"
    frame = struct.pack(
        "<IiiIIIHH", 0xAFAE4453, 0, 0, len(payload), len(payload), 0, 0, 0
    )
    struct.pack_into("<i", area, 120, 256 + len(frame) + len(payload))
    Path("archives/squish/general.SQD").write_bytes(area + frame + payload)
    Path("archives/squish/general.SQI").write_bytes(struct.pack("<iII", 256, 1, 0))
    # Classic Hudson: one board 7 message, Pascal strings and one text block.
    header = struct.pack(
        "<10H2BH3B", 1, 0, 0, 0, 0, 1, 236, 77, 236, 100, 2, 2, 0, 0, 0, 7
    )
    header += pascal(b"12:00", 6) + pascal(b"10-04-26", 9)
    header += pascal(b"Bob", 36) + pascal(b"Alice", 36) + pascal(b"Demo", 73)
    Path("archives/hudson/MSGIDX.BBS").write_bytes(struct.pack("<HB", 1, 7))
    Path("archives/hudson/MSGHDR.BBS").write_bytes(header)
    Path("archives/hudson/MSGTXT.BBS").write_bytes(pascal(b"Hello.\0", 256))
    return tmp_path


@pytest.mark.parametrize(
    "name",
    ["read_formats", "hudson_board", "shared_reader", "strict_errors", "archive_read"],
)
def test_file_examples(name, archive):
    stdout = io.StringIO()
    namespace = {}
    with contextlib.redirect_stdout(stdout):
        exec(compile(guide().examples[name], name, "exec"), namespace)
    result = stdout.getvalue()
    if name == "read_formats":
        assert result.splitlines() == ["1 Alice Demo"] * 5
    elif name == "hudson_board":
        assert result == "Demo\n"
    elif name == "shared_reader":
        assert result == "1 Demo\njam 1 1024\n"
    elif name == "strict_errors":
        assert result == "Messages: 1\n"
    else:
        assert result == "Messages: 1\nTraversal completed: True\n"
        assert namespace["issues"] == []


def test_archive_example_reports_skips_and_stops(archive):
    # A valid index slot points to a truncated header: a reported skip.
    path = Path("archives/jam/general.JDX")
    path.write_bytes(path.read_bytes() + struct.pack("<II", 0, 999999))
    namespace = {}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(guide().examples["archive_read"], namespace)
    assert any(issue.action == "skipped" for issue in namespace["issues"])
    assert namespace["complete_traversal"] is True
    # A partial index record prevents safe traversal and must report a stop.
    path.write_bytes(struct.pack("<II", 0, 1024) + b"x")
    with contextlib.redirect_stdout(io.StringIO()):
        exec(guide().examples["archive_read"], namespace)
    assert namespace["complete_traversal"] is False


def test_strict_example_handles_filesystem_and_parser_errors(archive):
    path = Path("archives/jam/general.JHR")
    path.write_bytes(b"broken")
    for expected in ("Cannot parse the source:", "Cannot access the source:"):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exec(guide().examples["strict_errors"], {})
        assert stdout.getvalue().startswith(expected)
        path.unlink(missing_ok=True)


def test_html5_document():
    parser = html5lib.HTMLParser(strict=True)
    parser.parse((ROOT / "site/index.html").read_text(encoding="utf-8"))
