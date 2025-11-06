"""
Notification System
Sends notifications about train arrivals
"""

import logging
from datetime import datetime
from typing import Optional

try:
    from plyer import notification as plyer_notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    logging.warning("plyer not available, notifications will only be logged")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Notifier:
    """Handles sending notifications to the user"""

    def __init__(self, app_name: str = "Train Delay Notifier"):
        self.app_name = app_name
        self.last_notification = None

    def send_notification(
        self,
        title: str,
        message: str,
        timeout: int = 10
    ) -> bool:
        """
        Send a desktop notification

        Args:
            title: Notification title
            message: Notification message
            timeout: How long to display (seconds)

        Returns:
            True if notification was sent successfully
        """
        logger.info(f"NOTIFICATION: {title} - {message}")

        if PLYER_AVAILABLE:
            try:
                plyer_notification.notify(
                    title=title,
                    message=message,
                    app_name=self.app_name,
                    timeout=timeout
                )
                self.last_notification = datetime.now()
                return True
            except Exception as e:
                logger.error(f"Error sending notification: {e}")
                return False
        else:
            logger.warning("Notification system not available (plyer not installed)")
            return False

    def notify_train_arrival(
        self,
        train_number: str,
        train_name: str,
        station: str,
        scheduled_time: datetime,
        actual_time: datetime,
        delay_minutes: int,
        minutes_until_arrival: int
    ) -> bool:
        """
        Send a notification about an upcoming train arrival

        Args:
            train_number: Train number (e.g., "140")
            train_name: Train name (e.g., "EC Ostravan")
            station: Destination station name
            scheduled_time: Originally scheduled arrival time
            actual_time: Actual arrival time (with delay)
            delay_minutes: Delay in minutes
            minutes_until_arrival: Minutes until actual arrival

        Returns:
            True if notification was sent successfully
        """
        # Format times
        scheduled_str = scheduled_time.strftime('%H:%M')
        actual_str = actual_time.strftime('%H:%M')

        # Build message
        if delay_minutes > 0:
            delay_info = f" (delay: +{delay_minutes} min)"
        elif delay_minutes < 0:
            delay_info = f" (early: {delay_minutes} min)"
        else:
            delay_info = " (on time)"

        title = f"🚆 Train {train_number} arriving soon!"

        message = (
            f"{train_name}\n"
            f"Arriving at {station} in {minutes_until_arrival} minutes\n"
            f"Scheduled: {scheduled_str}\n"
            f"Expected: {actual_str}{delay_info}"
        )

        return self.send_notification(title, message, timeout=15)

    def notify_delay_update(
        self,
        train_number: str,
        train_name: str,
        old_delay: int,
        new_delay: int,
        actual_time: datetime
    ) -> bool:
        """
        Notify about a change in delay

        Args:
            train_number: Train number
            train_name: Train name
            old_delay: Previous delay in minutes
            new_delay: New delay in minutes
            actual_time: Updated arrival time

        Returns:
            True if notification was sent successfully
        """
        delay_change = new_delay - old_delay

        if delay_change > 0:
            change_str = f"increased by {delay_change} min"
            emoji = "⚠️"
        else:
            change_str = f"decreased by {abs(delay_change)} min"
            emoji = "✅"

        title = f"{emoji} Delay Update - Train {train_number}"

        message = (
            f"{train_name}\n"
            f"Delay {change_str}\n"
            f"New delay: {new_delay:+d} minutes\n"
            f"Expected arrival: {actual_time.strftime('%H:%M')}"
        )

        return self.send_notification(title, message, timeout=12)

    def notify_error(self, error_message: str) -> bool:
        """
        Send an error notification

        Args:
            error_message: Error description

        Returns:
            True if notification was sent successfully
        """
        title = "⚠️ Train Monitor Error"
        return self.send_notification(title, error_message, timeout=10)

    def notify_monitoring_started(
        self,
        train_number: str,
        train_name: str,
        station: str,
        notify_minutes_before: int
    ) -> bool:
        """
        Notify that monitoring has started

        Args:
            train_number: Train number
            train_name: Train name
            station: Destination station
            notify_minutes_before: When to notify (minutes before arrival)

        Returns:
            True if notification was sent successfully
        """
        title = "🚆 Train Monitoring Started"

        message = (
            f"Monitoring train {train_number} {train_name}\n"
            f"Destination: {station}\n"
            f"Will notify {notify_minutes_before} minutes before arrival"
        )

        return self.send_notification(title, message, timeout=8)


def main():
    """Test the notifier"""
    from datetime import datetime, timedelta

    notifier = Notifier()

    print("Testing notification system...")

    # Test basic notification
    notifier.send_notification(
        "Test Notification",
        "This is a test notification from the Train Delay Notifier"
    )

    # Test train arrival notification
    scheduled = datetime.now().replace(hour=19, minute=36)
    actual = scheduled + timedelta(minutes=10)

    notifier.notify_train_arrival(
        train_number="140",
        train_name="EC Ostravan",
        station="Praha hl.n.",
        scheduled_time=scheduled,
        actual_time=actual,
        delay_minutes=10,
        minutes_until_arrival=75
    )

    # Test monitoring started
    notifier.notify_monitoring_started(
        train_number="140",
        train_name="EC Ostravan",
        station="Praha hl.n.",
        notify_minutes_before=75
    )

    print("\nNotifications sent! Check your notification center.")


if __name__ == '__main__':
    main()
