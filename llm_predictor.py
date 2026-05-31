"""LLM-enhanced match predictor using Hugging Face transformers."""

import logging
import sys
from typing import Optional

logger = logging.getLogger(__name__)


class LLMPredictor:
    def __init__(self, model_name: str = "microsoft/Phi-3-mini-4k-instruct"):
        self.model_name = model_name
        self.pipeline = None
        self._loaded = False

    def load(self) -> bool:
        if self._loaded:
            return True
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
            import torch

            logger.info(f"Loading LLM model: {self.model_name}")
            tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
            model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True,
            )
            self.pipeline = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=150,
                temperature=0.3,
                do_sample=True,
                top_p=0.9,
            )
            self._loaded = True
            return True
        except Exception as e:
            logger.warning(f"Could not load LLM model: {e}")
            return False

    def predict_match(self, team_a: str, team_a_strength: float,
                      team_b: str, team_b_strength: float,
                      context: Optional[str] = None) -> Optional[dict]:
        if not self._loaded:
            if not self.load():
                return None

        prompt = self._build_prompt(team_a, team_a_strength, team_b, team_b_strength, context)
        try:
            result = self.pipeline(prompt, return_full_text=False)
            text = result[0]["generated_text"]
            return self._parse_response(text, team_a, team_b)
        except Exception as e:
            logger.warning(f"LLM prediction failed: {e}")
            return None

    def predict_group(self, group_name: str, teams: list) -> Optional[list]:
        if not self._loaded:
            if not self.load():
                return None

        prompt = self._build_group_prompt(group_name, teams)
        try:
            result = self.pipeline(prompt, return_full_text=False)
            text = result[0]["generated_text"]
            return self._parse_group_response(text, teams)
        except Exception as e:
            logger.warning(f"LLM group prediction failed: {e}")
            return None

    def _build_prompt(self, team_a: str, str_a: float,
                      team_b: str, str_b: float,
                      context: Optional[str] = None) -> str:
        exp_a = 1.0 / (1.0 + 10 ** ((str_b - str_a) / 600.0))
        exp_b = 1.0 - exp_a
        ctx = f"\nContext: {context}" if context else ""

        return (
            f"<|system|>\nYou are a football analytics expert. Predict match outcomes "
            f"based on team strength ratings. Return ONLY valid JSON.\n<|end|>\n"
            f"<|user|>\nFIFA World Cup 2026 match:\n"
            f"{team_a} (strength: {str_a:.1f}, win prob: {exp_a:.1%}) vs "
            f"{team_b} (strength: {str_b:.1f}, win prob: {exp_b:.1%}){ctx}\n\n"
            f"Predict: winner, scoreline, and brief reasoning as JSON:\n"
            f'{{"winner": "...", "score": "X-Y", "reasoning": "..."}}\n<|end|>\n<|assistant|>\n'
        )

    def _build_group_prompt(self, group_name: str, teams: list) -> str:
        lines = [f"<|system|>\nYou are a football analytics expert. Predict group standings "
                 f"for World Cup 2026 Group {group_name}. Return ONLY valid JSON.\n<|end|>\n"
                 f"<|user|>\nGroup {group_name} teams:"]
        for t in teams:
            lines.append(f"- {t.name} (FIFA: {t.fifa_points:.0f}, conf: {t.confederation})")
        lines.append("\nPredict final group standings (1st to 4th) with points as JSON:")
        lines.append('[{"team": "...", "position": 1, "points": 7}, ...]')
        lines.append("<|end|>\n<|assistant|>\n")
        return "\n".join(lines)

    def _parse_response(self, text: str, team_a: str, team_b: str) -> Optional[dict]:
        import json
        import re

        try:
            json_match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return {
                    "winner": data.get("winner"),
                    "score": data.get("score"),
                    "reasoning": data.get("reasoning", ""),
                }
        except Exception:
            pass

        try:
            lines = text.strip().split("\n")
            for line in lines:
                if ":" in line:
                    parts = line.split(":", 1)
                    key = parts[0].strip().lower()
                    val = parts[1].strip()
                    if "winner" in key:
                        return {"winner": val, "score": "?", "reasoning": "parsed from output"}
        except Exception:
            pass

        return {"winner": team_a if "win" in text.lower() else team_b,
                "score": "?", "reasoning": "fallback parse"}

    def _parse_group_response(self, text: str, teams: list) -> Optional[list]:
        import json
        import re

        try:
            json_match = re.search(r"\[.*\]", text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                if isinstance(data, list) and len(data) == 4:
                    return data
        except Exception:
            pass
        return None
