# DEPLOY.md

## Unraid Deployment Guide

### Installation via Community Apps
1. Open Unraid web interface
2. Navigate to Apps tab
3. Search for "HDHomeRun EPG"
4. Click Install
5. Configure settings:
   - **HDHomeRun IP**: Enter your device IP (e.g., 192.168.1.100)
   - **Web Port**: Default 8083 (change if needed)
   - **Timezone**: Select your timezone
   - **Update Schedule**: Default 3 AM daily
6. Click Apply

### Manual Docker Deployment
```bash
# SSH into Unraid
ssh root@unraid-ip

# Create container
docker run -d \
  --name='HDHomeRun-EPG' \
  --net='bridge' \
  -e 'HDHOMERUN_HOST'='192.168.1.100' \
  -e 'TZ'='America/New_York' \
  -e 'CRON_SCHEDULE'='0 3 * * *' \
  -p '8083:8083/tcp' \
  ghcr.io/your-username/hdhomerun-epg:latest
```

### Configuration in Media Servers

#### Plex
1. Settings → Live TV & DVR
2. Set up HDHomeRun (if not already done)
3. Electronic Program Guide → XMLTV
4. Enter: `http://[UNRAID-IP]:8083/epg.xml`
5. Optional: Add `?dummy=1hr` for channels without data

#### Jellyfin
1. Dashboard → Live TV
2. TV Guide Data Providers → Add
3. Type: XMLTV
4. File/URL: `http://[UNRAID-IP]:8083/epg.xml`
5. Refresh interval: 24 hours

#### Emby
1. Live TV → Guide Data
2. Add Guide Provider → XMLTV
3. Path: `http://[UNRAID-IP]:8083/epg.xml`
4. Save and refresh

### URL Parameters
Customize EPG output with URL parameters:
- `?dummy=30min` - Add 30-minute dummy blocks
- `?dummy=1hr` - Add 1-hour dummy blocks
- `?dummy=2hr` - Add 2-hour dummy blocks
- `?format=raw` - Raw HDHomeRun format
- `?format=plex` - Optimized for Plex
- `?format=minimal` - Minimal XML headers

Combine parameters: `?format=plex&dummy=1hr`

### Monitoring

#### Check Status
```bash
# Container logs
docker logs HDHomeRun-EPG

# Server status
curl http://[UNRAID-IP]:8083/status

# Health check
curl http://[UNRAID-IP]:8083/health
```

#### Verify EPG Updates
1. Check last modified time: `http://[UNRAID-IP]:8083/status`
2. View logs for cron execution
3. Monitor file size changes

### Backup & Recovery

#### Backup EPG Data
```bash
# Backup current EPG
docker exec HDHomeRun-EPG cat /output/epg.xml > epg_backup.xml
```

#### Restore After Failure
1. Reinstall from Community Apps
2. Use same configuration
3. EPG will regenerate automatically

### Performance Tuning

#### Resource Limits (Optional)
Add to Docker run command:
```bash
--memory="256m" \
--cpu-shares="1024" \
```

#### Adjust Update Frequency
- More frequent: `CRON_SCHEDULE="0 */6 * * *"` (every 6 hours)
- Less frequent: `CRON_SCHEDULE="0 3 */2 * *"` (every 2 days)

### Troubleshooting Deployment

**Container won't start**
- Check port 8083 availability
- Verify HDHomeRun IP is correct
- Review docker logs

**EPG not updating**
- Check cron schedule format
- Verify timezone setting
- Ensure HDHomeRun is accessible

**Media server can't connect**
- Use Unraid IP, not container name
- Ensure port is mapped correctly
- Check firewall rules

### Security Considerations
- Container runs unprivileged
- No sensitive data stored
- Read-only access to HDHomeRun
- No external dependencies

### Support
- GitHub Issues: [Repository Issues]
- Unraid Forums: HDHomeRun EPG thread
- Check `/status` endpoint for diagnostics