---
name: tailscale
description: Comprehensive Tailscale VPN management - secure private networking, mesh VPN, peer-to-peer connections, MagicDNS, subnet routing, exit nodes, and SSH.
metadata: {"openclaw":{"emoji":"🔐","requires":{"bins":["tailscale"]}}}
---

# Tailscale Skill

Complete Tailscale mesh VPN management for secure private networking across all your devices.

## What is Tailscale?

Tailscale creates a secure private network (tailnet) connecting all your devices:
- **Zero-config VPN** - Devices see each other instantly
- **Peer-to-peer** - Direct connections when possible, encrypted relays when not
- **Magic DNS** - Access devices by name (`ssh mac-mini` instead of IPs)
- **Cross-platform** - macOS, Linux, Windows, iOS, Android, everywhere

## Setup

### Install Tailscale

**macOS:**
```bash
brew install tailscale
brew services start tailscale
```

**Linux:**
```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

**Windows:**
Download from https://tailscale.com/download

### Authenticate

```bash
# First-time setup (opens browser)
{baseDir}/scripts/tailscale.sh up

# Or use the CLI directly
tailscale up
```

This opens a browser for authentication. Sign in with your Google/Microsoft/GitHub account.

## Quick Commands

### Status & Info

```bash
# Check connection status
{baseDir}/scripts/tailscale.sh status

# Detailed JSON status
{baseDir}/scripts/tailscale.sh status --json

# Get your Tailscale IPs
{baseDir}/scripts/tailscale.sh ip

# Get another device's IP
{baseDir}/scripts/tailscale.sh ip mac-mini

# Who is this IP?
{baseDir}/scripts/tailscale.sh whois 100.x.y.z
```

### Network Operations

```bash
# Ping a device (Tailscale-specific ping)
{baseDir}/scripts/tailscale.sh ping mac-mini

# Test network conditions
{baseDir}/scripts/tailscale.sh netcheck

# SSH to a device
{baseDir}/scripts/tailscale.sh ssh alice@mac-mini

# Connect/disconnect
{baseDir}/scripts/tailscale.sh up      # Connect
{baseDir}/scripts/tailscale.sh down    # Disconnect
```

### Serve & Funnel

```bash
# Serve a local service to your tailnet
{baseDir}/scripts/tailscale.sh serve http://localhost:3000

# Expose to public internet (Tailscale Funnel)
{baseDir}/scripts/tailscale.sh funnel http://localhost:3000

# Check serve/funnel status
{baseDir}/scripts/tailscale.sh serve status
{baseDir}/scripts/tailscale.sh funnel status
```

### File Sharing (Taildrop)

```bash
# Send file to another device
{baseDir}/scripts/tailscale.sh file cp file.txt mac-mini:

# Receive files
{baseDir}/scripts/tailscale.sh file get ~/Downloads/
```

### Exit Nodes

```bash
# Use a device as exit node (route all traffic through it)
{baseDir}/scripts/tailscale.sh up --exit-node=mac-mini

# Use auto-selected exit node
{baseDir}/scripts/tailscale.sh set --exit-node=auto:any

# Disable exit node
{baseDir}/scripts/tailscale.sh set --exit-node=

# List available exit nodes
{baseDir}/scripts/tailscale.sh exit-node list

# Advertise this device as an exit node
{baseDir}/scripts/tailscale.sh up --advertise-exit-node
```

### Subnet Routing

```bash
# Advertise subnet routes (share local network)
{baseDir}/scripts/tailscale.sh up --advertise-routes=192.168.1.0/24,10.0.0.0/24

# Accept subnet routes from other devices
{baseDir}/scripts/tailscale.sh up --accept-routes

# Update routes without reconnecting
{baseDir}/scripts/tailscale.sh set --advertise-routes=192.168.1.0/24
```

### Access Control

```bash
# Enable SSH server
{baseDir}/scripts/tailscale.sh up --ssh

# Enable shields-up (block incoming)
{baseDir}/scripts/tailscale.sh up --shields-up

# Update settings
{baseDir}/scripts/tailscale.sh set --ssh=true
{baseDir}/scripts/tailscale.sh set --shields-up=false
```

## Advanced Features

### MagicDNS

Automatically enabled. Access devices by name:
```bash
# Instead of:
ssh 100.64.23.45

# Use:
ssh mac-mini
ping raspberrypi-cahul
curl http://m1-macbook:8080
```

### Tailscale SSH

Zero-config SSH with certificates:
```bash
# Enable SSH server on a device
tailscale up --ssh

# Connect from another device (no keys needed)
tailscale ssh user@hostname
```

### Tailscale Serve

Share local services with your tailnet:
```bash
# Serve web app on port 3000
tailscale serve http://localhost:3000

# Serve on specific path
tailscale serve --http /app http://localhost:3000

# Serve HTTPS with auto-cert
tailscale serve --https /app http://localhost:3000

# Check what's being served
tailscale serve status
```

### Tailscale Funnel

Expose services to public internet:
```bash
# WARNING: Exposes to internet!
tailscale funnel http://localhost:3000

# Status
tailscale funnel status

# Stop funnel
tailscale funnel reset
```

### Taildrive (File Sharing)

Share directories with your tailnet:
```bash
# Share a directory
tailscale drive share ~/Documents shared-docs

# List shares
tailscale drive list

# Rename share
tailscale drive rename shared-docs company-docs

