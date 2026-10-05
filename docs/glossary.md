# FTN terminology and jargon

A vocabulary for the library guide, core API and four format references. Terms here
explain the data and the tools; they do not imply that these packages implement a
BBS, tosser or complete message network.

## Networks, areas and addresses

| Term | Meaning here |
| --- | --- |
| FTN | FidoNet Technology Network: the family of networks using FidoNet-style addressing and message exchange conventions. FidoNet is one FTN network. |
| BBS | Bulletin Board System: software that gives users access to messages and other services. These libraries supply message-base access, not a BBS. |
| Message base / area | Stored messages. An area is a logical collection; depending on the format it occupies a directory, a basename with several files, or one board inside a shared Hudson base. |
| Netmail | Addressed mail to a particular FTN destination. A format may store netmail and echomail in the same kind of base; routing policy belongs to the caller. |
| Echomail | Messages exchanged for a named discussion area across participating systems. |
| Board | Hudson’s numbered partition within a shared base. Boards are 1–200; `BOARD7` is this reader’s synthetic identifier, not the configured area name. |
| FTN address | `zone:net/node.point@domain`. The point and domain may be absent. `2:236/77.1` identifies point 1 of node 77 in net 236, zone 2. |
| Zone / net / node / point | Address components. A point is a system associated with a node. Zero and absent metadata are distinct values; formats impose their own ranges. |
| Domain | An optional network qualifier, such as `fidonet`. Binary formats do not all represent it. |
| FTSC | FidoNet Technical Standards Committee. “FTSC MSG” here identifies the classic MSG header layout, distinguished from the Opus variant. |
| Opus | A BBS implementation with its own interpretation of some MSG header words, including packed written and arrival dates. Select the reader layout explicitly. |

## Message text and control lines

| Term | Meaning here |
| --- | --- |
| Kludge / control line | Machine-readable message metadata. A kludge typically begins with SOH (`\x01`); readers expose supported controls through `control_lines`. Unknown controls may still matter to other software. |
| SOH | Start of Heading, byte `0x01`. Used to mark or separate control metadata. |
| NUL | The zero byte, `0x00`. Some fields and bodies use it as a terminator or padding. It is not an empty string. |
| MSGID | External message identifier carried in control metadata. It is separate from a filename number, JAM number, Squish UID or Hudson number. Writers do not generate it automatically. |
| REPLY / REPLYID | External identifier of a replied-to message. Distinct from binary numeric reply links. JAM has a dedicated reply-ID subfield. |
| INTL | Control giving destination and origin zone:net/node addresses. Point numbers can be supplied separately. |
| FMPT / TOPT | From-point / to-point controls. They supplement the sender and destination addresses. |
| CHRS / CHARSET | Encoding declarations. The charset token names an encoding; CHRS can also carry a level. Conflicting declarations can make serialization fail. |
| CP850 / IBMPC | CP850 is the default legacy encoding in these libraries. `IBMPC` is one FTN declaration alias resolved to CP850 by the core. It does not mean arbitrary PC text is always CP850. |
| TZUTC | Timezone-offset metadata. Preserving this control does not mean every decoded datetime is timezone-aware. Check the format’s date mapping. |
| PID / FLAGS | Program identifier and textual flag metadata. Their representation depends on the format; they are not interchangeable with raw binary attribute bits. |
| SEEN-BY | Routing history listing participating nodes. These packages retain supplied strings without expanding, deduplicating or calculating routing. |
| PATH | Routing-path metadata. The core parser distinguishes plain `PATH:` lines from SOH controls; format readers may handle additional forms. |
| Tearline | A line beginning `---`, traditionally carrying software or version information. |
| Origin line | A recognized ` * Origin:` line, often with a description and an address in parentheses. It is not permission to invent missing header addresses. |
| Mojibake | Text produced by decoding bytes with the wrong encoding. Optional repair is a heuristic and never runs automatically. Retain the original decoded text and source bytes when they matter. |

## Records, identities and metadata

