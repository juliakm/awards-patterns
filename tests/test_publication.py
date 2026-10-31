import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

import pytest

HELPER = Path(__file__).parents[1] / "scripts" / "validate_publication.py"
SPEC = importlib.util.spec_from_file_location("validate_publication", HELPER)
publication = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(publication)


@pytest.fixture
def workspace():
    # Keep fixture writes inside the project, never in OS temporary directories.
    directory = Path.cwd() / f".publication-test-{uuid4().hex}"
    directory.mkdir()
    try:
        yield directory
    finally:
        shutil.rmtree(directory)


@pytest.fixture
def site(workspace):
    directory = workspace / "_site"
    directory.mkdir()
    for name in publication.APPROVED_FILES:
        path = directory / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    (directory / "index.html").write_text(
        '<!doctype html><html><a href="./index.html#home">Home</a>'
        '<button class="navbar-toggler" onclick="if (window.quartoToggleHeadroom) '
        '{ window.quartoToggleHeadroom(); }">Menu</button></html>',
        encoding="utf-8",
    )
    (directory / "search.json").write_text("[]", encoding="utf-8")
    (directory / "robots.txt").write_text(
        "Sitemap: " + publication.SITE_URL + "sitemap.xml\n", encoding="utf-8"
    )
    (directory / "sitemap.xml").write_text(
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"<url><loc>{publication.SITE_URL}index.html</loc></url></urlset>",
        encoding="utf-8",
    )
    return directory


def test_homepage_artifact_reports_only_approved_files(site):
    inventory = publication.validate_site(site)
    assert {entry["path"] for entry in inventory} == publication.APPROVED_FILES
    assert (
        next(entry for entry in inventory if entry["path"] == "index.html")["bytes"] > 0
    )


@pytest.mark.parametrize("stylesheet", publication.APPROVED_BOOTSTRAP_STYLESHEETS)
def test_reviewed_platform_stylesheet_and_link_are_accepted(site, stylesheet):
    original = next(
        name
        for name in publication.APPROVED_FILES
        if name in publication.APPROVED_BOOTSTRAP_STYLESHEETS
    )
    (site / original).rename(site / stylesheet)
    (site / "index.html").write_text(
        f'<html><link rel="stylesheet" href="{stylesheet}"></html>', encoding="utf-8"
    )
    inventory = publication.validate_site(site)
    assert stylesheet in {entry["path"] for entry in inventory}


def test_multiple_reviewed_stylesheets_are_rejected(site):
    for stylesheet in publication.APPROVED_BOOTSTRAP_STYLESHEETS:
        (site / stylesheet).write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="exactly one reviewed Bootstrap"):
        publication.validate_site(site)


@pytest.mark.parametrize(
    "name",
    [
        "articles/OScAr-history.html",
        "site_libs/%4fscar.js",
        "data/raw/ballots.csv",
        "private/source.txt",
        "models/fitted.joblib",
        ".env",
        "credentials.json",
        "render.log",
        "notebooks/review.ipynb",
        "unselected.html",
        "site_libs/quarto-html/unreviewed.js",
        "site_libs/bootstrap/bootstrap-00000000000000000000000000000000.min.css",
    ],
)
def test_unapproved_artifacts_fail_closed(site, name):
    path = site / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("not for publication", encoding="utf-8")
    with pytest.raises(ValueError, match="Forbidden|Unapproved"):
        publication.validate_site(site)


@pytest.mark.parametrize("kind", ["file", "directory", "root", "hardlink"])
def test_links_are_not_publishable(site, workspace, kind):
    if kind == "root":
        linked = workspace / "linked-site"
        linked.symlink_to(site, target_is_directory=True)
        candidate = linked
    elif kind == "directory":
        linked = site / "site_libs" / "quarto-nav"
        shutil.rmtree(linked)
        linked.symlink_to(workspace, target_is_directory=True)
        candidate = site
    else:
        linked = site / "index.html"
        linked.unlink()
        source = workspace / "saved.html"
        source.write_text("private source", encoding="utf-8")
        if kind == "hardlink":
            linked.hardlink_to(source)
        else:
            linked.symlink_to(source)
        candidate = site
    with pytest.raises(ValueError, match="[Ss]ymlink|Hard-linked"):
        publication.validate_site(candidate)


