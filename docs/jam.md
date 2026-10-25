# JAM format reference

Read and edit JAM revision 1 areas with `golded_ftn_jam`. A basename identifies
separate header, text and index files. Python 3.12+ is required. Version 1.3.0 is published on
[PyPI](https://pypi.org/project/golded-ftn-jam/1.3.0/).

Use the [core API reference](core-api.html) for shared models and errors, and
[Editing message bases](writers.html) for revision and patch contracts.

## Public API

The package exports exactly `JamReader`, `JamWriter` and `JamSession`.
Construct readers and writers without arguments. Obtain a session through `open`
and use it as a context manager; a closed or poisoned session cannot be reused.

```text
JamReader()
JamReader.read(path: str | PathLike[str], options: ReaderOptions | None = None)
    -> Iterable[ParsedMessage]
JamWriter()
JamWriter.create(path: str | PathLike[str]) -> None
JamWriter.open(path: str | PathLike[str], options: WriterOptions | None = None)
    -> JamSession
JamSession(base: Path, options: WriterOptions)
JamSession.read(msgno: int) -> SessionMessage
JamSession.append(message: OutgoingMessage) -> WriteResult
JamSession.update(identity: MessageIdentity, patch: MessagePatch,
    expected_revision: RevisionToken) -> WriteResult
JamSession.delete(identity: MessageIdentity,
    expected_revision: RevisionToken) -> MessageIdentity
```

## Base paths and initialization

Pass an exact basename without an extension, such as `areas/general`.
The reader resolves `.JHR`, `.JDT` and `.JDX` case-insensitively. Each must identify
one regular file; symlinks and ambiguous extension variants are rejected.

`create` refuses existing base files, creates parent directories and initializes:

| File | Contents and role |
| --- | --- |
| `.JHR` | 1024-byte base header with JAM signature; message headers and subfields follow |
| `.JDT` | Empty message text file |
| `.JDX` | Empty fixed-slot index |
| `.JLR` | Empty lastread file |

The initial message number is 1. Standalone reading ignores `.JLR`; edits preserve
existing lastread bytes. The index determines message numbers and live records.
Index holes and deleted messages are skipped; old unindexed headers are ignored.
Identity uses format `jam`, resolved basename and JAM message number, separately
from external MSGID. Provenance identifies the `.JHR` header location.

## Reading and metadata

Default reading streams indexed messages: the index is loaded, then each header
and body is sought and yielded in message-number order. Pass
`ReaderOptions(eager=True)` to restore the older behaviour that loads the three
files, validates every indexed record, and returns a tuple before any message
escapes. With eager mode, a malformed later record cannot produce a partial
result. Streaming may yield earlier messages before a later failure. Validation
covers signatures, revision, record boundaries, offsets, subfield lengths,
message numbers and reused header offsets. Damage and decoding failures raise
`ParserException` with source path, physical offset and chained cause.
Filesystem errors remain filesystem errors.

The standalone reader takes no lock and provides no cross-file snapshot. Stop
writers or read a consistent copy. Use session `read` for a locked read and a
revision suitable for editing.

Decoding is strict with CP850 fallback. Header FTSKLUDGE charset declarations
precede body declarations; conflicting declarations and IDs fail. Unknown charset
names use the configured fallback. No mojibake repair is performed.

`body_text` contains normalized `.JDT` text. Header controls and routing subfields
populate `control_lines`, before body metadata. Repeated controls and routing
retain order within the model's sequences. Unknown subfields and nonzero HiID
values are bounds-checked and skipped in the parsed view, but preserved by edits.
The first originating/destination address is retained as decoded text, including
node zero, point and domain. Repeated single-value metadata must agree.
Header MSGID/REPLYID take precedence over matching inline values; absent MSGID
uses the core synthetic identity.

Dates are naive `1970-01-01 + DateWritten seconds`, independent of local timezone;
zero becomes `None`. TZUTC remains a control. Raw attributes and all three reply
links are retained; zero links become `None`. Unsupported active compressed,
encrypted or escaped messages are rejected.

## Writing and limits

CP850 is the default writer encoding. Encoding is strict; conflicting charset
metadata, truncation and embedded nulls in body text are rejected. Body newlines
serialize as CR. Address components must fit unsigned 16-bit values; domains may
contain letters, digits, dots, underscores and hyphens and must start with a letter
or digit. Attributes, reply links, message numbers, timestamps, offsets and lengths
use unsigned 32-bit values. Unsupported compression/encryption/escape and deleted
attributes cannot be used for a normal append.

Dates serialize as whole epoch seconds. Naive dates are interpreted as UTC;
aware dates use their UTC timestamp. `None` uses zero, which also means no date
when reading. Fractional seconds are discarded.

Supported bounded metadata uses encoded-byte limits: addresses, names, IDs and
subject (subfield IDs 0–6) allow 100 bytes, PID allows 40, and FTSKLUDGE allows
255. Metadata must be a single line without nulls or control separators.
Routing is supplied explicitly; MSGID, routing and duplicate checks are never
generated automatically.

JAM has `reply_to_msgno`, `reply1st_msgno` and `reply_next_msgno`. Arbitrary reply
lists are unsupported. Provenance cannot be patched. Omitted patch fields retain
raw values; optional metadata can be cleared with `None`, while names, subject,
text and attributes reject `None`.

General `control_lines` replacement affects header controls and inline controls.
Omitted MSGID, addresses and routing retain their separate fields. Explicit
conflicts are rejected. External-ID and routing patches remove obsolete inline
copies; body-only changes preserve existing controls and routing.

Content updates append a new header/subfields and text, then redirect the index.
Header-only changes preserve text bytes and placement. Unknown subfields, HiID,
reserved words, timestamps and omitted reply links survive. CRCs, modification
counter and active count are maintained. Delete sets the header's deleted bit,
sets recipient index CRC to `FFFFFFFF` and decrements the active count. Message
numbers remain unchanged; other messages' reply links are not rewritten.
Old blocks are left in place. Packing and repair are outside this package.

## Create, read, update and delete

This example creates a temporary base, changes its text and removes its message.
No archive or user data is involved.

```python
from pathlib import Path
from tempfile import TemporaryDirectory

from golded_ftn import MessagePatch, OutgoingMessage
from golded_ftn_jam import JamReader, JamWriter

with TemporaryDirectory() as directory:
    base = Path(directory) / "general"
    writer = JamWriter()
    writer.create(base)
    with writer.open(base) as session:
        added = session.append(
            OutgoingMessage(
                from_name="Alice",
                to_name="Bob",
                subject="Hello",
                body_text="First line",
            )
        )
        current = session.read(added.identity.msgno)
        changed = session.update(
            current.identity,
            MessagePatch(body_text="A longer second line"),
            current.revision,
        )
        assert (
            session.read(changed.identity.msgno).message.body_text
            == "A longer second line"
        )
        assert session.delete(changed.identity, changed.revision) == changed.identity
    assert list(JamReader().read(base)) == []
    assert base.with_suffix(".JLR").read_bytes() == b""
```

## Archive reading

Archive reading requires `ReaderOptions(archive_mode=True, on_issue=...)`.
Issues report `recovered`, `skipped` or `stopped`, actual file, record identity and
physical offset without message contents. A stop marks incomplete traversal;
a validated prefix may be returned. Multiple issues can describe one record.

Overlong bounded fields are retained and reported. Malformed TZUTC remains
uninterpreted. Distinct PID, FLAGS and TZUTC entries preserve source order.
Conflicting single-value metadata or charset declarations are skipped, never
guessed. Failed records use the next fixed index slot; reused header offsets
stop traversal. Declared ASCII may use the configured strict fallback and report
recovery without changing its original control. Other decoding failures are
skipped. Callback and filesystem exceptions propagate; files must remain stable.
Archive mode never enables writer repair or damaged-base editing.

## Locks, rollback and compatibility

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

JAM locks JHR byte 0 and retains that descriptor through index/header/text mutations. Recovery covers JHR/JDT/JDX; JLR is untouched.

Ordinary I/O rollback preserves earlier completed operations. A rollback failure
poisons the session. Recovery sessions stage durable mutations and reconcile the
caller journal; UNKNOWN commit state keeps evidence and prevents blind replay.

## Implementation references

- [Package README](https://github.com/golded-dev/golded-ftn-jam-python/blob/main/README.md)
- [Reader](https://github.com/golded-dev/golded-ftn-jam-python/blob/main/src/golded_ftn_jam/reader.py)
  and [writer](https://github.com/golded-dev/golded-ftn-jam-python/blob/main/src/golded_ftn_jam/writer.py)
- Original GoldED commit `600266252b73174ff5116cee697ef9a97aeb1859`:
  `gmojamm.h` structures, `gmojamm2.cpp` initialization and scan,
  `gmojamm4.cpp` locking and save, and `gcrcs32.cpp::strCrc32` CRC behavior.
  These establish source layout and write semantics, not tested live compatibility.

## Candidate API additions

Public exports: `JamReader`, `JamSession`, `JamWriter`, `JamWriterOptions`.

Format options select extension_case for new files and preserve existing case.
`recovery_session` adds durable staged mutation and explicit journal settlement.
See [Editing message bases](writers.html) for recovery and concurrency prerequisites.

```text
JamWriterOptions(*, target_charset: 'str' = 'CP850', lock_timeout: 'float' = 5.0, concurrent: 'bool' = False, extension_case: "Literal['upper', 'lower']" = 'upper') -> None
```

```text
JamWriter.create(self, path: 'str | PathLike[str]', options: 'WriterOptions | None' = None) -> 'None'
```

```text
JamWriter.open(self, path: 'str | PathLike[str]', options: 'WriterOptions | None' = None) -> 'JamSession'
```

```text
JamWriter.recovery_session(self, path: 'str | PathLike[str]', *, recovery_root: 'str | PathLike[str]', options: 'WriterOptions | None' = None) -> 'Iterator[JamRecoverableSession]'
```
