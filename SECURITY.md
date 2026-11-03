# Security policy

Report a vulnerability privately through GitHub: **Security → Report a
vulnerability** on this repository
(<https://github.com/hubbiot/tvenndb/security/advisories/new>). Do not open a
public issue for anything that might be a vulnerability, and do not test
against installations you do not own.

Include what you can of: the TvennDB version (`GET /health`, the image tag
or digest), the component (gateway, shard, Explorer, MCP endpoint, command
line tool, Helm chart), steps to reproduce, and the impact you believe it
has.

| Step | Target |
|---|---|
| Acknowledgement | 2 business days |
| Triage and severity (CVSS 3.1) | 5 business days |
| Fix for critical and high severity | 30 days from triage |
| Fix for medium and low severity | next minor release, at most 90 days |
| Public advisory | with the fix release, coordinated with the reporter |

We credit reporters in the advisory unless they prefer otherwise.
