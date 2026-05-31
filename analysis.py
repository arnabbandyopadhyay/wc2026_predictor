"""Team analysis: strengths, weaknesses, playing style, key insights."""

from typing import List, Dict, Tuple
from data import get_team_data, POISSON_PARAMS, FIFA_RANKINGS_APRIL_2026, RECENT_FORM_MODIFIERS


STRENGTH_WEAKNESS_RULES = {
    "high_attack": ("⚡ Prolific Attack", "Elite goalscoring threat; consistently finds the net", "attack > 1.3"),
    "elite_defense": ("🛡️ Rock-solid Defense", "Concedes very few chances; disciplined back line", "defense < 0.85"),
    "balance": ("⚖️ Balanced Unit", "Well-rounded attack and defense with no glaring weak area", "0.9 <= attack <= 1.3 and 0.85 <= defense <= 1.1"),
    "vulnerable_defense": ("🔓 Leaky Defense", "Defensive frailty that top teams can exploit", "defense > 1.2"),
    "blunt_attack": ("😶 Blunt Attack", "Struggles to create quality scoring chances", "attack < 0.7"),
    "physical": ("💪 Physical Presence", "Strong aerial threat and set-piece danger", "conf in {'UEFA','CAF'} and attack > 0.9"),
    "counter": ("⚡ Counter-attacking Threat", "Dangerous on the break with pace", "defense > 1.0 and attack > 0.8"),
    "possession": ("🎯 Possession Masters", "Controls tempo through high passing accuracy", "conf == 'UEFA' and attack > 1.0"),
    "giant_killer": ("😤 Giant Killers", "Historically upsets higher-ranked opponents", "fifa_rank > 20 and recent_form > 0"),
    "inexperienced": ("🌱 Tournament Newcomers", "Limited World Cup experience; unproven at this level", "appearances <= 1"),
    "veteran_squad": ("🧠 Veteran Squad", "Deep tournament experience; thrives under pressure", "appearances >= 4 and best_result in ('Winner','Runners-up','Semi-finals')"),
    "host_boost": ("🇺🇸 Host Nation Advantage", "Playing on home soil with massive crowd support", "is_host"),
    "momentum": ("📈 Hot Form", "Excellent recent results building confidence", "recent_form > 8"),
    "slump": ("📉 Poor Run", "Below-par recent form raising concerns", "recent_form < -8"),
    "set_piece": ("🎯 Set-piece Specialists", "Deadly from corners and free-kicks", "conf in {'UEFA','CONMEBOL'} and attack > 1.0 and defense < 1.0"),
}


STYLES = {
    "High Press": ["France", "Spain", "England", "Netherlands", "Germany", "Portugal"],
    "Counter-attack": ["Morocco", "Japan", "South Korea", "Senegal", "Iran"],
    "Possession": ["Spain", "Argentina", "Portugal", "Brazil", "France"],
    "Physical": ["England", "Belgium", "Croatia", "Serbia", "Scotland"],
    "Tiki-taka": ["Spain", "Mexico", "Japan"],
    "Route One": ["Norway", "Scotland", "Sweden", "Turkey"],
    "Samba": ["Brazil", "Colombia", "Argentina"],
    "Park the Bus": ["Panama", "Curacao", "Haiti", "Cape Verde"],
}


