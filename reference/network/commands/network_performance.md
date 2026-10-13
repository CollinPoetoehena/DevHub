# Network Performance Testing

Commands for measuring network bandwidth, throughput, latency, and jitter between hosts. Use these to verify link capacity, diagnose bottlenecks, and baseline network performance.

---

## Table of Contents

- [iperf3 — Bandwidth Measurement](#iperf3--bandwidth-measurement)

---

## `iperf3` — Bandwidth Measurement

Measures maximum achievable bandwidth between two endpoints by generating traffic between a client and a server. One host runs in server mode (listening), the other in client mode (sending). Use it to verify link speed, test throughput between subnets, or diagnose congestion.

**Architecture:** iperf3 always requires two sides — a **server** (passive, waits for connections) and a **client** (active, initiates the test and generates traffic). The client controls all test parameters.

**Basic usage:**

```bash
# Server side (run on the host you want to test TO):
iperf3 -s                              # listen on default port 5201

# Client side (run on the host you want to test FROM):
iperf3 -c <server-ip>                  # TCP upload test to server (default: 10 seconds)
iperf3 -c <server-ip> -R               # reverse — server sends TO client (download test)
iperf3 -c <server-ip> -u -b 100M       # UDP test at 100 Mbit/s target rate
iperf3 -c <server-ip> -t 30            # run for 30 seconds instead of default 10
iperf3 -c <server-ip> -P 4             # 4 parallel streams (saturate the link)
```

**Common flags — server:**

| Flag | Description |
|------|-------------|
| `-s` | Run in server mode — listen for incoming client connections. |
| `-p <port>` | Listen on a specific port (default: 5201). |
| `-D` | Run as a daemon (background). |
| `-1` | Handle one client connection and exit (useful for scripted tests). |

**Common flags — client:**

| Flag | Description |
|------|-------------|
| `-c <host>` | Run in client mode — connect to the server at `<host>`. |
| `-t <seconds>` | Test duration (default: 10 seconds). |
| `-n <bytes>` | Transfer a fixed amount of data instead of running for a time (e.g. `-n 1G`). |
| `-P <streams>` | Number of parallel TCP streams. Useful for saturating high-bandwidth links where a single stream is window-limited. |
| `-R` | Reverse mode — server sends, client receives. Without this, client sends (upload test). |
| `-u` | Use UDP instead of TCP. Must specify target bandwidth with `-b`. |
| `-b <rate>` | Target bandwidth for UDP tests (e.g. `100M`, `1G`). For TCP, sets a rate cap (default: unlimited). |
| `-w <size>` | Set TCP window size / socket buffer size (e.g. `-w 256K`). Affects throughput on high-latency links. |
| `-i <seconds>` | Reporting interval (default: 1 second). |
| `-J` | JSON output — machine-readable results. |
| `-4` / `-6` | Force IPv4 or IPv6. |
| `--bidir` | Bidirectional test — simultaneous upload and download. |

**Output format (TCP):**

```
[ ID] Interval           Transfer     Bitrate         Retr  Cwnd
[  5]   0.00-1.00   sec   112 MBytes   941 Mbits/sec    0    320 KBytes
[  5]   1.00-2.00   sec   112 MBytes   940 Mbits/sec    0    320 KBytes
...
[  5]   0.00-10.00  sec  1.09 GBytes   940 Mbits/sec    0             sender
[  5]   0.00-10.00  sec  1.09 GBytes   939 Mbits/sec                  receiver
```

**Key fields:**

| Field | Description |
|-------|-------------|
| `Interval` | Time window for this measurement line. |
| `Transfer` | Amount of data transferred in the interval. |
| `Bitrate` | Throughput — the key metric. Compare to the expected link speed. |
| `Retr` | TCP retransmissions — non-zero indicates packet loss or congestion. |
| `Cwnd` | TCP congestion window size — how much data TCP sends before waiting for ACKs. |
| `sender` / `receiver` | Final summary from each side's perspective — small differences are normal (in-flight data). |

**Output format (UDP):**

```
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-10.00  sec  119 MBytes   100 Mbits/sec  0.045 ms  3/86145 (0.0035%)  receiver
```

**Additional UDP fields:**

| Field | Description |
|-------|-------------|
| `Jitter` | Variation in packet arrival time — lower is better. High jitter causes issues for real-time applications (VoIP, video). |
| `Lost/Total` | Packets lost vs total sent — indicates link quality. |

**Examples — common use cases:**

```bash
# Test throughput between router and a lab host:
# On the router (server):
iperf3 -s

# On the management VM (client) — upload test:
iperf3 -c 10.42.0.1

# Download test (server sends to client):
iperf3 -c 10.42.0.1 -R

# Saturate a gigabit link with parallel streams:
iperf3 -c 10.42.0.1 -P 4

# UDP test at 500 Mbit/s — measure jitter and packet loss:
iperf3 -c 10.42.0.1 -u -b 500M

# Bidirectional test — upload and download simultaneously:
iperf3 -c 10.42.0.1 --bidir

# Long-running test to check for intermittent issues:
iperf3 -c 10.42.0.1 -t 60

# Test across subnets (from home network to lab through the router):
# Server on lab host 10.42.0.168:
iperf3 -s
# Client from home network device:
iperf3 -c 10.42.0.168
```

**Example — TCP test between mgmtvm and router:**

```
poetoec@mgmtvm:~ $ iperf3 -c 10.42.0.1
Connecting to host 10.42.0.1, port 5201
[  5] local 10.42.0.168 port 43210 connected to 10.42.0.1 port 5201
[ ID] Interval           Transfer     Bitrate         Retr  Cwnd
[  5]   0.00-1.00   sec   112 MBytes   941 Mbits/sec    0    320 KBytes
[  5]   1.00-2.00   sec   112 MBytes   940 Mbits/sec    0    320 KBytes
[  5]   2.00-3.00   sec   112 MBytes   940 Mbits/sec    0    320 KBytes
[  5]   3.00-4.00   sec   112 MBytes   941 Mbits/sec    0    320 KBytes
[  5]   4.00-5.00   sec   112 MBytes   940 Mbits/sec    0    320 KBytes
[  5]   5.00-6.00   sec   112 MBytes   940 Mbits/sec    0    320 KBytes
[  5]   6.00-7.00   sec   112 MBytes   941 Mbits/sec    0    320 KBytes
[  5]   7.00-8.00   sec   112 MBytes   940 Mbits/sec    0    320 KBytes
[  5]   8.00-9.00   sec   112 MBytes   940 Mbits/sec    0    320 KBytes
[  5]   9.00-10.00  sec   112 MBytes   941 Mbits/sec    0    320 KBytes
- - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Retr
[  5]   0.00-10.00  sec  1.09 GBytes   940 Mbits/sec    0             sender
[  5]   0.00-10.00  sec  1.09 GBytes   939 Mbits/sec                  receiver

iperf Done.
```

- ~940 Mbit/s on a gigabit link — expected (TCP overhead reduces theoretical 1000 to ~940).
- 0 retransmissions — clean link with no packet loss.
- Consistent bitrate across all intervals — no congestion or buffering issues.

**Example — UDP test with jitter measurement:**

```
poetoec@mgmtvm:~ $ iperf3 -c 10.42.0.1 -u -b 100M
Connecting to host 10.42.0.1, port 5201
[  5] local 10.42.0.168 port 55432 connected to 10.42.0.1 port 5201
[ ID] Interval           Transfer     Bitrate         Total Datagrams
[  5]   0.00-10.00  sec   119 MBytes   100 Mbits/sec  86145
- - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-10.00  sec   119 MBytes   100 Mbits/sec  0.045 ms  3/86145 (0.0035%)  receiver

iperf Done.
```

- 100 Mbit/s achieved as requested — link can handle this rate.
- 0.045 ms jitter — excellent, suitable for real-time traffic.
- 3 packets lost out of 86145 (0.0035%) — negligible loss.

**Interpreting results:**

| Symptom | Meaning |
|---------|---------|
| Bitrate matches link speed (~940 Mbit/s for gigabit) | Link is healthy and performing at capacity. |
| Bitrate significantly below link speed | Bottleneck — could be CPU (on slow devices like Raspberry Pi), duplex mismatch, cable quality, or congestion. |
| High retransmissions (`Retr`) | Packet loss on the path — bad cable, congested switch, or buffer overflow. |
| Bitrate fluctuates between intervals | Intermittent congestion or shared medium interference (WiFi). |
| UDP loss > 1% | Link cannot sustain the requested rate — reduce `-b` or investigate the bottleneck. |
| High jitter (> 1 ms on a LAN) | Bufferbloat, congested switch, or CPU overload on the endpoint. |
| `-P 4` gives much higher throughput than `-P 1` | Single-stream throughput limited by TCP window or CPU — common on high-latency or high-bandwidth links. |
| Upload fast but download slow (or vice versa) | Asymmetric link, duplex mismatch, or one-directional congestion. Use `-R` and `--bidir` to compare. |

> **Tip:** When testing Raspberry Pi or low-power devices, the CPU often becomes the bottleneck before the network does. If you see unexpectedly low throughput, check `top` on both ends during the test — if iperf3 or `ksoftirqd` is at 100% CPU, the device cannot push/receive data fast enough.
