"""World Cup 2026 tournament simulation engine with Poisson model and real bracket."""

import copy
import random
from collections import defaultdict, OrderedDict
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple

from data import (WORLD_CUP_GROUPS, get_all_teams, get_team_data, Team,
                   GROUP_BRACKET_PATHS, ROUND_OF_32_MATCHUPS,
                   KNOCKOUT_BRACKET, R16_BRACKET, QF_BRACKET, SF_BRACKET,
                   HOST_NATIONS)
from poisson import simulate_match_poisson, predict_match_poisson


@dataclass
class MatchResult:
    team_a: str
    team_b: str
    goals_a: int
    goals_b: int
    is_knockout: bool = False

    def winner(self) -> Optional[str]:
        if self.goals_a > self.goals_b:
            return self.team_a
        elif self.goals_b > self.goals_a:
            return self.team_b
        return None

    def loser(self) -> Optional[str]:
        w = self.winner()
        if w == self.team_a:
            return self.team_b
        elif w == self.team_b:
            return self.team_a
        return None

    def is_draw(self) -> bool:
        return self.goals_a == self.goals_b


@dataclass
class GroupStanding:
    team: str
    points: int
    goals_for: int
    goals_against: int
    goal_diff: int
    played: int = 0


class GroupStage:
    def __init__(self):
        self.groups: dict[str, list[GroupStanding]] = {}
        self.matches: dict[str, list[MatchResult]] = {}
        self._init_standings()

    def _init_standings(self):
        for group_name, team_names in WORLD_CUP_GROUPS.items():
            self.groups[group_name] = [
                GroupStanding(team=t, points=0, goals_for=0, goals_against=0, goal_diff=0)
                for t in team_names
            ]
            self.matches[group_name] = []

    def play_match(self, group: str, team_a: str, team_b: str,
                   is_neutral: bool = True) -> MatchResult:
        ta = get_team_data(team_a)
        tb = get_team_data(team_b)
        pred = predict_match_poisson(team_a, team_b, is_neutral=is_neutral)
        goals_a, goals_b = simulate_match_poisson(pred.lambda_a, pred.lambda_b)
        result = MatchResult(team_a, team_b, goals_a, goals_b)
        self.matches[group].append(result)

        for gs in self.groups[group]:
            if gs.team == team_a:
                gs.played += 1
                gs.goals_for += goals_a
                gs.goals_against += goals_b
                gs.goal_diff = gs.goals_for - gs.goals_against
                if goals_a > goals_b:
                    gs.points += 3
                elif goals_a == goals_b:
                    gs.points += 1
            elif gs.team == team_b:
                gs.played += 1
                gs.goals_for += goals_b
                gs.goals_against += goals_a
                gs.goal_diff = gs.goals_for - gs.goals_against
                if goals_b > goals_a:
                    gs.points += 3
                elif goals_a == goals_b:
                    gs.points += 1
        return result

    def simulate_group(self, group_name: str) -> list[GroupStanding]:
        teams = WORLD_CUP_GROUPS[group_name]
        fixtures = [
            (teams[0], teams[1]), (teams[2], teams[3]),
            (teams[0], teams[2]), (teams[1], teams[3]),
            (teams[0], teams[3]), (teams[1], teams[2]),
        ]
        for ta, tb in fixtures:
            is_neutral = not (ta in HOST_NATIONS or tb in HOST_NATIONS)
            self.play_match(group_name, ta, tb, is_neutral=is_neutral)

        self.groups[group_name].sort(key=lambda x: (-x.points, -x.goal_diff, -x.goals_for))
        return self.groups[group_name]

    def simulate_all_groups(self) -> dict[str, list[GroupStanding]]:
        for g in sorted(WORLD_CUP_GROUPS.keys()):
            self.simulate_group(g)
        return self.groups

    def get_qualified_teams(self):
        group_winners = []
        group_runners_up = []
        third_placed = []

        for g in sorted(self.groups.keys()):
            standings = self.groups[g]
            group_winners.append(standings[0].team)
            group_runners_up.append(standings[1].team)
            if len(standings) >= 3:
                gs = standings[2]
                third_placed.append((gs.team, gs.points, gs.goal_diff, gs.goals_for, g))

        third_placed.sort(key=lambda x: (-x[1], -x[2], -x[3]))
        best_third = [t[0] for t in third_placed[:8]]

        return group_winners, group_runners_up, best_third


