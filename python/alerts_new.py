"""
ON1Builder – Alerts Module
==========================

This module provides functionality for sending alerts via Slack and email.
"""

import os
import json
import time
import smtplib
import logging
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

# Alert levels
ALERT_LEVELS = {
    "INFO": 0,
    "WARNING": 1,
    "ERROR": 2,
    "CRITICAL": 3
}

# Alert colors for Slack
ALERT_COLORS = {
    "INFO": "#36a64f",     # Green
    "WARNING": "#ffcc00",  # Yellow
    "ERROR": "#ff9900",    # Orange
    "CRITICAL": "#ff0000"  # Red
}


class SlackNotifier:
    """Notifier for sending messages to Slack."""

    def __init__(self, webhook_url: str = None):
        """Initialize the Slack notifier.
        
        Args:
            webhook_url: The Slack webhook URL
        """
        self.webhook_url = webhook_url
        self.logger = logging.getLogger("SlackNotifier")

    def send(self, message: str, level: str = "INFO", details: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send a message to Slack.
        
        Args:
            message: The message to send
            level: The alert level (INFO, WARNING, ERROR, CRITICAL)
            details: Additional details to include in the message
            
        Returns:
            True if the message was sent successfully, False otherwise
        """
        if not self.webhook_url:
            self.logger.warning("Slack webhook URL not set, skipping notification")
            return False
            
        details = details or {}
        
        # Add timestamp if not provided
        if "timestamp" not in details:
            details["timestamp"] = datetime.utcnow().isoformat() + "Z"
            
        try:
            # Convert details to Slack fields
            fields = []
            for key, value in details.items():
                fields.append({
                    "title": key,
                    "value": str(value),
                    "short": True
                })
                
            # Create payload
            payload = {
                "attachments": [
                    {
                        "fallback": f"{level} - {message}",
                        "color": ALERT_COLORS.get(level, "#36a64f"),
                        "pretext": "ON1Builder Alert",
                        "title": f"{level} - {message}",
                        "fields": fields,
                        "footer": "ON1Builder",
                        "ts": int(time.time())
                    }
                ]
            }
            
            # Send to Slack
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info(f"Slack message sent: {level} - {message}")
                return True
            else:
                self.logger.error(f"Failed to send Slack message: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending Slack message: {e}")
            return False
