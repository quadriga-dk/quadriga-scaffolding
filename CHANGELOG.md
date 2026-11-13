# Changelog

All notable changes to this project are documented in this file. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-11-13

First stable release. It is identical to `v1.0.0-rc.1` apart from the citation metadata: the Zenodo
concept DOI is now part of `CITATION.cff` and `README.md`.

## [1.0.0-rc.1] - 2026-11-13

First public release candidate. It combines everything the QUADRIGA OERs previously copied by
hand from the [Book_Template](https://github.com/quadriga-dk/Book_Template) into one installable
tool, so an OER can be brought up to date with a single command.

### Added

- `scaffold` command that compares an OER against the packaged shared files and reports drift per
  path with git-style status letters (`A`, `M`, `D`, `?`, `!`, and `ok` with `--show-ok`).
- `--update` to write the current file versions and remove retired ones, `--diff` for a git-style
  unified diff of modified files, `--color` for the diff output, and `--manifest` to swap the
  manifest for testing.
- Manifest format with `+` (install or overwrite) and `-` (delete) entries, validated against the
  packaged `data/` tree. Invalid manifests exit with code `2`.
- Safety rules for the destructive parts of an update: directories that are not empty, files inside
  a managed directory that are not tracked, and paths that are symlinks (or lie below one) are
  reported as blocked and are never written or deleted.
- The shared metadata scripts under `quadriga/metadata/`: they extract the book data and learning
  objectives into `quadriga-metadata.yml`, validate it, and generate `CITATION.cff`, `CITATION.bib`,
  `.zenodo.json`, JSON-LD, RDF/XML and the OERSI `metadata.yml` from it.
- `quadriga/metadata/run_all.py` as the entry point that regenerates all derived metadata files, and
  the matching `update-metadata.yml` GitHub Action that runs it on push and on version tags.
- Shared styling and scripts for carousels, drag-and-drop quizzes, custom tables and assessment
  boxes.
- The `video_figure` Sphinx extension and `video-figure.js`, which render `.mp4`/`.webm`/`.ogv`
  figure targets as HTML5 videos with click/`Space`/`Enter` playback and no native controls.
- Mermaid diagram support in `quadriga.css`, so diagrams are styled like figures instead of code
  blocks.
- Release metadata for this package: `CITATION.cff`, `.zenodo.json` and `RELEASING.md`.

### Fixed

- Bibliography entries keep words intact instead of breaking them mid-word.
- The metadata workflow derives a distinctive BibTeX key from the title and registers the R kernel
  without calling `IRkernel::installspec()`.

[Unreleased]: https://github.com/quadriga-dk/quadriga-scaffolding/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/quadriga-dk/quadriga-scaffolding/releases/tag/v1.0.0
[1.0.0-rc.1]: https://github.com/quadriga-dk/quadriga-scaffolding/releases/tag/v1.0.0-rc.1
