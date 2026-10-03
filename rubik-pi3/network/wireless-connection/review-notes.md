# Review notes for the preserved Wi-Fi guide

Status: editorial review flags, not board-tested replacement instructions. The [original guide](wifi-setup.md) is retained unchanged for provenance.

Before teaching from it:

1. Confirm the installed image actually uses NetworkManager and discover the interface name; do not assume `wlan0` or install a competing network manager blindly.
2. Prefer interactive secret entry, for example `sudo nmcli --ask device wifi connect "Your_SSID"`, rather than putting a password in command history or a process argument. Never include secrets in submitted logs. Quoting is not credential protection.
3. Section 4's certificate-handling recipe is not an approved secure enterprise configuration. Do not follow it as a way to avoid CA verification. Obtain the institution's EAP method, trusted CA and expected authentication-server domain; configure certificate and server-name validation accordingly. The `phase2-autheap peap` example needs correction against the actual EAP deployment; PEAP with inner MSCHAPv2 is not configured by treating PEAP as that inner method.
4. Autoconnect priority selects among eligible profiles when connecting. It is not guaranteed proactive roaming, Internet-health failover, or automatic replacement of an active connection.
5. Captive portals vary and may require JavaScript or institution-specific flows. Use the operator's documented method and validate HTTPS before entering credentials. Do not copy the generic HTTP password-POST example into a real login; an HTTP discovery request is not a safe credential-submission channel.
6. An external ping alone does not prove DNS or application connectivity, and blocked ICMP does not prove the connection is down. Test each layer separately.
7. Restarting NetworkManager, changing profiles or rebooting can terminate SSH. Arrange console/secondary access and record a recovery path first.
8. The shell-quoting examples need classroom review: a single quote inside a password requires different handling, and backslash behavior inside double quotes is subtle. Interactive prompts avoid these examples entirely.

Release gate: revise the teaching version with the network administrator's settings, record OS/NetworkManager versions, and demonstrate successful validation and recovery on a test board. Do not claim that enterprise setup is verified until then.
