# HDHomeRun EPG to XMLTV for Unraid

Automatically fetch Electronic Program Guide (EPG) data from your HDHomeRun device and serve it via HTTP in XMLTV format. Perfect for Plex, Jellyfin, Emby, and other media servers. No volume mounting required - just point your media server to the URL!

## Features

- 🎯 **Direct HTTP Access** - No file mounting needed, access EPG at `http://YOUR-IP:8083/epg.xml`
- 📺 **Dummy Programming** - Fill gaps for channels without EPG data
- 🔄 **Automatic Updates** - Cron-based scheduling (default: 3 AM daily)
- 🎨 **Multiple Formats** - Support for different XMLTV variations
- 🌐 **Web Interface** - Built-in status page and health monitoring
- 🐳 **Unraid Optimized** - Ready for Community Apps submission

## Quick Start for Unraid

1. Install from Unraid Community Apps (search "HDHomeRun EPG")
2. Configure your HDHomeRun IP address
3. Set your preferred port (default: 8083)
4. Apply and start the container
5. Point your media server to: `http://YOUR-UNRAID-IP:8083/epg.xml`

## Available Endpoints

### EPG Data
- `http://YOUR-IP:8083/epg.xml` - Standard XMLTV format
- `http://YOUR-IP:8083/xmltv.xml` - Alternative endpoint (same data)
- `http://YOUR-IP:8083/guide.xml` - Alternative endpoint (same data)

### URL Parameters

#### Dummy Programming
Add placeholder programming for channels without EPG data:
- `?dummy=30min` - 30-minute blocks
- `?dummy=1hr` - 1-hour blocks (default when dummy=true)
- `?dummy=2hr` - 2-hour blocks
- `?dummy=3hr` - 3-hour blocks
- `?dummy=6hr` - 6-hour blocks

#### Format Options
- `?format=raw` - Unmodified HDHomeRun output
- `?format=plex` - Optimized for Plex (removes XML declaration)
- `?format=minimal` - Minimal XML headers

#### Combining Parameters
Parameters can be combined:
- `?format=plex&dummy=30min`
- `?format=raw&dummy=2hr`

### Other Endpoints
- `/` - Web interface with status and links
- `/status` - JSON status information
- `/health` - Simple health check (returns "OK")
- `/lineup.json` - HDHomeRun-compatible channel lineup

## Media Server Configuration

### Plex
1. Settings → Live TV & DVR → Set up Plex DVR
2. Select your HDHomeRun tuner
3. For EPG, choose "XMLTV"
4. Enter: `http://YOUR-IP:8083/epg.xml`
   - Add `?dummy=1hr` if you have channels without guide data
5. **Important**: Use your actual IP address, NOT localhost

### Jellyfin
1. Dashboard → Live TV → TV Guide Data Providers
2. Add new XMLTV provider
3. URL: `http://YOUR-IP:8083/epg.xml`
4. Refresh interval: 24 hours

### Emby
1. Live TV → Guide Data → Add
2. Type: XMLTV
3. Path: `http://YOUR-IP:8083/epg.xml`
4. Save and refresh

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HDHOMERUN_HOST` | `hdhomerun.local` | Your HDHomeRun IP or hostname |
| `WEB_PORT` | `8083` | HTTP server port |
| `CRON_SCHEDULE` | `0 3 * * *` | Update schedule (cron format) |
| `TZ` | `America/New_York` | Your timezone |
| `DAYS` | `7` | Days of EPG to fetch (max 7) |
| `HOURS` | `3` | Minimum hours between updates |
| `DEBUG` | `on` | Enable debug logging |
| `RUN_ON_START` | `true` | Generate EPG on container start |

## Example URLs

### Basic EPG
```
http://192.168.1.100:8083/epg.xml
```

### With 30-minute dummy programming
```
http://192.168.1.100:8083/epg.xml?dummy=30min
```

### Plex-optimized with 1-hour dummy blocks
```
http://192.168.1.100:8083/epg.xml?format=plex&dummy=1hr
```

### Raw HDHomeRun format
```
http://192.168.1.100:8083/epg.xml?format=raw
```

## Docker Compose

```yaml
version: '3'
services:
  hdhomerun-epg:
    image: ghcr.io/metacolin/hdhr-epg2xml-for-unraid:latest
    container_name: hdhomerun-epg
    ports:
      - "8083:8083"
    environment:
      - HDHOMERUN_HOST=hdhomerun.local  # Change to your HDHomeRun IP
      - TZ=America/New_York
      - CRON_SCHEDULE=0 3 * * *
    restart: unless-stopped
```

## Troubleshooting

### No EPG Data
- Verify HDHomeRun IP is correct and accessible
- Check container logs: `docker logs hdhomerun-epg`
- Test HDHomeRun directly: `http://YOUR-HDHOMERUN-IP/lineup.json`

### Plex Shows "Error communicating with provider"
- **Never use localhost** - always use your server's actual IP address
- Ensure the port is accessible from Plex
- Try the URL in a browser first to verify it works

### Missing Channels
- Use the dummy programming parameter: `?dummy=1hr`
- Check if your HDHomeRun has a channel scan completed

### Time Zone Issues
- Set the TZ environment variable to match your local timezone
- Times in EPG should match your local schedule

## Credits

This project builds upon the excellent work of [IncubusVictim's HDHomeRunEPG-to-XmlTv](https://github.com/IncubusVictim/HDHomeRunEPG-to-XmlTv). The core EPG fetching functionality (HDHomeRunEPG_To_XmlTv.py) was created by IncubusVictim and is used under the GPL license.

Our contributions:
- Dockerization for Unraid deployment
- HTTP server for direct EPG access
- Dummy programming feature for channels without EPG data
- URL parameter support for format and duration options
- Unraid Community Apps integration

## Technical Details

- Python 3.11 slim Docker container
- Automatic EPG updates via cron
- No database required - simple file-based storage
- Lightweight HTTP server with minimal resource usage

## Support

For issues or questions, please check the [GitHub repository](https://github.com/metaColin/HDHR-EPG2XML-for-Unraid) or post in the Unraid Forums.

## License

This project includes GPL-licensed components. See individual files for specific licensing information.