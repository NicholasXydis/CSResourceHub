# Security Policy

## Supported Versions

| Version | Supported |
| --- | --- |
| 1.0.0 | ✅ |

Only the latest release receives security fixes. The dataset and site are published from `main`.

## Reporting a Vulnerability

If you find a malicious URL, harmful content, a vulnerability in the frontend in `src/`, or a security concern in a dependency, please **do not open a public issue**.

Report privately through [GitHub Security Advisories](https://github.com/NicholasXydis/CSResourceHub/security/advisories/new), or email <NicholasXydis@outlook.com>.

Include:

- The file and resource name, or the affected source file
- The URL in question
- Why you believe it is harmful

I will respond within 48 hours and remove the resource or patch the issue if confirmed.

## Automated Scanning

Every push and pull request to `main` runs:

- **CodeQL** static analysis for Python, TypeScript, and GitHub Actions workflows.
- **OSV-Scanner** against the `package-lock.json` and `uv.lock` lockfiles.
- **npm audit** on production dependencies, failing on high severity or above.
- **License policy** enforcement, restricting production dependencies to a permissive allowlist.
- **Dependency review** on pull requests, blocking new high-severity or AGPL-licensed dependencies.

On a schedule:

- **Dependabot** monitors Python, npm, and GitHub Actions dependencies for known vulnerabilities.
- **Link checking** verifies every resource URL and reports dead links.
- **Production health** checks that the live site serves the expected security headers.

## Hardening

- All GitHub Actions are pinned to full commit SHAs, not tags.
- Workflows run with least-privilege `permissions` and drop credentials (`persist-credentials: false`) wherever they do not push.
- Python dependencies are locked (`uv.lock`) and installed with `uv sync --frozen`.
- The site is served with a strict Content Security Policy, plus `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, and `Permissions-Policy` (see [`public/_headers`](./public/_headers)).
