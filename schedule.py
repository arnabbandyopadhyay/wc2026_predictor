"""World Cup 2026 match schedule with official FIFA dates, venues, and kickoff times."""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Optional

from data import WORLD_CUP_GROUPS


@dataclass
class MatchFixture:
    match_id: str
    round: str
    group: Optional[str]
    team_a: str
    team_b: str
    date: date
    kickoff: str
    venue: str
    matchday: int
    is_knockout: bool = False


def _md(day: int) -> date:
    return date(2026, 6, day)


def _jul(day: int) -> date:
    return date(2026, 7, day)


# (date, group, team_a, team_b, venue, kickoff)
_GROUP_FIXTURES = [
    # === Matchday 1 ===
    # Group A
    (_md(11), "A", "Mexico", "South Africa", "Estadio Azteca, Mexico City", "13:00"),
    (_md(11), "A", "South Korea", "Czechia", "Estadio Akron, Guadalajara", "20:00"),
    # Group B
    (_md(12), "B", "Canada", "Bosnia and Herzegovina", "BMO Field, Toronto", "15:00"),
    (_md(13), "B", "Qatar", "Switzerland", "Levi's Stadium, Santa Clara", "15:00"),
    # Group C
    (_md(13), "C", "Brazil", "Morocco", "MetLife Stadium, East Rutherford", "18:00"),
    (_md(13), "C", "Haiti", "Scotland", "Gillette Stadium, Foxborough", "21:00"),
    # Group D
    (_md(12), "D", "United States", "Paraguay", "SoFi Stadium, Inglewood", "21:00"),
    (_md(13), "D", "Australia", "Turkey", "BC Place, Vancouver", "12:00"),
    # Group E
    (_md(14), "E", "Germany", "Curacao", "NRG Stadium, Houston", "12:00"),
    (_md(14), "E", "Ivory Coast", "Ecuador", "Lincoln Financial Field, Philadelphia", "19:00"),
    # Group F
    (_md(14), "F", "Netherlands", "Japan", "AT&T Stadium, Arlington", "16:00"),
    (_md(14), "F", "Sweden", "Tunisia", "Estadio BBVA, Monterrey", "22:00"),
    # Group G
    (_md(15), "G", "Belgium", "Egypt", "Lumen Field, Seattle", "15:00"),
    (_md(15), "G", "Iran", "New Zealand", "SoFi Stadium, Inglewood", "21:00"),
    # Group H
    (_md(15), "H", "Spain", "Cape Verde", "Mercedes-Benz Stadium, Atlanta", "12:00"),
    (_md(15), "H", "Saudi Arabia", "Uruguay", "Allegiant Stadium, Las Vegas", "18:00"),
    # Group I
    (_md(16), "I", "France", "Senegal", "MetLife Stadium, East Rutherford", "15:00"),
    (_md(16), "I", "Iraq", "Norway", "Gillette Stadium, Foxborough", "18:00"),
    # Group J
    (_md(16), "J", "Argentina", "Algeria", "Allegiant Stadium, Las Vegas", "21:00"),
    (_md(16), "J", "Austria", "Jordan", "Levi's Stadium, Santa Clara", "12:00"),
    # Group K
    (_md(17), "K", "Portugal", "DR Congo", "NRG Stadium, Houston", "13:00"),
    (_md(17), "K", "Uzbekistan", "Colombia", "Estadio Azteca, Mexico City", "22:00"),
    # Group L
    (_md(17), "L", "England", "Croatia", "AT&T Stadium, Arlington", "16:00"),
    (_md(17), "L", "Ghana", "Panama", "BMO Field, Toronto", "19:00"),

    # === Matchday 2 ===
    # Group A
    (_md(18), "A", "Czechia", "South Africa", "Mercedes-Benz Stadium, Atlanta", "12:00"),
    (_md(18), "A", "Mexico", "South Korea", "Estadio Akron, Guadalajara", "21:00"),
    # Group B
    (_md(18), "B", "Switzerland", "Bosnia and Herzegovina", "SoFi Stadium, Inglewood", "15:00"),
    (_md(18), "B", "Canada", "Qatar", "BC Place, Vancouver", "18:00"),
    # Group C
    (_md(19), "C", "Scotland", "Morocco", "Gillette Stadium, Foxborough", "15:00"),
    (_md(19), "C", "Brazil", "Haiti", "Lincoln Financial Field, Philadelphia", "21:00"),
    # Group D
    (_md(19), "D", "United States", "Australia", "Lumen Field, Seattle", "15:00"),
    (_md(19), "D", "Turkey", "Paraguay", "Levi's Stadium, Santa Clara", "12:00"),
    # Group E
    (_md(20), "E", "Germany", "Ivory Coast", "BMO Field, Toronto", "16:00"),
    (_md(20), "E", "Ecuador", "Curacao", "Allegiant Stadium, Las Vegas", "20:00"),
    # Group F
    (_md(20), "F", "Netherlands", "Sweden", "NRG Stadium, Houston", "13:00"),
    (_md(20), "F", "Tunisia", "Japan", "Estadio BBVA, Monterrey", "22:00"),
    # Group G
    (_md(21), "G", "Belgium", "Iran", "SoFi Stadium, Inglewood", "15:00"),
    (_md(21), "G", "New Zealand", "Egypt", "BC Place, Vancouver", "21:00"),
    # Group H
    (_md(21), "H", "Spain", "Saudi Arabia", "Mercedes-Benz Stadium, Atlanta", "12:00"),
    (_md(21), "H", "Uruguay", "Cape Verde", "Allegiant Stadium, Las Vegas", "18:00"),
    # Group I
    (_md(22), "I", "Norway", "Senegal", "MetLife Stadium, East Rutherford", "20:00"),
    (_md(22), "I", "France", "Iraq", "Lincoln Financial Field, Philadelphia", "18:00"),
    # Group J
    (_md(22), "J", "Jordan", "Algeria", "Levi's Stadium, Santa Clara", "12:00"),
    (_md(22), "J", "Argentina", "Austria", "AT&T Stadium, Arlington", "15:00"),
    # Group K
    (_md(23), "K", "Portugal", "Uzbekistan", "NRG Stadium, Houston", "13:00"),
    (_md(23), "K", "Colombia", "DR Congo", "Estadio Akron, Guadalajara", "22:00"),
    # Group L
    (_md(23), "L", "England", "Ghana", "Gillette Stadium, Foxborough", "16:00"),
    (_md(23), "L", "Panama", "Croatia", "BMO Field, Toronto", "19:00"),

    # === Matchday 3 ===
    # Group A
    (_md(24), "A", "Mexico", "Czechia", "Estadio Azteca, Mexico City", "21:00"),
    (_md(24), "A", "South Korea", "South Africa", "Estadio BBVA, Monterrey", "21:00"),
    # Group B
    (_md(24), "B", "Switzerland", "Canada", "BC Place, Vancouver", "15:00"),
    (_md(24), "B", "Bosnia and Herzegovina", "Qatar", "Lumen Field, Seattle", "15:00"),
    # Group C
    (_md(24), "C", "Brazil", "Scotland", "Allegiant Stadium, Las Vegas", "18:00"),
    (_md(24), "C", "Morocco", "Haiti", "Mercedes-Benz Stadium, Atlanta", "18:00"),
    # Group D
    (_md(25), "D", "United States", "Turkey", "SoFi Stadium, Inglewood", "16:00"),
    (_md(25), "D", "Paraguay", "Australia", "Levi's Stadium, Santa Clara", "16:00"),
    # Group E
    (_md(25), "E", "Ecuador", "Germany", "MetLife Stadium, East Rutherford", "16:00"),
    (_md(25), "E", "Curacao", "Ivory Coast", "Lincoln Financial Field, Philadelphia", "16:00"),
    # Group F
    (_md(25), "F", "Japan", "Sweden", "AT&T Stadium, Arlington", "16:00"),
    (_md(25), "F", "Tunisia", "Netherlands", "Allegiant Stadium, Las Vegas", "16:00"),
    # Group G
    (_md(26), "G", "New Zealand", "Belgium", "BC Place, Vancouver", "21:00"),
    (_md(26), "G", "Egypt", "Iran", "Lumen Field, Seattle", "21:00"),
    # Group H
    (_md(26), "H", "Cape Verde", "Saudi Arabia", "NRG Stadium, Houston", "20:00"),
    (_md(26), "H", "Uruguay", "Spain", "Estadio Akron, Guadalajara", "22:00"),
    # Group I
    (_md(26), "I", "Norway", "France", "Gillette Stadium, Foxborough", "15:00"),
    (_md(26), "I", "Senegal", "Iraq", "BMO Field, Toronto", "15:00"),
    # Group J
    (_md(27), "J", "Argentina", "Jordan", "AT&T Stadium, Arlington", "22:00"),
    (_md(27), "J", "Algeria", "Austria", "Allegiant Stadium, Las Vegas", "22:00"),
    # Group K
    (_md(27), "K", "Colombia", "Portugal", "Allegiant Stadium, Las Vegas", "19:30"),
    (_md(27), "K", "DR Congo", "Uzbekistan", "Mercedes-Benz Stadium, Atlanta", "19:30"),
    # Group L
    (_md(27), "L", "Panama", "England", "MetLife Stadium, East Rutherford", "17:00"),
    (_md(27), "L", "Croatia", "Ghana", "Lincoln Financial Field, Philadelphia", "17:00"),
]

