from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from tools.profiles.loader import resolve_profile
from tools.profiles.model import ProfileCatalog, ProjectProfile

IGNORED_NAMES = {
    ".git",
    ".generated",
    ".dist",
    ".report",
    ".runtime",
    ".venv",
    ".pytest_cache",
    "__pycache__",
    "coverage",
    "dist",
    "node_modules",
    "target",
}


class GenerationError(RuntimeError):
    """Raised when a scaffold target cannot be prepared safely."""


@dataclass(frozen=True, slots=True)
class ScaffoldPlan:
    project_root: Path
    target_dir: Path
    profile: ProjectProfile
    paths: tuple[Path, ...]


def build_scaffold_plan(
    catalog: ProfileCatalog,
    *,
    project_root: Path,
    target_dir: Path,
    profile_id: str,
) -> ScaffoldPlan:
    root = project_root.resolve()
    target = target_dir.resolve()
    profile = resolve_profile(catalog, profile_id)
    relative_paths = _ordered_relative_paths(catalog, profile)
    source_paths = tuple(root / relative for relative in relative_paths)

    _validate_sources(source_paths, root)
    _validate_target(root, target)

    return ScaffoldPlan(
        project_root=root,
        target_dir=target,
        profile=profile,
        paths=source_paths,
    )


def scaffold_project(plan: ScaffoldPlan, *, dry_run: bool = False) -> None:
    if dry_run:
        return

    plan.target_dir.mkdir(parents=True, exist_ok=True)

    for source in plan.paths:
        destination = plan.target_dir / source.relative_to(plan.project_root)
        if source.is_dir():
            shutil.copytree(source, destination, dirs_exist_ok=True, ignore=_ignore_transient_content)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

    _write_project_profile(plan.target_dir, plan.profile)
    _write_frontend_profile_module(plan.target_dir, plan.profile)


def render_project_profile(profile: ProjectProfile) -> str:
    feature_lines = ", ".join(f'"{feature}"' for feature in profile.features)
    return (
        f"schema_version = {profile.schema_version}\n"
        f'id = "{profile.profile_id}"\n'
        f'name = "{profile.name}"\n'
        f'description = "{profile.description}"\n'
        f"features = [{feature_lines}]\n"
    )


def render_frontend_profile_module(profile: ProjectProfile) -> str:
    feature_lines = ", ".join(f'"{feature}"' for feature in profile.features)
    return (
        f'export const activeProfileId = "{profile.profile_id}";\n'
        f'export const activeProfileName = "{profile.name}";\n'
        f"export const enabledFeatures = [{feature_lines}] as const;\n"
        f"export type ProjectFeature = (typeof enabledFeatures)[number];\n\n"
        "const featureSet = new Set<string>(enabledFeatures);\n\n"
        "export function hasFeature(feature: string): boolean {\n"
        "  return featureSet.has(feature);\n"
        "}\n"
    )


def _ordered_relative_paths(catalog: ProfileCatalog, profile: ProjectProfile) -> tuple[Path, ...]:
    ordered: list[Path] = []
    seen: set[Path] = set()

    def add(relative: str) -> None:
        path = Path(relative)
        if path in seen:
            return
        ordered.append(path)
        seen.add(path)

    for relative in catalog.core_paths:
        add(relative)
    for feature_id in profile.features:
        for relative in catalog.features[feature_id].paths:
            add(relative)

    return tuple(ordered)


def _validate_sources(source_paths: tuple[Path, ...], project_root: Path) -> None:
    missing = [path.relative_to(project_root).as_posix() for path in source_paths if not path.exists()]
    if missing:
        raise GenerationError(f"Scaffold source path(s) are missing: {', '.join(missing)}.")


def _validate_target(project_root: Path, target_dir: Path) -> None:
    if target_dir == project_root:
        raise GenerationError("Refusing to scaffold into the template repository root.")

    if project_root in target_dir.parents:
        relative = target_dir.relative_to(project_root)
        if relative.parts and relative.parts[0] != ".generated":
            raise GenerationError(
                "Refusing to scaffold into an arbitrary subdirectory of the template repository. "
                "Use '.generated/<profile-id>' or an external target directory."
            )

    if target_dir.exists() and any(target_dir.iterdir()):
        raise GenerationError(f"Target directory is not empty: {target_dir}")


def _ignore_transient_content(_directory: str, names: list[str]) -> list[str]:
    ignored: list[str] = []
    for name in names:
        if name in IGNORED_NAMES or name.endswith((".pyc", ".pyo")):
            ignored.append(name)
    return ignored


def _write_project_profile(target_dir: Path, profile: ProjectProfile) -> None:
    path = target_dir / "project-profile.toml"
    path.write_text(render_project_profile(profile), encoding="utf-8", newline="\n")


def _write_frontend_profile_module(target_dir: Path, profile: ProjectProfile) -> None:
    frontend_dir = target_dir / "frontend" / "src"
    if not frontend_dir.exists():
        return
    module_path = frontend_dir / "project-profile.ts"
    module_path.write_text(render_frontend_profile_module(profile), encoding="utf-8", newline="\n")
