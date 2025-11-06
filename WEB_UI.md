# 🌐 Web UI Guide

The Train Delay Notifier now includes a modern web interface for easier configuration and monitoring!

## Features

- 📊 **Real-time Dashboard** - See your train status at a glance
- ⚙️ **Easy Configuration** - Set up trains through a web form
- 🔔 **Monitoring Control** - Start/stop monitoring with one click
- 🔍 **Connection Testing** - Verify your configuration before starting
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile

## Quick Start

### 1. Install Web Dependencies

```bash
cd ~/Development/Trains
source venv/bin/activate
pip install flask flask-cors
```

Or reinstall all requirements:

```bash
pip install -r requirements.txt
```

### 2. Start the Web Server

```bash
python3 web_server.py
```

You'll see:

```
🚆 Train Delay Notifier - Web UI
==================================================

Starting web server...

📱 Open your browser and go to:
   http://localhost:5000

==================================================
```

### 3. Open Your Browser

Navigate to: **http://localhost:5000**

## Using the Web UI

### Configuration

1. **Get Train URL:**
   - Go to [cd.cz](https://www.cd.cz)
   - Search for your train
   - Click "All information about the train"
   - Copy the URL from your browser

2. **Fill in the Form:**
   - Paste the train URL
   - Enter destination station (e.g., "Praha")
   - Set notification time (minutes before arrival)
   - Set check interval (how often to check for updates)

3. **Test Connection:**
   - Click "Test Connection" to verify it works
   - The app will fetch train data and show you:
     - Train number and name
     - Current delay
     - Scheduled and expected arrival times
     - Available stations (if destination not found)

4. **Save Configuration:**
   - Click "Save Configuration" to store your settings

### Monitoring

1. **Start Monitoring:**
   - Click "Start Monitoring" button
   - Status indicator will turn green
   - Train info will appear on the dashboard

2. **Monitor Status:**
   - The dashboard automatically updates every 10 seconds
   - Shows:
     - Current delay
     - Scheduled vs. actual arrival time
     - Last check time
     - Monitoring status

3. **Stop Monitoring:**
   - Click "Stop Monitoring" when done
   - You can reconfigure and restart anytime

## Dashboard Explained

### Status Card

- **Green dot (pulsing)** - Monitoring is active
- **Gray dot** - Not monitoring
- **Train Info Section** - Shows:
  - Train number and name
  - Destination station
  - Scheduled arrival time
  - Current delay (with color coding)
  - Expected arrival time
  - Last status check

### Configuration Card

All your train settings in one place:
- Train URL
- Destination station
- Notification timing
- Check interval

### Help Card

Quick instructions for getting started.

## API Endpoints

The web UI exposes these REST API endpoints:

### GET `/api/config`
Get current configuration

### POST `/api/config`
Update configuration
```json
{
  "train_url": "https://www.cd.cz/vlak/...",
  "destination_station": "Praha",
  "notify_minutes_before": 60,
  "check_interval_minutes": 5
}
```

### GET `/api/status`
Get monitoring status
```json
{
  "active": true,
  "train_number": "140",
  "train_name": "EC Ostravan",
  "destination": "Praha hl.n.",
  "current_delay": 12,
  "scheduled_arrival": "19:36",
  "actual_arrival": "19:48",
  "last_check": "17:15:30"
}
```

### POST `/api/train/info`
Test train connection (fetch info without monitoring)
```json
{
  "train_url": "https://www.cd.cz/vlak/...",
  "destination_station": "Praha"
}
```

### POST `/api/monitor/start`
Start monitoring

### POST `/api/monitor/stop`
Stop monitoring

## Accessing from Other Devices

The web server runs on `0.0.0.0:5000`, so you can access it from other devices on your network:

1. Find your computer's local IP address:
   ```bash
   # On Mac
   ifconfig | grep "inet "

   # On Linux
   hostname -I
   ```

2. On another device, open:
   ```
   http://YOUR_IP_ADDRESS:5000
   ```

   For example: `http://192.168.1.100:5000`

## Troubleshooting

### Port Already in Use

If port 5000 is already in use, edit `web_server.py` and change:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use 5001 instead
```

### Can't Access from Other Devices

Check your firewall settings and allow port 5000.

### Notifications Not Working

The web UI uses the same notification system as the CLI app. Make sure:
- On macOS: `osascript` notifications are enabled
- Desktop notifications are enabled in system preferences
- The web server is running on the same machine where you want notifications

## Running in Background

To keep the web server running:

### On Mac/Linux:

```bash
# Using nohup
nohup python3 web_server.py &

# Or using screen
screen -S train-monitor
python3 web_server.py
# Press Ctrl+A, then D to detach
```

### Stopping Background Process:

```bash
# Find the process
ps aux | grep web_server

# Kill it
kill <PID>
```

## Security Note

This web UI is designed for **local/personal use** only. It does not include authentication. Do not expose it to the public internet without adding proper security measures.

## Comparison: Web UI vs CLI

| Feature | Web UI | CLI |
|---------|--------|-----|
| **Configuration** | Web form | JSON file |
| **Monitoring Control** | Start/Stop buttons | Run/Stop script |
| **Status Updates** | Real-time dashboard | Terminal logs |
| **Accessibility** | Any browser | Terminal only |
| **Multi-device** | Yes | No |
| **Setup** | Slightly more complex | Simpler |

Both interfaces work with the same backend and can be used interchangeably!

## Next Steps

- Configure your train in the web UI
- Test the connection
- Start monitoring
- Keep the browser tab open to see real-time updates
- Desktop notifications will work even if you close the tab (as long as the server runs)

Enjoy your modern train monitoring experience! 🚆✨
