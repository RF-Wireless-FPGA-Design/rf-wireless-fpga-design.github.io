# Wireless connection

- [Wi-Fi setup](wifi-setup.md): migrated existing guide, preserved unchanged; not independently revalidated on hardware.
- [Review notes](review-notes.md): required safety/correctness review before classroom use.

## Planned mission: connect the edge node

Predict the available interface and authentication method. Establish a recovery console or a second access path before changing networking. Connect to an authorized test network, then test association, address assignment, gateway reachability, DNS and HTTPS independently.

Evidence: redacted command outputs, a layer-by-layer diagnosis, and reconnect results after a controlled reboot. Reboot only when local recovery access is available.

Stretch task: compare two saved profiles during a deliberate disconnect/reconnect. Do not assume priority settings will interrupt a healthy active connection or detect an Internet outage.
