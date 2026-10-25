# Read a message archive

Have a folder of messages from a BBS and want to see what is in it? Start here.
You can list the messages, read their text and save a message as a text file.
You do not need to write Python code, join a network or configure a BBS.

This guide uses `ftnt`, a terminal command for reading message bases on Linux and
macOS. It is not a graphical mail reader. The examples below only read the message
base; they do not edit, delete or send messages.

## Start with a copy

Keep the original files together and make a working copy with your file manager.
If the files are inside a ZIP or another compressed file, extract a copy first.
Do not rename individual files: some formats need several files with the same name.
If the BBS is still running, stop it before making the copy so the files agree.

In the examples, the working copy is called `archive-copy`. Replace each example
path with the location of your copy. Keep the quotes if the path contains spaces.

## Recognise the files

A message base stores the sender, recipient, subject and text of messages.
Different BBS programs used different storage formats. Look at the filenames in
your copy before choosing a command.

| Files you see | Format | Path to give the command |
| --- | --- | --- |
| Numbered files such as `1.MSG`, `2.MSG`, `42.MSG` | MSG; sometimes the Opus variant | The folder containing them, such as `archive-copy/msg` |
| `general.JHR`, `general.JDT`, `general.JDX` (often also `.JLR`) | JAM | `archive-copy/jam/general`, without an extension |
| `general.SQD`, `general.SQI` (often also `.SQL`) | Squish | `archive-copy/squish/general`, without an extension |
| `MSGHDR.BBS`, `MSGIDX.BBS`, `MSGTXT.BBS`, and possibly other `.BBS` files | Hudson | The folder containing them, such as `archive-copy/hudson` |

Uppercase and lowercase extensions are accepted. Keep every file from the original
base, even if it is not listed here. A missing companion file may prevent reading.
A `.PKT` file is a transfer packet, not one of these message bases;
see [Packets](packet.html) if that is what you have.

Numbered `.MSG` files do not tell you whether they use FTSC or Opus headers.
Use `--format opus` if the BBS configuration or original software identifies them
as Opus. Otherwise check that information before relying on decoded dates and
addresses; format detection is not automatic. GoldBase `.DAT` files are not
supported by these Python readers.

## Install the reader

You need Python 3.12 or newer, up to 3.14, on Linux or macOS. Open Terminal and
check the version:

```sh
python3 --version
```

Create a separate environment for the tool, activate it and install:

```sh
python3 -m venv .ftnt-reader
. .ftnt-reader/bin/activate
python -m pip install golded-ftn-tools==1.1.0
ftnt --version
```

**Release status:** version 1.1.0 is published. The installation command above
uses PyPI. To use reviewed wheel files instead, replace it with the following,
using your wheel folder's actual path:

```sh
python -m pip install --no-index --find-links "/path/to/wheelhouse" golded-ftn-tools==1.1.0
```

The normal installation includes all four message-base readers. No network extra
is needed. When opening a new terminal, activate the environment again before
using `ftnt`.

## List the messages

Choose **one** command matching the files you found:

```sh
ftnt heads "archive-copy/msg" --format msg --limit 10
ftnt heads "archive-copy/jam/general" --format jam --limit 10
ftnt heads "archive-copy/squish/general" --format squish --limit 10
ftnt heads "archive-copy/hudson" --format hudson --limit 10
```

For Opus, use the MSG folder command with `--format opus` instead.

Each output line describes one message. It is JSON: labelled fields in braces.
Look for `msgno` (message number), `from_name` (sender), `to_name` (recipient) and
`subject`. The limit keeps this first look to ten messages. For Hudson, each line
also has `board`, the numbered discussion area to which the message belongs.

## Read one message

Take a `msgno` from the list. These examples use **42**; replace it with a number
that actually appeared in your output:

```sh
ftnt read "archive-copy/msg" 42 --format msg --body
ftnt read "archive-copy/jam/general" 42 --format jam --body
ftnt read "archive-copy/squish/general" 42 --format squish --body
ftnt read "archive-copy/hudson" 42 --format hudson --board 7 --body
```

Again, choose only the command for your format. For Hudson, also replace **7** with
the message's `board` from the list. For Opus, use `--format opus`.

`--body` shows the message text rather than JSON. Some messages include routing or
format-control lines alongside the text; the reader does not silently remove them.
To save the text for reading in your normal editor, redirect it into a new file:

```sh
ftnt read "archive-copy/jam/general" 42 --format jam --body > message-42.txt
```

Choose a new output filename: `>` replaces an existing file with that name.
Save outside the message-base folder. This saves the decoded text of one message,
not a backup of its original binary files.

## If reading fails

First check the path, selected format and companion files. JAM and Squish need a
basename without an extension. Hudson needs the containing folder. Message numbers
can have gaps, so use a number from the list rather than assuming the first is 1.

If letters are garbled, the text may use a different character encoding. Readers
use declarations in the messages and otherwise fall back to CP850. If you know
that undeclared text uses another encoding, try `--fallback-charset`, for example:

```sh
ftnt read "archive-copy/jam/general" 42 --format jam --body --fallback-charset CP437
```

This changes the fallback for this read; it does not rewrite the files. Do not
assume every base uses CP437 or that it overrides a message's own declaration.

A damaged base may fail normal reading. Recovery mode can list recoverable messages
and report problems separately:

```sh
ftnt heads "archive-copy/jam/general" --format jam --archive --limit 10
```

Replace the path and format for your base. Recovery mode does not repair files or
guarantee that every message is recovered. Exit status 7 means issues occurred;
keep the diagnostics. Normal `read` still validates strictly and may fail even
when recovery mode listed a message. See the [CLI guide](cli.html) for recovery
exports if that happens. Keep the original files regardless of the result.

## Where to go next

For more terminal commands, use the [CLI guide](cli.html). For a Python program
that reads messages, use the [library guide](guide.html). Details of each storage
format are in [MSG / Opus](msg.html), [JAM](jam.html), [Squish](squish.html) and
[Hudson](hudson.html). You can stay with reading; none of these steps requires
configuring the network packages.
