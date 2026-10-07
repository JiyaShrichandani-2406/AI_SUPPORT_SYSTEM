# DNS Issues

## Metadata

Title: General DNS Issues and Troubleshooting
Product: Domain Name System (DNS)
Product Version: Current DNS Standards / Services
Source Type: Official Technical Documentation
Source Organization: Cloudflare
Topic: DNS Resolution and Troubleshooting
Source URL: https://developers.cloudflare.com/dns/troubleshooting/dns-issues/
Last Updated: April 16, 2026
Collected On: September 19, 2026

## Problem / Overview

The Domain Name System (DNS) translates domain names and hostnames
into information such as IP addresses that clients can use to
connect to services.

When DNS resolution fails, an application or browser may be unable
to reach the intended service even when the service itself is
running.

DNS problems can occur because of incorrect records, incorrect
nameservers, DNSSEC configuration, resolver problems, caching, or
incorrect hostnames.

## Symptoms

Common DNS-related symptoms include:

- "This site can't be reached."
- "This webpage is not available."
- `ERR_NAME_NOT_RESOLVED`
- "Can't find the server."
- `DNS_PROBE_FINISHED_NXDOMAIN`
- `DNS_PROBE_POSSIBLE`
- Hostname resolves to the wrong IP address.
- Newly created DNS records do not resolve immediately.
- Some clients resolve the hostname while others do not.

## Common Causes

Common DNS causes include:

- Misspelled domain or subdomain.
- Missing DNS record.
- Incorrect DNS record.
- Incorrect IP address in a DNS record.
- Incorrect nameserver configuration.
- DNSSEC configuration problems.
- DNS resolver problems.
- DNS caching.
- Negative DNS caching.
- Incorrect CNAME configuration.
- DNS server unavailable or unreachable.

## Diagnostic Steps

### 1. Verify the Hostname

Check that the domain or hostname is spelled correctly.

For example:

example.com

and:

www.example.com

may have separate DNS records.

### 2. Check DNS Records

Verify that the expected DNS records exist.

Depending on the service, this may include:

- A records
- AAAA records
- CNAME records
- MX records
- NS records

### 3. Check the Returned IP Address

Verify that the hostname resolves to the expected destination
address.

An incorrect IP address can cause the client to connect to the
wrong server or fail to connect.

### 4. Check Nameservers

Verify that the domain's nameservers are correctly configured.

If the domain is managed through a DNS provider, confirm that the
registrar delegates the domain to the expected nameservers.

### 5. Check DNSSEC

If DNSSEC is enabled, verify that the DNSSEC configuration is
consistent.

Incorrect DNSSEC configuration can cause DNS resolution failures.

### 6. Check for NXDOMAIN

`NXDOMAIN` indicates that the requested domain name does not exist
according to the DNS response.

For:

DNS_PROBE_FINISHED_NXDOMAIN

check whether the required DNS record exists.

### 7. Check DNS Caching

Recently created or modified DNS records may not appear immediately
at every resolver.

DNS resolvers can cache responses.

Negative responses can also be cached. This means a resolver may
continue returning a previous "does not exist" result for some time
after a DNS record has been created.

### 8. Compare Different DNS Resolvers

If possible, compare resolution results from different DNS resolvers.

For example:

dig example.com @1.1.1.1

and:

dig example.com @8.8.8.8

Different results can help identify resolver or caching-related
issues.

### 9. Query the Authoritative Nameserver

When appropriate, query the authoritative nameserver directly.

This can help determine whether the DNS record exists at the
authoritative source or whether the problem is related to resolver
caching.

## Resolution / Recommended Actions

- Correct misspelled domain or subdomain names.
- Create missing DNS records.
- Correct incorrect DNS records.
- Correct an incorrect IP address.
- Correct CNAME configuration.
- Verify that the domain uses the intended nameservers.
- Correct DNSSEC configuration when applicable.
- Allow appropriate DNS cache periods to expire after changes.
- Compare resolver responses when troubleshooting inconsistent
  resolution.
- Query authoritative nameservers when necessary to distinguish
  authoritative configuration problems from resolver caching.

## Important Notes / Limitations

- `NXDOMAIN` means that the DNS response indicates that the requested
  domain name does not exist.
- A DNS resolution problem does not necessarily mean that the
  destination server is unavailable.
- DNS changes may not become visible to every resolver immediately.
- Negative caching can cause a newly created record to continue
  returning an earlier `NXDOMAIN` response until the cached response
  expires.
- Clearing the local DNS cache affects the local device but does not
  necessarily clear upstream recursive resolver caches.
- DNSSEC problems can prevent successful DNS resolution.
- DNS behavior depends on the resolver, authoritative DNS provider,
  domain configuration, and caching state.

## Source

Cloudflare Official DNS Documentation:

General DNS Issues
https://developers.cloudflare.com/dns/troubleshooting/dns-issues/

DNS_PROBE_FINISHED_NXDOMAIN
https://developers.cloudflare.com/dns/troubleshooting/dns-probe-finished-nxdomain/

DNS Troubleshooting
https://developers.cloudflare.com/dns/troubleshooting/

Microsoft Learn:

Troubleshooting DNS Servers
https://learn.microsoft.com/en-us/windows-server/networking/dns/troubleshoot/troubleshoot-dns-server