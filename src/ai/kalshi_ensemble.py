"""
Kalshi Multi-Model AI Ensemble
Combines predictions from GPT-4, Claude, Gemini, and local models
"""

import logging
import asyncio
from typing import List, Dict, Optional, Literal
from dataclasses import dataclass
from datetime import datetime
import json
import os

from src.ai.model_clients import (
    GPT4Client,
    ClaudeClient,
    GeminiClient,
    LocalModelClient
)
from src.ai.prompt_templates import (
    build_market_analysis_prompt,
    build_context_summary
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ModelPrediction:
    """Individual model's prediction"""
    model_name: str
    predicted_outcome: str  # 'yes' or 'no'
    confidence: float  # 0-100
    edge_percentage: float  # Can be negative
    reasoning: str
    key_factors: List[str]
    raw_response: Dict
    latency_ms: int
    timestamp: datetime


@dataclass
class ConsensusPrediction:
    """Ensemble consensus prediction"""
    predicted_outcome: str
    confidence: float
    edge_percentage: float
    model_agreement: float  # Percentage of models that agree
    reasoning: str
    key_factors: List[str]
    individual_predictions: List[ModelPrediction]

    # Recommendation
    recommended_action: str
    recommended_stake_pct: float
    risk_level: str

    # Metadata
    ensemble_mode: str
    models_used: List[str]
    total_latency_ms: int
    timestamp: datetime


class KalshiEnsemble:
    """
    Multi-model AI ensemble for Kalshi market prediction

    Supports 4 operation modes:
    - 'premium': All 4 models (highest accuracy, highest cost)
    - 'balanced': GPT-4 + Claude + Gemini (default)
    - 'fast': GPT-4 + Gemini (speed optimized)
    - 'cost': Gemini + Llama3 (cost optimized)
    """

    # Model weights for consensus voting
    MODEL_WEIGHTS = {
        'gpt4': 0.40,
        'claude': 0.30,
        'gemini': 0.20,
        'llama3': 0.10
    }

    # Ensemble modes
    ENSEMBLE_MODES = {
        'premium': ['gpt4', 'claude', 'gemini', 'llama3'],
        'balanced': ['gpt4', 'claude', 'gemini'],
        'fast': ['gpt4', 'gemini'],
        'cost': ['gemini', 'llama3']
    }

    def __init__(self, mode: Literal['premium', 'balanced', 'fast', 'cost'] = 'balanced'):
        """
        Initialize ensemble with specified mode

        Args:
            mode: Operation mode (premium, balanced, fast, cost)
        """
        self.mode = mode
        self.models_to_use = self.ENSEMBLE_MODES[mode]

        # Initialize model clients
        self.clients = {}

        if 'gpt4' in self.models_to_use:
            self.clients['gpt4'] = GPT4Client()

        if 'claude' in self.models_to_use:
            self.clients['claude'] = ClaudeClient()

        if 'gemini' in self.models_to_use:
            self.clients['gemini'] = GeminiClient()

        if 'llama3' in self.models_to_use:
            self.clients['llama3'] = LocalModelClient()

        logger.info(f"Initialized Kalshi Ensemble in '{mode}' mode with models: {self.models_to_use}")

    async def predict(self, market: Dict, context: Optional[Dict] = None) -> ConsensusPrediction:
        """
        Generate ensemble prediction for a market

        Args:
            market: Market data dictionary
            context: Optional contextual data (weather, injuries, etc.)

        Returns:
            ConsensusPrediction with aggregated results
        """
        start_time = datetime.now()

        # Build prompt for all models
        prompt = build_market_analysis_prompt(market, context)

        # Run predictions in parallel
        tasks = []
        for model_name, client in self.clients.items():
            task = self._get_model_prediction(model_name, client, prompt, market)
            tasks.append(task)

        # Wait for all predictions
        predictions = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out errors
        valid_predictions = [
            p for p in predictions
            if isinstance(p, ModelPrediction)
        ]

        if not valid_predictions:
            logger.error("All models failed to generate predictions")
            raise Exception("Ensemble prediction failed - no valid predictions")

        # Log any errors
        for i, p in enumerate(predictions):
            if isinstance(p, Exception):
                logger.error(f"Model {self.models_to_use[i]} failed: {p}")

        # Calculate consensus
        consensus = self._calculate_consensus(valid_predictions)

        # Calculate total latency
        total_latency = int((datetime.now() - start_time).total_seconds() * 1000)

        # Build final prediction
        return ConsensusPrediction(
            predicted_outcome=consensus['outcome'],
            confidence=consensus['confidence'],
            edge_percentage=consensus['edge'],
            model_agreement=consensus['agreement'],
            reasoning=consensus['reasoning'],
            key_factors=consensus['key_factors'],
            individual_predictions=valid_predictions,
            recommended_action=consensus['action'],
            recommended_stake_pct=consensus['stake_pct'],
            risk_level=consensus['risk_level'],
            ensemble_mode=self.mode,
            models_used=[p.model_name for p in valid_predictions],
            total_latency_ms=total_latency,
            timestamp=datetime.now()
        )

    async def _get_model_prediction(
        self,
        model_name: str,
        client,
        prompt: str,
        market: Dict
    ) -> ModelPrediction:
        """
        Get prediction from a single model

        Args:
            model_name: Name of model
            client: Model client instance
            prompt: Analysis prompt
            market: Market data

        Returns:
            ModelPrediction
        """
        start_time = datetime.now()

        try:
            # Call model API
            response = await client.analyze_market(prompt)

            # Parse response
            parsed = self._parse_model_response(response, model_name)

            # Calculate latency
            latency = int((datetime.now() - start_time).total_seconds() * 1000)

            return ModelPrediction(
                model_name=model_name,
                predicted_outcome=parsed['predicted_outcome'],
                confidence=parsed['confidence'],
                edge_percentage=parsed['edge_percentage'],
                reasoning=parsed['reasoning'],
                key_factors=parsed['key_factors'],
                raw_response=response,
                latency_ms=latency,
                timestamp=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error getting prediction from {model_name}: {e}")
            raise

    def _parse_model_response(self, response: Dict, model_name: str) -> Dict:
        """
        Parse model response into standardized format

        Args:
            response: Raw model response
            model_name: Name of model

        Returns:
            Parsed prediction dictionary
        """
        try:
            # Try to extract JSON from response
            if isinstance(response, dict) and 'content' in response:
                content = response['content']
            else:
                content = str(response)

            # Look for JSON in response
            if '{' in content:
                json_start = content.index('{')
                json_end = content.rindex('}') + 1
                json_str = content[json_start:json_end]
                parsed = json.loads(json_str)
            else:
                # If no JSON, try to parse structured text
                parsed = self._parse_text_response(content)

            # Validate required fields
            required_fields = [
                'predicted_outcome',
                'confidence',
                'edge_percentage',
                'reasoning'
            ]

            for field in required_fields:
                if field not in parsed:
                    raise ValueError(f"Missing required field: {field}")

            # Normalize values
            parsed['predicted_outcome'] = parsed['predicted_outcome'].lower()
            parsed['confidence'] = float(parsed['confidence'])
            parsed['edge_percentage'] = float(parsed['edge_percentage'])

            if 'key_factors' not in parsed:
                parsed['key_factors'] = []

            return parsed

        except Exception as e:
            logger.error(f"Error parsing {model_name} response: {e}")
            # Return default prediction on parse error
            return {
                'predicted_outcome': 'no',
                'confidence': 50.0,
                'edge_percentage': 0.0,
                'reasoning': f"Parse error: {str(e)}",
                'key_factors': []
            }

    def _parse_text_response(self, text: str) -> Dict:
        """
        Parse unstructured text response (fallback)

        Args:
            text: Response text

        Returns:
            Parsed prediction dictionary
        """
        # Simple heuristic parsing (not ideal, but works as fallback)
        prediction = {
            'predicted_outcome': 'no',
            'confidence': 50.0,
            'edge_percentage': 0.0,
            'reasoning': text[:200],
            'key_factors': []
        }

        text_lower = text.lower()

        # Detect outcome
        if 'recommend yes' in text_lower or 'bet yes' in text_lower:
            prediction['predicted_outcome'] = 'yes'
        elif 'recommend no' in text_lower or 'bet no' in text_lower:
            prediction['predicted_outcome'] = 'no'

        # Try to extract confidence
        if 'confidence:' in text_lower:
            try:
                conf_idx = text_lower.index('confidence:')
                conf_str = text[conf_idx:conf_idx+50]
                conf_val = float(''.join(c for c in conf_str if c.isdigit() or c == '.'))
                prediction['confidence'] = min(conf_val, 100.0)
            except:
                pass

        return prediction

    def _calculate_consensus(self, predictions: List[ModelPrediction]) -> Dict:
        """
        Calculate ensemble consensus from individual predictions

        Args:
            predictions: List of model predictions

        Returns:
            Consensus dictionary
        """
        # Weighted vote for outcome
        yes_weight = sum(
            p.confidence * self.MODEL_WEIGHTS.get(p.model_name, 0.25)
            for p in predictions
            if p.predicted_outcome == 'yes'
        )

        no_weight = sum(
            p.confidence * self.MODEL_WEIGHTS.get(p.model_name, 0.25)
            for p in predictions
            if p.predicted_outcome == 'no'
        )

        # Consensus outcome
        total_weight = yes_weight + no_weight
        if total_weight == 0:
            consensus_outcome = 'no'
            consensus_confidence = 50.0
        else:
            consensus_outcome = 'yes' if yes_weight > no_weight else 'no'
            consensus_confidence = max(yes_weight, no_weight) / total_weight * 100

        # Edge calculation (weighted average)
        consensus_edge = sum(
            p.edge_percentage * self.MODEL_WEIGHTS.get(p.model_name, 0.25)
            for p in predictions
        )

        # Agreement rate (how many models agree with consensus)
        agreement_rate = sum(
            1 for p in predictions
            if p.predicted_outcome == consensus_outcome
        ) / len(predictions)

        # Apply disagreement penalty to confidence
        consensus_confidence *= agreement_rate

        # Aggregate reasoning (combine top insights)
        reasoning_parts = []
        reasoning_parts.append(
            f"Ensemble consensus: {consensus_outcome.upper()} with "
            f"{consensus_confidence:.0f}% confidence ({agreement_rate*100:.0f}% model agreement)."
        )

        if consensus_edge > 5:
            reasoning_parts.append(f"Strong value detected with {consensus_edge:.1f}% edge.")
        elif consensus_edge > 0:
            reasoning_parts.append(f"Moderate value with {consensus_edge:.1f}% edge.")
        else:
            reasoning_parts.append(f"Limited value ({consensus_edge:.1f}% edge).")

        # Find most common key factors
        all_factors = []
        for p in predictions:
            all_factors.extend(p.key_factors)

        from collections import Counter
        top_factors = [
            factor for factor, count in Counter(all_factors).most_common(5)
        ]

        # Generate recommendation
        action = self._generate_recommendation(
            consensus_edge,
            consensus_confidence,
            agreement_rate
        )

        # Calculate stake size (Kelly Criterion)
        stake_pct = self._calculate_stake_size(
            consensus_edge,
            consensus_confidence,
            agreement_rate
        )

        # Assess risk level
        if agreement_rate < 0.6 or consensus_confidence < 60:
            risk_level = 'high'
        elif agreement_rate < 0.8 or consensus_confidence < 75:
            risk_level = 'medium'
        else:
            risk_level = 'low'

        return {
            'outcome': consensus_outcome,
            'confidence': round(consensus_confidence, 2),
            'edge': round(consensus_edge, 2),
            'agreement': round(agreement_rate * 100, 2),
            'reasoning': ' '.join(reasoning_parts),
            'key_factors': top_factors,
            'action': action,
            'stake_pct': stake_pct,
            'risk_level': risk_level
        }

    def _generate_recommendation(
        self,
        edge: float,
        confidence: float,
        agreement: float
    ) -> str:
        """
        Generate betting recommendation

        Args:
            edge: Edge percentage
            confidence: Confidence score
            agreement: Model agreement rate

        Returns:
            Recommendation string ('strong_buy', 'buy', 'hold', 'pass')
        """
        # Require minimum agreement
        if agreement < 0.5:
            return 'pass'

        # Strong buy: high edge + high confidence + high agreement
        if edge > 10 and confidence > 75 and agreement > 0.75:
            return 'strong_buy'

        # Buy: moderate edge + confidence
        if edge > 5 and confidence > 65:
            return 'buy'

        # Hold: small positive edge
        if edge > 0 and confidence > 55:
            return 'hold'

        return 'pass'

    def _calculate_stake_size(
        self,
        edge: float,
        confidence: float,
        agreement: float
    ) -> float:
        """
        Calculate recommended stake size using modified Kelly Criterion

        Args:
            edge: Edge percentage
            confidence: Confidence score
            agreement: Model agreement rate

        Returns:
            Stake percentage (0-10%)
        """
        if edge <= 0 or confidence < 55:
            return 0.0

        # Kelly formula: f = (bp - q) / b
        # where b = odds - 1, p = win probability, q = lose probability

        # Convert edge to probability advantage
        # If we have 10% edge, we think true prob is market_prob * 1.10
        # For simplicity, assume market_prob ≈ 0.5 for most markets

        p = (confidence / 100)  # Our win probability estimate
        q = 1 - p

        # Assume break-even odds for calculation
        b = 1.0

        kelly_fraction = (b * p - q) / b

        # Use fractional Kelly (25% of full Kelly for safety)
        fractional_kelly = kelly_fraction * 0.25

        # Apply agreement penalty (reduce stake if models disagree)
        fractional_kelly *= agreement

        # Cap at 10% of bankroll
        stake_pct = max(0, min(fractional_kelly * 100, 10))

        return round(stake_pct, 2)

    def get_cost_estimate(self, num_markets: int) -> Dict:
        """
        Estimate API costs for analyzing markets

        Args:
            num_markets: Number of markets to analyze

        Returns:
            Cost estimate dictionary
        """
        # Average tokens per analysis
        AVG_INPUT_TOKENS = 2000
        AVG_OUTPUT_TOKENS = 500

        costs = {
            'gpt4': {
                'input_per_1m': 10.0,
                'output_per_1m': 30.0
            },
            'claude': {
                'input_per_1m': 3.0,
                'output_per_1m': 15.0
            },
            'gemini': {
                'input_per_1m': 0.5,
                'output_per_1m': 1.5
            },
            'llama3': {
                'input_per_1m': 0.0,
                'output_per_1m': 0.0
            }
        }

        total_cost = 0.0
        breakdown = {}

        for model in self.models_to_use:
            input_cost = (AVG_INPUT_TOKENS / 1_000_000) * costs[model]['input_per_1m']
            output_cost = (AVG_OUTPUT_TOKENS / 1_000_000) * costs[model]['output_per_1m']
            model_cost = (input_cost + output_cost) * num_markets

            breakdown[model] = round(model_cost, 2)
            total_cost += model_cost

        return {
            'total_cost': round(total_cost, 2),
            'cost_per_market': round(total_cost / num_markets, 4),
            'breakdown': breakdown,
            'num_markets': num_markets,
            'mode': self.mode
        }


# ============================================================================
# Testing
# ============================================================================

async def test_ensemble():
    """Test ensemble prediction"""

    # Sample market
    market = {
        'ticker': 'NFL-KC-BUF-001',
        'title': 'Will the Chiefs beat the Bills by more than 3 points?',
        'yes_price': 0.48,
        'no_price': 0.52,
        'volume': 125000,
        'open_interest': 8500,
        'close_time': '2025-11-10T13:00:00Z'
    }

    # Sample context
    context = {
        'weather': {
            'temp': 38,
            'wind_speed': 12,
            'conditions': 'Partly Cloudy'
        },
        'injuries': {
            'chiefs': ['Travis Kelce (Questionable - Ankle)'],
            'bills': []
        }
    }

    # Test different modes
    for mode in ['cost', 'fast', 'balanced']:
        print(f"\n{'='*80}")
        print(f"Testing {mode.upper()} mode")
        print(f"{'='*80}")

        ensemble = KalshiEnsemble(mode=mode)

        # Get prediction
        try:
            prediction = await ensemble.predict(market, context)

            print(f"\nConsensus Prediction:")
            print(f"  Outcome: {prediction.predicted_outcome.upper()}")
            print(f"  Confidence: {prediction.confidence}%")
            print(f"  Edge: {prediction.edge_percentage}%")
            print(f"  Model Agreement: {prediction.model_agreement}%")
            print(f"  Recommendation: {prediction.recommended_action}")
            print(f"  Stake: {prediction.recommended_stake_pct}%")
            print(f"  Risk Level: {prediction.risk_level}")
            print(f"\nReasoning:")
            print(f"  {prediction.reasoning}")
            print(f"\nKey Factors:")
            for factor in prediction.key_factors:
                print(f"  - {factor}")
            print(f"\nModels Used: {', '.join(prediction.models_used)}")
            print(f"Total Latency: {prediction.total_latency_ms}ms")

            # Individual predictions
            print(f"\nIndividual Model Predictions:")
            for p in prediction.individual_predictions:
                print(f"  {p.model_name}: {p.predicted_outcome.upper()} "
                      f"({p.confidence}% conf, {p.edge_percentage}% edge) "
                      f"[{p.latency_ms}ms]")

        except Exception as e:
            print(f"Error: {e}")

        # Cost estimate
        cost = ensemble.get_cost_estimate(100)
        print(f"\nCost Estimate (100 markets):")
        print(f"  Total: ${cost['total_cost']:.2f}")
        print(f"  Per Market: ${cost['cost_per_market']:.4f}")


if __name__ == "__main__":
    asyncio.run(test_ensemble())
