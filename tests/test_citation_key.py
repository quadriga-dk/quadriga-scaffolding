"""Tests for the BibTeX citation key generation.

The metadata scripts ship as a template inside the packaged ``data/`` tree and
are not part of the tool's own code base (``data/`` is excluded from ruff and
mypy). Inside a scaffolded OER repository they run as the ``quadriga`` package,
where PyYAML is available. The fixture below mirrors that environment: it copies
the packaged ``quadriga`` tree to ``tmp_path``, puts it on ``sys.path`` and
stubs ``yaml`` if PyYAML is not installed for the tool itself.
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
def utils(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[ModuleType]:
    """Load the packaged metadata utils the way an OER repository runs them."""
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
    module = importlib.import_module("quadriga.metadata.utils")
    yield module
    for name in list(sys.modules):
        if name == "quadriga" or name.startswith("quadriga."):
            sys.modules.pop(name, None)


AUTHORS = [{"familyName": "Schnaitter", "givenName": "Hannes"}]


def test_key_uses_label_after_last_colon(utils: ModuleType) -> None:
    title = "QUADRIGA-OER: erstellen und gestalten mit Jupyter Book. QUADRIGA Open Educational Resources: Anleitung"
    assert utils.generate_citation_key(AUTHORS, title, "2026") == "Schnaitter_Anleitung_2026"


def test_key_uses_first_word_without_subtitle(utils: ModuleType) -> None:
    assert utils.generate_citation_key(AUTHORS, "Einstieg in die Datenanalyse", "2025") == "Schnaitter_Einstieg_2025"


def test_key_ignores_empty_colon_segments(utils: ModuleType) -> None:
    assert utils.generate_citation_key(AUTHORS, "Titel:  : Anleitung ", "2026") == "Schnaitter_Anleitung_2026"


def test_key_falls_back_to_untitled(utils: ModuleType) -> None:
    assert utils.generate_citation_key(AUTHORS, "", "2026") == "Schnaitter_Untitled_2026"


def test_key_without_authors(utils: ModuleType) -> None:
    assert utils.generate_citation_key([], "QUADRIGA Lernhinweise: Anleitungen", "2026") == "Unknown_Anleitungen_2026"
