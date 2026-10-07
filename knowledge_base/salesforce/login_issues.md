# Salesforce Login Issues

## Metadata

Title: Best Practices for Handling and Troubleshooting Failed Logins in Salesforce
Product: Salesforce
Product Version: Current Salesforce Platform
Source Type: Official Documentation
Source Organization: Salesforce
Topic: Login Failures and Troubleshooting
Source URL: https://help.salesforce.com/s/articleView?id=000212767&language=en_US&type=1
Last Updated: July 1, 2026
Collected On: September 19, 2026

## Problem / Overview

Salesforce login failures can occur for different reasons, including
invalid credentials, incorrect user or organization permissions,
expired passwords, API access restrictions, security-token
requirements, and account or organization restrictions.

Salesforce supports login through the Salesforce user interface,
mobile applications, and programmatic API access.

Repeated or simultaneous failed login attempts can create additional
overhead and may negatively affect the user experience. Salesforce
also documents that, in severe cases, the IP address generating
excessive failed login requests may be temporarily blocked.

## Symptoms

Common documented login-related errors include:

- INVALID_LOGIN
- PASSWORD_LOCKOUT
- INVALID_OPERATION_WITH_EXPIRED_PASSWORD
- API_DISABLED_FOR_ORG
- API_CURRENTLY_DISABLED
- LOGIN_MUST_USE_SECURITY_TOKEN
- INVALID_SESSION_ID

A failed login may also occur because of incorrect user or
organization permissions.

## Common Causes

According to Salesforce documentation, login failures may be caused by:

- Invalid username or password.
- Expired password.
- User account being locked because of excessive failed attempts.
- Incorrect user or organization permissions.
- API access being disabled.
- API limits being reached.
- Security token being required but not supplied.
- Invalid or expired session.
- Organization-level restrictions.

## Diagnostic Steps

### 1. Check the Specific Error

Do not repeatedly retry a failed login without first identifying
the error returned by Salesforce.

For API-based authentication, inspect the response or exception
for the Salesforce error code and message.

### 2. Check `INVALID_LOGIN`

`INVALID_LOGIN` indicates invalid credentials.

Verify the username and password and request the correct credentials
from the authorized user when appropriate.

### 3. Check `PASSWORD_LOCKOUT`

`PASSWORD_LOCKOUT` indicates that the user has exceeded the allowed
number of failed password attempts.

Salesforce recommends not repeatedly attempting authentication after
this error.

### 4. Check Password Expiration

An expired password can result in:

`INVALID_OPERATION_WITH_EXPIRED_PASSWORD`

Integration code should handle this condition rather than repeatedly
retrying the login.

### 5. Check API Permissions

If the login is being performed through an API, verify that API
access is available for the organization and that the user has the
required API permissions.

### 6. Check Security Token Requirements

For API logins, Salesforce may require the security token to be
included with the password.

If required but missing, Salesforce can return:

`LOGIN_MUST_USE_SECURITY_TOKEN`

### 7. Check Session Status

If an existing session is no longer valid, Salesforce can return:

`INVALID_SESSION_ID`

The application should handle the expired session according to the
authentication mechanism being used.

### 8. Check API Limits

Salesforce documents limits on API calls, including programmatic
logins. Check whether the organization has reached its applicable
API limit.

## Resolution / Recommended Actions

- Verify the username and password.
- Address expired-password conditions.
- Do not repeatedly retry authentication when the returned error
  indicates that retrying will not resolve the problem.
- Verify that the user has the appropriate permissions.
- Verify that API access is enabled when API login is being used.
- Provide the required security token when Salesforce requires one.
- Handle expired sessions by refreshing or obtaining a new session
  according to the authentication method.
- Monitor API usage when login failures may be related to API limits.
- If excessive failed logins are occurring, investigate the reason
  for the failures before continuing automated retries.

## Important Notes / Limitations

- A failed login does not necessarily indicate an incorrect password.
- The exact Salesforce error code should be examined before choosing
  a troubleshooting action.
- Repeated failed login attempts can create unnecessary overhead.
- Salesforce documents that excessive failed logins may result in a
  temporary IP block in severe circumstances.
- A temporary IP block can also affect valid login attempts from the
  same IP address.
- API login behavior can differ from normal Salesforce UI login
  behavior.
- Security-token requirements depend on the Salesforce organization
  and login configuration.
- Do not store real Salesforce passwords, security tokens,
  access tokens, client secrets, or other credentials in this
  Knowledge Base.

## Source

Salesforce Official Documentation:

Best Practices for Handling and Troubleshooting Failed Logins in Salesforce

https://help.salesforce.com/s/articleView?id=000212767&language=en_US&type=1