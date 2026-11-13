# QUADRIGA scaffolding

`scaffold` updates a QUADRIGA OER that was created from the
[QUADRIGA Book_Template](https://github.com/quadriga-dk/Book_Template): it compares the OER against
the shared files that ship with this package and reports the differences, and with `--update` it
copies the current versions into the OER and removes files that are no longer needed.

The shared files are the metadata scripts (`quadriga/`), the common CSS and JavaScript
(`_static/`), the video-figure extension (`_ext/video_figure.py`) and the metadata GitHub Action
(`.github/workflows/update-metadata.yml`). Only paths listed in the packaged manifest are managed.
Book-specific files — `_config.yml`, `_toc.yml`, chapters, notebooks, `assets/`, `references.bib`
and `requirements.*` — are never touched. The tool does not run git or build the book; review and
commit the result yourself.

## Installation

### As a tool

The package is not published on PyPI; install it directly from GitHub with
[`uv`](https://docs.astral.sh/uv/) or [`pipx`](https://pipx.pypa.io/):

```console
$ uv tool install git+https://github.com/quadriga-dk/quadriga-scaffolding.git
```

```console
$ pipx install git+https://github.com/quadriga-dk/quadriga-scaffolding.git
```

Both put a `scaffold` executable on your `PATH`. To pick up newer revisions, run
`uv tool upgrade quadriga-scaffolding` (or reinstall with `pipx install --force …`). Python 3.11 or
newer is required.

### For development

The project is a standard `pyproject.toml`-based package. The recommended way to set up a
development environment is via [`just`](https://github.com/casey/just):

```console
$ git clone https://github.com/quadriga-dk/quadriga-scaffolding.git
$ cd quadriga-scaffolding
$ just install
```

If you don't have `just` yet, install it via your package manager (e.g. `brew install just`,
`apt install just`, `cargo install just`) — see the
[just installation docs](https://github.com/casey/just#installation) for more options.

`just install` will detect whether `uv` is available and use it (`uv sync`) if so. Otherwise it
falls back to creating a `.venv/` with `python3 -m venv` and installing the package in **editable**
mode together with the development tools (`pytest`, `ruff`, `mypy`) via `pip`.

If you'd rather run the steps yourself, with `uv`:

```console
$ uv sync
```

Or with plain `pip`:

```console
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -e ".[dev]"
```

## Updating an OER

Run the command from the OER's repository root (or pass its path). A typical update:

```console
$ cd ~/code/Text-Fallstudie-1
$ git status                   # start from a clean working tree
$ scaffold .                   # what would change? (exit code 1 = drift)
$ scaffold --diff .            # show the content changes of modified files
$ scaffold --update .          # write the packaged files, remove retired ones
$ git add -A                   # new files may have been added
$ git diff --cached            # review the result
$ git commit -m "chore: update QUADRIGA scaffold"
```

In `--update` mode the files are written first and the printed output is the state **after** the
update. Everything resolvable is gone from that output, so a clean update prints nothing and exits
`0`; anything that is still listed is drift the tool refuses to resolve (see
[Conflicts and safety](#conflicts-and-safety)) and exits `1`.

When you are working inside a clone of this repository, `just scaffold` runs the local version of
the tool:

```console
$ just scaffold ../Text-Fallstudie-1/
```

Note that the `just` recipe always exits `0` so that `just` does not fail on drift. Use the
`scaffold` command directly when you need the exit code (for example in a script or CI).

Equivalent invocations:

```console
$ uv run python -m quadriga_scaffolding ../path/to/oer/
$ scaffold ../path/to/oer/        # if the venv is activated or the tool is installed
```

## Command-line options

| Option | Meaning |
|---|---|
| `OER_PATH` | Path to the OER directory (required). All reported paths are relative to it. |
| `--update` | Apply the changes instead of only reporting them. |
| `--diff` | Print a git-style unified diff of each modified (`M`) file below its status line. |
| `--color {auto,always,never}` | Colorize the `--diff` output. Default `auto`. |
| `--show-ok` | Also print in-sync (`ok`) entries. |
| `--manifest PATH` | Use another manifest instead of the packaged one. |
| `-v`, `--verbose` | Show INFO logging on stderr (the diff output is unchanged). |
| `-d`, `--debug` | Show DEBUG logging on stderr (implies `--verbose`). |

`--diff` only adds content for `M` entries; `A`/`D`/`?`/`!` lines are unchanged. In `--update` mode
the modifications are resolved first, so there is nothing left to diff. `-v`/`-d` only affect
logging verbosity, not which diff entries are printed — that is what `--show-ok` is for.

`--manifest` replaces the manifest, not the data: entries are still resolved against the packaged
`data/` directory. It is useful for testing and local experimentation.

## Output

Each changed path is printed on its own line with a git-style status letter:

| Letter | Meaning |
|---|---|
| `A` | **add** — listed in the manifest but missing in the OER |
| `M` | **modify** — present but its bytes differ from the packaged version |
| `D` | **delete** — listed for deletion and removable |
| `?` | **untracked** — inside a managed `+ dir/` but not in the manifest |
| `!` | **blocked** — a `- dir/` that is not empty (cannot be deleted), or a tracked target that is a symlink / lies under one (not written through) |
| ` ` | **ok** — already in sync (only shown with `--show-ok`) |

A detail in parentheses explains `!` entries, e.g. `(3 files inside)` or `(symlink)`. Entries are
sorted by status (drift first, in the order above) and then by path. Comparison is byte-exact: no
line-ending or whitespace normalization is applied.

### Diff mode

`--diff` prints a git-style unified diff of each modified (`M`) file directly under its status
line, so you can see *what* would change before running `--update`. The packaged version is the
`a/` (old) side and the OER's current file is the `b/` (new) side. Files that are not valid UTF-8
(or contain NUL bytes) are reported as `Binary files a/… and b/… differ` instead of a line diff.

```console
$ scaffold --diff ../path/to/oer/
M _static/quadriga.css
--- a/_static/quadriga.css
+++ b/_static/quadriga.css
@@ -1,3 +1,3 @@
 body {
-  color: #000;
+  color: #111;
 }
```

The diff body is colored git-style (added lines green, removed lines red, hunk headers cyan, file
headers bold); the `A`/`M`/`D`/`?`/`!` status lines are never colored. Coloring follows
`--color=auto` by default: on when stdout is a terminal, off when the output is piped or redirected,
and always off when the [`NO_COLOR`](https://no-color.org) environment variable is set. Pass
`--color=always` to force colors (e.g. when piping into a pager that interprets them) or
`--color=never` to disable them.

## What the scaffold manages

The packaged `data/` directory mirrors the OER root, so `data/_static/quadriga.css` is installed as
`<oer>/_static/quadriga.css`. The manifest currently covers:

| Area | Paths | Purpose |
|---|---|---|
| Assessment helpers | `quadriga/assessment.py`, `quadriga/colors.py` | Drag-and-drop quizzes, answer boxes, `JupyterQuiz` colors |
| Metadata scripts | `quadriga/metadata/` | Extract book data and learning objectives into `quadriga-metadata.yml`, validate it, and generate `CITATION.cff`, `CITATION.bib`, `.zenodo.json`, JSON-LD, RDF/XML and the OERSI `metadata.yml` |
| Metadata entry point | `quadriga/metadata/run_all.py` | Regenerates all derived metadata files; used by the workflow and runnable as `python -m quadriga.metadata.run_all` |
| Shared styling and scripts | `_static/` | `quadriga.css`, carousel, drag-and-drop, custom tables, video figures |
| Video figures | `_ext/video_figure.py`, `_static/video-figure.js` | Renders `{figure}` targets that are `.mp4`/`.webm`/`.ogv` as HTML5 video |
| Metadata workflow | `.github/workflows/update-metadata.yml` | Regenerates and commits the metadata files on push and on version tags |

`_config.yml` is book-specific and not managed: it is where `_static/` and `_ext/` content is
registered (see [Enabling video figures](#enabling-video-figures-in-an-oer) and
[Enabling Mermaid diagrams](#enabling-mermaid-diagrams-in-an-oer)). If your book does not load one of
the shared files yet, add it there — the scaffold only copies the files into place.

## Manifest format

The manifest lives at `src/quadriga_scaffolding/data/scaffold.txt` and ships with the package. One
entry per line:

| Syntax | Meaning |
|---|---|
| `+ path/to/file` | Install or overwrite `<oer>/path/to/file` with `data/path/to/file`. |
| `+ path/to/dir/` | Manage every packaged file under `data/path/to/dir/`. The trailing `/` is required for directories. |
| `- path/to/file` | Delete `<oer>/path/to/file` if it exists. |
| `- path/to/dir/` | Delete `<oer>/path/to/dir/` if it is recursively empty. |
| anything else | Comment (blank lines included). |

Rules:

- Paths are relative to the OER root. Absolute paths and `..` segments are rejected.
- A path must not appear under both `+` and `-`; that fails validation.
- Every `+` entry must exist in the packaged `data/` tree with a matching kind (file vs. directory);
  `-` entries do not need to exist in the package.
- If a file is covered more than once (e.g. by `+ dir/` and `+ dir/file`), it is reported once, with
  the most drifted status winning.
- Lines under `+ dir/` that are not in the package are reported as untracked; the tool never deletes
  them.

## Conflicts and safety

Three kinds of drift are **never** resolved automatically:

- A directory marked for deletion (`- dir/`) that still contains files is **never** auto-deleted —
  remove its contents yourself first.
- Files found inside a managed directory (`+ dir/`) but not listed in the manifest are reported as
  **untracked** and **never** deleted.
- A tracked path that is a symlink (or lies under a symlinked directory) is reported as
  **blocked** and **never** written through — the tool skips the write instead of following the
  link out of the OER tree. Remove the link yourself and re-run.

In `--update` mode these warnings are also logged to stderr, and the entries remain in the final
output, so the command exits `1`.

## Ignored artifacts

Build, editor, and VCS artifacts are ignored everywhere — `__pycache__/`, `*.pyc`/`*.pyo`,
`.DS_Store`, `.ipynb_checkpoints/`, and `.git/`. They are never synced from the package, never
reported as untracked, and a `- dir/` containing only such artifacts counts as empty (and so is
removable).

## Exit codes

| Code | Meaning |
|---|---|
| `0` | fully in sync (no `A`/`M`/`D`/`?`/`!` after the run) |
| `1` | drift detected; in `--update` mode this means `?`/`!` items remain after the update |
| `2` | the manifest fails validation (missing packaged file, wrong kind, or a path listed under both `+` and `-`) |

## Enabling video figures in an OER

The scaffold ships three pieces of video support: `_ext/video_figure.py` (renders a `{figure}` whose
target is an `.mp4`/`.webm`/`.ogv` file as an HTML5 `<video>` instead of an `<img>`, keeping caption
numbering and cross-references), `_static/video-figure.js` (no native controls; click, `Space` or
`Enter` toggles play/pause, and videos pause while off-screen) and the matching rules in
`_static/quadriga.css` (responsive sizing, pointer cursor, play icon in the caption).

Videos autoplay muted in a loop, like the animated GIFs they replace. That means the motion starts
without user interaction; a click, `Space` or `Enter` stops it. Keep animations short and essential,
and make sure the caption (`alt` text plus the visible caption) describes what the animation shows,
because the motion itself is not accessible to screen readers.

`_config.yml` is book-specific and not managed by the scaffold, so each OER has to register both
pieces itself:

```yaml
sphinx:
  local_extensions:
    video_figure: _ext
  config:
    html_js_files:
      - carousel.js
      - video-figure.js
```

After that a figure works like any other, only with a video file as the target:

````markdown
```{figure} assets/beispiel.mp4
---
align: center
width: 100%
alt: Beschreibung der Animation für Screenreader.
---
Bildunterschrift der Animation.
```
````

Prefer videos over animated GIFs: at the same quality an MP4 is roughly 20 times smaller, which
keeps the GitHub Pages deployment fast. Converting an existing GIF:

```bash
ffmpeg -i eingabe.gif -an -c:v libx264 -preset slow -crf 23 \
  -pix_fmt yuv420p -movflags +faststart ausgabe.mp4
```

## Enabling Mermaid diagrams in an OER

Diagrams can be written as [Mermaid](https://mermaid.js.org/) instead of being exported as SVG or
PNG. They are versionable, diffable and reviewable as text, and no separate source file has to be
maintained. `_static/quadriga.css` styles them like figures instead of code blocks (no background,
no border, natural height).

`_config.yml` is book-specific and not managed by the scaffold, so each OER has to register the
extension and the sizing itself. Add `sphinxcontrib-mermaid` to `requirements.in` first, then
configure the extension:

```yaml
sphinx:
  extra_extensions:
    - sphinxcontrib.mermaid
  config:
    # keep the SVG's aspect ratio instead of the 500px viewport that
    # sphinxcontrib-mermaid uses by default
    mermaid_height: auto
    # the fullscreen button overlaps small diagrams
    mermaid_fullscreen: false
```

Then a diagram is just a directive:

````markdown
```{mermaid}
:align: center
:caption: Flussdiagramm: Einstieg, Inhaltskapitel, Reflexion und Resümee, Abschluss.

graph LR
    A[Einstieg] --> B[Inhaltskapitel] --> C[Reflexion und Resümee] --> D[Abschluss]
```
````

Because the diagrams are rendered in the browser, they only work in the web version of a book, not
in PDF/LaTeX output.

## Troubleshooting

| Symptom | Cause | What to do |
|---|---|---|
| `? path` | A file in a managed directory is not part of the package. | Keep it if it is intentional (it stays untracked), otherwise move or delete it. |
| `! dir/ (N files inside)` | The manifest deletes a directory that is not empty. | Remove the remaining files yourself, then re-run `--update`. |
| `! path (symlink)` | The tracked path, or a parent directory, is a symlink. | Replace the link with a regular file/directory, then re-run `--update`. |
| `M` for a file you edited | Local customization of a managed file. | Move the customization to a book-specific file, or accept that `--update` overwrites it. |
| Exit code `2` | The manifest does not match the packaged `data/` tree. | Read the validation warnings printed on stderr and fix the manifest or `data/`. |
| No output, exit code `0` | The OER is in sync. | Nothing to do. |

## Structure of the repo

The package lives under `src/quadriga_scaffolding/`:

- `scaffold.py` — core logic (parsing and validating the manifest, diffing the OER, rendering
  diffs, applying updates).
- `cli.py` — command-line entry point (`scaffold` console script).
- `__main__.py` — enables `python -m quadriga_scaffolding`.
- `data/` — a mirror of the files that are common to all OERs. **These ship with the installed
  package.**
  - `data/scaffold.txt` — manifest listing files/directories to be created or overwritten (lines
    starting with `+ `) and deleted (lines starting with `- `).
  - `data/quadriga/` — the metadata and assessment helper package.
  - `data/_static/` — shared CSS and JavaScript.
  - `data/_ext/` — Sphinx extensions.
  - `data/.github/workflows/` — shared GitHub Actions.

Tests live under `tests/`.

Version and citation metadata live next to it: `pyproject.toml` (package version), `CITATION.cff`
(citation metadata), `.zenodo.json` (Zenodo record for each release) and `CHANGELOG.md`.

## Releases

Releases are tagged `vMAJOR.MINOR.PATCH` and archived on Zenodo, which mints a DOI for every
version. The checklist for cutting one — bumping the version, tagging on `main`, publishing the
release and adding the DOI — is in [`RELEASING.md`](RELEASING.md).

## Citation

[`CITATION.cff`](CITATION.cff) holds the citation metadata for this software; GitHub's *Cite this
repository* button and most reference managers read it. [`.zenodo.json`](.zenodo.json) describes the
Zenodo record that is created for each release.

If you use `scaffold` in a publication or in teaching material, please cite the version you used.
The Zenodo record lists all versions under one concept DOI.

## Development checks

With [`just`](https://github.com/casey/just):

```console
$ just check   # run all checks (ruff, mypy, pytest)
$ just ruff    # lint
$ just format  # auto-format
$ just mypy    # type-check
$ just test    # tests
```

Or with `uv`:

```console
$ uv run pytest          # tests
$ uv run ruff check .    # lint
$ uv run ruff format .   # auto-format
$ uv run mypy            # type-check
```
