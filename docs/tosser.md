# golded-ftn-tosser

A tosser sorts incoming FTN messages into local message bases and prepares outgoing messages for delivery. It brings together message storage, packet files, routing rules and file transfer. Use it when you want to operate a node, meaning a configured system that exchanges mail with other systems. To read an archive or try one local message, begin with the [library guide](guide.html) instead.

Version 1.0.0. Python 3.12–3.14 on Linux and macOS.

## Installation

```sh
python -m pip install golded-ftn-tosser==1.0.0
```

The package is published on PyPI. The command above installs the reviewed release;
no sibling checkout or private wheelhouse is needed.

## First working example

This first example only creates a local node with no peers, routes or message areas and checks its state. It does not send or receive mail. The later sections explain the configuration needed for delivery.

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from golded_ftn_tosser import TosserNode

with TemporaryDirectory() as directory:
    root = Path(directory)
    config: dict[str, object] = {
        "product_id": 0x00FE,  # Synthetic fixture only.
        "paths": {
            name: str(root / name)
            for name in ("state", "inbound", "outbound", "held", "receipts")
        },
        "domains": [{"name": "test.invalid", "default_zone": 2}],
        "akas": [{"address": "2:999/1@test.invalid"}],
        "links": [],
        "areas": [],
        "area_rights": [],
        "mailboxes": [],
        "routes": [],
    }
    node = TosserNode.from_mapping(config)
    assert node.check()["ok"] is True
    node.recover()
    assert node.status()["held_reasons"] == []
