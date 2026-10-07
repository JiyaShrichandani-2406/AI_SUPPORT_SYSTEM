# API Authentication

## Metadata

Title: HTTP Authentication
Product: HTTP / Web APIs
Product Version: HTTP Semantics / Current Web Standards
Source Type: Official Technical Documentation
Source Organization: MDN Web Docs / HTTP Standards
Topic: API Authentication and Authorization Headers
Source URL: https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Authentication
Last Updated: Current MDN documentation
Collected On: September 19, 2026

## Problem / Overview

HTTP provides a general framework for authentication and access
control.

When a client requests a protected resource without valid
authentication credentials, the server can respond with:

401 Unauthorized

The server can include a `WWW-Authenticate` response header to
indicate the authentication scheme or challenge that the client
should use.

The client can then send credentials using the `Authorization`
request header.

The general authentication flow is:

Client
  ↓
Request protected resource
  ↓
Server returns 401
  ↓
WWW-Authenticate challenge
  ↓
Client provides credentials
  ↓
Authorization header
  ↓
Server processes authenticated request

## Symptoms

Authentication-related API problems may appear as:

- API returns `401 Unauthorized`.
- API returns `403 Forbidden`.
- Server returns a `WWW-Authenticate` header.
- API rejects requests without an `Authorization` header.
- Access token is missing.
- Access token is invalid or expired.
- Authentication scheme is not supported.
- Credentials are incorrectly formatted.

## Common Causes

API authentication problems can be associated with:

- Missing authentication credentials.
- Invalid credentials.
- Expired credentials.
- Incorrect authentication scheme.
- Incorrect `Authorization` header format.
- Missing or incorrect access token.
- Insufficient permissions after successful authentication.
- Incorrect server authentication configuration.

Authentication and authorization are different concepts.

Authentication determines whether the client can establish its
identity.

Authorization determines whether the authenticated client has
permission to access or modify a resource.

## Diagnostic Steps

### 1. Check the HTTP Status Code

A `401 Unauthorized` response indicates that the request lacks valid
authentication credentials.

A `403 Forbidden` response generally indicates that the server knows
the client's identity but refuses access because the client does not
have sufficient permission.

### 2. Check `WWW-Authenticate`

For a `401 Unauthorized` response, inspect the
`WWW-Authenticate` response header.

Example:

WWW-Authenticate: Bearer

The header identifies an authentication challenge supported by the
server.

### 3. Check the `Authorization` Header

Verify that the client sends the required credentials using the
appropriate authentication scheme.

General syntax:

Authorization: <auth-scheme> <credentials>

### 4. Check the Authentication Scheme

Common HTTP authentication schemes include:

- Basic
- Digest
- Bearer
- Other scheme-specific mechanisms

The exact authentication scheme depends on the API or server.

### 5. Check Token Validity

For APIs using access tokens, verify that:

- The token is present.
- The token has not expired.
- The token is intended for the requested API.
- The token is correctly formatted.
- The token has the required permissions or scopes.

### 6. Check HTTPS

Authentication credentials should be protected during transmission.

Basic authentication encodes credentials using Base64, but Base64
encoding does not provide encryption.

HTTPS/TLS should therefore be used when transmitting authentication
credentials.

### 7. Check Permissions

If authentication succeeds but the API returns `403 Forbidden`,
investigate whether the authenticated identity has permission to
perform the requested operation.

## Resolution / Recommended Actions

- Supply valid authentication credentials.
- Use the authentication scheme required by the API.
- Correct the `Authorization` header format.
- Obtain a new access token when the existing token has expired.
- Ensure that the token has the required permissions or scopes.
- Use HTTPS/TLS when transmitting authentication credentials.
- Check the server's `WWW-Authenticate` challenge when a `401`
  response is returned.
- Distinguish authentication failures from authorization failures.

## Important Notes / Limitations

- `401 Unauthorized` means that valid authentication credentials
  are required.
- `403 Forbidden` is different from `401`; it generally means the
  request is authenticated but access is not permitted.
- The `WWW-Authenticate` header is used by the server to advertise
  authentication challenges.
- The `Authorization` header contains credentials used to
  authenticate the client.
- Basic authentication uses Base64 encoding, which is reversible
  and does not provide cryptographic protection.
- HTTPS/TLS should be used to protect credentials in transit.
- Authentication behavior can vary depending on the API and the
  authentication scheme it implements.
- Never store real passwords, API keys, access tokens, refresh
  tokens, client secrets, or other credentials in this Knowledge
  Base.

## Source

MDN Web Docs:

HTTP Authentication
https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Authentication

Authorization Header
https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Authorization

WWW-Authenticate Header
https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/WWW-Authenticate

HTTP Response Status Codes
https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status