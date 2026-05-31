"""Advanced statistical model for match prediction."""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from data import FIFA_RANKINGS_APRIL_2026, get_team_data
from scraper import scraper


@dataclass
class MatchPrediction:
    team_a: str
    team_b: str
    win_prob_a: float
    win_prob_b: float
    draw_prob: float
    predicted_score: Tuple[int, int]
    confidence: float
    factors: Dict[str, float]


class StatsModel:
    def __init__(self):
        self.h2h_db = scraper.h2h_db
        self.form_cache: Dict[str, dict] = {}

    def predict(self, team_a: str, team_b: str,
                neutral_ground: bool = True) -> MatchPrediction:
        factors = {}

        # 1. Elo rating prediction
        td_a, td_b = get_team_data(team_a), get_team_data(team_b)
        str_a, str_b = td_a.effective_strength(), td_b.effective_strength()
        elo_exp_a = 1.0 / (1.0 + 10.0 ** ((str_b - str_a) / 600.0))
        elo_exp_b = 1.0 - elo_exp_a
        factors["elo"] = elo_exp_a - elo_exp_b

        # 2. Recent form analysis
        form_a = scraper.get_form_ratings(team_a)
        form_b = scraper.get_form_ratings(team_b)
        form_a_score = self._form_to_score(form_a["last_10"])
        form_b_score = self._form_to_score(form_b["last_10"])
        factors["form"] = (form_a_score - form_b_score) * 0.05

        # 3. Goals scored/conceded differential
        gd_a = form_a["avg_goals_scored"] - form_a["avg_goals_conceded"]
        gd_b = form_b["avg_goals_scored"] - form_b["avg_goals_conceded"]
        factors["goal_diff"] = (gd_a - gd_b) * 0.03

        # 4. Squad value / quality depth
        squad_values = scraper.get_squad_value()
        sv_a = squad_values.get(team_a, 0.5)
        sv_b = squad_values.get(team_b, 0.5)
        factors["squad_value"] = (sv_a - sv_b) * 0.08

        # 5. Head-to-head history
        h2h = scraper.h2h_db.get_h2h(team_a, team_b)
        if h2h["total"] > 0:
            a_wins = h2h.get(f"{team_a}_wins", 0)
            b_wins = h2h.get(f"{team_b}_wins", 0)
            total = h2h["total"]
            h2h_factor = ((a_wins - b_wins) / total) * 0.06
            factors["h2h"] = h2h_factor
        else:
            factors["h2h"] = 0.0

        # 6. Media consensus / expert opinion
        try:
            consensus = scraper.get_analyst_consensus(team_a, team_b)
            media_a = consensus["team_a_positive_ratio"]
            media_b = consensus["team_b_positive_ratio"]
            factors["media"] = (media_a - media_b) * 0.04
        except Exception:
            factors["media"] = 0.0

        # 7. Confederation strength modifier
        conf_strength = {
            "UEFA": 0.03, "CONMEBOL": 0.02, "CAF": -0.01,
            "AFC": -0.02, "CONCACAF": -0.01, "OFC": -0.04,
        }
        factors["conf"] = (conf_strength.get(td_a.confederation, 0)
                          - conf_strength.get(td_b.confederation, 0))

        # 8. Tournament experience
        exp_a = min(td_a.appearances / 10.0, 1.0)
        exp_b = min(td_b.appearances / 10.0, 1.0)
        factors["experience"] = (exp_a - exp_b) * 0.03

        # Combine all factors into final probability adjustment
        total_adjustment = sum(factors.values())
        raw_prob_a = elo_exp_a + total_adjustment
        raw_prob_a = max(0.05, min(0.95, raw_prob_a))

        # Normalize to get probabilities
        win_prob_a = raw_prob_a
        win_prob_b = 1.0 - raw_prob_a
        draw_prob = 0.0

        # Adjust for draws in close matches
        if abs(win_prob_a - 0.5) < 0.15:
            draw_prob = 0.22 * (1 - abs(win_prob_a - 0.5) * 2)
            win_prob_a -= draw_prob * win_prob_a / (win_prob_a + win_prob_b)
            win_prob_b -= draw_prob * win_prob_b / (win_prob_a + win_prob_b)

        # Predicted score
        expected_goals_a = form_a["avg_goals_scored"] * (0.8 + 0.4 * win_prob_a)
        expected_goals_b = form_b["avg_goals_scored"] * (0.8 + 0.4 * win_prob_b)

        pred_goals_a = max(0, round(expected_goals_a))
        pred_goals_b = max(0, round(expected_goals_b))

        # Confidence based on how many factors align
        confidence = self._calc_confidence(win_prob_a, total_adjustment, factors)

        return MatchPrediction(
            team_a=team_a, team_b=team_b,
            win_prob_a=round(win_prob_a, 4),
            win_prob_b=round(win_prob_b, 4),
            draw_prob=round(draw_prob, 4),
            predicted_score=(pred_goals_a, pred_goals_b),
            confidence=confidence,
            factors={k: round(v, 4) for k, v in factors.items()},
        )

    def _form_to_score(self, form_str: str) -> float:
        score = 0.0
        for i, c in enumerate(form_str[:10]):
            if c == "W":
                score += 3.0
            elif c == "D":
                score += 1.0
            weight = 1.0 + (10 - i) * 0.1
            score += (3.0 if c == "W" else 1.0 if c == "D" else 0.0) * weight
        return score / (len(form_str[:10]) or 1)

    def _calc_confidence(self, prob: float, adjustment: float,
                         factors: Dict) -> float:
        base = abs(prob - 0.5) * 2
        factor_agreement = 0.0
        pos_count = sum(1 for v in factors.values() if v > 0)
        neg_count = sum(1 for v in factors.values() if v < 0)
        total = pos_count + neg_count or 1
        factor_agreement = abs(pos_count - neg_count) / total
        return round(min(1.0, base * 0.6 + factor_agreement * 0.4), 2)

    def get_goal_distribution(self, team: str) -> Dict[str, float]:
        form = scraper.get_form_ratings(team)
        avg_f = form["avg_goals_scored"]
        avg_a = form["avg_goals_conceded"]
        return {
            "avg_scored": avg_f,
            "avg_conceded": avg_a,
            "clean_sheet_prob": max(0, min(1, 0.4 - avg_a * 0.1)),
            "score_2plus_prob": max(0, min(1, avg_f * 0.3)),
        }

    def predict_group(self, group_name: str, teams: List[str]) -> List[dict]:
        results = []
        for i in range(len(teams)):
            pts = 0
            gf = 0
            ga = 0
            for j in range(len(teams)):
                if i == j:
                    continue
                pred = self.predict(teams[i], teams[j])
                if pred.win_prob_a > 0.5 and pred.team_a == teams[i]:
                    pts += 3
                elif pred.win_prob_b > 0.5 and pred.team_b == teams[i]:
                    pts += 0
                else:
                    pts += 1
                gf += pred.predicted_score[0] if pred.team_a == teams[i] else pred.predicted_score[1]
                ga += pred.predicted_score[1] if pred.team_a == teams[i] else pred.predicted_score[0]
            results.append({"team": teams[i], "points": pts, "gf": gf, "ga": ga, "gd": gf - ga})
        results.sort(key=lambda x: (-x["points"], -x["gd"], -x["gf"]))
        return results


stats_model = StatsModel()
