# DNS Lookup — dig & nslookup

Commands for querying DNS servers to resolve hostnames to IP addresses (or vice versa). Use these to debug DNS resolution issues — verify that a hostname resolves correctly, check which DNS server is answering, and inspect the full DNS response.

There are two commands: `dig` (the modern, detailed tool) and `nslookup` (simpler, available on most systems including Windows). Both query DNS; `dig` gives more control and detail.

---

## Table of Contents

- [dig](#dig)
- [nslookup](#nslookup)
- [When to use which](#when-to-use-which)

---

## `dig`

`dig` (Domain Information Groper) queries a DNS server and shows the full response, including the answer, the server that responded, and the query time.

**Basic usage:**

```bash
dig <hostname>                  # query the default DNS server for an A record
dig <hostname> @<server>        # query a specific DNS server
dig -x <ip>                     # reverse DNS lookup (IP → hostname)
dig <hostname> AAAA             # query for IPv6 address
dig <hostname> MX               # query for mail server records
dig <hostname> NS               # query for nameservers
dig <hostname> SOA              # query for Start of Authority (zone info)
dig <hostname> TXT              # query for TXT records (SPF, verification, etc.)
dig <hostname> ANY              # request all available record types
dig <hostname> +short           # compact output — just the answer
dig <hostname> +noall +answer   # suppress everything except the answer section
dig <hostname> +trace           # trace the full resolution path from root to answer
```

**Example — full query:**

```
poetoec@lab-router:~ $ dig google.com

; <<>> DiG 9.18.28 <<>> google.com
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 12345
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; QUESTION SECTION:
;google.com.                    IN      A

;; ANSWER SECTION:
google.com.             300     IN      A       142.250.185.110

;; Query time: 12 msec
;; SERVER: 192.168.2.254#53(192.168.2.254) (UDP)
;; WHEN: Thu Aug 14 12:00:00 CEST 2026
;; MSG SIZE  rcvd: 55
```

**Header flags:**

The line `flags: qr rd ra` contains single-letter flags describing the query and response:

| Flag | Name | Description |
|------|------|-------------|
| `qr` | Query Response | This is a response (not a query). |
| `rd` | Recursion Desired | The client asked the server to resolve recursively (follow the chain of nameservers on its behalf). |
| `ra` | Recursion Available | The server supports recursion. |
| `aa` | Authoritative Answer | The responding server is the authoritative nameserver for this domain (not a cache). Absent here because the ISP modem's resolver is a cache, not the authority for `google.com`. |
| `tc` | Truncated | Response was too large for UDP and was truncated — the client should retry over TCP. |
| `ad` | Authenticated Data | DNSSEC validation passed — the response is cryptographically verified. |
| `cd` | Checking Disabled | The client asked the server to skip DNSSEC validation. |

The `status` field shows the result: `NOERROR` = success, `NXDOMAIN` = domain does not exist, `SERVFAIL` = server error (e.g. upstream unreachable or DNSSEC failure), `REFUSED` = server refused the query.

The counters (`QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1`) show how many records are in each section of the response.

**Answer format:**

Each line in the ANSWER section has five columns:

```
google.com.             300     IN      A       142.250.185.110
<name>                  <TTL>   <class> <type>  <data>
```

| Column | Description |
|--------|-------------|
| `<name>` | The domain name this record belongs to. The trailing `.` is the DNS root — all fully qualified domain names end with it. |
| `<TTL>` | Time To Live in seconds — how long this answer may be cached. `300` = 5 minutes. After this, the resolver must re-query. |
| `<class>` | Almost always `IN` (Internet). Other classes exist (`CH`, `HS`) but are rarely used. |
| `<type>` | Record type — see table below. |
| `<data>` | The record value — an IP address, hostname, or other data depending on the type. |

**Common record types in detail:**

| Type | Description | Example Data |
|------|-------------|--------------|
| `A` | IPv4 address | `142.250.185.110` |
| `AAAA` | IPv6 address | `2a00:1450:400e:811::200e` |
| `CNAME` | Alias — points to another hostname (the "canonical name"). The resolver follows the chain until it reaches an A/AAAA record. | `www.google.com. → www.google.com.cdn.example.net.` |
| `MX` | Mail exchanger — where to deliver email for this domain. Includes a priority (lower = preferred). | `10 smtp.google.com.` |
| `NS` | Nameserver — the authoritative DNS servers for this domain. | `ns1.google.com.` |
| `TXT` | Arbitrary text — used for SPF (email anti-spoofing), domain verification, DKIM, etc. | `"v=spf1 include:_spf.google.com ~all"` |
| `SOA` | Start of Authority — zone metadata: primary nameserver, admin email, serial number, refresh/retry/expire timers. | `ns1.google.com. dns-admin.google.com. 2024010100 900 900 1800 60` |
| `PTR` | Pointer — reverse DNS, maps an IP back to a hostname. Used with `dig -x`. | `mijnmodem.kpn.` |
| `SRV` | Service locator — specifies host and port for a service (e.g. SIP, LDAP, Kubernetes API). | `0 5 5060 sip.example.com.` |

**Key sections:**

| Section | Description |
|---------|-------------|
| `QUESTION` | What was asked — the hostname and record type. |
| `ANSWER` | The response records matching the question. |
| `AUTHORITY` | The authoritative nameservers for the domain (usually present when the answer comes from a referral). |
| `ADDITIONAL` | Extra records provided to avoid follow-up queries (e.g. A records for the nameservers listed in AUTHORITY). |
| `SERVER` | Which DNS server answered (here: the ISP modem at `192.168.2.254`). |
| `Query time` | How long the lookup took — useful for comparing resolvers. |

**Example — short output:**

```
poetoec@lab-router:~ $ dig google.com +short
142.250.185.110
```

**Example — clean answer only:**

```bash
dig google.com +noall +answer
```

Suppresses the header, question, authority, and additional sections — shows only the answer lines. Useful for scripting or when you want a clean but not *too* short output (unlike `+short`, this still shows TTL and record type).

**Example — query a specific DNS server:**

```bash
dig google.com @8.8.8.8          # ask Google's public DNS directly
dig google.com @10.42.0.1        # ask the router's DNS (e.g. the homelab router)
```

Useful for verifying whether the lab's local DNS server resolves differently from a public one. For example, if `dig lab-node1.lab @10.42.0.1` returns an answer but `dig lab-node1.lab @8.8.8.8` returns `NXDOMAIN`, your local DNS is working correctly — public resolvers have no knowledge of private hostnames.

**Example — reverse DNS:**

```bash
dig -x 192.168.2.254 +short      # find the hostname for an IP
```

This sends a PTR query for `254.2.168.192.in-addr.arpa` — the special reversed-IP format used for reverse DNS.

**Example — trace full resolution path:**

```bash
dig google.com +trace
```

Shows every step of the resolution: root nameservers → `.com` TLD nameservers → `google.com` authoritative nameservers → final answer. Useful for debugging where in the chain a lookup breaks — if the trace stops at a certain level, that is where the problem is.

**Example — querying different record types:**

```bash
dig google.com MX +short          # mail servers
dig google.com NS +short          # authoritative nameservers
dig google.com TXT +short         # TXT records (SPF, verification)
dig google.com SOA +short         # zone authority info
```

**Useful flag combinations:**

| Command | Purpose |
|---------|---------|
| `dig <host> +short` | Quick answer only. |
| `dig <host> +noall +answer` | Answer with TTL and record type, no clutter. |
| `dig <host> +trace` | Trace full resolution chain from root. |
| `dig <host> @<server>` | Test a specific resolver. |
| `dig <host> +stats` | Show query time and server (default on, useful if disabled). |
| `dig -x <ip>` | Reverse DNS lookup. |

---

## `nslookup`

`nslookup` is a simpler DNS lookup tool. Less detailed than `dig`, but available on virtually every OS (Linux, macOS, Windows).

**Basic usage:**

```bash
nslookup <hostname>              # query the default DNS server
nslookup <hostname> <server>     # query a specific DNS server
nslookup <ip>                    # reverse DNS lookup
```

**Example:**

```
poetoec@lab-router:~ $ nslookup google.com
Server:         192.168.2.254
Address:        192.168.2.254#53

Non-authoritative answer:
Name:   google.com
Address: 142.250.185.110
```

- `Server` / `Address` — the DNS server that was queried.
- `Non-authoritative answer` — the response came from a cache (the recursive resolver), not directly from Google's authoritative nameserver. This is normal.

**Example — query a specific server:**

```
poetoec@lab-router:~ $ nslookup google.com 8.8.8.8
Server:         8.8.8.8
Address:        8.8.8.8#53

Non-authoritative answer:
Name:   google.com
Address: 142.250.185.110
```

---

## When to use which

| Tool | Best for |
|------|----------|
| `dig +short` | Quick "does this hostname resolve?" check. |
| `dig` (full) | Debugging DNS — see TTL, response status, which server answered, query time. |
| `dig @<server>` | Testing whether a specific DNS server (e.g. the lab router) resolves correctly. |
| `nslookup` | Quick lookups on any OS, especially Windows where `dig` is not installed by default. |
