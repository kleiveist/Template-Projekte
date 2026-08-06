from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.config.loader import load_contract, render_env_example
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
    env_example: str


def build_scaffold_plan(
    catalog: ProfileCatalog,
    *,
    project_root: Path,
    target_dir: Path,
    profile_id: str,
    optional_features: tuple[str, ...] = (),
) -> ScaffoldPlan:
    root = project_root.resolve()
    target = target_dir.resolve()
    profile = resolve_profile(catalog, profile_id, optional_features=optional_features)
    relative_paths = _ordered_relative_paths(catalog, profile)
    source_paths = tuple(root / relative for relative in relative_paths)
    contract = load_contract(root / "config" / "environment.toml")
    env_example = render_env_example(contract, profile.features)

    _validate_sources(source_paths, root)
    _validate_target(root, target)

    return ScaffoldPlan(
        project_root=root,
        target_dir=target,
        profile=profile,
        paths=source_paths,
        env_example=env_example,
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
    _configure_frontend_dependencies(plan.target_dir, plan.profile)
    _configure_env_example(plan.target_dir, plan.env_example)


def render_project_profile(profile: ProjectProfile) -> str:
    feature_lines = ", ".join(_quoted(value) for value in profile.features)
    optional_lines = ", ".join(_quoted(value) for value in profile.optional_features)
    return (
        f"schema_version = {profile.schema_version}\n"
        f"id = {_quoted(profile.profile_id)}\n"
        f"name = {_quoted(profile.name)}\n"
        f"description = {_quoted(profile.description)}\n"
        f"optional_features = [{optional_lines}]\n"
        f"features = [{feature_lines}]\n"
    )


def render_frontend_profile_module(profile: ProjectProfile) -> str:
    feature_lines = ", ".join(_quoted(value) for value in profile.features)
    return (
        f"export const activeProfileId = {_quoted(profile.profile_id)};\n"
        f"export const activeProfileName = {_quoted(profile.name)};\n"
        f"export const enabledFeatures = [{feature_lines}] as const;\n"
        f"export type ProjectFeature = (typeof enabledFeatures)[number];\n\n"
        "const featureSet = new Set<string>(enabledFeatures);\n\n"
        "export function hasFeature(feature: string): boolean {\n"
        "  return featureSet.has(feature);\n"
        "}\n"
    )


def _quoted(value: str) -> str:
    # JSON string syntax is valid for TOML basic strings and TypeScript literals.
    return json.dumps(value, ensure_ascii=False)


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
    outside = [path for path in source_paths if not path.resolve().is_relative_to(project_root)]
    if outside:
        raise GenerationError(f"Scaffold source path resolves outside the template repository: {outside[0]}.")

    missing = [path.relative_to(project_root).as_posix() for path in source_paths if not path.exists()]
    if missing:
        raise GenerationError(f"Scaffold source path(s) are missing: {', '.join(missing)}.")

    for source in source_paths:
        if not source.is_dir():
            continue
        for directory, dirnames, filenames in os.walk(source, topdown=True, followlinks=False):
            parent = Path(directory)
            dirnames[:] = [name for name in dirnames if not _is_ignored_name(name)]
            for name in (*dirnames, *filenames):
                if _is_ignored_name(name):
                    continue
                candidate = parent / name
                if candidate.is_symlink():
                    _validate_symlink(candidate, project_root)


def _validate_symlink(path: Path, project_root: Path) -> None:
    try:
        link_target = path.resolve(strict=True)
    except OSError as exc:
        raise GenerationError(f"Scaffold source contains a broken symbolic link: {path}.") from exc
    if not link_target.is_relative_to(project_root):
        raise GenerationError(f"Scaffold source symbolic link points outside the template repository: {path}.")


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
    return [name for name in names if _is_ignored_name(name)]


def _is_ignored_name(name: str) -> bool:
    return name in IGNORED_NAMES or name.endswith((".pyc", ".pyo"))


def _write_project_profile(target_dir: Path, profile: ProjectProfile) -> None:
    path = target_dir / "project-profile.toml"
    path.write_text(render_project_profile(profile), encoding="utf-8", newline="\n")


def _write_frontend_profile_module(target_dir: Path, profile: ProjectProfile) -> None:
    frontend_dir = target_dir / "frontend" / "src"
    if not frontend_dir.exists():
        return
    module_path = frontend_dir / "project-profile.ts"
    module_path.write_text(render_frontend_profile_module(profile), encoding="utf-8", newline="\n")


def _configure_frontend_dependencies(target_dir: Path, profile: ProjectProfile) -> None:
    if profile.has_feature("tauri"):
        return

    package_path = target_dir / "frontend" / "package.json"
    if not package_path.exists():
        return

    package = _read_json_object(package_path)
    scripts = package.get("scripts")
    if isinstance(scripts, dict):
        scripts.pop("tauri", None)
    dev_dependencies = package.get("devDependencies")
    if isinstance(dev_dependencies, dict):
        dev_dependencies.pop("@tauri-apps/cli", None)
    _write_json(package_path, package)

    lock_path = target_dir / "frontend" / "package-lock.json"
    if not lock_path.exists():
        return

    lock = _read_json_object(lock_path)
    packages = lock.get("packages")
    if isinstance(packages, dict):
        root_package = packages.get("")
        if isinstance(root_package, dict):
            root_dev_dependencies = root_package.get("devDependencies")
            if isinstance(root_dev_dependencies, dict):
                root_dev_dependencies.pop("@tauri-apps/cli", None)
        for key in list(packages):
            if key == "node_modules/@tauri-apps/cli" or key.startswith("node_modules/@tauri-apps/cli-"):
                del packages[key]
    dependencies = lock.get("dependencies")
    if isinstance(dependencies, dict):
        dependencies.pop("@tauri-apps/cli", None)
    _write_json(lock_path, lock)


def _configure_env_example(target_dir: Path, content: str) -> None:
    path = target_dir / ".env.example"
    path.write_text(content, encoding="utf-8", newline="\n")


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GenerationError(f"Could not read generated JSON file {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise GenerationError(f"Generated JSON file must contain an object: {path}")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