| Term | Meaning here |
| --- | --- |
| Header | Structured fields describing a message or base. It may contain names, attributes, dates, addresses, offsets and reply links. |
| Index | Records selecting active messages and locating their headers. JAM, Squish and Hudson use indexes as authority; scanning every physical header would return obsolete records. |
| Offset / slot | A byte position / a fixed record position. Hudson scan indexes store physical header slots, not message numbers. |
| Subfield | JAM’s typed variable-length header metadata. A subfield has IDs, a length and bytes. Unknown subfields can survive editing without appearing in the core parsed model. |
| Frame | A Squish allocation containing a frame header, message header, controls and text. Content edits can move a message to a new frame while preserving its UID. |
| UID | Squish’s persistent unique message number within a base. It is not the current relative index position or an external MSGID. |
| Free list | Squish’s chain of unused frames. Deleted or superseded frames can join it; this Python writer does not recycle or pack them. |
| Pascal string / text block | A length-prefixed field. Hudson text blocks are 256 bytes: one length byte followed by up to 255 payload bytes. Join payloads before decoding. |
| Attribute bits | Format-specific binary flags. `attributes_raw` retains their integer value; bit meanings differ across formats. |
| Reply links | Format-specific numeric relationships. Squish has nine reply slots, while the shared parsed model exposes only part of that structure. Deletion does not rewrite other messages’ links. |
| Lastread | Per-user read-position information, stored in format-specific auxiliary files. Writers preserve existing lastread data. |
| CRC | A cyclic redundancy check used by formats such as JAM for indexed lookups and metadata. It is not the SHA-256 revision digest. |
| Provenance | Where a parsed value came from: format, path, record ID and physical offset when known. It is not a revision or authority to edit. |
| Synthetic ID | The core’s `hash:sha256:...` ID derived from decoded message fields. It is separate from raw record identity and must not be serialized as an external MSGID. |

## Reading, editing and failure boundaries

| Term | Meaning here |
| --- | --- |
| Strict reading | Reject malformed records and undecodable bytes rather than silently repairing them. Some readers validate the entire active base before returning messages; MSG can yield earlier files before a later failure. |
| Archive mode | Explicit, reported recovery while reading imperfect data. It requires an issue callback. It does not enable editing a damaged base. |
| Recovered / skipped / stopped | Issue actions: a deviation was accepted / a record was excluded / traversal is incomplete. Several issues may describe one record. |
| Stable copy | Files that do not change during a read. Copying separate files while another process writes is not automatically a consistent snapshot. |
| Offline editing | GoldED and other uncoordinated access remain closed while editing. All current writers reject `concurrent=True`. |
| Record lock | A lock over a file-byte range. It coordinates cooperating processes; a matching write lock alone does not prove that GoldED reading, caching and refresh are safe. |
| Session | Context-managed access to one base, plus an explicit board for Hudson. Each operation takes and releases the format lock. |
| Revision token | Identity, physical placement and SHA-256 over raw message bytes. Used to check that the target still matches a previous consistent read. Other messages’ changes do not automatically invalidate it. |
| Patch / UNSET / None | A patch changes selected fields. `UNSET` leaves a field untouched; `None` requests clearing when the format can represent that. Empty strings and zero are separate values. |
| Conflict | The target is missing or changed, or the supplied identity/revision does not match. Read again and reconcile rather than blindly retrying a stale patch. |
| Commit unit | One successful writer operation. Earlier operations survive a later failure; a session is not one transaction around all its operations. |
| Rollback | Restoration of watched bytes and file sizes after a handled I/O failure, under the lock. Failed rollback poisons the session. There is no process-kill or power-loss transaction guarantee. |
| Poisoned session | A session made unusable by failed rollback. Reopening is not proof that the underlying base is healthy. |

## Tools outside these libraries

| Term | Meaning here |
| --- | --- |
| GoldED | Message editor used as the main format implementation reference. Current-build interoperability and live refresh tests are deferred. |
| Tosser | Software that imports, exports and distributes FTN messages between packets and message areas. These writers expose storage operations, not tossing policy. |
| Packet | A transport container for FTN messages. Packet handling is outside these packages. |
| Packing | Reclaiming obsolete records or allocations and potentially changing physical layout. These writers leave obsolete blocks in place rather than compacting bases. |
| GoldBase | A different message-base layout using `.DAT` files; the Hudson package supports classic `.BBS` files instead. |

## Read next

- [Library guide](guide.html): installation and practical examples.
- [Core API](core-api.html): exact value, helper and exception contracts.
- [Writer contract](writers.html): shared operation and revision rules.
- Format references: [MSG / Opus](msg.html), [JAM](jam.html),
  [Squish](squish.html) and [Hudson](hudson.html).
