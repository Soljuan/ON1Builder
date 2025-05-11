#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ON1Builder – API Server with Multi-Chain Support
=============================================
Provides API endpoints for monitoring and controlling the bot.
"""

import os
import sys
import json
import logging
import asyncio
import time
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
from flask import Flask, jsonify, request, Response, g, current_app
from flask_cors import CORS
from python.configuration_multi_chain import MultiChainConfiguration
from python.multi_chain_core import MultiChainCore
from python.alerts_new import SlackNotifier
from python.transaction_core import simulate_transaction

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log"),
    ],
)
logger = logging.getLogger("App")

# Create Flask app
app = Flask(__name__)
CORS(app)

# Initialize app config with default values
app.config['config'] = None
app.config['core'] = None
app.config['bot_status'] = "stopped"
app.config['bot_task'] = None

# Initialize configuration and core
async def initialize() -> bool:
    """Initialize the configuration and core.
    
    Returns:
        True if initialization was successful, False otherwise
    """
    try:
        # Load configuration
        logger.info("Loading configuration...")
        app.config['config'] = MultiChainConfiguration()
        
        # Create core
        logger.info("Creating MultiChainCore...")
        app.config['core'] = MultiChainCore(app.config['config'])
        
        # Initialize core
        logger.info("Initializing MultiChainCore...")
        success = await app.config['core'].initialize()
        if not success:
            logger.error("Failed to initialize MultiChainCore")
            return False
        
        logger.info("Initialization complete")
        return True
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        return False

# Health check
@app.route("/healthz", methods=["GET"])
def healthz() -> Tuple[Dict[str, Any], int]:
    """Health check endpoint.
    
    Returns:
        A tuple of (response, status_code)
    """
    try:
        config = current_app.config['config']
        core = current_app.config['core']
        bot_status = current_app.config['bot_status']
        
        # Check if configuration is loaded
        if config is None:
            return jsonify({
                "status": "error",
                "message": "Configuration not loaded",
                "go_live": False,
            }), 500
        
        # Check if core is initialized
        if core is None:
            return jsonify({
                "status": "error",
                "message": "Core not initialized",
                "go_live": config.GO_LIVE,
            }), 500
        
        # Check if any chains are active
        if not core.workers:
            return jsonify({
                "status": "error",
                "message": "No active chains",
                "go_live": config.GO_LIVE,
            }), 500
        
        # Check Vault connectivity if GO_LIVE is true
        if config.GO_LIVE:
            if not hasattr(config, "VAULT_ADDR") or not config.VAULT_ADDR:
                return jsonify({
                    "status": "error",
                    "message": "VAULT_ADDR not set",
                    "go_live": config.GO_LIVE,
                }), 500
            
            if not hasattr(config, "VAULT_TOKEN") or not config.VAULT_TOKEN:
                return jsonify({
                    "status": "error",
                    "message": "VAULT_TOKEN not set",
                    "go_live": config.GO_LIVE,
                }), 500
        
        # All checks passed
        return jsonify({
            "status": "ok",
            "message": "Service is healthy",
            "go_live": config.GO_LIVE,
            "active_chains": len(core.workers),
            "bot_status": bot_status,
        }), 200
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        config = current_app.config['config']
        return jsonify({
            "status": "error",
            "message": f"Error in health check: {str(e)}",
            "go_live": getattr(config, "GO_LIVE", False) if config else False,
        }), 500

# Metrics endpoint
@app.route("/metrics", methods=["GET"])
def metrics() -> Dict[str, Any]:
    """Metrics endpoint.
    
    Returns:
        A dictionary of metrics
    """
    try:
        core = current_app.config['core']
        bot_status = current_app.config['bot_status']
        
        # Check if core is initialized
        if core is None:
            return jsonify({
                "status": "error",
                "message": "Core not initialized",
            }), 500
        
        # Get metrics from core
        metrics = core.get_metrics()
        
        # Add bot status
        metrics["bot_status"] = bot_status
        
        return jsonify(metrics)
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error getting metrics: {str(e)}",
        }), 500

# Status endpoint
@app.route("/status", methods=["GET"])
def status() -> Dict[str, Any]:
    """Status endpoint.
    
    Returns:
        A dictionary with the current status
    """
    try:
        config = current_app.config['config']
        core = current_app.config['core']
        bot_status = current_app.config['bot_status']
        
        return jsonify({
            "status": bot_status,
            "go_live": getattr(config, "GO_LIVE", False) if config else False,
            "dry_run": getattr(config, "DRY_RUN", True) if config else True,
            "active_chains": len(core.workers) if core else 0,
            "uptime": core.metrics["uptime_seconds"] if core else 0,
        })
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error getting status: {str(e)}",
        }), 500

# Start bot endpoint
@app.route("/start", methods=["POST"])
def start_bot() -> Dict[str, Any]:
    """Start the bot.
    
    Returns:
        A dictionary with the result
    """
    try:
        core = current_app.config['core']
        bot_status = current_app.config['bot_status']
        
        # Check if bot is already running
        if bot_status == "running":
            return jsonify({
                "status": "error",
                "message": "Bot is already running",
            }), 400
        
        # Check if core is initialized
        if core is None:
            return jsonify({
                "status": "error",
                "message": "Core not initialized",
            }), 500
        
        # Start the bot
        logger.info("Starting bot...")
        current_app.config['bot_status'] = "starting"
        
        # Create task to run the core
        async def run_core():
            try:
                current_app.config['bot_status'] = "running"
                await core.run()
            except Exception as e:
                logger.error(f"Error running core: {e}")
            finally:
                current_app.config['bot_status'] = "stopped"
        
        # Start the task
        loop = asyncio.get_event_loop()
        current_app.config['bot_task'] = loop.create_task(run_core())
        
        return jsonify({
            "status": "success",
            "message": "Bot started",
        })
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        current_app.config['bot_status'] = "error"
        return jsonify({
            "status": "error",
            "message": f"Error starting bot: {str(e)}",
        }), 500

# Stop bot endpoint
@app.route("/stop", methods=["POST"])
def stop_bot() -> Dict[str, Any]:
    """Stop the bot.
    
    Returns:
        A dictionary with the result
    """
    try:
        core = current_app.config['core']
        bot_status = current_app.config['bot_status']
        bot_task = current_app.config['bot_task']
        
        # Check if bot is running
        if bot_status != "running":
            return jsonify({
                "status": "error",
                "message": f"Bot is not running (status: {bot_status})",
            }), 400
        
        # Check if core is initialized
        if core is None:
            return jsonify({
                "status": "error",
                "message": "Core not initialized",
            }), 500
        
        # Stop the bot
        logger.info("Stopping bot...")
        current_app.config['bot_status'] = "stopping"
        
        # Create task to stop the core
        async def stop_core():
            try:
                await core.stop()
                if bot_task:
                    bot_task.cancel()
            except Exception as e:
                logger.error(f"Error stopping core: {e}")
            finally:
                current_app.config['bot_status'] = "stopped"
        
        # Start the task
        loop = asyncio.get_event_loop()
        loop.create_task(stop_core())
        
        return jsonify({
            "status": "success",
            "message": "Bot stopping",
        })
    except Exception as e:
        logger.error(f"Error stopping bot: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error stopping bot: {str(e)}",
        }), 500

# Test alert endpoint
@app.route("/api/test-alert", methods=["POST"])
def test_alert() -> Dict[str, Any]:
    """Send a test alert.
    
    Returns:
        A dictionary with the result
    """
    try:
        core = current_app.config['core']
        config = current_app.config['config']
        
        # Check if core is initialized
        if core is None:
            return jsonify({
                "status": "error",
                "message": "Core not initialized",
            }), 500
        
        # Log test alert
        logger.info("Sending test alert")
        
        # Get request data
        data = request.json or {}
        chain_id = data.get("chain_id", "1")
        
        # Send alert via Slack
        notifier = SlackNotifier(webhook_url=config.SLACK_WEBHOOK_URL)
        notifier.send(f"✅ Test alert from ON1Builder on chain {chain_id} at {datetime.utcnow().isoformat()}Z")
        
        return jsonify({
            "status": "success",
            "message": "Test alert sent",
        })
    except Exception as e:
        logger.error(f"Error sending test alert: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error sending test alert: {str(e)}",
        }), 500

# Simulate transaction endpoint
@app.route("/api/simulate-transaction", methods=["POST"])
def simulate_transaction_endpoint() -> Dict[str, Any]:
    """Simulate a transaction.
    
    Returns:
        A dictionary with the result
    """
    try:
        core = current_app.config['core']
        
        # Check if core is initialized
        if core is None:
            return jsonify({
                "status": "error",
                "message": "Core not initialized",
            }), 500
        
        # Get request data
        data = request.json or {}
        chain_id = data.get("chain_id", "1")
        opportunity = data.get("opportunity", {})
        
        # Check if chain is active
        if chain_id not in core.workers:
            return jsonify({
                "status": "error",
                "message": f"Chain {chain_id} is not active",
            }), 400
        
        # Log simulation
        logger.info(f"Simulating transaction on chain {chain_id}")
        
        # Simulate transaction
        sim_result = simulate_transaction(chain_id=chain_id, opportunity=opportunity)
        logger.info(f"Simulation result for chain {chain_id}: {sim_result}")
        
        return jsonify({
            "status": "success",
            "message": "Transaction simulated",
            "chain_id": chain_id,
            "result": sim_result,
        })
    except Exception as e:
        logger.error(f"Error simulating transaction: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error simulating transaction: {str(e)}",
        }), 500

# Main function
async def main() -> int:
    """Main entry point.
    
    Returns:
        Exit code
    """
    try:
        # Initialize configuration and core
        success = await initialize()
        if not success:
            logger.error("Initialization failed")
            return 1
        
        logger.info("Initialization successful")
        return 0
    except Exception as e:
        logger.error(f"Error in main: {e}")
        return 1

# Run the app
if __name__ == "__main__":
    # Run initialization
    loop = asyncio.get_event_loop()
    exit_code = loop.run_until_complete(main())
    
    if exit_code != 0:
        sys.exit(exit_code)
    
    # Run the Flask app
    app.run(host="0.0.0.0", port=5001)
