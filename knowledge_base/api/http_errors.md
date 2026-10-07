# HTTP API Errors

## Metadata

Title: HTTP Response Status Codes
Product: HTTP / Web APIs
Product Version: HTTP Semantics / Current Web Standards
Source Type: Official Technical Documentation
Source Organization: MDN Web Docs / HTTP Standards
Topic: HTTP API Errors and Response Status Codes
Source URL: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status
Last Updated: Current MDN documentation
Collected On: September 19, 2026

## Problem / Overview

HTTP response status codes indicate the result of an HTTP request.

They are grouped into five classes:

- 100–199: Informational responses
- 200–299: Successful responses
- 300–399: Redirection responses
- 400–499: Client error responses
- 500–599: Server error responses

API clients should inspect the HTTP status code returned by the
server to determine whether a request succeeded or failed.

An HTTP error does not by itself identify the complete root cause.
The response body, headers, request parameters, and server-side
information may also be required for diagnosis.

## Symptoms

Common HTTP API error symptoms include:

- API request returns a 4xx status code.
- API request returns a 5xx status code.
- Requested resource cannot be found.
- Authentication is required.
- Client request contains invalid data.
- HTTP method is not supported.
- Server does not respond within the expected time.
- Gateway or proxy cannot obtain a response from an upstream server.

## Common Causes

HTTP API errors can be associated with:

- Malformed request syntax.
- Invalid request parameters.
- Missing authentication credentials.
- Insufficient permissions.
- Incorrect URL or resource identifier.
- Unsupported HTTP method.
- Request timeout.
- Server-side errors.
- Gateway or proxy problems.
- Service unavailability.
- Network authentication requirements.

The exact cause depends on the HTTP status code and additional
information returned by the API.

## Diagnostic Steps

### 1. Check the HTTP Status Code

Identify the status code returned by the API.

Important client-error codes include:

- `400 Bad Request`
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`
- `405 Method Not Allowed`
- `408 Request Timeout`
- `409 Conflict`
- `429 Too Many Requests`

Important server or gateway errors include:

- `500 Internal Server Error`
- `502 Bad Gateway`
- `503 Service Unavailable`
- `504 Gateway Timeout`

### 2. Check the Request

Verify:

- HTTP method
- URL
- Path parameters
- Query parameters
- Request headers
- Request body
- Content type
- Authentication information

### 3. Check the Response Body

Many APIs provide additional error information in the response body.

Review the returned message, error code, or error details when
available.

### 4. Check Authentication

If the response is `401 Unauthorized`, verify that valid
authentication credentials are being supplied.

### 5. Check Permissions

If the response is `403 Forbidden`, determine whether the
authenticated client has permission to access or modify the
requested resource.

### 6. Check the Resource

If the response is `404 Not Found`, verify that:

- The URL is correct.
- The endpoint exists.
- The resource identifier is correct.
- The resource is available to the authenticated client.

### 7. Check the HTTP Method

A `405 Method Not Allowed` response indicates that the server knows
the HTTP method but the target resource does not support that method.

Verify whether the API expects GET, POST, PUT, PATCH, DELETE, or
another method.

### 8. Check Timeouts

For `408 Request Timeout` or `504 Gateway Timeout`, investigate
whether the request or an upstream service failed to respond within
the required time.

### 9. Check Rate Limits

For `429 Too Many Requests`, determine whether the client has sent
requests too frequently and follow the API's documented rate-limit
behavior.

## Resolution / Recommended Actions

- Correct malformed or invalid request data.
- Verify the API endpoint and resource identifier.
- Use the HTTP method expected by the endpoint.
- Supply valid authentication credentials.
- Verify that the authenticated user or application has the required
  permissions.
- Correct request headers and content type.
- Handle rate limiting according to the API documentation.
- Investigate upstream services when a gateway or server error occurs.
- Retry requests only when the API's documented behavior indicates
  that retrying is appropriate.
- Record the HTTP status code and relevant error information in
  application logs.

## Important Notes / Limitations

- `401 Unauthorized` semantically indicates that the request lacks
  valid authentication credentials.
- `403 Forbidden` generally indicates that the server understood the
  request but refuses access.
- `404 Not Found` can indicate that the requested resource does not
  exist. In some security designs, it may also be returned instead
  of `403` to hide the existence of a resource.
- `500` indicates an internal server error.
- `502` indicates a bad gateway response.
- `503` indicates that the service is unavailable.
- `504` indicates that a gateway did not receive a response in time.
- A status code alone may not identify the complete root cause.
- API-specific documentation should be consulted for API-specific
  error codes and retry behavior.

## Source

MDN Web Docs:

HTTP Response Status Codes
https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status

HTTP Messages
https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages