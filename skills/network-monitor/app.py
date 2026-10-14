"""
Local Network Monitoring Web UI
Monitors WiFi connection, connected devices, ARP table, netstat, and network interfaces.
"""

import subprocess
import re
import json
import socket
import struct
import threading
import time
import os
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# ─── Helpers ────────────────────────────────────────────────────────

def run_cmd(cmd, timeout=15):
    """Run a shell command and return stdout."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            shell=True, encoding='utf-8', errors='replace'
        )
        return result.stdout.strip()
    except Exception as e:
        return f"ERROR: {e}"


def run_powershell(script, timeout=20):
    """Run a PowerShell script and return stdout."""
    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True, text=True, timeout=timeout,
            encoding='utf-8', errors='replace'
        )
        return result.stdout.strip()
    except Exception as e:
        return f"ERROR: {e}"


# ─── WiFi Info ─────────────────────────────────────────────────────

def get_wifi_info():
    """Get current WiFi connection details via netsh."""
    raw = run_cmd("netsh wlan show interfaces")
    if not raw or "ERROR" in raw:
        return {"error": raw}

    info = {}
    for line in raw.splitlines():
        line = line.strip()
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if key and val:
                info[key] = val

    # Also get the profile XML for more details
    ssid = info.get("SSID", "")
    if ssid:
        profile_raw = run_cmd(f'netsh wlan show profile name="{ssid}" key=clear')
        if profile_raw and "ERROR" not in profile_raw:
            # Extract key content
            m = re.search(r'Key Content\s*:\s*(.+)', profile_raw)
            if m:
                info["_key"] = m.group(1).strip()
            # Extract authentication
            m = re.search(r'Authentication\s*:\s*(.+)', profile_raw)
            if m:
                info["_auth"] = m.group(1).strip()

    return info


def get_wifi_networks():
    """Get list of available WiFi networks."""
    raw = run_cmd("netsh wlan show networks mode=bssid", timeout=20)
    if not raw or "ERROR" in raw:
        return []

    networks = []
    current = {}
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("SSID"):
            if current:
                networks.append(current)
            current = {"ssid": line.split(":", 1)[-1].strip() if ":" in line else ""}
        elif ":" in line and current:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if key == "BSSID":
                current.setdefault("bssids", []).append(val)
            elif key == "Signal":
                current["signal"] = val
            elif key == "Band":
                current["band"] = val
            elif key == "Channel":
                current["channel"] = val
            elif key == "Authentication":
                current["auth"] = val
            elif key == "Cipher":
                current["cipher"] = val
    if current:
        networks.append(current)
    return networks


# ─── ARP Table ─────────────────────────────────────────────────────

def get_arp_table():
    """Get ARP table (IP -> MAC mappings)."""
    raw = run_cmd("arp -a")
    if not raw or "ERROR" in raw:
        return []

    entries = []
    current_iface = ""
    for line in raw.splitlines():
        line = line.strip()
        # Interface line: "Interface: 192.168.1.100 --- 0x..."
        m = re.match(r'Interface:\s+(\S+)\s+---s+(0x\S+)', line)
        if m:
            current_iface = m.group(1)
            continue
        # ARP entry: "  192.168.1.1     00-11-22-33-44-55     dynamic"
        m = re.match(r'(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F:-]{17})\s+(\w+)', line)
        if m:
            entries.append({
                "ip": m.group(1),
                "mac": m.group(2).lower(),
                "type": m.group(3),
                "interface": current_iface
            })
    return entries


# ─── Network Interfaces ────────────────────────────────────────────

def get_interfaces():
    """Get network interface details."""
    raw = run_cmd("ipconfig /all")
    if not raw or "ERROR" in raw:
        return []

    interfaces = []
    current = {}
    for line in raw.splitlines():
        line = line.rstrip()
        # New interface starts with a non-indented line containing "adapter"
        if "adapter" in line.lower() and ":" in line:
            if current:
                interfaces.append(current)
            name = line.split(":", 1)[0].strip()
            current = {"name": name, "description": name}
        elif current and ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if key and val:
                current[key.lower().replace(" ", "_")] = val
    if current:
        interfaces.append(current)
    return interfaces


# ─── Netstat ───────────────────────────────────────────────────────

def get_netstat():
    """Get active TCP/UDP connections."""
    raw = run_cmd("netstat -ano")
    if not raw or "ERROR" in raw:
        return {"tcp": [], "udp": []}

    tcp_entries = []
    udp_entries = []
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("TCP"):
            parts = line.split()
            if len(parts) >= 4:
                tcp_entries.append({
                    "proto": "TCP",
                    "local": parts[1],
                    "remote": parts[2],
                    "state": parts[3] if len(parts) > 3 else "",
                    "pid": parts[-1]
                })
        elif line.startswith("UDP"):
            parts = line.split()
            if len(parts) >= 3:
                udp_entries.append({
                    "proto": "UDP",
                    "local": parts[1],
                    "remote": parts[2] if len(parts) > 2 else "*:*",
                    "pid": parts[-1]
                })
    return {"tcp": tcp_entries, "udp": udp_entries}


# ─── Device Scan ───────────────────────────────────────────────────

def ping_host(ip, timeout=1):
    """Ping a single host, return True if reachable."""
    try:
        result = subprocess.run(
            ["ping", "-n", "1", "-w", str(timeout * 1000), ip],
            capture_output=True, timeout=timeout + 2
        )
        return result.returncode == 0
    except:
        return False


def get_device_info(ip):
    """Get device info from ARP and reverse DNS."""
    # Get MAC from ARP
    mac = ""
    try:
        result = subprocess.run(
            ["arp", "-a", ip],
            capture_output=True, text=True, timeout=5
        )
        m = re.search(r'([0-9a-fA-F:-]{17})', result.stdout)
        if m:
            mac = m.group(1).lower()
    except:
        pass

    # Reverse DNS
    hostname = ""
    try:
        hostname = socket.gethostbyaddr(ip)[0]
    except:
        pass

    # Get vendor from MAC OUI
    vendor = ""
    if mac:
        oui = mac[:8].replace(":", "-").upper()
        # Common OUIs
        vendors = {
            "00-50-56": "VMware",
            "00-0C-29": "VMware",
            "00-05-69": "VMware",
            "08-00-27": "VirtualBox",
            "52-54-00": "QEMU/KVM",
            "B8-27-EB": "Raspberry Pi",
            "DC-A6-32": "Raspberry Pi",
            "E4-5F-01": "Raspberry Pi",
            "00-17-88": "Philips Hue",
            "18-B4-30": "Nest/Google",
            "64-16-66": "Amazon",
            "A4-DA-22": "Amazon",
            "F0-27-2D": "Amazon",
            "44-65-0D": "Amazon",
            "74-75-48": "Amazon",
            "00-04-4B": "NVIDIA",
            "00-14-22": "Dell",
            "00-18-8B": "Dell",
            "F8-BC-12": "Dell",
            "00-0C-41": "Samsung",
            "00-12-47": "Samsung",
            "00-15-99": "Samsung",
            "00-17-C9": "Samsung",
            "00-1A-8A": "Samsung",
            "00-1C-43": "Samsung",
            "00-1D-25": "Samsung",
            "00-1D-F6": "Samsung",
            "00-1E-7D": "Samsung",
            "00-1F-CC": "Samsung",
            "00-21-19": "Samsung",
            "00-23-39": "Samsung",
            "00-23-99": "Samsung",
            "00-23-9C": "Samsung",
            "00-23-D6": "Samsung",
            "00-23-D7": "Samsung",
            "00-24-54": "Samsung",
            "00-24-E9": "Samsung",
            "00-25-66": "Samsung",
            "00-26-37": "Samsung",
            "00-26-5D": "Samsung",
            "00-26-8A": "Samsung",
            "00-26-A0": "Samsung",
            "00-26-A1": "Samsung",
            "00-26-A2": "Samsung",
            "00-26-A3": "Samsung",
            "00-26-A4": "Samsung",
            "00-26-A5": "Samsung",
            "00-26-A6": "Samsung",
            "00-26-A7": "Samsung",
            "00-26-A8": "Samsung",
            "00-26-A9": "Samsung",
            "00-26-AA": "Samsung",
            "00-26-AB": "Samsung",
            "00-26-AC": "Samsung",
            "00-26-AD": "Samsung",
            "00-26-AE": "Samsung",
            "00-26-AF": "Samsung",
            "00-26-B0": "Samsung",
            "00-26-B1": "Samsung",
            "00-26-B2": "Samsung",
            "00-26-B3": "Samsung",
            "00-26-B4": "Samsung",
            "00-26-B5": "Samsung",
            "00-26-B6": "Samsung",
            "00-26-B7": "Samsung",
            "00-26-B8": "Samsung",
            "00-26-B9": "Samsung",
            "00-26-BA": "Samsung",
            "00-26-BB": "Samsung",
            "00-26-BC": "Samsung",
            "00-26-BD": "Samsung",
            "00-26-BE": "Samsung",
            "00-26-BF": "Samsung",
            "00-26-C0": "Samsung",
            "00-26-C1": "Samsung",
            "00-26-C2": "Samsung",
            "00-26-C3": "Samsung",
            "00-26-C4": "Samsung",
            "00-26-C5": "Samsung",
            "00-26-C6": "Samsung",
            "00-26-C7": "Samsung",
            "00-26-C8": "Samsung",
            "00-26-C9": "Samsung",
            "00-26-CA": "Samsung",
            "00-26-CB": "Samsung",
            "00-26-CC": "Samsung",
            "00-26-CD": "Samsung",
            "00-26-CE": "Samsung",
            "00-26-CF": "Samsung",
            "00-26-D0": "Samsung",
            "00-26-D1": "Samsung",
            "00-26-D2": "Samsung",
            "00-26-D3": "Samsung",
            "00-26-D4": "Samsung",
            "00-26-D5": "Samsung",
            "00-26-D6": "Samsung",
            "00-26-D7": "Samsung",
            "00-26-D8": "Samsung",
            "00-26-D9": "Samsung",
            "00-26-DA": "Samsung",
            "00-26-DB": "Samsung",
            "00-26-DC": "Samsung",
            "00-26-DD": "Samsung",
            "00-26-DE": "Samsung",
            "00-26-DF": "Samsung",
            "00-26-E0": "Samsung",
            "00-26-E1": "Samsung",
            "00-26-E2": "Samsung",
            "00-26-E3": "Samsung",
            "00-26-E4": "Samsung",
            "00-26-E5": "Samsung",
            "00-26-E6": "Samsung",
            "00-26-E7": "Samsung",
            "00-26-E8": "Samsung",
            "00-26-E9": "Samsung",
            "00-26-EA": "Samsung",
            "00-26-EB": "Samsung",
            "00-26-EC": "Samsung",
            "00-26-ED": "Samsung",
            "00-26-EE": "Samsung",
            "00-26-EF": "Samsung",
            "00-26-F0": "Samsung",
            "00-26-F1": "Samsung",
            "00-26-F2": "Samsung",
            "00-26-F3": "Samsung",
            "00-26-F4": "Samsung",
            "00-26-F5": "Samsung",
            "00-26-F6": "Samsung",
            "00-26-F7": "Samsung",
            "00-26-F8": "Samsung",
            "00-26-F9": "Samsung",
            "00-26-FA": "Samsung",
            "00-26-FB": "Samsung",
            "00-26-FC": "Samsung",
            "00-26-FD": "Samsung",
            "00-26-FE": "Samsung",
            "00-26-FF": "Samsung",
        }
        vendor = vendors.get(oui, "")

    return {
        "ip": ip,
        "mac": mac,
        "hostname": hostname,
        "vendor": vendor,
        "last_seen": datetime.now().isoformat()
    }


def scan_network():
    """Scan local network for connected devices."""
    # Get local IP and subnet
    local_ip = ""
    subnet = ""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        pass

    if not local_ip:
        return {"error": "Cannot determine local IP", "devices": []}

    # Assume /24 subnet
    parts = local_ip.split(".")
    subnet = ".".join(parts[:3])

    # Get existing ARP entries first
    arp_entries = get_arp_table()
    known_ips = {e["ip"] for e in arp_entries}

    # Ping sweep
    devices = []
    ips_to_ping = [f"{subnet}.{i}" for i in range(1, 256)]

    with ThreadPoolExecutor(max_workers=50) as executor:
        future_to_ip = {executor.submit(ping_host, ip, 1): ip for ip in ips_to_ping}
        for future in as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                if future.result():
                    devices.append(get_device_info(ip))
            except:
                pass

    # Add ARP entries that didn't respond to ping
    for entry in arp_entries:
        if entry["ip"] not in known_ips or entry["ip"] not in [d["ip"] for d in devices]:
            if entry["ip"].startswith(subnet + "."):
                dev = get_device_info(entry["ip"])
                if dev["mac"] == entry["mac"]:
                    devices.append(dev)

    # Sort by IP
    devices.sort(key=lambda d: tuple(int(x) for x in d["ip"].split(".")))

    return {
        "local_ip": local_ip,
        "subnet": subnet,
        "devices": devices,
        "scan_time": datetime.now().isoformat()
    }


# ─── Network Stats ─────────────────────────────────────────────────

def get_network_stats():
    """Get network interface statistics via PowerShell."""
    ps_script = """
    Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | ForEach-Object {
        $stats = $_ | Get-NetAdapterStatistics
        [PSCustomObject]@{
            Name = $_.Name
            InterfaceDescription = $_.InterfaceDescription
            MacAddress = $_.MacAddress
            LinkSpeed = $_.LinkSpeed
            ReceivedBytes = $stats.ReceivedBytes
            SentBytes = $stats.SentBytes
            ReceivedPackets = $stats.ReceivedPackets
            SentPackets = $stats.SentPackets
            ReceivedDiscarded = $stats.ReceivedDiscardedPackets
            SentDiscarded = $stats.OutboundDiscardedPackets
        }
    } | ConvertTo-Json -Depth 3
    """
    raw = run_powershell(ps_script, timeout=15)
    if not raw or "ERROR" in raw:
        return []
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return [data]
        return data
    except:
        return []


def get_network_connections():
    """Get detailed network connections with process names."""
    ps_script = """
    Get-NetTCPConnection | Where-Object {$_.State -eq 'Established' -or $_.State -eq 'Listen'} | ForEach-Object {
        $proc = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
        [PSCustomObject]@{
            LocalAddress = $_.LocalAddress
            LocalPort = $_.LocalPort
            RemoteAddress = $_.RemoteAddress
            RemotePort = $_.RemotePort
            State = $_.State
            OwningProcess = $_.OwningProcess
            ProcessName = if ($proc) { $proc.ProcessName } else { "Unknown" }
        }
    } | ConvertTo-Json -Depth 3
    """
    raw = run_powershell(ps_script, timeout=15)
    if not raw or "ERROR" in raw:
        return []
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return [data]
        return data
    except:
        return []


# ─── API Routes ────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/wifi")
def api_wifi():
    return jsonify(get_wifi_info())


@app.route("/api/wifi/networks")
def api_wifi_networks():
    return jsonify(get_wifi_networks())


@app.route("/api/arp")
def api_arp():
    return jsonify(get_arp_table())


@app.route("/api/interfaces")
def api_interfaces():
    return jsonify(get_interfaces())


@app.route("/api/netstat")
def api_netstat():
    return jsonify(get_netstat())


@app.route("/api/scan")
def api_scan():
    return jsonify(scan_network())


@app.route("/api/stats")
def api_stats():
    return jsonify(get_network_stats())


@app.route("/api/connections")
def api_connections():
    return jsonify(get_network_connections())


@app.route("/api/all")
def api_all():
    """Get all data in one call."""
    return jsonify({
        "wifi": get_wifi_info(),
        "wifi_networks": get_wifi_networks(),
        "arp": get_arp_table(),
        "interfaces": get_interfaces(),
        "netstat": get_netstat(),
        "stats": get_network_stats(),
        "connections": get_network_connections(),
        "timestamp": datetime.now().isoformat()
    })


# ─── Main ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  Local Network Monitoring UI")
    print("  http://localhost:5000")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=False)
