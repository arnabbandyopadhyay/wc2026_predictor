"""RAG-enhanced LLM predictor using Gemini/OpenAI/Transformers."""

import json
import logging
import os
import re
from dataclasses import dataclass
from typing import Optional, Dict

from data import get_team_data, get_h2h, HOST_NATIONS
from scraper import scraper

logger = logging.getLogger(__name__)


@dataclass
class LLMPrediction:
    winner: str
    score: str
    win_prob_a: float
    win_prob_b: float
    reasoning: str
    confidence: float
    model_used: str = ""


class RAGPredictor:
    def __init__(self):
        self.model_source = self._detect_available_model()
        self._initialized = False
        self._client = None

    def _detect_available_model(self) -> str:
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))
            _ = genai.list_models()
            if os.environ.get("GEMINI_API_KEY"):
                return "gemini"
        except Exception:
            pass

        try:
            import openai
            if os.environ.get("OPENAI_API_KEY"):
                return "openai"
        except Exception:
            pass

        try:
            from transformers import pipeline
            return "transformers"
        except Exception:
            pass

        return "none"

    def initialize(self) -> bool:
        if self._initialized:
            return True

        if self.model_source == "gemini":
            try:
                import google.generativeai as genai
                genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))
                self._client = genai.GenerativeModel("gemini-1.5-flash")
                self._initialized = True
                return True
            except Exception as e:
                logger.warning(f"Gemini init failed: {e}")
                self.model_source = "transformers"

        if self.model_source == "openai":
            try:
                import openai
                self._client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
                self._initialized = True
                return True
            except Exception as e:
                logger.warning(f"OpenAI init failed: {e}")
                self.model_source = "transformers"

        if self.model_source == "transformers":
            try:
                from transformers import pipeline
                self._client = pipeline(
                    "text-generation",
                    model="microsoft/phi-3-mini-4k-instruct",
                    max_new_tokens=300,
                    temperature=0.2,
                    do_sample=True,
                )
                self._initialized = True
                return True
            except Exception as e:
                logger.warning(f"Transformers init failed: {e}")
                self.model_source = "none"
                return False

        return False

    def _build_rag_context(self, team_a: str, team_b: str) -> Dict:
        td_a = get_team_data(team_a)
        td_b = get_team_data(team_b)
        h2h = get_h2h(team_a, team_b)
        news_a = scraper.extract_team_news(team_a)
        news_b = scraper.extract_team_news(team_b)
        form_a = scraper.get_form_ratings(team_a)
        form_b = scraper.get_form_ratings(team_b)
        squad_values = scraper.get_squad_value()

        return {
            "team_a": {
                "name": team_a,
                "rank": td_a.fifa_rank,
                "points": round(td_a.fifa_points, 1),
                "confederation": td_a.confederation,
                "attack_strength": td_a.attack,
                "defense_strength": td_a.defense,
                "wc_appearances": td_a.appearances,
                "best_result": td_a.best_result,
                "form": form_a["last_10"],
                "avg_goals_scored": form_a["avg_goals_scored"],
                "avg_goals_conceded": form_a["avg_goals_conceded"],
                "squad_value": squad_values.get(team_a, 0.5),
                "recent_news": news_a.headlines[:3],
                "injuries": news_a.injuries,
                "is_host": team_a in HOST_NATIONS,
            },
            "team_b": {
                "name": team_b,
                "rank": td_b.fifa_rank,
                "points": round(td_b.fifa_points, 1),
                "confederation": td_b.confederation,
                "attack_strength": td_b.attack,
                "defense_strength": td_b.defense,
                "wc_appearances": td_b.appearances,
                "best_result": td_b.best_result,
                "form": form_b["last_10"],
                "avg_goals_scored": form_b["avg_goals_scored"],
                "avg_goals_conceded": form_b["avg_goals_conceded"],
                "squad_value": squad_values.get(team_b, 0.5),
                "recent_news": news_b.headlines[:3],
                "injuries": news_b.injuries,
                "is_host": team_b in HOST_NATIONS,
            },
            "head_to_head": {
                "total_matches": h2h["total"],
                f"{team_a}_wins": h2h[f"{team_a}_wins"],
                f"{team_b}_wins": h2h[f"{team_b}_wins"],
                "draws": h2h["draws"],
                f"{team_a}_goals": h2h[f"{team_a}_goals"],
                f"{team_b}_goals": h2h[f"{team_b}_goals"],
            },
        }

    def _build_prompt(self, ctx: Dict) -> str:
        a = ctx["team_a"]
        b = ctx["team_b"]
        h = ctx["head_to_head"]

        prompt = f"""You are a world-class football analyst predicting a 2026 FIFA World Cup match.

MATCH: {a['name']} vs {b['name']}

TEAM A: {a['name']}
- FIFA Ranking: #{a['rank']} ({a['points']} pts)
- Confederation: {a['confederation']}
- Attack Strength: {a['attack_strength']} / Defense Strength: {a['defense_strength']}
- WC Appearances: {a['wc_appearances']}, Best: {a['best_result']}
- Recent Form (last 10): {a['form']}
- Avg Goals Scored: {a['avg_goals_scored']}, Conceded: {a['avg_goals_conceded']}
- Squad Value Index: {a['squad_value']}
- Host Nation: {'YES' if a['is_host'] else 'No'}
- Latest News: {'; '.join(a['recent_news'])}
- Injuries: {'; '.join(a['injuries']) if a['injuries'] else 'None reported'}

TEAM B: {b['name']}
- FIFA Ranking: #{b['rank']} ({b['points']} pts)
- Confederation: {b['confederation']}
- Attack Strength: {b['attack_strength']} / Defense Strength: {b['defense_strength']}
- WC Appearances: {b['wc_appearances']}, Best: {b['best_result']}
- Recent Form (last 10): {b['form']}
- Avg Goals Scored: {b['avg_goals_scored']}, Conceded: {b['avg_goals_conceded']}
- Squad Value Index: {b['squad_value']}
- Host Nation: {'YES' if b['is_host'] else 'No'}
- Latest News: {'; '.join(b['recent_news'])}
- Injuries: {'; '.join(b['injuries']) if b['injuries'] else 'None reported'}

HEAD-TO-HEAD HISTORY ({h['total_matches']} matches):
- {a['name']} wins: {h[a['name'] + '_wins']}, {b['name']} wins: {h[b['name'] + '_wins']}, Draws: {h['draws']}
- Goals: {a['name']} {h[a['name'] + '_goals']} - {h[b['name'] + '_goals']} {b['name']}

Analyze this match considering: current form, squad quality, historical data, tactical matchups, injury impacts, and host advantage.

Respond with ONLY valid JSON:
{{"winner": "team_name", "score": "X-Y", "win_probability_a": 0-100, "win_probability_b": 0-100, "confidence": 0-100, "reasoning": "brief 2-sentence analysis"}}"""

        return prompt

    def predict(self, team_a: str, team_b: str) -> Optional[LLMPrediction]:
        if not self._initialized:
            if not self.initialize():
                return None

        ctx = self._build_rag_context(team_a, team_b)
        prompt = self._build_prompt(ctx)

        try:
            raw_output = self._call_llm(prompt)
            result = self._parse_response(raw_output, team_a, team_b)
            if result:
                result.model_used = self.model_source
            return result
        except Exception as e:
            logger.warning(f"LLM prediction failed: {e}")
            return None

    def _call_llm(self, prompt: str) -> str:
        if self.model_source == "gemini":
            response = self._client.generate_content(prompt)
            return response.text

        elif self.model_source == "openai":
            response = self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=300,
            )
            return response.choices[0].message.content

        elif self.model_source == "transformers":
            result = self._client(prompt, return_full_text=False)
            return result[0]["generated_text"]

        return ""

    def _parse_response(self, text: str, team_a: str, team_b: str) -> Optional[LLMPrediction]:
        if not text:
            return None

        try:
            json_match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
            if not json_match:
                return None

            data = json.loads(json_match.group())

            winner = data.get("winner", "")
            score = data.get("score", "0-0")
            prob_a = float(data.get("win_probability_a", 50))
            prob_b = float(data.get("win_probability_b", 50))
            confidence = float(data.get("confidence", 50))
            reasoning = data.get("reasoning", "")

            return LLMPrediction(
                winner=winner,
                score=score,
                win_prob_a=prob_a / 100.0 if prob_a > 1 else prob_a,
                win_prob_b=prob_b / 100.0 if prob_b > 1 else prob_b,
                reasoning=reasoning,
                confidence=confidence / 100.0 if confidence > 1 else confidence,
            )
        except Exception as e:
            logger.debug(f"Failed to parse LLM response: {e}")
            return None


rag_predictor = RAGPredictor()
