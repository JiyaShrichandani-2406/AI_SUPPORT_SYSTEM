# Salesforce Authentication

## Metadata

Title: User Authentication
Product: Salesforce
Product Version: Current Salesforce Platform
Source Type: Official Documentation
Source Organization: Salesforce
Topic: User Authentication, MFA, SSO and Passwordless Authentication
Source URL: https://help.salesforce.com/s/articleView?id=xcloud.security_user_authentication.htm&language=en_US&type=5
Last Updated: Current Salesforce documentation
Collected On: September 19, 2026

## Problem / Overview

Authentication protects access to Salesforce by verifying the identity
of users before allowing access to Salesforce resources.

Salesforce supports multiple authentication approaches, including:

- Username and password authentication
- Multi-factor authentication (MFA)
- Single sign-on (SSO)
- Passkeys
- Certificate-based authentication
- Lightning Login

Authentication requirements and available methods can vary depending
on the type of Salesforce access and organization configuration.

## Symptoms

Authentication-related problems may appear as:

- User cannot complete Salesforce login.
- User is asked for an additional verification factor.
- MFA verification cannot be completed.
- SSO authentication does not complete successfully.
- Authentication through a third-party identity provider fails.
- A configured authentication method is unavailable.
- A user cannot complete a passwordless login.

## Common Causes

Authentication problems can be associated with:

- Incorrect username or password.
- MFA verification problems.
- Incorrect SSO configuration.
- Identity-provider configuration problems.
- Incorrect authentication-provider configuration.
- Missing or invalid authentication signals in an SSO flow.
- Certificate configuration problems.
- Problems with passkey or security-key authentication.
- Organization security settings.

## Diagnostic Steps

### 1. Identify the Authentication Method

Determine whether the user is attempting:

- Direct Salesforce login.
- Single sign-on (SSO).
- Passkey authentication.
- Lightning Login.
- Certificate-based authentication.

The troubleshooting process depends on the authentication method.

### 2. Check Direct Login

For direct Salesforce login, verify the user's credentials and
authentication requirements.

Salesforce requires MFA for applicable employee logins.

### 3. Check MFA

MFA requires the user to provide an additional verification factor
in addition to the primary login credentials.

Supported verification approaches include:

- Built-in authenticators and passkeys.
- Security keys.
- Salesforce Authenticator.
- Third-party authenticator applications.

Verify that the user has an available and properly registered
verification method.

### 4. Check SSO

When SSO is used, Salesforce can rely on a third-party identity
provider to authenticate users.

Verify the SSO configuration and determine whether authentication
is successfully completed by the identity provider.

### 5. Check Authentication Signals

For SSO configurations, Salesforce may require authentication
signals from the identity provider to indicate that the required
authentication method was completed.

SAML identity providers can send relevant authentication information
in the SAML response.

OpenID Connect providers can provide authentication information
through the ID token.

### 6. Check Authentication Provider Configuration

When Salesforce is configured as a relying party using an
authentication provider, verify the provider configuration,
registration handler, and relevant third-party settings.

### 7. Check Passwordless Authentication

If passkeys or Lightning Login are being used, verify that the
required authenticator or security key is available and correctly
registered.

## Resolution / Recommended Actions

- Verify the authentication method being used.
- Verify the user's credentials for direct login.
- Complete the required MFA verification.
- Verify that the user's MFA verification method is registered
  and available.
- Check SSO configuration when authentication is delegated to an
  identity provider.
- Verify that the identity provider sends the required authentication
  information.
- Check authentication-provider configuration when third-party
  authentication is being used.
- Verify passkey, security-key, or certificate configuration when
  those methods are used.
- Follow Salesforce's documented configuration procedure for the
  specific authentication method.

## Important Notes / Limitations

- Authentication and authorization are related but different
  concepts. Authentication verifies identity; authorization controls
  access to resources.
- Salesforce supports multiple authentication mechanisms.
- Salesforce requires MFA for applicable employee logins to
  Salesforce products.
- MFA requirements also apply to applicable SSO login scenarios.
- Authentication requirements can differ between direct login,
  SSO, API access, and other integration scenarios.
- SSO can use a third-party identity provider.
- Do not store passwords, MFA secrets, recovery codes, security
  tokens, access tokens, client secrets, certificates containing
  private keys, or other credentials in this Knowledge Base.

## Source

Salesforce Official Documentation:

1. User Authentication
   https://help.salesforce.com/s/articleView?id=xcloud.security_user_authentication.htm&language=en_US&type=5

2. Understand MFA Requirements
   https://help.salesforce.com/s/articleView?id=xcloud.mfa_make_the_case.htm&language=en_US&type=5

3. MFA Verification Methods for Direct Salesforce Login
   https://help.salesforce.com/articleView?id=mfa_supported_verification_methods.htm