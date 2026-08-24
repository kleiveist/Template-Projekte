from __future__ import annotations

import re
from pathlib import Path

from tools.profiles import generator, loader

ROOT = Path(__file__).resolve().parents[2]
PROFILES_DIR = ROOT / "profiles"
ISSUE_FORMS = tuple(sorted((ROOT / ".github" / "ISSUE_TEMPLATE").glob("[0-9][0-9]-*.yml")))
ISSUE_CONFIG = ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml"
PULL_REQUEST_TEMPLATE = ROOT / ".github" / "pull_request_template.md"
REPOSITORY_URL = "https://github.com/kleiveist/Template-Projekte"
MASTER_ONLY_PATHS = (
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    ".github/SECURITY.md",
    ".github/ISSUE_TEMPLATE",
    ".github/pull_request_template.md",
    ".github/workflows",
)


def test_scaffold_owns_license_but_not_master_community_governance(tmp_path: Path) -> None:
    catalog = loader.load_catalog(PROFILES_DIR, validate_paths=False)
    target = tmp_path / "web-only"
    plan = generator.build_scaffold_plan(
        catalog,
        project_root=ROOT,
        target_dir=target,
        profile_id="web-only",
    )

    generator.scaffold_project(plan)

    assert (target / "LICENSE").read_text(encoding="utf-8") == (ROOT / "LICENSE").read_text(encoding="utf-8")
    assert all(not (target / relative).exists() for relative in MASTER_ONLY_PATHS)
    generated_readme = (target / "README.md").read_text(encoding="utf-8")
    assert "CODE_OF_CONDUCT.md" not in generated_readme
    assert "CONTRIBUTING.md" not in generated_readme
    assert ".github/SECURITY.md" not in generated_readme
    assert "[MIT License](LICENSE)" in generated_readme


def test_master_community_template_links_use_rendered_github_context() -> None:
    templates = (*ISSUE_FORMS, PULL_REQUEST_TEMPLATE)
    for template in templates:
        targets = re.findall(r"\[[^\]]+\]\(([^)]+)\)", template.read_text(encoding="utf-8"))
        for target in targets:
            assert target.startswith(f"{REPOSITORY_URL}/"), (
                f"Community template links render in issue or pull-request bodies and must use a stable repository URL: "
                f"{template}: {target}"
            )

    security_policy_url = f"{REPOSITORY_URL}/security/policy"
    assert all(security_policy_url in form.read_text(encoding="utf-8") for form in ISSUE_FORMS)
    assert security_policy_url in PULL_REQUEST_TEMPLATE.read_text(encoding="utf-8")
    assert f"{REPOSITORY_URL}/security" in ISSUE_CONFIG.read_text(encoding="utf-8")
