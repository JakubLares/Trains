"""
Web Server for Train Delay Notifier
Provides a web UI for monitoring trains
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import threading
import logging
from datetime import datetime
from typing import Optional
import json
import os

from train_monitor import TrainMonitor
from train_fetcher import TrainFetcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global state
monitor_thread: Optional[threading.Thread] = None
current_monitor: Optional[TrainMonitor] = None
monitor_active = False
monitor_status = {
    'active': False,
    'train_number': None,
    'train_name': None,
    'destination': None,
    'last_check': None,
    'next_check': None,
    'current_delay': 0,
    'scheduled_arrival': None,
    'actual_arrival': None,
    'notifications_sent': [],
    'error': None
}


def load_config():
    """Load configuration from config.json"""
    config_file = 'config.json'
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return {
        'train_url': '',
        'destination_station': '',
        'notify_minutes_before': 60,
        'check_interval_minutes': 5
    }


def save_config(config):
    """Save configuration to config.json"""
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    config = load_config()
    return jsonify(config)


@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration"""
    try:
        config = request.json
        save_config(config)
        return jsonify({'success': True, 'message': 'Configuration saved'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current monitoring status"""
    return jsonify(monitor_status)


@app.route('/api/train/info', methods=['POST'])
def get_train_info():
    """Fetch train information without starting monitoring"""
    try:
        data = request.json
        train_url = data.get('train_url')
        destination = data.get('destination_station')

        if not train_url or not destination:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        # Fetch train data
        fetcher = TrainFetcher()
        train_data = fetcher.fetch_train_data(train_url)

        if not train_data:
            return jsonify({'success': False, 'error': 'Failed to fetch train data'}), 500

        # Get arrival info
        arrival_info = fetcher.get_arrival_time_at_station(train_data, destination)

        if not arrival_info:
            return jsonify({
                'success': False,
                'error': f'Could not find station "{destination}"',
                'available_stations': [s['name'] for s in train_data.get('stations', [])]
            }), 404

        return jsonify({
            'success': True,
            'train_number': train_data.get('train_number'),
            'train_name': train_data.get('train_name'),
            'overall_delay': train_data.get('overall_delay', 0),
            'destination': arrival_info['station'],
            'scheduled_arrival': arrival_info['scheduled_arrival'].strftime('%H:%M'),
            'actual_arrival': arrival_info['actual_arrival'].strftime('%H:%M'),
            'delay_minutes': arrival_info['delay_minutes'],
            'stations': [s['name'] for s in train_data.get('stations', [])]
        })

    except Exception as e:
        logger.error(f"Error fetching train info: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/monitor/start', methods=['POST'])
def start_monitoring():
    """Start monitoring a train"""
    global monitor_thread, current_monitor, monitor_active, monitor_status

    if monitor_active:
        return jsonify({'success': False, 'error': 'Monitoring already active'}), 400

    try:
        config = load_config()

        # Validate config
        if not config.get('train_url') or not config.get('destination_station'):
            return jsonify({'success': False, 'error': 'Please configure train details first'}), 400

        # Create monitor
        current_monitor = TrainMonitor(
            train_url=config['train_url'],
            destination_station=config['destination_station'],
            notify_minutes_before=config.get('notify_minutes_before', 60),
            check_interval_minutes=config.get('check_interval_minutes', 5)
        )

        # Start monitoring in background thread
        monitor_active = True
        monitor_thread = threading.Thread(target=run_monitor, daemon=True)
        monitor_thread.start()

        monitor_status['active'] = True
        monitor_status['error'] = None

        return jsonify({'success': True, 'message': 'Monitoring started'})

    except Exception as e:
        logger.error(f"Error starting monitor: {e}", exc_info=True)
        monitor_active = False
        monitor_status['active'] = False
        monitor_status['error'] = str(e)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/monitor/stop', methods=['POST'])
def stop_monitoring():
    """Stop monitoring"""
    global monitor_active, current_monitor, monitor_status

    if not monitor_active:
        return jsonify({'success': False, 'error': 'No active monitoring'}), 400

    monitor_active = False
    if current_monitor:
        current_monitor.monitoring_active = False

    monitor_status['active'] = False

    return jsonify({'success': True, 'message': 'Monitoring stopped'})


def run_monitor():
    """Run the monitor (called in background thread)"""
    global current_monitor, monitor_active, monitor_status

    try:
        if not current_monitor:
            return

        # Run initial check
        arrival_info = current_monitor.check_train()

        if arrival_info:
            monitor_status.update({
                'train_number': current_monitor.train_data.get('train_number'),
                'train_name': current_monitor.train_data.get('train_name'),
                'destination': arrival_info['station'],
                'current_delay': arrival_info['delay_minutes'],
                'scheduled_arrival': arrival_info['scheduled_arrival'].strftime('%H:%M'),
                'actual_arrival': arrival_info['actual_arrival'].strftime('%H:%M'),
                'last_check': datetime.now().strftime('%H:%M:%S')
            })

        # Start monitoring loop
        current_monitor.start_monitoring()

    except Exception as e:
        logger.error(f"Monitor error: {e}", exc_info=True)
        monitor_status['error'] = str(e)
        monitor_status['active'] = False
        monitor_active = False


if __name__ == '__main__':
    import sys

    # Default port, can be overridden with command line argument
    port = 5001
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number. Using default: 5001")

    print("\n" + "="*60)
    print("🚆 Train Delay Notifier - Web UI")
    print("="*60)
    print("\nStarting web server...")
    print("\n📱 Open your browser and go to:")
    print(f"   http://localhost:{port}")
    print("\n💡 Tip: Port 5000 is used by macOS AirPlay Receiver")
    print(f"   We're using port {port} instead")
    print("\n"+"="*60+"\n")

    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)
