#!/usr/bin/env python3
"""
Simple API server for Polymarket Insider Detector
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import psycopg2.extras
from config import Config

app = Flask(__name__)
CORS(app)

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy'})

@app.route('/api/stats')
def stats():
    try:
        conn = psycopg2.connect(Config.DATABASE_URL)
        cur = conn.cursor()
        
        # Get basic stats
        cur.execute("SELECT COUNT(*) FROM alerts WHERE created_at >= NOW() - INTERVAL '24 hours'")
        total_alerts = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM alerts WHERE created_at >= NOW() - INTERVAL '24 hours' AND confidence_level = 'HIGH'")
        high_risk = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM alerts WHERE created_at >= NOW() - INTERVAL '24 hours' AND confidence_level = 'MEDIUM'")
        medium_risk = cur.fetchone()[0]
        
        cur.execute("SELECT SUM(t.amount_usd) FROM alerts a JOIN trades t ON a.trade_id = t.id WHERE a.created_at >= NOW() - INTERVAL '24 hours'")
        result = cur.fetchone()
        total_volume = float(result[0]) if result[0] else 0
        
        conn.close()
        
        return jsonify({
            'total_alerts': total_alerts,
            'high_risk': high_risk,
            'medium_risk': medium_risk,
            'total_volume': total_volume
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/large-trades')
def large_trades():
    """Get large trades for easy viewing"""
    try:
        min_amount = int(request.args.get('min_amount', 1000))
        hours = int(request.args.get('hours', 168))  # Default 7 days
        
        conn = psycopg2.connect(Config.DATABASE_URL)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cur.execute("""
            SELECT 
                t.tx_hash,
                t.amount_usd,
                t.timestamp,
                t.block_number,
                w.address as wallet,
                w.total_trades,
                w.total_volume_usd,
                w.first_seen,
                EXTRACT(EPOCH FROM (NOW() - w.first_seen))/3600 as wallet_age_hours,
                CASE 
                    WHEN w.winning_trades + w.losing_trades > 0 
                    THEN (w.winning_trades::float / (w.winning_trades + w.losing_trades) * 100)::numeric(5,1)
                    ELSE 0
                END as win_rate_pct,
                m.title as market_title,
                m.category as market_category,
                m.description as market_description,
                EXTRACT(EPOCH FROM (m.end_date - NOW()))/86400 as days_until_close,
                o.outcome_name as bet_side,
                o.current_price as bet_odds
            FROM trades t
            JOIN wallets w ON t.wallet_id = w.id
            JOIN markets m ON t.market_id = m.id
            LEFT JOIN outcomes o ON m.id = o.market_id AND t.outcome_index = o.outcome_index
            WHERE t.amount_usd >= %s
              AND t.timestamp >= NOW() - INTERVAL '%s hours'
            ORDER BY t.amount_usd DESC, t.timestamp DESC
            LIMIT 100
        """, (min_amount, hours))
        
        trades = [dict(row) for row in cur.fetchall()]
        
        # Add risk analysis to each trade
        for trade in trades:
            flags = []
            risk_score = 0
            
            # New wallet
            if trade['wallet_age_hours'] < 48:
                flags.append("New wallet")
                risk_score += 25
                
            # Large first trade
            if trade['total_trades'] == 1 and trade['amount_usd'] >= 10000:
                flags.append("First trade")
                risk_score += 30
                
            # High win rate
            if trade['win_rate_pct'] >= 75 and trade['total_trades'] >= 3:
                flags.append(f"{trade['win_rate_pct']}% win rate")
                risk_score += 20
                
            # Whale size
            if trade['amount_usd'] >= 50000:
                flags.append("Whale trade")
                risk_score += 15
            elif trade['amount_usd'] >= 20000:
                flags.append("Large trade")
                risk_score += 10
                
            # Determine risk level
            if risk_score >= 40:
                risk_level = "HIGH"
            elif risk_score >= 20:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
                
            trade['flags'] = flags
            trade['risk_score'] = risk_score
            trade['risk_level'] = risk_level
        
        conn.close()
        return jsonify({'trades': trades, 'total': len(trades)})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts')
def alerts():
    try:
        conn = psycopg2.connect(Config.DATABASE_URL)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cur.execute("""
            SELECT 
                a.id,
                a.insider_score,
                a.confidence_level,
                a.flags,
                a.description,
                a.created_at,
                w.address as wallet_address,
                w.total_trades as wallet_total_trades,
                w.winning_trades,
                w.losing_trades,
                COALESCE(w.winning_trades::float / NULLIF(w.winning_trades + w.losing_trades, 0), 0) as win_rate,
                m.title as market_title,
                m.category as market_category,
                t.amount_usd,
                t.price_per_share,
                t.outcome_index,
                t.tx_hash,
                t.timestamp as trade_timestamp
            FROM alerts a
            JOIN wallets w ON a.wallet_id = w.id
            JOIN markets m ON a.market_id = m.id
            JOIN trades t ON a.trade_id = t.id
            WHERE a.created_at >= NOW() - INTERVAL '24 hours'
            ORDER BY a.insider_score DESC, a.created_at DESC
            LIMIT 50
        """)
        
        alerts = [dict(row) for row in cur.fetchall()]
        conn.close()
        
        return jsonify({
            'alerts': alerts,
            'total': len(alerts),
            'has_more': False
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Simple API Server on http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=False)