def test_missing_homepage_is_rejected(site):
    (site / "index.html").unlink()
    with pytest.raises(ValueError, match="Missing.*index.html"):
        publication.validate_site(site)


def test_cli_rejects_injected_case_insensitive_forbidden_path(site):
    (site / "OSCAR.txt").write_text("not public", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(HELPER), "--site", str(site)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "Forbidden publication path: OSCAR.txt" in result.stderr
    assert not result.stdout


@pytest.mark.parametrize(
    "html",
    [
        '<a href="data/raw/ballots.csv">Download</a>',
        '<a href="index.html" download>Download</a>',
        '<script type="application/json">{"data": ["private"]}</script>',
        '<script src="https://example.org/api.js"></script>',
        '<a href="%4fScAr.html">Unintended page</a>',
        '<a href="../outside.html">Outside</a>',
        '<button class="navbar-toggler" onclick="fetch(\'/private\')">Menu</button>',
        "<pre>-----BEGIN PRIVATE KEY-----</pre>",
    ],
)
def test_html_resources_downloads_and_credentials_are_guarded(site, html):
    (site / "index.html").write_text(html, encoding="utf-8")
    with pytest.raises(ValueError):
        publication.validate_site(site)


def test_search_payload_cannot_link_an_unselected_notebook(site):
    (site / "search.json").write_text(
        json.dumps(
            [
                {
                    "objectID": "review.ipynb",
                    "href": "review.ipynb",
                    "title": "Review",
                    "section": "",
                    "text": "",
                }
            ]
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Unapproved resource reference"):
        publication.validate_site(site)


@pytest.fixture
def inspection(workspace):
    for name in ("index.qmd", "_quarto.yml", "uv.lock"):
        (workspace / name).write_text("reviewed fixture", encoding="utf-8")
    return {
        "quarto": {"version": "1.10.20"},
        "engines": ["markdown"],
        "resources": [],
        "fileInformation": {"index.qmd": {"includeMap": [], "codeCells": []}},
        "project": {
            "config": {
                "project": {
                    "type": "website",
                    "output-dir": "_site",
                    "render": ["index.qmd"],
                    "resources": [],
                },
                "website": {"site-url": publication.SITE_URL},
            }
        },
    }


def test_minimal_inputs_do_not_require_any_dataset_or_frozen_result(
    inspection, workspace
):
    report = publication.validate_inspection(inspection, workspace)
    assert report["public_data_inputs"] == report["saved_computations"] == []
    assert not (workspace / "data").exists()


def test_missing_root_source_is_rejected_before_publication(inspection, workspace):
    (workspace / "index.qmd").unlink()
    with pytest.raises(ValueError, match="Missing.*index.qmd"):
        publication.validate_inspection(inspection, workspace)


@pytest.mark.parametrize("change", ["render", "resources", "execute", "include"])
def test_preflight_rejects_unreviewed_targets_resources_or_execution(
    inspection, workspace, change
):
    if change == "render":
        inspection["project"]["config"]["project"]["render"].append("notebooks/*.ipynb")
    elif change == "resources":
        inspection["project"]["config"]["project"]["resources"].append("data/raw/**")
    elif change == "execute":
        inspection["fileInformation"]["index.qmd"]["codeCells"].append(
            {"source": "train_model()"}
        )
    else:
        inspection["fileInformation"]["index.qmd"]["includeMap"].append("private.qmd")
    with pytest.raises(ValueError, match="Only the data-free|Unapproved computation"):
        publication.validate_inspection(inspection, workspace)
