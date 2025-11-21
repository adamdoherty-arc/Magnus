"""
Performance Tracker for Kalshi Predictions

Tracks actual outcomes, calculates performance metrics, and stores results in database.
"""

import os
import psycopg2
import psycopg2.extras
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging

from .metrics import (
    calculate_brier_score,
    calculate_log_loss,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_max_drawdown,
    calculate_roi_metrics,
    calculate_calibration_metrics,
    calculate_confidence_metrics,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceTracker:
    """Tracks prediction performance and calculates metrics"""

    def __init__(self, db_config: Optional[Dict] = None):
        """
        Initialize performance tracker.

        Args:
            db_config: Database configuration dict. If None, uses default.
        """
        self.db_config = db_config or {
            'host': 'localhost',
            'port': '5432',
            'database': 'magnus',
            'user': 'postgres',
            'password': os.getenv('DB_PASSWORD')
        }
        self._initialize_schema()

    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)

    def _initialize_schema(self):
        """Initialize analytics schema"""
        try:
            schema_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'analytics_schema.sql'
            )

            if not os.path.exists(schema_path):
                logger.warning(f"Analytics schema not found: {schema_path}")
                return

            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()

            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(schema_sql)
            conn.commit()
            cur.close()
            conn.close()

            logger.info("Analytics schema initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing schema: {e}")

    def update_market_outcome(self, ticker: str, actual_outcome: str) -> bool:
        """
        Update the actual outcome for a market and calculate performance metrics.

        Args:
            ticker: Market ticker
            actual_outcome: 'yes' or 'no'

        Returns:
            True if successful
        """
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            # Get prediction data
            cur.execute("""
                SELECT
                    p.id as prediction_id,
                    p.market_id,
                    p.ticker,
                    p.predicted_outcome,
                    p.confidence_score,
                    m.yes_price,
                    m.market_type,
                    m.home_team,
                    m.close_time,
                    p.created_at
                FROM kalshi_predictions p
                JOIN kalshi_markets m ON p.market_id = m.id
                WHERE p.ticker = %s
            """, (ticker,))

            pred = cur.fetchone()
            if not pred:
                logger.warning(f"No prediction found for {ticker}")
                return False

            # Calculate metrics
            predicted_outcome = pred['predicted_outcome']
            is_correct = (predicted_outcome == actual_outcome)

            # Convert confidence to probability
            confidence_score = float(pred['confidence_score'])
            if predicted_outcome == 'yes':
                predicted_prob = confidence_score / 100.0
            else:
                predicted_prob = 1.0 - (confidence_score / 100.0)

            actual_value = 1.0 if actual_outcome == 'yes' else 0.0

            # Calculate Brier score and log loss
            brier = calculate_brier_score(
                np.array([predicted_prob]),
                np.array([actual_value])
            )
            log_loss_val = calculate_log_loss(
                np.array([predicted_prob]),
                np.array([actual_value])
            )

            # Calculate P&L (assuming $100 bet)
            bet_size = 100.0
            market_price = float(pred['yes_price']) if pred['yes_price'] else 0.5

            if predicted_outcome == actual_outcome:
                # Win: get back (bet / price)
                pnl = (bet_size / market_price) - bet_size
            else:
                # Loss: lose the bet
                pnl = -bet_size

            roi_percent = (pnl / bet_size) * 100

            # Calculate time to close
            close_time = pred['close_time']
            predicted_at = pred['created_at']
            if close_time and predicted_at:
                time_to_close = close_time - predicted_at
                time_to_close_hours = int(time_to_close.total_seconds() / 3600)
            else:
                time_to_close_hours = None

            # Determine sector (team name)
            sector = pred['home_team'] or 'Unknown'

            # Store performance record
            cur.execute("""
                INSERT INTO prediction_performance (
                    prediction_id, market_id, ticker,
                    predicted_outcome, confidence_score,
                    predicted_probability, market_price,
                    actual_outcome, is_correct, settled_at,
                    bet_size, pnl, roi_percent,
                    brier_score, log_loss,
                    market_type, sector, time_to_close_hours,
                    predicted_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(),
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (prediction_id) DO UPDATE SET
                    actual_outcome = EXCLUDED.actual_outcome,
                    is_correct = EXCLUDED.is_correct,
                    settled_at = NOW(),
                    pnl = EXCLUDED.pnl,
                    roi_percent = EXCLUDED.roi_percent,
                    brier_score = EXCLUDED.brier_score,
                    log_loss = EXCLUDED.log_loss,
                    updated_at = NOW()
            """, (
                pred['prediction_id'], pred['market_id'], ticker,
                predicted_outcome, confidence_score,
                predicted_prob, market_price,
                actual_outcome, is_correct,
                bet_size, pnl, roi_percent,
                brier, log_loss_val,
                pred['market_type'], sector, time_to_close_hours,
                predicted_at
            ))

            conn.commit()
            logger.info(f"Updated outcome for {ticker}: {actual_outcome} (Correct: {is_correct}, P&L: ${pnl:.2f})")
            return True

        except Exception as e:
            conn.rollback()
            logger.error(f"Error updating outcome for {ticker}: {e}")
            return False

        finally:
            cur.close()
            conn.close()

    def get_performance_summary(self, market_type: Optional[str] = None,
                               days: Optional[int] = None) -> Dict:
        """
        Get overall performance summary.

        Args:
            market_type: Filter by 'nfl', 'college', or None for all
            days: Only include predictions from last N days

        Returns:
            Dictionary with performance metrics
        """
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            query = """
                SELECT
                    COUNT(*) as total_predictions,
                    COUNT(actual_outcome) as settled_predictions,
                    COUNT(CASE WHEN is_correct = TRUE THEN 1 END) as correct_predictions,
                    SUM(pnl) as total_pnl,
                    AVG(roi_percent) as avg_roi,
                    AVG(brier_score) as avg_brier_score,
                    AVG(log_loss) as avg_log_loss,
                    MIN(predicted_at) as first_prediction,
                    MAX(predicted_at) as last_prediction
                FROM prediction_performance
                WHERE actual_outcome IS NOT NULL
            """

            params = []
            if market_type:
                query += " AND market_type = %s"
                params.append(market_type)

            if days:
                query += " AND predicted_at >= NOW() - INTERVAL '%s days'"
                params.append(days)

            cur.execute(query, params)
            result = cur.fetchone()

            if not result or result['settled_predictions'] == 0:
                return {
                    'total_predictions': 0,
                    'settled_predictions': 0,
                    'accuracy': 0.0,
                    'total_pnl': 0.0,
                    'avg_roi': 0.0,
                    'avg_brier_score': 0.0,
                    'avg_log_loss': 0.0,
                }

            accuracy = (result['correct_predictions'] / result['settled_predictions'] * 100
                       if result['settled_predictions'] > 0 else 0)

            return {
                'total_predictions': result['total_predictions'],
                'settled_predictions': result['settled_predictions'],
                'correct_predictions': result['correct_predictions'],
                'accuracy': float(accuracy),
                'total_pnl': float(result['total_pnl'] or 0),
                'avg_roi': float(result['avg_roi'] or 0),
                'avg_brier_score': float(result['avg_brier_score'] or 0),
                'avg_log_loss': float(result['avg_log_loss'] or 0),
                'first_prediction': result['first_prediction'],
                'last_prediction': result['last_prediction'],
            }

        finally:
            cur.close()
            conn.close()

    def get_performance_by_confidence(self) -> pd.DataFrame:
        """Get performance metrics grouped by confidence level"""
        conn = self.get_connection()

        query = """
            SELECT
                CASE
                    WHEN confidence_score >= 80 THEN 'High (≥80)'
                    WHEN confidence_score >= 60 THEN 'Medium (60-80)'
                    ELSE 'Low (<60)'
                END as confidence_bucket,
                COUNT(*) as total,
                COUNT(CASE WHEN is_correct = TRUE THEN 1 END) as correct,
                ROUND(100.0 * COUNT(CASE WHEN is_correct = TRUE THEN 1 END) /
                      NULLIF(COUNT(*), 0), 2) as accuracy,
                AVG(confidence_score) as avg_confidence,
                AVG(brier_score) as avg_brier_score,
                SUM(pnl) as total_pnl
            FROM prediction_performance
            WHERE actual_outcome IS NOT NULL
            GROUP BY confidence_bucket
            ORDER BY avg_confidence DESC
        """

        try:
            df = pd.read_sql_query(query, conn)
            return df
        finally:
            conn.close()

    def get_performance_by_sector(self, limit: int = 20) -> pd.DataFrame:
        """Get performance metrics by sector (team)"""
        conn = self.get_connection()

        query = f"""
            SELECT
                sector,
                COUNT(*) as total,
                COUNT(CASE WHEN is_correct = TRUE THEN 1 END) as correct,
                ROUND(100.0 * COUNT(CASE WHEN is_correct = TRUE THEN 1 END) /
                      NULLIF(COUNT(*), 0), 2) as accuracy,
                SUM(pnl) as total_pnl,
                AVG(roi_percent) as avg_roi
            FROM prediction_performance
            WHERE actual_outcome IS NOT NULL
            GROUP BY sector
            ORDER BY total_pnl DESC
            LIMIT {limit}
        """

        try:
            df = pd.read_sql_query(query, conn)
            return df
        finally:
            conn.close()

    def get_performance_over_time(self, days: int = 30,
                                  market_type: Optional[str] = None) -> pd.DataFrame:
        """Get daily performance metrics"""
        conn = self.get_connection()

        query = """
            SELECT
                DATE(predicted_at) as date,
                COUNT(*) as predictions,
                COUNT(actual_outcome) as settled,
                COUNT(CASE WHEN is_correct = TRUE THEN 1 END) as correct,
                ROUND(100.0 * COUNT(CASE WHEN is_correct = TRUE THEN 1 END) /
                      NULLIF(COUNT(actual_outcome), 0), 2) as accuracy,
                SUM(pnl) as daily_pnl
            FROM prediction_performance
            WHERE predicted_at >= NOW() - INTERVAL '%s days'
        """

        params = [days]
        if market_type:
            query += " AND market_type = %s"
            params.append(market_type)

        query += """
            GROUP BY DATE(predicted_at)
            ORDER BY date DESC
        """

        try:
            df = pd.read_sql_query(query, conn, params=params)
            return df
        finally:
            conn.close()

    def get_calibration_data(self) -> Dict:
        """Get calibration curve data"""
        conn = self.get_connection()
        cur = conn.cursor()

        try:
            cur.execute("""
                SELECT
                    predicted_probability,
                    CASE WHEN actual_outcome = predicted_outcome THEN 1 ELSE 0 END as correct
                FROM prediction_performance
                WHERE actual_outcome IS NOT NULL
            """)

            rows = cur.fetchall()
            if not rows:
                return {'ece': 0, 'bins': [], 'bin_accuracy': [], 'bin_confidence': []}

            predicted_probs = np.array([float(row[0]) for row in rows])
            actual_outcomes = np.array([float(row[1]) for row in rows])

            calibration = calculate_calibration_metrics(predicted_probs, actual_outcomes, n_bins=10)
            return calibration

        finally:
            cur.close()
            conn.close()

    def get_best_predictions(self, limit: int = 10) -> pd.DataFrame:
        """Get best predictions by ROI"""
        conn = self.get_connection()

        query = f"""
            SELECT
                ticker,
                predicted_outcome,
                actual_outcome,
                confidence_score,
                pnl,
                roi_percent,
                predicted_at
            FROM prediction_performance
            WHERE actual_outcome IS NOT NULL
            ORDER BY pnl DESC
            LIMIT {limit}
        """

        try:
            df = pd.read_sql_query(query, conn)
            return df
        finally:
            conn.close()

    def get_worst_predictions(self, limit: int = 10) -> pd.DataFrame:
        """Get worst predictions by ROI"""
        conn = self.get_connection()

        query = f"""
            SELECT
                ticker,
                predicted_outcome,
                actual_outcome,
                confidence_score,
                pnl,
                roi_percent,
                predicted_at
            FROM prediction_performance
            WHERE actual_outcome IS NOT NULL
            ORDER BY pnl ASC
            LIMIT {limit}
        """

        try:
            df = pd.read_sql_query(query, conn)
            return df
        finally:
            conn.close()

    def calculate_sharpe_sortino(self, days: int = 30) -> Dict[str, float]:
        """Calculate Sharpe and Sortino ratios"""
        conn = self.get_connection()

        query = """
            SELECT pnl, bet_size
            FROM prediction_performance
            WHERE actual_outcome IS NOT NULL
              AND predicted_at >= NOW() - INTERVAL '%s days'
            ORDER BY predicted_at
        """

        try:
            df = pd.read_sql_query(query, conn, params=[days])

            if df.empty or len(df) < 2:
                return {'sharpe_ratio': 0.0, 'sortino_ratio': 0.0}

            # Calculate returns
            returns = (df['pnl'] / df['bet_size']).values

            sharpe = calculate_sharpe_ratio(returns, periods_per_year=365)
            sortino = calculate_sortino_ratio(returns, periods_per_year=365)

            return {
                'sharpe_ratio': float(sharpe),
                'sortino_ratio': float(sortino),
            }

        finally:
            conn.close()

    def calculate_max_drawdown_from_db(self, days: Optional[int] = None) -> Dict[str, float]:
        """Calculate maximum drawdown from historical P&L"""
        conn = self.get_connection()

        query = """
            SELECT predicted_at, pnl
            FROM prediction_performance
            WHERE actual_outcome IS NOT NULL
        """

        params = []
        if days:
            query += " AND predicted_at >= NOW() - INTERVAL '%s days'"
            params.append(days)

        query += " ORDER BY predicted_at"

        try:
            df = pd.read_sql_query(query, conn, params=params)

            if df.empty:
                return {'max_drawdown_pct': 0.0, 'max_drawdown_amount': 0.0}

            # Calculate equity curve
            initial_capital = 10000.0
            equity = initial_capital + df['pnl'].cumsum()

            max_dd_pct, start_idx, end_idx = calculate_max_drawdown(equity.values)

            return {
                'max_drawdown_pct': float(max_dd_pct),
                'max_drawdown_amount': float(equity.iloc[start_idx] - equity.iloc[end_idx]) if start_idx >= 0 else 0.0,
            }

        finally:
            conn.close()


