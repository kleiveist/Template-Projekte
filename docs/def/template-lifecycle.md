<!-- AUTO-GENERATED:backlink START -->
[← Back](def.md)
<!-- AUTO-GENERATED:backlink END -->
# Template lifecycle

| Field | Value |
| --- | --- |
| Status | Active |
| Owner | Project team |
| Last review | 2026-08-23 |
| Audience | Template maintainers and product maintainers |
| Related ATP | [ATP-0001](../atp/completed/ATP-0001-template-lifecycle.md) |

## Purpose

This document defines how a generated or adopted product records template provenance, compares itself with another template revision, and applies safe template changes without taking ownership of product code, product identity, product version, or user data.

## Scope

### Included

- deterministic lifecycle state and baseline manifests;
- generation, status, audit, adoption, planning, update, and verification;
- a local Git template source and exact commit resolution;
- BASE/LOCAL/INCOMING comparison and conflict handling;
- versioned structural template migrations;
- transactional apply and rollback; and
- human-readable and machine-readable reports.

### Excluded

- remote resolution, automatic fetches, or GitHub API access;
- pull-request, commit, push, merge, tag, release, or publication automation;
- product-specific or database-data migrations;
- automatic profile or capability changes; and
- automatic resolution of ambiguous conflicts.

## Lifecycle model

```text
local template source
    |-- init  -> generated product with provenance
    |-- audit -> read-only legacy comparison
    |-- adopt -> managed product state
    |-- plan  -> deterministic operations and conflicts
    `-- update -> staged, verified, transactional apply
                         |
                         `-- verify
```

Template version and product version are independent:

| Value | Location | Meaning |
| --- | --- | --- |
| Product version | Product root `VERSION` and enabled component mirrors | The product's release version |
| Template version | `.template/state.toml` under `source.version` | Human-readable template release classification |
| Template commit | `.template/state.toml` under `source.commit` | Exact technical provenance and comparison identity |

A lifecycle update never invokes `version sync` and never changes the product version to the template version. Before comparison, reconstructed scaffolds are normalized to the product's current version and recorded identity. Two template revisions with the same template version but different commits are distinct.

## Tracked state

Every managed product commits these files:

```text
.template/
├── state.toml
└── baseline.json
```

Temporary worktrees, staging data, journals, and reports do not belong under `.template/`.

### State schema

`state.toml` uses a versioned schema and records:

- repository kind and canonical template ID;
- provenance as `generated`, `adopted`, or `working-tree`;
- whether the source template worktree was dirty;
- canonical source identifier, template SemVer, resolved ref, full 40-character commit, and scaffold digest;
- selected profile, optional capabilities, and fully resolved features;
- product display name, slug, application identifier, and binary name; and
- baseline manifest path, digest, and successfully applied migration IDs.

The file contains no local absolute paths, timestamps, random identifiers, secrets, or user data. A full commit, not a moving branch name, is stored as the installed revision.

### Baseline manifest

`baseline.json` contains one sorted entry per template-managed scaffold file. Each entry has a relative path, SHA-256, byte size, content kind, and executable flag. The manifest also has a schema version and a digest over its canonical content.

It contains hashes and metadata, never file contents. Paths must remain inside the project root. Broken links and symbolic links that resolve outside the root are rejected. The manifest excludes lifecycle metadata and protected runtime content.

The ownership rule is dynamic:

```text
path in baseline manifest      -> template-managed baseline path
path absent from the manifest -> product-owned path
```

Product-owned paths are not added to an update plan merely because they exist. `.env.example` remains template-managed when present in the baseline, while real environment files, virtual environments, dependencies, build output, reports, caches, Git metadata, runtime data, local databases, credentials, and detected user data remain protected.

## Generation provenance

`init` writes lifecycle metadata only after copying the scaffold, removing master-only content, writing the active profile, configuring capabilities and environment examples, applying product identity, and normalizing product metadata. The resulting baseline therefore describes the product-shaped scaffold rather than the unconfigured master tree.

