"""FIFA World Cup 2026 - Team data, rankings, group draw, H2H, and historical info."""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple

FIFA_RANKINGS_APRIL_2026 = {
    "France": 1877.32, "Spain": 1876.40, "Argentina": 1874.81, "England": 1825.97,
    "Portugal": 1763.83, "Brazil": 1761.16, "Netherlands": 1757.87, "Morocco": 1755.87,
    "Belgium": 1734.71, "Germany": 1730.37, "Croatia": 1717.07, "Colombia": 1693.09,
    "Senegal": 1688.99, "Mexico": 1681.03, "United States": 1673.13, "Uruguay": 1673.07,
    "Japan": 1660.43, "Switzerland": 1649.40, "Norway": 1609.14, "South Korea": 1587.52,
    "Austria": 1578.61, "Iran": 1570.15, "Ecuador": 1566.90, "Turkey": 1563.47,
    "Sweden": 1558.23, "Australia": 1548.59, "Scotland": 1541.63,
    "Panama": 1514.97, "Canada": 1510.31, "Egypt": 1506.25, "Algeria": 1498.42,
    "Paraguay": 1489.71, "Tunisia": 1483.55, "Ivory Coast": 1478.18, "Ghana": 1465.39,
    "Bosnia and Herzegovina": 1457.84, "South Africa": 1443.17, "Qatar": 1431.54,
    "Saudi Arabia": 1427.62, "Jordan": 1419.16, "Uzbekistan": 1411.30, "Iraq": 1404.87,
    "Cape Verde": 1398.12, "DR Congo": 1391.74, "Haiti": 1367.55, "New Zealand": 1354.21,
    "Curacao": 1348.63, "Czechia": 1532.12,
}

QUALIFIED_TEAMS = sorted(FIFA_RANKINGS_APRIL_2026.keys())

WORLD_CUP_GROUPS = {
    "A": ["Mexico", "South Africa", "South Korea", "Czechia"],
    "B": ["Canada", "Bosnia and Herzegovina", "Qatar", "Switzerland"],
    "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "D": ["United States", "Paraguay", "Australia", "Turkey"],
    "E": ["Germany", "Curacao", "Ivory Coast", "Ecuador"],
    "F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "H": ["Spain", "Cape Verde", "Saudi Arabia", "Uruguay"],
    "I": ["France", "Senegal", "Iraq", "Norway"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "DR Congo", "Uzbekistan", "Colombia"],
    "L": ["England", "Croatia", "Ghana", "Panama"],
}

# 2026 Round of 32 bracket pairings
# Official FIFA bracket: 12 group winners + 12 runners-up + 8 best 3rd-place teams
# R32 matchups based on confirmed schedule (June 28 - July 3)
GROUP_BRACKET_PATHS = {
    "A": {"1st": "R32-7", "2nd": "R32-1"},
    "B": {"1st": "R32-13", "2nd": "R32-1"},
    "C": {"1st": "R32-4", "2nd": "R32-3"},
    "D": {"1st": "R32-9", "2nd": "R32-16"},
    "E": {"1st": "R32-2", "2nd": "R32-6"},
    "F": {"1st": "R32-3", "2nd": "R32-4"},
    "G": {"1st": "R32-10", "2nd": "R32-16"},
    "H": {"1st": "R32-12", "2nd": "R32-14"},
    "I": {"1st": "R32-5", "2nd": "R32-6"},
    "J": {"1st": "R32-14", "2nd": "R32-12"},
    "K": {"1st": "R32-15", "2nd": "R32-11"},
    "L": {"1st": "R32-8", "2nd": "R32-11"},
}

# Official R32 matchups
ROUND_OF_32_MATCHUPS = {
    "R32-1": ("2A", "2B"),
    "R32-2": ("1E", "3rd"),
    "R32-3": ("1F", "2C"),
    "R32-4": ("1C", "2F"),
    "R32-5": ("1I", "3rd"),
    "R32-6": ("2E", "2I"),
    "R32-7": ("1A", "3rd"),
    "R32-8": ("1L", "3rd"),
    "R32-9": ("1D", "3rd"),
    "R32-10": ("1G", "3rd"),
    "R32-11": ("2K", "2L"),
    "R32-12": ("1H", "2J"),
    "R32-13": ("1B", "3rd"),
    "R32-14": ("1J", "2H"),
    "R32-15": ("1K", "3rd"),
    "R32-16": ("2D", "2G"),
}

# R16 onwards bracket flow: {slot: next_slot}
KNOCKOUT_BRACKET = {
    "R32-1": "R16-1", "R32-2": "R16-1",
    "R32-3": "R16-2", "R32-4": "R16-2",
    "R32-5": "R16-3", "R32-6": "R16-3",
    "R32-7": "R16-4", "R32-8": "R16-4",
    "R32-9": "R16-5", "R32-10": "R16-5",
    "R32-11": "R16-6", "R32-12": "R16-6",
    "R32-13": "R16-7", "R32-14": "R16-7",
    "R32-15": "R16-8", "R32-16": "R16-8",
}

R16_BRACKET = {
    "R16-1": "QF-1", "R16-2": "QF-1",
    "R16-3": "QF-2", "R16-4": "QF-2",
    "R16-5": "QF-3", "R16-6": "QF-3",
    "R16-7": "QF-4", "R16-8": "QF-4",
}

QF_BRACKET = {
    "QF-1": "SF-1", "QF-2": "SF-1",
    "QF-3": "SF-2", "QF-4": "SF-2",
}

SF_BRACKET = {"SF-1": "F-1", "SF-2": "F-1"}

