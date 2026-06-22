# TODO: Fill this in when I start on the actual home lab and get to this point, etc.

TODO: this is a large topic, maybe turn this into a folder with multiple files, etc.??

TODO: here creating the cluster of nodes and the network between them

Link your nodes together so they behave as one system.

For Proxmox: create a cluster and join the other nodes

For Kubernetes: install k3s or kubeadm and join worker nodes

Verify node communication and cluster health
etc...

A stable network is essential for clustering and node communication.

# TODO: network setup to avoid breakage of home network, etc.
TODO: below is brainstorming, later make into nice documentation with AI!

**Why bother and why keep ISPs modem:** TODO: explain I want to learn networking, but there are a lot of others in the house who use the internet and I don't want to break it and/or maintain an entire network setup myself if I would set up the modem myself, etc. So I want to keep the ISP modem as the main router for the home network, and then put my own router behind it to create a separate network for the lab, which is safer and easier to manage without risking the home network. This also allows me to experiment freely in the lab without worrying about breaking the internet for everyone else, and if I want to try a new network setup or experiment with it I do not have the obligation to maintain it for the home network, etc. It also allows me to learn about networking and routing in a more realistic way, as I can set up different subnets, VLANs, firewall rules, etc. in the lab without affecting the home network.

**TODO: VERY IMPORTANT: SETUP TO NOT BREAK THE HOME NETWORK:** Below is some brainstorming with AI on the setup to protect the home network from any mistakes in the lab network, which is critical to avoid breaking the home network and lose internet access, and avoids angry family members, etc.:
1) Use Your Own Router Behind the ISP Modem
This is the best and safest method.
How it works
Code
ISP Modem → Your Router → Home Network + Lab Network
Your router becomes the “brain” of your network. Your ISP modem becomes just the internet gateway.
Why this protects your home
•	Your lab is on its own subnet
•	Your home devices stay on the default subnet
•	Lab mistakes (DHCP conflicts, firewall rules, routing loops) never reach your home WiFi
What you need
•	A router that supports VLANs or multiple subnets (Ubiquiti, TP-Link Omada, OPNsense, etc.)
2) Alternative: you can use VLANs inside your home network if your router/modem from your ISP supports it, but this is generally more complex and riskier, as a misconfiguration can easily break your home network. Furthermore, most modems/routers from ISPs do not support VLANs or very limited, etc. That is why this option is NOT used in my home network setup.
What NOT to Do (These break home networks)
•	❌ Running a DHCP server on the same subnet as your home devices
•	❌ Changing DNS settings on the ISP modem
•	❌ Putting Kubernetes nodes on the same network as your TV, phones, etc.
•	❌ Using Proxmox bridges incorrectly (can cause loops)
•	❌ Running firewall experiments on the home LAN
These are the classic “I broke the internet” mistakes.
Recommendation: Option 1 because that is the safest and most robust way to protect your home network while still allowing you to experiment freely in your lab network. It also provides better isolation and security between the two networks, and allows for more advanced configurations (e.g. VLANs, routing rules, etc.) without risking the stability of your home network.
## TODO: brainstormed setup, already did some things:
### Router setup:
Hoe sluit je jouw nieuwe router aan op de Experia Box?
Dit is de exacte stappenlijst die werkt met KPN:

1) Verbind de apparaten
Code
Experia Box LAN poort → WAN poort van jouw nieuwe router
Dat is het.
Je hoeft niets te veranderen aan de Experia Box.

2) Geef je nieuwe router een eigen subnet
Voorbeeld:

Experia Box LAN: 192.168.2.0/24

Jouw router LAN: 192.168.10.0/24

Dit voorkomt IP‑conflicten en DHCP‑problemen.

3) Laat DHCP op beide routers aan
Experia Box DHCP → voor je thuisnetwerk

Nieuwe router DHCP → voor je lab

Ze zitten op verschillende netwerken, dus geen conflict.

4) (Optioneel) Zet je nieuwe router in de DMZ van de Experia Box
Dit maakt port forwarding makkelijker.

Ga naar Experia Box instellingen

Zoek DMZ

Vul het WAN‑IP van je nieuwe router in (bijv. 192.168.2.50)

Niet verplicht, maar handig.

5) Sluit je mini‑PC’s aan op de nieuwe router
Nu zitten ze volledig geïsoleerd:

Code
Mini PC 1 → Nieuwe router → Experia Box → Internet
Mini PC 2 → Nieuwe router → Experia Box → Internet
Je kunt nu alles kapot testen zonder dat je thuisnetwerk last heeft.

