"""The site check should pass a clean build and catch each kind of leak."""

import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "check_site", Path("scripts/check_site.py")
)
check_site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_site)


@pytest.fixture
def site(tmp_path):
    (tmp_path / "index.html").write_text("<p>Hello</p>", encoding="utf-8")
    return tmp_path


def test_clean_site_passes(site):
    assert check_site.problems(site) == []


@pytest.mark.parametrize(
    ("name", "content"),
    [
        ("full_data.csv", "Ceremony"),
        ("Oscars/page.html", "ok"),
        ("page.html", "-----BEGIN PRIVATE KEY-----"),
    ],
)
def test_leaks_fail(site, name, content):
    path = site / name
    path.parent.mkdir(exist_ok=True)
    path.write_text(content, encoding="utf-8")
    assert check_site.problems(site)


def test_missing_homepage_fails(tmp_path):
    assert check_site.problems(tmp_path) == ["missing index.html"]
