"""Poisson goal-scoring model for football match prediction."""

import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from data import (
    WC_AVG_GOALS, POISSON_PARAMS, HOST_NATIONS, get_team_data, get_h2h, get_manager,
    RECENT_WC_PERFORMANCE, XG_DATA, OPPONENT_QUALITY,
)


@dataclass
class PoissonPrediction:
    team_a: str
    team_b: str
    lambda_a: float
    lambda_b: float
    win_prob_a: float
    win_prob_b: float
    draw_prob: float
    predicted_score: Tuple[int, int]
    home_advantage: float = 0.0
    confidence: float = 0.0
    factor_breakdown: Dict[str, float] = field(default_factory=dict)
    adjusted_lambda_a: Optional[float] = None
    adjusted_lambda_b: Optional[float] = None


def poisson_prob(k: float, lam: float) -> float:
    """P(X = k) for Poisson(lambda)"""
    return (lam ** k) * math.exp(-lam) / math.factorial(k)


def poisson_cdf(k: int, lam: float) -> float:
    """P(X <= k) for Poisson(lambda)"""
    return sum(poisson_prob(i, lam) for i in range(k + 1))


def predict_match_poisson(team_a: str, team_b: str,
                          is_neutral: bool = True) -> PoissonPrediction:
    td_a = get_team_data(team_a)
    td_b = get_team_data(team_b)

    league_avg = WC_AVG_GOALS / 2.0

    home_adv = 0.0
    if not is_neutral:
        if team_a in HOST_NATIONS:
            home_adv = 0.35
        elif team_b in HOST_NATIONS:
            home_adv = -0.25

    lambda_a = td_a.attack * td_b.defense * league_avg + home_adv
    lambda_b = td_b.attack * td_a.defense * league_avg

    lambda_a = max(0.1, lambda_a)
    lambda_b = max(0.1, lambda_b)

    win_a = 0.0
    win_b = 0.0
    draw = 0.0

    max_goals = 10
    for ga in range(max_goals + 1):
        pa = poisson_prob(ga, lambda_a)
        for gb in range(max_goals + 1):
            pb = poisson_prob(gb, lambda_b)
            prob = pa * pb
            if ga > gb:
                win_a += prob
            elif gb > ga:
                win_b += prob
            else:
                draw += prob

    total = win_a + win_b + draw
    if total > 0:
        win_a /= total
        win_b /= total
        draw /= total

    expected_a = round(lambda_a)
    expected_b = round(lambda_b)
    if expected_a == expected_b:
        if win_a > win_b:
            expected_a += 1
        elif win_b > win_a:
            expected_b += 1

    prob_diff = abs(win_a - 0.5) * 2
    confidence = min(0.95, 0.5 + prob_diff * 0.3)

    return PoissonPrediction(
        team_a=team_a, team_b=team_b,
        lambda_a=round(lambda_a, 3), lambda_b=round(lambda_b, 3),
        win_prob_a=round(win_a, 4), win_prob_b=round(win_b, 4),
        draw_prob=round(draw, 4),
        predicted_score=(expected_a, expected_b),
        home_advantage=round(home_adv, 2),
        confidence=round(confidence, 2),
    )


def simulate_match_poisson(lambda_a: float, lambda_b: float) -> Tuple[int, int, int]:
    goals_a = random.randint(0, 5)
    goals_b = random.randint(0, 5)
    prob_a = poisson_prob(goals_a, lambda_a)
    prob_b = poisson_prob(goals_b, lambda_b)
    goals_a = int(lambda_a + random.uniform(-0.5, 0.5) * math.sqrt(lambda_a))
    goals_b = int(lambda_b + random.uniform(-0.5, 0.5) * math.sqrt(lambda_b))
    if goals_a < 0: goals_a = 0
    if goals_b < 0: goals_b = 0

    if goals_a == goals_b:
        if random.random() < 0.5:
            goals_a += 1
        else:
            goals_b += 1

    if lambda_a > lambda_b * 1.5 and goals_a <= goals_b:
        if random.random() < 0.4:
            goals_a += 1

    if lambda_b > lambda_a * 1.5 and goals_b <= goals_a:
        if random.random() < 0.4:
            goals_b += 1

    return goals_a, goals_b


def predict_group_poisson(group_name: str, teams: list) -> list:
    results = []
    for i in range(len(teams)):
        pts = 0
        gf = 0
        ga = 0
        for j in range(len(teams)):
            if i == j:
                continue
            name_a = teams[i].name if hasattr(teams[i], 'name') else teams[i]
            name_b = teams[j].name if hasattr(teams[j], 'name') else teams[j]
            tname_a = teams[i].name if hasattr(teams[i], 'name') else teams[i]
            pred = predict_match_poisson(name_a, name_b)
            if pred.win_prob_a > 0.5 and pred.team_a == tname_a:
                pts += 3
            elif pred.win_prob_b > 0.5 and pred.team_b == tname_a:
                pts += 0
            else:
                pts += 1
            gf += pred.predicted_score[0] if pred.team_a == tname_a else pred.predicted_score[1]
            ga += pred.predicted_score[1] if pred.team_a == tname_a else pred.predicted_score[0]
        results.append({"team": tname_a, "points": pts, "gf": gf, "ga": ga, "gd": gf - ga})
    results.sort(key=lambda x: (-x["points"], -x["gd"], -x["gf"]))
    return results


