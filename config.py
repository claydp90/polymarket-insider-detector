import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # API Keys and URLs
    ALCHEMY_WS_URL = os.getenv('ALCHEMY_WS_URL', '')
    POLYGONSCAN_API_KEY = os.getenv('POLYGONSCAN_API_KEY', '')
    # Allow running without Polygonscan initially
    POLYGONSCAN_REQUIRED = False
    DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL', '')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/polymarket_detector')
    
    # Polymarket API
    POLYMARKET_API_BASE = 'https://gamma-api.polymarket.com'
    POLYMARKET_CLOB_API = 'https://clob.polymarket.com'
    
    # Contract Addresses (Polygon)
    USDC_CONTRACT = '0x2791bca1f2de4661ed88a30c99a7a9449aa84174'
    POLYMARKET_EXCHANGE = '0x4bfb41d5b3570defd03c39a9a4d8de6bd8b8982e'
    CONDITIONAL_TOKENS = '0x4d97dcd97ec945f40cf65f87097ace5ea0476045'
    
    # Detection Parameters
    WHALE_THRESHOLD_USD = 10000
    NEW_WALLET_HOURS = 48
    SUSPICIOUS_WIN_RATE = 0.75
    AGAINST_MARKET_THRESHOLD = 0.30
    MARKET_IMPACT_THRESHOLD = 0.05
    HIGH_SCORE_THRESHOLD = 70
    MEDIUM_SCORE_THRESHOLD = 40
    
    # Timing Analysis
    RESOLUTION_WINDOW_HOURS = 24
    SUSPICIOUS_TIMING_PERCENTAGE = 0.60
    
    # Alert Settings
    MIN_ALERT_SCORE = 40
    DISCORD_ALERT_ENABLED = bool(DISCORD_WEBHOOK_URL)
    
    # API Rate Limits
    POLYMARKET_RATE_LIMIT = 100  # requests per minute
    POLYGONSCAN_RATE_LIMIT = 5   # requests per second
    
    # Monitoring Settings
    SYNC_INTERVAL_SECONDS = 30
    CLEANUP_DAYS = 30  # Clean old data after 30 days
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate required configuration and return status"""
        status = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Required fields
        required_fields = [
            ('ALCHEMY_WS_URL', cls.ALCHEMY_WS_URL),
            ('DATABASE_URL', cls.DATABASE_URL)
        ]
        
        # Optional but recommended
        if cls.POLYGONSCAN_REQUIRED and not cls.POLYGONSCAN_API_KEY:
            required_fields.append(('POLYGONSCAN_API_KEY', cls.POLYGONSCAN_API_KEY))
        
        for field_name, field_value in required_fields:
            if not field_value:
                status['errors'].append(f"Missing required environment variable: {field_name}")
                status['valid'] = False
        
        # Optional but recommended
        if not cls.DISCORD_WEBHOOK_URL:
            status['warnings'].append("Discord webhook not configured - alerts will not be sent")
            
        if not cls.POLYGONSCAN_API_KEY:
            status['warnings'].append("Polygonscan API key not configured - wallet funding analysis will be limited")
        
        # Validate URLs
        if cls.ALCHEMY_WS_URL and not cls.ALCHEMY_WS_URL.startswith('wss://'):
            status['errors'].append("ALCHEMY_WS_URL must be a WebSocket URL starting with wss://")
            status['valid'] = False
            
        return status
    
    @classmethod
    def get_scoring_weights(cls) -> Dict[str, int]:
        """Get the scoring weights for different risk factors"""
        return {
            'new_wallet_large_bet': 30,
            'high_win_rate': 40,
            'against_consensus': 20,
            'whale_size': 15,
            'high_market_impact': 20,
            'privacy_funding': 25,
            'suspicious_timing': 35,
            'concentrated_betting': 15
        }