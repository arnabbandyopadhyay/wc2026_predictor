"""Elo-based match prediction model using FIFA ranking points."""

import math
import random


def expected_score(rating_a: float, rating_b: float) -> float:
    return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 600.0))


def predict_match(team_a_strength: float, team_b_strength: float) -> tuple[float, float]:
    exp_a = expected_score(team_a_strength, team_b_strength)
    return exp_a, 1.0 - exp_a


def simulate_match(team_a_strength: float, team_b_strength: float) -> tuple[int, int]:
    exp_a, exp_b = predict_match(team_a_strength, team_b_strength)
    win_prob_a = exp_a / (exp_a + exp_b)

    if random.random() < win_prob_a:
        # Team A wins - sample goal difference
        gd = _sample_goal_diff(exp_a)
        goals_a = max(1, int((1 + gd) * random.uniform(0.5, 1.2)))
        goals_b = max(0, goals_a - gd)
    else:
        gd = _sample_goal_diff(exp_b)
        goals_b = max(1, int((1 + gd) * random.uniform(0.5, 1.2)))
        goals_a = max(0, goals_b - gd)

    if goals_a == goals_b:
        if random.random() < 0.3:
            goals_a += 1
        else:
            goals_b += 1

    return goals_a, goals_b


def _sample_goal_diff(exp: float) -> int:
    stronger = exp > 0.6
    if stronger:
        return random.choices([1, 2, 3], weights=[0.5, 0.35, 0.15])[0]
    else:
        return random.choices([1, 2], weights=[0.7, 0.3])[0]
