# Security Policy

## Supported versions

| Version | Supported |
| --- | --- |
| Latest fully validated `1.0.x` GitHub Release | Yes |
| Tag-only or incomplete candidates, including `v1.0.1` | No |
| Current `main` | Best effort |
| Earlier major or minor release lines | No |

Security reports about the latest fully validated template release and the current `main` development line are assessed on a best-effort basis. An annotated tag alone does not establish a supported release: the applicable same-SHA workflows, tag-triggered validation, and governed GitHub Release publication must all complete successfully. Publications from `v1.0.2` onward additionally require an active non-bypassable release-tag ruleset and native GitHub Release immutability. A project generated from this template must define its own supported versions and security policy; support for the template does not automatically extend to generated products.

## Report a vulnerability privately

Do not open a public GitHub Issue for a suspected security vulnerability.

The preferred route is GitHub Private Vulnerability Reporting through the repository's [Security tab](https://github.com/kleiveist/Template-Projekte/security). If the private reporting form is unavailable, send the report to [kleiveist@proton.me](mailto:kleiveist@proton.me). This address is reserved for confidential security and Code-of-Conduct incidents only.

Normal bugs, feature requests, and support questions belong in public GitHub Issues; see [CONTRIBUTING.md](../CONTRIBUTING.md).

## Include useful details

Please provide enough information to reproduce and assess the issue without including credentials, access tokens, private keys, or unnecessary personal data:

- affected component, project profile, version, commit, or deployment context;
- impact and the conditions required to trigger the issue;
- reproducible steps or a minimal proof of concept;
- a proposed mitigation or fix, if available; and
- a safe way to ask follow-up questions.

## What happens after a report

Maintainers may acknowledge the report, request clarification, assess the impact, and coordinate a remedy through the private channel. This policy does not promise a response time, a fix, a publication date, or a reward.

## Coordinated disclosure

Please keep vulnerability details private while they are being assessed. Give maintainers an opportunity to investigate and coordinate a remedy before public disclosure. Disclosure timing and credit, where appropriate, can be discussed through the private report.

## Security, bugs, and support

Use this policy only for vulnerabilities that could affect confidentiality, integrity, availability, authorization, or other security properties. Use the public Issue Forms for reproducible non-security defects and feature proposals. Use the [contribution guide](../CONTRIBUTING.md) for development and support guidance.