def _form_to_score(form_str: str) -> float:
    """Convert W/D/L string to a score where W=1, D=0.5, L=0."""
    if not form_str:
        return 0.5
    scores = {"W": 1.0, "D": 0.5, "L": 0.0}
    return sum(scores.get(c.upper(), 0.5) for c in form_str) / len(form_str)


def _count_key_injuries(injuries: List[str]) -> int:
    """Count injuries that are likely to impact performance."""
    keywords = ["doubtful", "recovering", "muscle", "hamstring", "knee",
                "ankle", "groin", "calf", "knock", "strain"]
    return sum(1 for i in injuries if any(k in i.lower() for k in keywords))


def _wc_stage_to_score(stage: Optional[str]) -> float:
    """Convert WC stage to numerical score for performance weighting."""
    if not stage:
        return 0.0
    mapping = {
        "Winner": 1.0, "Runners-up": 0.9, "Third place": 0.8,
        "Fourth place": 0.7, "Quarter-finals": 0.6, "Round of 16": 0.4,
        "Group stage": 0.2,
    }
    return mapping.get(stage, 0.0)


def _compute_factor_adjustment(
    team_a: str, team_b: str,
    td_a, td_b,
    scraper_instance=None,
    schedule_data: Optional[dict] = None,
) -> Tuple[float, float, Dict[str, float]]:
    """
    Compute lambda adjustments for both teams based on multi-factor model.
    Returns (adj_a, adj_b, factor_details).
    Positive adj_a means team_a scores more.
    """
    factors = {}

    # 1. Recent form
    form_a = td_a.recent_form
    form_b = td_b.recent_form
    form_adj = (form_a - form_b) * 0.006
    factors["form"] = round(form_adj, 4)

    # 2. Goal differential from form ratings
    if scraper_instance:
        try:
            fr_a = scraper_instance.get_form_ratings(team_a)
            fr_b = scraper_instance.get_form_ratings(team_b)
            gd_a = fr_a["avg_goals_scored"] - fr_a["avg_goals_conceded"]
            gd_b = fr_b["avg_goals_scored"] - fr_b["avg_goals_conceded"]
            gd_adj = (gd_a - gd_b) * 0.03
            factors["goal_diff"] = round(gd_adj, 4)
        except Exception:
            factors["goal_diff"] = 0.0
    else:
        factors["goal_diff"] = 0.0

    # 3. Head-to-head history
    h2h = get_h2h(team_a, team_b)
    if h2h["total"] > 0:
        a_wins = h2h[f"{team_a}_wins"]
        b_wins = h2h[f"{team_b}_wins"]
        total = h2h["total"]
        rate_diff = (a_wins - b_wins) / total
        h2h_adj = rate_diff * 0.12
        factors["h2h"] = round(h2h_adj, 4)
    else:
        factors["h2h"] = 0.0

    # 4. Squad value
    if scraper_instance:
        try:
            squad_values = scraper_instance.get_squad_value()
            sv_a = squad_values.get(team_a, 0.5)
            sv_b = squad_values.get(team_b, 0.5)
            sv_adj = (sv_a - sv_b) * 0.10
            factors["squad_value"] = round(sv_adj, 4)
        except Exception:
            factors["squad_value"] = 0.0
    else:
        factors["squad_value"] = 0.0

    # 5. Tournament experience
    exp_a = min(td_a.appearances / 8, 1.0)
    exp_b = min(td_b.appearances / 8, 1.0)
    exp_adj = (exp_a - exp_b) * 0.05
    factors["experience"] = round(exp_adj, 4)

    # 6. Confederation strength
    conf_strength = {
        "UEFA": 0.04, "CONMEBOL": 0.03, "CONCACAF": 0.0,
        "CAF": -0.01, "AFC": -0.02, "OFC": -0.04,
    }
    conf_adj = conf_strength.get(td_a.confederation, 0) - conf_strength.get(td_b.confederation, 0)
    factors["confederation"] = round(conf_adj, 4)

    # 7. Injury impact
    if scraper_instance:
        try:
            news_a = scraper_instance.extract_team_news(team_a)
            news_b = scraper_instance.extract_team_news(team_b)
            injury_count_a = _count_key_injuries(news_a.injuries)
            injury_count_b = _count_key_injuries(news_b.injuries)
            injury_adj = (injury_count_b - injury_count_a) * 0.05
            factors["injuries"] = round(injury_adj, 4)
        except Exception:
            factors["injuries"] = 0.0
    else:
        factors["injuries"] = 0.0

    # 8. Manager pedigree
    mgr_a = get_manager(team_a)
    mgr_b = get_manager(team_b)
    mgr_adj = 0.0
    if mgr_a["won_tournament"]:
        mgr_adj += 0.03
    if mgr_b["won_tournament"]:
        mgr_adj -= 0.03
    factors["manager"] = round(mgr_adj, 4)

    # 9. Recent WC performance (2018 + 2022)
    perf_a = RECENT_WC_PERFORMANCE.get(team_a, {})
    perf_b = RECENT_WC_PERFORMANCE.get(team_b, {})
    if perf_a and perf_b:
        stage_a_2022 = _wc_stage_to_score(perf_a.get("2022_stage"))
        stage_b_2022 = _wc_stage_to_score(perf_b.get("2022_stage"))
        stage_a_2018 = _wc_stage_to_score(perf_a.get("2018_stage"))
        stage_b_2018 = _wc_stage_to_score(perf_b.get("2018_stage"))
        wc_score_a = stage_a_2022 * 0.7 + stage_a_2018 * 0.3
        wc_score_b = stage_b_2022 * 0.7 + stage_b_2018 * 0.3
        wc_adj = (wc_score_a - wc_score_b) * 0.06
        factors["wc_performance"] = round(wc_adj, 4)
    else:
        factors["wc_performance"] = 0.0

    # 10. xG differential (expected goals for/against)
    xg_a = XG_DATA.get(team_a, {})
    xg_b = XG_DATA.get(team_b, {})
    if xg_a and xg_b:
        xg_diff_a = xg_a.get("xg_for", 1.0) - xg_a.get("xg_against", 1.0)
        xg_diff_b = xg_b.get("xg_for", 1.0) - xg_b.get("xg_against", 1.0)
        xg_adj = (xg_diff_a - xg_diff_b) * 0.04
        factors["xG_differential"] = round(xg_adj, 4)
    else:
        factors["xG_differential"] = 0.0

    # 11. Quality of opponent faced (strength of schedule)
    opp_a = OPPONENT_QUALITY.get(team_a, 0.5)
    opp_b = OPPONENT_QUALITY.get(team_b, 0.5)
    opp_adj = (opp_a - opp_b) * 0.05
    factors["opponent_quality"] = round(opp_adj, 4)

    total_adj = sum(factors.values())
    total_adj = max(-0.50, min(0.50, total_adj))

    return total_adj, -total_adj, factors


