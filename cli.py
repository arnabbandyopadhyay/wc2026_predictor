"""CLI interface for the WC2026 Predictor."""

import random
import sys
from typing import Optional

from data import (FIFA_RANKINGS_APRIL_2026, WORLD_CUP_GROUPS,
                   RECENT_FORM_MODIFIERS, WORLD_CUP_HISTORY,
                   get_all_teams, get_team_data, get_group_teams, Team)
from tournament import TournamentSimulator, GroupStage, MatchResult, GroupStanding
from llm_predictor import LLMPredictor


def print_banner():
    print("""
+-------------------------------------------------------------+
|           FIFA WORLD CUP 2026 PREDICTOR SYSTEM              |
|     LLM-Enhanced Tournament Forecasting Engine              |
|     Based on April 2026 FIFA Rankings & Recent Form Data    |
+-------------------------------------------------------------+
    """)


def show_rankings():
    print("\n+--------------------------------------------------+")
    print("|  FIFA WORLD RANKINGS (APRIL 2026)                |")
    print("+--------------------------------------------------+")
    print(f"{'Rank':<6} {'Team':<20} {'Conf':<10} {'Points':<10} {'Form':<6}")
    print("-" * 55)
    sorted_teams = sorted(FIFA_RANKINGS_APRIL_2026.items(), key=lambda x: -x[1])
    for i, (name, points) in enumerate(sorted_teams, 1):
        try:
            td = get_team_data(name)
            form = RECENT_FORM_MODIFIERS.get(name, 0)
            form_str = f"{form:+d}" if form != 0 else " 0"
            print(f"{i:<6} {name:<20} {td.confederation:<10} {points:<10.2f} {form_str:<6}")
        except Exception:
            pass
    print()


def show_groups():
    print("\n+--------------------------------------------------+")
    print("|  WORLD CUP 2026 GROUP DRAW                        |")
    print("+--------------------------------------------------+")
    for g_name in sorted(WORLD_CUP_GROUPS.keys()):
        teams = WORLD_CUP_GROUPS[g_name]
        print(f"\n  Group {g_name}:")
        for i, t in enumerate(teams, 1):
            td = get_team_data(t)
            print(f"    {i}. {t:<20} FIFA: {td.fifa_points:<8.1f}  ({td.confederation})")
    print()


def simulate_single():
    print("\n+--------------------------------------------------+")
    print("|  SINGLE TOURNAMENT SIMULATION                     |")
    print("+--------------------------------------------------+")
    sim = TournamentSimulator()
    result = sim.run()

    gs = result["group_standings"]
    print("\n-- Group Stage Results --")
    for g in sorted(gs.keys()):
        standings = gs[g]
        print(f"\n  Group {g}:")
        print(f"  {'#':<3} {'Team':<20} {'Pts':<5} {'GD':<5} {'GF':<5}")
        for i, s in enumerate(standings, 1):
            marker = " *" if i <= 2 else ""
            print(f"  {i:<3} {s.team:<20} {s.points:<5} {s.goal_diff:<5} {s.goals_for:<5}{marker}")

        matches = result["group_matches"].get(g, [])
        for m in matches:
            print(f"    {m.team_a} {m.goals_a}-{m.goals_b} {m.team_b}")

    ko = result["knockout"]
    if ko:
        print("\n-- Knockout Stage --")
        _print_ko_round("Round of 32", ko.get("round_of_32", []))
        _print_ko_round("Round of 16", ko.get("round_of_16", []))
        _print_ko_round("Quarter-finals", ko.get("quarter_finals", []))
        _print_ko_round("Semi-finals", ko.get("semi_finals", []))

        if ko.get("third_place"):
            m = ko["third_place"]
            print(f"\n  Third Place: {m.team_a} {m.goals_a}-{m.goals_b} {m.team_b}")

        if ko.get("final"):
            m = ko["final"]
            print(f"\n  FINAL: {m.team_a} {m.goals_a}-{m.goals_b} {m.team_b}")
            print(f"\n  CHAMPION: {ko['winner']}")

    return result


def _print_ko_round(name: str, matches: list):
    if not matches:
        return
    print(f"\n  {name}:")
    for m in matches:
        print(f"    {m.team_a} {m.goals_a}-{m.goals_b} {m.team_b}")


def run_monte_carlo(n: int = 100):
    print(f"\n+--------------------------------------------------+")
    print(f"|  MONTE CARLO SIMULATION ({n} runs)                 |")
    print(f"+--------------------------------------------------+")
    print(f"  Running {n} tournament simulations...")

    sim = TournamentSimulator()
    results = sim.run_monte_carlo(n)

    print(f"\n-- Win Probability (Top 20) --")
    print(f"  {'Team':<20} {'Win %':<10} {'Semi %':<10} {'Quarter %':<10}")
    print(f"  {'-'*50}")
    top20 = list(results["winners"].items())[:20]
    for team, wins in top20:
        wp = wins / n * 100
        sp = results["semi_finalists"].get(team, 0) / n * 100
        qp = results["quarter_finalists"].get(team, 0) / n * 100
        print(f"  {team:<20} {wp:<8.1f}% {sp:<8.1f}% {qp:<8.1f}%")

    print(f"\n-- Championship Favorites (Top 10) --")
    for i, (team, wins) in enumerate(top20[:10], 1):
        pct = wins / n * 100
        print(f"  {i}. {team} - {pct:.1f}%")

    return results


