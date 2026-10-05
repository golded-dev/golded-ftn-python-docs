# FTN Python 1.2.0 release — 2026-10-05

All five repositories were committed and pushed on `main`. Annotated `v1.2.0`
tags point to the reviewed source commits. Their GitHub releases are public and
contain one wheel, one sdist and `RELEASE-SHA256.txt` each.

| Package | Source commit | GitHub release | Tag CI |
| --- | --- | --- | --- |
| `golded-ftn` | `55e0032bb5e383f0c3ab6f8e36e8c3d298a3daf4` | [v1.2.0](https://github.com/golded-dev/golded-ftn-python/releases/tag/v1.2.0) | [passed](https://github.com/golded-dev/golded-ftn-python/actions/runs/37297992812) |
| `golded-ftn-msg` | `751f03f5e5c430f2706708e0225a8c5ac0369049` | [v1.2.0](https://github.com/golded-dev/golded-ftn-msg-python/releases/tag/v1.2.0) | [passed](https://github.com/golded-dev/golded-ftn-msg-python/actions/runs/37298054973) |
| `golded-ftn-jam` | `6b9d75787225ce6dea5794f34152b8b3d190327f` | [v1.2.0](https://github.com/golded-dev/golded-ftn-jam-python/releases/tag/v1.2.0) | [passed](https://github.com/golded-dev/golded-ftn-jam-python/actions/runs/37298056138) |
| `golded-ftn-squish` | `276c907d8826daa1c26011b0f794300e10000490` | [v1.2.0](https://github.com/golded-dev/golded-ftn-squish-python/releases/tag/v1.2.0) | [passed](https://github.com/golded-dev/golded-ftn-squish-python/actions/runs/37298058878) |
| `golded-ftn-hudson` | `110cef3e377eb4de4b071feceba49c9cb2067f5a` | [v1.2.0](https://github.com/golded-dev/golded-ftn-hudson-python/releases/tag/v1.2.0) | [passed](https://github.com/golded-dev/golded-ftn-hudson-python/actions/runs/37298060315) |

## Verification

The release commits and tags passed Linux Python 3.12–3.14 lint, format, strict
mypy, stubtest, pytest, builds and distribution checks. macOS and Windows Python
3.14 pytest jobs passed. CodeQL on all five release commits passed separately.

The first Windows runs exposed MSG temporary-file cleanup before descriptor
closure and platform-specific fault-step counts, plus a POSIX-only JAM test
helper. These were corrected and the remote suites passed before release.
MSG now has 113 local tests; the other local counts remain core 127, JAM 127,
Squish 159 and Hudson 156, with one case-sensitive-filesystem skip in each of
JAM, Squish and Hudson on the local macOS filesystem.

All 15 public release assets were downloaded again. The ten archive hashes match
both the downloaded manifests and the checked-in manifests. A fresh environment
installed the five downloaded wheels at 1.2.0, passed `uv pip check`, and executed
all four format CRUD examples from the shared HTML guide.

The shared guide's public commit pins were updated locally. Installing from
those pinned GitHub checkouts, without `--local`, passed 44 documentation tests
and strict mypy on 20 HTML examples. The documentation checkout was not committed,
pushed or deployed as part of the package releases.

## PyPI publication completed

All five Trusted Publishers were registered through the owner's PyPI account
and the five manual publishing workflows succeeded. Core was published and
installed from PyPI before the format workflows were dispatched. PyPI limits
pending publishers to three; consuming core and the first formats freed slots
for Squish and Hudson. All five publishers are now active.

The ten PyPI archives were downloaded and their SHA-256 values matched both
PyPI metadata and the reviewed GitHub release manifests. A fresh environment
installed all five packages at 1.2.0 from `https://pypi.org/simple`, passed
`uv pip check`, and executed all four HTML format CRUD examples.

- [golded-ftn 1.2.0](https://pypi.org/project/golded-ftn/1.2.0/) — [publishing run](https://github.com/golded-dev/golded-ftn-python/actions/runs/37303913149).
- [golded-ftn-msg 1.2.0](https://pypi.org/project/golded-ftn-msg/1.2.0/) — [publishing run](https://github.com/golded-dev/golded-ftn-msg-python/actions/runs/37304078307).
- [golded-ftn-jam 1.2.0](https://pypi.org/project/golded-ftn-jam/1.2.0/) — [publishing run](https://github.com/golded-dev/golded-ftn-jam-python/actions/runs/37304080739).
- [golded-ftn-squish 1.2.0](https://pypi.org/project/golded-ftn-squish/1.2.0/) — [publishing run](https://github.com/golded-dev/golded-ftn-squish-python/actions/runs/37304082708).
- [golded-ftn-hudson 1.2.0](https://pypi.org/project/golded-ftn-hudson/1.2.0/) — [publishing run](https://github.com/golded-dev/golded-ftn-hudson-python/actions/runs/37304173850).

GitHub README, SECURITY and release documents now record publication. The
immutable 1.2.0 archives retain their pre-publication README text. Future releases
will include the updated text. The existing tags and archive bytes were preserved.

GoldED interoperability stays deferred. Keep GoldED closed while writing;
concurrent mode remains disabled. The documentation site was not deployed.