# Head-to-Head Database: Real World Cup & major tournament matches (2010-2022)
# Format: (team_a, team_b, goals_a, goals_b, competition, year)
HEAD_TO_HEAD_MATCHES = [
    # 2010 World Cup
    ("France", "Mexico", 0, 2, "WC Group", 2010),
    ("France", "South Africa", 1, 2, "WC Group", 2010),
    ("Germany", "Australia", 4, 0, "WC Group", 2010),
    ("Germany", "Ghana", 1, 0, "WC Group", 2010),
    ("Germany", "England", 4, 1, "WC R16", 2010),
    ("Germany", "Argentina", 4, 0, "WC QF", 2010),
    ("Germany", "Spain", 0, 1, "WC SF", 2010),
    ("Netherlands", "Denmark", 2, 0, "WC Group", 2010),
    ("Netherlands", "Japan", 1, 0, "WC Group", 2010),
    ("Netherlands", "Brazil", 2, 1, "WC QF", 2010),
    ("Netherlands", "Uruguay", 3, 2, "WC SF", 2010),
    ("Netherlands", "Spain", 0, 1, "WC Final", 2010),
    ("Spain", "Switzerland", 0, 1, "WC Group", 2010),
    ("Spain", "Portugal", 1, 0, "WC R16", 2010),
    ("Spain", "Germany", 1, 0, "WC SF", 2010),
    ("Argentina", "Mexico", 3, 1, "WC R16", 2010),
    ("Argentina", "Germany", 0, 4, "WC QF", 2010),
    ("Brazil", "Chile", 3, 0, "WC R16", 2010),
    ("Brazil", "Netherlands", 1, 2, "WC QF", 2010),
    ("Uruguay", "South Korea", 2, 1, "WC R16", 2010),
    ("Uruguay", "Ghana", 1, 1, "WC QF", 2010),
    ("Uruguay", "Netherlands", 2, 3, "WC SF", 2010),
    ("England", "Germany", 1, 4, "WC R16", 2010),
    ("Japan", "Denmark", 3, 1, "WC Group", 2010),
    ("Japan", "Paraguay", 0, 0, "WC R16", 2010),
    ("USA", "Algeria", 1, 0, "WC Group", 2010),
    ("USA", "Ghana", 1, 2, "WC R16", 2010),
    # 2014 World Cup
    ("Germany", "Portugal", 4, 0, "WC Group", 2014),
    ("Germany", "USA", 1, 0, "WC Group", 2014),
    ("Germany", "France", 1, 0, "WC QF", 2014),
    ("Germany", "Brazil", 7, 1, "WC SF", 2014),
    ("Germany", "Argentina", 1, 0, "WC Final", 2014),
    ("Argentina", "Bosnia", 2, 1, "WC Group", 2014),
    ("Argentina", "Iran", 1, 0, "WC Group", 2014),
    ("Argentina", "Nigeria", 3, 2, "WC Group", 2014),
    ("Argentina", "Switzerland", 1, 0, "WC R16", 2014),
    ("Argentina", "Belgium", 1, 0, "WC QF", 2014),
    ("Argentina", "Netherlands", 0, 0, "WC SF", 2014),
    ("Argentina", "Germany", 0, 1, "WC Final", 2014),
    ("Brazil", "Croatia", 3, 1, "WC Group", 2014),
    ("Brazil", "Mexico", 0, 0, "WC Group", 2014),
    ("Brazil", "Chile", 1, 1, "WC R16", 2014),
    ("Brazil", "Colombia", 2, 1, "WC QF", 2014),
    ("Brazil", "Germany", 1, 7, "WC SF", 2014),
    ("Brazil", "Netherlands", 0, 3, "WC 3rd", 2014),
    ("Netherlands", "Spain", 5, 1, "WC Group", 2014),
    ("Netherlands", "Australia", 3, 2, "WC Group", 2014),
    ("Netherlands", "Mexico", 2, 1, "WC R16", 2014),
    ("Netherlands", "Costa Rica", 0, 0, "WC QF", 2014),
    ("Netherlands", "Argentina", 0, 0, "WC SF", 2014),
    ("Netherlands", "Brazil", 3, 0, "WC 3rd", 2014),
    ("France", "Honduras", 3, 0, "WC Group", 2014),
    ("France", "Switzerland", 5, 2, "WC Group", 2014),
    ("France", "Nigeria", 2, 0, "WC R16", 2014),
    ("France", "Germany", 0, 1, "WC QF", 2014),
    ("Spain", "Netherlands", 1, 5, "WC Group", 2014),
    ("Spain", "Chile", 0, 2, "WC Group", 2014),
    ("England", "Italy", 1, 2, "WC Group", 2014),
    ("England", "Uruguay", 1, 2, "WC Group", 2014),
    ("England", "Costa Rica", 0, 0, "WC Group", 2014),
    ("Portugal", "Germany", 0, 4, "WC Group", 2014),
    ("Portugal", "USA", 2, 2, "WC Group", 2014),
    ("Portugal", "Ghana", 2, 1, "WC Group", 2014),
    ("Belgium", "Algeria", 2, 1, "WC Group", 2014),
    ("Belgium", "Russia", 1, 0, "WC Group", 2014),
    ("Belgium", "South Korea", 1, 0, "WC Group", 2014),
    ("Belgium", "USA", 2, 1, "WC R16", 2014),
    ("Belgium", "Argentina", 0, 1, "WC QF", 2014),
    ("Colombia", "Greece", 3, 0, "WC Group", 2014),
    ("Colombia", "Ivory Coast", 2, 1, "WC Group", 2014),
    ("Colombia", "Japan", 4, 1, "WC Group", 2014),
    ("Colombia", "Uruguay", 2, 0, "WC R16", 2014),
    ("Colombia", "Brazil", 1, 2, "WC QF", 2014),
    ("Uruguay", "England", 2, 1, "WC Group", 2014),
    ("Uruguay", "Italy", 1, 0, "WC Group", 2014),
    ("Uruguay", "Colombia", 0, 2, "WC R16", 2014),
    ("Mexico", "Cameroon", 1, 0, "WC Group", 2014),
    ("Mexico", "Brazil", 0, 0, "WC Group", 2014),
    ("Mexico", "Croatia", 3, 1, "WC Group", 2014),
    ("Mexico", "Netherlands", 1, 2, "WC R16", 2014),
    ("Switzerland", "Ecuador", 2, 1, "WC Group", 2014),
    ("Switzerland", "France", 2, 5, "WC Group", 2014),
    ("Switzerland", "Argentina", 0, 1, "WC R16", 2014),
    ("USA", "Ghana", 2, 1, "WC Group", 2014),
    ("USA", "Portugal", 2, 2, "WC Group", 2014),
    ("USA", "Germany", 0, 1, "WC Group", 2014),
    ("USA", "Belgium", 1, 2, "WC R16", 2014),
    ("Japan", "Ivory Coast", 1, 2, "WC Group", 2014),
    ("Japan", "Greece", 0, 0, "WC Group", 2014),
    ("Japan", "Colombia", 1, 4, "WC Group", 2014),
    ("Iran", "Nigeria", 0, 0, "WC Group", 2014),
    ("Iran", "Argentina", 0, 1, "WC Group", 2014),
    ("Iran", "Bosnia", 1, 3, "WC Group", 2014),
    ("Croatia", "Brazil", 1, 3, "WC Group", 2014),
    ("Croatia", "Cameroon", 4, 0, "WC Group", 2014),
    ("Croatia", "Mexico", 1, 3, "WC Group", 2014),
    ("Ghana", "USA", 1, 2, "WC Group", 2014),
    ("Ghana", "Germany", 2, 2, "WC Group", 2014),
    ("Ghana", "Portugal", 1, 2, "WC Group", 2014),
    ("Algeria", "Belgium", 1, 2, "WC Group", 2014),
    ("Algeria", "South Korea", 4, 2, "WC Group", 2014),
    ("Algeria", "Germany", 1, 2, "WC R16", 2014),
    # 2018 World Cup
    ("France", "Australia", 2, 1, "WC Group", 2018),
    ("France", "Peru", 1, 0, "WC Group", 2018),
    ("France", "Argentina", 4, 3, "WC R16", 2018),
    ("France", "Uruguay", 2, 0, "WC QF", 2018),
    ("France", "Belgium", 1, 0, "WC SF", 2018),
    ("France", "Croatia", 4, 2, "WC Final", 2018),
    ("Croatia", "Nigeria", 2, 0, "WC Group", 2018),
    ("Croatia", "Argentina", 3, 0, "WC Group", 2018),
    ("Croatia", "Denmark", 1, 1, "WC R16", 2018),
    ("Croatia", "Russia", 2, 2, "WC QF", 2018),
    ("Croatia", "England", 2, 1, "WC SF", 2018),
    ("Croatia", "France", 2, 4, "WC Final", 2018),
    ("Argentina", "Iceland", 1, 1, "WC Group", 2018),
    ("Argentina", "Croatia", 0, 3, "WC Group", 2018),
    ("Argentina", "Nigeria", 2, 1, "WC Group", 2018),
    ("Argentina", "France", 3, 4, "WC R16", 2018),
    ("Brazil", "Switzerland", 1, 1, "WC Group", 2018),
    ("Brazil", "Costa Rica", 2, 0, "WC Group", 2018),
    ("Brazil", "Serbia", 2, 0, "WC Group", 2018),
    ("Brazil", "Mexico", 2, 0, "WC R16", 2018),
    ("Brazil", "Belgium", 1, 2, "WC QF", 2018),
    ("Belgium", "Panama", 3, 0, "WC Group", 2018),
    ("Belgium", "Tunisia", 5, 2, "WC Group", 2018),
    ("Belgium", "England", 1, 0, "WC Group", 2018),
    ("Belgium", "Japan", 3, 2, "WC R16", 2018),
    ("Belgium", "Brazil", 2, 1, "WC QF", 2018),
    ("Belgium", "France", 0, 1, "WC SF", 2018),
    ("Belgium", "England", 2, 0, "WC 3rd", 2018),
    ("England", "Tunisia", 2, 1, "WC Group", 2018),
    ("England", "Panama", 6, 1, "WC Group", 2018),
    ("England", "Belgium", 0, 1, "WC Group", 2018),
    ("England", "Colombia", 1, 1, "WC R16", 2018),
    ("England", "Sweden", 2, 0, "WC QF", 2018),
    ("England", "Croatia", 1, 2, "WC SF", 2018),
    ("England", "Belgium", 0, 2, "WC 3rd", 2018),
    ("Uruguay", "Egypt", 1, 0, "WC Group", 2018),
    ("Uruguay", "Saudi Arabia", 1, 0, "WC Group", 2018),
    ("Uruguay", "Russia", 3, 0, "WC Group", 2018),
    ("Uruguay", "Portugal", 2, 1, "WC R16", 2018),
    ("Uruguay", "France", 0, 2, "WC QF", 2018),
    ("Portugal", "Spain", 3, 3, "WC Group", 2018),
    ("Portugal", "Morocco", 1, 0, "WC Group", 2018),
    ("Portugal", "Iran", 1, 1, "WC Group", 2018),
    ("Portugal", "Uruguay", 1, 2, "WC R16", 2018),
    ("Spain", "Portugal", 3, 3, "WC Group", 2018),
    ("Spain", "Iran", 1, 0, "WC Group", 2018),
    ("Spain", "Morocco", 2, 2, "WC Group", 2018),
    ("Spain", "Russia", 1, 1, "WC R16", 2018),
    ("Mexico", "Germany", 1, 0, "WC Group", 2018),
    ("Mexico", "South Korea", 2, 1, "WC Group", 2018),
    ("Mexico", "Sweden", 0, 3, "WC Group", 2018),
    ("Mexico", "Brazil", 0, 2, "WC R16", 2018),
    ("Sweden", "South Korea", 1, 0, "WC Group", 2018),
    ("Sweden", "Germany", 1, 2, "WC Group", 2018),
    ("Sweden", "Mexico", 3, 0, "WC Group", 2018),
    ("Sweden", "Switzerland", 1, 0, "WC R16", 2018),
    ("Sweden", "England", 0, 2, "WC QF", 2018),
    ("Japan", "Colombia", 2, 1, "WC Group", 2018),
    ("Japan", "Senegal", 2, 2, "WC Group", 2018),
    ("Japan", "Poland", 0, 1, "WC Group", 2018),
    ("Japan", "Belgium", 2, 3, "WC R16", 2018),
    ("Senegal", "Poland", 2, 1, "WC Group", 2018),
    ("Senegal", "Japan", 2, 2, "WC Group", 2018),
    ("Senegal", "Colombia", 0, 1, "WC Group", 2018),
    ("Switzerland", "Brazil", 1, 1, "WC Group", 2018),
    ("Switzerland", "Serbia", 2, 1, "WC Group", 2018),
    ("Switzerland", "Costa Rica", 2, 2, "WC Group", 2018),
    ("Switzerland", "Sweden", 0, 1, "WC R16", 2018),
    ("Colombia", "Japan", 1, 2, "WC Group", 2018),
    ("Colombia", "Poland", 3, 0, "WC Group", 2018),
    ("Colombia", "Senegal", 1, 0, "WC Group", 2018),
    ("Colombia", "England", 1, 1, "WC R16", 2018),
    ("Iran", "Morocco", 1, 0, "WC Group", 2018),
    ("Iran", "Spain", 0, 1, "WC Group", 2018),
    ("Iran", "Portugal", 1, 1, "WC Group", 2018),
    ("South Korea", "Sweden", 0, 1, "WC Group", 2018),
    ("South Korea", "Mexico", 1, 2, "WC Group", 2018),
    ("South Korea", "Germany", 2, 0, "WC Group", 2018),
    ("Germany", "Mexico", 0, 1, "WC Group", 2018),
    ("Germany", "Sweden", 2, 1, "WC Group", 2018),
    ("Germany", "South Korea", 0, 2, "WC Group", 2018),
    ("Australia", "France", 1, 2, "WC Group", 2018),
    ("Australia", "Denmark", 1, 1, "WC Group", 2018),
    ("Australia", "Peru", 0, 2, "WC Group", 2018),
    # 2022 World Cup
    ("Argentina", "Saudi Arabia", 1, 2, "WC Group", 2022),
    ("Argentina", "Mexico", 2, 0, "WC Group", 2022),
    ("Argentina", "Poland", 2, 0, "WC Group", 2022),
    ("Argentina", "Australia", 2, 1, "WC R16", 2022),
    ("Argentina", "Netherlands", 2, 2, "WC QF", 2022),
    ("Argentina", "Croatia", 3, 0, "WC SF", 2022),
    ("Argentina", "France", 3, 3, "WC Final", 2022),
    ("France", "Australia", 4, 1, "WC Group", 2022),
    ("France", "Denmark", 2, 1, "WC Group", 2022),
    ("France", "Tunisia", 0, 1, "WC Group", 2022),
    ("France", "Poland", 3, 1, "WC R16", 2022),
    ("France", "England", 2, 1, "WC QF", 2022),
    ("France", "Morocco", 2, 0, "WC SF", 2022),
    ("France", "Argentina", 3, 3, "WC Final", 2022),
    ("Brazil", "Serbia", 2, 0, "WC Group", 2022),
    ("Brazil", "Switzerland", 1, 0, "WC Group", 2022),
    ("Brazil", "Cameroon", 0, 1, "WC Group", 2022),
    ("Brazil", "South Korea", 4, 1, "WC R16", 2022),
    ("Brazil", "Croatia", 1, 1, "WC QF", 2022),
    ("England", "Iran", 6, 2, "WC Group", 2022),
    ("England", "USA", 0, 0, "WC Group", 2022),
    ("England", "Wales", 3, 0, "WC Group", 2022),
    ("England", "Senegal", 3, 0, "WC R16", 2022),
    ("England", "France", 1, 2, "WC QF", 2022),
    ("Spain", "Costa Rica", 7, 0, "WC Group", 2022),
    ("Spain", "Germany", 1, 1, "WC Group", 2022),
    ("Spain", "Japan", 1, 2, "WC Group", 2022),
    ("Spain", "Morocco", 0, 0, "WC R16", 2022),
    ("Netherlands", "Senegal", 2, 0, "WC Group", 2022),
    ("Netherlands", "Ecuador", 1, 1, "WC Group", 2022),
    ("Netherlands", "Qatar", 2, 0, "WC Group", 2022),
    ("Netherlands", "USA", 3, 1, "WC R16", 2022),
    ("Netherlands", "Argentina", 2, 2, "WC QF", 2022),
    ("Croatia", "Morocco", 0, 0, "WC Group", 2022),
    ("Croatia", "Canada", 4, 1, "WC Group", 2022),
    ("Croatia", "Belgium", 0, 0, "WC Group", 2022),
    ("Croatia", "Japan", 1, 1, "WC R16", 2022),
    ("Croatia", "Brazil", 1, 1, "WC QF", 2022),
    ("Croatia", "Argentina", 0, 3, "WC SF", 2022),
    ("Croatia", "Morocco", 2, 1, "WC 3rd", 2022),
    ("Morocco", "Croatia", 0, 0, "WC Group", 2022),
    ("Morocco", "Belgium", 2, 0, "WC Group", 2022),
    ("Morocco", "Canada", 2, 1, "WC Group", 2022),
    ("Morocco", "Spain", 0, 0, "WC R16", 2022),
    ("Morocco", "Portugal", 1, 0, "WC QF", 2022),
    ("Morocco", "France", 0, 2, "WC SF", 2022),
    ("Morocco", "Croatia", 1, 2, "WC 3rd", 2022),
    ("Portugal", "Ghana", 3, 2, "WC Group", 2022),
    ("Portugal", "Uruguay", 2, 0, "WC Group", 2022),
    ("Portugal", "South Korea", 1, 2, "WC Group", 2022),
    ("Portugal", "Switzerland", 6, 1, "WC R16", 2022),
    ("Portugal", "Morocco", 0, 1, "WC QF", 2022),
    ("Japan", "Germany", 2, 1, "WC Group", 2022),
    ("Japan", "Costa Rica", 0, 1, "WC Group", 2022),
    ("Japan", "Spain", 2, 1, "WC Group", 2022),
    ("Japan", "Croatia", 1, 1, "WC R16", 2022),
    ("Belgium", "Canada", 1, 0, "WC Group", 2022),
    ("Belgium", "Morocco", 0, 2, "WC Group", 2022),
    ("Belgium", "Croatia", 0, 0, "WC Group", 2022),
    ("USA", "Wales", 1, 1, "WC Group", 2022),
    ("USA", "England", 0, 0, "WC Group", 2022),
    ("USA", "Iran", 1, 0, "WC Group", 2022),
    ("USA", "Netherlands", 1, 3, "WC R16", 2022),
    ("Germany", "Japan", 1, 2, "WC Group", 2022),
    ("Germany", "Spain", 1, 1, "WC Group", 2022),
    ("Germany", "Costa Rica", 4, 2, "WC Group", 2022),
    ("Uruguay", "South Korea", 0, 0, "WC Group", 2022),
    ("Uruguay", "Portugal", 0, 2, "WC Group", 2022),
    ("Uruguay", "Ghana", 2, 0, "WC Group", 2022),
    ("Switzerland", "Cameroon", 1, 0, "WC Group", 2022),
    ("Switzerland", "Brazil", 0, 1, "WC Group", 2022),
    ("Switzerland", "Serbia", 3, 2, "WC Group", 2022),
    ("Switzerland", "Portugal", 1, 6, "WC R16", 2022),
    ("Senegal", "Netherlands", 0, 2, "WC Group", 2022),
    ("Senegal", "Qatar", 3, 1, "WC Group", 2022),
    ("Senegal", "Ecuador", 2, 1, "WC Group", 2022),
    ("Senegal", "England", 0, 3, "WC R16", 2022),
    ("Ecuador", "Qatar", 2, 0, "WC Group", 2022),
    ("Ecuador", "Netherlands", 1, 1, "WC Group", 2022),
    ("Ecuador", "Senegal", 1, 2, "WC Group", 2022),
    ("Iran", "England", 2, 6, "WC Group", 2022),
    ("Iran", "Wales", 2, 0, "WC Group", 2022),
    ("Iran", "USA", 0, 1, "WC Group", 2022),
    ("South Korea", "Uruguay", 0, 0, "WC Group", 2022),
    ("South Korea", "Ghana", 2, 3, "WC Group", 2022),
    ("South Korea", "Portugal", 2, 1, "WC Group", 2022),
    ("South Korea", "Brazil", 1, 4, "WC R16", 2022),
    ("Australia", "France", 1, 4, "WC Group", 2022),
    ("Australia", "Tunisia", 1, 0, "WC Group", 2022),
    ("Australia", "Denmark", 1, 0, "WC Group", 2022),
    ("Australia", "Argentina", 1, 2, "WC R16", 2022),
    ("Canada", "Belgium", 0, 1, "WC Group", 2022),
    ("Canada", "Croatia", 1, 4, "WC Group", 2022),
    ("Canada", "Morocco", 1, 2, "WC Group", 2022),
    ("Mexico", "Poland", 0, 0, "WC Group", 2022),
    ("Mexico", "Argentina", 0, 2, "WC Group", 2022),
    ("Mexico", "Saudi Arabia", 2, 1, "WC Group", 2022),
    ("Ghana", "Portugal", 2, 3, "WC Group", 2022),
    ("Ghana", "South Korea", 3, 2, "WC Group", 2022),
    ("Ghana", "Uruguay", 0, 2, "WC Group", 2022),
    ("Tunisia", "Denmark", 0, 0, "WC Group", 2022),
    ("Tunisia", "Australia", 0, 1, "WC Group", 2022),
    ("Tunisia", "France", 1, 0, "WC Group", 2022),
    ("Qatar", "Ecuador", 0, 2, "WC Group", 2022),
    ("Qatar", "Senegal", 1, 3, "WC Group", 2022),
    ("Qatar", "Netherlands", 0, 2, "WC Group", 2022),
    ("Saudi Arabia", "Argentina", 2, 1, "WC Group", 2022),
    ("Saudi Arabia", "Poland", 0, 2, "WC Group", 2022),
    ("Saudi Arabia", "Mexico", 1, 2, "WC Group", 2022),
]

