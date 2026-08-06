from __future__ import annotations

from pathlib import Path

from tools import logger
from tools.profiles.generator import GenerationError, build_scaffold_plan, scaffold_project
from tools.profiles.loader import load_catalog
from tools.profiles.model import ProfileCatalog, ProfileDefinition
from tools.profiles.validator import CatalogValidationError, ProfileError, ProfileLookupError

ROOT = Path(__file__).resolve().parents[2]


def main(args) -> int:
    try:
        catalog = load_catalog(ROOT / "profiles")
        profile = _resolve_profile_choice(catalog, getattr(args, "profile", None))
        target_dir = _resolve_target_dir(getattr(args, "target_dir", None), profile.id)
        plan = build_scaffold_plan(
            catalog,
            project_root=ROOT,
            target_dir=target_dir,
            profile_id=profile.id,
        )
    except ProfileLookupError as exc:
        logger.fail(str(exc))
        return 2
    except (CatalogValidationError, GenerationError, OSError, ValueError) as exc:
        logger.fail(str(exc))
        return 1

    _print_plan(plan)
    scaffold_project(plan, dry_run=bool(getattr(args, "dry_run", False)))

    if getattr(args, "dry_run", False):
        logger.ok("Init dry-run completed; no files were written")
        return 0

    logger.ok(f"Generated profile '{plan.profile.profile_id}' in {plan.target_dir}")
    return 0


def _ordered_profiles(catalog: ProfileCatalog) -> list[ProfileDefinition]:
    return sorted(catalog.profiles.values(), key=lambda item: (item.order, item.name.lower(), item.id))


def _resolve_profile_choice(catalog: ProfileCatalog, explicit_profile: str | None) -> ProfileDefinition:
    if explicit_profile:
        profile = catalog.profiles.get(explicit_profile)
        if profile is None:
            known = ", ".join(item.id for item in _ordered_profiles(catalog))
            raise ProfileLookupError(f"Unknown profile '{explicit_profile}'. Available profiles: {known}.")
        return profile
    return _prompt_for_profile(catalog)


def _prompt_for_profile(catalog: ProfileCatalog) -> ProfileDefinition:
    options = _ordered_profiles(catalog)
    print("Choose project profile:\n")
    for index, profile in enumerate(options, start=1):
        print(f"{index}. {profile.name} ({profile.id})")
        print(f"   {profile.description}")
    print("")

    while True:
        try:
            choice = input(f"Selection [1-{len(options)} or q]: ").strip().lower()
        except EOFError:
            choice = "q"
            print("")

        if choice in {"q", "quit", "exit"}:
            raise GenerationError("Initialization cancelled.")

        try:
            index = int(choice)
        except ValueError:
            logger.warn("Enter a profile number or 'q' to cancel.")
            continue

        if 1 <= index <= len(options):
            return options[index - 1]
        logger.warn("Selected profile is outside the available range.")


def _resolve_target_dir(explicit_target: str | None, profile_id: str) -> Path:
    if explicit_target:
        return Path(explicit_target).expanduser()
    return ROOT / ".generated" / profile_id


def _print_plan(plan) -> None:
    logger.info(f"Profile: {plan.profile.name} ({plan.profile.profile_id})")
    logger.info(f"Description: {plan.profile.description}")
    logger.info(f"Enabled features: {', '.join(plan.profile.features)}")
    logger.info(f"Target directory: {plan.target_dir}")
    logger.info("Scaffold paths:")
    for source in plan.paths:
        logger.info(f"  - {source.relative_to(plan.project_root).as_posix()}")
