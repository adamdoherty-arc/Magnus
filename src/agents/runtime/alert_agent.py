"""Alert Agent for monitoring and notifications"""

import asyncio
import redis
import json
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from loguru import logger
from decimal import Decimal
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests


class AlertAgent:
    """Agent responsible for monitoring conditions and sending alerts"""
    
    def __init__(self, redis_client: redis.Redis, config: Dict[str, Any]):
        self.redis_client = redis_client
        self.config = config
        self.alert_channels = config.get('alert_channels', ['console'])
        self.alert_rules = []
        self.alert_history = []
        
    async def monitor_alerts(self) -> None:
        """Main monitoring loop for alerts"""
        logger.info("Starting alert monitoring")
        
        while True:
            try:
                # Check all active alert rules
                for rule in self.alert_rules:
                    if await self._should_trigger(rule):
                        await self._trigger_alert(rule)
                
                # Check for system alerts from Redis pub/sub
                await self._check_system_alerts()
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in alert monitoring: {e}")
                await asyncio.sleep(60)
    
    def add_alert_rule(self, rule: Dict[str, Any]) -> str:
        """Add a new alert rule"""
        rule_id = f"rule_{datetime.now().timestamp()}"
        rule['id'] = rule_id
        rule['created_at'] = datetime.now().isoformat()
        rule['active'] = True
        rule['last_triggered'] = None
        
        self.alert_rules.append(rule)
        logger.info(f"Added alert rule: {rule_id}")
        
        return rule_id
    
    async def send_opportunity_alert(
        self,
        opportunity: Dict[str, Any],
        priority: str = 'medium'
    ) -> None:
        """Send alert for new opportunity"""
        alert = {
            'type': 'opportunity',
            'priority': priority,
            'data': opportunity,
            'timestamp': datetime.now().isoformat()
        }
        
        title = f"🎯 New {opportunity['strategy']} Opportunity: {opportunity['symbol']}"
        
        message = self._format_opportunity_message(opportunity)
        
        await self._send_alert(title, message, alert)
    
    async def send_price_alert(
        self,
        symbol: str,
        event_type: str,
        details: Dict[str, Any]
    ) -> None:
        """Send price movement alert"""
        alert = {
            'type': 'price_alert',
            'symbol': symbol,
            'event': event_type,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        
        if event_type == 'large_move':
            emoji = "📈" if details['change'] > 0 else "📉"
            title = f"{emoji} {symbol} moved {abs(details['change_pct']):.1%}"
        elif event_type == 'target_hit':
            title = f"🎯 {symbol} hit target price ${details['price']:.2f}"
        else:
            title = f"⚠️ {symbol} Alert: {event_type}"
        
        message = self._format_price_alert_message(symbol, event_type, details)
        
        await self._send_alert(title, message, alert)
    
    async def send_position_alert(
        self,
        position: Dict[str, Any],
        event_type: str
    ) -> None:
        """Send position-related alert"""
        alert = {
            'type': 'position_alert',
            'position': position,
            'event': event_type,
            'timestamp': datetime.now().isoformat()
        }
        
        symbol = position['symbol']
        
        if event_type == 'assignment_warning':
            title = f"⚠️ {symbol} Assignment Warning"
            message = f"Your {position['strategy']} position on {symbol} is at risk of assignment."
        elif event_type == 'expiration_near':
            title = f"⏰ {symbol} Expiring Soon"
            message = f"Your {position['strategy']} position expires in {position['days_to_expiry']} days."
        elif event_type == 'profit_target':
            title = f"💰 {symbol} Profit Target Hit"
            message = f"Your position has reached {position['profit_pct']:.1%} profit."
        else:
            title = f"📊 {symbol} Position Update"
            message = f"Position event: {event_type}"
        
        await self._send_alert(title, message, alert)
    
    async def send_risk_alert(
        self,
        risk_type: str,
        details: Dict[str, Any]
    ) -> None:
        """Send risk management alert"""
        alert = {
            'type': 'risk_alert',
            'risk_type': risk_type,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        
        if risk_type == 'position_size_exceeded':
            title = "⚠️ Position Size Limit Exceeded"
        elif risk_type == 'sector_concentration':
            title = "⚠️ High Sector Concentration"
        elif risk_type == 'portfolio_risk_high':
            title = "🚨 High Portfolio Risk"
        else:
            title = f"⚠️ Risk Alert: {risk_type}"
        
        message = self._format_risk_alert_message(risk_type, details)
        
        await self._send_alert(title, message, alert, priority='high')
    
    async def _send_alert(
        self,
        title: str,
        message: str,
        alert_data: Dict[str, Any],
        priority: str = 'medium'
    ) -> None:
        """Send alert through configured channels"""
        
        # Store in history
        self.alert_history.append(alert_data)
        
        # Send through each configured channel
        for channel in self.alert_channels:
            try:
                if channel == 'console':
                    await self._send_console_alert(title, message)
                elif channel == 'email':
                    await self._send_email_alert(title, message, priority)
                elif channel == 'discord':
                    await self._send_discord_alert(title, message, priority)
                elif channel == 'telegram':
                    await self._send_telegram_alert(title, message)
                    
            except Exception as e:
                logger.error(f"Failed to send alert via {channel}: {e}")
    
    async def _send_console_alert(self, title: str, message: str) -> None:
        """Print alert to console"""
        logger.info(f"\n{'='*50}\n{title}\n{'-'*50}\n{message}\n{'='*50}")
    
    async def _send_email_alert(
        self,
        title: str,
        message: str,
        priority: str
    ) -> None:
        """Send email alert"""
        if not self.config.get('email'):
            return
        
        email_config = self.config['email']
        
        msg = MIMEMultipart()
        msg['From'] = email_config['from']
        msg['To'] = email_config['to']
        msg['Subject'] = f"[{priority.upper()}] {title}"
        
        msg.attach(MIMEText(message, 'plain'))
        
        with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
    
    async def _send_discord_alert(
        self,
        title: str,
        message: str,
        priority: str
    ) -> None:
        """Send Discord webhook alert"""
        if not self.config.get('discord_webhook'):
            return
        
        color = {
            'low': 0x00FF00,  # Green
            'medium': 0xFFFF00,  # Yellow
            'high': 0xFF0000  # Red
        }.get(priority, 0x0099FF)
        
        webhook_data = {
            'embeds': [{
                'title': title,
                'description': message,
                'color': color,
                'timestamp': datetime.now().isoformat(),
                'footer': {'text': 'Wheel Strategy Bot'}
            }]
        }
        
        response = requests.post(
            self.config['discord_webhook'],
            json=webhook_data
        )
        
        if response.status_code != 204:
            logger.error(f"Discord webhook failed: {response.status_code}")
    
    async def _send_telegram_alert(self, title: str, message: str) -> None:
        """Send Telegram alert"""
        if not self.config.get('telegram'):
            return
        
        tg_config = self.config['telegram']
        
        text = f"**{title}**\n\n{message}"
        
        url = f"https://api.telegram.org/bot{tg_config['bot_token']}/sendMessage"
        
        payload = {
            'chat_id': tg_config['chat_id'],
            'text': text,
            'parse_mode': 'Markdown'
        }
        
        response = requests.post(url, json=payload)
        
        if not response.json().get('ok'):
            logger.error(f"Telegram alert failed: {response.text}")
    
    def _format_opportunity_message(self, opp: Dict[str, Any]) -> str:
        """Format opportunity alert message"""
        return f"""
Strategy: {opp['strategy']}
Symbol: {opp['symbol']}
Strike: ${opp['strike']:.2f}
Expiration: {opp['expiration']}
DTE: {opp['dte']} days

Premium: ${opp['premium']:.2f}
Premium Yield: {opp['premium_yield']:.2%}
Expected Return: {opp['expected_return']:.1f}% annualized

Current Price: ${opp['current_price']:.2f}
Capital Required: ${opp['capital_required']:.2f}

Score: {opp['score']:.1f}/100
Recommendation: {opp['recommendation']}
"""
    
    def _format_price_alert_message(
        self,
        symbol: str,
        event_type: str,
        details: Dict[str, Any]
    ) -> str:
        """Format price alert message"""
        if event_type == 'large_move':
            return f"""
{symbol} has moved {details['change_pct']:.2%} in the last {details.get('period', 'period')}.

Previous: ${details['previous']:.2f}
Current: ${details['current']:.2f}
Change: ${details['change']:.2f}

Volume: {details.get('volume', 'N/A')}
"""
        else:
            return f"""
{symbol} alert triggered.

Event: {event_type}
Details: {json.dumps(details, indent=2)}
"""
    
    def _format_risk_alert_message(
        self,
        risk_type: str,
        details: Dict[str, Any]
    ) -> str:
        """Format risk alert message"""
        if risk_type == 'position_size_exceeded':
            return f"""
Position size limit exceeded.

Symbol: {details['symbol']}
Position Size: {details['position_size_pct']:.1%}
Limit: {details['limit']:.1%}

Recommendation: Reduce position size or skip this trade.
"""
        elif risk_type == 'sector_concentration':
            return f"""
High concentration in {details['sector']}.

Current Exposure: {details['exposure']:.1%}
Limit: {details['limit']:.1%}

Top Holdings:
{chr(10).join([f"- {h['symbol']}: {h['weight']:.1%}" for h in details.get('holdings', [])])}

Recommendation: Diversify into other sectors.
"""
        else:
            return f"""
Risk alert: {risk_type}

Details:
{json.dumps(details, indent=2)}
"""
    
    async def _should_trigger(self, rule: Dict[str, Any]) -> bool:
        """Check if alert rule should trigger"""
        if not rule.get('active'):
            return False
        
        # Check cooldown period
        if rule['last_triggered']:
            last_trigger = datetime.fromisoformat(rule['last_triggered'])
            cooldown = rule.get('cooldown_minutes', 60)
            
            if datetime.now() - last_trigger < timedelta(minutes=cooldown):
                return False
        
        # Check rule conditions
        rule_type = rule.get('type')
        
        if rule_type == 'price_threshold':
            return await self._check_price_threshold(rule)
        elif rule_type == 'volatility_spike':
            return await self._check_volatility_spike(rule)
        elif rule_type == 'volume_spike':
            return await self._check_volume_spike(rule)
        
        return False
    
    async def _check_price_threshold(self, rule: Dict[str, Any]) -> bool:
        """Check if price threshold is crossed"""
        # Implementation would check actual prices
        return False
    
    async def _check_volatility_spike(self, rule: Dict[str, Any]) -> bool:
        """Check for volatility spike"""
        # Implementation would check implied volatility
        return False
    
    async def _check_volume_spike(self, rule: Dict[str, Any]) -> bool:
        """Check for volume spike"""
        # Implementation would check volume data
        return False
    
    async def _trigger_alert(self, rule: Dict[str, Any]) -> None:
        """Trigger alert for rule"""
        rule['last_triggered'] = datetime.now().isoformat()
        
        await self.send_price_alert(
            rule.get('symbol', 'UNKNOWN'),
            rule['type'],
            rule
        )
    
    async def _check_system_alerts(self) -> None:
        """Check for system-generated alerts from Redis"""
        # Implementation would subscribe to Redis pub/sub channels
        pass