# Attack/Defense strength coefficients for Poisson model (based on WC 2014-2022)
# attack > 1.0 = scores more than average, defense < 1.0 = concedes less than average
POISSON_PARAMS = {
    "France": {"attack": 1.9, "defense": 0.7},
    "Spain": {"attack": 1.7, "defense": 0.8},
    "Argentina": {"attack": 1.5, "defense": 0.6},
    "England": {"attack": 1.6, "defense": 0.7},
    "Portugal": {"attack": 1.3, "defense": 0.9},
    "Brazil": {"attack": 1.6, "defense": 0.8},
    "Netherlands": {"attack": 1.4, "defense": 0.8},
    "Morocco": {"attack": 0.9, "defense": 0.7},
    "Belgium": {"attack": 1.2, "defense": 1.0},
    "Germany": {"attack": 1.5, "defense": 1.0},
    "Croatia": {"attack": 1.1, "defense": 0.9},
    "Colombia": {"attack": 1.1, "defense": 1.0},
    "Senegal": {"attack": 1.0, "defense": 1.0},
    "Mexico": {"attack": 0.8, "defense": 1.0},
    "United States": {"attack": 0.9, "defense": 1.0},
    "Uruguay": {"attack": 1.0, "defense": 0.9},
    "Japan": {"attack": 1.1, "defense": 0.9},
    "Switzerland": {"attack": 0.9, "defense": 1.0},
    "Norway": {"attack": 1.1, "defense": 1.1},
    "South Korea": {"attack": 1.0, "defense": 1.2},
    "Austria": {"attack": 1.0, "defense": 1.1},
    "Iran": {"attack": 0.7, "defense": 0.9},
    "Ecuador": {"attack": 0.9, "defense": 1.1},
    "Turkey": {"attack": 1.0, "defense": 1.1},
    "Sweden": {"attack": 0.9, "defense": 1.0},
    "Australia": {"attack": 0.7, "defense": 1.2},
    "Scotland": {"attack": 0.9, "defense": 1.1},
    "Czechia": {"attack": 0.9, "defense": 1.1},
    "Panama": {"attack": 0.5, "defense": 1.6},
    "Canada": {"attack": 0.8, "defense": 1.3},
    "Egypt": {"attack": 0.8, "defense": 1.1},
    "Algeria": {"attack": 0.9, "defense": 1.2},
    "Paraguay": {"attack": 0.7, "defense": 1.1},
    "Tunisia": {"attack": 0.7, "defense": 1.0},
    "Ivory Coast": {"attack": 0.8, "defense": 1.2},
    "Ghana": {"attack": 0.9, "defense": 1.3},
    "Bosnia and Herzegovina": {"attack": 0.8, "defense": 1.2},
    "South Africa": {"attack": 0.7, "defense": 1.2},
    "Qatar": {"attack": 0.6, "defense": 1.4},
    "Saudi Arabia": {"attack": 0.7, "defense": 1.3},
    "Jordan": {"attack": 0.6, "defense": 1.3},
    "Uzbekistan": {"attack": 0.6, "defense": 1.3},
    "Iraq": {"attack": 0.6, "defense": 1.3},
    "Cape Verde": {"attack": 0.6, "defense": 1.4},
    "DR Congo": {"attack": 0.6, "defense": 1.4},
    "Haiti": {"attack": 0.4, "defense": 1.7},
    "New Zealand": {"attack": 0.5, "defense": 1.5},
    "Curacao": {"attack": 0.4, "defense": 1.8},
}

