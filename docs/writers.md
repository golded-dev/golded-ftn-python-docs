# Editing FTN message bases

The candidate versions are core 1.3.0, MSG 1.4.0, JAM/Squish/Hudson 1.3.0.
Offline editing remains the default. Explicit `WriterOptions(concurrent=True)` is
qualified only for the tested Linux/macOS GoldED 3.1.0 builds, Unix local filesystems
and the tested read, append, refresh, lastread and stale-editor scenarios. A matching
lock byte alone does not establish compatibility with another editor or build.
Windows and network filesystems are outside this profile. MSG/Opus stale-save
checks detect changes but do not supply an atomic shared writer transaction with
GoldED; avoid simultaneous MSG/Opus edits to the same message.

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
MSG supports explicit FTSC or Opus writes; Opus timestamp policy remains explicit. Hudson supports classic .BBS, not
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

Ordinary open() provides no transaction guarantee for process termination or power
failure and no automatic repair. Use recovery_session() with a durable caller journal. Deterministic failure tests cover ordinary exceptions;
they do not prove recovery from every possible partial write.

## Verification boundary

Local binary fixtures and injected-failure tests are separate from GoldED
interoperability. See each format's README and tests for exact coverage. POSIX
locks are implemented for macOS/Linux and Windows has an offline lock/I/O path;
only platforms actually tested may be reported as tested. GoldED source is the
format reference, not evidence that the current executable accepts the output.

The suite includes packet, nodelist, BSO/binkp, tosser and CLI packages with separate
policy boundaries. The GoldED 3.1.0 source candidate has native macOS/Linux
read/edit/refresh/stale-save checks recorded against the pinned source and binaries.
Offline remains the default; explicit concurrent mode is bounded to that profile.

## Check the candidate wheels

```sh
uv run python scripts/install_readers.py --wheelhouse /path/to/reviewed/wheelhouse
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run python scripts/check_examples.py
```

No sibling working copies are required. `--local` selects the suite's retained
candidate wheelhouse; the default installer uses exact candidate versions from the
public index after their separately authorized publication. package-refs.json
records local candidate commits, not already-published releases.

## Recovery sessions

Each format exposes `recovery_session(path, recovery_root=..., options=...)`;
MSG additionally requires explicit header_format and Hudson may require board and
scan_path. Under the base lock, inspect pending mutations and reconcile their
transaction UUID with the caller's durable journal. `prepare_append`,
`prepare_update` and `prepare_delete` persist recoverable intent; `apply` mutates;
`settle` finalizes or rolls back according to CommitState. COMMITTED, UNCOMMITTED
and UNKNOWN are different outcomes. An unknown commit must keep recovery evidence
and block automatic replay. Preserve the state directory and physical-base identity
through restart. A journal filename alone does not identify an unchanged base.

## Filename case and compatibility

Format options expose extension_case for new bases. Existing uppercase/lowercase
files are opened in their existing case; ambiguous mixed duplicates are rejected.
For the Unix GoldED profile select lower for newly created JAM, MSG, Squish and
Hudson files and keep Hudson scan files in the configured system directory.
The qualified GoldED 3.1.0 code resolves existing casing; older binaries may split
one apparent base into separate files on case-sensitive filesystems.

The suite manifest pins the exact source archive and native verification builds.
Earlier compatibility results refer to their recorded binaries and cannot be
silently transferred to another build. See the manifest before production use.
