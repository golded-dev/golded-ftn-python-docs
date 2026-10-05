# Squish message bases

Read classic Squish areas and edit them offline with `golded-ftn-squish`.
Imports use `golded_ftn_squish`. Version 1.2.0 is available on
[PyPI](https://pypi.org/project/golded-ftn-squish/1.2.0/). Python 3.12 or newer is required.

The [core API reference](core-api.html) defines shared models and errors.
[Editing message bases](writers.html) defines patches, revision tokens and the
common session contract. This page covers Squish's storage and public API.

## Public API

The package exports exactly `SquishReader`, `SquishWriter` and `SquishSession`.
Construct a reader with `SquishReader()`. Construct a writer with
`SquishWriter()`; its keyword-only `io: IO | None = None` argument is an internal
fault-injection hook, not a second storage backend.

| Call | Result |
| --- | --- |
| `SquishReader().read(path, options=None)` | `Iterable[ParsedMessage]`, ordered by UID |
| `SquishWriter().create(path)` | `None` |
| `writer.open(path, options=None)` | Context-managed `SquishSession` |
| `session.read(msgno)` | `SessionMessage` |
| `session.append(message)` | `WriteResult` |
| `session.update(identity, patch, expected_revision)` | `WriteResult` |
| `session.delete(identity, expected_revision)` | Deleted `MessageIdentity` |

Paths accept `str` or `PathLike[str]`. Reader options are `ReaderOptions`;
writer options are `WriterOptions`. Arguments to append, update and delete use
`OutgoingMessage`, `MessageIdentity`, `MessagePatch` and `RevisionToken`.
`SquishSession(base: Path, options: WriterOptions, io: IO)` is exported, but
`writer.open()` supplies its dependencies and is the normal entry point.
The context manager returns the session and closes it on exit.

## Files and initialization

Pass a basename without an extension, such as `messages/general`. Readers require
regular `.SQD` and `.SQI` files, resolve extensions case-insensitively and reject
ambiguous candidates. `create()` requires an existing parent directory and rejects
existing `.SQD`, `.SQI` or `.SQL` files for that basename. It creates a 256-byte
`.SQD` area header and empty `.SQI` and `.SQL` files. The basename must fit within
79 filesystem-encoded bytes. Editing preserves existing `.SQL` lastread bytes.

The supported layout has a 256-byte area header, 28-byte frame header,
238-byte message header and 12-byte index records. Extended layouts, compressed
frames and frames marked as being updated are rejected. The active index prefix
is selected by the area message count; preallocated index tails are ignored.
Unindexed old and free frames are ignored by the reader. Active frames must have
positive increasing unique UIDs and distinct, non-overlapping extents.

The first newly allocated UID is 2, matching GoldED initialization. `msgno` is
this persistent UID, not an index position or external MSGID. A valid header UID
is checked when the MSGUID attribute marks it as present. Gaps are allowed.
UIDs are preserved across updates and never renumbered by deletion.

## Reading and metadata

Standalone reading requires stable files: `.SQD` and `.SQI` are read separately,
without a lock or atomic snapshot. Strict mode validates every active record
before returning messages. Filesystem failures remain filesystem errors;
malformed records and decoding failures raise `ParserException` with the actual
path, byte offset and chained cause. Session `read()` instead takes the writer's
lock and provides a consistent read.

Names, subject and body decode strictly, with CP850 fallback. Charset declarations
in the separate control block precede body declarations; conflicting declarations
fail. `body_text` is the normalized body payload. Separate header controls appear
in `control_lines` before body controls. Controls retain order and repetitions.
The control block uses SOH separators; empty segments, trailing SOH, line breaks
and non-NUL bytes after a NUL terminator fail strict reading.

Header and body MSGID/REPLY values must agree. MSGID becomes `external_id`;
otherwise core derives a synthetic ID over decoded normalized fields. It is
separate from the Squish UID. Controls and routing map through core helpers;
no routing or MSGID is generated automatically. Binary addresses preserve node
zero and points. INTL/FMPT/TOPT may supplement incomplete components, subject
to conflict checks. Unresolvable addresses become `None`; no domain is invented.

A valid packed DateWritten becomes timezone-aware UTC. The stored signed UTC
offset does not alter it. A zero packed date permits a valid, timezone-naive
FTSC-date fallback; invalid dates become `None`. Arrival time and binary UTC
offset have no dedicated core fields. Existing TZUTC controls remain metadata.
Attributes are raw Squish bits, not a cross-format bit mask.

`reply_to_msgno` and `reply1st_msgno` map header UIDs, with zero represented by
`None`. `reply_next_msgno` is `None`: the other eight entries are a reply list,
not next-sibling pointers. Writers preserve all nine entries internally.
Provenance identifies `squish`, the actual SQD filename, UID and frame offset.
Configured area names and other unsupported metadata remain `None`.

## Editing and limits

Updates start with the raw record. Omitted fields preserve unknown metadata,
arrival time, UTC offset and attribute bits. Attribute-only patches preserve
control and text bytes. Content changes append a new frame, redirect the index,
update the active chain and put the previous frame on the free list. No free-frame
reuse, merging, packing or automatic purge is performed. Other messages' reply
links are not rewritten.

`reply_list` accepts up to nine UIDs. If supplied with `reply1st_msgno`, their first
entry must agree, including an explicit zero or `None`. `reply_next_msgno` cannot
represent the Squish reply array. Body-only patches preserve omitted routing;
control replacement preserves an omitted `external_id` and rejects conflicting
MSGID declarations. Use structured fields for deliberate metadata changes.

Serialization uses strict `WriterOptions.target_charset`, CP850 by default.
Charset declarations must agree. Encoded sender and recipient names are limited
to 35 bytes each, subjects to 71 bytes, leaving space for a NUL. No silent
truncation or replacement characters are used. New dates must be timezone-aware
and lie within 1980–2107; they are converted to UTC and packed at two-second
precision. The existing raw date survives an omitted date patch.

An area `maxmsgs` setting rejects appends at capacity. The writer rejects exhausted
UID allocation and frame extents beyond the signed 32-bit file-offset limit.
It does not remove another message to make room. Invalid or unrepresentable
values fail before data writing.

## Synthetic CRUD example

This example uses an empty temporary area and no message archive.

```python
from pathlib import Path
from tempfile import TemporaryDirectory

from golded_ftn import MessagePatch, OutgoingMessage
from golded_ftn_squish import SquishReader, SquishWriter

with TemporaryDirectory() as directory:
    base = Path(directory) / "general"
    writer = SquishWriter()
    writer.create(base)
    with writer.open(base) as session:
        added = session.append(
            OutgoingMessage(
                from_name="Alice", to_name="Bob", subject="Hello", body_text="Body"
            )
        )
        assert added.identity.msgno == 2
        current = session.read(added.identity.msgno)
        assert current.message.subject == "Hello"
        changed = session.update(
            current.identity, MessagePatch(body_text="A longer body"), current.revision
        )
        session.delete(changed.identity, changed.revision)
    assert list(SquishReader().read(base)) == []
```

## Archive mode and safety

Archive reading requires `ReaderOptions(archive_mode=True, on_issue=callback)`.
Issues report `recovered`, `skipped` or `stopped`, file, identity and physical
offset without message contents. The index UID wins over a conflicting header
UID with a report; empty control segments are ignored with reports. Failed
indexed messages are skipped. Invalid UID order, duplicate offsets, overlapping
frames and truncated indices stop traversal. A returned prefix may be incomplete.
Charset and metadata conflicts are skipped. Declared ASCII decoding failures may
try the configured fallback strictly, with a report; the original declaration
is preserved. Other decoding failures are skipped. Callback and filesystem
exceptions propagate. Archive mode neither repairs nor licenses editing.

Each session operation locks byte 0 of `.SQD`, rereads and validates the base,
including the active index and both frame chains, and flushes before unlocking.
The core lock manager serializes cooperating sessions in one process and keeps
one descriptor for the lock file. Do not directly open or close base files during
an operation. Revision tokens cover identity, frame offset and raw message bytes;
neighbor links are excluded because another append changes them. Missing or
changed targets raise `ConflictError`, while unrelated changes do not.

Handled write, truncate and flush failures restore watched bytes and file sizes
in place under the lock. Previous completed operations remain committed. Failed
rollback raises `RollbackError` and makes the session unusable. This provides no
transactional guarantee for process termination or power loss.

Use the writer offline with GoldED closed. `concurrent=True` raises
`UnsupportedOperationError` on every platform. macOS runtime tests are recorded;
Linux and Windows execution and current GoldED build integration remain
unverified. A compatible byte lock alone does not prove safe concurrent reading,
cache refresh or competing writes.

See the [package source and tests](https://github.com/golded-dev/golded-ftn-squish-python),
its [writer source notes](https://github.com/golded-dev/golded-ftn-squish-python/blob/main/docs/writer-sources.md)
and the [independent Squish structures](https://github.com/fidosoft/maximus/blob/master/msgapi/api_sq.h).
