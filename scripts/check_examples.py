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
    source = (ROOT / "site/index.html").read_text(encoding="utf-8")
    parser.feed(source)
    with tempfile.TemporaryDirectory(prefix="ftn-doc-examples-") as temporary:
        paths = []
        for name, code in parser.items.items():
            ast.parse(code)
            path = Path(temporary) / (name + ".py")
            path.write_text(code, encoding="utf-8")
            paths.append(str(path))
        subprocess.run(["mypy", "--strict", *paths], check=True)
    assert len(parser.items) == 9
    for filename in re.findall(r'src="([^"]+)"', source):
        if not filename.startswith("https:"):
            assert (ROOT / "site" / filename).is_file(), filename
    print("Nine HTML examples parsed and passed strict mypy; image assets exist.")


if __name__ == "__main__":
    main()
