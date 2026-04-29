#!/usr/bin/env python3
"""
OT Watchdog Agent - Raspberry Pi Monitoring Script
Monitors OT devices (PLC, HMI, Switch, Modem) and sends status to WordPress
"""

import os
import json
import logging
import time
import subprocess
from datetime import datetime
import requests
from typing import Dict, List, Tuple

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ot-watchdog-agent')


class OTWatchdogAgent:
    """Main agent class for OT device monitoring"""

    def __init__(self):
        """Initialize the agent with configuration"""
        self.wordpress_url = os.getenv('WORDPRESS_URL')
        self.api_key = os.getenv('OT_WATCHDOG_API_KEY')
        self.check_interval = int(os.getenv('CHECK_INTERVAL', 30))
        
        # Parse devices from JSON
        devices_json = os.getenv('OT_DEVICES', '{}')
        self.devices = json.loads(devices_json)
        
        if not self.wordpress_url or not self.api_key:
            logger.error('Missing required environment variables: WORDPRESS_URL, OT_WATCHDOG_API_KEY')
            raise ValueError('Configuration incomplete')
        
        if not self.devices:
            logger.warning('No devices configured in OT_DEVICES')
        
        logger.info(f'OT Watchdog Agent initialized')
        logger.info(f'WordPress: {self.wordpress_url}')
        logger.info(f'Devices: {list(self.devices.keys())}')
        logger.info(f'Check interval: {self.check_interval}s')

    def ping_device(self, host: str, timeout: int = 5) -> bool:
        """
        Ping a device to check if it's online
        
        Args:
            host: IP address or hostname
            timeout: Ping timeout in seconds
            
        Returns:
            True if device is reachable, False otherwise
        """
        try:
            # Use ping command (cross-platform)
            cmd = ['ping', '-c', '1', '-W', str(timeout * 1000), host]
            result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout + 1)
            return result.returncode == 0
        except Exception as e:
            logger.warning(f'Error pinging {host}: {e}')
            return False

    def check_devices(self) -> Dict[str, str]:
        """
        Check status of all configured devices
        
        Returns:
            Dictionary with device names and their status (online/offline)
        """
        status = {}
        logger.debug(f'Checking {len(self.devices)} devices...')
        
        for device_name, device_ip in self.devices.items():
            is_online = self.ping_device(device_ip)
            status[device_name] = 'online' if is_online else 'offline'
            logger.info(f'{device_name} ({device_ip}): {status[device_name]}')
        
        return status

    def send_status(self, status: Dict[str, str]) -> bool:
        """
        Send device status to WordPress via REST API
        
        Args:
            status: Dictionary with device status
            
        Returns:
            True if successful, False otherwise
        """
        api_url = f'{self.wordpress_url.rstrip("/")}/wp-json/ot/v1/update'
        
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key
        }
        
        try:
            logger.debug(f'Sending status to {api_url}')
            response = requests.post(
                api_url,
                json=status,
                headers=headers,
                timeout=10,
                verify=True
            )
            
            if response.status_code in [200, 201]:
                logger.info(f'Status sent successfully (HTTP {response.status_code})')
                return True
            else:
                logger.error(f'Failed to send status (HTTP {response.status_code}): {response.text}')
                return False
                
        except requests.exceptions.ConnectionError as e:
            logger.error(f'Connection error: {e}')
            return False
        except requests.exceptions.Timeout:
            logger.error('Request timeout')
            return False
        except Exception as e:
            logger.error(f'Error sending status: {e}')
            return False

    def run(self) -> None:
        """
        Main loop - continuously monitor devices and send status
        """
        logger.info('Starting monitoring loop...')
        
        try:
            while True:
                try:
                    # Check all devices
                    status = self.check_devices()
                    
                    # Send status to WordPress
                    self.send_status(status)
                    
                    # Wait for next check
                    logger.debug(f'Waiting {self.check_interval}s until next check')
                    time.sleep(self.check_interval)
                    
                except Exception as e:
                    logger.error(f'Error in monitoring loop: {e}')
                    time.sleep(self.check_interval)
                    
        except KeyboardInterrupt:
            logger.info('Received shutdown signal')
        except Exception as e:
            logger.critical(f'Fatal error: {e}')
            raise


def main():
    """Entry point"""
    try:
        agent = OTWatchdogAgent()
        agent.run()
    except KeyboardInterrupt:
        logger.info('Agent stopped')
    except Exception as e:
        logger.critical(f'Fatal error: {e}')
        exit(1)


if __name__ == '__main__':
    main()
