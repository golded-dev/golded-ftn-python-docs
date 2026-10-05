# Editing FTN message bases

The 1.2.0 working sources add writers for FTSC MSG, JAM revision 1, classic
Squish and classic Hudson. Stop GoldED and other base users before editing.
`WriterOptions(concurrent=True)` is rejected: compatibility with a current
GoldED build, concurrent reading and refresh are deferred. A matching byte lock
alone does not establish safe concurrent use.

## Session API

The [complete core API reference](core-api.md) covers all public exports.
Core exports `OutgoingMessage`, `MessagePatch`, `MessageIdentity`,
`RevisionToken`, `SessionMessage`, `WriteResult` and writer errors. Each format
exports its writer: `MsgWriter`, `JamWriter`, `SquishWriter`, `HudsonWriter`.

`create(path)` initializes a whole base and refuses existing base files. Hudson
creation is not board-specific. `open(path, options)` is a context-managed
session; Hudson also requires an explicit board in 1–200. Its optional
`scan_path` identifies GoldED's system directory when that differs from the base.

| Operation | Result |
| --- | --- |
| `read(msgno)` | `SessionMessage(message, identity, revision)` |
| `append(message)` | `WriteResult(identity, revision)` |
| `update(identity, patch, expected_revision)` | `WriteResult(identity, revision)` |
| `delete(identity, expected_revision)` | The deleted `MessageIdentity` |

These values have keyword-only constructors. Access the parsed message through
`session.read(number).message`. Keep the returned identity and revision together.
A revision covers the message's raw header, metadata and text bytes and physical
record location. It excludes base-wide counters. An unrelated message change
must not invalidate it. A changed or missing edit target raises `ConflictError`.

An omitted patch field is `UNSET` and remains unchanged. `None` explicitly clears
only a field the format can clear; unrepresentable requests fail. Updates start
from raw records so unknown metadata, timestamps and attribute bits survive.
Attribute-only changes preserve text bytes. Reply fields are format-specific;
Squish retains its complete nine-entry reply array. If a patch supplies both
`reply_list` and `reply1st_msgno`, they must agree, including explicit zero or
`None`. A body-only patch preserves omitted routing. Replacing `control_lines`
keeps omitted structured MSGID and address fields; conflicting explicit controls
are rejected. JAM handles controls in both header subfields and inline text. Deletion does not rewrite
other messages' reply links, and message identities are never renumbered.

This example edits one synthetic message in each format. It uses no archive:

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from golded_ftn import MessagePatch, OutgoingMessage
from golded_ftn_jam import JamWriter
from golded_ftn_msg import MsgWriter
from golded_ftn_squish import SquishWriter
from golded_ftn_hudson import HudsonWriter

message = OutgoingMessage(
    from_name="Alice",
    to_name="Bob",
    subject="Demo",
    body_text="Hello.",
)
with TemporaryDirectory() as root:
    for name, writer in (
        ("msg", MsgWriter()),
        ("jam", JamWriter()),
        ("squish", SquishWriter()),
    ):
        path = Path(root) / name
        writer.create(path)
        with writer.open(path) as session:
            added = session.append(message)
            loaded = session.read(added.identity.msgno)
            changed = session.update(
                loaded.identity,
                MessagePatch(body_text="Edited."),
                loaded.revision,
            )
            assert session.read(changed.identity.msgno).message.body_text.endswith(
                "Edited."
            )
            session.delete(changed.identity, changed.revision)
        print(name)
    hudson = HudsonWriter()
    path = Path(root) / "hudson"
    hudson.create(path)
    with hudson.open(path, board=200) as session:
        added = session.append(message)
        loaded = session.read(added.identity.msgno)
        changed = session.update(
            loaded.identity,
            MessagePatch(body_text="Edited."),
            loaded.revision,
        )
        assert session.read(changed.identity.msgno).message.body_text.endswith(
            "Edited."
        )
        session.delete(changed.identity, changed.revision)
    print("hudson")
```

## Encoding and message policy

`WriterOptions` defaults to CP850 and a five-second monotonic lock timeout.
Encoding is strict: unencodable characters, conflicting charset declarations,
field overflow and unrepresentable dates or addresses fail before data writes.
MSG writes FTSC; Opus editing is rejected. Hudson supports classic .BBS, not
GoldBase. Routing strings remain unexpanded. Writers do not generate MSGID,
route messages or check duplicates.

## Locks and rollback

| Format | Lock | Content update |
| --- | --- | --- |
| MSG | Internal coordination, offline with GoldED | Complete file replacement |
| JAM | Byte 0 in .JHR | New header/subfields and text; redirect .JDX |
| Squish | Byte 0 in .SQD | New frame; maintain chains, .SQI and free list |
| Hudson | Byte 407 in MSGINFO.BBS | New Pascal text blocks; replace headerslot |

Each operation rereads control data under the lock and flushes before unlocking.
Session reads use that same lock and descriptor. Caller access to base files
outside the session is forbidden while operations run: POSIX closes on another
descriptor can release a process's record locks.

The shared I/O seam snapshots original bytes and sizes before mutation. Ordinary
write or flush failures trigger in-place rollback under the lock. A failed
rollback raises `RollbackError` with base and operation context and disables the
session. Earlier completed operations survive later failures. Full-file
snapshots cost memory proportional to base size. Locked files are never replaced
by rename. Existing lastread data is preserved.

There is no transaction guarantee for process termination or power failure and
no automatic repair. Deterministic failure tests cover ordinary exceptions;
they do not prove recovery from every possible partial write.

## Verification boundary

Local binary fixtures and injected-failure tests are separate from GoldED
interoperability. See each format's README and tests for exact coverage. POSIX
locks are implemented for macOS/Linux and Windows has an offline lock/I/O path;
only platforms actually tested may be reported as tested. GoldED source is the
format reference, not evidence that the current executable accepts the output.

The integration build and GoldED read/write/cache/refresh checks remain deferred
at the user's request. Concurrent mode stays disabled on every platform.
No BBS, tosser, packet, packing, repair or GoldED changes are included.

## Check the working sources

Keep all five package repositories beside this documentation repository:

```sh
uv run python scripts/install_readers.py --local
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run python scripts/check_examples.py
```

`--local` builds and installs wheels from sibling development checkouts. Without
that flag, the installer uses `package-refs.json`, which pins the public 1.2.0
release commits. All five packages are published on PyPI. GoldED interoperability
checks remain deferred; concurrent mode is disabled.
