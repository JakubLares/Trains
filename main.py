#!/usr/bin/env python3
"""
Train Delay Notifier - Main Application
Monitors Czech Railways trains and sends notifications before arrival
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from train_monitor import TrainMonitor
from train_fetcher import TrainFetcher
from notifier import Notifier

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = 'config.json') -> dict:
    """Load configuration from JSON file"""
    config_file = Path(config_path)

    if not config_file.exists():
        logger.error(f"Config file not found: {config_path}")
        logger.info("Please create a config.json file (see config.example.json)")
        sys.exit(1)

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        sys.exit(1)


def validate_config(config: dict) -> bool:
    """Validate configuration"""
    required_fields = ['train_url', 'destination_station']

    for field in required_fields:
        if field not in config:
            logger.error(f"Missing required field in config: {field}")
            return False

    return True


def test_connection(train_url: str, destination: str):
    """Test fetching train data"""
    print("=" * 60)
    print("Testing connection to České dráhy...")
    print("=" * 60)

    fetcher = TrainFetcher()

    print(f"\nFetching: {train_url}")
    train_data = fetcher.fetch_train_data(train_url)

    if not train_data:
        print("❌ Failed to fetch train data")
        print("\nPossible issues:")
        print("- Invalid URL")
        print("- Network connection problems")
        print("- CD.cz website structure changed")
        return False

    print(f"✅ Successfully fetched train data")
    print(f"\nTrain: {train_data.get('train_number')} {train_data.get('train_name')}")
    print(f"Stations found: {len(train_data.get('stations', []))}")

    # Try to find destination
    arrival_info = fetcher.get_arrival_time_at_station(train_data, destination)

    if not arrival_info:
        print(f"\n⚠️  Could not find station '{destination}' in train data")
        print("\nAvailable stations:")
        for station in train_data.get('stations', [])[:15]:
            print(f"  - {station['name']}")
        return False

    print(f"\n✅ Found destination: {arrival_info['station']}")
    print(f"Scheduled arrival: {arrival_info['scheduled_arrival'].strftime('%H:%M')}")
    print(f"Delay: {arrival_info['delay_minutes']:+d} minutes")
    print(f"Expected arrival: {arrival_info['actual_arrival'].strftime('%H:%M')}")

    print("\n" + "=" * 60)
    print("✅ Connection test successful!")
    print("=" * 60)

    return True


def test_notifications():
    """Test notification system"""
    print("=" * 60)
    print("Testing notification system...")
    print("=" * 60)

    notifier = Notifier()

    print("\nSending test notification...")
    success = notifier.send_notification(
        "Train Delay Notifier - Test",
        "If you see this, notifications are working! 🎉"
    )

    if success:
        print("✅ Test notification sent successfully")
        print("Check your system notifications/notification center")
    else:
        print("⚠️  Notification may not have been displayed")
        print("Notifications will still be logged to the console")

    print("=" * 60)


def start_monitoring(config: dict):
    """Start monitoring a train"""
    monitor = TrainMonitor(
        train_url=config['train_url'],
        destination_station=config['destination_station'],
        notify_minutes_before=config.get('notify_minutes_before', 60),
        check_interval_minutes=config.get('check_interval_minutes', 5)
    )

    monitor.start_monitoring()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Train Delay Notifier - Monitor Czech Railways trains and get notified before arrival',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                   # Start monitoring with config.json
  %(prog)s --config my-train.json            # Use custom config file
  %(prog)s --test                            # Test connection and fetching
  %(prog)s --test-notifications              # Test notification system
  %(prog)s --url "https://..." --dest Praha --notify 75

For more information, see README.md
        """
    )

    parser.add_argument(
        '--config',
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )

    parser.add_argument(
        '--test',
        action='store_true',
        help='Test connection and data fetching'
    )

    parser.add_argument(
        '--test-notifications',
        action='store_true',
        help='Test notification system'
    )

    parser.add_argument(
        '--url',
        help='Train URL from CD.cz (overrides config)'
    )

    parser.add_argument(
        '--dest',
        help='Destination station name (overrides config)'
    )

    parser.add_argument(
        '--notify',
        type=int,
        help='Minutes before arrival to notify (overrides config)'
    )

    parser.add_argument(
        '--interval',
        type=int,
        help='Check interval in minutes (overrides config)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Test notifications
    if args.test_notifications:
        test_notifications()
        return

    # Load config
    config = load_config(args.config)

    if not validate_config(config):
        sys.exit(1)

    # Override with command line arguments
    if args.url:
        config['train_url'] = args.url
    if args.dest:
        config['destination_station'] = args.dest
    if args.notify:
        config['notify_minutes_before'] = args.notify
    if args.interval:
        config['check_interval_minutes'] = args.interval

    # Test mode
    if args.test:
        test_connection(config['train_url'], config['destination_station'])
        return

    # Start monitoring
    print("\n🚆 Train Delay Notifier\n")
    start_monitoring(config)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nStopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
