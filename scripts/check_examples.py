"""Type-check exactly the Python snippets published in the guide."""

import ast
import re
import subprocess
import tempfile
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Examples(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.items: dict[str, str] = {}
        self.current: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "code" and values.get("data-language") == "python":
            self.current = values["id"]
            assert self.current is not None
            self.items[self.current] = ""

    def handle_data(self, data: str) -> None:
        if self.current:
            self.items[self.current] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "code":
            self.current = None


def main() -> None:
    parser = Examples()
    source = (ROOT / "site/guide.html").read_text(encoding="utf-8")
    parser.feed(source)
    assert len(parser.items) == 9
    writer_source = (ROOT / "site/writers.html").read_text(encoding="utf-8")
    parser.feed(writer_source)
    assert len(parser.items) == 10
    api_source = (ROOT / "site/core-api.html").read_text(encoding="utf-8")
    parser.feed(api_source)
    assert any(name.startswith("core_api_") for name in parser.items)
    format_sources = ""
    for name in ("msg", "jam", "squish", "hudson"):
        page = (ROOT / "site" / f"{name}.html").read_text(encoding="utf-8")
        parser.feed(page)
        format_sources += page
        assert any(key.startswith(f"{name}_example_") for key in parser.items)
    with tempfile.TemporaryDirectory(prefix="ftn-doc-examples-") as temporary:
        paths = []
        for name, code in parser.items.items():
            ast.parse(code)
            path = Path(temporary) / (name + ".py")
            path.write_text(code, encoding="utf-8")
            paths.append(str(path))
        subprocess.run(["mypy", "--strict", *paths], check=True)
    for filename in re.findall(
        r'src="([^"]+)"', source + writer_source + api_source + format_sources
    ):
        if not filename.startswith("https:"):
            assert (ROOT / "site" / filename).is_file(), filename
    print(f"{len(parser.items)} HTML examples passed strict mypy; image assets exist.")


if __name__ == "__main__":
    main()
