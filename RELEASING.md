# Releasing

Every release does two things: GitHub gets a tag and a release, and Zenodo archives that release
and mints a DOI. A DOI cannot be reserved before the release exists, which is why the first release
was a release candidate (`v1.0.0-rc.1`): it validated the metadata and produced the concept DOI that
`README.md` and `CITATION.cff` now cite for all versions.

## Version numbering

- Tags are `vMAJOR.MINOR.PATCH`, release candidates `vX.Y.Z-rc.N`.
- The version is maintained in exactly two files: `pyproject.toml` and `CITATION.cff`.
- `.zenodo.json` deliberately carries no `version` (and no `publication_date`): Zenodo takes both
  from the release, so the file stays correct across versions.

## 1. Prepare the release (pull request)

- [ ] Start from an up-to-date `main` and create a release branch.
- [ ] Run `just check` and make sure it is green.
- [ ] Set the new version in `pyproject.toml` and in `CITATION.cff` (`version`, `date-released`).
- [ ] Move the `Unreleased` entries in `CHANGELOG.md` under the new version heading and add the
      compare links for the new tag.
- [ ] Commit as `chore(release): prepare vX.Y.Z`, open a pull request and merge it.

## 2. Publish the release (on `main`)

Tags are created on `main`, after the release pull request has been merged.

- [ ] `git switch main && git pull`
- [ ] `git tag -a vX.Y.Z -m "vX.Y.Z" && git push origin vX.Y.Z`
- [ ] Create the GitHub release from that tag, using the changelog section as the release notes.
      For a release candidate, tick **Set as a pre-release**.
- [ ] Check the new record under <https://zenodo.org/account/settings/github/>: title, creators,
      affiliation, licence, language, keywords and description. Zenodo may take a few minutes.

Zenodo archives release candidates as well. That is intentional here: the RC exists to prove that
the metadata validates and to get the DOI before the final release.

## 3. The DOI is already in place

`README.md` and `CITATION.cff` cite the Zenodo **concept DOI** (`10.5281/zenodo.24200612`), which
always resolves to the latest release, so neither file has to change for a new version. Every
release additionally gets its own version DOI, which is listed on the Zenodo record only.

Only the first archived release had to add it (done for `v1.0.0-rc.1`):

- The concept DOI is listed on the Zenodo record under *Cite all versions*; the DOI of the single
  record is the version DOI and must not be used for this purpose.
- It is set as `doi` in `CITATION.cff` and as the badge plus citation example in `README.md`.

## Notes

- `.zenodo.json` takes precedence over `CITATION.cff` for the Zenodo record; `CITATION.cff` is what
  GitHub's *Cite this repository* button and reference managers read. Their shared fields (title,
  authors, licence, keywords, abstract/description) must stay consistent.
- Do not put a DOI into `.zenodo.json`. Zenodo assigns it, and a hard-coded value would be wrong for
  the next version.
- `communities` in `.zenodo.json` does not add the record to the QUADRIGA community on its own: the
  community has a closed review policy. Add the published record to the community manually (or ask
  a community curator) after the release has been archived.
- A Zenodo record cannot be deleted, only superseded by a new version. If a release fails because of
  its metadata, fix the files and publish the next version.
- Zenodo only archives releases that are created *after* the repository has been enabled in Zenodo.
