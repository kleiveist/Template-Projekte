from __future__ import annotations

import re
from pathlib import Path
from pathlib import PurePosixPath, PureWindowsPath
from typing import Iterable

from tools.profiles.model import ProfileCatalog


class ProfileError(RuntimeError):
    """Base error for profile loading and runtime validation."""


class CatalogValidationError(ProfileError):
    """Raised when a feature or profile catalog is internally inconsistent."""


class ProfileLookupError(ProfileError):
    """Raised when a requested profile id does not exist."""


ID_PATTERN = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*")


def _validate_id(value: str, *, kind: str) -> str | None:
    if ID_PATTERN.fullmatch(value):
        return None
    return f"{kind} id '{value}' must use lowercase kebab-case."


def _validate_relative_path(value: str, *, context: str) -> str | None:
    posix_path = PurePosixPath(value)
    windows_path = PureWindowsPath(value)
    raw_parts = value.split("/")

    if "\\" in value:
        return f"{context} path '{value}' must use forward slashes."
    if posix_path.is_absolute() or windows_path.is_absolute() or windows_path.drive:
        return f"{context} path '{value}' must be relative to the repository root."
    if not posix_path.parts or any(part in {"", ".", ".."} for part in raw_parts):
        return f"{context} path '{value}' must not be empty or contain '.' or '..' segments."
    return None


def _dependency_cycle(catalog: ProfileCatalog) -> tuple[str, ...] | None:
    visited: set[str] = set()
    active: list[str] = []
    active_set: set[str] = set()

    def visit(feature_id: str) -> tuple[str, ...] | None:
        if feature_id in active_set:
            start = active.index(feature_id)
            return tuple(active[start:] + [feature_id])
        if feature_id in visited:
            return None

        active.append(feature_id)
        active_set.add(feature_id)
        for dependency in catalog.features[feature_id].requires:
            if dependency in catalog.features:
                cycle = visit(dependency)
                if cycle is not None:
                    return cycle
        active.pop()
        active_set.remove(feature_id)
        visited.add(feature_id)
        return None

    for feature_id in catalog.features:
        cycle = visit(feature_id)
        if cycle is not None:
            return cycle
    return None


def validate_feature_selection(feature_ids: Iterable[str], catalog: ProfileCatalog) -> tuple[str, ...]:
    selected = tuple(dict.fromkeys(feature_ids))
    errors: list[str] = []
    enabled = set(selected)

    for feature_id in selected:
        if feature_id not in catalog.features:
            errors.append(f"Unknown feature '{feature_id}'.")

    if errors:
        raise CatalogValidationError("\n".join(errors))

    for feature_id in selected:
        feature = catalog.features[feature_id]
        for dependency in feature.requires:
            if dependency not in enabled:
                errors.append(f"Feature '{feature_id}' requires feature '{dependency}'.")

    if errors:
        raise CatalogValidationError("\n".join(errors))

    return selected


def validate_catalog(
    catalog: ProfileCatalog,
    *,
    project_root: Path | None = None,
    validate_paths: bool = True,
) -> None:
    errors: list[str] = []

    if not catalog.core_paths:
        errors.append("Profile catalog must define at least one core path.")

    if not catalog.features:
        errors.append("Profile catalog must define at least one feature.")

    if not catalog.profiles:
        errors.append("Profile catalog must define at least one profile.")

    root = project_root.resolve() if project_root is not None else None
    for relative in catalog.core_paths:
        path_error = _validate_relative_path(relative, context="Core")
        if path_error:
            errors.append(path_error)
            continue
        if validate_paths and root is not None:
            candidate = (root / relative).resolve()
            if not candidate.is_relative_to(root):
                errors.append(f"Core path '{relative}' resolves outside {root}.")
            elif not candidate.exists():
                errors.append(f"Core path '{relative}' does not exist under {root}.")

    for feature in catalog.features.values():
        id_error = _validate_id(feature.id, kind="Feature")
        if id_error:
            errors.append(id_error)
        for dependency in feature.requires:
            if dependency not in catalog.features:
                errors.append(f"Feature '{feature.id}' requires unknown feature '{dependency}'.")
        for relative in feature.paths:
            path_error = _validate_relative_path(relative, context=f"Feature '{feature.id}'")
            if path_error:
                errors.append(path_error)
                continue
            if validate_paths and root is not None:
                candidate = (root / relative).resolve()
                if not candidate.is_relative_to(root):
                    errors.append(f"Feature '{feature.id}' path '{relative}' resolves outside {root}.")
                elif not candidate.exists():
                    errors.append(f"Feature '{feature.id}' path '{relative}' does not exist under {root}.")

    cycle = _dependency_cycle(catalog)
    if cycle is not None:
        errors.append(f"Feature dependency cycle detected: {' -> '.join(cycle)}.")

    for profile in catalog.profiles.values():
        id_error = _validate_id(profile.id, kind="Profile")
        if id_error:
            errors.append(id_error)
        if profile.schema_version != catalog.schema_version:
            errors.append(
                f"Profile '{profile.id}' uses schema version {profile.schema_version}; "
                f"catalog version is {catalog.schema_version}."
            )
        try:
            validate_feature_selection(profile.features, catalog)
        except CatalogValidationError as exc:
            errors.append(f"Profile '{profile.id}' is invalid: {exc}")

    if errors:
        raise CatalogValidationError("\n".join(errors))
