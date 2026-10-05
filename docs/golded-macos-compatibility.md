# GoldED macOS offline interoperability — 2026-10-05

Bounded offline probes passed for FTSC MSG, JAM, Squish and classic Hudson with
the corrected executable below. The original Squish failure and subsequent
retest are preserved in this report. These results do not enable concurrent mode or establish
complete compatibility across builds, configurations or platforms.

## Executable and environment

- Executable: `golded-linux-macos/golded3/gedmac`, Mach-O arm64.
- SHA-256: `914262cfe885bcfe5a407662939f12c4622aff89b8208bd23a936a450ad9eec0`.
- Displayed version: `GoldED/MAC 3.0.1-os1`; compiled `Oct 5 2026 14:39:27`.
- Source checkout HEAD: `dd8e90b92550fa4165303aa960abfe97c553e03a`.
  The checkout has local build/instruction changes and the Squish loader fix;
  this is not a clean-tag build.
- Platform: macOS 27.0, build 26A428, arm64; Python 3.14.6.
- All five installed Python distributions: 1.2.0.
- Installed compiler: Homebrew GCC 16.2.0 (`g++-16`). The current build recipes
  select it with `-g -Wall -funsigned-char -Wno-sign-compare -fno-exceptions`
  and `-O2 -std=gnu++98 -fpermissive -Wno-deprecated -Wno-write-strings`.
  The exact invocation that produced the supplied executable was not captured;
  compiler and flags are recipe evidence, not a verified binary provenance claim.
  The executable was not rebuilt or modified by these probes.

The harness creates temporary synthetic bases, runtime support files and an
explicit `.cfg` configuration. It passes a minimal child environment and runs
GoldED in the temporary directory. Operator config and archives are not opened.
This build contains a debug write to `/tmp/golded-loadmsg.log`; its own diagnostic
side effect is not redirected by the harness.

Configuration: local area, `MSGLISTFIRST NO`, `SQUISHSCAN API`, internal editor,
header/editor/save menus disabled, explicit Hudson board. Stored text uses
CP850. The terminal local charset is LATIN-1 with `850_ISO.CHS` and `ISO_850.CHS`
conversion tables. A `.cfg` input keeps GoldED's compiled `.gem` cache separate.

## Results

| Format | Python-created base edited by GoldED and Python | GoldED-created base read/edited/deleted by Python | Concurrent mode |
| --- | --- | --- | --- |
| FTSC MSG | Passed | Passed | Disabled |
| JAM | Passed | Passed | Disabled |
| Classic Hudson, board 1 | Passed | Passed | Disabled |
| Classic Hudson, board 200 | Passed | Not separately run | Disabled |
| Squish | Passed after loader fix | Passed after loader fix | Disabled |

The interoperability sequence checks:

1. Python creates the base, appends parent/unrelated/reply records, grows and
   shrinks parent text, and deletes a fourth record.
2. GoldED opens the resulting base and displays parent and recipient names, body
   markers and actual Danish `æøå ÆØÅ` terminal glyphs. Reply navigation skips
   the unrelated record and returns to the parent.
3. GoldED changes parent text and appends a new message. It exits normally.
4. Python's strict reader validates all live records, the changed body, Danish
   text and both reply links. A separate session reads the GoldED-created record
   and patches its subject/body while preserving controls, date and attributes.
5. Lastread files are compared by relative path and bytes before/after the Python
   patch, including missing-file detection. One populated existing file was
   compared for each successful format. A pre-GoldED revision is rejected after GoldED edits
   that target; the unrelated message's revision remains unchanged.
6. A new GoldED process reads the Python-edited record and deletes it. Python's
   strict reader verifies the remaining three records and absence of that ID.

A separate creation sequence starts without format files. GoldED writes its
first message; Python reads the base, updates that message and deletes it. This
passed for MSG, JAM, Squish and Hudson board 1.

## Original Squish failure — corrected and retested

The short reply fixture contains two control fields and a short body. Its
independently unpacked frame has 53 control bytes and 19 text bytes.
The original `goldlib/gmb3/gmosqsh3.cpp:119–124` allocated `1 + ctlsize + textsize` bytes,
placed the control read at `buffer + ctlsize`, then read `ctlsize` bytes there.
For this fixture, it allocated 73 bytes and wrote through offset 105: a 33-byte
overrun before control conversion. GoldED's allocation checker detects it at
`golded3/gelmsg.cpp:98` and exits 34:

```text
Pointer error exit at [gelmsg.cpp,98].
An allocated memory region was overrun.
Ptr (...,73) at [gmosqsh3.cpp,119].
```

The second probe lets GoldED create Squish files and save its own short first
message. It also triggers the allocation checker, without Python writing any
Squish record. Those failures occurred with executable SHA-256
`50d6c0cbf6a427be93a08749912fc51fe2c80f05f136ac683647d7a5209325c0`.

The supplied replacement executable uses `1 + 2 * ctlsize + textsize` with an
unsigned-overflow guard. The loader also replaces an unaligned control-prefix
integer read with a string comparison. Both Squish scenarios were rerun unchanged
against the replacement and passed, including short controls/body, reply navigation,
CP850, lastread preservation, revision conflict, updates and deletion. MSG, JAM and
Hudson board 1 were also rerun in both scenarios against that same executable;
Hudson board 200 passed the interoperability scenario. The GoldED correction and
rebuild were supplied separately, not performed by the documentation probe.

## Reproduce

Install the released wheels first, then run from this documentation repository:

```sh
uv run python scripts/check_golded_compatibility.py --binary /path/to/golded3/gedmac
uv run python scripts/check_golded_compatibility.py --binary /path/to/golded3/gedmac --format hudson --board 200 --scenario interoperability
```

The default runs both scenarios for all formats and exits nonzero on any failure.
`--format` may be repeated; `--scenario create` isolates GoldED-created bases.
The opt-in harness uses a POSIX pseudo-terminal and requires the executable's
public `cfgs/config` and `cfgs/charset` support files beside it. It is not part
of ordinary pytest or GitHub CI and does not silently skip a missing executable.
Python optimization is refused because it would remove validation assertions.

Terminal actions wait for output states with monotonic deadlines.
Ashley/Claude reviewed the probe for false positives;
reply ordering, lastread presence, process isolation and stale-revision controls
were strengthened in response.

## Remaining boundary

The full acceptance matrix is still incomplete. These probes do not cover all
attribute bits, timestamp/address limits, unknown binary subfields, every reply
list, all boards, empty-area refresh after deletion, or every helper/scan index.
Longer/shorter serialization is exercised in Python; GoldED only reads the final
shorter version in that sequence. No Linux or Windows GoldED runtime was tested.

No concurrent-write, concurrent-read, caching or live refresh guarantee has been
established. The reread above occurs in a newly started GoldED process. Concurrent
mode remains disabled on every platform; matching record locks alone are not a
safe-coexistence result. No process-kill or power-loss guarantee is added.
