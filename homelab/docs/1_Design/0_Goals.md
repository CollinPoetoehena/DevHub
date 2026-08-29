# Personal Goals

The goal of this home lab is simple: **learn the fundamentals of DevOps and Software Engineering, and have fun doing it — while building a cool and satisfying home lab to experiment with.** Topics include networking, Linux, Kubernetes, monitoring (Grafana, Prometheus), infrastructure automation, and more — because I genuinely enjoy experimenting with these things and want to advance my Engineering skills.

There's something genuinely cool and satisfying about having a real home lab cluster sitting on your desk: physical nodes, real networking, services you deployed yourself, dashboards showing live metrics from your own hardware. It's not just a learning environment — it's a playground to break things, try out new tools before using them at work, and experiment without any consequences. And it just looks and feels awesome.

In my work I use these techniques daily and will continue to do so: VMs, networking, Linux, containers, etc. Having hands-on experience with them makes my work easier and more enjoyable, and makes me a better Engineer overall. A home lab is the best way to get that unrestricted, persistent environment where you can break things, fix them, and learn without consequences.

## What this is NOT

This lab is purely for learning and fun — not production, not an obligation.

Personally, I work as a DevOps Engineer, not as a hardware, network, or storage engineer. That means this lab is mostly about broadening my knowledge and following personal interest, but not about mastering hardware, networking, or storage topics at a deeply advanced specialist level like hardware, network, or storage engineers do. It is focused on theory, practical understanding, and some more advanced concepts, but not on the most advanced specialist work a dedicated network, storage, or hardware engineer would do.

**This is not a self-hosting / home data centre project.** Some people enjoy turning their home lab into a full self-hosted platform — replacing cloud services like OneDrive, Netflix, Spotify, running their own VPN, NAS, DNS, mail server, and making their entire household depend on the lab. That's a perfectly valid hobby, but it's not the goal here. That kind of setup essentially becomes a second job: you need to maintain uptime, handle backups, deal with security patches, manage storage, and if the lab goes down, the whole house is affected — no media, no files, no internet services. It demands production-level reliability from what is supposed to be a learning environment.

This lab is the opposite for myself: it's for **learning, experimenting, and having fun**. If I break something, nothing in the house stops working. If I want to wipe and rebuild the entire cluster over the weekend, I can — no impact on anyone. The lab should be something I enjoy tinkering with, not something I'm obligated to keep running. That freedom to break things without consequences is exactly what makes it valuable for learning. A home lab should not feel like a second job. It should not come with on-call responsibilities, uptime obligations, or the stress of "if this goes down, people are affected." The moment it starts feeling like an obligation — patching at midnight because the family can't stream, debugging DNS at 7 AM because smart home devices stopped working — it stops being fun and starts being ops work you're not getting paid for. Keep it simple, keep it enjoyable, and keep it separate from the things your household actually depends on. That is the goal of this personal homelab for me.

Key boundaries:

- **Not 24/7 uptime required**: can turn it off when done for the day or keep it running depending on preference, no stress.
- **Not self-hosting everything**: still using cloud storage (e.g. OneDrive), streaming services (e.g. Netflix), and the ISP's modem/router. Setting up your own NAS with drives, a VPN, and a custom router costs a lot of money and effort, introduces security risks (e.g. a self-hosted VPN exposes your home network to the internet if misconfigured), and is the domain of Network/Storage/Infrastructure Engineers — which is not my goal at this time. The focus is on learning DevOps concepts, not on building a custom home network or storage solution.
- **Not advanced hardware tinkering**: the focus is on DevOps concepts (K8s, automation, observability), not on assembling servers or deep hardware engineering.
- **Repurpose old hardware**: rather than buying new, old laptops and refurbished enterprise-grade mini PCs are used — good for the environment, good for the wallet, and still perfectly capable for learning.

The choices made in this home lab are based on these personal goals and interests.