#!/bin/bash

# Set timezone
if [ ! -z "$TZ" ]; then
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime
    echo $TZ > /etc/timezone
fi

# Build the command with environment variables (use full python path)
EPG_CMD="/usr/local/bin/python3 /app/HDHomeRunEPG_To_XmlTv.py"

if [ ! -z "$HDHOMERUN_HOST" ]; then
    EPG_CMD="$EPG_CMD --host $HDHOMERUN_HOST"
fi

if [ ! -z "$OUTPUT_FILENAME" ]; then
    EPG_CMD="$EPG_CMD --filename $OUTPUT_FILENAME"
fi

if [ ! -z "$DAYS" ]; then
    EPG_CMD="$EPG_CMD --days $DAYS"
fi

if [ ! -z "$HOURS" ]; then
    EPG_CMD="$EPG_CMD --hours $HOURS"
fi

if [ ! -z "$DEBUG" ]; then
    EPG_CMD="$EPG_CMD --debug $DEBUG"
fi

# Create the cron job with PATH environment
echo "Setting up cron schedule: $CRON_SCHEDULE"

# Build the cron command
FULL_CMD="$EPG_CMD"

(
    echo "PATH=/usr/local/bin:/usr/bin:/bin"
    echo "HDHOMERUN_HOST=$HDHOMERUN_HOST"
    echo "OUTPUT_FILENAME=$OUTPUT_FILENAME"
    echo "DAYS=$DAYS"
    echo "$CRON_SCHEDULE $FULL_CMD >> /var/log/cron.log 2>&1"
) | crontab -

# Create run-once script for initial execution
cat > /app/run-once.sh << EOF
#!/bin/bash
echo "Running initial EPG update..."
$EPG_CMD
echo "Initial EPG update completed."
EOF
chmod +x /app/run-once.sh

# Create log file
touch /var/log/cron.log

# Display configuration
echo "==========================================="
echo "HDHomeRun EPG to XML Converter"
echo "==========================================="
echo "Host: $HDHOMERUN_HOST"
echo "Output: $OUTPUT_FILENAME"
echo "Days: $DAYS"
echo "Schedule: $CRON_SCHEDULE"
echo "Timezone: $TZ"
echo "Run on start: $RUN_ON_START"
echo "==========================================="

# Start supervisor
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf