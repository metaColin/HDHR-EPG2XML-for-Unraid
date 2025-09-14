#!/usr/bin/env python3
"""
EPG HTTP Server
Serves EPG XML files via HTTP endpoint
"""

import os
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import mimetypes
import json
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EPGHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        """Handle HEAD requests (required by Plex)"""
        self.handle_request(head_only=True)

    def do_GET(self):
        """Handle GET requests"""
        self.handle_request(head_only=False)

    def handle_request(self, head_only=False):
        """Handle both GET and HEAD requests"""
        # Parse path and query parameters
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == '/':
            if not head_only:
                self.send_index()
        elif path == '/epg.xml' or path == '/xmltv.xml' or path == '/guide.xml':
            # Support multiple common EPG endpoints
            self.send_epg_file(query, head_only)
        elif path == '/lineup.json':
            # Some apps expect HDHomeRun-style lineup
            if not head_only:
                self.send_lineup()
        elif path == '/status':
            if not head_only:
                self.send_status()
        elif path == '/health':
            if not head_only:
                self.send_health()
        else:
            self.send_error(404, "File not found")

    def send_index(self):
        """Send index page with available endpoints"""
        html = """<!DOCTYPE html>
<html>
<head>
    <title>HDHomeRun EPG Server</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }
        .endpoint { background: #f9f9f9; padding: 15px; margin: 15px 0; border-left: 4px solid #4CAF50; border-radius: 5px; }
        .endpoint h3 { margin-top: 0; color: #4CAF50; }
        .endpoint a { color: #2196F3; text-decoration: none; font-family: monospace; font-size: 14px; }
        .endpoint a:hover { text-decoration: underline; }
        .status { margin-top: 20px; padding: 15px; background: #e8f5e9; border-radius: 5px; }
        .description { color: #666; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎥 HDHomeRun EPG Server</h1>
        <p>Electronic Program Guide (EPG) data server for HDHomeRun devices</p>

        <div class="endpoint">
            <h3>EPG Data - Multiple Formats</h3>
            <a href="/epg.xml">/epg.xml</a> - Standard format (Plex, Jellyfin, Emby)<br>
            <a href="/epg.xml?dummy=1hr">/epg.xml?dummy=1hr</a> - With 1-hour dummy programming blocks<br>
            <a href="/epg.xml?dummy=30min">/epg.xml?dummy=30min</a> - With 30-minute dummy programming blocks<br>
            <a href="/xmltv.xml">/xmltv.xml</a> - Alternative endpoint<br>
            <a href="/guide.xml">/guide.xml</a> - Alternative endpoint<br>
            <p class="description">
                XMLTV formatted EPG data.<br>
                <strong>Parameters:</strong><br>
                • <code>format</code>: raw, plex, minimal<br>
                • <code>dummy</code>: true, 30min, 1hr, 2hr, 3hr, 6hr<br>
                • Combine: <code>?format=raw&dummy=2hr</code>
            </p>
        </div>

        <div class="endpoint">
            <h3>Channel Lineup</h3>
            <a href="/lineup.json">/lineup.json</a>
            <p class="description">HDHomeRun-compatible JSON channel lineup (for Channels, xTeVe)</p>
        </div>

        <div class="endpoint">
            <h3>Server Status</h3>
            <a href="/status">/status</a>
            <p class="description">Current server status and last update time</p>
        </div>

        <div class="endpoint">
            <h3>Health Check</h3>
            <a href="/health">/health</a>
            <p class="description">Simple health check endpoint for monitoring</p>
        </div>

        <div class="status">
            <strong>Configuration:</strong><br>
            • HDHomeRun Host: {host}<br>
            • Update Schedule: {schedule}<br>
            • Port: {port}
        </div>
    </div>
</body>
</html>""".format(
            host=os.environ.get('HDHOMERUN_HOST', 'not configured'),
            schedule=os.environ.get('CRON_SCHEDULE', '0 3 * * *'),
            port=os.environ.get('WEB_PORT', '8083')
        )

        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', str(len(html)))
        self.end_headers()
        self.wfile.write(html.encode())

    def send_epg_file(self, query_params=None, head_only=False):
        """Send the EPG XML file with format options"""
        epg_path = Path(os.environ.get('OUTPUT_FILENAME', '/output/epg.xml'))

        if not epg_path.exists():
            error_msg = "EPG file not found. The system may still be generating the initial EPG data. Please check back in a few moments."
            self.send_error(404, error_msg)
            return

        try:
            with open(epg_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for dummy parameter to add dummy programming on-the-fly
            if query_params and 'dummy' in query_params:
                dummy_value = query_params['dummy'][0].lower()
                if dummy_value:
                    content = self.add_dummy_programming_to_xml(content, dummy_value)

            # Check for format parameter
            format_type = 'standard'
            if query_params and 'format' in query_params:
                format_type = query_params['format'][0]

            # Apply format-specific modifications
            if format_type == 'raw':
                # Send exactly as generated by HDHomeRun script
                pass
            elif format_type == 'plex':
                # Plex prefers NO XML declaration or DOCTYPE
                # Remove any existing XML declaration
                if content.startswith('<?xml'):
                    content = content.split('\n', 1)[1] if '\n' in content else content
                # Remove DOCTYPE if present
                if content.startswith('<!DOCTYPE'):
                    content = content.split('\n', 1)[1] if '\n' in content else content
            elif format_type == 'minimal':
                # Some apps prefer minimal XML declaration
                if not content.startswith('<?xml'):
                    content = '<?xml version="1.0"?>\n' + content
            else:
                # For Plex - add minimal XML declaration if missing
                # "Invalid or missing file" suggests it needs the declaration
                if not content.startswith('<?xml'):
                    content = '<?xml version="1.0" encoding="UTF-8"?>\n' + content

            content_bytes = content.encode('utf-8')

            self.send_response(200)
            # Use application/xml now that Plex can connect
            self.send_header('Content-Type', 'application/xml; charset=UTF-8')
            self.send_header('Content-Length', str(len(content_bytes)))
            self.send_header('Cache-Control', 'public, max-age=1800')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            if not head_only:
                self.wfile.write(content_bytes)

            logger.info(f"Served EPG file to {self.client_address[0]}")
        except Exception as e:
            logger.error(f"Error serving EPG file: {e}")
            self.send_error(500, "Internal server error")

    def send_status(self):
        """Send server status as JSON"""
        epg_path = Path(os.environ.get('OUTPUT_FILENAME', '/output/epg.xml'))

        status = {
            'server': 'running',
            'epg_file_exists': epg_path.exists(),
            'epg_file_size': epg_path.stat().st_size if epg_path.exists() else 0,
            'epg_last_modified': datetime.fromtimestamp(epg_path.stat().st_mtime).isoformat() if epg_path.exists() else None,
            'hdhomerun_host': os.environ.get('HDHOMERUN_HOST', 'not configured'),
            'update_schedule': os.environ.get('CRON_SCHEDULE', '0 3 * * *'),
            'server_time': datetime.now().isoformat()
        }

        json_response = json.dumps(status, indent=2)

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(json_response)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json_response.encode())

    def send_lineup(self):
        """Send channel lineup in HDHomeRun JSON format for compatibility"""
        epg_path = Path(os.environ.get('OUTPUT_FILENAME', '/output/epg.xml'))

        if not epg_path.exists():
            self.send_error(404, "EPG data not available yet")
            return

        try:
            # Parse EPG to extract channel list
            import xml.etree.ElementTree as ET
            tree = ET.parse(epg_path)
            root = tree.getroot()

            channels = []
            for channel in root.findall('channel'):
                channel_id = channel.get('id', '')
                display_name = channel.find('display-name')
                if display_name is not None:
                    channels.append({
                        'GuideNumber': channel_id,
                        'GuideName': display_name.text,
                        'URL': f'http://{os.environ.get("HDHOMERUN_HOST", "hdhomerun.local")}:5004/auto/v{channel_id}'
                    })

            json_response = json.dumps(channels, indent=2)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(json_response)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json_response.encode())

        except Exception as e:
            logger.error(f"Error generating lineup: {e}")
            self.send_error(500, "Error generating lineup")

    def send_health(self):
        """Simple health check endpoint"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')

    def add_dummy_programming_to_xml(self, xml_content, dummy_duration='1hr'):
        """Add dummy programming to channels without EPG data

        Args:
            xml_content: The EPG XML content
            dummy_duration: Duration of dummy blocks (true/1hr/30min/2hr/3hr/6hr etc)
        """
        import xml.etree.ElementTree as ET
        import requests
        from datetime import datetime, timedelta
        import time
        import re

        try:
            # Parse duration parameter
            duration_hours = 1.0  # Default to 1 hour

            if dummy_duration in ['true', '1', 'yes']:
                duration_hours = 1.0
            else:
                # Parse duration strings like "30min", "1hr", "2hr", "90min"
                match = re.match(r'(\d+(?:\.\d+)?)(hr|hour|hours|min|mins|minutes?)?', dummy_duration)
                if match:
                    value = float(match.group(1))
                    unit = match.group(2) or 'hr'

                    if unit.startswith('min'):
                        duration_hours = value / 60.0
                    else:  # hours
                        duration_hours = value

                    # Limit to reasonable values (5 minutes to 12 hours)
                    duration_hours = max(5/60, min(12, duration_hours))
            # Parse the XML
            root = ET.fromstring(xml_content)

            # Fetch HDHomeRun lineup
            hdhomerun_host = os.environ.get('HDHOMERUN_HOST', 'hdhomerun.local')
            lineup_url = f"http://{hdhomerun_host}/lineup.json"
            lineup_response = requests.get(lineup_url, timeout=5)
            lineup = lineup_response.json() if lineup_response.status_code == 200 else []

            # Get channels with programming
            channels_with_programs = set()
            for programme in root.findall('programme'):
                channel_id = programme.get('channel')
                if channel_id:
                    channels_with_programs.add(channel_id)

            # Get all defined channels
            existing_channels = {ch.get('id') for ch in root.findall('channel')}

            # Get timezone offset
            tz_offset = time.strftime('%z')
            if not tz_offset:
                tz_offset = '+0000'

            # Start date for dummy programming
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

            channels_added = 0

            # Add missing channels from HDHomeRun lineup
            for channel in lineup:
                guide_number = channel.get('GuideNumber', '')
                guide_name = channel.get('GuideName', '')

                if guide_number and guide_number not in existing_channels:
                    # Add channel definition
                    channel_elem = ET.Element('channel')
                    channel_elem.set('id', guide_number)

                    display_name = ET.SubElement(channel_elem, 'display-name')
                    display_name.set('lang', 'en')
                    display_name.text = guide_name

                    # Find position to insert (before first programme)
                    programmes = root.findall('programme')
                    if programmes:
                        root.insert(list(root).index(programmes[0]), channel_elem)
                    else:
                        root.append(channel_elem)

                    existing_channels.add(guide_number)
                    channels_added += 1

            # Add dummy programming for channels without any
            dummy_added = 0
            for channel_id in existing_channels:
                if channel_id not in channels_with_programs:
                    # Add 7 days of dummy programming with specified duration
                    current_time = start_date
                    end_time = start_date + timedelta(days=7)

                    while current_time < end_time:
                        programme = ET.Element('programme')
                        programme.set('channel', channel_id)
                        programme.set('start', current_time.strftime('%Y%m%d%H%M%S ') + tz_offset)

                        next_time = current_time + timedelta(hours=duration_hours)
                        programme.set('stop', next_time.strftime('%Y%m%d%H%M%S ') + tz_offset)

                        title = ET.SubElement(programme, 'title')
                        title.set('lang', 'en')
                        title.text = os.environ.get('DUMMY_PROGRAM_TITLE', 'No Information')

                        desc = ET.SubElement(programme, 'desc')
                        desc.set('lang', 'en')
                        channel_name = next((ch.get('GuideName', channel_id) for ch in lineup
                                           if ch.get('GuideNumber') == channel_id), channel_id)
                        desc.text = os.environ.get('DUMMY_PROGRAM_DESC',
                                                  f'No program information is currently available for {channel_name}.')

                        root.append(programme)
                        current_time = next_time

                    dummy_added += 1

            if channels_added > 0 or dummy_added > 0:
                duration_str = f"{duration_hours:.1f} hour" if duration_hours >= 1 else f"{int(duration_hours * 60)} minute"
                logger.info(f"Added {channels_added} channel definitions and {duration_str} dummy programming for {dummy_added} channels")

            # Convert back to string
            return ET.tostring(root, encoding='unicode')

        except Exception as e:
            logger.error(f"Error adding dummy programming: {e}")
            # Return original content if processing fails
            return xml_content

    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.client_address[0]} - {format % args}")

def run_server(port=None):
    """Run the HTTP server"""
    if port is None:
        port = int(os.environ.get('WEB_PORT', '8083'))
    server_address = ('', port)
    httpd = HTTPServer(server_address, EPGHandler)
    logger.info(f"EPG HTTP Server starting on port {port}")
    logger.info(f"Access EPG at: http://<your-server>:{port}/epg.xml")
    httpd.serve_forever()

if __name__ == '__main__':
    port = int(os.environ.get('WEB_PORT', '8083'))
    run_server(port)