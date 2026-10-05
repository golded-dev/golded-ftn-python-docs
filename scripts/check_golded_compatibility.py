"""Opt-in offline interoperability probe against an explicitly supplied GoldED binary.

Run with the installed release wheels. Uses only temporary synthetic message bases;
never opens operator configuration. No concurrent support is enabled by this probe.
"""

import argparse
import fcntl
import hashlib
import importlib.metadata
import json
import os
import platform
import pty
import re
import select
import shutil
import struct
import subprocess
import tempfile
import termios
import time
import traceback
from datetime import UTC, datetime
from pathlib import Path

from golded_ftn import (
    ConflictError,
    ControlLine,
    FtnAddress,
    MessagePatch,
    OutgoingMessage,
)
from golded_ftn_hudson import HudsonReader, HudsonWriter
from golded_ftn_jam import JamReader, JamWriter
from golded_ftn_msg import MsgReader, MsgWriter
from golded_ftn_squish import SquishReader, SquishWriter

FORMATS = {
    "msg": (MsgWriter, MsgReader, "FTSC"),
    "jam": (JamWriter, JamReader, "JAM"),
    "squish": (SquishWriter, SquishReader, "Squish"),
    "hudson": (HudsonWriter, HudsonReader, "Hudson"),
}
ANSI = re.compile(r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


class Terminal:
    """Drive the real application; await output states instead of timed keystrokes."""

    def __init__(self, binary: Path, config: Path):
        self.output = bytearray()
        self.root = config.parent
        self.fd, slave = pty.openpty()
        try:
            fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", 25, 80, 0, 0))
            self.proc = subprocess.Popen(
                [str(binary), "-C" + str(config)],
                cwd=config.parent,
                stdin=slave,
                stdout=slave,
                stderr=slave,
                env={"TERM": "xterm", "PATH": os.defpath},
            )
        except BaseException:
            os.close(self.fd)
            raise
        finally:
            os.close(slave)

    @property
    def text(self):
        return self.normalized(self.output)

    @staticmethod
    def normalized(data):
        return ANSI.sub("", data.decode("utf-8", "replace"))

    def wait(self, *expected, start=0, timeout=15):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if all(item in self.normalized(self.output[start:]) for item in expected):
                return
            if self.proc.poll() is not None:
                raise RuntimeError(
                    f"GoldED exited {self.proc.returncode}; wanted {expected}\n"
                    f"{self.text[-1800:]}\n"
                    + (self.root / "runtime/golded.log").read_text(errors="replace")[
                        -2500:
                    ]
                )
            ready, _, _ = select.select([self.fd], [], [], 0.1)
            if ready:
                try:
                    chunk = os.read(self.fd, 65536)
                except OSError:
                    chunk = b""
                self.output.extend(chunk)
        raise RuntimeError(
            f"Terminal state not reached: {expected}\n{self.text[-2500:]}"
        )

    def send(self, keys, *expected):
        start = len(self.output)
        os.write(self.fd, keys)
        if expected:
            self.wait(*expected, start=start)

    def quit(self):
        self.send(b"\x11")
        deadline = time.monotonic() + 10
        while self.proc.poll() is None and time.monotonic() < deadline:
            ready, _, _ = select.select([self.fd], [], [], 0.1)
            if ready:
                try:
                    self.output.extend(os.read(self.fd, 65536))
                except OSError:
                    pass
        if self.proc.poll() != 0:
            raise RuntimeError("GoldED did not quit cleanly")

    def close(self):
        if self.proc.poll() is None:
            self.proc.kill()
            self.proc.wait()
        os.close(self.fd)


def configure(root, binary, kind, base, board):
    runtime = root / "runtime"
    runtime.mkdir(exist_ok=True)
    for file in (binary.parent / "cfgs/config").glob("*"):
        if file.is_file():
            shutil.copy2(file, runtime / file.name)
    target = str(board) if kind == "hudson" else str(base)
    config = root / "synthetic.cfg"
    config.write_text(
        "USERNAME Test Operator\nADDRESS 2:236/999\n"
        f"GOLDPATH {runtime}/\nXLATPATH {binary.parent / 'cfgs/charset'}/\n"
        "XLATLOCALSET LATIN-1\nXLATIMPORT CP850\nXLATEXPORT CP850\n"
        "XLATCHARSET CP850 LATIN-1 850_ISO.CHS\n"
        "XLATCHARSET LATIN-1 CP850 ISO_850.CHS\n"
        f"HUDSONPATH {base}/\nSQUISHSCAN API\n"
        "MSGLISTFIRST NO\nEDITMENU NO\nEDITHEADERFIRST NO\nEDITSAVEMENU NO\n"
        f'AREADEF PYTHON.TEST "Synthetic compatibility" 0 Local '
        f"{FORMATS[kind][2]} {target} . (Loc)\n"
    )
    return config


def session(writer, base, kind, board):
    return writer.open(base, board=board) if kind == "hudson" else writer.open(base)


def message(kind, subject, body, **kwargs):
    return OutgoingMessage(
        from_name="Test Operator",
        to_name="Test Recipient",
        subject=subject,
        body_text=body,
        from_address=FtnAddress(zone=2, net=236, node=999),
        to_address=FtnAddress(zone=2, net=236, node=100),
        posted_at=datetime(
            2026, 10, 5, 12, 0, 0, tzinfo=UTC if kind == "squish" else None
        ),
        **kwargs,
    )


def run_format(binary, kind, board):
    writer_type, reader_type, _ = FORMATS[kind]
    checks = []
    with tempfile.TemporaryDirectory(
        prefix=f"ftn-golded-{kind}.", dir="/tmp"
    ) as directory:
        root = Path(directory)
        base = root / "base"
        writer = writer_type()
        writer.create(base)
        with session(writer, base, kind, board) as opened:
            parent = opened.append(
                message(
                    kind,
                    "PYTHON PARENT",
                    "Initial body.",
                    external_id="2:236/999 11111111",
                )
            )
            unrelated = opened.append(
                message(kind, "UNRELATED", "Unrelated body marker.")
            )
            reply = opened.append(
                message(
                    kind,
                    "PYTHON REPLY",
                    "Reply body marker.",
                    reply_to_msgno=parent.identity.msgno,
                    external_id="2:236/100 22222222",
                    control_lines=(
                        ControlLine(
                            name="REPLY",
                            value="2:236/999 11111111",
                            raw="\x01REPLY: 2:236/999 11111111",
                        ),
                    ),
                )
            )
            linked = opened.update(
                parent.identity,
                MessagePatch(reply1st_msgno=reply.identity.msgno),
                parent.revision,
            )
            long = opened.update(
                linked.identity,
                MessagePatch(body_text="Long body.\n" * 80),
                linked.revision,
            )
            short = opened.update(
                long.identity,
                MessagePatch(body_text="Python body marker.\nDansk: æøå ÆØÅ."),
                long.revision,
            )
            discarded = opened.append(
                message(kind, "DELETED PYTHON", "Must disappear.")
            )
            opened.delete(discarded.identity, discarded.revision)
        assert len(tuple(reader_type().read(base))) == 3
        with session(writer, base, kind, board) as opened:
            assert opened.read(parent.identity.msgno).revision == short.revision
            unrelated_revision = opened.read(unrelated.identity.msgno).revision
        checks.append("Python create/append/update longer/update shorter/delete")
        config = configure(root, binary, kind, base, board)
        terminal = Terminal(binary, config)
        try:
            terminal.wait("PYTHON.TEST")
            terminal.send(
                b"\r", "PYTHON PARENT", "Python body marker.", "Dansk: æøå ÆØÅ."
            )
            assert "Test Recipient" in terminal.text
            terminal.send(b"+", "PYTHON REPLY", "Reply body marker.")
            terminal.send(b"-", "PYTHON PARENT", "Python body marker.")
            checks.append("GoldED reads Python records and navigates reply links")
            terminal.send(b"c", "Edit 1,1.")
            terminal.send(b"GoldED changed marker.\r", "Edit 2,1.")
            terminal.send(b"\x1a", "Read All", "GoldED changed marker.")
            terminal.send(b"e", "Edit ")
            terminal.send(b"GoldED appended marker.\r")
            terminal.send(b"\x1a", "Read All")
            terminal.quit()
        finally:
            terminal.close()
        rows = tuple(reader_type().read(base))
        assert len(rows) == 4
        changed = next(row for row in rows if row.msgno == parent.identity.msgno)
        assert "GoldED changed marker." in changed.body_text
        assert "Dansk: æøå ÆØÅ." in changed.body_text
        assert changed.reply1st_msgno == reply.identity.msgno
        reply_row = next(row for row in rows if row.msgno == reply.identity.msgno)
        assert reply_row.reply_to_msgno == parent.identity.msgno
        new = next(row for row in rows if "GoldED appended marker." in row.body_text)
        assert new.from_name == "Test Operator"
        assert changed.control_lines.charset == "CP850 2"
        checks.append(
            "Python strict reader validates GoldED edit and append; CP850 survives"
        )
        lastread_names = {"base.jlr", "base.sql", "lastread", "lastread.bbs"}
        lastread = {
            p.relative_to(root): p.read_bytes()
            for p in root.rglob("*")
            if p.is_file() and p.name.lower() in lastread_names
        }
        expected = {"jam": "base.jlr", "squish": "base.sql", "hudson": "lastread.bbs"}
        if kind in expected:
            assert any(p.name.lower() == expected[kind] for p in lastread)
        assert lastread and all(lastread.values()), "Expected populated lastread files"
        with session(writer, base, kind, board) as opened:
            assert opened.read(unrelated.identity.msgno).revision == unrelated_revision
            try:
                opened.update(
                    short.identity, MessagePatch(subject="Stale"), short.revision
                )
            except ConflictError:
                pass
            else:
                raise AssertionError("GoldED edit did not invalidate Python revision")
            old = opened.read(new.msgno)
            patched = opened.update(
                old.identity,
                MessagePatch(
                    subject="PYTHON UPDATED GOLDED", body_text="Python re-edit marker."
                ),
                old.revision,
            )
            reread = opened.read(new.msgno).message
            assert reread.control_lines == old.message.control_lines
            assert reread.posted_at == old.message.posted_at
            assert reread.attributes_raw == old.message.attributes_raw
        after_lastread = {
            p.relative_to(root): p.read_bytes()
            for p in root.rglob("*")
            if p.is_file() and p.name.lower() in lastread_names
        }
        assert after_lastread == lastread
        checks.append(
            "Python preserves exposed controls/date/attrs and lastread; stale conflict"
        )
        terminal = Terminal(binary, config)
        try:
            terminal.wait("PYTHON.TEST")
            terminal.send(b"\r", "Read All")
            terminal.send(b">", "PYTHON UPDATED GOLDED", "Python re-edit marker.")
            terminal.send(b"d", "Delete")
            terminal.send(b"y", "Read All")
            terminal.quit()
        finally:
            terminal.close()
        rows = tuple(reader_type().read(base))
        assert len(rows) == 3
        assert patched.identity.msgno not in {row.msgno for row in rows}
        assert {row.msgno for row in rows} == {
            parent.identity.msgno,
            unrelated.identity.msgno,
            reply.identity.msgno,
        }
        assert {row.subject for row in rows} == {
            "PYTHON PARENT",
            "UNRELATED",
            "PYTHON REPLY",
        }
        checks.append("GoldED rereads/deletes Python-edited record; Python validates")
    return {
        "format": kind,
        "board": board if kind == "hudson" else None,
        "checks": checks,
        "lastread_files_compared": len(lastread),
    }


def run_golded_create(binary, kind, board):
    """GoldED creates the format files; Python validates its first message."""
    writer_type, reader_type, _ = FORMATS[kind]
    with tempfile.TemporaryDirectory(
        prefix="ftn-golded-create.", dir="/tmp"
    ) as directory:
        root = Path(directory)
        base = root / "base"
        if kind in ("msg", "hudson"):
            base.mkdir()
        config = configure(root, binary, kind, base, board)
        terminal = Terminal(binary, config)
        try:
            terminal.wait("PYTHON.TEST")
            terminal.send(b"\re", "Edit ")
            terminal.send(b"Created by GoldED marker.\r")
            terminal.send(b"\x1a", "Read All")
            terminal.quit()
        finally:
            terminal.close()
        rows = tuple(reader_type().read(base))
        assert len(rows) == 1, "Expected one GoldED-created message"
        assert "Created by GoldED marker." in rows[0].body_text
        writer = writer_type()
        with session(writer, base, kind, board) as opened:
            old = opened.read(rows[0].msgno)
            changed = opened.update(
                old.identity,
                MessagePatch(subject="Python changed GoldED base"),
                old.revision,
            )
            assert (
                opened.read(rows[0].msgno).message.subject
                == "Python changed GoldED base"
            )
            opened.delete(changed.identity, changed.revision)
        assert tuple(reader_type().read(base)) == (), "Python delete did not empty base"
    return {
        "format": kind,
        "board": board if kind == "hudson" else None,
        "checks": ["GoldED creates base/message; Python reads/updates/deletes"],
    }


def main():
    if not __debug__:
        raise RuntimeError(
            "Run without Python optimization; probe assertions are required"
        )
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", required=True, type=Path)
    parser.add_argument("--format", choices=FORMATS, action="append")
    parser.add_argument("--board", type=int, default=1)
    parser.add_argument(
        "--scenario", choices=("interoperability", "create", "both"), default="both"
    )
    args = parser.parse_args()
    if not 1 <= args.board <= 200:
        parser.error("board must be 1–200")
    binary = args.binary.expanduser().resolve(strict=True)
    if not binary.is_file() or not os.access(binary, os.X_OK):
        parser.error("binary must be an executable file")
    print(
        json.dumps(
            {
                "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
                "platform": platform.platform(),
                "packages": {
                    name: importlib.metadata.version(name)
                    for name in (
                        "golded-ftn",
                        "golded-ftn-msg",
                        "golded-ftn-jam",
                        "golded-ftn-squish",
                        "golded-ftn-hudson",
                    )
                },
            }
        ),
        flush=True,
    )
    failed = False
    probes = {"interoperability": run_format, "create": run_golded_create}
    selected = (
        probes if args.scenario == "both" else {args.scenario: probes[args.scenario]}
    )
    for kind in args.format or FORMATS:
        for scenario, probe in selected.items():
            try:
                result = probe(binary, kind, args.board)
            except Exception as error:
                failed = True
                result = {
                    "format": kind,
                    "error": f"{type(error).__name__}: {error}",
                    "location": traceback.extract_tb(error.__traceback__)[-1].lineno,
                }
            result["scenario"] = scenario
            print(json.dumps(result, ensure_ascii=False), flush=True)
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
