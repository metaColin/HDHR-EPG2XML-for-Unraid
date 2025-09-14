# HDHR-EPG2XML-for-Unraid

HDHomeRun EPG to XML converter for Unraid - Dockerized Python application that fetches Electronic Program Guide (EPG) data from HDHomeRun devices and serves it via HTTP in XMLTV format for use with TV software like Plex, Emby, or Jellyfin.

## Architecture
- **Core Script**: `HDHomeRunEPG_To_XmlTv.py` (GPL licensed, included)
- **Web Server**: Built-in HTTP server serving EPG data on configurable port (default: 8083)
- **Containerization**: Docker with Python 3.11-slim base
- **Scheduling**: Cron-based automatic updates with supervisor process management
- **Output**: XMLTV formatted EPG data served via HTTP at `http://<container>:8083/epg.xml`

## Quick Start

### Using Docker Compose
```bash
# Edit docker-compose.yml to set your HDHomeRun IP
vim docker-compose.yml

# Start the container
docker-compose up -d

# Access EPG at:
http://localhost:8083/epg.xml
```

### Using Docker Run
```bash
# Build the image
docker build -t hdhomerun-epg .

# Run the container
docker run -d \
  --name hdhomerun-epg \
  -p 8083:8083 \
  -e HDHOMERUN_HOST=192.168.1.100 \
  -e CRON_SCHEDULE="0 3 * * *" \
  -e TZ=America/New_York \
  hdhomerun-epg
```

## HTTP Endpoints

- **`/`** - Web interface with links to all endpoints
- **`/epg.xml`** - XMLTV formatted EPG data
- **`/status`** - JSON status of the server and EPG file
- **`/health`** - Simple health check endpoint

## Configure Your Media Server

Point your media server to the EPG URL:
- **Plex**: `http://<unraid-ip>:8083/epg.xml`
- **Emby**: `http://<unraid-ip>:8083/epg.xml`
- **Jellyfin**: `http://<unraid-ip>:8083/epg.xml`

No volume mounting required!

## Environment Variables
- `HDHOMERUN_HOST`: HDHomeRun device hostname/IP (default: hdhomerun.local)
- `OUTPUT_FILENAME`: Internal EPG file path (default: /output/epg.xml)
- `DAYS`: Days of EPG data to fetch (default: 7)
- `HOURS`: Hours per update interval (default: 3)
- `DEBUG`: Debug mode on/off (default: on)
- `TZ`: Timezone (e.g., America/New_York)
- `CRON_SCHEDULE`: Cron schedule for updates (default: "0 3 * * *" - 3 AM daily)
- `RUN_ON_START`: Run EPG update on container start (default: true)
- `WEB_PORT`: HTTP server port (default: 8083)

## File Structure
- **Dockerfile**: Container definition with cron and web server
- **docker-compose.yml**: Ready-to-use Docker Compose configuration
- **HDHomeRunEPG_To_XmlTv.py**: Core EPG extraction script (GPL licensed)
- **epg_server.py**: HTTP server for EPG distribution
- **supervisord.conf**: Process management configuration
- **cron-entrypoint.sh**: Container initialization and cron setup

## Important Considerations
1. **Port 8083**: Must be available on your host system (configurable via WEB_PORT)
2. **HDHomeRun Discovery**: Container needs network access to your HDHomeRun device
3. **HDHomeRun Compatibility**: Tested with HDHomeRun Flex 4K, compatible with all HDHomeRun models
4. **Timezone**: Set TZ environment variable to match local timezone for correct scheduling
5. **Initial Update**: EPG generation runs on container start (configurable via RUN_ON_START)
6. **License**: Includes GPL-licensed HDHomeRunEPG_To_XmlTv.py script

## Troubleshooting

- **No EPG data**: Check HDHomeRun IP is correct and reachable
- **Port conflict**: Change WEB_PORT if 8083 is already in use
- **Time issues**: Ensure TZ environment variable matches your timezone
- **Check logs**: `docker logs hdhomerun-epg`