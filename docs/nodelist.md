# golded-ftn-nodelist

Version 0.1.0 candidate. Python 3.12–3.14 on Linux and macOS.

## Installation

```sh
python -m pip install golded-ftn-nodelist==0.1.0
```

The command becomes available after publication. For the unpublished suite, install
all reviewed wheels from the candidate wheelhouse; no sibling checkouts are needed.

## First working example

```python
from golded_ftn_nodelist import ListDialect, ParseOptions, parse_list, find_by_name

source = b"Zone,2,Example,Nowhere,Coordinator,-Unpublished-,300,CM\r\nHost,999,Example,Nowhere,Alice,-Unpublished-,300,CM\r\n,1,Example,Nowhere,Bob,-Unpublished-,300,CM\r\n"
document = parse_list(
    source,
    options=ParseOptions(
        dialect=ListDialect.STANDARD,
        domain="test.invalid",
        default_zone=2,
    ),
)
assert len(find_by_name(document, "Bob")) == 1
```

## Formats and configuration

Select an explicit `ListDialect`: STANDARD, BOSS, POSS, POINT, DK_FAKENET or
UBOSS. Supply domain and default zone; do not infer a production network from a
filename. `ParseOptions` selects ASCII/CP850, CRC policy, explicit fakenet mappings
and optional boss entries. CRC uses CRC-16/XMODEM; it detects accidental damage,
not authenticity. REQUIRE_VALID rejects absent or invalid CRCs.

`export_list` returns bytes in SEG, PVT, NAM, NET, DUP, TXT or VR7_TEXT format.
VR7_TEXT is text, not a binary V7 index. `DkpcExportOptions` controls encoding,
headers, boss inheritance, pointnets and terminators. Preserve the input bytes
separately if provenance matters; an export is not a byte-identical backup.

## Errors and privacy

Use `ListParseError`, `ListExportError` and `MappingResolutionError` codes and
structured diagnostics. Inspect document diagnostics before using recovered entries.
Unknown or ambiguous boss mappings require explicit input; do not guess routes.
Names and phone fields are personal data. Errors and repr suppress their contents;
application logging must preserve that boundary. No network fetching or filesystem
write occurs in the parser/exporter itself.

## Public API reference

Signatures below are extracted from the installed candidate wheel. Constructors
are keyword-only where shown. Default enum repr values describe defaults, not
Python source to paste.

### `BossContact`

```text
BossContact(*, phone: 'str', speed: 'int', flags: 'tuple[str, ...]' = (), system: 'str | None' = None, location: 'str | None' = None, sysop: 'str | None' = None) -> None
```


### `BossGroup`

```text
BossGroup(*, boss: 'NodeIdentity', fakenet: 'int | None' = None, contact: 'BossContact | None' = None, contact_conflicted: 'bool' = False, points: 'tuple[ListEntry, ...]' = (), source_lines: 'tuple[int, ...]' = ()) -> None
```


### `CrcPolicy`

```text
CrcPolicy(*values)
```

Enum where members are also (and must be) strings

### `CrcResult`

```text
CrcResult(*, status: 'CrcStatus', declared: 'int | None', computed: 'int | None') -> None
```


### `CrcStatus`

```text
CrcStatus(*values)
```

Enum where members are also (and must be) strings

### `DiagnosticCode`

```text
DiagnosticCode(*values)
```

Enum where members are also (and must be) strings

### `DkpcExportOptions`

```text
DkpcExportOptions(*, all_pointnets: 'bool' = False, inherit_boss_contact: 'bool' = False, write_crc: 'bool' = True, insert_h0: 'bool' = False, write_ctrl_z: 'bool' = True, include_zone: 'bool' = True, encoding: "Literal['ascii', 'cp850']" = 'ascii') -> None
```


### `EntryKind`

```text
EntryKind(*values)
```

Enum where members are also (and must be) strings

### `ExportFormat`

```text
ExportFormat(*values)
```

Enum where members are also (and must be) strings

### `ExportHeader`

```text
ExportHeader(*, edition_date: 'date', day_of_year: 'int', network_label: 'str', preamble: 'tuple[str, ...]' = (), postamble: 'tuple[str, ...]' = ()) -> None
```


### `FakenetMapping`

```text
FakenetMapping(*, domain: 'str', zone: 'int', fakenet: 'int', boss: 'NodeIdentity', source_lines: 'tuple[int, ...]' = ()) -> None
```


### `ListDiagnostic`

