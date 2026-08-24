<!-- AUTO-GENERATED:backlink START -->
[← Back](README.md)
<!-- AUTO-GENERATED:backlink END -->
# Contributing

Thank you for helping improve this full-stack project template. This guide applies to changes made to the master template. Product projects generated from it own their product behavior, deployment, data, and community policies.

Please read and follow the [Code of Conduct](CODE_OF_CONDUCT.md) in every project space.

## Choose the right channel

Use public GitHub Issues for reproducible bugs and feature requests. Search existing issues before opening a new one, then use the appropriate Issue Form.

Do not report a security vulnerability in a public issue. Follow the private reporting route in the [Security Policy](.github/SECURITY.md). The confidential address in that policy is only for security and Code-of-Conduct incidents; it is not a support channel. Normal support questions belong in public GitHub Issues so that answers can help other users.

## Local development

Run commands from the repository root. The normal preparation sequence is:

```sh
python tools/control.py doctor
python tools/control.py install
```

The baseline requires Git, Python 3.11 or newer, and Node.js 24 or newer with npm. Desktop work also requires Rust Stable and the applicable [Tauri prerequisites](https://v2.tauri.app/start/prerequisites/). Docker is needed only for container workflows, and PostgreSQL is needed only when testing the optional `postgres` capability against a reachable service.

`tools/control.py` is the public, profile-aware entry point. It detects the active project profile and runs checks only for enabled components.

## Profiles

| Profile | Intended project shape |
| --- | --- |
| `web-only` | Vite and TypeScript browser application |
| `web-cloud` | Browser application with a FastAPI backend and cloud boundaries |
| `desktop-local` | Tauri desktop application with the shared frontend |
| `desktop-cloud` | Tauri desktop client with a FastAPI backend and cloud boundaries |
| `full-platform` | Browser, backend, cloud, and desktop surfaces together |

`postgres` is an optional capability for backend-enabled profiles. It is incompatible with `web-only` and `desktop-local`.

## Verified development commands

Use the smallest relevant command while developing, then run the complete applicable gate before requesting review.

| Purpose | Command |
| --- | --- |
| Inspect tools, profile, dependencies, and ports | `python tools/control.py doctor` |
| Install profile-relevant dependencies | `python tools/control.py install` |
| Start enabled local services | `python tools/control.py run` |
| Run all applicable automated tests | `python tools/control.py test --suite all` |
| Run the complete quality and architecture gate | `python tools/control.py quality` |
| Check formatting | `python tools/control.py quality format` |
| Run linting and profile-relevant type/compiler checks | `python tools/control.py quality lint` |
| Build the web artifact | `python tools/control.py build web` |
| Validate a cloud-profile container model | `python tools/control.py container validate` |
| Check desktop prerequisites | `python tools/control.py tauri doctor` |
| Preview and regenerate documentation navigation | `python tools/control.py docs index --dry-run` and `python tools/control.py docs index` |
| Validate documentation navigation | `python tools/control.py docs check` |

For desktop artifacts, use `python tools/control.py build desktop` only in a desktop-enabled profile. For focused test suites and profile-specific commands, consult the [Tooling Guide](docs/tools/tooling.md).

## Branches, commits, and pull requests

There is no mandatory branch-name or commit-message convention in this repository, and Conventional Commits are not required. Create a focused branch from current `main`, use a concise commit subject that explains the change, and keep unrelated work out of the same pull request.

1. Search existing issues and open or reference the relevant issue when practical.
2. Explain the intended scope before beginning substantial work, especially for architecture, profile, or migration changes.
3. Make the smallest coherent change. Keep profile-specific behavior behind the existing profile and feature boundaries.
4. Add or update automated tests and English documentation together with the change.
5. Run the relevant checks. Before hand-off, run `python tools/control.py quality` and the applicable test suite.
6. Open a pull request using the repository template, describe the evidence, and respond to review feedback.

## Tests, documentation, and compatibility

Tests must cover behavior that changes. Update the affected documentation in English, including commands, profiles, architecture, and acceptance evidence where relevant. Do not weaken quality rules, hide violations, or add broad exceptions to make a change pass.

Call out breaking changes and required migrations in the pull request. Template lifecycle changes must preserve product ownership and follow the documented [template lifecycle](docs/def/template-lifecycle.md) and [migration rules](docs/tools/template-migrations.md). A change that affects generated projects must identify its effect on every applicable profile.

## Review and acceptance

Reviewers look for a focused scope, correct profile behavior, relevant tests, a passing quality gate, accurate documentation, safe handling of secrets, and a clear migration story. A check that does not apply may be marked as not applicable in the pull request with a short reason; it must not be represented as having run.

## License for contributions

By submitting a contribution, you agree that it may be distributed under this repository's [MIT License](LICENSE).

## Derived projects

Before a generated project accepts contributions or is published, its maintainers must review the inherited repository description, license, and copyright owner. They must create product-owned contribution, security, Code-of-Conduct, and community governance and define their own support and security scope.
