# 🚆 Train Delay Notifier

A Python application that monitors Czech Railways (České dráhy) trains and sends desktop notifications before arrival, including real-time delay information.

> ✅ **Status: Fully Functional!** The app successfully fetches train data using Selenium, extracts delays from JavaScript, and sends notifications!

## Features

- 📍 Monitor any train connection from České dráhy (CD.cz)
- ⏰ Get notified X minutes before arrival at your destination
- 🔄 Automatically checks for delay updates
- 📢 Desktop notifications with actual arrival times including delays
- ⚠️ Additional notifications when delays change significantly (5+ minutes)
- 🔧 Configurable check intervals and notification timing

## Example Use Case

Monitor train **EC 140 Ostravan** from Ostrava to Praha:
- Get notified 75 minutes before arrival
- Scheduled arrival: 19:36
- With 10 minute delay, actual arrival: 19:46
- You'll be notified at 18:29 (75 minutes before 19:46)

## Requirements

- Python 3.7+
- Internet connection
- Linux, macOS, or Windows

## Installation

### 1. Clone or download this repository

```bash
git clone <repository-url>
cd Trains
```

### 2. Create a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Configuration

### 1. Create your configuration file

Copy the example configuration:

```bash
cp config.example.json config.json
```

### 2. Edit config.json

```json
{
  "train_url": "https://www.cd.cz/vlak/140/6.11.2025/5617915/14.34/5457076/19.36/",
  "destination_station": "Praha",
  "notify_minutes_before": 75,
  "check_interval_minutes": 5
}
```

**Configuration options:**

- `train_url` - Full URL from CD.cz for your train (see "How to get train URL" below)
- `destination_station` - Name of your destination station (partial match works, e.g., "Praha" matches "Praha hl.n.")
- `notify_minutes_before` - Send notification X minutes before arrival (default: 60)
- `check_interval_minutes` - How often to check for updates (default: 5)

### How to get train URL

1. Go to [cd.cz](https://www.cd.cz/en/)
2. Search for your connection
3. Click on your train
4. Click "All information about the train"
5. Copy the URL from your browser
   - Format: `https://www.cd.cz/vlak/{TRAIN_NUMBER}/{DATE}/...`

Example URL structure:
```
https://www.cd.cz/vlak/140/6.11.2025/5617915/14.34/5457076/19.36/
                     ^    ^          ^        ^      ^       ^
                     |    |          |        |      |       |
                   train  date    origin   origin  dest    dest
                   number        station   time   station  time
```

## Usage

### Basic Usage

Start monitoring with your configuration:

```bash
python main.py
```

### Test Connection

Test if the app can fetch train data:

```bash
python main.py --test
```

This will:
- Fetch the train data from CD.cz
- Display train information
- Show the destination station and arrival time
- Verify the configuration is correct

### Test Notifications

Test if desktop notifications work on your system:

```bash
python main.py --test-notifications
```

### Command Line Options

Override configuration with command line arguments:

```bash
# Use custom config file
python main.py --config my-train.json

# Override URL and destination
python main.py --url "https://www.cd.cz/vlak/..." --dest "Brno"

# Change notification timing
python main.py --notify 60  # Notify 60 minutes before arrival

# Change check interval
python main.py --interval 3  # Check every 3 minutes

# Enable verbose logging
python main.py --verbose
```

## How It Works

1. **Fetching Data**: The app periodically fetches train data from CD.cz using web scraping
2. **Parsing Delays**: It extracts schedule information and current delays from the website
3. **Calculating Arrival**: It calculates the actual arrival time (scheduled time + delay)
4. **Monitoring**: It checks if current time is within the notification window
5. **Notifying**: When it's time (X minutes before actual arrival), it sends a desktop notification

## Monitoring Behavior

- ✅ Checks train status every N minutes (configurable)
- ✅ Sends main notification X minutes before actual arrival (including delays)
- ✅ Sends additional notifications if delay changes by 5+ minutes
- ✅ Continues monitoring even after main notification (in case delays change)
- ✅ Stops automatically after the train has arrived

## Notifications

The app sends desktop notifications for:

1. **Monitoring Started** - Confirms the app is running
2. **Train Arriving Soon** - Main notification X minutes before arrival
3. **Delay Updated** - When delay increases/decreases significantly
4. **Errors** - If something goes wrong

### Notification Example

```
🚆 Train 140 arriving soon!

EC Ostravan
Arriving at Praha hl.n. in 75 minutes
Scheduled: 19:36
Expected: 19:46 (delay: +10 min)
```

## Troubleshooting

### No notifications appearing

1. Check if notifications work: `python main.py --test-notifications`
2. On Linux, ensure notification daemon is running
3. On Windows, check notification settings
4. On macOS, grant Python terminal notification permissions

### "Failed to fetch train data"

1. Check internet connection
2. Verify train URL is correct: `python main.py --test`
3. CD.cz website might have changed structure
4. Try using a different train URL

### "Could not find station"

1. Run `python main.py --test` to see available stations
2. Use shorter station name (e.g., "Praha" instead of "Praha hlavní nádraží")
3. Check spelling and try variations

### No delay information

- The CD.cz website might not show delays for future trains
- Delays typically appear closer to departure time
- The app will still work and show scheduled times

## Advanced Usage

### Multiple Trains

Create separate config files for each train:

```bash
# Morning commute
python main.py --config morning-train.json

# Evening commute
python main.py --config evening-train.json
```

### Running as Background Service

On Linux with systemd:

```bash
# Create service file: /etc/systemd/system/train-notifier.service
[Unit]
Description=Train Delay Notifier
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/Trains
ExecStart=/path/to/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable train-notifier
sudo systemctl start train-notifier
```

## Development

### Project Structure

```
Trains/
├── main.py              # Main application entry point
├── train_fetcher.py     # Fetches and parses train data from CD.cz
├── train_monitor.py     # Monitoring logic and scheduling
├── notifier.py          # Desktop notification system
├── config.json          # Your configuration (not in git)
├── config.example.json  # Example configuration
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Testing Individual Components

Test the fetcher:
```bash
python train_fetcher.py
```

Test the notifier:
```bash
python notifier.py
```

Test the monitor:
```bash
python train_monitor.py
```

## Limitations

- ⚠️ **No official API**: This app uses web scraping, so it may break if CD.cz changes their website
- ⚠️ **Czech Railways only**: Only works with České dráhy (CD.cz) trains
- ⚠️ **Desktop only**: Notifications are desktop-only (no mobile push notifications)
- ⚠️ **Network required**: Requires active internet connection

## Future Improvements

Potential enhancements:
- [ ] Support for multiple trains/destinations
- [ ] Email/SMS notifications
- [ ] Mobile app companion
- [ ] Historical delay statistics
- [ ] Web dashboard
- [ ] Support for other rail operators (RegioJet, Leo Express, etc.)
- [ ] Use official API if/when available

## Contributing

Contributions are welcome! Areas for improvement:
- More robust HTML parsing
- Better error handling
- Additional notification methods
- Support for more train operators
- Automated tests

## License

MIT License - feel free to use and modify

## Disclaimer

This is an unofficial tool and is not affiliated with České dráhy. Use at your own risk. The accuracy of delay information depends on the data provided by CD.cz.

## Support

For issues, questions, or suggestions:
1. Check the troubleshooting section
2. Run tests: `python main.py --test`
3. Enable verbose logging: `python main.py --verbose`
4. Open an issue on GitHub

---

**Happy travels! 🚆**