# Average goals per game in World Cups
WC_AVG_GOALS = 2.5

WORLD_CUP_HISTORY = {
    "Argentina": (5, "Winner", 2022), "Australia": (5, "Round of 16", 2022),
    "Austria": (0, "Third place", 1954), "Belgium": (4, "Third place", 2018),
    "Bosnia and Herzegovina": (1, "Group stage", 2014), "Brazil": (5, "Winner", 2002),
    "Canada": (1, "Group stage", 2022), "Cape Verde": (0, "Debut", None),
    "Colombia": (3, "Quarter-finals", 2014), "Croatia": (5, "Runners-up", 2018),
    "Curacao": (0, "Debut", None), "Czech Republic": (1, "Group stage", 2006), "Czechia": (1, "Group stage", 2006),
    "DR Congo": (0, "Group stage", 1974), "Ecuador": (3, "Round of 16", 2006),
    "Egypt": (1, "Group stage", 2018), "England": (5, "Runners-up", 2022),
    "France": (5, "Winner", 2018), "Germany": (4, "Winner", 2014),
    "Ghana": (4, "Quarter-finals", 2010), "Haiti": (0, "Group stage", 1974),
    "Iran": (4, "Group stage", 2022), "Iraq": (0, "Group stage", 1986),
    "Ivory Coast": (3, "Group stage", 2014), "Japan": (5, "Round of 16", 2022),
    "Jordan": (0, "Debut", None), "Mexico": (5, "Quarter-finals", 1986),
    "Morocco": (3, "Fourth place", 2022), "Netherlands": (4, "Runners-up", 2010),
    "New Zealand": (0, "Group stage", 2010), "Norway": (0, "Round of 16", 1998),
    "Panama": (1, "Group stage", 2018), "Paraguay": (2, "Quarter-finals", 2010),
    "Portugal": (5, "Third place", 1966), "Qatar": (1, "Group stage", 2022),
    "Saudi Arabia": (3, "Round of 16", 1994), "Scotland": (0, "Group stage", 1998),
    "Senegal": (3, "Quarter-finals", 2002), "South Africa": (1, "Group stage", 2010),
    "South Korea": (5, "Fourth place", 2002), "Spain": (5, "Winner", 2010),
    "Sweden": (2, "Runners-up", 1958), "Switzerland": (5, "Quarter-finals", 1954),
    "Tunisia": (4, "Group stage", 2022), "Turkey": (1, "Third place", 2002),
    "United States": (3, "Round of 16", 2014), "Uruguay": (4, "Fourth place", 2010),
    "Algeria": (4, "Round of 16", 2014), "Uzbekistan": (0, "Debut", None),
}

