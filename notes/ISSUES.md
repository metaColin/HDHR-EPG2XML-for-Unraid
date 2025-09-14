# ISSUES.md

## Solved Issues

### 1. Missing Core Python Script
**Problem**: Initial containerization attempt missing HDHomeRunEPG_To_XmlTv.py
**Solution**: Downloaded GPL-licensed script from GitHub repository
**Status**: ✅ Resolved

### 2. Plex "Error communicating with provider"
**Problem**: Plex couldn't connect to EPG endpoint using localhost
**Solution**: Use actual server IP instead of localhost/127.0.0.1
**CRITICAL**: NEVER use localhost in URLs for Plex - it cannot reach the container's localhost from its context
**Testing URLs**:
- ❌ WRONG: `http://localhost:8083/epg.xml`
- ✅ CORRECT: `http://192.168.134.164:8083/epg.xml`
**Status**: ✅ Resolved

### 3. Plex "Invalid or missing file"
**Problem**: Plex rejected EPG XML format
**Root Cause**: Missing XML declaration and wrong content-type
**Solution**:
- Added `<?xml version="1.0" encoding="UTF-8"?>` declaration
- Changed content-type to `application/xml; charset=UTF-8`
- Added proper Cache-Control headers
**Status**: ✅ Resolved

### 4. Cron Job Python Path
**Problem**: Cron couldn't find python3 command
**Solution**: Use full path `/usr/local/bin/python3` in cron commands
**Status**: ✅ Resolved

### 5. Volume Mounting Complexity
**Problem**: Users need to mount volumes between containers for EPG sharing
**Solution**: Built HTTP server to serve EPG via URL endpoints
**Status**: ✅ Resolved

### 6. Channels Without EPG Data
**Problem**: Some channels have no program information
**Solution**: Added URL parameter support for dummy programming (?dummy=1hr)
**Status**: ✅ Resolved

## Known Limitations

### 1. HDHomeRun API Rate Limits
**Issue**: Frequent API calls might hit rate limits
**Mitigation**: Default 3-hour minimum between updates
**Impact**: Low - normal usage won't hit limits

### 2. Large EPG Files
**Issue**: 7 days of EPG for many channels can be 10+ MB
**Mitigation**: Compression headers, caching, configurable day count
**Impact**: Low - modern networks handle this fine

### 3. Time Zone Handling
**Issue**: Container time must match local time for accurate scheduling
**Mitigation**: TZ environment variable configuration
**Impact**: Medium - requires user configuration

## Technical Debt

### 1. No Persistent Cache
**Description**: EPG regenerates fully each update
**Proposed Fix**: Implement differential updates
**Priority**: Low - current approach works well

### 2. Single-threaded Server
**Description**: HTTP server handles one request at a time
**Proposed Fix**: Use asyncio or threading
**Priority**: Low - EPG requests are infrequent

### 3. No Metrics/Monitoring
**Description**: No built-in performance metrics
**Proposed Fix**: Add Prometheus endpoint
**Priority**: Low - can use container metrics

## Future Improvements

### 1. M3U Playlist Generation
**Benefit**: Direct IPTV app support
**Complexity**: Medium
**Priority**: Post-release

### 2. Admin Web Interface
**Benefit**: Configure without restart
**Complexity**: High
**Priority**: Consider based on user feedback

### 3. Multi-HDHomeRun Support
**Benefit**: Aggregate multiple devices
**Complexity**: Medium
**Priority**: Based on user demand

## Debugging Tips

### Check EPG Generation
```bash
docker exec HDHomeRun-EPG python3 /app/HDHomeRunEPG_To_XmlTv.py \
  --host [IP] --debug on
```

### Verify Cron Schedule
```bash
docker exec HDHomeRun-EPG crontab -l
```

### Test Dummy Programming
```bash
curl "http://localhost:8080/epg.xml?dummy=30min" | head -100
```

### Monitor Memory Usage
```bash
docker stats HDHomeRun-EPG
```

## Support Process
1. Check /status endpoint for diagnostics
2. Review docker logs for errors
3. Verify HDHomeRun accessibility
4. Test with curl before media server
5. Report issues with logs and status output