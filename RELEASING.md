# Releasing

Every release does two things: GitHub gets a tag and a release, and Zenodo archives that release
and mints a DOI. The DOI only exists after the release has been published, so the very first release
is a release candidate (`v1.0.0-rc.1`): it validates the metadata and yields the concept DOI that
the final release cites in `README.md` and `CITATION.cff`.

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

## 3. Add the DOI (second pull request)

- [ ] Copy the **concept DOI** (the one that resolves to the latest version) from the Zenodo record.
- [ ] In `CITATION.cff`, add the DOI as `doi` and as an entry in `identifiers`.
- [ ] In `README.md`, add the Zenodo badge and the DOI to the *Citation* section.
- [ ] Merge, then repeat step 1 with `version = "1.0.0"` and publish `v1.0.0` in step 2. The concept
      DOI stays the same, so the README and `CITATION.cff` do not need to change again.

## Notes

- `.zenodo.json` takes precedence over `CITATION.cff` for the Zenodo record; `CITATION.cff` is what
  GitHub's *Cite this repository* button and reference managers read. Their shared fields (title,
  authors, licence, keywords, abstract/description) must stay consistent.
- Do not put a DOI into `.zenodo.json`. Zenodo assigns it, and a hard-coded value would be wrong for
  the next version.
- A Zenodo record cannot be deleted, only superseded by a new version. If a release fails because of
  its metadata, fix the files and publish the next version.
- Zenodo only archives releases that are created *after* the repository has been enabled in Zenodo.
