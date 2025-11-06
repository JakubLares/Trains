"""
Train Monitor
Monitors train delays and sends notifications at the appropriate time
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Optional
import schedule

from train_fetcher import TrainFetcher
from notifier import Notifier

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TrainMonitor:
    """Monitors a train and sends notifications before arrival"""

    def __init__(
        self,
        train_url: str,
        destination_station: str,
        notify_minutes_before: int = 60,
        check_interval_minutes: int = 5
    ):
        """
        Initialize train monitor

        Args:
            train_url: CD.cz URL for the train
            destination_station: Name of destination station to monitor
            notify_minutes_before: Send notification X minutes before arrival
            check_interval_minutes: How often to check for updates
        """
        self.train_url = train_url
        self.destination_station = destination_station
        self.notify_minutes_before = notify_minutes_before
        self.check_interval_minutes = check_interval_minutes

        self.fetcher = TrainFetcher()
        self.notifier = Notifier()

        # State tracking
        self.last_known_delay = None
        self.notification_sent = False
        self.last_actual_arrival = None
        self.train_data = None
        self.monitoring_active = True

    def check_train(self) -> Optional[Dict]:
        """
        Check current train status

        Returns:
            Dictionary with current train status or None if failed
        """
        try:
            # Fetch train data
            train_data = self.fetcher.fetch_train_data(self.train_url)

            if not train_data:
                logger.error("Failed to fetch train data")
                return None

            self.train_data = train_data

            # Get arrival information for destination
            arrival_info = self.fetcher.get_arrival_time_at_station(
                train_data,
                self.destination_station
            )

            if not arrival_info:
                logger.error(f"Could not find arrival info for {self.destination_station}")
                return None

            return arrival_info

        except Exception as e:
            logger.error(f"Error checking train: {e}")
            return None

    def should_notify(self, arrival_info: Dict) -> bool:
        """
        Determine if it's time to send a notification

        Args:
            arrival_info: Arrival information dictionary

        Returns:
            True if notification should be sent
        """
        if self.notification_sent:
            return False

        actual_arrival = arrival_info['actual_arrival']
        now = datetime.now()

        # Calculate time until arrival
        time_until_arrival = actual_arrival - now

        # Convert to minutes
        minutes_until_arrival = time_until_arrival.total_seconds() / 60

        logger.info(f"Minutes until arrival: {minutes_until_arrival:.1f}")

        # Check if we're within the notification window
        # We want to notify when we're at or just past the notification time
        if 0 <= minutes_until_arrival <= self.notify_minutes_before:
            return True

        return False

    def check_delay_change(self, arrival_info: Dict) -> bool:
        """
        Check if delay has changed significantly

        Args:
            arrival_info: Arrival information dictionary

        Returns:
            True if delay changed and notification was sent
        """
        current_delay = arrival_info['delay_minutes']

        if self.last_known_delay is not None:
            delay_change = abs(current_delay - self.last_known_delay)

            # Notify if delay changed by 5+ minutes
            if delay_change >= 5:
                train_name = self.train_data.get('train_name', '')
                train_number = self.train_data.get('train_number', '')

                self.notifier.notify_delay_update(
                    train_number=train_number,
                    train_name=train_name,
                    old_delay=self.last_known_delay,
                    new_delay=current_delay,
                    actual_time=arrival_info['actual_arrival']
                )

                self.last_known_delay = current_delay
                return True

        self.last_known_delay = current_delay
        return False

    def run_check(self):
        """Run a single check cycle"""
        logger.info("=" * 60)
        logger.info("Running train check...")

        arrival_info = self.check_train()

        if not arrival_info:
            logger.error("Failed to get arrival info")
            return

        # Log current status
        logger.info(f"Train: {self.train_data.get('train_number')} {self.train_data.get('train_name')}")
        logger.info(f"Destination: {arrival_info['station']}")
        logger.info(f"Scheduled arrival: {arrival_info['scheduled_arrival'].strftime('%H:%M')}")
        logger.info(f"Delay: {arrival_info['delay_minutes']:+d} minutes")
        logger.info(f"Expected arrival: {arrival_info['actual_arrival'].strftime('%H:%M')}")

        # Check for delay changes
        self.check_delay_change(arrival_info)

        # Check if we should notify
        if self.should_notify(arrival_info):
            actual_arrival = arrival_info['actual_arrival']
            now = datetime.now()
            minutes_until = int((actual_arrival - now).total_seconds() / 60)

            logger.info("🔔 Sending notification!")

            self.notifier.notify_train_arrival(
                train_number=self.train_data.get('train_number', ''),
                train_name=self.train_data.get('train_name', ''),
                station=arrival_info['station'],
                scheduled_time=arrival_info['scheduled_arrival'],
                actual_time=arrival_info['actual_arrival'],
                delay_minutes=arrival_info['delay_minutes'],
                minutes_until_arrival=minutes_until
            )

            self.notification_sent = True
            logger.info("Notification sent! Monitoring will continue until arrival.")

        # Check if train has arrived (stop monitoring)
        actual_arrival = arrival_info['actual_arrival']
        now = datetime.now()

        if now > actual_arrival + timedelta(minutes=10):
            logger.info("Train has arrived. Stopping monitoring.")
            self.monitoring_active = False
            return schedule.CancelJob

    def start_monitoring(self):
        """Start monitoring the train"""
        logger.info("=" * 60)
        logger.info("Train Delay Notifier - Monitoring Started")
        logger.info("=" * 60)
        logger.info(f"Train URL: {self.train_url}")
        logger.info(f"Destination: {self.destination_station}")
        logger.info(f"Notification: {self.notify_minutes_before} minutes before arrival")
        logger.info(f"Check interval: {self.check_interval_minutes} minutes")
        logger.info("=" * 60)

        # Send initial notification
        train_data = self.fetcher.fetch_train_data(self.train_url)
        if train_data:
            self.notifier.notify_monitoring_started(
                train_number=train_data.get('train_number', ''),
                train_name=train_data.get('train_name', ''),
                station=self.destination_station,
                notify_minutes_before=self.notify_minutes_before
            )

        # Run first check immediately
        self.run_check()

        # Schedule periodic checks
        schedule.every(self.check_interval_minutes).minutes.do(self.run_check)

        # Keep running until monitoring is stopped
        try:
            while self.monitoring_active:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds if any job needs to run
        except KeyboardInterrupt:
            logger.info("\nMonitoring stopped by user")
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            self.notifier.notify_error(f"Monitoring error: {str(e)}")

        logger.info("Monitoring stopped")


def main():
    """Test the monitor"""
    # Example: EC 140 Ostravan - Ostrava to Praha
    train_url = "https://www.cd.cz/vlak/140/6.11.2025/5617915/14.34/5457076/19.36/"
    destination = "Praha"
    notify_before = 75  # 75 minutes before arrival

    monitor = TrainMonitor(
        train_url=train_url,
        destination_station=destination,
        notify_minutes_before=notify_before,
        check_interval_minutes=5
    )

    monitor.start_monitoring()


if __name__ == '__main__':
    main()