def build_real_bracket(group_winners: List[str],
                       group_runners_up: List[str],
                       best_third: List[str]) -> List[Tuple[str, str]]:
    groups_ordered = sorted(WORLD_CUP_GROUPS.keys())
    gw_dict = {g: group_winners[i] for i, g in enumerate(groups_ordered) if i < len(group_winners)}
    ru_dict = {g: group_runners_up[i] for i, g in enumerate(groups_ordered) if i < len(group_runners_up)}
    bt_pool = list(best_third)
    bt_idx = 0

    used = set()
    matches = []

    def team_from_spec(spec: str):
        if spec.startswith("1"):
            return gw_dict.get(spec[1:])
        elif spec.startswith("2"):
            return ru_dict.get(spec[1:])
        elif spec == "3rd":
            nonlocal bt_idx
            if bt_idx < len(bt_pool):
                t = bt_pool[bt_idx]
                bt_idx += 1
                return t
        return None

    for slot_name, (spec_a, spec_b) in sorted(ROUND_OF_32_MATCHUPS.items()):
        team1 = team_from_spec(spec_a)
        team2 = team_from_spec(spec_b)

        if not team1 or team1 in used:
            team1 = None
        if not team2 or team2 in used or team2 == team1:
            # Try to find an alternative
            alt_found = None
            for alt in group_runners_up + bt_pool:
                if alt not in used and alt != team1:
                    alt_found = alt
                    break
            team2 = alt_found if spec_b == "3rd" else team2

        if team1 and team2:
            matches.append((team1, team2))
            used.add(team1)
            used.add(team2)

    remaining = [t for t in group_winners + group_runners_up + bt_pool if t not in used]
    random.shuffle(remaining)
    for i in range(0, len(remaining) - 1, 2):
        matches.append((remaining[i], remaining[i + 1]))

    return matches


def simulate_knockout_round(matchups: List[Tuple[str, str]], store: List) -> List[str]:
    winners = []
    for ta, tb in matchups:
        if ta is None or tb is None:
            w = ta or tb
            if w: winners.append(w)
            continue
        pred = predict_match_poisson(ta, tb)
        ga, gb = simulate_match_poisson(pred.lambda_a, pred.lambda_b)
        result = MatchResult(ta, tb, ga, gb, True)
        store.append(result)
        winners.append(result.winner())
    return winners


def _pair_up(teams: List[str]) -> List[Tuple[str, str]]:
    pairs = []
    for i in range(0, len(teams) - 1, 2):
        pairs.append((teams[i], teams[i + 1]))
    if len(teams) % 2 == 1:
        pairs.append((teams[-1], None))
    return pairs


def simulate_bracket(r32_matches: List[Tuple[str, str]]) -> dict:
    results = {"round_of_32": [], "round_of_16": [], "quarter_finals": [],
               "semi_finals": [], "third_place": None, "final": None, "winner": None}

    r16_winners = [w for w in simulate_knockout_round(r32_matches, results["round_of_32"]) if w]
    qf_winners = [w for w in simulate_knockout_round(_pair_up(r16_winners), results["round_of_16"]) if w]
    sf_winners = [w for w in simulate_knockout_round(_pair_up(qf_winners), results["quarter_finals"]) if w]
    finalists = [w for w in simulate_knockout_round(_pair_up(sf_winners), results["semi_finals"]) if w]

    sf_losers = [m.loser() for m in results["semi_finals"] if m.loser()]
    if len(sf_losers) >= 2:
        pred = predict_match_poisson(sf_losers[0], sf_losers[1])
        tf_ga, tf_gb = simulate_match_poisson(pred.lambda_a, pred.lambda_b)
        results["third_place"] = MatchResult(sf_losers[0], sf_losers[1], tf_ga, tf_gb, True)

    finalists = [f for f in finalists if f is not None]
    if len(finalists) >= 2:
        pred = predict_match_poisson(finalists[0], finalists[1])
        f_ga, f_gb = simulate_match_poisson(pred.lambda_a, pred.lambda_b)
        results["final"] = MatchResult(finalists[0], finalists[1], f_ga, f_gb, True)
        results["winner"] = results["final"].winner()

    return results


class TournamentSimulator:
    def __init__(self):
        self.group_stage = GroupStage()
        self.knockout_results: Optional[dict] = None

    def run(self) -> dict:
        self.group_stage.simulate_all_groups()
        gw_list, gr_list, bt_list = self.group_stage.get_qualified_teams()

        bracket = build_real_bracket(gw_list, gr_list, bt_list)
        self.knockout_results = simulate_bracket(bracket)
        return self._compile_results()

    def _compile_results(self) -> dict:
        return {
            "group_standings": self.group_stage.groups,
            "group_matches": self.group_stage.matches,
            "knockout": self.knockout_results,
        }

    def run_monte_carlo(self, n: int = 1000) -> dict:
        winners = defaultdict(int)
        semi_finalists = defaultdict(int)
        quarter_finalists = defaultdict(int)

        for _ in range(n):
            sim = TournamentSimulator()
            result = sim.run()
            w = result["knockout"]["winner"]
            if w:
                winners[w] += 1

            for rnd in ["semi_finals", "quarter_finals"]:
                for m in result["knockout"].get(rnd, []):
                    if m and hasattr(m, 'winner'):
                        w = m.winner()
                        l = m.loser()
                        if rnd == "semi_finals":
                            if w: semi_finalists[w] += 1
                            if l: semi_finalists[l] += 1
                        if rnd == "quarter_finals":
                            if w: quarter_finalists[w] += 1
                            if l: quarter_finalists[l] += 1

        return {
            "total_simulations": n,
            "winners": dict(sorted(winners.items(), key=lambda x: -x[1])),
            "semi_finalists": dict(sorted(semi_finalists.items(), key=lambda x: -x[1])),
            "quarter_finalists": dict(sorted(quarter_finalists.items(), key=lambda x: -x[1])),
        }
