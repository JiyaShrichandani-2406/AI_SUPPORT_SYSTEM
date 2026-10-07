# Infrastructure Networking Issues

## Metadata

Title: Network Troubleshooting
Product: Network Infrastructure
Product Version: General TCP/IP Networking
Source Type: Official Technical Documentation
Source Organization: Microsoft Learn
Topic: Network Connectivity and Troubleshooting
Source URL: https://learn.microsoft.com/en-us/windows-server/networking/
Last Updated: Current Microsoft Learn documentation
Collected On: September 19, 2026

## Problem / Overview

Network connectivity problems can prevent applications and services
from communicating with servers, databases, APIs, and other
network resources.

A networking problem can occur at different points in the
communication path, including the client, local network, DNS
resolution, routing, firewall, server, or application layer.

Troubleshooting should therefore identify the layer at which the
communication fails instead of assuming that the server or
application is the cause.

## Symptoms

Common networking symptoms include:

- Application cannot connect to a server.
- Connection times out.
- Connection is refused.
- Host cannot be reached.
- DNS name cannot be resolved.
- Network requests fail intermittently.
- API requests cannot reach the destination server.
- Database connections cannot be established.
- Services become unreachable from a particular client or network.

## Common Causes

Potential causes include:

- Incorrect IP configuration.
- Incorrect hostname or IP address.
- DNS resolution problems.
- Network connectivity problems.
- Routing problems.
- Firewall restrictions.
- Server not listening on the expected address or port.
- Incorrect port configuration.
- Network service unavailable.
- Intermediate network device or proxy problems.

The exact cause must be determined from the available diagnostic
evidence.

## Diagnostic Steps

### 1. Check Local IP Configuration

Verify the affected machine's:

- IP address
- Subnet mask
- Default gateway
- Configured DNS servers

On Windows, the following command can be used:

ipconfig /all

### 2. Check Name Resolution

Determine whether the hostname resolves to the expected IP address.

On Windows, `nslookup` can be used to query DNS.

Example:

nslookup example.com

### 3. Check Server Reachability

Determine whether the destination server can be reached from the
affected client.

Check the network path and compare results from an unaffected
machine when appropriate.

### 4. Check the Destination Port

If an application uses a specific TCP port, verify that the service
is listening on the expected port and that network or firewall
configuration does not block access.

### 5. Check Firewall Configuration

Review firewall rules on the client, server, and relevant network
devices.

Determine whether the required traffic is being blocked.

### 6. Check DNS Separately

If the hostname does not resolve, troubleshoot DNS before treating
the problem as an application or server failure.

### 7. Check Logs

Review relevant:

- Application logs
- System logs
- Network-device logs
- DNS logs
- Server logs

### 8. Compare With Another Client

If possible, test the same destination from another client or
network.

If the problem occurs only on one client, investigate that client's
configuration.

If the problem occurs from multiple clients, investigate shared
network, DNS, firewall, or server configuration.

## Resolution / Recommended Actions

- Correct incorrect IP configuration.
- Correct hostname or IP address configuration.
- Correct DNS configuration when name resolution fails.
- Verify that the destination service is running.
- Verify that the service is listening on the expected port.
- Correct firewall rules when legitimate traffic is being blocked.
- Correct routing or network configuration where required.
- Restart or restore an unavailable network service when appropriate.
- Retest connectivity after making a configuration change.

## Important Notes / Limitations

- A network timeout does not automatically mean that the destination
  server is down.
- DNS failure and network connectivity failure are different
  problems and should be investigated separately.
- Firewall filtering can make a reachable service appear unavailable.
- Troubleshooting should begin with the affected client and the
  specific network path involved.
- Diagnostic commands and available logs depend on the operating
  system and network environment.
- Do not store passwords, private keys, API credentials, or other
  secrets in the Knowledge Base.

## Source

Microsoft Learn:

Troubleshooting DNS Servers
https://learn.microsoft.com/en-us/windows-server/networking/dns/troubleshoot/troubleshoot-dns-server

Troubleshooting DNS Issues
https://learn.microsoft.com/en-us/windows-server/networking/dns/troubleshoot/troubleshoot-dns-data-collection