RECENT_FORM_MODIFIERS = {
    "Argentina": 15, "Brazil": -10, "England": 10, "France": 20, "Germany": 5,
    "Netherlands": 5, "Portugal": 10, "Spain": 20, "Belgium": -15, "Croatia": -5,
    "Morocco": 10, "Colombia": 5, "Uruguay": 0, "Japan": 10, "United States": 5,
    "Mexico": 0, "Senegal": 0, "Switzerland": -5, "Norway": 15, "Austria": 10,
    "Turkey": 10, "Sweden": 5, "Scotland": 10, "Czech Republic": 5, "Czechia": 5, "Canada": 10,
    "Ecuador": 5, "Australia": 0, "South Korea": 0, "Iran": -5, "Paraguay": 0,
    "Panama": 5, "Algeria": 10, "Egypt": 5, "Tunisia": -5, "Ivory Coast": 5,
    "Ghana": 5, "South Africa": 5, "Qatar": -10, "Saudi Arabia": -10,
    "Uzbekistan": 10, "Jordan": 5, "Iraq": 5, "Cape Verde": 10, "DR Congo": 0,
    "Bosnia and Herzegovina": 0, "Haiti": -5, "New Zealand": -5, "Curacao": 0,
}

HOST_NATIONS = {"United States", "Mexico", "Canada"}

