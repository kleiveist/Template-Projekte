from __future__ import annotations

from pathlib import Path
from typing import Iterable

from tools.profiles.model import ProfileCatalog


class ProfileError(RuntimeError):
    """Base error for profile loading and runtime validation."""


class CatalogValidationError(ProfileError):
    """Raised when a feature or profile catalog is internally inconsistent."""


class ProfileLookupError(ProfileError):
    """Raised when a requested profile id does not exist."""


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

    if validate_paths and project_root is not None:
        for relative in catalog.core_paths:
            if not (project_root / relative).exists():
                errors.append(f"Core path '{relative}' does not exist under {project_root}.")

        for feature in catalog.features.values():
            for relative in feature.paths:
                if not (project_root / relative).exists():
                    errors.append(f"Feature '{feature.id}' path '{relative}' does not exist under {project_root}.")

    for profile in catalog.profiles.values():
        try:
            validate_feature_selection(profile.features, catalog)
        except CatalogValidationError as exc:
            errors.append(f"Profile '{profile.id}' is invalid: {exc}")

    if errors:
        raise CatalogValidationError("\n".join(errors))
