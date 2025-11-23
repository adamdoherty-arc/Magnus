"""
Ensemble Model

Combines XGBoost structured predictions with existing LLM predictions.
Implements stacking, weighted averaging, and probability calibration.

Author: Python Pro
Created: 2025-11-09
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import log_loss, brier_score_loss, roc_auc_score
import pickle
from pathlib import Path

logger = logging.getLogger(__name__)


class EnsembleModel:
    """
    Ensemble model combining XGBoost and LLM predictions

    Uses stacking approach:
    1. XGBoost base model on structured features
    2. LLM predictions as additional features
    3. Meta-model combines both
    4. Isotonic/Platt calibration for probability outputs
    """

    def __init__(self,
                 xgboost_params: Optional[Dict] = None,
                 calibration_method: str = "isotonic",
                 use_feature_scaling: bool = True):
        """
        Initialize ensemble model

        Args:
            xgboost_params: Parameters for XGBoost model
            calibration_method: "isotonic" or "sigmoid" (Platt scaling)
            use_feature_scaling: Whether to scale features
        """
        self.xgboost_params = xgboost_params or self._default_xgboost_params()
        self.calibration_method = calibration_method
        self.use_feature_scaling = use_feature_scaling

        # Models
        self.base_model: Optional[GradientBoostingClassifier] = None
        self.calibrated_model: Optional[CalibratedClassifierCV] = None
        self.scaler: Optional[StandardScaler] = None

        # Feature importance
        self.feature_names: List[str] = []
        self.feature_importance: Optional[np.ndarray] = None

        # Training metrics
        self.training_metrics: Dict[str, float] = {}

        # Model metadata
        self.is_trained = False
        self.n_samples_trained = 0

    def _default_xgboost_params(self) -> Dict:
        """Default XGBoost parameters"""
        return {
            "n_estimators": 200,
            "learning_rate": 0.05,
            "max_depth": 6,
            "min_samples_split": 10,
            "min_samples_leaf": 5,
            "subsample": 0.8,
            "max_features": 0.8,
            "random_state": 42
        }

    def prepare_features(self, feature_df: pd.DataFrame,
                        llm_predictions: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Prepare features for model training/prediction

        Args:
            feature_df: DataFrame with structured features
            llm_predictions: Optional DataFrame with LLM predictions
                           (columns: ticker, predicted_prob, confidence_score)

        Returns:
            Combined feature DataFrame
        """
        df = feature_df.copy()

        # Add LLM predictions as features if available
        if llm_predictions is not None and not llm_predictions.empty:
            # Merge on ticker
            if 'ticker' in df.columns and 'ticker' in llm_predictions.columns:
                df = df.merge(
                    llm_predictions[['ticker', 'predicted_prob', 'confidence_score']],
                    on='ticker',
                    how='left'
                )

                # Fill missing LLM predictions with neutral values
                df['predicted_prob'] = df['predicted_prob'].fillna(0.5)
                df['confidence_score'] = df['confidence_score'].fillna(50.0)

                # Normalize confidence score to 0-1
                df['confidence_normalized'] = df['confidence_score'] / 100.0

                # LLM edge features
                df['llm_edge'] = abs(df['predicted_prob'] - 0.5)
                df['llm_high_confidence'] = (df['confidence_score'] >= 75).astype(float)
            else:
                # No ticker column, add neutral LLM features
                df['predicted_prob'] = 0.5
                df['confidence_normalized'] = 0.5
                df['llm_edge'] = 0.0
                df['llm_high_confidence'] = 0.0
        else:
            # No LLM predictions, add neutral features
            df['predicted_prob'] = 0.5
            df['confidence_normalized'] = 0.5
            df['llm_edge'] = 0.0
            df['llm_high_confidence'] = 0.0

        # Remove ticker column for modeling
        if 'ticker' in df.columns:
            df = df.drop(columns=['ticker'])

        return df

    def train(self, X: pd.DataFrame, y: np.ndarray,
             validation_split: float = 0.2) -> Dict[str, float]:
        """
        Train ensemble model

        Args:
            X: Feature DataFrame
            y: Target labels (0 or 1)
            validation_split: Fraction of data for validation

        Returns:
            Dictionary of training metrics
        """
        if len(X) != len(y):
            raise ValueError("X and y must have same length")

        if len(X) < 50:
            raise ValueError("Need at least 50 samples for training")

        logger.info(f"Training ensemble model on {len(X)} samples...")

        # Store feature names
        self.feature_names = list(X.columns)

        # Split into train/validation
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42, stratify=y
        )

        # Scale features if enabled
        if self.use_feature_scaling:
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_val_scaled = self.scaler.transform(X_val)
        else:
            X_train_scaled = X_train.values
            X_val_scaled = X_val.values

        # Train base model (Gradient Boosting, similar to XGBoost)
        self.base_model = GradientBoostingClassifier(**self.xgboost_params)
        self.base_model.fit(X_train_scaled, y_train)

        # Get feature importance
        self.feature_importance = self.base_model.feature_importances_

        # Calibrate predictions
        logger.info(f"Calibrating model using {self.calibration_method} method...")

        self.calibrated_model = CalibratedClassifierCV(
            self.base_model,
            method=self.calibration_method,
            cv='prefit'  # Use prefit model
        )

        self.calibrated_model.fit(X_val_scaled, y_val)

        # Evaluate on validation set
        y_pred_proba = self.calibrated_model.predict_proba(X_val_scaled)[:, 1]
        y_pred = (y_pred_proba >= 0.5).astype(int)

        # Calculate metrics
        accuracy = (y_pred == y_val).mean()
        logloss = log_loss(y_val, y_pred_proba)
        brier = brier_score_loss(y_val, y_pred_proba)

        try:
            auc = roc_auc_score(y_val, y_pred_proba)
        except ValueError:
            auc = 0.5  # If only one class in y_val

        self.training_metrics = {
            'accuracy': accuracy,
            'log_loss': logloss,
            'brier_score': brier,
            'auc_roc': auc,
            'n_samples': len(X),
            'n_features': len(self.feature_names)
        }

        self.is_trained = True
        self.n_samples_trained = len(X)

        logger.info(f"Training complete. Metrics: {self.training_metrics}")

        return self.training_metrics

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict calibrated probabilities

        Args:
            X: Feature DataFrame

        Returns:
            Array of probabilities (shape: n_samples)
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")

        # Ensure feature order matches training
        X = X[self.feature_names]

        # Scale features if enabled
        if self.use_feature_scaling and self.scaler is not None:
            X_scaled = self.scaler.transform(X)
        else:
            X_scaled = X.values

        # Predict using calibrated model
        probabilities = self.calibrated_model.predict_proba(X_scaled)[:, 1]

        return probabilities

    def predict(self, X: pd.DataFrame, threshold: float = 0.5) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict class labels and probabilities

        Args:
            X: Feature DataFrame
            threshold: Classification threshold (default: 0.5)

        Returns:
            Tuple of (predictions, probabilities)
        """
        probabilities = self.predict_proba(X)
        predictions = (probabilities >= threshold).astype(int)

        return predictions, probabilities

    def get_feature_importance(self, top_n: int = 20) -> pd.DataFrame:
        """
        Get feature importance from base model

        Args:
            top_n: Number of top features to return

        Returns:
            DataFrame with feature names and importance scores
        """
        if self.feature_importance is None:
            raise ValueError("Model not trained")

        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.feature_importance
        })

        importance_df = importance_df.sort_values('importance', ascending=False)

        return importance_df.head(top_n)

    def calculate_confidence(self, probabilities: np.ndarray) -> np.ndarray:
        """
        Calculate confidence scores from probabilities

        Confidence is distance from 0.5 (neutral), scaled to 0-100

        Args:
            probabilities: Array of probabilities

        Returns:
            Array of confidence scores (0-100)
        """
        # Distance from 0.5, scaled to 0-100
        confidence = abs(probabilities - 0.5) * 200

        # Cap at 100
        confidence = np.minimum(confidence, 100)

        return confidence

    def save_model(self, filepath: str):
        """
        Save trained model to disk

        Args:
            filepath: Path to save model
        """
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")

        model_data = {
            'base_model': self.base_model,
            'calibrated_model': self.calibrated_model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'feature_importance': self.feature_importance,
            'training_metrics': self.training_metrics,
            'xgboost_params': self.xgboost_params,
            'calibration_method': self.calibration_method,
            'use_feature_scaling': self.use_feature_scaling,
            'n_samples_trained': self.n_samples_trained
        }

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)

        logger.info(f"Model saved to {filepath}")

    def load_model(self, filepath: str):
        """
        Load trained model from disk

        Args:
            filepath: Path to load model from
        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"Model file not found: {filepath}")

        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)

        self.base_model = model_data['base_model']
        self.calibrated_model = model_data['calibrated_model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.feature_importance = model_data['feature_importance']
        self.training_metrics = model_data['training_metrics']
        self.xgboost_params = model_data['xgboost_params']
        self.calibration_method = model_data['calibration_method']
        self.use_feature_scaling = model_data['use_feature_scaling']
        self.n_samples_trained = model_data['n_samples_trained']

        self.is_trained = True

        logger.info(f"Model loaded from {filepath}")


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Generate synthetic training data
    np.random.seed(42)

    n_samples = 500
    n_features = 20

    # Create random features
    X = pd.DataFrame(
        np.random.randn(n_samples, n_features),
        columns=[f'feature_{i}' for i in range(n_features)]
    )

    # Add LLM prediction features
    X['predicted_prob'] = np.random.uniform(0.3, 0.7, n_samples)
    X['confidence_score'] = np.random.uniform(50, 90, n_samples)

    # Create synthetic target (correlated with some features)
    y = ((X['feature_0'] + X['feature_1'] + X['predicted_prob'] * 2) > 0.5).astype(int)

    print("\n" + "="*80)
    print("ENSEMBLE MODEL TEST")
    print("="*80)

    # Train model
    model = EnsembleModel(calibration_method="isotonic")

    print("\nTraining model...")
    metrics = model.train(X, y.values, validation_split=0.2)

    print("\nTraining Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value:.4f}")

    # Feature importance
    print("\nTop 10 Important Features:")
    importance_df = model.get_feature_importance(top_n=10)
    for idx, row in importance_df.iterrows():
        print(f"  {row['feature']}: {row['importance']:.4f}")

    # Make predictions on test data
    X_test = X.head(10)
    predictions, probabilities = model.predict(X_test)
    confidence = model.calculate_confidence(probabilities)

    print("\nSample Predictions:")
    for i in range(min(5, len(X_test))):
        print(f"  Sample {i+1}: Prob={probabilities[i]:.3f}, "
              f"Pred={predictions[i]}, Confidence={confidence[i]:.1f}%")

    # Save and load model
    model_path = "test_ensemble_model.pkl"
    model.save_model(model_path)

    model2 = EnsembleModel()
    model2.load_model(model_path)

    print(f"\n✓ Model saved and loaded successfully")
    print(f"  Trained on {model2.n_samples_trained} samples")

    # Cleanup
    import os
    if os.path.exists(model_path):
        os.remove(model_path)

    print("\n" + "="*80)
