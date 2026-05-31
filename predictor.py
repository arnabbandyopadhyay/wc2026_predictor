"""Ensemble predictor combining Poisson statistical model + RAG LLM."""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from poisson import predict_match_poisson, predict_match_enhanced, PoissonPrediction, predict_group_poisson
from llm_rag import rag_predictor, LLMPrediction
from data import get_h2h, get_team_data, HOST_NATIONS
from scraper import scraper

logger = logging.getLogger(__name__)


@dataclass
class EnsemblePrediction:
    team_a: str
    team_b: str
    poisson_prediction: PoissonPrediction
    llm_prediction: Optional[LLMPrediction]
    win_prob_a: float
    win_prob_b: float
    draw_prob: float
    predicted_score: Tuple[int, int]
    confidence: float
    factors: Dict[str, float]
    model_blend: str
    h2h: dict
    home_advantage: float


def predict(team_a: str, team_b: str,
            use_enhanced: bool = True) -> EnsemblePrediction:
    is_neutral = not (team_a in HOST_NATIONS or team_b in HOST_NATIONS)

    if use_enhanced:
        poisson = predict_match_enhanced(team_a, team_b, is_neutral=is_neutral, scraper_instance=scraper)
    else:
        poisson = predict_match_poisson(team_a, team_b, is_neutral=is_neutral)

    llm = rag_predictor.predict(team_a, team_b)

    h2h = get_h2h(team_a, team_b)

    if llm and llm.confidence > 0.3:
        llm_weight = min(0.35, llm.confidence * 0.4)
        poisson_weight = 1.0 - llm_weight

        if llm.win_prob_a > 0:
            combined_a = poisson.win_prob_a * poisson_weight + llm.win_prob_a * llm_weight
        else:
            combined_a = poisson.win_prob_a * poisson_weight
            if llm.winner == team_a:
                combined_a += 0.05 * llm_weight * 10
            elif llm.winner == team_b:
                combined_a -= 0.05 * llm_weight * 10

        combined_a = max(0.05, min(0.95, combined_a))
        combined_b = 1.0 - combined_a
        draw = 0.0

        if abs(combined_a - 0.5) < 0.15:
            draw = 0.2 * (1 - abs(combined_a - 0.5) * 2)
            combined_a -= draw * combined_a / (combined_a + combined_b)
            combined_b -= draw * combined_b / (combined_a + combined_b)

        model_blend = f"Poisson({poisson_weight:.0%}) + LLM({llm_weight:.0%})"

        llm_score = llm.score.split("-") if llm.score and "-" in llm.score else None
        if llm_score:
            try:
                pred_score = (int(llm_score[0]), int(llm_score[1]))
            except (ValueError, IndexError):
                pred_score = poisson.predicted_score
        else:
            pred_score = poisson.predicted_score
    else:
        combined_a = poisson.win_prob_a
        combined_b = poisson.win_prob_b
        draw = poisson.draw_prob
        model_blend = "Enhanced Poisson (LLM unavailable)" if use_enhanced else "Poisson (LLM unavailable)"
        pred_score = poisson.predicted_score

    confidence = poisson.confidence
    if llm:
        confidence = min(0.95, (poisson.confidence * 0.6 + llm.confidence * 0.4))

    factors = {
        "poisson_attack_a": poisson.lambda_a,
        "poisson_attack_b": poisson.lambda_b,
        "h2h_advantage": (h2h[f"{team_a}_wins"] - h2h[f"{team_b}_wins"]) / max(h2h["total"], 1),
        "home_advantage": poisson.home_advantage,
    }

    if use_enhanced and poisson.factor_breakdown:
        for k, v in poisson.factor_breakdown.items():
            factors[f"factor_{k}"] = v

    if llm:
        factors["llm_confidence"] = llm.confidence

    return EnsemblePrediction(
        team_a=team_a, team_b=team_b,
        poisson_prediction=poisson,
        llm_prediction=llm,
        win_prob_a=round(combined_a, 4),
        win_prob_b=round(combined_b, 4),
        draw_prob=round(draw, 4),
        predicted_score=pred_score,
        confidence=round(confidence, 2),
        factors=factors,
        model_blend=model_blend,
        h2h=h2h,
        home_advantage=poisson.home_advantage,
    )


def predict_group(group_name: str, teams: list) -> list:
    return predict_group_poisson(group_name, teams)
