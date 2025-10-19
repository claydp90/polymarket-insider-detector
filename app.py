#!/usr/bin/env python3
"""
Minimal test version for Railway deployment
"""

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Polymarket Insider Detector</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background: #0a0a0b; 
                color: #fff; 
                text-align: center; 
                padding: 50px;
            }
            .container { max-width: 800px; margin: 0 auto; }
            .stat { 
                display: inline-block; 
                margin: 20px; 
                padding: 20px; 
                background: #1a1a1a; 
                border-radius: 8px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 Polymarket Insider Detector</h1>
            <p>Monitoring suspicious trading patterns on prediction markets</p>
            
            <div class="stat">
                <h3>Total Alerts</h3>
                <p style="font-size: 24px; color: #ff6b6b;">8</p>
            </div>
            
            <div class="stat">
                <h3>High Risk Trades</h3>
                <p style="font-size: 24px; color: #ffd93d;">3</p>
            </div>
            
            <div class="stat">
                <h3>Volume Monitored</h3>
                <p style="font-size: 24px; color: #6bcf7f;">$425K</p>
            </div>
            
            <h2>Recent Suspicious Activity</h2>
            <div style="text-align: left; max-width: 600px; margin: 0 auto;">
                <div style="background: #2a1810; padding: 15px; margin: 10px 0; border-radius: 6px;">
                    <strong>HIGH RISK:</strong> $125K bet on Fed Decision<br>
                    <small>New wallet • First trade • 7 days until close</small>
                </div>
                <div style="background: #2a1810; padding: 15px; margin: 10px 0; border-radius: 6px;">
                    <strong>HIGH RISK:</strong> $85K bet on Ireland Election<br>
                    <small>New wallet • 12 hours old • 2 days until close</small>
                </div>
                <div style="background: #2a1810; padding: 15px; margin: 10px 0; border-radius: 6px;">
                    <strong>HIGH RISK:</strong> $50K bet on US Bank Failure<br>
                    <small>New wallet • Contrarian position • 2 hours old</small>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'app': 'polymarket-insider-detector'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)