def analyze_team(team: str) -> dict:
    td = get_team_data(team)
    is_host = team in {"United States", "Mexico", "Canada"}
    params = POISSON_PARAMS.get(team, {"attack": 0.8, "defense": 1.2})

    strengths = []
    weaknesses = []

    if params["attack"] > 1.3:
        strengths.append(("⚡ Prolific Attack", "Elite goalscoring threat averaging well above tournament mean"))
    if params["defense"] < 0.85:
        strengths.append(("🛡️ Rock-solid Defense", "Concedes very few chances; disciplined back line"))
    if params["defense"] > 1.2:
        weaknesses.append(("🔓 Leaky Defense", "Defensive frailty that top teams can exploit"))
    if params["attack"] < 0.7:
        weaknesses.append(("😶 Blunt Attack", "Struggles to create high-quality scoring chances"))
    if td.appearances <= 1:
        weaknesses.append(("🌱 Tournament Newcomers", "Limited World Cup experience at this level"))
    if td.appearances >= 4 and td.best_result in ("Winner", "Runners-up", "Semi-finals", "Fourth place", "Quarter-finals"):
        strengths.append(("🧠 Veteran Squad", f"Deep tournament pedigree ({td.appearances} appearances, best: {td.best_result})"))
    if is_host:
        strengths.append(("🇺🇸 Host Nation Boost", "Home crowds and familiar conditions provide measurable edge"))
    if td.recent_form > 8:
        strengths.append(("📈 Hot Form", "Excellent recent results building confidence"))
    if td.recent_form < -8:
        weaknesses.append(("📉 Poor Run", "Below-par recent form raising concerns"))
    if is_host and team == "United States":
        strengths.append(("⚡ Athletic Squad", "Deep, athletic roster with European top-league experience"))
    if team == "France":
        strengths.append(("⭐ Star Power", "Exceptional individual talent across every position"))
    if team == "Spain":
        strengths.append(("🎯 Possession Masters", "Controls matches through technical superiority"))
    if team == "Argentina":
        strengths.append(("🏆 Champion Mentality", "Defending champions with unmatched belief and cohesion"))
    if team == "Brazil":
        strengths.append(("🎭 Samba Flair", "Creative, unpredictable attack with individual brilliance"))
    if team == "England":
        strengths.append(("🏋️ Physical & Clinical", "Powerful set pieces and ruthless finishing"))
    if team == "Morocco":
        strengths.append(("🛡️ Defensive Organization", "Proven at WC 2022 with compact, hard-to-break shape"))

    avg_rank = sum(t[1] for t in sorted(FIFA_RANKINGS_APRIL_2026.items(), key=lambda x: -x[1])[:10]) / 10
    if td.fifa_rank > 25 and td.recent_form > 0:
        strengths.append(("😤 Rising Force", "Underdog on the rise with momentum and nothing to lose"))
    if params["attack"] - params["defense"] > 0.8:
        strengths.append(("📊 Positive Differential", "Attack significantly outpaces defensive frailty"))
    if params["defense"] - params["attack"] > 0.6:
        weaknesses.append(("📊 Negative Differential", "Defensive issues likely to outweigh attacking threat"))

    style = "Mixed / Adaptive"
    for sname, stlist in STYLES.items():
        if team in stlist:
            style = sname
            break

    return {
        "team": team,
        "style": style,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "attack_rating": params["attack"],
        "defense_rating": params["defense"],
        "form_score": td.recent_form,
        "experience": td.appearances,
    }


def compare_teams(team_a: str, team_b: str) -> dict:
    a = analyze_team(team_a)
    b = analyze_team(team_b)
    td_a = get_team_data(team_a)
    td_b = get_team_data(team_b)

    return {
        "team_a": a,
        "team_b": b,
        "key_battles": _key_battles(a, b),
        "advantage": _advantage(a, b, td_a, td_b),
    }


def _key_battles(a: dict, b: dict) -> List[str]:
    battles = []
    if a["attack_rating"] > 1.2 and b["defense_rating"] > 1.0:
        battles.append(f"{a['team']}'s attack ({a['attack_rating']:.1f}) vs {b['team']}'s defense ({b['defense_rating']:.1f})")
    if b["attack_rating"] > 1.2 and a["defense_rating"] > 1.0:
        battles.append(f"{b['team']}'s attack ({b['attack_rating']:.1f}) vs {a['team']}'s defense ({a['defense_rating']:.1f})")
    if abs(a["attack_rating"] - b["attack_rating"]) < 0.2:
        battles.append("Both teams have similar attacking output — midfield battle decides")
    if a["form_score"] > 5 and b["form_score"] < -3:
        battles.append(f"{a['team']} in hot form vs {b['team']} struggling — momentum matters")
    if b["form_score"] > 5 and a["form_score"] < -3:
        battles.append(f"{b['team']} in hot form vs {a['team']} struggling — momentum matters")
    if a["experience"] >= 4 and b["experience"] <= 2:
        battles.append(f"Experience gap: {a['team']} ({a['experience']} WC) vs {b['team']} ({b['experience']} WC)")
    if b["experience"] >= 4 and a["experience"] <= 2:
        battles.append(f"Experience gap: {b['team']} ({b['experience']} WC) vs {a['team']} ({a['experience']} WC)")
    return battles[:4]


def _advantage(a: dict, b: dict, td_a, td_b) -> dict:
    cats = {}
    if a["attack_rating"] > b["attack_rating"]:
        cats["Attack"] = a["team"]
    else:
        cats["Attack"] = b["team"]
    if a["defense_rating"] < b["defense_rating"]:
        cats["Defense"] = a["team"]
    else:
        cats["Defense"] = b["team"]
    if td_a.fifa_rank < td_b.fifa_rank:
        cats["Ranking"] = a["team"]
    else:
        cats["Ranking"] = b["team"]
    if td_a.effective_strength() > td_b.effective_strength():
        cats["Overall"] = a["team"]
    else:
        cats["Overall"] = b["team"]
    if td_a.appearances > td_b.appearances:
        cats["Experience"] = a["team"]
    else:
        cats["Experience"] = b["team"]
    return cats
