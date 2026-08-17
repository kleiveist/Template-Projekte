# Coding Agent Governance

These instructions apply to every coding agent working in this repository or in a project generated from it. Follow the existing repository architecture and the policy in `config/code-quality.toml`.

## Source-size limits

1. Never create or extend a handwritten source file beyond 900 code lines. Blank lines and comment-only lines do not count toward this limit.
2. Treat 900 code lines as a hard maximum, never as a target. A file with 900 code lines is permitted; a file with 901 is an error.
3. Evaluate every file above 600 code lines for a cohesive split before extending it.
4. Normally refactor a file above 750 code lines before adding significant functionality.
5. Respect the configured limits for functions, classes, complexity, nesting, and parameter count as well as the file limit. Passing the file-size check alone does not make code clean.

## Architecture and implementation

6. Existing repository architecture takes precedence over implementation convenience. Do not invent empty layers or replace established boundaries without an explicit architecture decision.
7. Prefer existing modules, contracts, and abstractions over duplicate utilities.
8. Keep routers, controllers, adapters, Tauri commands, and composition roots thin. They validate or translate input, delegate work, and translate output.
9. Put business rules and reusable product behavior in the appropriate application service or domain module, not in transport, framework, database, UI, or native-platform adapters.
10. Keep domain code framework-neutral. Depend on domain-owned contracts at infrastructure boundaries.

## Quality policy

11. Never disable or weaken lint, formatting, type, architecture, test, or quality rules merely to complete a task or make CI pass.
12. Do not add inline quality-ignore comments as a substitute for a policy decision.
13. Do not add a quality exception without a specific, documented architectural reason and an expiry date. Prefer a path-aware generated-output exclusion for generated files.
14. Resolve a genuine violation by refactoring when practical. Do not hide existing violations behind broad excludes or exceptions.

## Required verification

15. Run `python tools/control.py quality` after structural code changes and before hand-off.
16. Run the relevant automated tests after the quality gate. Expand to the full applicable suite when a change crosses subsystem boundaries.
17. Report any quality finding or test failure that remains unresolved; do not describe a partial or suppressed result as passing.

See `docs/def/code-quality.md` for the complete thresholds, rule catalog, architecture boundaries, exception format, and CI behavior.
