---
name: cloudflare
description: Comprehensive Cloudflare API skill for DNS, Tunnels, Zero Trust, Workers, Pages, R2, KV, D1, and more. Supports token creation for granular permissions.
metadata: {"openclaw":{"emoji":"☁️","requires":{"bins":["curl","jq"]}}}
---

# Cloudflare Skill

Full Cloudflare platform access via API.

## Setup

Store credentials in `~/.openclaw/secrets/cloudflare.env` or `~/clawd/.secrets/cloudflare.env`:

```bash
# Option 1: Full access token (can create other tokens)
CLOUDFLARE_API_TOKEN=<token-with-create-permissions>

# Option 2: Service-specific tokens
CLOUDFLARE_API_TOKEN=<dns-token>
CLOUDFLARE_ZERO_TRUST_TOKEN=<zero-trust-token>
CLOUDFLARE_ACCESS_TOKEN=<access-token>
CLOUDFLARE_WORKERS_TOKEN=<workers-token>
```

**Recommended:** Provide a token with "API Tokens: Edit" permission so OpenClaw can create scoped tokens as needed.

## ⚠️ Token Creator — LOCKED RULE (2026-03-19)

**We have a token creator token.** NEVER ask Ali to create tokens in the dashboard.

- **`CLOUDFLARE_TOKEN_CREATOR`** in `~/.openclaw/secrets/cloudflare.env` (also in `openclaw.json` env as `CLOUDFLARE_API_TOKEN`)
- This token has **`API Tokens: Edit`** permission — it can mint ANY scoped token via the API
- **Workflow when you need a new Cloudflare permission:**
  1. Use `CLOUDFLARE_TOKEN_CREATOR` to call `GET /user/tokens/permission_groups` — find the permission group IDs you need
  2. Call `POST /user/tokens` with those permission groups to mint a new scoped token
  3. Save the new token to `~/.openclaw/secrets/cloudflare.env`
  4. Use it

```bash
# Example: mint a new token with Zone Write + DNS Write
TOKEN_CREATOR="$(grep CLOUDFLARE_TOKEN_CREATOR ~/.openclaw/secrets/cloudflare.env | cut -d= -f2)"

# 1. Find permission group IDs
curl -s "https://api.cloudflare.com/client/v4/user/tokens/permission_groups" \
  -H "Authorization: Bearer $TOKEN_CREATOR" | jq '[.result[] | select(.name | test("Zone Write|DNS Write")) | {id, name}]'

# 2. Create scoped token
curl -s -X POST "https://api.cloudflare.com/client/v4/user/tokens" \
  -H "Authorization: Bearer $TOKEN_CREATOR" \
  -H "Content-Type: application/json" \
  --data '{"name":"My Scoped Token","policies":[{"effect":"allow","resources":{"com.cloudflare.api.account.9d83562c2c3ba1ab31c90cb52d8a8c81":"*"},"permission_groups":[{"id":"<perm-group-id>"}]}]}'
```

### Existing Scoped Tokens
| Env Variable | Permissions | Created |
|---|---|---|
| `CLOUDFLARE_API_TOKEN` | General ops (tunnels, access, DNS for existing zones) | Legacy |
| `CLOUDFLARE_ZONE_TOKEN` | Zone Write + DNS Write + Email Routing (all account zones) | 2026-03-19 |
| `CLOUDFLARE_TUNNEL_TOKEN` | Tunnel-specific | Legacy |

### Account Details
- **Account ID:** `9d83562c2c3ba1ab31c90cb52d8a8c81`
- **Primary zone:** `emaygroup.org` (`f221600817fe40bff2d0dc5dfe293faa`)

## Available Services

| Service | Description | Token Permission Needed |
|---------|-------------|------------------------|
| **DNS** | Manage DNS records | Zone:DNS:Edit |
| **Tunnels** | Cloudflare Tunnel management | Account:Cloudflare Tunnel:Edit |
| **Zero Trust** | Access policies, Gateway, WARP | Account:Access:Edit |
| **Workers** | Serverless functions | Account:Workers Scripts:Edit |
| **Pages** | JAMstack deployments | Account:Pages:Edit |
| **R2** | Object storage | Account:Workers R2 Storage:Edit |
| **KV** | Key-Value storage | Account:Workers KV Storage:Edit |
| **D1** | SQLite database | Account:D1:Edit |
| **Images** | Image optimization/storage | Account:Cloudflare Images:Edit |
| **Stream** | Video streaming | Account:Stream:Edit |
| **Load Balancing** | Traffic distribution | Zone:Load Balancers:Edit |
| **SSL/TLS** | Certificate management | Zone:SSL and Certificates:Edit |
| **Firewall** | WAF rules | Zone:Firewall Services:Edit |
| **Analytics** | Traffic analytics | Zone:Analytics:Read |