`init --dry-run` writes no files. A clean template checkout records `provenance = "generated"` and `source_dirty = false`. A development generation from uncommitted template content records `provenance = "working-tree"`, `source_dirty = true`, and a digest of the actual scaffold. Such a baseline is inspectable but cannot be used for automatic update apply; re-adopt the product against a trusted clean commit first.

## Local source resolution

Version 1 accepts a local template checkout through `--source-dir`. The resolver:

- requires a Git repository with the expected template identity;
- normalizes the configured origin when one exists;
- resolves a requested ref to a full commit;
- requires both baseline and target commits to exist locally;
- does not fetch or access the network;
- does not switch branches or modify the source worktree; and
- reports an actionable error when required history is unavailable.

A branch name may be supplied for planning, but the plan and state contain only its resolved commit. Apply resolves the input again and rejects a branch that moved after planning.

Detached temporary worktrees reconstruct the generator at the baseline and target commits. Cleanup runs after success and failure. Subprocesses receive argument lists and never use `shell=True`.

## Commands

A bare command displays the complete group help and returns success without changing files:

```sh
python tools/control.py template
```

### Status

```sh
python tools/control.py template status
python tools/control.py template status \
  --source-dir ../Template-Projekte \
  --to-ref <trusted-template-tag-or-sha> \
  --format json
```

Status is read-only. It reports installed provenance, template commit and version, product version, profile and capabilities, manifest validity, managed-file drift, and product-owned file counts. With a local source and target ref, it also reports the resolved target and whether an update is available.

### Audit

```sh
python tools/control.py template audit \
  --target-dir ../LegacyProduct \
  --source-dir . \
  --to-ref <trusted-template-tag-or-sha> \
  --profile <profile-id> \
  --name "<Product Name>" \
  --slug <product-slug> \
  --identifier <reverse-domain-identifier>
```

Audit works without lifecycle state. It compares a legacy tree with the selected target scaffold, inventories overlaps and product files, and identifies missing template components and potential conflicts. It changes no tracked product file. An optional report directory is the only permitted output.

### Adopt

```sh
python tools/control.py template adopt \
  --target-dir ../Product \
  --source-dir . \
  --baseline-ref <trusted-template-tag-or-sha> \
  --profile <profile-id> \
  --name "<Product Name>" \
  --slug <product-slug> \
  --identifier <reverse-domain-identifier> \
  --apply
```

Adoption requires an explicit baseline ref and, for apply, a completely clean product worktree. It reconstructs the declared baseline and writes only `.template/state.toml` and `.template/baseline.json` with `provenance = "adopted"`. Existing differences remain product changes. Adoption is metadata onboarding, not a product migration. Without `--apply`, it is a preview and writes no lifecycle files.

### Plan and update

```sh
python tools/control.py template plan \
  --target-dir ../Product \
  --source-dir . \
  --to-ref <trusted-template-tag-or-sha>

python tools/control.py template update \
  --target-dir ../Product \
  --source-dir . \
  --to-ref <trusted-template-tag-or-sha> \
  --apply
```

`plan` and `update` without `--apply` are read-only previews. A plan contains `ADD`, `UPDATE`, `MERGE`, `DELETE`, `MOVE`, `PRESERVE`, `CONFLICT`, and `STATE_UPDATE` operations as applicable. At least one unresolved conflict makes planning return a non-zero status and prevents apply.

### Verify

```sh
python tools/control.py template verify
```

Verification is local and offline. It checks state and manifest schemas, full commit format, template identity, digests, safe paths, profile and capability consistency, resolved features, product identity, product version mirrors, known and unique migration IDs, lifecycle files, dirty-baseline restrictions, and baseline-file integrity. Identity drift is reported; apply never silently rewrites it.

## Three-way planning rules

