# Setup & Installation: Network

> **TODO — future home context:** Present this setup as the network for my own home, which I can follow when I have my own home, but not yet while I live with my parents. The existing homelab hardware can be reused and only the Wi-Fi access points still need buying; refer to [Networking Hardware](../1_Design/1_Design_Hardware_Prerequisites.md#part-1--networking-hardware). This note is a pending documentation task, not an instruction to change the setup steps below. **The documentation does NOT need to be changed for this, this note is only for future context so that I am reminded for myself this was my intended setup and goal.**

This guide implements the [shared home-and-lab network design](../1_Design/3_Design_Network.md) with the selected UniFi Cloud Gateway Max, Lite 8 PoE switch, and two wired U6+ APs. One physical gateway serves separate logical networks and hosts their network management. See [Networking Hardware](../1_Design/1_Design_Hardware_Prerequisites.md#part-1--networking-hardware) for the equipment and [Router & Firewall Software](../1_Design/2_Design_Software_Prerequisites.md#router--firewall-software) for the software decision.

UniFi OS and Network run on the gateway itself. Its optional camera-recording SSD is not needed for routing, firewalling, or managing the switch/APs; see the [no-storage gateway decision](../1_Design/1_Design_Hardware_Prerequisites.md#router--firewall-cloud-gateway-max).

> **Chosen setup, example values only:** VLAN IDs, subnets, port numbers, SSID labels, and addresses below illustrate this setup; they are not a live inventory. Substitute the privately recorded values consistently. Follow [Security and Public Repository](../0_Security_and_Public_Repository.md), including its [safe-documentation guidance](../0_Security_and_Public_Repository.md#information-that-is-usually-safe-to-document). Never publish real WAN addresses, global IPv6 prefixes, credentials, Wi-Fi passwords, recovery codes, or unredacted exports/screenshots.

**Validation status:** these are setup instructions, not evidence that the live network has passed them. Record installed versions and completed checks privately. GUI labels can change between UniFi Network releases; the paths below follow Ubiquiti's documentation. Verify the corresponding setting on the installed version instead of substituting an unrelated option.

## Table of Contents

- [Step 1: Prepare the Equipment and Network Plan](#step-1-prepare-the-equipment-and-network-plan)
- [Step 2: Connect and Initialize the Gateway](#step-2-connect-and-initialize-the-gateway)
- [Step 3: Adopt the Switch and Access Points](#step-3-adopt-the-switch-and-access-points)
- [Step 4: Create the Networks](#step-4-create-the-networks)
- [Step 5: Configure Firewall Policy](#step-5-configure-firewall-policy)
- [Step 6: Assign Ports and Move Device Management](#step-6-assign-ports-and-move-device-management)
- [Step 7: Configure Wi-Fi](#step-7-configure-wi-fi)
- [Step 8: Connect Household and Lab Clients](#step-8-connect-household-and-lab-clients)
- [Step 9: Validate the Setup](#step-9-validate-the-setup)
- [Step 10: Back Up and Maintain the Network](#step-10-back-up-and-maintain-the-network)
- [Recovery and Troubleshooting](#recovery-and-troubleshooting)
- [Future VPN and IPv6 Work](#future-vpn-and-ipv6-work)

TODO: the setup below is generated with AI, it is checked and looks good but follow the steps and change where needed if anything is found to be incorrect/can be improved, etc.!

---

## Step 1: Prepare the Equipment and Network Plan

Prepare the equipment, addressing, ISP requirements, and recovery access before installation, following the [design's maintenance and recovery requirements](../1_Design/3_Design_Network.md#maintenance-recovery-and-safe-experiments).

1. Choose suitable locations for the gateway, switch, and APs, with power, ventilation, and wired backhaul. Schedule any service interruptions with the people who depend on the connection.
2. Prepare the gateway and its power supply, switch and its power adapter, two APs, Ethernet cables, and a laptop with wired Ethernet. Check [cabling](../1_Design/1_Design_Hardware_Prerequisites.md#ethernet-cables), ventilation, and [PoE capacity](../1_Design/1_Design_Hardware_Prerequisites.md#managed-switch). The gateway has no Wi-Fi or PoE output; power the APs from the switch's PoE+ ports.
3. Privately record ISP connection requirements: DHCP, PPPoE credentials, static addressing, or provider VLAN tagging as applicable. Confirm bridge/passthrough support and any TV/voice dependencies using the [core/edge design](../1_Design/3_Design_Network.md#core--edge-layer).
4. Check proposed subnets against the upstream LAN, VPN routes, and cluster pod/service ranges. Use the [addressing design](../1_Design/3_Design_Network.md#ipv4-addressing); do not assume its example addresses are suitable unchanged.
5. Prepare secure storage for local backups and administrator credentials outside Git and outside lab-only storage. Keep ISP settings and recovery instructions accessible if the gateway or lab is offline.
6. Initially connect only trusted setup equipment. Keep household, lab, IoT, and guest clients disconnected until their segmentation is ready. Ensure the gateway is the intended DHCP server and, if IPv6 is enabled later, the intended router advertising prefixes on each segment; do not attach competing routers or DHCP servers.

---

## Step 2: Connect and Initialize the Gateway

Follow Ubiquiti's [How to Set Up UniFi](https://help.ui.com/hc/en-us/articles/4416276882327) for the console wizard.

1. Connect the modem's LAN/handoff to the gateway port identified as WAN. Connect the laptop directly to a gateway LAN port and power the gateway with its own adapter. Leave other clients disconnected.
2. For initial staging, it is acceptable to leave the ISP device routing and obtain a private WAN lease on the gateway, provided the downstream LAN does not overlap it. This is temporary double NAT, not the final segmentation policy. If an upstream DHCP reservation is used, keep it private.
3. Open the gateway's local setup page using the address shown on its display or the laptop's DHCP default gateway. Alternatively, use the UniFi mobile app with Bluetooth near the gateway. Do not assume the example management address below is already configured.
4. Complete the wizard with the actual WAN connection type. A provider WAN VLAN is distinct from the internal VLAN IDs in [Step 4](#step-4-create-the-networks). Verify internet access from the wired laptop before continuing.
5. Configure a strong administrator credential. If using a UI Account, enable MFA and securely store recovery codes. Establish and test local administrative access supported by the installed UniFi OS so recovery is not dependent solely on cloud sign-in.
6. Review remote console access separately from WAN firewall management: a cloud-management feature can exist without an inbound port forward. Leave remote access disabled unless deliberately required. Do not expose the console, SSH, or device-adoption ports to the internet.
7. Install suitable official/stable UniFi OS and Network updates before connecting clients, following release notes. Record versions privately; do not use early-access firmware for the essential household network.
8. Preserve a direct wired bootstrap connection and save an initial private backup using [Step 10](#step-10-back-up-and-maintain-the-network).

Where supported, perform the final ISP bridge/passthrough change during the maintenance window, configure the gateway's corresponding WAN settings, and recheck internet/TV/voice services. If it fails, restore the known-good modem mode. If bridge mode is unavailable, document double NAT and ISP carrier-grade NAT limitations under the [WAN design](../1_Design/3_Design_Network.md#core--edge-layer). Do not disable all firewalls as a troubleshooting shortcut.

---

## Step 3: Adopt the Switch and Access Points

Use [UniFi Device Adoption](https://help.ui.com/hc/en-us/articles/360012622613). Initially keep the devices on the gateway's default/bootstrap LAN, connected only to trusted setup equipment.

1. Connect a gateway LAN port to the Lite 8 PoE switch and power the switch with its supplied adapter. One uplink is enough; do not create a loop with a second cable.
2. In UniFi Network's **Devices** view, adopt the switch if it is pending adoption. Confirm it becomes online before changing VLAN settings.
3. Connect each U6+ to one of the switch's four PoE+ ports. Adopt both APs into the gateway's Network application, not standalone mode or a separate controller.
4. Check that both APs have a wired uplink and remain online after provisioning. Install compatible official firmware, one device at a time.
5. Record physical port roles privately. Give devices clear role labels without publishing identifying hostnames or hardware IDs.
6. Check the PoE budget: two APs at their published maximum of 9 W each fit within the switch's 52 W budget. Recalculate before adding more powered devices.

Do not enable household SSIDs yet. Configure management only after networks, firewall policy, and the tagged path are prepared in [Steps 4–6](#step-4-create-the-networks). If a device is managed by another console, verify ownership and follow Ubiquiti's device-adoption guidance; factory reset only the specific device deliberately being reprovisioned.

---

## Step 4: Create the Networks

In **UniFi Network > Settings > Networks**, create each virtual network with the **Cloud Gateway as its router**, following [Creating Virtual Networks](https://help.ui.com/hc/en-us/articles/9761080275607). Do not choose a third-party gateway or a VLAN-only definition: this gateway must provide routing and DHCP.

Use the [chosen segment roles and example VLAN plan](../1_Design/3_Design_Network.md#subnet--vlan-design):

| Network role | Example VLAN ID | Example gateway / subnet | DHCP intent |
|---|---|---|---|
| Management | 10 | 10.42.10.1/24 | Infrastructure reservations and trusted administration |
| Lab | 20 | 10.42.20.1/24 | Lab VMs and cluster nodes as required |
| IoT | 30 | 10.42.30.1/24 | Constrained devices |
| Home | 40 | 10.42.40.1/24 | Household clients |
| Guest | 50 | 10.42.50.1/24 | Visitor clients |

1. Set each network's name, VLAN ID, gateway/subnet, and non-overlapping DHCP pool explicitly. For example, a pool of `.100`–`.199` leaves room for infrastructure addresses in each `/24`; use private reservations and exclude manually assigned addresses from the pool.
2. Configure client DNS to use the gateway's supported DNS forwarding service, with suitable upstream resolvers. Do not make household DNS depend on lab compute or a cluster service.
3. Leave cross-VLAN mDNS/service discovery disabled unless a specific documented use requires it. Do not enable blanket discovery or UPnP to make segmentation problems disappear.
4. Start with IPv4. Disable WAN/LAN IPv6 configuration for this baseline until [IPv6 rollout](#future-vpn-and-ipv6-work) is deliberately validated. IPv6 link-local addresses may still exist; they do not prove routed internet connectivity.
5. Keep the original Default/bootstrap network temporarily for trusted provisioning and rollback. It is not Home and not a permanent unfiltered sixth client network. Do not delete or renumber the path currently used for administration before testing its replacement.

**Creating VLANs is not isolation.** New networks may inherit permissive inter-network policies; configure [Step 5](#step-5-configure-firewall-policy) before attaching untrusted clients.

---

## Step 5: Configure Firewall Policy

Implement the [design's firewall and access matrix](../1_Design/3_Design_Network.md#firewall-and-access-policy), not just a "guest" label. Use Ubiquiti's [Zone-Based Firewall](https://help.ui.com/hc/en-us/articles/115003173168-Zone-Based-Firewalls-in-UniFi) and [Traffic Policy Management](https://help.ui.com/hc/en-us/articles/5546542486551) guides.

In Network 9.4, policy creation is documented under **Settings > Zones > Create Policy** or **Settings > Policy Table > Create New Policy**; Network 9.3 uses **Settings > Policy Engine > Zones**. Check the installed version. Older legacy firewall layouts require their corresponding documentation, not blindly translated clicks.

1. Give Management, Lab, IoT, Home, and Guest distinct custom zones and assign each network to its intended zone. Keep the bootstrap LAN limited to trusted setup use. **Do not assume the built-in Internal zone is default-deny**: its default policies can allow inter-network traffic.
2. Before adding deny rules, create narrow permissions for approved administrators to the Management zone and the **Gateway zone**. Gateway-zone rules protect services on the router itself; inter-VLAN rules alone do not restrict its console.
3. Permit the required gateway DHCP and DNS services from each served network. Permit device-management communication from switch/AP management addresses to the local Network application using Ubiquiti's [required-port reference](https://help.ui.com/hc/en-us/articles/218506997). Restrict those flows to the infrastructure devices; never forward adoption ports from WAN.
4. Allow only explicitly selected Home-to-Lab application endpoints and IoT-to-service flows, with destination addresses and ports. If none are needed, create no such exception.
5. Preserve established/related return traffic for allowed sessions. Use the policy's **Auto Allow Return Traffic** where needed, or verified stateful return rules. Deny unsolicited new connections in the reverse direction; do not replace that with a blanket bidirectional allow.
6. Add default-deny policies for other new connections between the custom zones and for client-to-Gateway traffic not explicitly required. This must deny gateway administration from ordinary Home, Lab, IoT, and Guest clients while preserving DHCP/DNS and the approved infrastructure/admin flows. Keep those exceptions above broader blocks. Inspect effective rule order, including built-in rules.
7. Allow internet access according to each segment's needs, while preserving stateful WAN protection against unsolicited inbound traffic. Check both directions in the zone matrix and review any automatically created exceptions.
8. Keep same-VLAN Management clients restricted to infrastructure and approved administrators. The gateway cannot filter traffic that stays entirely on that VLAN; use device account controls, host firewalls, or supported client isolation where required.
9. If IPv6 is later enabled, select rules matching both IP families and explicitly allow necessary IPv6 control traffic; do not assume IPv4 rules cover it. See [IPv6 Design and Rollout](../1_Design/3_Design_Network.md#ipv6-design-and-rollout).

Apply changes incrementally from the wired administrator connection. Test console access, DHCP/DNS, and switch/AP connectivity after each policy group. Do not accept a rule set that only appears correct in the UI; the endpoint tests in [Step 9](#step-9-validate-the-setup) are required.

---

## Step 6: Assign Ports and Move Device Management

Use [Switch Port VLAN Assignment](https://help.ui.com/hc/en-us/articles/26136855808919), [VLAN Troubleshooting](https://help.ui.com/hc/en-us/articles/9592924981911), and the [design's port-assignment explanation](../1_Design/3_Design_Network.md#switch-port-assignments). In UniFi's **Ports** view, set **Native VLAN / Network** and **Tagged VLAN Management**: **Block All** creates an access port; **Custom** permits only selected tagged VLANs. Avoid leaving **Allow All** everywhere.

For the example below, Management VLAN 10 is **tagged for infrastructure management** and the bootstrap network remains native on infrastructure trunks during configuration. This differs from the design's optional untagged-management variant but serves the same segment roles; do not mix both variants on the same link.

| Example switch port | Role | Native network | Tagged VLANs when configured |
|---|---|---|---|
| 1–2 (PoE+) | AP 1 and AP 2 | Bootstrap, with no ordinary clients | Management 10, IoT 30, Home 40, Guest 50 |
| 3–4 | Spare PoE ports | None in use; disabled | None |
| 5 | Gateway uplink | Bootstrap, matching gateway LAN port | Management 10, Lab 20, IoT 30, Home 40, Guest 50 |
| 6–7 | Lab host uplinks | Management 10 | Lab 20; additional segments only if needed |
| 8 | Wired administrator / local recovery | Management 10 | None |

These are example assignments, not a claim about installed cabling. If household wired devices need more ports, repurpose a spare as a Home access port or expand capacity. The switch's AP uplinks must carry Management 10 because the AP management override below uses tags.

1. Configure the gateway LAN uplink and switch uplink to permit all five required tagged VLANs, retaining their matching native/bootstrap network. Confirm the switch is still online.
2. Configure the dedicated administrator port as a Management access port: native Management, tagged VLANs blocked. Move the laptop there, renew its DHCP lease, and test the gateway's Management address and console login. Keep another known-working direct bootstrap path until this succeeds.
3. In the switch's device settings, use the supported management **Network Override** to select Management. The uplink must already carry VLAN 10 tagged. Confirm its new lease/reservation, online status, and reprovisioning before proceeding. Do not assume a switch management VLAN changes its uplink profile automatically.
4. For each AP, first permit Management and its intended SSID VLANs on the uplink, then select Management in the AP's **IP Settings / Network Override**. Confirm one AP stays online before configuring the other.
5. Only after management connectivity is verified, trim tagged allowances to the table. Keep AP native/bootstrap separate from the tagged SSID networks; Ubiquiti documents client-connectivity problems when an AP's non-default native VLAN also carries a broadcast SSID.
6. Configure lab host ports for the intended management variant. In this example, host management is **untagged on Management**, while VM Lab traffic is tagged. Align the host configuration in [Step 8](#step-8-connect-household-and-lab-clients); any host template must match this native/tagged choice.
7. Assign ordinary wired clients access ports with Home or IoT as native and tagged VLANs blocked. Disable unused ports.
8. Once all replacement paths are tested, remove temporary bootstrap allows and prevent bootstrap access to production networks/administration. Leave no ordinary devices or SSIDs on it. Document any retained native network's restrictions privately; it is not an automatic recovery backdoor.

Keep a physically controlled local Management access port for recovery, enabling it only when needed if normally disabled. A wrong trunk or override can disconnect a device; use [Recovery and Troubleshooting](#recovery-and-troubleshooting) rather than broadening every port or firewall permanently.

---

## Step 7: Configure Wi-Fi

Follow [Creating UniFi WiFi SSIDs](https://help.ui.com/hc/en-us/articles/26136823938583) and the [distribution/access design](../1_Design/3_Design_Network.md#distribution-and-access-layers).

1. In **Settings > WiFi**, create a small set of networks and select their corresponding virtual network in the **Network** dropdown:

   | Example SSID label | Network | Purpose |
   |---|---|---|
   | Home | Home / example VLAN 40 | Trusted household clients |
   | IoT | IoT / example VLAN 30 | Constrained devices |
   | Guest | Guest / example VLAN 50 | Visitor internet access |

2. Broadcast them on both wired APs as needed. Use privately stored strong passwords; no real SSIDs or credentials belong in this repository.
3. Use WPA2/WPA3 Personal with suitable protected-management-frame settings for supported clients. Prefer stronger modes when all clients support them; if IoT needs WPA2 compatibility, confine that change to the IoT SSID instead of weakening Home. Do not use an open guest network by default.
4. Enable guest wireless client isolation where supported. This complements, but does not replace, Guest-to-internal firewall blocks. A captive portal is not required.
5. Keep management off the household/guest SSIDs. Confirm all VLANs selected for SSIDs are permitted along the AP-to-switch-to-gateway path.
6. Disable wireless meshing when wired backhaul is confirmed and mesh is not needed. Use appropriate local country settings, then check channel use, power, coverage, and roaming with actual clients. Start with conservative settings rather than forcing wide channels or maximum transmit power.

The [U6+ hardware decision](../1_Design/1_Design_Hardware_Prerequisites.md#wi-fi-access-points) explains its bands and gigabit limit. Do not treat advertised radio rates as measured internet throughput.

---

## Step 8: Connect Household and Lab Clients

1. Test one client per intended network before connecting the rest. Confirm its subnet, gateway, and DNS match the private plan; reserve infrastructure addresses as needed.
2. Put household wired clients on Home access ports and wireless clients on Home. Move IoT and visitors only to their intended ports/SSIDs. Do not connect clients directly to the modem to bypass policy.
3. Connect each lab host only after its port profile is ready. Its management interface must match the switch's native/tagged choice. For the example in [Step 6](#step-6-assign-ports-and-move-device-management), host management is untagged and VM Lab traffic uses VLAN 20.
4. Configure the hypervisor's VLAN-aware bridge and assign VM network interfaces to the Lab VLAN; do not trunk Home/Guest into lab hosts without a specific requirement. Host installation/configuration belongs in [Hypervisor Setup](3_Setup_Hypervisor.md), while Talos VM networking belongs in [Cluster Setup](5_Setup_Cluster.md). Verify host templates match the selected port configuration before applying them.
5. Configure clients to obtain addressing, gateway, and DNS through DHCP unless a documented static configuration is needed. Keep static addresses, reservations, and automation inventories consistent with the private network plan.
6. Keep household DHCP/DNS on the gateway. The gateway is not an SSH jumphost; see [Management Access and Optional Jumphost](../1_Design/3_Design_Network.md#management-access-and-optional-jumphost). A lab bastion, if added later, must not become the only recovery route.

After Home connectivity passes validation, disable redundant ISP Wi-Fi/LAN client service only as appropriate to the selected modem mode and any provider services. Record the intended modem settings and how to recover them.

---

## Step 9: Validate the Setup

Use the [design's verification requirements](../1_Design/3_Design_Network.md#maintenance-recovery-and-safe-experiments). Record each result as passed, failed, or not yet tested, alongside actual device/software versions, in private operational notes. Do not put the network into normal use while required checks fail.

| Check | Required result |
|---|---|
| Gateway, switch, and APs | Online after provisioning; intended management network and wired links; no unexpected bootstrap clients |
| DHCP/DNS on each segment | Correct subnet, gateway, DNS, and reservations; no unexpected DHCP servers or Router Advertisements |
| Home internet | Working DNS and web access from wired and wireless clients |
| Guest isolation | Internet/DHCP/DNS work; Management, Home, Lab, IoT, and gateway administration are inaccessible |
| Home-to-Lab application exception | Only the selected endpoint/service works, if configured; other lab/management services remain blocked |
| Lab / IoT restrictions | New access to Home/Management blocked; only expressly configured exceptions work |
| Management access | Approved administrator reaches console and host/device administration; ordinary clients do not |
| Same-VLAN isolation | Guest wireless clients cannot reach one another where isolation is enabled; evaluate wired clients separately |
| Stateful return traffic | Responses to approved connections work without allowing unrelated reverse connections |
| IPv6 baseline or rollout | No unintended routed IPv6 path; if enabled, both allowed and denied tests pass over IPv6 |
| Local recovery | Wired Management access and local sign-in work without cloud sign-in |
| Independence from lab | With lab hosts/VMs off, household internet, DHCP, DNS, and Wi-Fi still work |
| Restart / reconnection | During the agreed window, gateway/switch/AP restart does not lose configuration; devices and clients recover |

**Test the service, not just ping.** For each denied path, first establish that the destination service is actually listening and reachable from an authorized source. Then attempt the same destination address/port from the denied segment; inspect firewall events/counters where available. A closed service, incorrect address, or host firewall can make a test fail without proving gateway isolation. Check both zone directions and both IP families if enabled.

For allowed paths, use the actual application, DNS lookup, or administrative service. An illustrative DNS test is `nslookup example.com 10.42.40.1` from a Home client, substituting the private gateway address. Do not paste command outputs exposing real endpoints into public Git. Use the DevHub [Network Reference](https://github.com/CollinPoetoehena/DevHub/tree/main/reference/network) for diagnostic tools.

Connect the remaining clients and remove temporary bootstrap allowances after all required checks pass. Keep a private final port/SSID/network map rather than treating these example tables as the live inventory.

---

## Step 10: Back Up and Maintain the Network

Follow [UniFi Backups and Migration](https://help.ui.com/hc/en-us/articles/360008976393), the [network recovery design](../1_Design/3_Design_Network.md#maintenance-recovery-and-safe-experiments), and the [software backup boundary](../1_Design/2_Design_Software_Prerequisites.md#backup).

1. Download a **System Config Backup** from the console's **Settings > Control Plane > Backups**. Prefer this complete gateway/OS/application/device configuration backup to assuming a Network-only export covers everything.
2. Keep dated backups before changes and after validated configuration. Store them encrypted/access-controlled outside this repository and outside storage that needs the lab to run. Keep an additional protected copy away from the gateway.
3. Automatic cloud backups are optional and account-dependent, not the only recovery mechanism. If enabled, protect the owner account with MFA and understand what is stored. Still retain an offline copy.
4. Record restoration steps, installed versions, ISP settings, management connectivity, and device re-adoption requirements privately. Review restore compatibility for the target gateway/version using Ubiquiti's guide.
5. Confirm a downloaded backup is available and that the restore workflow is understood. Schedule any actual restore test in a maintenance window; do not claim restore success merely because a file was downloaded.
6. Apply supported stable firmware updates in planned windows, reading release notes and backing up first. Update incrementally and repeat connectivity/isolation checks after changes. Lab monitoring can be optional, but must not be required for network operation.

Do not commit console backups, exports, keys, credentials, or identifying screenshots. Follow [Review Before Publishing](../0_Security_and_Public_Repository.md#review-before-publishing) for any public notes.

---

## Recovery and Troubleshooting

The first response is to restore the last tested path, not factory-reset the entire network. Keep recovery independent of the lab and cloud login, as required by [Management Access](../1_Design/3_Design_Network.md#management-access-and-optional-jumphost).

| Symptom | Check / recovery action |
|---|---|
| No WAN internet | Check link, configured DHCP/PPPoE/static/provider VLAN, upstream subnet overlap, and ISP status. Revert a failed modem-mode change; do not disable WAN protection. |
| Device offline after VLAN change | Check native VLAN agreement, tagged Management allowance, device Network Override, and lease. Revert the last changed port/override through a known-working local path. |
| Wi-Fi joins but no address or internet | Check SSID Network mapping and VLAN allowance on every uplink, DHCP, DNS, and Gateway-zone exceptions. |
| Client reaches an unexpected segment | Inspect network-to-zone assignment, effective policy order, broad Internal/allow rules, port membership, and IPv6. Remove the unwanted path and repeat allowed/denied tests. |
| Administrator locked out | Use the documented wired Management port and local account. If DHCP is unavailable, a correctly chosen private static address may help only if the port/VLAN path still works; it cannot repair wrong tags or firewall policy. |
| Gateway fails or cannot be recovered locally | During a planned outage, follow Ubiquiti's model-specific reset/recovery procedure, restore a compatible private backup, then verify device reconnection and isolation. Do not reset other devices unless actually required. |

Factory reset is a **last resort** that removes configuration; use [How to Reset UniFi Devices](https://help.ui.com/hc/en-us/articles/205143490) and the [backup/restore guide](https://help.ui.com/hc/en-us/articles/360008976393). Ensure physical access, power, WAN details, credentials, and the offline backup are available first. Keep ordinary clients disconnected during recovery until segmentation has been restored and verified.

See [Troubleshooting](Troubleshooting.md) for related network issues; use only the sections applicable to this equipment.

---

## Future VPN and IPv6 Work

- **VPN remains TODO**, not part of basic setup. Follow the [software VPN decision](../1_Design/2_Design_Software_Prerequisites.md#router--firewall-software) before choosing OpenVPN, WireGuard, or another supported option. Check firmware, double NAT/carrier-grade NAT, credentials, and minimum segment access. Keep remote endpoints and VPN exports private.
- **IPv6 requires a separate validated rollout**, following [IPv6 Design and Rollout](../1_Design/3_Design_Network.md#ipv6-design-and-rollout) and [UniFi DHCPv6 Prefix Delegation](https://help.ui.com/hc/en-us/articles/115005868927). Configure the ISP-supported WAN prefix delegation and LAN `/64` allocations, required Router Advertisement/ICMPv6 behavior, DNS, and equivalent firewall policy before enabling routed IPv6 for clients. WAN IPv6 alone does not prove downstream delegation works. Do not assume NAT66 is required or publish real delegated prefixes; use `2001:db8::/32` only for documentation examples, not live internet addressing.