# Recent World Cup performance data (2018, 2022)
RECENT_WC_PERFORMANCE = {
    "Argentina":    {"appearances": 2, "best": "Winner",       "2022_stage": "Winner",       "2022_points": 18,  "2022_gd": 10,  "2018_stage": "Round of 16", "2018_points": 9,  "2018_gd": 0},
    "France":       {"appearances": 2, "best": "Winner",       "2022_stage": "Runners-up",   "2022_points": 15,  "2022_gd": 4,   "2018_stage": "Winner",      "2018_points": 15, "2018_gd": 8},
    "Croatia":      {"appearances": 2, "best": "Runners-up",   "2022_stage": "Third place",  "2022_points": 10,  "2022_gd": 2,   "2018_stage": "Runners-up",   "2018_points": 13, "2018_gd": 8},
    "Morocco":      {"appearances": 2, "best": "Fourth place", "2022_stage": "Fourth place", "2022_points": 11,  "2022_gd": 3,   "2018_stage": "Group stage",  "2018_points": 1,  "2018_gd": -2},
    "England":      {"appearances": 2, "best": "Runners-up",   "2022_stage": "Quarter-finals","2022_points":10,   "2022_gd": 7,   "2018_stage": "Fourth place", "2018_points": 12, "2018_gd": 5},
    "Belgium":      {"appearances": 2, "best": "Third place",  "2022_stage": "Group stage",  "2022_points": 4,   "2022_gd": -1,  "2018_stage": "Third place",  "2018_points": 15, "2018_gd": 8},
    "Brazil":       {"appearances": 2, "best": "Winner",       "2022_stage": "Quarter-finals","2022_points":10,   "2022_gd": 5,   "2018_stage": "Quarter-finals","2018_points":10, "2018_gd": 5},
    "Netherlands":  {"appearances": 1, "best": "Runners-up",   "2022_stage": "Quarter-finals","2022_points":8,    "2022_gd": 3,   "2018_stage": None,          "2018_points": 0, "2018_gd": 0},
    "Portugal":     {"appearances": 2, "best": "Round of 16",  "2022_stage": "Quarter-finals","2022_points":9,    "2022_gd": 3,   "2018_stage": "Round of 16",  "2018_points": 5, "2018_gd": 1},
    "Spain":        {"appearances": 2, "best": "Winner",       "2022_stage": "Round of 16",  "2022_points": 4,   "2022_gd": 6,   "2018_stage": "Round of 16",  "2018_points": 5, "2018_gd": -1},
    "Germany":      {"appearances": 2, "best": "Winner",       "2022_stage": "Group stage",  "2022_points": 4,   "2022_gd": -1,  "2018_stage": "Group stage",  "2018_points": 3, "2018_gd": -2},
    "Japan":        {"appearances": 2, "best": "Round of 16",  "2022_stage": "Round of 16",  "2022_points": 6,   "2022_gd": 1,   "2018_stage": "Round of 16",  "2018_points": 4, "2018_gd": 0},
    "Switzerland":  {"appearances": 2, "best": "Quarter-finals","2022_stage": "Round of 16", "2022_points": 4,   "2022_gd": 0,   "2018_stage": "Round of 16",  "2018_points": 5, "2018_gd": -1},
    "Senegal":      {"appearances": 2, "best": "Quarter-finals","2022_stage": "Round of 16", "2022_points": 6,   "2022_gd": -1,  "2018_stage": "Group stage",  "2018_points": 4, "2018_gd": -2},
    "United States":{"appearances": 1, "best": "Round of 16",  "2022_stage": "Round of 16",  "2022_points": 5,   "2022_gd": 0,   "2018_stage": None,          "2018_points": 0, "2018_gd": 0},
    "Australia":    {"appearances": 2, "best": "Round of 16",  "2022_stage": "Round of 16",  "2022_points": 6,   "2022_gd": -2,  "2018_stage": "Group stage",  "2018_points": 1, "2018_gd": -3},
    "South Korea":  {"appearances": 2, "best": "Fourth place", "2022_stage": "Round of 16",  "2022_points": 4,   "2022_gd": -1,  "2018_stage": "Group stage",  "2018_points": 1, "2018_gd": 0},
    "Poland":       {"appearances": 2, "best": "Round of 16",  "2022_stage": "Round of 16",  "2022_points": 4,   "2022_gd": -1,  "2018_stage": "Group stage",  "2018_points": 3, "2018_gd": -2},
    "Ghana":        {"appearances": 1, "best": "Quarter-finals","2022_stage": "Group stage", "2022_points": 3,   "2022_gd": 0,   "2018_stage": None,          "2018_points": 0, "2018_gd": 0},
    "Iran":         {"appearances": 2, "best": "Group stage",  "2022_stage": "Group stage",  "2022_points": 3,   "2022_gd": -3,  "2018_stage": "Group stage",  "2018_points": 1, "2018_gd": -2},
    "Ecuador":      {"appearances": 1, "best": "Group stage",  "2022_stage": "Group stage",  "2022_points": 4,   "2022_gd": 0,   "2018_stage": None,          "2018_points": 0, "2018_gd": 0},
    "Cameroon":     {"appearances": 2, "best": "Quarter-finals","2022_stage": "Group stage", "2022_points": 4,   "2022_gd": -2,  "2018_stage": None,          "2018_points": 0, "2018_gd": 0},
    "Mexico":       {"appearances": 2, "best": "Quarter-finals","2022_stage": "Group stage", "2022_points": 4,   "2022_gd": -2,  "2018_stage": "Round of 16",  "2018_points": 6, "2018_gd": -1},
    "Canada":       {"appearances": 1, "best": "Group stage",  "2022_stage": "Group stage",  "2022_points": 0,   "2022_gd": -7,  "2018_stage": None,          "2018_points": 0, "2018_gd": 0},
    "Qatar":        {"appearances": 1, "best": "Group stage",  "2022_stage": "Group stage",  "2022_points": 0,   "2022_gd": -6,  "2018_stage": None,          "2018_points": 0, "2018_gd": 0},
    "Saudi Arabia": {"appearances": 1, "best": "Round of 16",  "2022_stage": "Group stage",  "2022_points": 3,   "2022_gd": -2,  "2018_stage": None,          "2018_points": 0, "2018_gd": 0},
    "Tunisia":      {"appearances": 2, "best": "Group stage",  "2022_stage": "Group stage",  "2022_points": 4,   "2022_gd": 0,   "2018_stage": "Group stage",  "2018_points": 3, "2018_gd": -4},
    "Costa Rica":   {"appearances": 2, "best": "Quarter-finals","2022_stage": "Group stage", "2022_points": 1,   "2022_gd": -6,  "2018_stage": "Group stage",  "2018_points": 1, "2018_gd": -6},
    "Uruguay":      {"appearances": 2, "best": "Winner",       "2022_stage": "Group stage",  "2022_points": 4,   "2022_gd": 0,   "2018_stage": "Quarter-finals","2018_points":9,  "2018_gd": 3},
    "Colombia":     {"appearances": 1, "best": "Quarter-finals","2022_stage": None,          "2022_points": 0,   "2022_gd": 0,   "2018_stage": "Round of 16",  "2018_points": 6, "2018_gd": 1},
    "Serbia":       {"appearances": 2, "best": "Group stage",  "2022_stage": "Group stage",  "2022_points": 1,   "2022_gd": -2,  "2018_stage": "Group stage",  "2018_points": 3, "2018_gd": -2},
    "Sweden":       {"appearances": 1, "best": "Runners-up",   "2022_stage": None,           "2022_points": 0,   "2022_gd": 0,   "2018_stage": "Quarter-finals","2018_points":6,  "2018_gd": 2},
    "Denmark":      {"appearances": 2, "best": "Quarter-finals","2022_stage": "Group stage", "2022_points": 1,   "2022_gd": -2,  "2018_stage": "Round of 16",  "2018_points": 5, "2018_gd": 1},
    "Algeria":           {"appearances": 0, "best": "Round of 16", "2022_stage": None, "2022_points": 0, "2022_gd": 0, "2018_stage": None, "2018_points": 0, "2018_gd": 0},
    "Austria":           {"appearances": 0, "best": "Third place", "2022_stage": None, "2022_points": 0, "2022_gd": 0, "2018_stage": None, "2018_points": 0, "2018_gd": 0},
    "Bosnia and Herzegovina": {"appearances": 0, "best": "Group stage", "2022_stage": None, "2022_points": 0, "2022_gd": 0, "2018_stage": None, "2018_points": 0, "2018_gd": 0},
    "Cape Verde":        {"appearances": 0, "best": "Debut",      "2022_stage": None, "2022_points": 0, "2022_gd": 0, "2018_stage": None, "2018_points": 0, "2018_gd": 0},
    "Curacao":           {"appearances": 0, "best": "Debut",      "2022_stage": None, "2022_points": 0, "2022_gd": 0, "2018_stage": None, "2018_points": 0, "2018_gd": 0},
    "Czechia":           {"appearances": 0, "best": "Group stage", "2022_stage": None, "2022_points": 0, "2022_gd": 0, "2018_stage": None, "2018_points": 0, "2018_gd": 0},
    "DR Congo":          {"appearances": 0, "best": "Group stage", "2022_stage": None, "2022_points": 0, "2022_gd": 0, "2018_stage": None, "2018_points": 0, "2018_gd": 0},
    "Egypt":             {"appearances": 0, "best": "Group stage", "2022_stage": None, "2022_points": 0, "2022_gd": 0, "2018_stage": "Group stage", "2018_points": 1, "2018_gd": -3},
    "Haiti":             {"appearances": 0, "best": "Group stage", "2022_stage": None, "2022_points": 0, "2022_gd": 0, "2018_stage": None, "2018_points": 0, "2018_gd": 0},
    "Iraq":              {"appearances": 0, "best": "Group stage", "2022_stage": None, "2022_points": 0, "2022_gd": 0, "2018_stage": None, "2018_points": 0, "2018_gd": 0},
    "Ivory Coast":       {"appearances": 0, "best": "Group stage", "2022_stage": None, "2022_points": 0, "2022_gd": 0, "2018_stage": None, "2018_points": 0, "2018_gd": 0},
    "Jordan":            {"appearances": 0, "best": "Debut",      "2022_stage": None, "2022_points": 0, "2022_gd": 0, "2018_stage": None, "2018_points": 0, "2018_gd": 0},
    "New Zealand":       {"appearances": 0, "best": "Group stage", "2022_stage": None, "2022_points": 0, "2022_gd": 0, "2018_stage": None, "2018_points": 0, "2018_gd": 0},
    "Norway":            {"appearances": 0, "best": "Round of 16", "2022_stage": None, "2022_points": 0, "2022_gd": 0, "2018_stage": None, "2018_points": 0, "2018_gd": 0},
    "Panama":            {"appearances": 1, "best": "Group stage", "2022_stage": None, "2022_points": 0, "2022_gd": 0, "2018_stage": "Group stage", "2018_points": 0, "2018_gd": -9},
    "Paraguay":          {"appearances": 0, "best": "Quarter-finals","2022_stage": None, "2022_points": 0, "2022_gd": 0, "2018_stage": None, "2018_points": 0, "2018_gd": 0},
    "Scotland":          {"appearances": 0, "best": "Group stage", "2022_stage": None, "2022_points": 0, "2022_gd": 0, "2018_stage": None, "2018_points": 0, "2018_gd": 0},
    "South Africa":      {"appearances": 0, "best": "Group stage", "2022_stage": None, "2022_points": 0, "2022_gd": 0, "2018_stage": None, "2018_points": 0, "2018_gd": 0},
    "Turkey":            {"appearances": 0, "best": "Third place", "2022_stage": None, "2022_points": 0, "2022_gd": 0, "2018_stage": None, "2018_points": 0, "2018_gd": 0},
    "Uzbekistan":        {"appearances": 0, "best": "Debut",      "2022_stage": None, "2022_points": 0, "2022_gd": 0, "2018_stage": None, "2018_points": 0, "2018_gd": 0},
}

