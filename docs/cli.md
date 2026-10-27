# CLI guide

The command-line interface lets you work with message files from a terminal instead of writing a Python program. Its command is `ftnt`. Start with local message bases; add the network commands when you need to inspect packet files, look up systems or operate a configured node.

Tools 1.2.0 supports Linux/macOS and Python 3.12–3.14.

## Install and first check

```sh
python -m pip install 'golded-ftn-tools[network]==1.2.0'
ftnt --version
ftnt catalog
```

The network extra installs the published packet, nodelist, binkp and tosser
dependencies. Without it, base
commands continue to work and network commands report network_missing.

## Message bases

```sh
ftnt create ./demo --format jam
ftnt write ./demo --format jam < message.json
ftnt heads ./demo --format jam
ftnt read ./demo 1 --format jam --body
ftnt export ./demo --format jam
```

Use the command's `--help` for input schemas and flags. write accepts a JSON object with from_name, to_name, subject and body_text; --jsonl appends each message separately. A later
failure does not undo prior commits. A closed output pipe may hide a committed
receipt; replaying the input can duplicate messages. MSG requires explicit FTSC
or Opus format; Hudson requires a board. Keep bases offline for CLI mutations.

## Packets and lists

```sh
ftnt packet read mail.pkt
ftnt packet write --output mail.pkt < packet.json
ftnt nodelist parse NODELIST.XXX --domain test.invalid --default-zone 2
ftnt nodelist lookup NODELIST.XXX --domain test.invalid --address 2:999/1
```

These are commands, not fixture production addresses. Packet read validates framing
and semantic fields. Nodelist parsing is not route configuration. See the package
references for schemas, CRC policy and supported dialects.

## Node operations

```sh
ftnt node --config node.toml check
ftnt node --config node.toml recover
ftnt node --config node.toml toss
ftnt node --config node.toml scan
ftnt node --config node.toml status
ftnt node --config node.toml poll --help
ftnt node --config node.toml serve --help
```

Read [Tosser operations](tosser.html) before creating node.toml. Keep credentials
in protected configuration, never arguments. poll/serve accept loopback hosts only.
recover reconciles journal/base work; status exposes queues and HELD. An empty
transport spool does not prove successful import into a recipient mailbox.

## Output and errors

Operational errors print closed codes without paths, payloads, credentials or a
traceback, including --debug. Exit codes are documented by the command help;
archive recovery exits 7 when issues occur, broken stdout exits 141. Read stdout
as data and stderr as diagnostics. `--log-level` overrides TOML [logging].level;
OFF suppresses logs, not the journal. repair is an explicit text heuristic; readers
and exporters never repair silently. MCP retains only catalog/heads/read/export/
decode/repair and exposes no node or writer commands.
