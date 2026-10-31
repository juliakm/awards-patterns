"""Fail-closed checks for the reviewed, data-free homepage publication.

Before rendering: python scripts/validate_publication.py --check-inputs
After rendering:  python scripts/validate_publication.py

The manifest below is the entire approved artifact for Quarto 1.10.20/cosmo,
not a repository resource scan. New articles, data, notebook downloads, chart
payloads and changed theme assets require explicit review and manifest changes.
This milestone has no public-data contract or saved computations to refresh:
only index.qmd is rendered, with execution disabled. Source/lock hashes and
artifact hashes are recorded in workflow logs, not copied into the website.
These checks complement human content review; they cannot identify every secret.
"""

import argparse
import hashlib
import json
import re
import stat
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

SITE_URL = "https://juliakm.com/awards-patterns/"
APPROVED_TARGETS = ("index.qmd",)
APPROVED_FILES = frozenset(
    {
        "index.html",
        "robots.txt",
        "search.json",
        "sitemap.xml",
        "site_libs/bootstrap/bootstrap-445b8638c3d06994fee0907d791121c4.min.css",
        "site_libs/bootstrap/bootstrap-icons.css",
        "site_libs/bootstrap/bootstrap-icons.woff",
        "site_libs/bootstrap/bootstrap.min.js",
        "site_libs/clipboard/clipboard.min.js",
        "site_libs/quarto-html/anchor.min.js",
        "site_libs/quarto-html/popper.min.js",
        "site_libs/quarto-html/quarto-syntax-highlighting-17888a1159294d3eb470f19f6f52f5a5.css",
        "site_libs/quarto-html/quarto.js",
        "site_libs/quarto-html/tabsets/tabsets.js",
        "site_libs/quarto-html/tippy.css",
        "site_libs/quarto-html/tippy.umd.min.js",
        "site_libs/quarto-nav/headroom.min.js",
        "site_libs/quarto-nav/quarto-nav.js",
    }
)
# Quarto's Cosmo fingerprint differs in the verified macOS and Linux builds.
APPROVED_BOOTSTRAP_STYLESHEETS = frozenset(
    {
        "site_libs/bootstrap/bootstrap-445b8638c3d06994fee0907d791121c4.min.css",
        "site_libs/bootstrap/bootstrap-a14d652b86e00f03abd5043129e363d4.min.css",
    }
)
APPROVED_DIRECTORIES = {
    str(parent)
    for name in APPROVED_FILES
    for parent in PurePosixPath(name).parents
    if str(parent) != "."
}
SECRET_PATTERN = re.compile(
    r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----"
    r"|(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{40,})"
    r"|(?:AKIA|ASIA)[A-Z0-9]{16}"
    r'|["\'](?:client_secret|private_key|api_key|access_token)["\']\s*:',
)


def approved_url(value: str, *, external_link: bool = False) -> None:
    """Check references, including encoded paths and project-subpath links."""
    url = urlsplit(unquote(value))
    if url.username or url.password or "\\" in value:
        raise ValueError("Credential-bearing or ambiguous resource URL")
    if url.scheme or url.netloc:
        if value.startswith(SITE_URL):
            path = unquote(url.path).removeprefix("/awards-patterns/")
        elif external_link and url.scheme == "https" and url.netloc:
            if PurePosixPath(url.path).suffix.lower() in {".ipynb", ".qmd"}:
                raise ValueError("Unapproved notebook download")
            return
        else:
            raise ValueError("Nonlocal or unsafe resource URL")
    else:
        path = url.path.removeprefix("./")
        if path.startswith("/awards-patterns/"):
            path = path.removeprefix("/awards-patterns/")
    if not path:
        return
    if "oscar" in path.casefold() or ".." in PurePosixPath(path).parts:
        raise ValueError(f"Forbidden resource path: {path}")
    if path not in APPROVED_FILES and path not in APPROVED_BOOTSTRAP_STYLESHEETS:
        raise ValueError(f"Unapproved resource reference: {path}")


class HomepageParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if "download" in attributes or tag in {
            "iframe",
            "object",
            "embed",
            "form",
        }:
            raise ValueError("Unapproved download or embedded content")
        if tag == "script" and "src" not in attributes:
            approved_inline = {
                "quarto-search-options": "application/json",
                "quarto-html-after-body": "application/javascript",
            }
            if (
                attributes.get("id") not in approved_inline
                or attributes.get("type") != approved_inline[attributes["id"]]
            ):
                raise ValueError("Unapproved inline script or chart payload")
        for key in ("href", "src", "poster", "data", "action", "srcset"):
            if key in attributes:
                approved_url(
                    attributes[key], external_link=(tag == "a" and key == "href")
                )
        for key, value in attributes.items():
            if key.startswith("on") and not (
                tag == "button"
                and "navbar-toggler" in attributes.get("class", "").split()
                and key == "onclick"
                and value
                == "if (window.quartoToggleHeadroom) { window.quartoToggleHeadroom(); }"
            ):
                raise ValueError("Unapproved inline event handler")

    handle_startendtag = handle_starttag