```

## Configuration and credentials

`TosserNode.from_path` loads strict TOML; unknown keys fail closed. The root table requires
`product_id`; optional `charset_fallback` defaults to CP850 and `lock_timeout` controls
lock acquisition. `[paths]` contains state, inbound, secure_inbound, outbound, held
and receipts. Domain, AKA, link, area, rights, mailbox and route tables define the
node. The no-link example above is a local journal smoke test, not a usable network.

Use `[[domains]]` name/default_zone, `[[akas]]` address, and `[[links]]` address,
session_password, areafix_password, host, port and optional allow_plaintext. Session
and AreaFix passwords have different purposes. Store them only in protected TOML
(mode 0600) or build an in-memory mapping from a secret store. Never pass credentials
in argv, examples, logs or issue reports. Fixtures use test.invalid, loopback peers
and product_id 0x00FE; none are production assignments or deployment defaults.

`[[areas]]` requires domain/tag/format/path/kind (echo or netmail). Hudson additionally
needs board 1–200 and the correct scan_dir. Squish needs an explicit IANA timezone
when converting naive times. `[[area_rights]]` controls import/export per domain, tag and
link. `[[mailboxes]]` maps a full destination address to domain/area_tag;
`[[routes]]` maps destination to via. No route is invented from a nodelist.

## Import, scan, routing and transport

Call `check`, then `recover` before resuming normal work. `toss` validates complete
packets and authenticated receipts before record import, routes netmail only to an
explicit mailbox or route, and fans out echomail only to permitted links. It preserves
canonical imported packet bytes for forwarding. ZIP import is bounded against
traversal, entry count, expansion and compression ratio; other archives are unsupported.
`scan` assigns stable MSGIDs, records local changes and publishes durable outbound
jobs. Direct read/write through format APIs does not perform this network policy.

`poll` delivers queued BSO work to a configured peer; `serve` receives binkp traffic.
CLI wrappers refuse non-loopback hosts. Delivery receipts precede spool acknowledgement.
The API exposes transport primitives; do not infer a hardened public service from a
loopback integration test. AreaFix uses a separate password and stored subscriptions;
RESCAN generations must not accidentally suppress requested replay as duplicates.

## Queues, HELD and restart

Unknown netmail routes remain in the queue with unknown_route; there is no open relay.
HELD records retain the original payload and a closed reason code. Inspect the reason,
correct configuration or source data and deliberately reprocess; a successful command
exit is not proof that every record reached a mailbox. `status` reports journal counts
and held_reasons without exposing message contents.

Recovery follows INTENT → READY → DONE and format PREPARED/APPLIED/settled state.
Call `recover` after restart, under the same state directory and base identity.
COMMITTED finalizes, UNCOMMITTED rolls back, UNKNOWN remains unresolved. Never treat
an uncertain commit as a safe resend or delete its recovery evidence. Preserve the
journal, recovery directories, receipts, HELD and outbound payloads together.

## Safety and concurrency

No TLS/CRYPT, fileecho, Type 2.2, public service hardening or live-network acceptance
is promised. Format writer defaults remain offline. `concurrent=True` is only for
the pinned Linux/macOS GoldED 3.1.0 profile described in the writer guide; it is not
a promise for every editor/build/filesystem. The journal and routing locks impose an
order; do not enter transport while holding a message-base mutation lock. Logging
levels are OFF/ERROR/WARNING/INFO/DEBUG; OFF does not turn off the durable journal.

## Public API reference

Signatures below are extracted from the installed release wheel. Constructors
are keyword-only where shown. Default enum repr values describe defaults, not
Python source to paste.

### `Component`

```text
Component(*values)
```


### `DiagnosticEvent`

```text
DiagnosticEvent(*, code: 'EventCode', component: 'Component', job_id: 'UUID | None' = None, transaction_id: 'UUID | None' = None, reason: 'ReasonCode | None' = None, state: 'State | None' = None, count: 'int | None' = None, retry_count: 'int | None' = None, retry_delay_seconds: 'int | None' = None) -> None
```

Finite diagnostic schema. Never add a field without privacy review.

```text
DiagnosticEvent.validate(self) -> 'None'
```

### `EventCode`

```text
EventCode(*values)
```


### `EventEmitter`

```text
EventEmitter(level: 'LogLevel' = <LogLevel.INFO: 'INFO'>) -> 'None'
```

An instance-level threshold layered under the application's log policy.

```text
EventEmitter.emit(self, event: 'DiagnosticEvent') -> 'None'
```

### `HeldError`

```text
HeldError(code: 'str') -> 'None'
```

### `Journal`

```text
Journal(state_dir: 'str | Path', *, lock_timeout: 'float' = 5.0, tracker: 'LockTracker | None' = None) -> 'None'
```

```text
Journal.write_txn(self) -> 'Iterator[sqlite3.Connection]'
```

```text
Journal.insert_intent(self, *, physical_base_key: 'str', operation: 'str') -> 'UUID'
```

```text
Journal.mark_ready(self, tx_id: 'UUID') -> 'None'
```

```text
Journal.mark_aborted(self, tx_id: 'UUID', *, error_code: 'str | None' = None) -> 'None'
```

```text
Journal.commit_done(self, tx_id: 'UUID', *, dupe_key: 'str | None' = None, fingerprint: 'str | None' = None, scan: 'tuple[str, str, int, int, str] | None' = None, inbound_receipt_id: 'UUID | None' = None, outbound: 'tuple[OutboundJob, ...]' = (), held_reason: 'str | None' = None, packet_ordinal: 'int | None' = None, netmail_queue: 'tuple[tuple[NodeIdentity, bytes, str], ...]' = ()) -> 'CommitState'
```

```text
Journal.resolve_commit_state(self, tx_id: 'UUID') -> 'CommitState'
```

```text
Journal.ensure_inbound_receipt(self, receipt_id: 'UUID', *, size_bytes: 'int', sha256: 'str') -> 'None'
```

```text
Journal.non_terminal_for_base(self, physical_base_key: 'str') -> 'tuple[TransactionRow, ...]'
```

```text
Journal.ready_count_for_base(self, physical_base_key: 'str') -> 'int'
```

```text
Journal.lookup_dupe(self, dupe_key: 'str') -> 'str | None'
```

```text
Journal.scan_recorded(self, physical_base_key: 'str', format: 'str', msgno: 'int', board: 'int') -> 'bool'
```

```text
Journal.assign_msgid(self, msgid: 'str') -> 'None'
```

```text
Journal.allocate_scan_msgid(self, *, physical_base_key: 'str', msgno: 'int', local: 'NodeIdentity') -> 'str'
```

```text
Journal.subscribers(self, domain: 'str', tag: 'str') -> 'tuple[NodeIdentity, ...]'
```

```text
Journal.seed_subscriptions(self, rights: 'tuple[AreaRights, ...]') -> 'None'
```

```text
Journal.record_held(self, *, reason_code: 'str', packet_ordinal: 'int | None' = None) -> 'UUID'
```

```text
Journal.record_identity(self, identity: 'NodeIdentity') -> 'None'
```

```text
Journal.all_outbound(self) -> 'tuple[OutboundJob, ...]'
```

```text
Journal.pending_outbound(self) -> 'tuple[OutboundJob, ...]'
```

```text
Journal.delivered_still_open(self, destination: 'NodeIdentity') -> 'tuple[OutboundJob, ...]'
```

```text
Journal.mark_job_publishing(self, job_id: 'UUID', payload_filename: 'str') -> 'None'
```

```text
Journal.mark_job_published(self, job_id: 'UUID') -> 'None'
```

```text
Journal.mark_job_delivered(self, job_id: 'UUID') -> 'None'
```

```text
Journal.published_job_id_for_payload(self, destination: 'NodeIdentity', payload_filename: 'str') -> 'UUID | None'
```

```text
Journal.counts(self) -> 'dict[str, int]'
```

```text
Journal.held_reasons(self) -> 'tuple[str, ...]'
```

```text
Journal.queued_unknown_routes(self) -> 'int'
```

```text
Journal.subscribe(self, *, domain: 'str', tag: 'str', link: 'NodeIdentity') -> 'None'
```

```text
Journal.unsubscribe(self, *, domain: 'str', tag: 'str', link: 'NodeIdentity') -> 'None'
```

```text
Journal.subscriptions_for(self, link: 'NodeIdentity') -> 'tuple[tuple[str, str], ...]'
```

### `LockOrderError`

```text
LockOrderError(code: 'str') -> 'None'
```

### `LockTracker`

```text
LockTracker(_base: 'int' = 0, _address: 'int' = 0, _sqlite_write: 'int' = 0, events: 'list[str]' = <factory>) -> None
```

Process-local tracker used by the tosser to enforce lock ordering.

```text
LockTracker.acquire_base(self) -> 'None'
```

```text
LockTracker.release_base(self) -> 'None'
```

```text
LockTracker.acquire_address(self) -> 'None'
```

```text
LockTracker.release_address(self) -> 'None'
```

```text
LockTracker.begin_sqlite_write(self) -> 'None'
```

```text
LockTracker.end_sqlite_write(self) -> 'None'
```

```text
LockTracker.base_lock(self) -> 'Iterator[None]'
```

```text
LockTracker.address_lock(self) -> 'Iterator[None]'
```

```text
LockTracker.sqlite_write(self) -> 'Iterator[None]'
```

### `LogConfigurationError`

### `LogLevel`

```text
LogLevel(*values)
```


### `NodeConfig`

```text
NodeConfig(*, product_id: 'int', charset_fallback: 'str', lock_timeout: 'float', logging_level: 'LogLevel', paths: 'NodePaths', domains: 'tuple[DomainConfig, ...]', akas: 'tuple[AkaConfig, ...]', links: 'tuple[LinkConfig, ...]', areas: 'tuple[AreaConfig, ...]', rights: 'tuple[AreaRights, ...]', mailboxes: 'tuple[MailboxRoute, ...]', routes: 'tuple[NetmailRoute, ...]', archive: 'ArchiveLimits', source: 'Mapping[str, object]') -> None
```


### `ReasonCode`

```text
ReasonCode(*values)
```


### `SafeEventError`

### `SafeFormatter`

```text
SafeFormatter(fmt=None, datefmt=None, style='%', validate=True, *, defaults=None)
```

Render only the typed event; ignore record text, extras and exceptions.

```text
SafeFormatter.format(self, record: 'logging.LogRecord') -> 'str'
```

### `SafeStreamHandler`

```text
SafeStreamHandler(stream: 'TextIO | None' = None) -> 'None'
```

An application-owned sink that never echoes failures or failed records.

```text
SafeStreamHandler.flush(self) -> 'None'
```

```text
SafeStreamHandler.handleError(self, record: 'logging.LogRecord') -> 'None'
```

### `State`

```text
State(*values)
```


### `TosserConfigError`

```text
TosserConfigError(code: 'str') -> 'None'
```

### `TosserError`

```text
TosserError(code: 'str') -> 'None'
```

### `TosserNode`

```text
TosserNode(config: 'NodeConfig', *, emitter: 'EventEmitter | None' = None, tracker: 'LockTracker | None' = None) -> 'None'
```

```text
TosserNode.from_path(cls, path: 'str | Path', *, cli_log_level: 'str | None' = None) -> 'TosserNode'
```

```text
TosserNode.from_mapping(cls, data: 'Mapping[str, object]', *, cli_log_level: 'str | None' = None) -> 'TosserNode'
```

```text
TosserNode.check(self) -> 'dict[str, object]'
```

```text
TosserNode.create_missing_bases(self) -> 'None'
```

```text
TosserNode.toss(self) -> 'dict[str, int]'
```

```text
TosserNode.scan(self) -> 'dict[str, int]'
```

```text
TosserNode.recover(self) -> 'dict[str, int]'
```

```text
TosserNode.status(self) -> 'dict[str, object]'
```

```text
TosserNode.poll(self, *, host: 'str' = '127.0.0.1', port: 'int', link_index: 'int' = 0) -> 'dict[str, object]'
```

```text
TosserNode.serve(self, *, host: 'str' = '127.0.0.1', port: 'int' = 0, wait: 'bool' = False, stop_event: 'threading.Event | None' = None, listening: 'threading.Event | None' = None) -> 'dict[str, object]'
```

### `load_node_config`

```text
load_node_config(path: 'str | Path', *, cli_log_level: 'str | None' = None) -> 'NodeConfig'
```

### `load_node_config_from_mapping`

```text
load_node_config_from_mapping(data: 'Mapping[str, object]', *, cli_log_level: 'str | None' = None) -> 'NodeConfig'
```

### `resolve_log_level`

```text
resolve_log_level(node_config: 'Mapping[str, object]' = {}, cli_override: 'str | None' = None) -> 'LogLevel'
```

Validate TOML-shaped input, then apply CLI > TOML > INFO precedence.
