"""
NAO Robot Client
Gestisce comunicazione con il server body.py
"""

import requests
import logging

logger = logging.getLogger(__name__)


class NaoClient:
    """Client for communicating with NAO robot server"""
    
    def __init__(self, base_url, timeout=30):
        """
        Initialize NAO client
        
        Args:
            base_url (str): Base URL of NAO server (e.g., "http://192.168.1.100:5004")
            timeout (int): Default timeout for requests
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
    
    def test_connection(self):
        """
        Test connection to NAO server
        
        Returns:
            bool: True if connected successfully
        """
        try:
            logger.info("Testing connection to NAO server...")
            response = requests.get(
                "{}/get_server_buffer_length".format(self.base_url),
                timeout=5
            )
            response.raise_for_status()
            logger.info("✓ Connected successfully to NAO server")
            return True
        except Exception as e:
            logger.error("✗ Failed to connect: {}".format(e))
            logger.error("  Make sure body.py is running on {}".format(self.base_url))
            return False
    
    def speak(self, text):
        """
        Make NAO speak
        
        Args:
            text (str): Text for NAO to speak
            
        Returns:
            bool: True if successful
        """
        try:
            logger.info("🔊 Sending text to NAO...")
            logger.debug("Text: {}".format(text[:100]))
            
            response = requests.post(
                "{}/talk".format(self.base_url),
                json={"message": text},
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.info("✓ NAO is speaking...")
            return True
            
        except requests.exceptions.Timeout:
            logger.error("❌ Timeout sending message to NAO")
            return False
        except Exception as e:
            logger.error("❌ Failed to send message: {}".format(e))
            return False
    
    def execute_action(self, action_name, params=None):
        """
        Execute physical action on NAO
        
        Args:
            action_name (str): Name of the action
            params (dict): Action parameters
            
        Returns:
            tuple: (success, message)
        """
        if params is None:
            params = {}
        
        try:
            logger.info("🤖 Executing action: {} with params: {}".format(action_name, params))
            
            response = requests.post(
                "{}/action/execute".format(self.base_url),
                json={"action": action_name, "params": params},
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            
            success = result.get("success", False)
            message = result.get("message", "Action completed")
            
            if success:
                logger.info("✓ Action completed: {}".format(message))
            else:
                logger.warning("⚠️ Action failed: {}".format(result.get('error', 'Unknown error')))
            
            return success, message
            
        except Exception as e:
            logger.error("❌ Failed to execute action: {}".format(e))
            return False, "Error: {}".format(e)
    
    def get_battery_level(self):
        """
        Get NAO battery level
        
        Returns:
            int or None: Battery percentage or None if failed
        """
        try:
            response = requests.get(
                "{}/action/battery".format(self.base_url),
                timeout=5
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("success"):
                # Extract percentage from message
                message = result.get("message", "")
                import re
                match = re.search(r'(\d+)%', message)
                if match:
                    return int(match.group(1))
            
            return None
            
        except Exception as e:
            logger.error("Failed to get battery level: {}".format(e))
            return None