def validate_site(site: Path) -> list[dict]:
    if site.is_symlink() or not site.is_dir():
        raise ValueError("Site root must be a real directory, not a symlink")
    inventory = []
    found = set()
    # Walk only the generated artifact; never follow symlinks or scan the checkout.
    for path in sorted(site.rglob("*")):
        name = path.relative_to(site).as_posix()
        if "oscar" in unquote(name).casefold():
            raise ValueError(f"Forbidden publication path: {name}")
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            raise ValueError(f"Symlink is not publishable: {name}")
        if stat.S_ISDIR(mode):
            if name not in APPROVED_DIRECTORIES:
                raise ValueError(f"Unapproved publication directory: {name}")
            continue
        if not stat.S_ISREG(mode) or (
            name not in APPROVED_FILES and name not in APPROVED_BOOTSTRAP_STYLESHEETS
        ):
            raise ValueError(f"Unapproved publication file: {name}")
        if path.stat().st_nlink != 1:
            raise ValueError(f"Hard-linked file is not publishable: {name}")
        payload = path.read_bytes()
        if path.suffix != ".woff" and SECRET_PATTERN.search(payload.decode("utf-8")):
            raise ValueError(f"Potential credential in publication file: {name}")
        found.add(name)
        inventory.append(
            {
                "path": name,
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        )
    missing = (APPROVED_FILES - APPROVED_BOOTSTRAP_STYLESHEETS) - found
    if missing:
        raise ValueError(
            f"Missing approved publication files: {', '.join(sorted(missing))}"
        )
    if len(found & APPROVED_BOOTSTRAP_STYLESHEETS) != 1:
        raise ValueError("Expected exactly one reviewed Bootstrap stylesheet")
    HomepageParser().feed((site / "index.html").read_text(encoding="utf-8"))
    search = json.loads((site / "search.json").read_text(encoding="utf-8"))
    if not isinstance(search, list):
        raise ValueError("Invalid search index")
    for entry in search:
        if not isinstance(entry, dict) or set(entry) != {
            "objectID",
            "href",
            "title",
            "section",
            "text",
        }:
            raise ValueError("Unapproved search payload")
        for key in ("href", "objectID"):
            approved_url(entry[key])
            if urlsplit(entry[key]).path != "index.html":
                raise ValueError("Search index must reference only the homepage")
    sitemap = ElementTree.parse(site / "sitemap.xml")
    locations = sitemap.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
    if [node.text for node in locations] != [SITE_URL + "index.html"]:
        raise ValueError("Sitemap must contain only the approved homepage")
    if (site / "robots.txt").read_text(encoding="utf-8").strip() != (
        "Sitemap: " + SITE_URL + "sitemap.xml"
    ):
        raise ValueError("Unapproved robots metadata")
    return inventory


def validate_inspection(inspection: dict, root: Path) -> dict:
    for name in (*APPROVED_TARGETS, "_quarto.yml", "uv.lock"):
        path = root / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Missing or symlinked publication input: {name}")
    config = inspection["project"]["config"]
    project = config["project"]
    if inspection["quarto"]["version"] != "1.10.20":
        raise ValueError("Publication requires pinned Quarto 1.10.20")
    if (
        project.get("render") != list(APPROVED_TARGETS)
        or project.get("resources") != []
        or project.get("output-dir") != "_site"
        or project.get("type") != "website"
        or project.get("pre-render")
        or project.get("post-render")
        or inspection.get("resources") != []
        or inspection.get("engines") != ["markdown"]
        or config["website"].get("site-url") != SITE_URL
    ):
        raise ValueError("Only the data-free homepage configuration is approved")
    information = inspection["fileInformation"]
    if set(information) != set(APPROVED_TARGETS) or any(
        item.get("codeCells") != [] or item.get("includeMap") != []
        for item in information.values()
    ):
        raise ValueError("Unapproved computation, notebook, or included source")
    return {
        "targets": list(APPROVED_TARGETS),
        "quarto": inspection["quarto"]["version"],
        "public_data_inputs": [],
        "saved_computations": [],
        "input_sha256": {
            name: hashlib.sha256((root / name).read_bytes()).hexdigest()
            for name in (*APPROVED_TARGETS, "_quarto.yml", "uv.lock")
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=Path("_site"))
    parser.add_argument("--check-inputs", action="store_true")
    args = parser.parse_args()
    try:
        if args.check_inputs:
            for name in (*APPROVED_TARGETS, "_quarto.yml"):
                if Path(name).is_symlink() or not Path(name).is_file():
                    raise ValueError(f"Missing or symlinked publication input: {name}")
            result = subprocess.run(
                ["quarto", "inspect", "index.qmd"],
                check=True,
                capture_output=True,
                text=True,
            )
            report = validate_inspection(json.loads(result.stdout), Path("."))
        else:
            report = {"approved_artifact": validate_site(args.site)}
        print(json.dumps(report, indent=2))
        return 0
    except (
        ValueError,
        KeyError,
        TypeError,
        OSError,
        ElementTree.ParseError,
        subprocess.CalledProcessError,
    ) as error:
        print(f"Publication validation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