# Remove share
tailscale drive unshare shared-docs
```

## Common Use Cases

### Use Case 1: Access Home Lab from Anywhere

**Setup:**
```bash
# On home server (advertise subnet)
tailscale up --advertise-routes=192.168.1.0/24 --ssh

# On laptop (accept routes)
tailscale up --accept-routes
```

**Access:**
```bash
# SSH to home server
tailscale ssh alice@home-server

# Access devices on home network
ssh pi@192.168.1.100
curl http://192.168.1.50:8123  # Home Assistant
```

### Use Case 2: Secure Remote Desktop

**Setup:**
```bash
# On desktop machine
tailscale up --ssh
```

**Access:**
```bash
# From laptop
tailscale ssh alice@desktop
# Or use VNC/RDP via Tailscale IP
open vnc://100.x.y.z
```

### Use Case 3: Connect Multiple Locations

**Jerusalem → Cahul → Turkey → Romania:**
```bash
# Install Tailscale on all machines
# They auto-discover each other

# Access any machine from any location
ssh mac-mini-cahul
ssh raspberrypi-jerusalem
curl http://server-turkey:8080
```

### Use Case 4: Share Development Server

**Setup:**
```bash
# On dev machine
cd my-project
npm run dev  # Starts on localhost:3000
tailscale serve http://localhost:3000
```

**Access:**
```bash
# From any device on your tailnet
open http://dev-machine:443
```

### Use Case 5: Secure Travel Internet

**Setup:**
```bash
# On home/office machine (always-on)
tailscale up --advertise-exit-node

# Enable in admin console:
# Settings → Machines → [device] → Edit Route Settings → Use as exit node
```

**Use:**
```bash
# On laptop while traveling
tailscale up --exit-node=home-server

# All traffic now routes through home
# Encrypted, secure, bypass geo-restrictions
```

## Integration with Cloudflare

### Hybrid Approach (Recommended)

**Tailscale for:**
- Internal services (n8n, databases, admin tools)
- Device-to-device communication
- Remote access (SSH, VNC)
- Development/testing

**Cloudflare for:**
- Public-facing websites
- Client/customer access
- Production SaaS products
- DDoS protection

**Example Migration:**
```bash
# Before (Cloudflare):
n8n.emaygroup.org → Public tunnel → Access policy

# After (Tailscale):
mac-mini:5678 → Private → Direct connection

# Benefit: Faster, more secure, simpler
```

## Troubleshooting

### Connection Issues

```bash
# Detailed network diagnostics
tailscale netcheck

# Test connection to specific device
tailscale ping mac-mini --verbose

# Check DERP relay being used
tailscale status --json | jq '.Peer[] | select(.HostName=="mac-mini") | .CurAddr'
```

### Can't Reach Device

```bash
# Verify device is online
tailscale status | grep mac-mini

# Check if firewall blocking
tailscale ping mac-mini --tsmp

# Verify routes
tailscale status --json | jq '.Peer[] | {name:.HostName, routes:.AllowedIPs}'
```

### DNS Not Working

```bash
# Check MagicDNS status
tailscale dns status

# Force refresh
tailscale down && tailscale up
```

### Slow Performance

```bash
# Check if using direct connection
tailscale status
# Look for "direct" vs "relay" in CurAddr column

# If relay only, check firewall/NAT
tailscale netcheck
```

## Security Best Practices

### 1. Use Tailnet Lock
```bash
# Enable hardware-based auth
tailscale lock init
```

### 2. Configure ACLs

Edit at https://login.tailscale.com/admin/acls
```json
{
  "acls": [
    {
      "action": "accept",
      "src": ["ali@emaygroup.org"],
      "dst": ["*:*"]
    },
    {
      "action": "accept",
      "src": ["group:family"],
      "dst": ["tag:homelab:*"]
    }
  ]
}
```

### 3. Tag Critical Servers
```bash
tailscale up --advertise-tags=tag:production,tag:critical
```

### 4. Enable Audit Logs

Admin console → Settings → Logs
- Enable activity logs
- Export to SIEM if needed

### 5. Use Key Expiry
- Default: Keys expire after 180 days
- Disable expiry only for servers (not personal devices)

## Quick Reference

| Task | Command |
|------|---------|
| Connect | `tailscale up` |
| Disconnect | `tailscale down` |
| Status | `tailscale status` |
| My IPs | `tailscale ip` |
| Ping device | `tailscale ping <device>` |
| SSH to device | `tailscale ssh user@device` |
| Send file | `tailscale file cp file.txt device:` |
| Serve web app | `tailscale serve http://localhost:PORT` |
| Use as VPN | `tailscale up --exit-node=device` |
| Share subnet | `tailscale up --advertise-routes=CIDR` |
| Enable SSH | `tailscale up --ssh` |

## Environment Variables

The skill script sources credentials from:
- `~/.openclaw/secrets/tailscale.env` (if exists)

Example:
```bash
# Optional: Pre-auth key for automation
TAILSCALE_AUTHKEY=tskey-auth-xxxxx
```

## Resources

- **Documentation:** https://tailscale.com/docs
- **Admin Console:** https://login.tailscale.com/admin
- **Community:** https://forum.tailscale.com
- **Status:** https://status.tailscale.com

## Script Location

Main wrapper: `{baseDir}/scripts/tailscale.sh`

This wraps the native `tailscale` CLI and adds:
- Credential management
- Logging
- Error handling
- Shortcuts for common operations