# Expected Goals (xG) data per team - based on recent performances
XG_DATA = {
    "Argentina": {"xg_for": 2.1, "xg_against": 0.7, "shots_per_game": 14.2, "shots_on_target_pct": 0.38},
    "France":    {"xg_for": 2.3, "xg_against": 0.9, "shots_per_game": 15.1, "shots_on_target_pct": 0.40},
    "Spain":     {"xg_for": 2.2, "xg_against": 0.8, "shots_per_game": 16.3, "shots_on_target_pct": 0.37},
    "England":   {"xg_for": 2.0, "xg_against": 0.8, "shots_per_game": 14.8, "shots_on_target_pct": 0.36},
    "Portugal":  {"xg_for": 1.8, "xg_against": 1.0, "shots_per_game": 13.5, "shots_on_target_pct": 0.35},
    "Brazil":    {"xg_for": 1.9, "xg_against": 0.9, "shots_per_game": 14.6, "shots_on_target_pct": 0.34},
    "Netherlands":{"xg_for": 1.7, "xg_against": 0.9, "shots_per_game": 12.8, "shots_on_target_pct": 0.33},
    "Germany":   {"xg_for": 2.0, "xg_against": 1.1, "shots_per_game": 14.9, "shots_on_target_pct": 0.36},
    "Belgium":   {"xg_for": 1.5, "xg_against": 1.1, "shots_per_game": 11.8, "shots_on_target_pct": 0.32},
    "Croatia":   {"xg_for": 1.4, "xg_against": 1.0, "shots_per_game": 11.2, "shots_on_target_pct": 0.31},
    "Morocco":   {"xg_for": 1.2, "xg_against": 0.8, "shots_per_game": 10.5, "shots_on_target_pct": 0.29},
    "Uruguay":   {"xg_for": 1.3, "xg_against": 1.0, "shots_per_game": 10.8, "shots_on_target_pct": 0.30},
    "Japan":     {"xg_for": 1.3, "xg_against": 0.9, "shots_per_game": 10.2, "shots_on_target_pct": 0.28},
    "Colombia":  {"xg_for": 1.3, "xg_against": 1.1, "shots_per_game": 10.0, "shots_on_target_pct": 0.29},
    "Senegal":   {"xg_for": 1.2, "xg_against": 1.0, "shots_per_game": 9.5,  "shots_on_target_pct": 0.28},
    "Switzerland":{"xg_for": 1.1, "xg_against": 1.0, "shots_per_game": 9.2,  "shots_on_target_pct": 0.27},
    "United States":{"xg_for": 1.2, "xg_against": 1.1, "shots_per_game": 10.1, "shots_on_target_pct": 0.28},
    "Mexico":    {"xg_for": 1.0, "xg_against": 1.2, "shots_per_game": 9.0,  "shots_on_target_pct": 0.26},
    "Austria":   {"xg_for": 1.2, "xg_against": 1.2, "shots_per_game": 9.8,  "shots_on_target_pct": 0.28},
    "Norway":    {"xg_for": 1.3, "xg_against": 1.2, "shots_per_game": 10.5, "shots_on_target_pct": 0.29},
    "South Korea":{"xg_for": 1.1, "xg_against": 1.2, "shots_per_game": 9.4,  "shots_on_target_pct": 0.26},
    "Turkey":    {"xg_for": 1.2, "xg_against": 1.3, "shots_per_game": 9.6,  "shots_on_target_pct": 0.27},
    "Sweden":    {"xg_for": 1.1, "xg_against": 1.1, "shots_per_game": 9.0,  "shots_on_target_pct": 0.26},
    "Ecuador":   {"xg_for": 1.1, "xg_against": 1.2, "shots_per_game": 8.8,  "shots_on_target_pct": 0.26},
    "Iran":      {"xg_for": 0.8, "xg_against": 1.3, "shots_per_game": 7.5,  "shots_on_target_pct": 0.24},
    "Australia": {"xg_for": 0.9, "xg_against": 1.4, "shots_per_game": 7.8,  "shots_on_target_pct": 0.24},
    "Ghana":     {"xg_for": 1.0, "xg_against": 1.3, "shots_per_game": 8.2,  "shots_on_target_pct": 0.25},
    "Ivory Coast":{"xg_for": 1.0, "xg_against": 1.3, "shots_per_game": 8.5,  "shots_on_target_pct": 0.25},
    "Egypt":     {"xg_for": 0.9, "xg_against": 1.2, "shots_per_game": 7.8,  "shots_on_target_pct": 0.24},
    "Algeria":   {"xg_for": 1.0, "xg_against": 1.3, "shots_per_game": 8.0,  "shots_on_target_pct": 0.25},
    "Paraguay":  {"xg_for": 0.8, "xg_against": 1.3, "shots_per_game": 7.2,  "shots_on_target_pct": 0.23},
    "Tunisia":   {"xg_for": 0.8, "xg_against": 1.2, "shots_per_game": 7.0,  "shots_on_target_pct": 0.22},
    "Scotland":  {"xg_for": 1.0, "xg_against": 1.3, "shots_per_game": 8.5,  "shots_on_target_pct": 0.25},
    "Canada":    {"xg_for": 0.8, "xg_against": 1.6, "shots_per_game": 7.0,  "shots_on_target_pct": 0.22},
    "Bosnia and Herzegovina":{"xg_for": 0.8, "xg_against": 1.4, "shots_per_game": 7.0, "shots_on_target_pct": 0.22},
    "Qatar":     {"xg_for": 0.6, "xg_against": 1.8, "shots_per_game": 6.0,  "shots_on_target_pct": 0.20},
    "Saudi Arabia":{"xg_for": 0.7, "xg_against": 1.5, "shots_per_game": 6.5, "shots_on_target_pct": 0.20},
    "Panama":    {"xg_for": 0.6, "xg_against": 1.7, "shots_per_game": 6.2,  "shots_on_target_pct": 0.20},
    "South Africa":{"xg_for": 0.7, "xg_against": 1.5, "shots_per_game": 6.8, "shots_on_target_pct": 0.21},
    "Czechia":   {"xg_for": 1.0, "xg_against": 1.2, "shots_per_game": 8.0,  "shots_on_target_pct": 0.25},
    "Iraq":      {"xg_for": 0.6, "xg_against": 1.5, "shots_per_game": 6.0,  "shots_on_target_pct": 0.19},
    "Jordan":    {"xg_for": 0.6, "xg_against": 1.6, "shots_per_game": 5.8,  "shots_on_target_pct": 0.19},
    "Uzbekistan":{"xg_for": 0.6, "xg_against": 1.4, "shots_per_game": 6.0,  "shots_on_target_pct": 0.20},
    "Cape Verde": {"xg_for": 0.6, "xg_against": 1.6, "shots_per_game": 6.0, "shots_on_target_pct": 0.20},
    "DR Congo":   {"xg_for": 0.6, "xg_against": 1.6, "shots_per_game": 5.8, "shots_on_target_pct": 0.19},
    "Haiti":     {"xg_for": 0.5, "xg_against": 1.9, "shots_per_game": 5.0,  "shots_on_target_pct": 0.18},
    "New Zealand":{"xg_for": 0.6, "xg_against": 1.7, "shots_per_game": 5.5, "shots_on_target_pct": 0.18},
    "Curacao":   {"xg_for": 0.5, "xg_against": 1.9, "shots_per_game": 5.0,  "shots_on_target_pct": 0.17},
}