_KO_FIXTURES = [
    # Round of 32
    ("Round of 32", _md(28), "Group A 2nd vs Group B 2nd", "SoFi Stadium, Inglewood", "15:00"),
    ("Round of 32", _md(29), "Group E Winner vs 3rd Place (A/B/C/D/F)", "Gillette Stadium, Foxborough", "16:30"),
    ("Round of 32", _md(29), "Group C Winner vs Group F 2nd", "NRG Stadium, Houston", "13:00"),
    ("Round of 32", _md(29), "Group F Winner vs Group C 2nd", "Estadio BBVA, Monterrey", "21:00"),
    ("Round of 32", _md(30), "Group I Winner vs 3rd Place (C/D/F/G/H)", "MetLife Stadium, East Rutherford", "17:00"),
    ("Round of 32", _md(30), "Group E 2nd vs Group I 2nd", "AT&T Stadium, Arlington", "13:00"),
    ("Round of 32", _md(30), "Group A Winner vs 3rd Place (C/E/F/H/I)", "Estadio Azteca, Mexico City", "21:00"),
    ("Round of 32", _jul(1), "Group L Winner vs 3rd Place (E/H/I/J/K)", "Mercedes-Benz Stadium, Atlanta", "12:00"),
    ("Round of 32", _jul(1), "Group D Winner vs 3rd Place (B/E/F/I/J)", "Levi's Stadium, Santa Clara", "20:00"),
    ("Round of 32", _jul(1), "Group G Winner vs 3rd Place (A/E/H/I/J)", "Lumen Field, Seattle", "16:00"),
    ("Round of 32", _jul(2), "Group H Winner vs Group J 2nd", "SoFi Stadium, Inglewood", "15:00"),
    ("Round of 32", _jul(2), "Group K 2nd vs Group L 2nd", "BMO Field, Toronto", "19:00"),
    ("Round of 32", _jul(2), "Group B Winner vs 3rd Place (D/E/I/J/L)", "BC Place, Vancouver", "23:00"),
    ("Round of 32", _jul(3), "Group J Winner vs Group H 2nd", "Allegiant Stadium, Las Vegas", "17:00"),
    ("Round of 32", _jul(3), "Group K Winner vs 3rd Place (D/E/I/J/L)", "Allegiant Stadium, Las Vegas", "21:00"),
    ("Round of 32", _jul(3), "Group D 2nd vs Group G 2nd", "AT&T Stadium, Arlington", "13:00"),
    # Round of 16
    ("Round of 16", _jul(4), "R32 74 Winner vs R32 77 Winner", "Lincoln Financial Field, Philadelphia", "16:00"),
    ("Round of 16", _jul(4), "R32 73 Winner vs R32 75 Winner", "NRG Stadium, Houston", "13:00"),
    ("Round of 16", _jul(5), "R32 76 Winner vs R32 78 Winner", "MetLife Stadium, East Rutherford", "16:00"),
    ("Round of 16", _jul(5), "R32 79 Winner vs R32 80 Winner", "Estadio Azteca, Mexico City", "13:00"),
    ("Round of 16", _jul(6), "R32 83 Winner vs R32 84 Winner", "AT&T Stadium, Arlington", "16:00"),
    ("Round of 16", _jul(6), "R32 81 Winner vs R32 82 Winner", "Lumen Field, Seattle", "13:00"),
    ("Round of 16", _jul(7), "R32 86 Winner vs R32 88 Winner", "Mercedes-Benz Stadium, Atlanta", "16:00"),
    ("Round of 16", _jul(7), "R32 85 Winner vs R32 87 Winner", "BC Place, Vancouver", "13:00"),
    # Quarter-finals
    ("Quarter-finals", _jul(9), "R16 89 Winner vs R16 90 Winner", "Gillette Stadium, Foxborough", "20:00"),
    ("Quarter-finals", _jul(10), "R16 93 Winner vs R16 94 Winner", "SoFi Stadium, Inglewood", "20:00"),
    ("Quarter-finals", _jul(11), "R16 91 Winner vs R16 92 Winner", "Allegiant Stadium, Las Vegas", "16:00"),
    ("Quarter-finals", _jul(11), "R16 95 Winner vs R16 96 Winner", "Allegiant Stadium, Las Vegas", "20:00"),
    # Semi-finals
    ("Semi-finals", _jul(14), "QF 97 Winner vs QF 98 Winner", "AT&T Stadium, Arlington", "20:00"),
    ("Semi-finals", _jul(15), "QF 99 Winner vs QF 100 Winner", "Mercedes-Benz Stadium, Atlanta", "20:00"),
    # Third place
    ("Third Place", _jul(18), "SF 101 Loser vs SF 102 Loser", "Allegiant Stadium, Las Vegas", "16:00"),
    # Final
    ("Final", _jul(19), "SF 101 Winner vs SF 102 Winner", "MetLife Stadium, East Rutherford", "15:00"),
]


