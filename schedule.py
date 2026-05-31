"""World Cup 2026 match schedule with dates, venues, and matchdays."""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Optional, Tuple

from data import WORLD_CUP_GROUPS, HOST_NATIONS


@dataclass
class MatchFixture:
    match_id: str
    round: str
    group: Optional[str]
    team_a: str
    team_b: str
    date: date
    venue: str
    matchday: int
    is_knockout: bool = False


VENUES = [
    "MetLife Stadium, East Rutherford",
    "SoFi Stadium, Inglewood",
    "AT&T Stadium, Arlington",
    "NRG Stadium, Houston",
    "Mercedes-Benz Stadium, Atlanta",
    "Lincoln Financial Field, Philadelphia",
    "Gillette Stadium, Foxborough",
    "Levi's Stadium, Santa Clara",
    "Lumen Field, Seattle",
    "Allegiant Stadium, Las Vegas",
    "Estadio Azteca, Mexico City",
    "Estadio BBVA, Monterrey",
    "Estadio Akron, Guadalajara",
    "BC Place, Vancouver",
    "BMO Field, Toronto",
    "Estadio Olímpico Universitario, Mexico City",
]

MD1_VENUES = [
    "MetLife Stadium", "SoFi Stadium", "AT&T Stadium", "NRG Stadium",
    "Mercedes-Benz Stadium", "Lincoln Financial Field", "Gillette Stadium",
    "Levi's Stadium", "Lumen Field", "Allegiant Stadium",
    "Estadio Azteca", "Estadio BBVA", "Estadio Akron",
    "BC Place", "BMO Field", "Estadio Olímpico Universitario",
]


def _md(day: int) -> date:
    return date(2026, 6, day)


def _jul(day: int) -> date:
    return date(2026, 7, day)


def build_schedule() -> List[MatchFixture]:
    fixtures = []
    mid = 0

    groups = sorted(WORLD_CUP_GROUPS.keys())
    gv = {}
    for gi, g in enumerate(groups):
        start_day = 11 + (gi // 4) * 3 + (gi % 4)
        if start_day > 27:
            start_day = 24 + (gi % 4)
        gv[g] = start_day

    for g in groups:
        teams = WORLD_CUP_GROUPS[g]
        team_abbr = {t: "".join(w[0] for w in t.split())[:3].upper() for t in teams}
        md_start = gv[g]
        matchdays = [
            [(teams[0], teams[1]), (teams[2], teams[3])],
            [(teams[0], teams[2]), (teams[1], teams[3])],
            [(teams[0], teams[3]), (teams[1], teams[2])],
        ]
        for mdi, mdpairs in enumerate(matchdays):
            d = _md(md_start + mdi)
            for pi, (ta, tb) in enumerate(mdpairs):
                mid += 1
                v = MD1_VENUES[(mid - 1) % len(MD1_VENUES)]
                fixtures.append(MatchFixture(
                    match_id=f"G{g}-{mdi+1}-{pi+1}",
                    round="Group Stage", group=g,
                    team_a=ta, team_b=tb,
                    date=d, venue=v,
                    matchday=mdi + 1,
                ))

    r32_dates = [_md(28), _md(29), _md(30), _jul(1)]
    for i in range(16):
        mid += 1
        fixtures.append(MatchFixture(
            match_id=f"R32-{i+1}",
            round="Round of 32", group=None,
            team_a="TBD", team_b="TBD",
            date=r32_dates[i % 4],
            venue=MD1_VENUES[i % len(MD1_VENUES)],
            matchday=1, is_knockout=True,
        ))

    r16_dates = [_jul(3), _jul(4), _jul(5), _jul(6)]
    for i in range(8):
        mid += 1
        fixtures.append(MatchFixture(
            match_id=f"R16-{i+1}",
            round="Round of 16", group=None,
            team_a="TBD", team_b="TBD",
            date=r16_dates[i % 4],
            venue=MD1_VENUES[i % len(MD1_VENUES)],
            matchday=2, is_knockout=True,
        ))

    qf_dates = [_jul(9), _jul(10), _jul(11)]
    for i in range(4):
        mid += 1
        fixtures.append(MatchFixture(
            match_id=f"QF-{i+1}",
            round="Quarter-finals", group=None,
            team_a="TBD", team_b="TBD",
            date=qf_dates[i % 3],
            venue=MD1_VENUES[i % len(MD1_VENUES)],
            matchday=3, is_knockout=True,
        ))

    sf_date = _jul(14)
    for i in range(2):
        mid += 1
        fixtures.append(MatchFixture(
            match_id=f"SF-{i+1}",
            round="Semi-finals", group=None,
            team_a="TBD", team_b="TBD",
            date=sf_date,
            venue="Mercedes-Benz Stadium, Atlanta",
            matchday=4, is_knockout=True,
        ))

    mid += 1
    fixtures.append(MatchFixture(
        match_id="3P",
        round="Third Place", group=None,
        team_a="TBD", team_b="TBD",
        date=_jul(18),
        venue="Estadio Azteca, Mexico City",
        matchday=5, is_knockout=True,
    ))

    mid += 1
    fixtures.append(MatchFixture(
        match_id="F",
        round="Final", group=None,
        team_a="TBD", team_b="TBD",
        date=_jul(19),
        venue="MetLife Stadium, East Rutherford",
        matchday=5, is_knockout=True,
    ))

    return fixtures


SCHEDULE = build_schedule()


def get_fixtures_for_date(d: date) -> List[MatchFixture]:
    return [f for f in SCHEDULE if f.date == d]


def get_fixtures_for_team(team: str) -> List[MatchFixture]:
    return [f for f in SCHEDULE if f.team_a == team or f.team_b == team]


def get_fixtures_for_group(g: str) -> List[MatchFixture]:
    return [f for f in SCHEDULE if f.group == g and f.round == "Group Stage"]


def get_fixtures_by_matchday() -> dict:
    mds = {}
    for f in SCHEDULE:
        key = f.date.isoformat()
        if key not in mds:
            mds[key] = []
        mds[key].append(f)
    return dict(sorted(mds.items()))


def get_todays_fixtures() -> List[MatchFixture]:
    today = date.today()
    if today < date(2026, 6, 11):
        return [f for f in SCHEDULE if f.date == date(2026, 6, 11)]
    if today > date(2026, 7, 19):
        return []
    return get_fixtures_for_date(today)


def get_upcoming_fixtures(days: int = 3) -> List[MatchFixture]:
    today = date.today()
    if today < date(2026, 6, 11):
        cutoff = date(2026, 6, 11)
    else:
        cutoff = today
    end = cutoff
    results = []
    for f in SCHEDULE:
        if cutoff <= f.date <= cutoff + timedelta(days=days - 1):
            results.append(f)
    return results
