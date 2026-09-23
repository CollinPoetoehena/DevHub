# Setup & Installation: Services

TODO: here the actual services that run on the homelab.

# TODO: what to run on the home lab cluster:
TODO: for services/workloads do energy monitoring to add value in the home
TODO: the IoT devices can run in VLAN 30 IoT, see [networking design](../2_Network_Hosts/TODO.md#network-topology)

**TODO: MetalLB for VIPs and load balancing. TODO: also how to securely expose services to the outside world (e.g., via Ingress, Traefik, or NGINX), etc., so that I can use the service from outside the home network for example, etc.**

**TODO: 1: Something with cooking and groceries (I can do this already when I do not own my own house yet): TODO: make a separate repo here as well because this is a separate service/project and deploy as a container.**
TODO: then add something like make your grocery shop list that exports to a PDF/PNG that automatically sorts it for you into sections (e.g. fruits, vegetables, dairy, meat, pantry), etc.
TODO: and also make it read a Word document and extract the "benodigdheden" automatically and put it into a DB, etc.
TODO: that will save a lot of time when doing grocery shopping, etc.!
TODO: see [Python Packages](../../../packages/Python.md) for details, I want to build this in Python because it is fun, easy to maintain, and has a rich ecosystem for handling tasks like PDF/Word processing, database interactions, and web integrations, etc.! 
TODO: see that file above and use best practices again I learned at my work also, such as Logging, Exceptions, etc.

**TODO: 2: Energy Monitoring: TODO: make in separate repo (NOT in DevHub/Homelab, it is a separate service/project, so build it into a container and then deploy it in homelab, etc.!)**
Content of energy monitoring: such as from AI:
Energy Monitoring (Highest Practical Value)

If you're in the Netherlands, energy prices and consumption are worth tracking.

Option A: Smart Meter Integration

Most Dutch smart meters expose data via the P1 port.

You can connect:

HomeWizard P1 Meter
ESP32 + P1 reader
Raspberry Pi P1 reader

Flow:

Plain Text
1
Smart Meter
2
|
3
P1
4
|
5
Home Assistant
6
|
7
Prometheus
8
|
9
Grafana
Meer regels weergeven

You can monitor:

Current consumption (W)
Current production (solar)
Daily usage
Energy costs
Gas usage

Example Grafana dashboard:

Plain Text
1
Today:
2
Electricity 8.2 kWh
3
Gas 0.7 m³
4
 
5
Current:
6
Import 423W
7
Export 0W
8
 
9
Month:
10
Electricity €42
11
Gas €18
Meer regels weergeven

This is usually the single most useful dashboard in a home.