## Quick Commands

### DNS

```bash
# List DNS records
{baseDir}/scripts/cloudflare.sh dns list <zone-id>

# Create record
{baseDir}/scripts/cloudflare.sh dns create <zone-id> <type> <name> <content> [proxied]

# Delete record
{baseDir}/scripts/cloudflare.sh dns delete <zone-id> <record-id>

# List zones
{baseDir}/scripts/cloudflare.sh zones list
```

### Tunnels

```bash
# List tunnels
{baseDir}/scripts/cloudflare.sh tunnel list

# Get tunnel config
{baseDir}/scripts/cloudflare.sh tunnel config <tunnel-id>

# Update tunnel ingress
{baseDir}/scripts/cloudflare.sh tunnel ingress <tunnel-id> <hostname> <service>

# Create tunnel
{baseDir}/scripts/cloudflare.sh tunnel create <name>
```

### Zero Trust / Access

```bash
# List Access applications
{baseDir}/scripts/cloudflare.sh access apps

# List Access policies
{baseDir}/scripts/cloudflare.sh access policies <app-id>

# Create bypass rule
{baseDir}/scripts/cloudflare.sh access bypass <app-id> <path>
```

### Workers

```bash
# List workers
{baseDir}/scripts/cloudflare.sh workers list

# Deploy worker
{baseDir}/scripts/cloudflare.sh workers deploy <name> <script-file>

# Delete worker
{baseDir}/scripts/cloudflare.sh workers delete <name>
```

### KV

```bash
# List namespaces
{baseDir}/scripts/cloudflare.sh kv namespaces

# Get value
{baseDir}/scripts/cloudflare.sh kv get <namespace-id> <key>

# Set value
{baseDir}/scripts/cloudflare.sh kv set <namespace-id> <key> <value>
```

### R2

```bash
# List buckets
{baseDir}/scripts/cloudflare.sh r2 buckets

# Create bucket
{baseDir}/scripts/cloudflare.sh r2 create <bucket-name>
```

### Health Diagnostics

```bash
# Full health check (tunnels + ingress + DNS + SSL)
{baseDir}/scripts/cloudflare.sh health full [tunnel-id] [zone-id]

# Check all tunnel statuses
{baseDir}/scripts/cloudflare.sh health tunnels

# Detailed tunnel info with connections
{baseDir}/scripts/cloudflare.sh health tunnel <tunnel-id>

# Test all ingress routes (local backend + public URL)
{baseDir}/scripts/cloudflare.sh health ingress <tunnel-id>

# Check DNS resolution for all records
{baseDir}/scripts/cloudflare.sh health dns [zone-id]

# Check SSL certificate status
{baseDir}/scripts/cloudflare.sh health ssl [zone-id]
```

### Token Management

```bash
# Verify current token
{baseDir}/scripts/cloudflare.sh token verify

# Create new scoped token
{baseDir}/scripts/cloudflare.sh token create <name> <permissions-json>

# List tokens
{baseDir}/scripts/cloudflare.sh token list
```

## Account & Zone IDs

Get your IDs:
```bash
# List zones with IDs
{baseDir}/scripts/cloudflare.sh zones list

# Get account ID from zone
{baseDir}/scripts/cloudflare.sh account id
```

## Environment Variables

The script auto-sources from:
1. `~/.openclaw/secrets/cloudflare.env`
2. `~/clawd/.secrets/cloudflare.env`

Or set directly:
```bash
export CLOUDFLARE_API_TOKEN=<your-token>
export CLOUDFLARE_ACCOUNT_ID=<your-account-id>
```

## Token Permissions Reference

For full access, create a token with:
- **Account:API Tokens:Edit** - Create/manage other tokens
- **Account:Cloudflare Tunnel:Edit** - Tunnel management
- **Account:Access: Organizations, Identity Providers, and Groups:Edit** - Zero Trust
- **Zone:DNS:Edit** - DNS management
- **All zones** or specific zones as needed

## Examples

### Add subdomain to tunnel
```bash
# Get tunnel ID
TUNNEL_ID=$({baseDir}/scripts/cloudflare.sh tunnel list | jq -r '.[] | select(.name=="mac-mini") | .id')

# Add ingress
{baseDir}/scripts/cloudflare.sh tunnel ingress $TUNNEL_ID "app.example.com" "http://localhost:3000"
```

### Create DNS + Tunnel route
```bash
ZONE_ID="your-zone-id"
TUNNEL_ID="your-tunnel-id"

# Add CNAME for tunnel
{baseDir}/scripts/cloudflare.sh dns create $ZONE_ID CNAME myapp "${TUNNEL_ID}.cfargotunnel.com" true

# Add ingress route
{baseDir}/scripts/cloudflare.sh tunnel ingress $TUNNEL_ID "myapp.example.com" "http://localhost:8080"
```
