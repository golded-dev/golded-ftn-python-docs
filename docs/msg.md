# MSG format reference

Read classic FTSC and Opus message directories. Edit FTSC messages through
`golded_ftn_msg`. Each message has its own numbered file and a 190-byte header.
Python 3.12+ is required. Candidate 1.4.0 is unpublished. The historical 1.2.0 release is on [PyPI](https://pypi.org/project/golded-ftn-msg/1.2.0/).

Use the [core API reference](core-api.html) for shared models and errors, and
[Editing message bases](writers.html) for revision and patch contracts.

## Public API

The package exports exactly `MsgReader`, `MsgWriter` and `MsgSession`.
Construct a writer without arguments. Obtain sessions through `open` and use them
as context managers; closing or a failed rollback makes them unusable.

```text
MsgReader(header_format: Literal["ftsc", "opus"] = "ftsc")
MsgReader.read(path: str | PathLike[str], options: ReaderOptions | None = None)
    -> Iterator[ParsedMessage]
MsgWriter()
MsgWriter.create(path: str | PathLike[str]) -> None
MsgWriter.open(path: str | PathLike[str], options: WriterOptions | None = None,
    *, header_format: Literal["ftsc", "opus"] = "ftsc") -> MsgSession
MsgWriter.write(path: str | PathLike[str], messages: Iterable[OutgoingMessage],
    options: WriterOptions | None = None) -> int
MsgSession(base: Path, options: WriterOptions)
MsgSession.read(msgno: int) -> SessionMessage
MsgSession.append(message: OutgoingMessage) -> WriteResult
MsgSession.update(identity: MessageIdentity, patch: MessagePatch,
    expected_revision: RevisionToken) -> WriteResult
MsgSession.delete(identity: MessageIdentity,
    expected_revision: RevisionToken) -> MessageIdentity
```

`write` is a batch convenience method: it creates the directory if needed and
returns the number of completed appends. Each append commits separately; an
exception on a later message leaves earlier appends in place.

## Area paths and initialization

Pass the directory, without a message filename. The reader accepts positive
numeric stems with case-insensitive `.msg` extensions, skips symlinks and reads
regular files in numeric order. Duplicate numeric identities are rejected, even
when filenames differ in padding or extension case.

`create` accepts a missing or empty directory and creates parent directories.
It refuses a nonempty directory. Opening a session initializes the private
`.golded-ftn-msg.lock` sidecar. This stores the highest allocated number, so
removing the highest message does not make its number available again.
Existing lastread files are preserved; no GoldED lastread file is required or
created for a new empty area.

Message identity uses format `msg`, the resolved area path and the filename
number. It is separate from an external MSGID. Reader provenance records the
actual filename and message number; byte offsets are unknown.

## Reading and metadata

FTSC is the default. Choose `MsgReader("opus")` explicitly for Opus: header
format detection is not automatic. FTSC words 176–183 represent zone and point;
Opus uses those bytes for DOS written/arrived timestamps. Opus addresses combine
header net/node with INTL/FMPT/TOPT, without interpreting timestamps as addresses.
Opus provenance uses source type `opus`.

Text decoding is strict, using core charset detection and CP850 fallback.
Kludges remain in the normalized body. Header addresses must agree with
INTL/FMPT/TOPT. Invalid FTSC textual dates become `None`; English month names and
the 1970–2069 two-digit year window are used. Opus written dates are naive,
have two-second precision and cover 1980–2107. Zero or invalid Opus timestamps
fall back to the textual date.

Raw 16-bit attributes are exposed as `attributes_raw`. The two header reply
words map to `reply_to_msgno` and `reply1st_msgno`; zero means no link.
General controls, external MSGID, addresses and routing remain distinct values.
No MSGID, routing or duplicate detection is generated automatically.

## Writing and limits

Writers require explicit FTSC or Opus selection. Opus timestamp policy is strict by
default; floor-seconds is an explicit opt-in for even-second DOS storage.
Names permit 35 encoded bytes and subjects 71. Header text rejects nulls, line
breaks and control separators. Encoding defaults to CP850 and is strict:
conflicting charset declarations, replacement characters and silent truncation
are refused. Dates must be naive, have no microseconds and lie in 1970–2069.
Address components, raw attributes and reply links use unsigned 16-bit values.
Domain addresses cannot be represented.

MSG represents only the reply-to and first-reply links. Additional reply links
and arbitrary reply lists are unsupported. Provenance is never serialized and
cannot be patched. Body lines serialize with CR and one terminating null byte;
embedded nulls are rejected.

Updates begin with the existing raw header. Unknown header bytes and omitted
fields survive. Attribute-only changes preserve original text bytes. Body-only
changes preserve controls and routing. `control_lines` replaces general controls;
omitted external MSGID, addresses and routing keep their structured values.
Explicit conflicting metadata is rejected. `None` clears only representable
optional values. Delete removes one file and leaves other messages' reply links
unchanged.

## Create, read, update and delete

This example uses an isolated temporary area. The session read issues the
revision used by the update; the updated revision is used for deletion.

```python
from pathlib import Path
from tempfile import TemporaryDirectory

from golded_ftn import MessagePatch, OutgoingMessage
from golded_ftn_msg import MsgReader, MsgWriter

with TemporaryDirectory() as directory:
    area = Path(directory) / "messages"
    writer = MsgWriter()
    writer.create(area)
    with writer.open(area) as session:
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
        assert session.read(changed.identity.msgno).message.body_text.endswith(
            "A longer second line"
        )
        assert session.delete(changed.identity, changed.revision) == changed.identity
    assert list(MsgReader().read(area)) == []
```

## Archive reading

Strict reading stops with `ParserException` for malformed message files; filesystem
errors remain filesystem errors. `ReaderOptions(archive_mode=True, on_issue=...)`
requires a callback and skips malformed records with `record_parse_error`.
Declared ASCII may fall back strictly to the configured charset, reporting
`ascii_decode_fallback`. Invalid UTF-8 and conflicting addresses are skipped.
Duplicate message numbers report `duplicate_message_number` with action `stopped`
before any messages are returned. Callback exceptions propagate. Issues identify
the source without including message contents. Archive mode never enables editing
or repairs original bytes.

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

MSG has no shared GoldED writer lock. Complete files are published atomically without clobbering existing names; updates replace the file. No numbering sidecar is created.

Ordinary I/O rollback preserves earlier completed operations. A rollback failure
poisons the session. Recovery sessions stage durable mutations and reconcile the
caller journal; UNKNOWN commit state keeps evidence and prevents blind replay.

## Implementation references

- [Package README](https://github.com/golded-dev/golded-ftn-msg-python/blob/main/README.md)
- [Reader](https://github.com/golded-dev/golded-ftn-msg-python/blob/main/src/golded_ftn_msg/reader.py)
  and [writer](https://github.com/golded-dev/golded-ftn-msg-python/blob/main/src/golded_ftn_msg/writer.py)
- [Writer source notes](https://github.com/golded-dev/golded-ftn-msg-python/blob/main/docs/writer-sources.md):
  original GoldED commit `600266252b73174ff5116cee697ef9a97aeb1859`,
  `gmofido.h` layout and `gmofido2.cpp` / `gmofido4.cpp` scan and write paths.

## Candidate API additions

Public exports: `MsgReader`, `MsgWriter`, `MsgWriterOptions`, `MsgSession`, `MsgRecoverableSession`.

Format options select extension_case for new files and preserve existing case.
`recovery_session` adds durable staged mutation and explicit journal settlement.
See [Editing message bases](writers.html) for recovery and concurrency prerequisites.

```text
MsgWriterOptions(*, target_charset: 'str' = 'CP850', lock_timeout: 'float' = 5.0, concurrent: 'bool' = False, opus_time_policy: 'OpusTimePolicy' = 'strict', extension_case: "Literal['upper', 'lower']" = 'upper') -> None
```

```text
MsgWriter.create(self, path: 'str | PathLike[str]', *, header_format: 'HeaderFormat' = 'ftsc') -> 'None'
```

```text
MsgWriter.open(self, path: 'str | PathLike[str]', options: 'WriterOptions | None' = None, *, header_format: 'HeaderFormat' = 'ftsc', opus_time_policy: 'OpusTimePolicy | None' = None) -> 'MsgSession'
```

```text
MsgWriter.recovery_session(self, path: 'str | PathLike[str]', *, recovery_root: 'str | PathLike[str]', options: 'WriterOptions | None' = None, header_format: 'HeaderFormat' = 'ftsc', opus_time_policy: 'OpusTimePolicy | None' = None) -> 'Iterator[MsgRecoverableSession]'
```
