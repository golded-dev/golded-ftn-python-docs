# SQLite format reference

Store FTN netmail and echomail in a SQLite database with
`golded_ftn_sqlite`. The package uses the shared `golded_ftn` message model and
requires Python 3.12 or newer. Candidate 0.1.0 is local and unpublished.

Use the [core API reference](core-api.html) for shared message types and
[Editing message bases](writers.html) for revision-token updates.

## Public API

The package exports `AreaDefinition`, `AreaKind`, `SqliteDatabase`,
`SqliteReader`, `SqliteSession` and `SqliteWriter`.

```text
SqliteDatabase.open(path: str | PathLike[str]) -> SqliteDatabase
SqliteDatabase.create(path: str | PathLike[str], *, area: AreaDefinition)
    -> SqliteDatabase
SqliteDatabase.add_area(area: AreaDefinition) -> None
SqliteDatabase.areas() -> tuple[AreaDefinition, ...]
SqliteReader(area_code: str | None = None)
SqliteReader.read(path: str | PathLike[str], options: ReaderOptions | None = None)
    -> Iterable[ParsedMessage]
SqliteWriter(area_code: str | None = None)
SqliteWriter.open(path: str | PathLike[str], options: WriterOptions | None = None)
    -> SqliteSession
SqliteSession.read(msgno: int) -> SessionMessage
SqliteSession.append(message: OutgoingMessage) -> WriteResult
SqliteSession.update(identity: MessageIdentity, patch: MessagePatch,
    expected_revision: RevisionToken) -> WriteResult
SqliteSession.delete(identity: MessageIdentity,
    expected_revision: RevisionToken) -> MessageIdentity
```

## Databases and areas

The format supports several areas in one database. The ordinary deployment is
one database file per area: it maps cleanly to GoldED configuration, keeps backup
and recovery local, and limits the blast radius when a disk has opinions.

Create the database with its first area. Add more areas explicitly when a single
database is useful. Area codes are case-insensitive. Message numbers are positive,
monotonic and local to an area; soft-deleted numbers are not reused.

Omit `area_code` from `SqliteReader` or `SqliteWriter` only when the database has
exactly one area. For several areas, select one by code.

## Create, write and read echomail

This example creates a temporary one-area database, stores one Unicode message
and reads it through the shared message model. No existing files are touched.

```python
from pathlib import Path
from tempfile import TemporaryDirectory

from golded_ftn import FtnAddress, OutgoingMessage
from golded_ftn_sqlite import (
    AreaDefinition,
    AreaKind,
    SqliteDatabase,
    SqliteReader,
    SqliteWriter,
)

with TemporaryDirectory() as directory:
    path = Path(directory) / "fido-general.sqlite3"
    SqliteDatabase.create(
        path,
        area=AreaDefinition(
            code="FIDO.GENERAL",
            name="FidoNet General",
            kind=AreaKind.ECHOMAIL,
            default_origin=FtnAddress(zone=2, net=230, node=0),
        ),
    )
    with SqliteWriter().open(path) as session:
        written = session.append(
            OutgoingMessage(
                from_name="Alice",
                to_name="All",
                subject="Hello",
                body_text="Stored transactionally. ÆØÅ.",
            )
        )
        assert session.read(written.identity.msgno).message.subject == "Hello"

    messages = tuple(SqliteReader().read(path))
    assert len(messages) == 1
    assert messages[0].area_code == "FIDO.GENERAL"
    assert messages[0].body_text == "Stored transactionally. ÆØÅ."
```

## Netmail and echomail data

Netmail requires origin and destination addresses. The origin may come from the
area's `default_origin`; the destination is always explicit. Both the Python API
and the database schema enforce the rule.

Messages store Unicode names, subject and body, timestamps, raw attributes,
external IDs, split FTN addresses, reply links and optional import provenance.
Ordered tables retain repeated and unknown control lines, `SEEN-BY`, `PATH` and
reply-list entries without flattening them into a JSON object.

Readers return a stable SQLite snapshot. Session reads fetch one requested
message. Deletes are soft deletes, so readers skip the message without making its
number available again.

## Updates and concurrency

Writer sessions provide `read`, `append`, `update` and `delete`. Updates and
deletes require the revision token returned by a session read or write. The token
covers the message and its ordered control, routing and reply-list rows, including
changes made directly by another SQLite client.

Writers use `BEGIN IMMEDIATE`, so allocation and mutations are serialized.
Readers keep SQLite snapshot semantics. A caller can tune lock waiting through
the shared `WriterOptions.lock_timeout` value.

## Schema and backup

Schema version 1 uses SQLite application ID `0x47465453` (`GFTS`), strict tables,
foreign keys and WAL journaling. Readers reject a different application ID or
schema version. The schema is a public format boundary; changing existing meaning
requires a migration and a new version.

Do not copy an open WAL database as a lone `.sqlite3` file. Use SQLite's backup
API, or close and checkpoint the database first. Copying only the main file can
omit committed pages still present in the WAL.

## Implementation references

- [Package README](https://github.com/golded-dev/golded-ftn-sqlite-python/blob/main/README.md)
- [Schema guide](https://github.com/golded-dev/golded-ftn-sqlite-python/blob/main/docs/schema.md)

Those GitHub targets become public only after the separate package repository is
committed and published. The format page does not establish that release state.
