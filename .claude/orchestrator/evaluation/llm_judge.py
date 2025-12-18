"""
LLM-as-Judge Evaluation System
Uses local Ollama models for code quality evaluation
100% Free - no API costs
"""
from typing import Dict, Any, List, Optional
import logging
import json
import subprocess

logger = logging.getLogger(__name__)


class LLMJudge:
    """
    LLM-based code quality evaluation using local Ollama
    - Evaluates code quality
    - Compares multiple approaches
    - Provides detailed feedback
    """

    def __init__(self, model: str = "qwen2.5-coder:latest"):
        self.model = model
        self.ollama_available = self._check_ollama()
        logger.info(f"LLM Judge initialized with model: {model}")

    def _check_ollama(self) -> bool:
        """Check if Ollama is available"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False

    def _call_ollama(self, prompt: str, max_tokens: int = 1000,
                    temperature: float = 0.3) -> Optional[str]:
        """Call local Ollama model"""
        if not self.ollama_available:
            return None

        try:
            result = subprocess.run(
                ["ollama", "run", self.model],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.error(f"Ollama error: {result.stderr}")
                return None

        except Exception as e:
            logger.error(f"Failed to call Ollama: {e}")
            return None

    def evaluate_code_quality(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Evaluate code quality using LLM"""
        prompt = f"""Evaluate this {language} code quality (1-10 scale):

CODE:
```{language}
{code}
```

Rate: Correctness, Readability, Maintainability, Performance, Security

JSON only:
{{"correctness": <1-10>, "readability": <1-10>, "maintainability": <1-10>, "performance": <1-10>, "security": <1-10>, "overall": <1-10>, "summary": "<brief>", "improvements": ["<tip>"]}}"""

        if not self.ollama_available:
            return self._rule_based_evaluation(code, language)

        response = self._call_ollama(prompt, max_tokens=500, temperature=0.2)

        if response:
            try:
                json_match = response[response.find('{'):response.rfind('}')+1]
                evaluation = json.loads(json_match)
                evaluation["evaluated_by"] = "llm"
                return evaluation
            except Exception as e:
                logger.error(f"Failed to parse LLM response: {e}")
                return self._rule_based_evaluation(code, language)
        else:
            return self._rule_based_evaluation(code, language)

    def _rule_based_evaluation(self, code: str, language: str) -> Dict[str, Any]:
        """Fallback rule-based evaluation"""
        lines = code.split('\n')
        score = 5

        if len(lines) < 100: score += 1
        if any('def ' in line or 'class ' in line for line in lines): score += 1
        if any('#' in line for line in lines): score += 1

        return {
            "correctness": score, "readability": score, "maintainability": score,
            "performance": score, "security": score, "overall": score,
            "summary": "Rule-based evaluation (Ollama not available)",
            "improvements": ["Install Ollama for AI-powered evaluation"],
            "evaluated_by": "rules"
        }

    def compare_approaches(self, approach_a: str, approach_b: str,
                          task_description: str) -> Dict[str, Any]:
        """Compare two code approaches"""
        prompt = f"""Compare for task: {task_description}

A: ```{approach_a}```
B: ```{approach_b}```

JSON: {{"winner": "A/B/tie", "confidence": <0-1>, "reasoning": "<why>", "approach_a_score": <1-10>, "approach_b_score": <1-10>}}"""

        if not self.ollama_available:
            return {"winner": "tie", "confidence": 0.5, "reasoning": "Ollama unavailable"}

        response = self._call_ollama(prompt, max_tokens=300, temperature=0.2)
        if response:
            try:
                json_match = response[response.find('{'):response.rfind('}')+1]
                return json.loads(json_match)
            except: pass
        return {"winner": "tie", "confidence": 0.5}


_judge_instance: Optional[LLMJudge] = None

def get_llm_judge(model: str = "qwen2.5-coder:latest") -> LLMJudge:
    global _judge_instance
    if _judge_instance is None:
        _judge_instance = LLMJudge(model)
    return _judge_instance
