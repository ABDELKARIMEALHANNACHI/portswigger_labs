# GraphQL API Vulnerability Labs

A professional security-research lab suite covering five real-world GraphQL
attack classes. Each lab mirrors the layout used in the SSRF suite:

```
<lab>/
├── exploit/   payloads · raw request · raw response
├── fix/       hardened Java · PHP · Python implementations
├── notes/     explanation · methodology
├── vuln/      vulnerable Java · PHP · Python implementations
└── README.md
```

## Labs

| # | Folder | Level | Topic |
|---|--------|-------|-------|
| 1 | graphql-private-posts | APPRENTICE | IDOR via unauthenticated query |
| 2 | graphql-accidental-field-exposure | PRACTITIONER | Introspection leaks hidden fields |
| 3 | graphql-hidden-endpoint | PRACTITIONER | Endpoint discovery & introspection |
| 4 | graphql-brute-force-bypass | PRACTITIONER | Alias-batching to bypass rate-limit |
| 5 | graphql-csrf | PRACTITIONER | CSRF over GET / content-type switch |

## Quick-start

```bash
chmod +x build_graphql.sh && ./build_graphql.sh
```

## References
- https://portswigger.net/web-security/graphql
- https://graphql.org/learn/introspection/
- https://owasp.org/www-project-web-security-testing-guide/