def predict_match_enhanced(
    team_a: str, team_b: str,
    is_neutral: bool = True,
    use_factors: bool = True,
    scraper_instance=None,
) -> PoissonPrediction:
    """
    Enhanced Poisson match prediction incorporating up to 8 factors:
    form, goal diff, H2H, squad value, experience, confederation,
    injuries, and manager pedigree.
    """
    # Base Poisson prediction
    base_pred = predict_match_poisson(team_a, team_b, is_neutral=is_neutral)

    if not use_factors:
        return base_pred

    td_a = get_team_data(team_a)
    td_b = get_team_data(team_b)

    adj_a, adj_b, factor_details = _compute_factor_adjustment(
        team_a, team_b, td_a, td_b, scraper_instance
    )

    # Apply adjustments to lambda
    adj_lambda_a = base_pred.lambda_a * (1 + adj_a)
    adj_lambda_b = base_pred.lambda_b * (1 + adj_b)
    adj_lambda_a = max(0.1, adj_lambda_a)
    adj_lambda_b = max(0.1, adj_lambda_b)

    # Recompute probabilities with adjusted lambdas
    win_a = 0.0
    win_b = 0.0
    draw = 0.0
    max_goals = 10
    for ga in range(max_goals + 1):
        pa = poisson_prob(ga, adj_lambda_a)
        for gb in range(max_goals + 1):
            pb = poisson_prob(gb, adj_lambda_b)
            prob = pa * pb
            if ga > gb:
                win_a += prob
            elif gb > ga:
                win_b += prob
            else:
                draw += prob

    total = win_a + win_b + draw
    if total > 0:
        win_a /= total
        win_b /= total
        draw /= total

    expected_a = round(adj_lambda_a)
    expected_b = round(adj_lambda_b)
    if expected_a == expected_b:
        if win_a > win_b:
            expected_a += 1
        elif win_b > win_a:
            expected_b += 1

    prob_diff = abs(win_a - 0.5) * 2
    confidence = min(0.95, 0.5 + prob_diff * 0.3)

    return PoissonPrediction(
        team_a=team_a, team_b=team_b,
        lambda_a=round(base_pred.lambda_a, 3),
        lambda_b=round(base_pred.lambda_b, 3),
        win_prob_a=round(win_a, 4),
        win_prob_b=round(win_b, 4),
        draw_prob=round(draw, 4),
        predicted_score=(expected_a, expected_b),
        home_advantage=base_pred.home_advantage,
        confidence=round(confidence, 2),
        factor_breakdown=factor_details,
        adjusted_lambda_a=round(adj_lambda_a, 3),
        adjusted_lambda_b=round(adj_lambda_b, 3),
    )