if __name__ == "__main__":
    # Test performance tracker
    print("="*80)
    print("PERFORMANCE TRACKER - Test")
    print("="*80)

    tracker = PerformanceTracker()

    # Get performance summary
    summary = tracker.get_performance_summary()
    print("\nPerformance Summary:")
    print(f"  Total Predictions: {summary['total_predictions']}")
    print(f"  Settled: {summary['settled_predictions']}")
    print(f"  Accuracy: {summary['accuracy']:.2f}%")
    print(f"  Total P&L: ${summary['total_pnl']:.2f}")
    print(f"  Avg ROI: {summary['avg_roi']:.2f}%")
    print(f"  Avg Brier Score: {summary['avg_brier_score']:.4f}")

    # Get performance by confidence
    print("\nPerformance by Confidence:")
    df_conf = tracker.get_performance_by_confidence()
    if not df_conf.empty:
        print(df_conf.to_string(index=False))

    # Get Sharpe/Sortino
    risk_metrics = tracker.calculate_sharpe_sortino(days=30)
    print(f"\nRisk Metrics (30 days):")
    print(f"  Sharpe Ratio: {risk_metrics['sharpe_ratio']:.2f}")
    print(f"  Sortino Ratio: {risk_metrics['sortino_ratio']:.2f}")

    # Get max drawdown
    dd_metrics = tracker.calculate_max_drawdown_from_db()
    print(f"  Max Drawdown: {dd_metrics['max_drawdown_pct']:.2f}%")

    print("\n" + "="*80)
    print("Test Complete!")
    print("="*80)
