PostgreSQL Authentication Problems

Metadata

Title: Client Authentication and Authentication Problems
Product: PostgreSQL
Product Version: PostgreSQL 18
Source Type: Official Documentation
Source Organization: PostgreSQL Global Development Group
Topic: Database Client Authentication
Source URL: https://www.postgresql.org/docs/current/client-authentication.html
Last Updated: Not explicitly stated on the page; current official PostgreSQL 18 documentation
Collected On: 2026-09-18

Problem / Overview

PostgreSQL client authentication is the process used by the database server to establish the identity of a client and determine whether that client may connect using the requested database user name.

PostgreSQL controls client authentication through the pg_hba.conf file. HBA means host-based authentication. Authentication rules can be selected according to the connection type, client address, database, and user. PostgreSQL users are logically separate from operating-system users; PostgreSQL privilege management is based on roles, and a database user is a role with the LOGIN privilege.

The pg_hba.conf file contains authentication records. PostgreSQL uses the first record that matches the connection type, client address, requested database, and user. There is no fallback to later records after a matching record fails. If no record matches, access is denied.

Symptoms

Common PostgreSQL authentication-related errors documented by PostgreSQL include:

FATAL: no pg_hba.conf entry for host "...", user "...", database "..."

FATAL: password authentication failed for user "..."

FATAL: user "..." does not exist

FATAL: database "..." does not exist

A no pg_hba.conf entry error means the server was contacted but no matching authentication rule was found.

A password authentication failed error means the server was contacted and the authentication method selected by pg_hba.conf did not accept the supplied credentials or authentication process.

A user does not exist error indicates that the requested PostgreSQL database user name was not found.

A database does not exist error indicates that the requested database was not found. When no database name is supplied, PostgreSQL uses the database user name as the default database name.

Common Causes

Based on the official PostgreSQL documentation, authentication failures can be caused by:

No matching rule in pg_hba.conf.

An authentication rule that specifies a different database, user, client address, or connection type.

Incorrect password or failure of the configured authentication mechanism.

A PostgreSQL user that does not exist.

A requested database that does not exist.

Password authentication configuration that is incompatible with the stored password format or client support.

A password that has not been set for the PostgreSQL user.

PostgreSQL supports multiple authentication methods, including trust, reject, scram-sha-256, md5, password, gss, sspi, ident, peer, ldap, radius, cert, and pam, subject to the applicable platform and configuration requirements.

Diagnostic Steps

Read the complete PostgreSQL error message and identify whether the failure relates to pg_hba.conf, the password, the database user, or the database name.

Check the relevant pg_hba.conf rules. Confirm that a rule matches the connection type, client address, requested database, and user.

Remember that PostgreSQL uses the first matching authentication record. A later rule does not act as a backup if the first matching rule fails.

Check the PostgreSQL server log if the reason for the authentication failure is unclear. PostgreSQL notes that the server log may contain more information than is returned to the client.

For password-authentication problems, verify that the database user has a password and that the selected authentication method is compatible with the password storage format and client library.

When changing pg_hba.conf, make sure PostgreSQL rereads the configuration. On systems other than Microsoft Windows, the configuration can be reloaded using PostgreSQL-supported reload mechanisms. On Microsoft Windows, changes are applied to subsequent new connections.

The PostgreSQL pg_hba_file_rules system view can help pre-test configuration changes and diagnose problems in the authentication configuration file.

Resolution / Recommended Actions

Add or correct the appropriate pg_hba.conf authentication rule when no matching rule exists.

Verify that the requested database user exists and has the necessary login capability.

Verify or reset the database user's password when password authentication is being used.

Use an authentication method appropriate for the environment and supported by the client.

Prefer scram-sha-256 for password authentication in current PostgreSQL deployments when the client libraries support it. PostgreSQL documents SCRAM as the most secure of its currently provided password-based methods.

Treat md5 as a migration concern because PostgreSQL documents MD5-encrypted passwords as deprecated and planned for removal in a future release.

Avoid the password authentication method on untrusted networks because it transmits the password in clear text unless the connection is protected by SSL.

After correcting pg_hba.conf, reload the configuration where required and test a new connection.

Important Notes / Limitations

pg_hba.conf controls client authentication; it does not replace PostgreSQL privilege management.

Authentication method selection is based on the connection characteristics matched by the configuration file.

Remote TCP/IP connections also depend on PostgreSQL being configured to listen on an appropriate address. The default behavior is to listen on the local loopback address.

scram-sha-256 is not supported by older client libraries, so client compatibility must be considered before migration.

PostgreSQL database passwords are separate from operating-system user passwords.

Do not store real customer passwords, API keys, or other secrets in this Knowledge Base.

This document summarizes troubleshooting-relevant information from the official PostgreSQL documentation; it is not a substitute for environment-specific investigation.

Source

PostgreSQL Official Documentation:

Client Authentication
https://www.postgresql.org/docs/current/client-authentication.html

The pg_hba.conf File
https://www.postgresql.org/docs/current/auth-pg-hba-conf.html

Password Authentication
https://www.postgresql.org/docs/current/auth-password.html

Authentication Problems
https://www.postgresql.org/docs/current/client-authentication-problems.html