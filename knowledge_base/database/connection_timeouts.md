# PostgreSQL Connection Timeouts

## Metadata

Title: Database Connection Control and Connection Timeout
Product: PostgreSQL
Product Version: PostgreSQL 18
Source Type: Official Documentation
Source Organization: PostgreSQL Global Development Group
Topic: Database Connectivity / Connection Timeout
Source URL: https://www.postgresql.org/docs/current/libpq-connect.html
Last Updated: August 13, 2026
Collected On: September 19, 2026

## Problem / Overview

A PostgreSQL client must establish a connection with the database server before it can execute queries.

PostgreSQL provides the `connect_timeout` connection parameter to control how long a client waits while establishing a connection.

The `connect_timeout` value is specified in seconds.

If `connect_timeout` is zero, negative, or not specified, the client can wait indefinitely.

Example:

host=localhost port=5432 dbname=mydb connect_timeout=10

PostgreSQL also supports connection strings containing parameters such as host, port, database name, user, and connection timeout.

## Symptoms

A connection-timeout problem may be observed when:

- The client cannot establish a connection to the PostgreSQL server.
- The connection attempt takes longer than the configured timeout.
- The application remains in the connection process for longer than expected.
- The server cannot be contacted using the supplied connection parameters.
- The client reports that no response was received from the server.

During asynchronous connection procedures, PostgreSQL provides connection states that can help identify the stage of the connection process.

Examples include:

- `CONNECTION_STARTED` — waiting for the connection to be made.
- `CONNECTION_MADE` — connection established and waiting to send.
- `CONNECTION_AWAITING_RESPONSE` — waiting for a response from the server.
- `CONNECTION_AUTH_OK` — authentication has been received and backend startup is continuing.
- `CONNECTION_SSL_STARTUP` — SSL negotiation is in progress.

## Common Causes

A connection timeout can occur when the client cannot successfully establish communication with the intended PostgreSQL server.

Relevant areas to investigate include:

- Incorrect hostname.
- Incorrect IP address.
- Incorrect port number.
- Network connectivity problems.
- Firewall or network access restrictions.
- PostgreSQL server availability.
- Incorrect connection parameters.
- Problems resolving the specified hostname.
- Server configuration that prevents the requested connection.

A timeout alone does not identify the exact root cause. Additional investigation is required.

## Diagnostic Steps

### 1. Verify the Host

Check that the hostname or IP address in the connection configuration points to the intended PostgreSQL server.

### 2. Verify the Port

Check the configured PostgreSQL port.

For example:

host=DB-02 port=5432

The port should correspond to the PostgreSQL service that the client is expected to reach.

### 3. Check the Connection Parameters

Review the complete connection configuration, including:

- Host
- Port
- Database name
- User
- Connection timeout
- SSL-related settings when applicable

### 4. Check Server Availability

PostgreSQL provides the `PQping` and `PQpingParams` functions for checking server status.

Possible results include:

- `PQPING_OK` — the server is running and appears to be accepting connections.
- `PQPING_REJECT` — the server is running but currently disallows connections.
- `PQPING_NO_RESPONSE` — the server could not be contacted. This may indicate that the server is not running, incorrect connection parameters such as the port were supplied, or there is a network connectivity problem.
- `PQPING_NO_ATTEMPT` — no attempt was made because the supplied parameters were obviously incorrect or a client-side problem occurred.

### 5. Check the Connection Status

When using PostgreSQL asynchronous connection functions, the application can check the connection status to determine the current stage of connection establishment.

For example:

`CONNECTION_STARTED`

indicates that the connection is waiting to be made.

`CONNECTION_AWAITING_RESPONSE`

indicates that the client is waiting for a response from the server.

### 6. Check the Configured Timeout

Verify whether `connect_timeout` has been configured.

An unspecified, zero, or negative value means that the client can wait indefinitely.

### 7. Investigate Network Connectivity

If the PostgreSQL server cannot be contacted, investigate the network path between the client and server.

Possible areas include:

- Network connectivity
- Firewall configuration
- Hostname resolution
- Server availability
- Incorrect port configuration

These checks should be performed based on the actual evidence available from the environment.

## Resolution / Recommended Actions

- Correct the PostgreSQL hostname or IP address if it is incorrect.
- Correct the configured port if it does not point to the intended PostgreSQL service.
- Verify that the requested PostgreSQL server is available.
- Verify network connectivity between the client and server.
- Review firewall or network access configuration where applicable.
- Correct invalid connection parameters.
- Configure an appropriate `connect_timeout` value when the application should not wait indefinitely.
- After making the required correction, test a new database connection.

For example:

host=DB-02 port=5432 dbname=mydb connect_timeout=10

The appropriate timeout value depends on the application's requirements and environment.

## Important Notes / Limitations

- `connect_timeout` controls connection establishment. It should not be confused with a query or statement execution timeout.
- If `connect_timeout` is zero, negative, or unspecified, PostgreSQL can wait indefinitely.
- The connection timeout is specified in seconds.
- PostgreSQL supports both keyword/value connection strings and connection URIs.
- PostgreSQL supports multiple hosts in a connection configuration. Hosts can be tried in the specified order.
- When using `PQconnectPoll`, the `connect_timeout` parameter is ignored. The application is responsible for determining whether the connection attempt has taken too long.
- A connection timeout does not by itself prove that the PostgreSQL server is down.
- A `PQPING_NO_RESPONSE` result can have several possible explanations, including an unavailable server, an incorrect port, or a network connectivity problem.
- The exact cause should be determined using additional diagnostic information rather than assumed from the timeout alone.

## Source

PostgreSQL Official Documentation:

1. Database Connection Control Functions  
   https://www.postgresql.org/docs/current/libpq-connect.html

2. PostgreSQL Client Connection Defaults  
   https://www.postgresql.org/docs/current/runtime-config-client.html