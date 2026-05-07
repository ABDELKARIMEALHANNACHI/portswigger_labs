# Lab 1 — Accessing Private GraphQL Posts (APPRENTICE)

## Vulnerability
IDOR via unauthenticated GraphQL query — private posts and credential fields
returned to any caller due to missing authorization checks.

## Files
| Path | Description |
|------|-------------|
| `vuln/vuln.py` | Vulnerable Flask/Graphql-core server |
| `vuln/vuln.php` | Vulnerable webonyx/graphql-php server |
| `vuln/vuln.java` | Vulnerable Spring Boot + GraphQL server |
| `exploit/payloads.txt` | GraphQL queries for exploitation |
| `exploit/request.txt` | Raw HTTP request |
| `exploit/response.txt` | Raw HTTP response (data leak) |
| `fix/fix.py` | Patched Python resolver |
| `fix/fix.php` | Patched PHP resolver |
| `fix/fix.java` | Patched Java resolver (Spring Security) |
| `notes/explanation.txt` | Vulnerability deep-dive |
| `notes/methodology.txt` | Step-by-step pentesting methodology |

## Quick Exploit
```graphql
{ getBlogPost(id: 2) { id title content postPassword isPublic } }
```