def predict_with_llm():
    """Run LLM-enhanced prediction (requires model download)."""
    print("\n+--------------------------------------------------+")
    print("|  LLM-ENHANCED PREDICTION                          |")
    print("+--------------------------------------------------+")
    print("  Loading LLM model (first time will download)...")

    predictor = LLMPredictor()
    if not predictor.load():
        print("  Could not load LLM model. Falling back to statistical mode.")
        return None

    print("\n-- Group Predictions (LLM) --")
    for g in sorted(WORLD_CUP_GROUPS.keys()):
        teams = get_group_teams(g)
        result = predictor.predict_group(g, teams)
        if result:
            print(f"\n  Group {g}:")
            for r in result:
                t = r.get("team", "?")
                p = r.get("points", "?")
                pos = r.get("position", "?")
                print(f"    {pos}. {t} ({p} pts)")

    print("\n-- Key Match Predictions (LLM) --")
    key_groups = ["A", "C", "D", "E", "G", "L"]
    for g in key_groups:
        teams = WORLD_CUP_GROUPS[g]
        matchups = [(teams[0], teams[1]), (teams[0], teams[2]), (teams[1], teams[3])]
        for ta, tb in matchups:
            td_a = get_team_data(ta)
            td_b = get_team_data(tb)
            result = predictor.predict_match(ta, td_a.effective_strength(),
                                             tb, td_b.effective_strength())
            if result:
                print(f"  {ta} vs {tb}: {result.get('score', '?')} "
                      f"[{result.get('winner', '?')}] - {result.get('reasoning', '')[:80]}")

    return predictor


def head_to_head(team_a: str, team_b: str):
    td_a = get_team_data(team_a)
    td_b = get_team_data(team_b)

    str_a = td_a.effective_strength()
    str_b = td_b.effective_strength()
    exp_a = 1.0 / (1.0 + 10 ** ((str_b - str_a) / 600.0))

    print(f"\n-- Head-to-Head: {team_a} vs {team_b} --")
    print(f"\n  {team_a}:")
    print(f"    FIFA Rank: #{td_a.fifa_rank}  ({td_a.fifa_points:.2f} pts)")
    print(f"    Confederation: {td_a.confederation}")
    print(f"    WC Appearances: {td_a.appearances}")
    print(f"    Best Result: {td_a.best_result}")
    print(f"    Recent Form Adj: {td_a.recent_form:+d}")
    print(f"    Effective Strength: {str_a:.1f}")

    print(f"\n  {team_b}:")
    print(f"    FIFA Rank: #{td_b.fifa_rank}  ({td_b.fifa_points:.2f} pts)")
    print(f"    Confederation: {td_b.confederation}")
    print(f"    WC Appearances: {td_b.appearances}")
    print(f"    Best Result: {td_b.best_result}")
    print(f"    Recent Form Adj: {td_b.recent_form:+d}")
    print(f"    Effective Strength: {str_b:.1f}")

    print(f"\n  Win Probability: {team_a} {exp_a*100:.1f}% | {team_b} {(1-exp_a)*100:.1f}%")
    print()


def interactive_menu():
    print_banner()
    while True:
        print("\n+--------------------------------------------------+")
        print("|  MAIN MENU                                        |")
        print("+--------------------------------------------------+")
        print("|  1. Show FIFA Rankings                            |")
        print("|  2. Show World Cup Groups                         |")
        print("|  3. Single Tournament Simulation                  |")
        print("|  4. Monte Carlo Simulation (100 runs)             |")
        print("|  5. Monte Carlo Simulation (1000 runs)            |")
        print("|  6. Head-to-Head Analysis                         |")
        print("|  7. LLM-Enhanced Prediction                       |")
        print("|  8. Team Profile                                  |")
        print("|  0. Exit                                          |")
        print("+--------------------------------------------------+")
        choice = input("\n  Select option: ").strip()

        if choice == "0":
            print("  Goodbye!")
            break
        elif choice == "1":
            show_rankings()
        elif choice == "2":
            show_groups()
        elif choice == "3":
            simulate_single()
        elif choice == "4":
            run_monte_carlo(100)
        elif choice == "5":
            run_monte_carlo(1000)
        elif choice == "6":
            team_a = input("  Team A: ").strip()
            team_b = input("  Team B: ").strip()
            head_to_head(team_a.title(), team_b.title())
        elif choice == "7":
            predict_with_llm()
        elif choice == "8":
            name = input("  Team name: ").strip().title()
            try:
                td = get_team_data(name)
                print(f"\n-- {td.name} --")
                print(f"  FIFA Rank: #{td.fifa_rank}")
                print(f"  FIFA Points: {td.fifa_points:.2f}")
                print(f"  Confederation: {td.confederation}")
                print(f"  WC Appearances: {td.appearances}")
                print(f"  Best Result: {td.best_result}")
                print(f"  Recent Form Adjustment: {td.recent_form:+d}")
                print(f"  Effective Strength: {td.effective_strength():.1f}")
            except Exception:
                print(f"  Team '{name}' not found.")
        else:
            print("  Invalid option.")
