"""Exercise the shared session contract across all four concrete packages."""

from contextlib import AbstractContextManager
from pathlib import Path

import pytest
from golded_ftn import (
    ConflictError,
    MessagePatch,
    MessageWriterSession,
    OutgoingMessage,
    UnsupportedOperationError,
    WriterOptions,
)
from golded_ftn_hudson import HudsonWriter
from golded_ftn_jam import JamWriter
from golded_ftn_msg import MsgWriter
from golded_ftn_squish import SquishWriter


def message(body="Hello."):
    return OutgoingMessage(
        from_name="Alice", to_name="Bob", subject="Fixture", body_text=body
    )


def create(format_name, path):
    writers = {
        "msg": MsgWriter(),
        "jam": JamWriter(),
        "squish": SquishWriter(),
        "hudson": HudsonWriter(),
    }
    writers[format_name].create(path)


def open_session(
    format_name: str, path: Path, options: WriterOptions | None = None
) -> AbstractContextManager[MessageWriterSession]:
    if format_name == "hudson":
        return HudsonWriter().open(path, board=1, options=options)
    if format_name == "jam":
        return JamWriter().open(path, options)
    if format_name == "squish":
        return SquishWriter().open(path, options)
    return MsgWriter().open(path, options)


@pytest.mark.parametrize("format_name", ["msg", "jam", "squish", "hudson"])
def test_sessions_preserve_independent_revisions_and_detect_conflicts(
    format_name, tmp_path
):
    path = tmp_path / "base"
    create(format_name, path)
    with (
        open_session(format_name, path) as first,
        open_session(format_name, path) as second,
    ):
        a = first.append(message())
        before = first.read(a.identity.msgno)
        b = second.append(message("Other message"))
        assert first.read(a.identity.msgno).revision == before.revision
        second.delete(b.identity, b.revision)
        assert first.read(a.identity.msgno).revision == before.revision
        changed = second.update(
            before.identity, MessagePatch(subject="Changed"), before.revision
        )
        for operation in ("update", "delete"):
            with pytest.raises(ConflictError):
                if operation == "update":
                    first.update(before.identity, MessagePatch(), before.revision)
                else:
                    first.delete(before.identity, before.revision)
        first.delete(changed.identity, changed.revision)
        with pytest.raises(ConflictError):
            second.delete(changed.identity, changed.revision)


@pytest.mark.parametrize("format_name", ["msg", "jam", "squish", "hudson"])
def test_golded_concurrent_mode_is_disabled(format_name, tmp_path):
    path = tmp_path / "base"
    create(format_name, path)
    with pytest.raises(UnsupportedOperationError):
        with open_session(format_name, path, WriterOptions(concurrent=True)):
            pytest.fail("Untested GoldED concurrency was enabled")
