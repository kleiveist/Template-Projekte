## Summary

Describe the change and its user-visible or maintainer-visible result.

## Motivation and linked issue

Explain why this change is needed and link the relevant issue when one exists.

## Change type

- [ ] Bug fix
- [ ] Feature or enhancement
- [ ] Documentation or tooling
- [ ] Refactor or maintenance
- [ ] Breaking change or migration

## Affected components and profiles

List the affected components and project profiles: `web-only`, `web-cloud`, `desktop-local`, `desktop-cloud`, `full-platform`, optional `postgres`, or shared tooling.

## Validation performed

Record each applicable command and its result. Mark a command not applicable only with a short reason.

| Command | Result or not-applicable reason |
| --- | --- |
| `python tools/control.py quality` | |
| `python tools/control.py test --suite all` | |
| `python tools/control.py build web` | |
| `python tools/control.py docs check` | |

## Manual testing

Describe the manual checks performed, including affected operating systems, browsers, desktop environments, or configuration where relevant.

## Screenshots or recordings

Attach screenshots or recordings for user-interface changes, or state why they do not apply.

## Documentation

List updated documentation, or explain why documentation does not need to change.

## Breaking changes and migrations

Describe compatibility impact, migration steps, and rollback considerations, or state that none are expected.

## Security impact

Describe security implications, including any review of secrets, permissions, dependencies, or trust boundaries. Do not disclose vulnerabilities publicly; follow the [Security Policy](https://github.com/kleiveist/Template-Projekte/security/policy).

## Author checklist

- [ ] This pull request has a focused scope and does not include unrelated changes.
- [ ] I followed the [contribution guide](https://github.com/kleiveist/Template-Projekte/blob/main/CONTRIBUTING.md) and [Code of Conduct](https://github.com/kleiveist/Template-Projekte/blob/main/CODE_OF_CONDUCT.md).
- [ ] I recorded the applicable validation evidence above, including any not-applicable reason.
- [ ] I added or updated relevant tests and English documentation, or explained why neither applies.
- [ ] I documented breaking changes or migrations when applicable.
- [ ] I did not add secrets, credentials, or unnecessary personal data.
