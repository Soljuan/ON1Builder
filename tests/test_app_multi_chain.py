#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the app_multi_chain module.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
import sys
import os
from datetime import datetime

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import after path setup
from python.app_multi_chain_updated import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@patch('python.alerts_new.SlackNotifier.send')
def test_test_alert_endpoint(mock_send, client):
    """Test the test_alert endpoint."""
    # Mock the configuration and core
    with app.app_context():
        app.config['config'] = MagicMock()
        app.config['config'].SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/test'
        app.config['core'] = MagicMock()
        
        # Set up the mock
        mock_send.return_value = True
        
        # Make a request to the endpoint
        response = client.post('/api/test-alert', json={'chain_id': '1'})
        
        # Check the response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['message'] == 'Test alert sent'
        
        # Check that the mock was called with the right arguments
        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        assert '✅ Test alert from ON1Builder on chain 1 at' in args[0]
        assert datetime.now().strftime('%Y-%m-%d') in args[0]


@patch('python.app_multi_chain_updated.simulate_transaction')
def test_simulate_transaction_endpoint(mock_simulate, client):
    """Test the simulate_transaction endpoint."""
    # Mock the configuration and core
    with app.app_context():
        app.config['config'] = MagicMock()
        app.config['core'] = MagicMock()
        app.config['core'].workers = {'1': MagicMock()}
        
        # Set up the mock
        mock_result = {
            'success': True,
            'gas_used': 150000,
            'gas_price_gwei': 25,
            'estimated_cost_eth': 0.003,
            'estimated_profit_eth': 0.007,
        }
        mock_simulate.return_value = mock_result
        
        # Make a request to the endpoint
        response = client.post('/api/simulate-transaction', json={
            'chain_id': '1',
            'opportunity': {'token': '0x123', 'amount': '1.0'}
        })
        
        # Check the response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['message'] == 'Transaction simulated'
        assert data['chain_id'] == '1'
        assert data['result'] == mock_result
        
        # Check that the mock was called with the right arguments
        mock_simulate.assert_called_once_with(
            chain_id='1',
            opportunity={'token': '0x123', 'amount': '1.0'}
        )


@patch('python.transaction_core.simulate_transaction')
def test_simulate_transaction_endpoint_chain_not_active(mock_simulate, client):
    """Test the simulate_transaction endpoint when the chain is not active."""
    # Mock the configuration and core
    with app.app_context():
        app.config['config'] = MagicMock()
        app.config['core'] = MagicMock()
        app.config['core'].workers = {'1': MagicMock()}
        
        # Make a request to the endpoint with an inactive chain
        response = client.post('/api/simulate-transaction', json={
            'chain_id': '137',
            'opportunity': {'token': '0x123', 'amount': '1.0'}
        })
        
        # Check the response
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert data['message'] == 'Chain 137 is not active'
        
        # Check that the mock was not called
        mock_simulate.assert_not_called()


@patch('python.alerts_new.SlackNotifier.send')
def test_test_alert_endpoint_core_not_initialized(mock_send, client):
    """Test the test_alert endpoint when the core is not initialized."""
    # Mock the configuration and core
    with app.app_context():
        app.config['config'] = MagicMock()
        app.config['core'] = None
        
        # Make a request to the endpoint
        response = client.post('/api/test-alert', json={'chain_id': '1'})
        
        # Check the response
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert data['message'] == 'Core not initialized'
        
        # Check that the mock was not called
        mock_send.assert_not_called()
