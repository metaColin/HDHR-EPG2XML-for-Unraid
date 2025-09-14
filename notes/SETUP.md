# SETUP.md

## Local Development Setup

### Prerequisites
- Docker Desktop or Docker Engine
- HDHomeRun device on network
- Git
- Text editor (VS Code recommended)

### Quick Start
```bash
# Clone repository
git clone <repository-url>
cd HDHR-EPG2XML-for-Unraid

# Build Docker image
docker build -t hdhomerun-epg:dev .

# Run with docker-compose (edit IP first)
vim docker-compose.yml  # Set HDHOMERUN_HOST
docker-compose up
```

### Environment Variables
Create `.env` file for local development:
```bash
HDHOMERUN_HOST=192.168.1.100  # Your HDHomeRun IP
CRON_SCHEDULE=0 3 * * *       # 3 AM daily
TZ=America/New_York            # Your timezone
WEB_PORT=8083                  # HTTP server port
DEBUG=on                       # Enable debug logging
RUN_ON_START=true             # Generate EPG on startup
DAYS=7                        # Days of EPG to fetch
HOURS=3                       # Hours between updates
```

### Testing Endpoints
```bash
# Check server status
curl http://localhost:8083/status

# Get EPG data
curl http://localhost:8083/epg.xml

# Get EPG with dummy programming
curl "http://localhost:8083/epg.xml?dummy=1hr"

# Get EPG in different format
curl "http://localhost:8083/epg.xml?format=raw"

# Combine parameters
curl "http://localhost:8083/epg.xml?format=plex&dummy=30min"
```

### Development Workflow
```bash
# Make changes to Python files
vim epg_server.py

# Rebuild image
docker build -t hdhomerun-epg:dev .

# Restart container
docker-compose down
docker-compose up

# Check logs
docker logs hdhomerun-epg

# Enter container for debugging
docker exec -it hdhomerun-epg /bin/bash
```

### Testing with Media Servers
1. **Plex**: Settings → Live TV & DVR → Set Up → XMLTV → `http://host.docker.internal:8083/epg.xml`
2. **Jellyfin**: Live TV → TV Guide Data Providers → Add → XMLTV → `http://localhost:8083/epg.xml`
3. **Emby**: Live TV → TV Guide Data → Add → XMLTV → `http://localhost:8083/epg.xml`

### Common Commands
```bash
# View running containers
docker ps

# Stop container
docker stop hdhomerun-epg

# Remove container
docker rm hdhomerun-epg

# View logs in real-time
docker logs -f hdhomerun-epg

# Check cron jobs inside container
docker exec hdhomerun-epg crontab -l

# Manually trigger EPG update
docker exec hdhomerun-epg python3 /app/HDHomeRunEPG_To_XmlTv.py --host <IP>

# Check EPG file size
docker exec hdhomerun-epg ls -lh /output/epg.xml
```

### Troubleshooting
- **Port 8083 in use**: Change WEB_PORT in .env
- **Can't find HDHomeRun**: Ensure device is on same network, try IP instead of hostname
- **No EPG data**: Check `docker logs`, verify HDHomeRun has channel lineup
- **Plex won't accept**: Ensure using actual IP, not localhost
- **Container won't start**: Check `docker logs` for Python errors