| BASE | LOCAL | INCOMING | Result |
| --- | --- | --- | --- |
| Same as incoming | Any | Same as base | Preserve local; no operation |
| Same as local | Same as base | Changed | Apply incoming |
| Any | Same as incoming | Same as local | No operation |
| Changed locally | Different from incoming | Unchanged from base | Preserve local |
| Changed locally | Changed locally | Changed compatibly | Record a three-way merge |
| Changed locally | Changed locally | Overlapping change | Conflict; apply nothing |

An unchanged local file deleted by the template is deleted. A locally changed deleted file conflicts. A new incoming file is added only when the local path is free. Binary files are never text-merged: if both sides changed, the result is a conflict. Executable modes are compared and applied explicitly.

## Transaction and rollback

Before `update --apply`, the complete output of `git status --porcelain --untracked-files=all` must be empty. Untracked files are included because they can collide with incoming paths.

Apply performs these stages:

1. resolve and validate the target commit again;
2. recompute the complete plan;
3. reject every conflict or untracked collision;
4. create an operation journal with source and target hashes;
5. run declared migrations in an isolated staging tree;
6. materialize all merge operations in staging;
7. verify the staged product and new lifecycle state;
8. replace product files transactionally;
9. write baseline and state after product files; and
10. run lifecycle verification and roll back every changed path on failure.

No partial conflict-free subset is applied when another path conflicts. A failed update leaves product files and both lifecycle files unchanged. The ignored report may remain as diagnostic evidence.

## Reports and exit codes

The default report location is `.report/template-lifecycle/<run-id>/`. A report can contain:

- `summary.md`;
- `plan.json`;
- `changes.patch`;
- `conflicts.json`; and
- `verification.json`.

Report JSON has a versioned schema and deterministic path ordering. Reports use relative paths and exclude secrets, environment dumps, and protected file contents. A timestamp is permitted only in the ignored run directory name.

| Exit code | Meaning |
| ---: | --- |
| `0` | Help or requested operation completed without a blocking finding |
| `1` | Operational, validation, verification, migration, or conflict failure |
| `2` | Invalid CLI usage or arguments |

Expected operational errors are concise and do not print a traceback in normal mode.

## Recommended Git workflow

```sh
git clone <template-repository>
cd Template-Projekte
git checkout <trusted-template-tag-or-sha>

python tools/control.py template audit \
  --target-dir ../Product \
  --source-dir . \
  --to-ref <trusted-template-tag-or-sha>

python tools/control.py template plan \
  --target-dir ../Product \
  --source-dir . \
  --to-ref <trusted-template-tag-or-sha>

python tools/control.py template update \
  --target-dir ../Product \
  --source-dir . \
  --to-ref <trusted-template-tag-or-sha> \
  --apply
```

Review the report and product diff, rerun product checks, then create a normal product commit. The lifecycle command creates no commit.

## Verification

```sh
python tools/control.py template status
python tools/control.py template verify
python tools/control.py quality
python tools/control.py test --suite tools
python tools/control.py docs check
python tools/control.py version check
```

The active acceptance protocol records which broader profile, database, desktop, build, and rollback checks were actually executed. Implementation alone is not acceptance evidence.

## Risks and limitations

- Version 1 requires a locally available template checkout and history.
- No product-specific migration is registered by this change.
- No general profile migration is available.
- Conflicts require product-owner review and a new clean plan.
- Remote, pull-request, and release automation remain future work.

## Related documents

- [Framework architecture](architecture.md)
- [Project profiles](project-profiles.md)
- [Template migrations](../tools/template-migrations.md)
- [Tooling Guide](../tools/tooling.md)
- [Release model](../tools/release-model.md)
- [Continuous integration](../tools/ci.md)
- [Lifecycle acceptance](../dev/template-lifecycle-acceptance.md)
- [ATP-0001](../atp/completed/ATP-0001-template-lifecycle.md)
