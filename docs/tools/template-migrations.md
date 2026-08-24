<!-- AUTO-GENERATED:backlink START -->
[← Back](tools.md)
<!-- AUTO-GENERATED:backlink END -->
# Template migrations

| Field | Value |
| --- | --- |
| Status | Active |
| Owner | Project team |
| Last review | 2026-08-23 |
| Audience | Template maintainers and migration authors |
| Related ATP | [ATP-0001](../atp/completed/ATP-0001-template-lifecycle.md) |

## Purpose

This document defines the controlled registry for structural changes that a three-way file merge cannot describe safely, such as a known template path move or a versioned configuration-key transformation.

## Scope

### Included

- deterministic migration selection and ordering;
- declarative staging-tree operations;
- preconditions, postconditions, and idempotence checks;
- integration with update planning, state, reports, and rollback; and
- authoring and verification rules for future template migrations.

### Excluded

- arbitrary Python or shell hooks;
- product business-data or user-data transformation;
- Alembic or another product database migration;
- network access, Git history changes, or external service calls;
- automatic profile changes; and
- concrete SunoDM, FMDFlashcard, or BlobFin migrations.

## Why a registry is required

BASE/LOCAL/INCOMING comparison handles ordinary additions, updates, deletions, and text merges. It cannot infer intent when a template deliberately renames a path, splits a configuration file, or changes a known schema key. Treating such a change as an unrelated deletion and addition can discard local edits or create false collisions.

A registered structural migration supplies that intent before the final merge is applied. It remains a template migration, not permission to modify product-owned data.

## Migration contract

Each migration declares:

| Field | Requirement |
| --- | --- |
| ID | Stable, globally unique, and never reused |
| Description | Concise explanation of the structural change |
| Source | Supported starting template version or revision range |
| Target | Supported target version or revision range |
| Order | Deterministic relative order |
| Preconditions | Facts that must be true before any operation |
| Operations | Ordered declarative transformations |
| Postconditions | Facts that must be true after all operations |
| Idempotence | A second evaluation must not repeat or corrupt the change |

Duplicate IDs are a verification failure. A migration already listed in `applied_migrations` is not run again. Successful IDs are recorded only after the complete update succeeds.

## Supported operation types

The first registry may expose these constrained operations:

| Operation | Intended use |
| --- | --- |
| `move_path` | Move a known template path and preserve mapped local changes |
| `copy_path` | Copy a known staged template path |
| `delete_path` | Remove a declared obsolete template path |
| `rename_key` | Rename a known key in supported structured configuration |
| `set_default` | Add a default only when the key is absent |
| `transform_json` | Apply a bounded JSON transformation |
| `transform_toml` | Apply a bounded TOML transformation |
| `transform_text` | Apply a deterministic, declared text transformation |
| `record_notice` | Add a non-mutating migration notice to the report |

Operations validate every relative path before use. They must not follow a link outside the staging root, escape through `..`, use an absolute or drive-qualified path, overwrite an undeclared product-owned path, or access protected runtime areas.

## Execution order

The planner selects migrations applicable to the recorded baseline and resolved target commit. The update pipeline then uses this order:

```text
resolve target
    -> reconstruct BASE and INCOMING
    -> select and validate migrations
    -> copy product into isolated staging
    -> run migration operations in deterministic order
    -> apply path mappings to three-way planning
    -> materialize merge results in staging
    -> verify migration postconditions and staged product
    -> transactionally replace product files
    -> record migration IDs in lifecycle state last
```

Migration IDs must appear in the plan and report before apply. A failed precondition, operation, postcondition, or idempotence check blocks the entire update.

## Path moves and product edits

A declared path move maps the old template-managed path to the new path during comparison. The planner uses the recorded baseline to distinguish template content from local product edits. Local edits follow the mapping and participate in the same three-way conflict rules at the destination.

The migration does not overwrite an unrelated product-owned destination. If the destination already contains a product-added file, planning reports a conflict and apply changes nothing.

## State and rollback

`applied_migrations` is part of the tracked lifecycle state. The list changes only after:

1. every migration completes in staging;
2. all merge operations complete;
3. lifecycle and product verification pass;
4. product paths are applied successfully; and
5. the new baseline manifest is ready.

If any later step fails, the transaction restores product files and both lifecycle files. The failed migration ID remains absent. A report may remain under `.report/template-lifecycle/` for diagnosis.

## Security boundary

Migration code and declarations must not:

- invoke a shell, subprocess, package script, or arbitrary executable;
- access the network or fetch template history;
- read or write environment secrets;
- inspect or copy `.env` files into reports;
- modify `.git`, commits, branches, tags, remotes, or hooks;
- write outside staging and the validated target root;
- change product/user data, local databases, uploads, caches, or runtime artifacts; or
- silently change the selected profile or capabilities.

The registry is intentionally less powerful than a general scripting system. A change that cannot be represented safely must remain a documented manual product migration.

## Authoring procedure

1. Give the migration one stable, descriptive ID.
2. Bind it to explicit source and target template revisions or versions.
3. Define the minimum preconditions needed to distinguish the expected old structure.
4. Choose only supported declarative operations.
5. Define observable postconditions and an idempotence check.
6. Add synthetic fixture tests for success, already-applied behavior, failure, and rollback.
7. Test local modifications at moved paths and destination collisions.
8. Test path traversal, external symlink, protected-path, and shell-execution rejection.
9. Document any architecture change and update the lifecycle ATP mapping.

Do not use a production product repository as the first migration fixture. Lifecycle tests create isolated local Git repositories and synthetic product trees without network access.

## Verification

Focused tests must prove:

- IDs are unique and ordering is deterministic;
- a successful migration is recorded once;
- repeated execution is a no-op;
- a failed migration is not recorded;
- local edits survive declared moves or produce a conflict;
- operations cannot escape staging or invoke a shell;
- state is written last; and
- a postcondition or final verify failure triggers complete rollback.

Run the public gates from the repository root:

```sh
python tools/control.py quality
python tools/control.py test --suite tools
python tools/control.py docs check
```

## Risks and limitations

- The initial registry contains no product-specific migration.
- A registry entry cannot replace review of a product's persistence and user-data boundaries.
- Downgrades are rejected unless an explicit supported migration describes them.
- General profile migration and automatic conflict resolution are not available.

## Related documents

- [Template lifecycle](../def/template-lifecycle.md)
- [Framework architecture](../def/architecture.md)
- [Project profiles](../def/project-profiles.md)
- [Database feature](../def/database-feature.md)
- [Tooling Guide](tooling.md)
- [Lifecycle acceptance](../dev/template-lifecycle-acceptance.md)
- [ATP-0001](../atp/completed/ATP-0001-template-lifecycle.md)