def _venue_short(full: str) -> str:
    """Return short venue name for display."""
    return full


def build_schedule():
    fixtures = []
    mid = 0

    for d, g, ta, tb, venue, ko in _GROUP_FIXTURES:
        mid += 1
        teams = WORLD_CUP_GROUPS[g]
        pair_num = 1
        md_num = 1
        for existing in fixtures:
            if existing.group == g and existing.round == "Group Stage":
                if existing.date == d:
                    pair_num += 1
                elif existing.date < d:
                    md_num = max(md_num, existing.matchday + 1)
        fixtures.append(MatchFixture(
            match_id=f"G{g}M{md_num}P{pair_num}",
            round="Group Stage", group=g,
            team_a=ta, team_b=tb,
            date=d, kickoff=ko, venue=venue,
            matchday=md_num, is_knockout=False,
        ))

    for rnd, d, label, venue, ko in _KO_FIXTURES:
        mid += 1
        parts = label.split(" vs ")
        team_a = parts[0] if len(parts) > 0 else "TBD"
        team_b = parts[1] if len(parts) > 1 else "TBD"
        fixtures.append(MatchFixture(
            match_id=f"KO-{mid}",
            round=rnd, group=None,
            team_a=team_a, team_b=team_b,
            date=d, kickoff=ko, venue=venue,
            matchday=1, is_knockout=True,
        ))

    # Sort by date then kickoff
    fixtures.sort(key=lambda f: (f.date, f.kickoff))
    return fixtures


SCHEDULE = build_schedule()


def get_fixtures_for_date(d: date):
    return [f for f in SCHEDULE if f.date == d]


def get_fixtures_for_team(team: str):
    return [f for f in SCHEDULE if team in (f.team_a, f.team_b)]


def get_fixtures_for_group(g: str):
    return [f for f in SCHEDULE if f.group == g and f.round == "Group Stage"]


def get_fixtures_by_matchday():
    mds = {}
    for f in SCHEDULE:
        key = f.date.isoformat()
        if key not in mds:
            mds[key] = []
        mds[key].append(f)
    return dict(sorted(mds.items()))


def get_todays_fixtures():
    today = date.today()
    if today < date(2026, 6, 11):
        return [f for f in SCHEDULE if f.date == date(2026, 6, 11)]
    if today > date(2026, 7, 19):
        return []
    return get_fixtures_for_date(today)


def get_upcoming_fixtures(days: int = 3):
    today = date.today()
    if today < date(2026, 6, 11):
        cutoff = date(2026, 6, 11)
    else:
        cutoff = today
    results = []
    for f in SCHEDULE:
        if cutoff <= f.date <= cutoff + timedelta(days=days - 1):
            results.append(f)
    return results