🛡️ Waarom dit 100% veilig is voor je thuisnetwerk
Je lab zit op een eigen subnet

Je lab heeft eigen DHCP

Je lab heeft eigen firewall

Experia Box blijft baas over je thuis-WiFi

Lab-fouten (DHCP, firewall, VLANs, Kubernetes) raken je thuisnetwerk niet

Je kunt letterlijk je lab-router verkeerd configureren en je gezin merkt er niets van.

### Why a router and not a switch:
What a Switch Does (and Why It’s Not Enough)



A switch:

Connects devices inside the same network

Gives them Ethernet ports

Does not create a new network

Does not isolate traffic

Does not provide firewalling

Does not run DHCP (unless it’s a special L3 switch)

A switch is basically a “power strip for Ethernet.”

Example
If you plug your mini PCs into a switch that’s connected to your Experia Box:

Code
Experia Box → Switch → Mini PCs
Then:

Your lab is on the same network as your home devices

Your lab can break your home network

DHCP conflicts can happen

Kubernetes networking can leak

VLANs won’t work unless the switch is managed and you have a router that understands them

This is why a switch alone is not safe for a home lab.

🌐 What a Router Does (and Why You Need One)
A router:

Creates a new network

Separates traffic between networks

Has a WAN side (toward the internet)

Has a LAN side (toward your devices)

Runs DHCP

Enforces firewall rules

Supports VLANs (if it’s a good one)

A router is the “brain” of your network.

Example
If you put your own router behind the Experia Box:

Code
Internet → Experia Box → Your Router → Lab
Then:

Your lab is isolated

Your home network stays safe

You can break anything in the lab

No DHCP conflicts

No routing loops

No Kubernetes chaos leaking into your home WiFi

This is why Option 1 uses a router, not a switch.

**Why a router and not a switch:** A switch only connects devices inside the same network, while a router creates a separate network with its own firewall, DHCP, and isolation. For a home lab, you need a router because it keeps your experiments on a different subnet so you can’t accidentally break your home WiFi. A switch can’t do that — it just adds more ports to the existing network.
- A router = traffic director between networks
- A switch = traffic distributor inside one network


### What router to buy:

TODO: Buy from Coolblue (trusted Dutch shop for electronics): https://www.coolblue.nl/product/874760/tp-link-omada-er605.html. In 2026: 58 EUR. This is because it has VLAN support, no WiFi (not needed, saves money) and is the perfect budget option for a home lab that is focused on learning, etc., and TP-Link is a trusted provider, etc.
#### General steps how to choose a router:
How to Choose a Router for a Home Lab (Short & General)
1) Ethernet ports (important)
You want at least 3–4 LAN ports so you can plug in:

Mini PC #1

Mini PC #2

Optional switch

Optional management laptop

More ports = more flexibility.

2) No WiFi needed
Your lab router does not need WiFi because:

Your KPN Experia Box already provides home WiFi

Your lab devices use Ethernet

WiFi adds cost you don’t need

WiFi on the router is optional — you can turn it off.

3) VLAN support
This is key for isolating your lab safely.
Look for 802.1Q VLAN support.

4) Good firewall controls
You want to be able to:

Block traffic

Allow only what you need

Keep home and lab separate

5) Stable firmware + updates
A router that gets updates stays secure and reliable.

6) Fits your budget
You don’t need enterprise gear — just something stable with VLANs.

🧱 Recommended Router Options (Short List)
1) TP‑Link ER605 — Budget, wired only
No WiFi

Cheap (€60–€90)

VLAN support

Simple UI

Perfect if you want the cheapest safe lab isolation

Great behind the KPN Experia Box

2) Ubiquiti UDR — Best all‑rounder
WiFi included but can be turned off

Excellent VLAN/firewall UI

Great monitoring

€150–€180

Best for learning networking + DevOps

3) Netgear Insight BR200 — Business‑style, wired
No WiFi

VLAN support

More expensive than TP‑Link

Good stability

Simple but not as polished as Ubiquiti

4) OPNsense Router — Advanced
Runs on a mini PC

No WiFi

Full enterprise firewall

Best for deep learning

€180–€250

⭐ Why I Choose TP‑Link for My Home Lab:
TP‑Link ER605 is ideal if you want:

The cheapest option

A wired-only router

VLAN support

A simple setup

Reliable isolation behind the Experia Box

No need for advanced monitoring or analytics

It’s the “budget workhorse” — perfect if you want to spend money on your mini PCs instead of networking gear.