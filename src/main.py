"""Main application entry point for Wheel Strategy Trading System"""

import asyncio
import redis
import os
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger
from dotenv import load_dotenv
import argparse
import json

# Import agents
from agents.market_data_agent import MarketDataAgent
from agents.wheel_strategy_agent import WheelStrategyAgent
from agents.risk_management_agent import RiskManagementAgent
from agents.alert_agent import AlertAgent

# Load environment variables
load_dotenv()

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="INFO"
)
logger.add(
    "logs/wheel_strategy.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="DEBUG",
    rotation="1 day"
)


class WheelStrategySystem:
    """Main system orchestrator for wheel strategy trading"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize Redis
        self.redis_client = redis.Redis(
            host=config.get('redis_host', 'localhost'),
            port=config.get('redis_port', 6379),
            db=config.get('redis_db', 0),
            decode_responses=True
        )
        
        # Initialize agents
        self.market_agent = MarketDataAgent(
            self.redis_client,
            max_price=config.get('max_stock_price', 50.0)
        )
        
        self.strategy_agent = WheelStrategyAgent(self.redis_client)
        self.risk_agent = RiskManagementAgent(self.redis_client)
        self.alert_agent = AlertAgent(self.redis_client, config)
        
        # Portfolio state
        self.portfolio = {
            'total_value': config.get('starting_capital', 50000),
            'cash_available': config.get('starting_capital', 50000),
            'positions': [],
            'risk_metrics': {}
        }
        
        # Watchlist
        self.watchlist = config.get('watchlist', [])
        
    async def run(self) -> None:
        """Main run loop"""
        logger.info("Starting Wheel Strategy Trading System")
        logger.info(f"Starting capital: ${self.portfolio['total_value']:,.2f}")
        
        # Start background tasks
        tasks = [
            asyncio.create_task(self.scan_opportunities_loop()),
            asyncio.create_task(self.monitor_positions_loop()),
            asyncio.create_task(self.risk_monitoring_loop()),
            asyncio.create_task(self.alert_agent.monitor_alerts())
        ]
        
        # If watchlist provided, start price monitoring
        if self.watchlist:
            tasks.append(
                asyncio.create_task(
                    self.market_agent.monitor_prices(
                        self.watchlist,
                        callback=self.handle_price_alert
                    )
                )
            )
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            for task in tasks:
                task.cancel()
    
    async def scan_opportunities_loop(self) -> None:
        """Continuously scan for opportunities"""
        while True:
            try:
                logger.info("Scanning for opportunities...")
                
                # Get candidate symbols
                symbols = self.watchlist if self.watchlist else None
                
                # Scan for opportunities
                opportunities = await self.market_agent.scan_opportunities(symbols)
                
                if opportunities:
                    logger.info(f"Found {len(opportunities)} potential opportunities")
                    
                    # Find put opportunities
                    put_opportunities = await self.strategy_agent.find_put_opportunities(
                        [opp['symbol'] for opp in opportunities],
                        capital_available=self.portfolio['cash_available']
                    )
                    
                    # Validate and rank opportunities
                    for opp in put_opportunities[:5]:  # Top 5
                        validation = await self.risk_agent.validate_trade(
                            opp,
                            self.portfolio
                        )
                        
                        if validation['valid']:
                            # Send alert for valid opportunity
                            await self.alert_agent.send_opportunity_alert(
                                opp,
                                priority='high' if opp['score'] > 80 else 'medium'
                            )
                        elif validation['warnings']:
                            logger.warning(
                                f"Opportunity {opp['symbol']} has warnings: {validation['warnings']}"
                            )
                
                # Check for covered call opportunities on holdings
                if self.portfolio['positions']:
                    holdings = [
                        p for p in self.portfolio['positions']
                        if p['position_type'] == 'stock'
                    ]
                    
                    if holdings:
                        call_opportunities = await self.strategy_agent.find_call_opportunities(
                            holdings
                        )
                        
                        for opp in call_opportunities:
                            await self.alert_agent.send_opportunity_alert(
                                opp,
                                priority='medium'
                            )
                
                # Wait before next scan
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"Error in opportunity scanning: {e}")
                await asyncio.sleep(60)
    
    async def monitor_positions_loop(self) -> None:
        """Monitor existing positions"""
        while True:
            try:
                if not self.portfolio['positions']:
                    await asyncio.sleep(60)
                    continue
                
                for position in self.portfolio['positions']:
                    if position['status'] != 'open':
                        continue
                    
                    # Check for assignment risk
                    if position['position_type'] in ['put', 'call']:
                        days_to_expiry = (
                            datetime.strptime(position['expiration_date'], '%Y-%m-%d') -
                            datetime.now()
                        ).days
                        
                        if days_to_expiry <= 7:
                            position['days_to_expiry'] = days_to_expiry
                            await self.alert_agent.send_position_alert(
                                position,
                                'expiration_near'
                            )
                        
                        # Check if position is ITM
                        current_price = await self.market_agent._get_current_price(
                            position['symbol']
                        )
                        
                        if position['position_type'] == 'put':
                            if current_price < position['strike_price']:
                                await self.alert_agent.send_position_alert(
                                    position,
                                    'assignment_warning'
                                )
                        elif position['position_type'] == 'call':
                            if current_price > position['strike_price']:
                                await self.alert_agent.send_position_alert(
                                    position,
                                    'assignment_warning'
                                )
                    
                    # Check profit targets
                    if position.get('unrealized_pnl', 0) > 0:
                        profit_pct = (
                            position['unrealized_pnl'] /
                            abs(position['entry_price'] * position['quantity'])
                        )
                        
                        if profit_pct > 0.5:  # 50% profit
                            position['profit_pct'] = profit_pct
                            await self.alert_agent.send_position_alert(
                                position,
                                'profit_target'
                            )
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error monitoring positions: {e}")
                await asyncio.sleep(60)
    
    async def risk_monitoring_loop(self) -> None:
        """Monitor portfolio risk metrics"""
        while True:
            try:
                # Analyze portfolio risk
                risk_analysis = await self.risk_agent.analyze_portfolio_risk(
                    self.portfolio
                )
                
                self.portfolio['risk_metrics'] = risk_analysis
                
                # Check risk levels
                if risk_analysis.get('risk_level') == 'HIGH':
                    await self.alert_agent.send_risk_alert(
                        'portfolio_risk_high',
                        risk_analysis
                    )
                
                # Check sector concentration
                for sector, weight in risk_analysis.get('sector_allocation', {}).items():
                    if weight > 0.30:
                        await self.alert_agent.send_risk_alert(
                            'sector_concentration',
                            {
                                'sector': sector,
                                'exposure': weight,
                                'limit': 0.30
                            }
                        )
                
                # Log risk metrics
                logger.info(
                    f"Portfolio Risk - Level: {risk_analysis.get('risk_level')}, "
                    f"Score: {risk_analysis.get('risk_score', 0):.1f}/100"
                )
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in risk monitoring: {e}")
                await asyncio.sleep(60)
    
    async def handle_price_alert(self, alert: Dict[str, Any]) -> None:
        """Handle price movement alerts"""
        await self.alert_agent.send_price_alert(
            alert['symbol'],
            'large_move',
            alert
        )
    
    async def execute_trade(self, trade: Dict[str, Any]) -> bool:
        """Execute a trade (simulation)"""
        logger.info(f"Executing trade: {trade}")
        
        # Validate trade
        validation = await self.risk_agent.validate_trade(
            trade,
            self.portfolio
        )
        
        if not validation['valid']:
            logger.error(f"Trade validation failed: {validation['errors']}")
            return False
        
        # Update portfolio (simulation)
        position = {
            'id': f"pos_{datetime.now().timestamp()}",
            'symbol': trade['symbol'],
            'position_type': 'put' if trade['strategy'] == 'CSP' else 'call',
            'strategy_type': trade['strategy'],
            'quantity': 1,
            'entry_price': trade['strike'],
            'current_price': trade['current_price'],
            'strike_price': trade['strike'],
            'expiration_date': trade['expiration'],
            'opening_premium': trade['premium'],
            'status': 'open',
            'opened_at': datetime.now().isoformat()
        }
        
        self.portfolio['positions'].append(position)
        self.portfolio['cash_available'] -= trade['capital_required']
        
        logger.info(f"Trade executed successfully: {position['id']}")
        return True


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Wheel Strategy Trading System')
    parser.add_argument(
        '--config',
        type=str,
        default='config.json',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--watchlist',
        type=str,
        nargs='+',
        help='List of symbols to watch'
    )
    parser.add_argument(
        '--capital',
        type=float,
        default=50000,
        help='Starting capital'
    )
    parser.add_argument(
        '--max-price',
        type=float,
        default=50.0,
        help='Maximum stock price to consider'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = {
        'starting_capital': args.capital,
        'max_stock_price': args.max_price,
        'watchlist': args.watchlist or [],
        'alert_channels': ['console'],
        'redis_host': os.getenv('REDIS_HOST', 'localhost'),
        'redis_port': int(os.getenv('REDIS_PORT', 6379)),
        'redis_db': int(os.getenv('REDIS_DB', 0))
    }
    
    # Load from config file if provided
    if os.path.exists(args.config):
        with open(args.config, 'r') as f:
            file_config = json.load(f)
            config.update(file_config)
    
    # Create and run system
    system = WheelStrategySystem(config)
    await system.run()


if __name__ == "__main__":
    asyncio.run(main())