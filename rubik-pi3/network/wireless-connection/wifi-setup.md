# WiFi/Wireless Network Installation on the Rubik Pi 3

A complete, beginner-friendly guide to configuring Wi-Fi on the **Rubik Pi 3** running Ubuntu (CLI/Server edition). This guide covers standard home Wi-Fi, priority fallback chains, corporate/university logins (username & password), captive portals, and common terminal troubleshooting.

---

## Table of Contents
1. [Prerequisites & Interface Check](#1-prerequisites--interface-check)
2. [Standard Home/Personal Wi-Fi (WPA-PSK)](#2-standard-homepersonal-wi-fi-wpa-psk)
3. [Setting Up Wi-Fi Connection Priority (Auto-Fallback)](#3-setting-up-wi-fi-connection-priority-auto-fallback)
4. [Enterprise Wi-Fi (Username & Password / 802.1X PEAP)](#4-enterprise-wi-fi-username--password--8021x-peap)
5. [Connecting to Captive Portals (Web Login Gateways)](#5-connecting-to-captive-portals-web-login-gateways)
6. [Troubleshooting: `-bash: event not found` (Special Characters)](#6-troubleshooting--bash-event-not-found-special-characters)
7. [Verification & Reboot Persistence](#7-verification--reboot-persistence)
8. [Quick Reference Cheat Sheet](#8-quick-reference-cheat-sheet)

---

## 1. Prerequisites & Interface Check

Before configuring Wi-Fi, ensure your network interface is active and detected by Ubuntu.

1. **Verify your Wi-Fi interface name:**
   ```bash
   nmcli device status
   ```
   *You should see an interface named `wlan0` (or similar) with the type `wifi`.*

2. **Turn Wi-Fi radio on if disabled:**
   ```bash
   sudo nmcli radio wifi on
   ```

3. **Scan for surrounding networks:**
   ```bash
   nmcli device wifi list
   ```
   *Locate your target SSID in the output list along with its signal strength and security type.*

---

## 2. Standard Home/Personal Wi-Fi (WPA-PSK)

For standard home routers, mobile hotspots, or office Wi-Fi networks requiring a single network password.

### Quick Connect (One-Liner)
```bash
sudo nmcli device wifi connect "Your_SSID" password "Your_WiFi_Password"
```

### Structured Profile Creation (Recommended)
Creating a named profile gives you cleaner control over autoconnect and priority settings:

```bash
sudo nmcli connection add \
  type wifi \
  con-name "Home_WiFi" \
  ifname wlan0 \
  ssid "Your_SSID" \
  wifi-sec.key-mgmt wpa-psk \
  wifi-sec.psk "Your_WiFi_Password"
```

* **`con-name "Home_WiFi"`**: A friendly nickname for the profile in your system.
* **`ssid "Your_SSID"`**: The actual name broadcasted by your router.

---

## 3. Setting Up Wi-Fi Connection Priority (Auto-Fallback)

If you use the Rubik Pi 3 across multiple locations (e.g., your phone hotspot, home Wi-Fi, and a lab network), you can configure an automatic fallback chain using **Autoconnect Priority**.

* **Rule:** A **higher integer** takes precedence over a lower integer.

### Example Priority Order
1. **Primary Network (Mobile Hotspot):** Priority `100`
2. **Secondary Network (Home Wi-Fi):** Priority `50`
3. **Tertiary Network (Lab/Office Wi-Fi):** Priority `10`

### Step 1: Add or Identify Your Profiles
```bash
nmcli connection show
```

### Step 2: Set the Priority Values
```bash
# Highest priority: Connects here first whenever in range
sudo nmcli connection modify "Hotspot_Profile" connection.autoconnect-priority 100 connection.autoconnect yes

# Fallback: Used when Hotspot is out of range
sudo nmcli connection modify "Home_WiFi" connection.autoconnect-priority 50 connection.autoconnect yes

# Last resort: Used if both above are unavailable
sudo nmcli connection modify "Lab_WiFi" connection.autoconnect-priority 10 connection.autoconnect yes
```

### Step 3: Reload Profiles
```bash
sudo nmcli connection reload
sudo nmcli device set wlan0 autoconnect yes
```

---

## 4. Enterprise Wi-Fi (Username & Password / 802.1X PEAP)

Enterprise networks (commonly used in corporate offices, universities, or *eduroam*) require a **Username/Identity** and **Password** rather than a single pre-shared key.

### Step 1: Create the Profile
Always enclose credentials in **single quotes (`'...'`)** to avoid bash syntax errors with symbols:

```bash
sudo nmcli connection add \
  type wifi \
  con-name "University_Corp_WiFi" \
  ifname wlan0 \
  ssid "Enterprise_SSID" \
  wifi-sec.key-mgmt wpa-eap \
  802-1x.eap peap \
  802-1x.phase2-auth mschapv2 \
  802-1x.identity 'your_username' \
  802-1x.password 'your_secret_password!@#'
```

### Step 2: Configure CA Certificate Handling
If your institution does not require you to install an explicit `.crt`/`.pem` certificate file on client devices, instruct NetworkManager not to demand one during Phase 1:

```bash
sudo nmcli connection modify "University_Corp_WiFi" \
  802-1x.phase1-peapver 0 \
  802-1x.phase2-autheap peap
```

### Step 3: Connect and Test
```bash
sudo nmcli connection up "University_Corp_WiFi"
```

Verify your assigned IP address:
```bash
ip addr show wlan0
```

---

## 5. Connecting to Captive Portals (Web Login Gateways)

Captive portals (hotels, airports, cafes, or guest networks) do not use enterprise Wi-Fi security. Instead, the Wi-Fi connects as an open or standard network, but the gateway redirects all web requests to a login webpage.

### Step 1: Connect to the Wi-Fi Link
```bash
# For an open network without a Wi-Fi password
sudo nmcli connection add type wifi con-name "Hotel_Guest" ifname wlan0 ssid "Hotel_Guest_WiFi"
sudo nmcli connection up "Hotel_Guest"
```

### Step 2: Test for Gateway Redirection
Check whether an HTTP request receives a `302 Found` redirect:
```bash
curl -I http://neverssl.com
```
*If you see `HTTP/1.1 302 Found` with a `Location:` header pointing to `http://192.168.x.x/login`, your traffic is currently intercepted.*

### Step 3: Authenticate Headless (No GUI)
Inspect the portal form's destination URL and input parameters, then send a POST request via `curl`:

```bash
curl -X POST -d "username=myuser&password=mypassword" http://<gateway-ip>/login-endpoint
```

Alternatively, use a lightweight text-mode web browser to complete the interactive web page directly inside your SSH session:
```bash
sudo apt update && sudo apt install -y lynx
lynx http://neverssl.com
```

---

## 6. Troubleshooting: `-bash: event not found` (Special Characters)

When entering complex passwords containing special characters (e.g., `!`, `$`, `#`, `@`), you may encounter:

```text
-bash: !@#: event not found
```

### Cause
In interactive Bash shells, the exclamation mark (`!`) triggers **Bash History Expansion**, which attempts to recall previous commands from your terminal history. **Double quotes (`"..."`) do not protect against this.**

### Solutions

#### Option 1: Use Single Quotes (Simplest & Best)
Single quotes (`'...'`) treat every character literally and disable Bash expansion:
```bash
802-1x.password 'StrongP@ssw0rd!'
```

#### Option 2: Escape the Exclamation Mark
Precede every `!` with a backslash (`\`):
```bash
802-1x.password "StrongP@ssw0rd\!"
```

#### Option 3: Disable History Expansion Temporarily
Turn off history expansion in your terminal session before entering your command:
```bash
set +H
```
*(You can re-enable it later with `set -H` if desired).*

---

## 7. Verification & Reboot Persistence

Settings modified with `nmcli connection modify` are written to persistent storage and automatically survive reboots.

### 1. Confirm Storage on Disk
Check that your configuration profiles are stored in the permanent system directory:
```bash
ls -la /etc/NetworkManager/system-connections/
```

### 2. Inspect Priority Rankings
Verify your configured fallback order across all stored networks:
```bash
nmcli -f NAME,TYPE,AUTOCONNECT,AUTOCONNECT-PRIORITY connection show
```

### 3. Check Active Link and Gateway
```bash
ip route show default
ping -c 3 8.8.8.8
```

---

## 8. Quick Reference Cheat Sheet

| Task | Command |
| :--- | :--- |
| **Scan available networks** | `nmcli device wifi list` |
| **View saved profiles** | `nmcli connection show` |
| **Delete an old profile** | `sudo nmcli connection delete "<profile-name>"` |
| **Set autoconnect priority** | `sudo nmcli connection modify "<profile>" connection.autoconnect-priority <number>` |
| **Bring profile up manually** | `sudo nmcli connection up "<profile>"` |
| **Check current IP address** | `ip -br addr show wlan0` |
| **Restart NetworkManager** | `sudo systemctl restart NetworkManager` |