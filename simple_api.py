#!/usr/bin/env python3
"""
Simple API server for Polymarket Insider Detector
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import psycopg2
import psycopg2.extras
from config import Config
import os

app = Flask(__name__)
  CORS(app, origins="*", methods=["GET", "POST", "OPTIONS"],
  allow_headers=["Content-Type", "Authorization"])

@app.route('/')
def dashboard():
    """Serve the main dashboard"""
    try:
        with open('dashboard_minimal.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({'message': 'Dashboard not found. Try /api/health to test API'}), 404

@app.route('/dashboard')
def dashboard_alt():
    """Alternative dashboard route"""
    return dashboard()

@app.route('/dashboard_minimal.html')
def dashboard_file():
    """Direct file access"""
    return dashboard()

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy'})

@app.route('/api/stats')
def stats():
    # Demo data for now (no database required)
    return jsonify({
        'total_alerts': 8,
        'high_risk': 3,
        'medium_risk': 5,
        'total_volume': 425000.50
    })

@app.route('/api/large-trades')
def large_trades():
    """Get large trades for easy viewing - Demo data"""
    # Demo data for now (no database required)
    demo_trades = [
        {
            'tx_hash': '0x1234567890abcdef...',
            'amount_usd': 125000,
            'timestamp': '2025-10-19T10:30:00Z',
            'wallet': '0x742d35Cc66...',
            'wallet_age_hours': 6,
            'total_trades': 1,
            'market_title': 'Fed Decision in October',
            'market_category': 'Economics',
            'bet_side': '25 bps decrease',
            'bet_odds': 0.95,
            'days_until_close': 7,
            'flags': ['New wallet', 'First trade', 'Whale trade'],
            'risk_score': 70,
            'risk_level': 'HIGH'
        },
        {
            'tx_hash': '0xabcdef1234567890...',
            'amount_usd': 85000,
            'timestamp': '2025-10-19T09:15:00Z',
            'wallet': '0x8ba1f109551b...',
            'wallet_age_hours': 12,
            'total_trades': 1,
            'market_title': 'Ireland Presidential Election',
            'market_category': 'Politics',
            'bet_side': 'Catherine Connolly',
            'bet_odds': 0.89,
            'days_until_close': 2,
            'flags': ['New wallet', 'First trade', 'Large trade'],
            'risk_score': 65,
            'risk_level': 'HIGH'
        },
        {
            'tx_hash': '0x9876543210fedcba...',
            'amount_usd': 50000,
            'timestamp': '2025-10-19T08:45:00Z',
            'wallet': '0x4f26FfBe5F04...',
            'wallet_age_hours': 2,
            'total_trades': 1,
            'market_title': 'US bank failure before July?',
            'market_category': 'Economics',
            'bet_side': 'Yes',
            'bet_odds': 0.15,
            'days_until_close': 253,
            'flags': ['New wallet', 'First trade', 'Whale trade'],
            'risk_score': 70,
            'risk_level': 'HIGH'
        }
    ]
    
    return jsonify({'trades': demo_trades, 'total': len(demo_trades)})

@app.route('/api/alerts')
def alerts():
    """Get alerts - Demo data"""
    # Demo data for now (no database required)
    demo_alerts = [
        {
            'id': 1,
            'insider_score': 85,
            'confidence_level': 'HIGH',
            'flags': ['new_wallet', 'large_first_trade', 'urgent_timing'],
            'description': 'Large bet on Fed decision by new wallet',
            'created_at': '2025-10-19T10:30:00Z',
            'wallet_address': '0x742d35Cc66...',
            'market_title': 'Fed Decision in October',
            'market_category': 'Economics',
            'amount_usd': 125000,
            'tx_hash': '0x1234567890abcdef...'
        },
        {
            'id': 2,
            'insider_score': 78,
            'confidence_level': 'HIGH',
            'flags': ['new_wallet', 'contrarian_bet'],
            'description': 'Large contrarian bet on Ireland election',
            'created_at': '2025-10-19T09:15:00Z',
            'wallet_address': '0x8ba1f109551b...',
            'market_title': 'Ireland Presidential Election',
            'market_category': 'Politics',
            'amount_usd': 85000,
            'tx_hash': '0xabcdef1234567890...'
        }
    ]
    
    return jsonify({
        'alerts': demo_alerts,
        'total': len(demo_alerts),
        'has_more': False
    })

if __name__ == '__main__':
    print("🚀 Starting Simple API Server on http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=False)
