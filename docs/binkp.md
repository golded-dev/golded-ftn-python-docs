# golded-ftn-binkp

Version 0.1.0 candidate. Python 3.12–3.14 on Linux and macOS.

## Installation

```sh
python -m pip install golded-ftn-binkp==0.1.0
```

The command becomes available after publication. For the unpublished suite, install
all reviewed wheels from the candidate wheelhouse; no sibling checkouts are needed.

## First working example

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from golded_ftn import FtnAddress
from golded_ftn_binkp import BsoSpool, DomainOutboundRoot

with TemporaryDirectory() as directory:
    spool = BsoSpool(
        (
            DomainOutboundRoot(
                domain="test.invalid",
                default_zone=2,
                root_path=str(Path(directory) / "outbound"),
            ),
        )
    )
    peer = FtnAddress(zone=2, net=999, node=2, domain="test.invalid")
    with spool.lock_address(peer, timeout=1.0) as lock:
        assert spool.list_ready(peer, lock=lock) == ()
```

## BSO publication and transport

`DomainOutboundRoot` scopes each domain and default zone. `BsoSpool` owns BSO zone
and point layout, `.bsy`/`.csy` address locks, direct packets and flow references.
Use the returned address lock for list/publish/acknowledge operations. Lock all
AKAs in canonical order; a busy address is retryable, not permission to bypass locks.
Publication is idempotent by job identity; acknowledge only after durable delivery.
Flow actions can remove/truncate payloads, so preserve their ownership boundary.

`BinkpConfig` supplies local AKAs, links and private temporary, secure inbound,
unauthenticated quarantine and receipt directories. `BinkpLink.password` is a
secret configuration field. Keep it in a permission-restricted file or an in-memory
configuration supplied by a secret store. Never put it in CLI arguments or logs.
`BinkpClient` and `BinkpServer` are asynchronous; await their methods in your event loop.
The tosser CLI wraps these with loopback-only host checks.

## Authentication, restart and limits

Supports binkp 1.0/1.1, CRAM-MD5 authentication, receiver-generated filenames,
partial staging, resume and durable `InboundReceipt` before M_GOT. Plaintext
password fallback requires explicit permission. Authentication does not encrypt
message contents. TLS and CRYPT are not implemented. This package is not an
Internet-facing deployment policy or a packet semantic validator.

Keep partial files and receipts through restart; reconcile acknowledgements with
your durable journal rather than blindly resending. Catch `BinkpError` and `BsoError`
subclasses by code. A conflict or exhausted name space needs operator resolution;
retrying with a new job identity can duplicate delivery.

## Public API reference

Signatures below are extracted from the installed candidate wheel. Constructors
are keyword-only where shown. Default enum repr values describe defaults, not
Python source to paste.

### `AddressLock`

```text
AddressLock(address: 'FtnAddress', bsy_path: 'str', csy_path: 'str') -> 'None'
```

Holds ``.bsy`` (and optional ``.csy``) for one address.

```text
AddressLock.release(self) -> 'None'
```

### `BinkpClient`

```text
BinkpClient(*, spool: 'BsoSpool', config: 'BinkpConfig') -> 'None'
```

```text
BinkpClient.connect(self, host: 'str', port: 'int', *, link: 'BinkpLink') -> 'BinkpSessionResult'
```

```text
BinkpClient.run_streams(self, reader: 'asyncio.StreamReader', writer: 'asyncio.StreamWriter', *, link: 'BinkpLink') -> 'BinkpSessionResult'
```

### `BinkpCommand`

```text
BinkpCommand(*values)
```

Enum where members are also (and must be) ints

### `BinkpConfig`

```text
BinkpConfig(*, local_akas: 'tuple[FtnAddress, ...]', links: 'tuple[BinkpLink, ...]', inbound_tmp: 'str', secure_inbound: 'str', unauthenticated_quarantine: 'str', inbound_receipts: 'str', allow_unauthenticated: 'bool' = False, system_name: 'str' = 'GoldED FTN', sysop: 'str' = 'Sysop', location: 'str' = 'Unknown', mailer_id: 'str' = 'golded-ftn-binkp/0.1.0') -> None
```


### `BinkpError`

```text
BinkpError(code: 'str') -> 'None'
```

### `BinkpLink`

```text
BinkpLink(*, akas: 'tuple[FtnAddress, ...]', password: 'str', allow_plaintext: 'bool' = False) -> None
```


### `BinkpServer`

```text
BinkpServer(*, spool: 'BsoSpool', config: 'BinkpConfig') -> 'None'
```

```text
BinkpServer.handle_connection(self, reader: 'asyncio.StreamReader', writer: 'asyncio.StreamWriter') -> 'BinkpSessionResult'
```

```text
BinkpServer.serve(self, host: 'str', port: 'int') -> 'asyncio.Server'
```

### `BinkpSessionResult`

```text
BinkpSessionResult(*, authenticated: 'bool', peer_akas: 'tuple[FtnAddress, ...]', inbound_receipts: 'tuple[InboundReceipt, ...]', outbound_got: 'tuple[PublishedSpoolItem, ...]', busy: 'bool' = False) -> None
```


### `BsoAddressBusyError`

```text
BsoAddressBusyError(code: 'str') -> 'None'
```

### `BsoConflictError`

```text
BsoConflictError(code: 'str') -> 'None'
```

### `BsoError`

```text
BsoError(code: 'str') -> 'None'
```

### `BsoExhaustedError`

```text
BsoExhaustedError(code: 'str') -> 'None'
```

### `BsoFlavor`

```text
BsoFlavor(*values)
```

Enum where members are also (and must be) strings

### `BsoSpool`

```text
BsoSpool(roots: 'tuple[DomainOutboundRoot, ...]') -> 'None'
```

```text
BsoSpool.layout(self, address: 'FtnAddress') -> 'tuple[DomainOutboundRoot, str, str]'
```

```text
BsoSpool.lock_address(self, address: 'FtnAddress', *, csy: 'bool' = False, timeout: 'float' = 5.0) -> 'AddressLock'
```

```text
BsoSpool.lock_addresses(self, addresses: 'tuple[FtnAddress, ...]', *, csy: 'bool' = False, timeout: 'float' = 5.0) -> 'AbstractContextManager[tuple[AddressLock, ...]]'
```

```text
BsoSpool.allocate_arcmail_name(self, origin: 'FtnAddress', destination: 'FtnAddress', *, weekday: 'int', lock: 'AddressLock') -> 'str'
```

```text
BsoSpool.publish(self, job: 'OutboundPublishJob', *, lock: 'AddressLock') -> 'PublishedSpoolItem'
```

```text
BsoSpool.list_ready(self, address: 'FtnAddress', *, lock: 'AddressLock') -> 'tuple[PublishedSpoolItem, ...]'
```

```text
BsoSpool.acknowledge_sent(self, item: 'PublishedSpoolItem', *, lock: 'AddressLock') -> 'None'
```

### `BsoUsageError`

```text
BsoUsageError(code: 'str') -> 'None'
```

### `DomainOutboundRoot`

```text
DomainOutboundRoot(*, domain: 'str', default_zone: 'int', root_path: 'str', directory_mode: 'int' = 448, file_mode: 'int' = 384) -> None
```


### `FlowAction`

```text
FlowAction(*values)
```

Enum where members are also (and must be) strings

### `InboundReceipt`

```text
InboundReceipt(*, receipt_id: 'UUID', link_address: 'FtnAddress', domain: 'str', authenticated: 'bool', logical_filename: 'str', stored_filename: 'str', size_bytes: 'int', mtime_epoch: 'int', sha256: 'str', received_at_utc: 'str') -> None
```


### `OutboundPublishJob`

```text
OutboundPublishJob(*, job_id: 'UUID', destination: 'FtnAddress', flavor: 'BsoFlavor', payload_filename: 'str', payload_bytes: 'bytes', flow_action: 'FlowAction' = <FlowAction.DELETE: 'delete'>, is_direct_packet: 'bool' = False) -> None
```


### `PublishedSpoolItem`

```text
PublishedSpoolItem(*, job_id: 'UUID | None', destination: 'FtnAddress', flavor: 'BsoFlavor', flow_file: 'str | None' = None, payload_path: 'str', flow_action: 'FlowAction', size_bytes: 'int', mtime_epoch: 'int', sha256: 'str') -> None
```
