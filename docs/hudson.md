# Hudson message bases

Read and edit classic `.BBS` Hudson bases with `golded-ftn-hudson`. Imports use
`golded_ftn_hudson`. Python 3.12 or newer is required. Version 1.3.0 is published on
[PyPI](https://pypi.org/project/golded-ftn-hudson/1.3.0/). GoldBase `.DAT` is a different format and
is not supported.

The [core API reference](core-api.html) defines shared models and errors.
[Editing message bases](writers.html) defines the common session, patch and
revision contract. This page covers Hudson's boards, files and public API.

## Public API

The package exports exactly `HudsonReader` and `HudsonWriter`. Both have
no-argument constructors. The standalone reader reads all boards; it has no
board filter. A writer session always selects one explicit board in **1–200**.
The board may be passed positionally or as `board=7`.

| Call | Result |
| --- | --- |
| `HudsonReader().read(path, options=None)` | `Iterator[ParsedMessage]`, all boards in ascending message-number order |
| `HudsonWriter().create(path)` | `None`; initializes the whole base |
| `writer.open(path, board, options=None, *, scan_path=None)` | Context-managed Hudson session |
| `session.read(msgno)` | `SessionMessage` from the selected board |
| `session.append(message)` | `WriteResult` |
| `session.update(identity, patch, expected_revision)` | `WriteResult` |
| `session.delete(identity, expected_revision)` | Deleted `MessageIdentity` |

Paths and `scan_path` accept `str` or `PathLike[str]`. Options use
`ReaderOptions` or `WriterOptions`; messages, identities, patches and revisions
use `OutgoingMessage`, `MessageIdentity`, `MessagePatch` and `RevisionToken`.
`HudsonSession` is the return type of `open()`, not a package-root export.
Use the context manager, which returns the session and closes it on exit.

## Files and whole-base creation

Pass the directory containing the base, not a filename or board subdirectory.
The standalone reader needs regular `MSGIDX.BBS`, `MSGHDR.BBS` and `MSGTXT.BBS`
files. Names are case-insensitive; symlinks and ambiguous variants are rejected.
It ignores `MSGINFO.BBS`, `MSGTOIDX.BBS` and `LASTREAD.BBS`. Writer sessions also
validate and maintain the information and recipient-index files.

`create()` creates the directory if necessary, then initializes **the whole base,
not one board**. Any existing base filename, including a case variant, is rejected.

| Initial file | Contents |
| --- | --- |
| `MSGINFO.BBS` | 406 zero bytes |
| `LASTREAD.BBS` | 400 zero bytes |
| `MSGHDR.BBS`, `MSGIDX.BBS`, `MSGTOIDX.BBS`, `MSGTXT.BBS` | Empty |
| `NETMAIL.BBS`, `ECHOMAIL.BBS` | Empty scan indices |

Existing lastread data is preserved during editing. A 3-byte message-index record
selects a corresponding 187-byte header slot. Header strings are Pascal fields.
Text consists of 256-byte blocks: one length byte followed by up to 255 payload
bytes. Payloads are joined before decoding, including multibyte characters or
controls spanning blocks. Bytes outside declared lengths are padding.

Active message numbers are global across boards and lie in 1–65534. `0xffff`
marks a deleted index entry; headers marked deleted are also skipped. Index and
header numbers and boards must agree, and active numbers must be unique.
Complete unused headers and text blocks are ignored, but file alignment is
checked. Zero-block bodies, short or empty text blocks and bodies without a
final NUL are accepted by the reader.

## Reading and metadata

Read a stable directory with no concurrent writer. The standalone reader reads
files separately without locking or an atomic snapshot. By default it streams:
the index is loaded, then headers and text spans are sought per message. Pass
`ReaderOptions(eager=True)` to parse every active message before yielding; in
eager mode a later malformed record cannot leave a partial result. Filesystem
errors remain filesystem errors. Malformed records and strict decoding failures
raise `ParserException` with the actual filename, byte offset and chained cause.
Session reads are locked.

Decoding uses core charset handling with CP850 fallback. Repeated charset, MSGID
and REPLY declarations must agree. `body_text` retains control lines; core
normalizes line endings and removes trailing NULs. Controls and routing keep
source order within their separate model sequences. INTL, FMPT and TOPT support
space and colon forms and supplement incomplete binary addresses. Conflicts fail;
nonzero header components and node zero with an established net survive.
Incomplete addresses become `None`; domains are not inferred from IDs or Origin.

Dates use `MM-DD-YY HH:MM`: years 00–79 mean 2000–2079 and 80–99 mean
1980–1999. They are timezone-naive and independent of machine settings.
Invalid or missing dates become `None`; malformed Pascal lengths still fail.
Timezone controls remain metadata rather than changing this date interpretation.

`attributes_raw` combines the message attribute byte with the network attribute
byte shifted left eight bits. Reply-to and first-reply numbers are retained,
with zero mapped to `None`. The read-count word is not a next-reply link;
`reply_next_msgno` is `None`. MSGID supplies `external_id`; otherwise core
creates a synthetic ID over decoded normalized fields.

Each board maps to synthetic `area_code="BOARD<n>"` and
`area_meta_key="hudson:<n>"`. Area name and display order remain `None`: configured
board names are not stored in this base. Provenance identifies `hudson`, the
actual `MSGHDR.BBS` filename, message number and header offset.

## Editing, scan indices and limits

Identity includes format, resolved base path, board and global message number.
Allocation includes deleted headers and preserves the high-number watermark;
deleted numbers are not reused. A session cannot edit a target on another board.
Deletion does not change other messages' replies. Next-reply and reply-list
requests are rejected because those structures cannot be stored here.

Updates start from raw header and text bytes. Omitted fields preserve controls,
padding, read count, cost, unknown attribute bits and dates. `None` clears only
representable optional fields such as dates, addresses, MSGID and reply links.
Names, body, subject and attributes cannot be cleared. Attribute-only changes
preserve allocated text bytes. Content changes append fresh Pascal text blocks
and update the existing header slot; old text blocks remain allocated.

A body-only patch preserves control and routing lines. General control replacement
preserves omitted structured MSGID, addresses and routing. Use the corresponding
structured patch fields to replace or clear them; conflicting explicit controls
are rejected. No MSGID generation, routing generation or duplicate checks occur.

Strict serialization defaults to CP850 through `WriterOptions.target_charset`.
Contradictory charset declarations, unencodable text, oversized Pascal fields
and out-of-range integers fail. Encoded sender and recipient names are limited
to 35 bytes each and subjects to 72 bytes. Dates must be timezone-naive and lie
in 1980–2079; storage has minute precision. Domains cannot be stored. Point
addresses use explicit FMPT/TOPT controls. Message numbers and reply references
must fit their Hudson ranges; allocation rejects exhaustion beyond message number
65534. Text start and count and scan header-slot indices must fit 16-bit words.

`MSGTOIDX.BBS` stores the recipient or GoldED's `* Received *` and
`* Deleted *` markers. `NETMAIL.BBS` and `ECHOMAIL.BBS` store physical header
slots, not message numbers. Net-transmit and echo-transmit bits enqueue slots;
existing entries remain until explicit deletion, following GoldED's write path.

GoldED places scan indices in its configured system directory. If that differs
from the base, pass `scan_path=golded_system_path` to `open()`. By default the
scan directory is the base directory. Existing scan files are validated; missing
ones are created only when an operation adds an entry. Empty files remain after
removal. Do not share one scan directory among independent bases: that exceeds
this base lock's scope.

## Synthetic CRUD example

This example creates the whole base, edits board 7 and uses no message archive.

```python
from tempfile import TemporaryDirectory

from golded_ftn import MessagePatch, OutgoingMessage
from golded_ftn_hudson import HudsonReader, HudsonWriter

with TemporaryDirectory() as directory:
    writer = HudsonWriter()
    writer.create(directory)
    with writer.open(directory, board=7) as session:
        added = session.append(
            OutgoingMessage(
                from_name="Alice", to_name="Bob", subject="Hello", body_text="Body"
            )
        )
        assert added.identity.board == 7
        current = session.read(added.identity.msgno)
        assert current.message.subject == "Hello"
        changed = session.update(
            current.identity, MessagePatch(body_text="A longer body"), current.revision
        )
        session.delete(changed.identity, changed.revision)
    assert list(HudsonReader().read(directory)) == []
```

## Archive mode and safety

Archive reading requires `ReaderOptions(archive_mode=True, on_issue=callback)`.
Issues report `recovered`, `skipped` or `stopped`, with actual file, record
identity and physical offset but no message contents. Failed active records are
skipped through the next fixed slot. Duplicate numbers, missing indexed headers
and alignment failures stop traversal; a returned validated prefix may be
incomplete. Charset, ID and address conflicts are skipped. Failed declared ASCII
may be retried strictly with the configured fallback and a report, without
rewriting the declaration. Other decoding failures are skipped. Filesystem and
callback exceptions propagate. Archive mode requires stable files and is not
an editing or repair mode.

Every session operation locks byte **407** of `MSGINFO.BBS`, derived from the
packed 406-byte information structure plus one. It rereads the base, validates
active records and information counts, and flushes before releasing the lock.
The core manager serializes same-process sessions and retains one lock-file
descriptor. Callers must not directly open or close base files during operations.

Revision tokens cover identity, header/index/text positions and SHA-256 over raw
header, index, recipient-index and allocated text-block bytes. Update and delete
recheck under the lock. Missing or changed targets raise `ConflictError`;
unrelated appends do not invalidate the token.

Before mutation, affected files are watched for in-place rollback of bytes and
sizes under the lock. Each completed operation is independent; a later failure
does not undo it. Failed rollback raises `RollbackError` with base and operation
details and makes the session unusable. There is no crash journal, transactional
guarantee for process termination or power loss, or promise to detect every
partial write.

## Locks, recovery and compatibility

Candidate interoperability is bounded to GoldED source commit `d7449053bd674df54c4a442c92dce8c06ad7b586`,
version 3.1.0, native macOS arm64/GCC 16 and Ubuntu 24.04 aarch64/GCC 13.
The suite release manifest pins the resulting binaries and records actual checks.
Other GoldED versions, Windows and network filesystems are not qualified.

Writers default to offline operation. Explicit `concurrent=True` opts into the
tested read/write/refresh/lastread/stale-save profile, not a general multiwriter
guarantee. Standalone readers still need a stable base; a session read uses its
format lock. MSG/Opus and Goldbase have no shared GoldED writer lock: stale-save
detection cannot close a race between comparison and a foreign write. Keep
same-message edits serialized. Goldbase is outside the Python C1 profile.

Use format-specific WriterOptions extension_case="lower" for newly created
Unix bases used by GoldED; preserve existing casing and reject ambiguous twins.
Hudson scan queues belong in the configured system directory. Recovery sessions
have a durable journal protocol; ordinary open() sessions only roll back handled
I/O failures. UNKNOWN outcomes retain artifacts for operator reconciliation.

Hudson locks MSGINFO.BBS byte 407, validates whole-base records and preserves other boards. scan_path identifies the configured GoldED system directory.

Ordinary I/O rollback preserves earlier completed operations. A rollback failure
poisons the session. Recovery sessions stage durable mutations and reconcile the
caller journal; UNKNOWN commit state keeps evidence and prevents blind replay.

## Candidate API additions

Public exports: `HudsonAdapterError`, `HudsonReader`, `HudsonWriter`, `HudsonWriterOptions`.

Format options select extension_case for new files and preserve existing case.
`recovery_session` adds durable staged mutation and explicit journal settlement.
See [Editing message bases](writers.html) for recovery and concurrency prerequisites.

```text
HudsonWriterOptions(*, target_charset: 'str' = 'CP850', lock_timeout: 'float' = 5.0, concurrent: 'bool' = False, extension_case: "Literal['upper', 'lower']" = 'upper') -> None
```

```text
HudsonWriter.create(self, path: 'str | PathLike[str]', options: 'WriterOptions | None' = None) -> 'None'
```

```text
HudsonWriter.open(self, path: 'str | PathLike[str]', board: 'int', options: 'WriterOptions | None' = None, *, scan_path: 'str | PathLike[str] | None' = None) -> 'HudsonSession'
```

```text
HudsonWriter.recovery_session(self, path: 'str | PathLike[str]', *, recovery_root: 'str | PathLike[str]', options: 'WriterOptions | None' = None, scan_path: 'str | PathLike[str] | None' = None, board: 'int' = 1) -> 'Iterator[HudsonRecoverableSession]'
```
