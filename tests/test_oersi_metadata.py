"""Tests for the OERSI metadata template script.

The script ships as a template inside the packaged ``data/`` tree and is not
part of the tool's own code base (``data/`` is excluded from ruff and mypy).
Inside a scaffolded OER repository it runs as the ``quadriga`` package, where
PyYAML is available. The fixture below mirrors that environment: it copies the
packaged ``quadriga`` tree to ``tmp_path``, puts it on ``sys.path`` and stubs
``yaml`` if PyYAML is not installed for the tool itself. Only the pure mapping
functions are exercised here; the file-based entry points are shared
``utils.py`` code that runs in the OER repositories.
"""

from __future__ import annotations

import importlib
import shutil
import sys
import types
from collections.abc import Iterator
from pathlib import Path
from types import ModuleType
from typing import cast

import pytest

from quadriga_scaffolding import scaffold as sc


@pytest.fixture
def oersi(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[ModuleType]:
    """Load the packaged OERSI template script the way an OER repository runs it."""
    data_root = cast(Path, sc.package_data_root())
    shutil.copytree(
        data_root / "quadriga",
        tmp_path / "quadriga",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    if "yaml" not in sys.modules:
        try:
            importlib.import_module("yaml")
        except ModuleNotFoundError:
            monkeypatch.setitem(sys.modules, "yaml", types.ModuleType("yaml"))
    module = importlib.import_module("quadriga.metadata.create_oersi_metadata")
    yield module
    for name in list(sys.modules):
        if name == "quadriga" or name.startswith("quadriga."):
            sys.modules.pop(name, None)


def test_normalize_github_pages_deep_link_to_book_root(oersi: ModuleType) -> None:
    assert (
        oersi._normalize_oer_url("https://quadriga-dk.github.io/Tabelle-Fallstudie-1/Markdown/0_Intro.html")
        == "https://quadriga-dk.github.io/Tabelle-Fallstudie-1/"
    )
    assert (
        oersi._normalize_oer_url("https://quadriga-dk.github.io/Tabelle-Fallstudie-2/Titelseite.html")
        == "https://quadriga-dk.github.io/Tabelle-Fallstudie-2/"
    )


def test_normalize_github_pages_root_is_unchanged(oersi: ModuleType) -> None:
    assert (
        oersi._normalize_oer_url("https://quadriga-dk.github.io/Text-Fallstudie-1/")
        == "https://quadriga-dk.github.io/Text-Fallstudie-1/"
    )
    assert (
        oersi._normalize_oer_url("https://quadriga-dk.github.io/Text-Fallstudie-1")
        == "https://quadriga-dk.github.io/Text-Fallstudie-1/"
    )


def test_normalize_github_pages_site_root_is_unchanged(oersi: ModuleType) -> None:
    # A user/organisation pages site serves its content at the site root.
    assert oersi._normalize_oer_url("https://quadriga-dk.github.io/") == "https://quadriga-dk.github.io/"


def test_normalize_leaves_other_hosts_unchanged(oersi: ModuleType) -> None:
    assert (
        oersi._normalize_oer_url("https://oersi.org/resources/intro.html") == "https://oersi.org/resources/intro.html"
    )
    assert oersi._normalize_oer_url("https://github.com/quadriga-dk/Text-Fallstudie-1") == (
        "https://github.com/quadriga-dk/Text-Fallstudie-1"
    )


def test_normalize_empty_input_returns_empty_string(oersi: ModuleType) -> None:
    assert oersi._normalize_oer_url("") == ""
    assert oersi._normalize_oer_url(None) == ""


def test_build_oersi_metadata_uses_normalised_id(oersi: ModuleType) -> None:
    metadata = {
        "title": "Test-OER",
        "identifierOER": "https://quadriga-dk.github.io/Tabelle-Fallstudie-1/Markdown/0_Intro.html",
    }
    result = oersi.build_oersi_metadata(metadata)
    assert result["id"] == "https://quadriga-dk.github.io/Tabelle-Fallstudie-1/"
