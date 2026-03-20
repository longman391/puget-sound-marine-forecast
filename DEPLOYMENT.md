# Deployment

The application is packaged as a single Docker image that serves both the API and the React frontend. The multi-stage Dockerfile builds the frontend with Node 22, then bundles everything into a Python 3.12 slim image. It runs as a non-root user and includes a built-in healthcheck.

Published images support `linux/amd64` and `linux/arm64`.

## Docker Compose (recommended)

Clone the repo, copy the example config, and start the service:

```bash
cp .env.example .env
# Edit .env — at minimum, set API_KEY if you want auth enabled
docker compose up -d --build
```

The service will be available at `http://localhost:8000`.

To use the pre-built image from GHCR instead of building locally, replace the `build: .` line in `docker-compose.yml` with:

```yaml
image: ghcr.io/longman391/puget-sound-marine-forecast:latest
```

## Docker Run (standalone)

```bash
docker run -d \
  --name marine-forecast \
  -p 8000:8000 \
  -e API_KEY=your-secret-key \
  -e CACHE_INTERVAL_MINUTES=60 \
  --restart unless-stopped \
  ghcr.io/longman391/puget-sound-marine-forecast:latest
```

See the [Configuration table in README.md](README.md#configuration) for all available environment variables.

## Unraid

Three options, from easiest to most manual.

### Option A: Community Applications

1. Open the **Apps** tab in Unraid.
2. Search for "Puget Sound Marine Forecast".
3. Click **Install** and configure the template variables.
4. Click **Apply**.

### Option B: Template URL

1. Go to **Docker** > **Add Container**.
2. Click **Template Repositories** at the bottom.
3. Add: `https://github.com/longman391/puget-sound-marine-forecast`
4. Click **Save**, then select "PugetSoundMarineForecast" from the template dropdown.
5. Configure variables and click **Apply**.

### Option C: Manual

1. Go to **Docker** > **Add Container**.
2. Set **Repository** to `ghcr.io/longman391/puget-sound-marine-forecast:latest`.
3. Add a port mapping: Host `8000` > Container `8000`.
4. Add environment variables as needed.
5. Click **Apply**.

The Unraid XML template is in `unraid/puget-sound-marine-forecast.xml`.

## Exposing to the Internet

For external access (Dakboard, remote agents, etc.), the service needs to be reachable from outside your network.

### Cloudflare Tunnel (recommended)

No port forwarding required. No ports exposed on your router.

1. Install `cloudflared` on your server (available as a Docker container on Unraid).
2. Create a tunnel: `cloudflared tunnel create marine-forecast`
3. Configure the tunnel to route your hostname to `http://localhost:8000`.
4. Add a CNAME record in Cloudflare DNS pointing to the tunnel.

```yaml
# cloudflared config.yml
tunnel: <tunnel-id>
credentials-file: /root/.cloudflared/<tunnel-id>.json
ingress:
  - hostname: forecast.yourdomain.com
    service: http://localhost:8000
  - service: http_status:404
```

### Nginx Proxy Manager

If you already run Nginx Proxy Manager (common on Unraid):

1. Add a proxy host for your forecast domain.
2. Forward to your server's IP on port `8000`.
3. Enable SSL via Let's Encrypt.
4. Set up port forwarding on your router: external 443 to NPM's port.

### Cloud Deployment

The same Docker image runs on any container hosting platform. Example with Azure Container Apps:

```bash
az containerapp up \
  --name marine-forecast \
  --resource-group marine-forecast-rg \
  --image ghcr.io/longman391/puget-sound-marine-forecast:latest \
  --target-port 8000 \
  --env-vars API_KEY=your-key CACHE_INTERVAL_MINUTES=60 \
  --ingress external
```

Point your domain to the Azure FQDN via CNAME. Consumption plan costs are minimal for low-traffic services.

## Client Integration

### Home Assistant

```yaml
# configuration.yaml
sensor:
  - platform: rest
    name: puget_sound_forecast
    resource: https://forecast.yourdomain.com/api/v1/forecast/PZZ135
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

Dakboard REST widgets support URL-based auth:

```
https://forecast.yourdomain.com/api/v1/forecast/PZZ135?api_key=your-api-key
```

Configure as a "Custom" widget and use JSON path expressions to extract the fields you need.

### MCP Clients

Point any MCP-compatible client (Claude Desktop, Cursor, etc.) at:

```
https://forecast.yourdomain.com/mcp
```

The MCP server uses stateless HTTP transport. No additional configuration is needed beyond the URL. If `API_KEY` is set, the MCP endpoint still requires auth through the standard header or query parameter.

## CI/CD

The GitHub Actions workflows handle testing and publishing:

- **ci.yml** — Runs on pushes to `main`/`dev` and PRs to `main`. Lints, type-checks, tests (Python 3.12 and 3.13 matrix), and builds the Docker image.
- **publish.yml** — Triggered by version tags (`v*`) or manual dispatch. Builds multi-platform images and pushes to GHCR with semver tags.

To publish a new release:

```bash
git tag v2.1.0
git push origin v2.1.0
```

The publish workflow will build and push `ghcr.io/longman391/puget-sound-marine-forecast:2.1.0`, `:2.1`, and `:latest`.

## Publishing to Unraid Community Apps

When ready to list in the Community Apps store:

1. Ensure the Docker image is publicly available on GHCR (happens automatically after the first `publish.yml` run).
2. Create an Unraid forum support thread for the app.
3. Update the `<Support>` URL in `unraid/puget-sound-marine-forecast.xml`.
4. Submit the template to the Community Applications maintainers via the [Unraid forums](https://forums.unraid.net/forum/38-docker-containers/).
5. Optionally create a dedicated template repo (`longman391/unraid-templates`) with the XML file, if the CA team prefers that structure.