# Quality of opponent faced in qualifying / recent matches
# Higher = faced stronger opposition (adjusts for padded stats vs weak teams)
OPPONENT_QUALITY = {
    "France": 0.92, "Spain": 0.90, "Argentina": 0.91, "England": 0.89,
    "Portugal": 0.87, "Brazil": 0.86, "Netherlands": 0.85, "Germany": 0.84,
    "Belgium": 0.82, "Croatia": 0.81, "Italy": 0.80, "Uruguay": 0.78,
    "Morocco": 0.76, "Colombia": 0.75, "Senegal": 0.72, "Japan": 0.71,
    "Mexico": 0.70, "United States": 0.70, "Switzerland": 0.70,
    "Austria": 0.68, "Norway": 0.67, "South Korea": 0.66, "Turkey": 0.65,
    "Sweden": 0.64, "Ecuador": 0.63, "Australia": 0.62, "Scotland": 0.62,
    "Ivory Coast": 0.61, "Algeria": 0.60, "Egypt": 0.59, "Ghana": 0.58,
    "Tunisia": 0.57, "Iran": 0.57, "Paraguay": 0.58, "Czechia": 0.60,
    "Bosnia and Herzegovina": 0.56, "Canada": 0.55, "South Africa": 0.52,
    "Panama": 0.50, "Saudi Arabia": 0.48, "Qatar": 0.47, "Jordan": 0.45,
    "Uzbekistan": 0.44, "Iraq": 0.43, "Cape Verde": 0.42, "DR Congo": 0.41,
    "New Zealand": 0.40, "Haiti": 0.38, "Curacao": 0.36,
}

MANAGER_DATA = {
    "France": ("Didier Deschamps", True, 2018),
    "Argentina": ("Lionel Scaloni", True, 2022),
    "Spain": ("Luis de la Fuente", True, 2024),
    "Germany": ("Julian Nagelsmann", False, None),
    "England": ("Gareth Southgate", False, None),
    "Brazil": ("Dorival Junior", False, None),
    "Portugal": ("Roberto Martinez", True, 2016),
    "Netherlands": ("Ronald Koeman", False, None),
    "Belgium": ("Domenico Tedesco", False, None),
    "Croatia": ("Zlatko Dalic", False, None),
    "Italy": ("Luciano Spalletti", False, None),
    "Uruguay": ("Marcelo Bielsa", False, None),
    "Colombia": ("Nestor Lorenzo", False, None),
    "Morocco": ("Walid Regragui", False, None),
    "Senegal": ("Aliou Cisse", False, None),
    "Japan": ("Hajime Moriyasu", False, None),
    "South Korea": ("Hong Myung-bo", False, None),
    "United States": ("Gregg Berhalter", False, None),
    "Mexico": ("Jaime Lozano", False, None),
    "Canada": ("Jesse Marsch", False, None),
    "Switzerland": ("Murat Yakin", False, None),
    "Norway": ("Stale Solbakken", False, None),
    "Sweden": ("Jon Dahl Tomasson", False, None),
    "Scotland": ("Steve Clarke", False, None),
    "Austria": ("Ralf Rangnick", False, None),
    "Turkey": ("Vincenzo Montella", False, None),
    "Czech Republic": ("Ivan Hasek", False, None), "Czechia": ("Ivan Hasek", False, None),
    "Iran": ("Amir Ghalenoei", False, None),
    "Ecuador": ("Felix Sanchez", False, None),
    "Australia": ("Graham Arnold", False, None),
    "Algeria": ("Vladimir Petkovic", False, None),
    "Egypt": ("Hossam Hassan", False, None),
    "Tunisia": ("Kais Yaakoubi", False, None),
    "Ivory Coast": ("Emerse Fae", True, 2023),
    "Ghana": ("Otto Addo", False, None),
    "South Africa": ("Hugo Broos", True, 2021),
    "Paraguay": ("Daniel Garnero", False, None),
    "Panama": ("Thomas Christiansen", False, None),
    "Saudi Arabia": ("Roberto Mancini", True, 2020),
    "Qatar": ("Tintin Marquez", False, None),
    "Iraq": ("Jesus Casas", False, None),
    "Jordan": ("Hussein Ammouta", False, None),
    "Uzbekistan": ("Srecko Katanec", False, None),
    "Bosnia and Herzegovina": ("Sergej Barbarez", False, None),
    "Cape Verde": ("Bubista", False, None),
    "DR Congo": ("Sebastien Desabre", False, None),
    "Haiti": ("Sebastien Migne", False, None),
    "New Zealand": ("Darren Bazeley", False, None),
    "Curacao": ("Dick Advocaat", False, None),
}


def get_manager(team: str) -> dict:
    m = MANAGER_DATA.get(team, ("Unknown", False, None))
    return {"name": m[0], "won_tournament": m[1], "trophy_year": m[2]}


@dataclass
class Team:
    name: str
    fifa_rank: int
    fifa_points: float
    confederation: str
    appearances: int
    best_result: str
    recent_form: int = 0
    attack: float = 1.0
    defense: float = 1.0

    def effective_strength(self) -> float:
        return self.fifa_points + self.recent_form * 2.5


def build_h2h_database() -> Dict[Tuple[str, str], List[Tuple[int, int, str, int]]]:
    db = {}
    for a, b, ga, gb, comp, year in HEAD_TO_HEAD_MATCHES:
        key = tuple(sorted([a, b]))
        if key not in db:
            db[key] = []
        db[key].append((ga, gb, comp, year))
    return db


H2H_DATABASE = build_h2h_database()


def get_h2h(team_a: str, team_b: str) -> dict:
    key = tuple(sorted([team_a, team_b]))
    matches = H2H_DATABASE.get(key, [])

    a_wins = sum(1 for ga, gb, _, _ in matches
                 if (team_a == key[0] and ga > gb) or (team_a == key[1] and gb > ga))
    b_wins = sum(1 for ga, gb, _, _ in matches
                 if (team_b == key[0] and ga > gb) or (team_b == key[1] and gb > ga))
    draws = len(matches) - a_wins - b_wins
    a_goals = sum(ga if team_a == key[0] else gb for ga, gb, _, _ in matches)
    b_goals = sum(gb if team_a == key[0] else ga for ga, gb, _, _ in matches)

    return {
        "matches": matches,
        "total": len(matches),
        f"{team_a}_wins": a_wins,
        f"{team_b}_wins": b_wins,
        "draws": draws,
        f"{team_a}_goals": a_goals,
        f"{team_b}_goals": b_goals,
    }


def get_team_data(name: str) -> Team:
    points = FIFA_RANKINGS_APRIL_2026.get(name, 1400)
    sorted_teams = sorted(FIFA_RANKINGS_APRIL_2026.items(), key=lambda x: -x[1])
    rank = next(i + 1 for i, (t, _) in enumerate(sorted_teams) if t == name)
    history = WORLD_CUP_HISTORY.get(name, (0, "Debut", None))
    form = RECENT_FORM_MODIFIERS.get(name, 0)
    params = POISSON_PARAMS.get(name, {"attack": 0.8, "defense": 1.2})

    uefa = {"England","France","Germany","Spain","Portugal","Netherlands","Belgium","Croatia",
            "Switzerland","Austria","Norway","Sweden","Scotland","Czech Republic","Czechia","Turkey","Bosnia and Herzegovina"}
    concacaf = {"United States","Mexico","Canada","Panama","Curacao","Haiti"}
    conmebol = {"Argentina","Brazil","Colombia","Uruguay","Ecuador","Paraguay"}
    caf = {"Morocco","Senegal","Tunisia","Egypt","Algeria","Ghana","Cape Verde","Ivory Coast","South Africa","DR Congo"}
    afc = {"Japan","Iran","South Korea","Australia","Qatar","Saudi Arabia","Uzbekistan","Jordan","Iraq"}
    ofc = {"New Zealand"}

    if name in uefa: conf = "UEFA"
    elif name in concacaf: conf = "CONCACAF"
    elif name in conmebol: conf = "CONMEBOL"
    elif name in caf: conf = "CAF"
    elif name in afc: conf = "AFC"
    elif name in ofc: conf = "OFC"
    else: conf = "Unknown"

    return Team(name=name, fifa_rank=rank, fifa_points=points,
                confederation=conf, appearances=history[0],
                best_result=history[1], recent_form=form,
                attack=params["attack"], defense=params["defense"])


def get_all_teams() -> dict[str, Team]:
    return {name: get_team_data(name) for name in QUALIFIED_TEAMS}


def get_group_teams(group_name: str) -> list[Team]:
    if group_name not in WORLD_CUP_GROUPS:
        raise ValueError(f"Invalid group: {group_name}")
    return [get_team_data(name) for name in WORLD_CUP_GROUPS[group_name]]
