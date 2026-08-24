<!-- AUTO-GENERATED:backlink START -->
[← Back](tools.md)
<!-- AUTO-GENERATED:backlink END -->
# Template-Projekte v1.0.0 release notes

| Field | Value |
| --- | --- |
| Version | `1.0.0` |
| Status | Candidate changes prepared and available local checks executed; clean-candidate and exact-HEAD validation pending |
| Published release tag | None |
| Intended future tag | `v1.0.0` |
| Historical architecture baseline | `461fc7519e0db638330904a7496c488e8a0d18bc` |
| Candidate review | 2026-08-24 |

## Purpose

Version 1.0.0 is the candidate for the first governed release of the reusable Template-Projekte master. It provides one profile-driven foundation for browser, cloud-backend, and Tauri desktop products. Candidate validation certifies the template and its generation paths as a commit-pinned migration basis; it does not publish a release or claim that an uncustomized derived product is production-ready.

The exact validated candidate commit is deliberately not embedded in a file that participates in that commit. GitHub Actions evidence and the final operator report record the full SHA after same-commit validation. No tag or GitHub Release currently exists; any future `v1.0.0` tag and publication record must identify that same validated commit.

## Supported project profiles

- `web-only`: Vite and TypeScript frontend;
- `web-cloud`: frontend, FastAPI backend, and provider-neutral cloud boundaries;
- `desktop-local`: frontend and local Tauri shell;
- `desktop-cloud`: frontend, FastAPI backend, cloud boundaries, and Tauri shell; and
- `full-platform`: browser, backend, cloud, and desktop surfaces together.

PostgreSQL remains an optional capability for the three backend-enabled profiles. `web-only + postgres` and `desktop-local + postgres` are rejected before generation. The valid PostgreSQL matrix exercises a real connection, Alembic migrations, database and API tests, and the central quality gate.

## Code quality and architecture governance

The public entry point is:

```sh
python tools/control.py quality
```

The policy covers repository scanning, code and physical line metrics, function and class size, complexity, nesting, parameter counts, narrow expiring exceptions, backend/frontend/tooling dependency rules, and the enabled Ruff, ESLint, Prettier, TypeScript, Cargo formatting, Clippy, and Cargo check adapters.

Rust scope and control-flow metrics use a pinned Syn 2.0.119 analyzer compiled to a portable WASI artifact and hosted by the
exact Wasmtime 47.0.1 tooling dependency. The 535,787-byte artifact has SHA-256
`7a27cb02a9392b62c487b4ce73a03524d7260b804c0c49eb4520ceb1a1cacfd8`. Provenance binds it to the exact Rust 1.97.1 compiler
commit, target and dependency versions, and a source digest over the build script, Cargo manifest and lockfile, toolchain file,
and Rust sources.

The build removes inherited compiler and profile overrides and applies a versioned, broad-to-specific path-remapping contract
for source, home, Cargo target/home, Rust sysroot, and dependency roots. Normal-registry, relocated-home/target paths containing
spaces, and in-tree-vendored builds were byte-identical on the pinned Linux builder and contained no private physical build
paths. This evidence does not claim cross-OS byte identity: Core CI and Release Validation rebuild and compare on Ubuntu, while
macOS and Windows Desktop jobs execute the checked-in artifact. Rust-free generated profiles can therefore run the same scanner
without installing a Rust toolchain, while malformed syntax, corrupt artifacts, resource failures, and invalid metric payloads
remain blocking errors.

The handwritten-source file limit is exact: 900 code lines produce a non-blocking strong warning; 901 code lines produce an unsuppressible `CQ001 ERROR` and a failing gate. Warning and strong-warning findings remain visible without being promoted to errors.

## Verification model

Candidate evidence must come from one final commit. Required GitHub checks are the six Core CI jobs, including the semantic Documentation Check, the five-profile matrix, the three-profile PostgreSQL matrix with a real PostgreSQL service, native Windows/macOS/Linux Desktop CI, and manually dispatched or tag-triggered Release Validation. The release process does not use `continue-on-error` for a required gate.

Documentation navigation is regenerated with `docs index` and verified independently with the read-only `docs check`. The bilingual case study, its four PDF editions, translation validation, and checksums are part of the release evidence.

## Upgrade and migration notes

There is no automatic in-place migration contract for projects generated before 1.0.0. Existing products should review template changes and adopt them selectively, preserving their own identity, business rules, dependencies, deployment, and data ownership decisions.

After adopting the release tooling, run:

```sh
python tools/control.py install
python tools/control.py quality
python tools/control.py version check
python tools/control.py test --suite all
```

Products that enable PostgreSQL must keep application startup separate from schema migration and run `python tools/control.py db upgrade` through an explicit deployment step. Version 1.0.0 does not introduce a template business schema or an application-data migration.

## Product work that remains product-specific

Before publishing a derived application, replace the canonical template identity and complete product requirements such as authentication, authorization, business models, provider-specific deployment, privacy declarations, observability, backups, support policy, signing, Apple notarization, and updater infrastructure. Add only the Tauri capabilities and remote origins the product actually needs.

## Related documentation

- [Release and desktop packaging model](release-model.md)
- [Continuous Integration](ci.md)
- [Code quality and architecture governance](../def/code-quality.md)
- [Project profiles](../def/project-profiles.md)
- [Template final acceptance](../dev/template-final-acceptance.md)
