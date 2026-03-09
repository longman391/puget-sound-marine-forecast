# Deployment Guide

## Docker (any host)

```bash
docker run -d \
  --name marine-forecast \
  -p 8000:8000 \
  -e API_KEY=your-secret-key \
  -e CACHE_INTERVAL_MINUTES=60 \
  --restart unless-stopped \
  ghcr.io/longman391/puget-sound-marine-forecast:latest
```

Or with docker-compose (clone the repo first):

```bash
cp .env.example .env
# Edit .env with your settings
docker compose up -d
```

## Unraid

### Option A: Community Applications (when published)

1. Open the **Apps** tab in Unraid
2. Search for "Puget Sound Marine Forecast"
3. Click **Install** and configure the template variables
4. Click **Apply**

### Option B: Manual install via template URL

1. Go to **Docker** → **Add Container**
2. Click **Template Repositories** at the bottom
3. Add: `https://github.com/longman391/puget-sound-marine-forecast`
4. Click **Save**, then select "PugetSoundMarineForecast" from the template dropdown
5. Configure variables and click **Apply**

### Option C: Manual Docker install on Unraid

1. Go to **Docker** → **Add Container**
2. Set **Repository** to `ghcr.io/longman391/puget-sound-marine-forecast:latest`
3. Add a port mapping: Host `8000` → Container `8000`
4. Add environment variables as needed (see Configuration below)
5. Click **Apply**

## Making it Internet-Facing (forecast.longmanhome.com)

For Dakboard, external agents, or public access, the service needs to be reachable
from the internet. Here are three approaches, from simplest to most flexible:

### Option 1: Cloudflare Tunnel (recommended)

The safest way to expose a home-hosted service — no port forwarding required.

1. Install `cloudflared` on your Unraid server (available as a Docker container)
2. Create a tunnel: `cloudflared tunnel create marine-forecast`
3. Configure the tunnel to point `forecast.longmanhome.com` → `http://localhost:8000`
4. Add a CNAME record in Cloudflare DNS pointing to the tunnel

```yaml
# cloudflared config.yml
tunnel: <tunnel-id>
credentials-file: /root/.cloudflared/<tunnel-id>.json
ingress:
  - hostname: forecast.longmanhome.com
    service: http://localhost:8000
  - service: http_status:404
```

**Pros:** No ports exposed, automatic HTTPS, Cloudflare DDoS protection.
**Cons:** Requires a Cloudflare account and domain managed by Cloudflare.

### Option 2: Nginx Proxy Manager (Unraid)

If you already run Nginx Proxy Manager on Unraid:

1. Add a new proxy host for `forecast.longmanhome.com`
2. Set the forward hostname/IP to the Unraid server IP and port `8000`
3. Enable SSL via Let's Encrypt
4. Set up port forwarding on your router: external 443 → Unraid NPM port

### Option 3: Azure Container App (secondary deployment)

Deploy the same Docker image to Azure as a secondary target:

```bash
# One-time setup
az containerapp up \
  --name marine-forecast \
  --resource-group marine-forecast-rg \
  --image ghcr.io/longman391/puget-sound-marine-forecast:latest \
  --target-port 8000 \
  --env-vars API_KEY=your-key CACHE_INTERVAL_MINUTES=60 \
  --ingress external

# Point forecast.longmanhome.com to the Azure FQDN via CNAME
```

**Pros:** Always available, no home network dependency.
**Cons:** Costs money (Azure Container Apps consumption plan is ~$0-5/month for low traffic).

## Authentication for External Clients

### Home Assistant

```yaml
# configuration.yaml
sensor:
  - platform: rest
    name: puget_sound_forecast
    resource: https://forecast.longmanhome.com/api/v1/forecast/PZZ135
    headers:
      X-API-Key: your-api-key
    value_template: "{{ value_json.has_active_advisory }}"
    json_attributes:
      - zone_name
      - forecast_text
      - advisory_text
      - has_active_advisory
      - has_upcoming_advisory
    scan_interval: 3600
```

### Dakboard

Dakboard REST widgets use URL-based auth:

```
https://forecast.longmanhome.com/api/v1/forecast/PZZ135?api_key=your-api-key
```

Configure as a "Custom" widget with JSON path to extract the fields you want.

## Publishing to Unraid Community Apps Store

When ready to publish to the official Community Apps store:

1. Ensure the Docker image is publicly available on GHCR (it will be after the
   first `publish.yml` workflow run)
2. Create an Unraid forum support thread for the app
3. Update the `<Support>` URL in `unraid/puget-sound-marine-forecast.xml`
4. Submit the template to the Community Applications maintainers via the
   [Unraid forums](https://forums.unraid.net/forum/38-docker-containers/)
5. Optionally create a dedicated template repo (`longman391/unraid-templates`)
   with just the XML file, if the CA team prefers that structure
