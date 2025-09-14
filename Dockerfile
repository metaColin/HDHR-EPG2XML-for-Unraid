FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install required system packages
RUN apt-get update && apt-get install -y \
    cron \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install required Python packages
RUN pip install --no-cache-dir requests argparse

# Copy application files
COPY HDHomeRunEPG_To_XmlTv.py /app/
COPY epg_server.py /app/

# Create output directory and log directory
RUN mkdir -p /output /var/log/supervisor

# Set environment variables with defaults
ENV HDHOMERUN_HOST=hdhomerun.local
ENV OUTPUT_FILENAME=/output/epg.xml
ENV DAYS=7
ENV HOURS=3
ENV DEBUG=on
ENV CRON_SCHEDULE="0 3 * * *"
ENV TZ=America/New_York
ENV RUN_ON_START=true
ENV WEB_PORT=8080

# Copy configuration files
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY cron-entrypoint.sh /app/
RUN chmod +x /app/cron-entrypoint.sh

# Expose web server port
EXPOSE 8080

ENTRYPOINT ["/app/cron-entrypoint.sh"]