# Network Monitor — Local WiFi & Device Dashboard

A deployable local web UI that monitors your WiFi connection, connected devices, and all network activity in real time.

## Features

- **WiFi Monitor** — Live SSID, signal strength, band, channel, authentication, cipher, BSSID, RSSI, link speed
- **Device Discovery** — Network scan that finds all connected devices with IP, MAC, hostname, and vendor identification
- **Available Networks** — See all nearby WiFi networks with signal strength
- **ARP Table** — IP-to-MAC address mappings with interface info
- **TCP/UDP Connections** — Active connections with process names and states
- **Network Interfaces** — All adapters with IPv4/IPv6/MAC details
- **Traffic Statistics** — Per-interface RX/TX bytes and packet counts
- **Auto-refresh** — Data updates every 30 seconds

## Quick Start

### Git Clone & Run
```bash
git clone <repo-url>
cd network-all-in-one/skills/network-monitor
pip install -r requirements.txt
python app.py
```

### Option 1: Double-click launcher (Windows)
```
start.bat
```

### Option 2: Manual
```bash
pip install -r requirements.txt
python app.py
```

Then open **http://localhost:5000** in your browser.

## Requirements

- Windows 10/11 (uses netsh, arp, netstat, PowerShell)
- Python 3.8+
- Flask (`pip install flask`)

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/wifi` | Current WiFi connection details |
| `GET /api/wifi/networks` | Available WiFi networks |
| `GET /api/arp` | ARP table |
| `GET /api/interfaces` | Network interface details |
| `GET /api/netstat` | TCP/UDP connections |
| `GET /api/scan` | Network device scan |
| `GET /api/stats` | Interface traffic statistics |
| `GET /api/connections` | Connections with process names |
| `GET /api/all` | Everything in one call |

## Files

- `app.py` — Flask backend with all API endpoints
- `templates/index.html` — Dark-themed dashboard UI
- `start.bat` — One-click launcher
- `requirements.txt` — Python dependencies

## Notes

- The server binds to `0.0.0.0:5000` so it's accessible from other devices on your LAN
- Device scan pings all 254 hosts on your /24 subnet (takes a few seconds)
- MAC vendor identification covers common OUIs (Raspberry Pi, Samsung, Amazon, Dell, VMware, etc.)
- No external dependencies beyond Flask — uses only Windows built-in networking tools