```text
ListDiagnostic(*, code: 'DiagnosticCode', line_number: 'int | None', offset: 'int | None', related_lines: 'tuple[int, ...]' = ()) -> None
```


### `ListDialect`

```text
ListDialect(*values)
```

Enum where members are also (and must be) strings

### `ListDocument`

```text
ListDocument(*, dialect: 'ListDialect', domain: 'str', entries: 'tuple[ListEntry, ...]', boss_groups: 'tuple[BossGroup, ...]', mappings: 'tuple[FakenetMapping, ...]', diagnostics: 'tuple[ListDiagnostic, ...]', raw: 'bytes', lines: 'tuple[RawLine, ...]', crc: 'CrcResult', day_of_year: 'int | None', boss_entries: 'tuple[ListEntry, ...]' = ()) -> None
```


### `ListEntry`

```text
ListEntry(*, identity: 'NodeIdentity', kind: 'EntryKind', status: 'NodeStatus', system: 'str', location: 'str', sysop: 'str', phone: 'str', speed: 'int', flags: 'tuple[str, ...]', boss: 'NodeIdentity | None', fakenet: 'int | None', region: 'int | None' = None, hub: 'int | None' = None, service: 'bool', changed: 'bool', user_comment: 'str | None' = None, raw_line: 'RawLine', raw_fields: 'tuple[bytes, ...]') -> None
```


### `ListExportError`

```text
ListExportError(code: 'str', line_number: 'int | None' = None, offset: 'int | None' = None) -> 'None'
```

### `ListParseError`

```text
ListParseError(code: 'str', line_number: 'int | None' = None, offset: 'int | None' = None) -> 'None'
```

### `MappingResolutionError`

```text
MappingResolutionError(code: 'str', line_number: 'int | None' = None, offset: 'int | None' = None) -> 'None'
```

### `NodeIdentity`

```text
NodeIdentity(*, domain: 'str', zone: 'int', net: 'int', node: 'int', point: 'int' = 0) -> None
```


### `NodeStatus`

```text
NodeStatus(*values)
```

Enum where members are also (and must be) strings

### `NodelistError`

```text
NodelistError(code: 'str', line_number: 'int | None' = None, offset: 'int | None' = None) -> 'None'
```

### `ParseOptions`

```text
ParseOptions(*, dialect: 'ListDialect', domain: 'str', default_zone: 'int | None' = None, encoding: "Literal['ascii', 'cp850']" = 'ascii', crc_policy: 'CrcPolicy' = <CrcPolicy.VERIFY_IF_PRESENT: 'verify_if_present'>, mappings: 'tuple[FakenetMapping, ...]' = (), boss_entries: 'tuple[ListEntry, ...]' = ()) -> None
```


### `RawLine`

```text
RawLine(*, line_number: 'int', offset: 'int', content: 'bytes', terminator: 'bytes') -> None
```


### `compute_nodelist_crc`

```text
compute_nodelist_crc(data: 'bytes') -> 'int'
```

Compute CRC-16/XMODEM (poly 0x1021, init 0x0000) matching dkpc.c updCrc16.

### `convert_fakenet`

```text
convert_fakenet(document: 'ListDocument', address: 'NodeIdentity') -> 'NodeIdentity'
```

Convert a fakenet node address (point == 0, node > 0) to its canonical point identity.

### `export_list`

```text
export_list(document: 'ListDocument', *, format: 'ExportFormat', header: 'ExportHeader', options: 'DkpcExportOptions' = DkpcExportOptions(all_pointnets=False, inherit_boss_contact=False, write_crc=True, insert_h0=False, write_ctrl_z=True, include_zone=True, encoding='ascii'), boss: 'NodeIdentity | None' = None) -> 'bytes'
```

Export a parsed ListDocument into one of the seven deterministic DKPC formats.

### `find_by_address`

```text
find_by_address(document: 'ListDocument', address: 'NodeIdentity') -> 'tuple[ListEntry, ...]'
```

Find all entries in document whose canonical 5D identity matches address.

### `find_by_name`

```text
find_by_name(document: 'ListDocument', query: 'str') -> 'tuple[ListEntry, ...]'
```

Find all entries in document matching query after FTN name normalization.

### `normalize_identity`

```text
normalize_identity(address: 'FtnAddress', *, domain: 'str') -> 'NodeIdentity'
```

Convert an FtnAddress into a canonical 5D NodeIdentity.

### `parse_list`

```text
parse_list(data: 'bytes', *, options: 'ParseOptions') -> 'ListDocument'
```

Parse an FTN nodelist or pointlist into an immutable ListDocument.
