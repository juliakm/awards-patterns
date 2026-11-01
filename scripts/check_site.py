"""Fail if the rendered site contains anything that should stay private."""

import re
import sys
from pathlib import Path

SITE = Path("_site")
# Raw data stays private; pages publish charts and summaries, never source files.
FORBIDDEN_SUFFIXES = {".csv", ".tsv", ".parquet", ".zip", ".ipynb", ".pkl", ".env"}
SECRET = re.compile(
    rb"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----"
    rb"|gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{40,}"
    rb"|(?:AKIA|ASIA)[A-Z0-9]{16}"
)


def problems(site: Path) -> list[str]:
    found = []
    if not (site / "index.html").is_file():
        found.append("missing index.html")
    for path in site.rglob("*"):
        name = path.relative_to(site).as_posix()
        if "oscar" in name.casefold():
            found.append(f"'oscar' in published path: {name}")
        if path.is_symlink():
            found.append(f"symlink: {name}")
        elif path.is_file():
            if path.suffix.casefold() in FORBIDDEN_SUFFIXES:
                found.append(f"data file: {name}")
            if SECRET.search(path.read_bytes()):
                found.append(f"possible secret: {name}")
    return found


def main() -> int:
    found = problems(SITE)
    for problem in found:
        print(problem, file=sys.stderr)
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
