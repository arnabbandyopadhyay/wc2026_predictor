"""Streamlit dashboard for WC2026 Predictor."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from data import (FIFA_RANKINGS_APRIL_2026, WORLD_CUP_GROUPS,
                                   RECENT_FORM_MODIFIERS, HOST_NATIONS,
                                   get_all_teams, get_team_data, get_group_teams, get_h2h, get_manager)
from tournament import TournamentSimulator
from poisson import predict_match_poisson, predict_match_enhanced, predict_group_poisson, poisson_prob
from datetime import date
from schedule import (SCHEDULE, get_fixtures_for_date, get_fixtures_for_team,
                      get_todays_fixtures, get_upcoming_fixtures,
                      get_fixtures_by_matchday, MatchFixture)
from analysis import analyze_team, compare_teams
from scraper import scraper

st.set_page_config(page_title="WC 2026 Predictor", page_icon="🏆",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    * { font-family: 'Inter', -apple-system, sans-serif; }

    .main > div { padding: 1.5rem 2.5rem; max-width: 100% !important; }
    .block-container { max-width: 100% !important; padding-left: 2rem !important; padding-right: 2rem !important; }
    .stApp { background: #f4f6fb; }

    h1 { color: #1a1a2e !important; font-weight: 800 !important; font-size: 2rem !important; letter-spacing: -0.5px; }
    h2 { color: #1a1a2e !important; font-weight: 700 !important; font-size: 1.5rem !important; }
    h3 { color: #1a1a2e !important; font-weight: 600 !important; font-size: 1.2rem !important; }
    h4 { color: #2d2d4e !important; font-weight: 600 !important; }
    p, li, span, div { color: #3d3d5c; }

    .team-card {
        background: white;
        border: 1px solid #e8ecf4;
        border-radius: 14px; padding: 1rem; margin: 0.4rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: all 0.15s ease;
    }
    .team-card:hover {
        border-color: #c0c8de;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    }
    .team-card strong { color: #1a1a2e; }

    .stMetric {
        background: white; padding: 0.8rem 1.2rem; border-radius: 12px;
        border: 1px solid #e8ecf4; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .stMetric label { color: #6b6b8d !important; font-size: 0.8rem !important; font-weight: 500 !important; text-transform: uppercase; letter-spacing: 0.3px; }
    .stMetric [data-testid="stMetricValue"] { color: #1a1a2e !important; font-size: 1.7rem !important; font-weight: 800 !important; }
    .stMetric [data-testid="stMetricDelta"] { color: #8888bb !important; }

    .stButton button {
        background: linear-gradient(135deg, #c8e6c9, #a5d6a7);
        color: white; border: none; font-weight: 700; font-size: 0.9rem;
        border-radius: 10px; padding: 0.5rem 1.5rem;
        box-shadow: 0 2px 8px rgba(76,175,80,0.15);
        transition: all 0.15s ease;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #dcedc8, #c5e1a5);
        box-shadow: 0 4px 16px rgba(76,175,80,0.2);
        transform: translateY(-1px);
    }

    .stDataFrame {
        background: white; border-radius: 12px; border: 1px solid #e8ecf4;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .stDataFrame td { color: #3d3d5c; padding: 0.6rem 0.8rem !important; }
    .stDataFrame th { color: #1a1a2e; background: #f8f9fd; font-weight: 600; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.3px; }

    .stSelectbox label { color: #3d3d5c !important; font-weight: 500 !important; }
    .stSelectbox div[data-baseweb="select"] { background: white; border: 1px solid #dce0ec; border-radius: 10px; }
    .stSelectbox div[data-baseweb="select"] * { color: #1a1a2e !important; }

    .stMultiSelect label { color: #3d3d5c !important; font-weight: 500 !important; }
    .stSlider label { color: #3d3d5c !important; font-weight: 500 !important; }

    section[data-testid="stSidebar"] {
        background: white;
        border-right: 1px solid #e8ecf4;
    }
    section[data-testid="stSidebar"] p { color: #6b6b8d; }
    section[data-testid="stSidebar"] .stRadio label {
        color: #3d3d5c; padding: 0.4rem 1rem;
        border-radius: 8px; font-weight: 500;
        transition: all 0.1s ease;
    }
    section[data-testid="stSidebar"] .stRadio label:hover { background: #f0f2f8; }
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] { gap: 2px; }

    .stExpander {
        background: white; border: 1px solid #e8ecf4; border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .stExpander summary { color: #1a1a2e !important; font-weight: 600 !important; }

    .stSpinner { color: #4361ee; }
    .stSuccess { background: #e8f5e9; border-color: #a5d6a7; color: #2e7d32; }

    a { color: #4361ee; font-weight: 500; }
    a:hover { color: #3a0ca3; }

    hr { border-color: #e8ecf4; margin: 1.5rem 0; }

    section[data-testid="stFileUploader"] { background: white; border: 1px dashed #dce0ec; border-radius: 12px; }

    .stTabs [data-baseweb="tab-list"] { gap: 0; background: #f8f9fd; border-radius: 10px; padding: 3px; }
    .stTabs [data-baseweb="tab"] { color: #6b6b8d; padding: 0.5rem 1.2rem; border-radius: 8px; font-weight: 500; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { color: #1a1a2e; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }

    .match-row {
        background: white; border-radius: 10px; padding: 6px 12px; margin: 3px 0;
        border: 1px solid #e8ecf4; font-size: 0.88rem; color: #3d3d5c;
        transition: all 0.1s ease;
    }
    .match-row:hover { border-color: #c0c8de; }

    .group-team {
        background: white; border-radius: 8px; padding: 5px 12px; margin: 3px 0;
        border-left: 3px solid #4361ee; font-size: 0.9rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }

    .sidebar-header {
        text-align: center; padding: 1rem 0 0.5rem 0;
    }
    .sidebar-header h1 {
        font-size: 1.6rem !important; color: #4361ee !important; margin: 0;
    }
    .sidebar-header p {
        color: #8888bb; margin-top: -8px; font-size: 0.85rem;
    }
    .sidebar-footer {
        color: #b0b8d0; font-size: 0.8rem;
    }
    .st-emotion-cache-1mi2ry8 { background: white; }
</style>
""", unsafe_allow_html=True)

ALL_TEAMS = sorted(FIFA_RANKINGS_APRIL_2026.keys())

FLAGS = {
    "France":"🇫🇷","Spain":"🇪🇸","Argentina":"🇦🇷","England":"🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "Portugal":"🇵🇹","Brazil":"🇧🇷","Netherlands":"🇳🇱","Morocco":"🇲🇦",
    "Belgium":"🇧🇪","Germany":"🇩🇪","Croatia":"🇭🇷","Colombia":"🇨🇴",
    "Senegal":"🇸🇳","Mexico":"🇲🇽","United States":"🇺🇸","Uruguay":"🇺🇾",
    "Japan":"🇯🇵","Switzerland":"🇨🇭","Norway":"🇳🇴","South Korea":"🇰🇷",
    "Austria":"🇦🇹","Iran":"🇮🇷","Ecuador":"🇪🇨","Turkey":"🇹🇷",
    "Sweden":"🇸🇪","Australia":"🇦🇺","Scotland":"🏴󠁧󠁢󠁳󠁣󠁴󠁿","Czech Republic":"🇨🇿","Czechia":"🇨🇿",
    "Panama":"🇵🇦","Canada":"🇨🇦","Egypt":"🇪🇬","Algeria":"🇩🇿",
    "Paraguay":"🇵🇾","Tunisia":"🇹🇳","Ivory Coast":"🇨🇮","Ghana":"🇬🇭",
    "Bosnia and Herzegovina":"🇧🇦","South Africa":"🇿🇦","Qatar":"🇶🇦",
    "Saudi Arabia":"🇸🇦","Jordan":"🇯🇴","Uzbekistan":"🇺🇿","Iraq":"🇮🇶",
    "Cape Verde":"🇨🇻","DR Congo":"🇨🇩","Haiti":"🇭🇹","New Zealand":"🇳🇿","Curacao":"🇨🇼",
}


def flag(name):
    return FLAGS.get(name, "🏳️")


def main():
    st.sidebar.markdown("<div class='sidebar-header'><h1>🏆 WC 2026</h1><p>Predictor Dashboard</p></div>", unsafe_allow_html=True)

    page = st.sidebar.radio("Navigate", [
        "Overview", "FIFA Rankings", "Groups", "Fixtures & News",
        "Tournament Sim", "Monte Carlo", "Head-to-Head", "Team Profile"
    ], label_visibility="collapsed")

    st.sidebar.markdown("---")
    st.sidebar.markdown("<div class='sidebar-footer'>48 teams · 12 groups · 32 KO<br>Hosts: 🇺🇸 🇲🇽 🇨🇦</div>", unsafe_allow_html=True)

    if page == "Overview":
        render_overview()
    elif page == "FIFA Rankings":
        render_rankings()
    elif page == "Groups":
        render_groups()
    elif page == "Fixtures & News":
        render_fixtures()
    elif page == "Tournament Sim":
        render_tournament()
    elif page == "Monte Carlo":
        render_monte_carlo()
    elif page == "Head-to-Head":
        render_h2h()
    elif page == "Team Profile":
        render_team_profile()


def team_card(team, stat_lines, medal_idx=None):
    colors = ["#4361ee", "#7b2cbf", "#e8ecf4"]
    bc = colors[medal_idx] if medal_idx is not None and medal_idx < 3 else "#e8ecf4"
    medals = ["🥇","🥈","🥉"]
    mtag = medals[medal_idx] if medal_idx is not None and medal_idx < 3 else ""
    stats = " · ".join(stat_lines)
    return f"""
    <div class='team-card' style='border-left:3px solid {bc};'>
        <div style='font-size:1.15rem;'>{mtag} {flag(team)} <strong style='color:#1a1a2e;'>{team}</strong></div>
        <div style='color:#6b6b8d;font-size:0.83rem;margin-top:4px;'>{stats}</div>
    </div>"""


def match_line(ta, tb, sa, sb, pa, pd, pb):
    return f"""<div class='match-row'>{flag(ta)} {ta} <strong style='color:#1a1a2e;'>{sa}–{sb}</strong> {tb} {flag(tb)} <span style='color:#8888bb;font-size:0.75rem;'>| {pa:.0%}/{pd:.0%}/{pb:.0%}</span></div>"""


def render_fixtures():
    st.markdown("# 📅 Fixtures & Match Predictions")

    view = st.radio("View", ["Upcoming Matches", "Full Schedule", "World Football News"],
                     horizontal=True, label_visibility="collapsed")

    if view == "Upcoming Matches":
        today = date.today()
        if today < date(2026, 6, 11):
            st.info("🏆 The World Cup starts on June 11, 2026. Showing opening day fixtures.")
            target = date(2026, 6, 11)
        elif today > date(2026, 7, 19):
            st.success("🏆 The tournament has concluded!")
            target = date(2026, 7, 19)
        else:
            target = today

        fixtures = get_fixtures_for_date(target)
        if not fixtures:
            next_fixtures = get_upcoming_fixtures(5)
            if next_fixtures:
                target = next_fixtures[0].date
                fixtures = get_fixtures_for_date(target)

        if fixtures:
            st.markdown(f"### 📆 {target.strftime('%A, %B %d, %Y')}")
            for i, f in enumerate(fixtures):
                _render_match_card(f, i)

        upcoming = [f for f in get_upcoming_fixtures(7) if f.date > target][:8]
        if upcoming:
            st.markdown("### ⏩ Also Coming Up")
            dates_shown = set()
            for f in upcoming:
                ds = f.date.isoformat()
                if ds not in dates_shown:
                    st.markdown(f"**{f.date.strftime('%a, %b %d')}** — {f.round}" + (f" Group {f.group}" if f.group else ""))
                    dates_shown.add(ds)
                st.markdown(f"<span style='color:#6b6b8d;font-size:0.9rem;margin-left:1rem;'>{flag(f.team_a)} {f.team_a} vs {f.team_b} {flag(f.team_b)} at {f.venue}</span>", unsafe_allow_html=True)

    elif view == "Full Schedule":
        st.markdown("### Full Tournament Schedule (with Predictions)")
        with st.expander("Filter options", expanded=False):
            filter_round = st.selectbox("Match Round",
                ["All", "Group Stage", "Round of 32", "Round of 16", "Quarter-finals", "Semi-finals", "Final"],
                index=0, key="filter_round")
            filter_group = st.selectbox("Group",
                ["All"] + sorted(WORLD_CUP_GROUPS.keys()), index=0, key="filter_group")
            search_team = st.text_input("Search team", "", placeholder="e.g. France, Argentina...")

        by_date = get_fixtures_by_matchday()
        match_count = 0
        for ds, fixtures in list(by_date.items()):
            d = date.fromisoformat(ds)
            filtered = []
            for f in fixtures:
                if filter_round != "All" and f.round != filter_round:
                    continue
                if filter_group != "All" and f.group != filter_group:
                    continue
                if search_team and search_team.lower() not in f.team_a.lower() and search_team.lower() not in f.team_b.lower():
                    continue
                filtered.append(f)
            if not filtered:
                continue
            st.markdown(f"**{d.strftime('%A, %B %d, %Y')}**")
            for f in filtered:
                _render_match_card(f, match_count)
                match_count += 1
        if match_count == 0:
            st.info("No matches match your filter criteria.")

    else:
        _render_news_feed()


def _render_match_card(f: MatchFixture, idx: int):
    is_group = f.round == "Group Stage"
    if "TBD" in (f.team_a, f.team_b):
        st.markdown(f"<div class='match-row' style='text-align:center;color:#8888bb;'>{f.round}: {f.team_a} vs {f.team_b} ({f.date}, {f.venue}) — draw pending</div>", unsafe_allow_html=True)
        return

    p = predict_match_enhanced(f.team_a, f.team_b, scraper_instance=scraper)
    a = analyze_team(f.team_a)
    b = analyze_team(f.team_b)
    news_a = scraper.get_team_news_with_links(f.team_a)
    news_b = scraper.get_team_news_with_links(f.team_b)
    injuries_a = scraper.extract_team_news(f.team_a).injuries
    injuries_b = scraper.extract_team_news(f.team_b).injuries

    with st.container():
        st.markdown(f"<h4 style='margin-bottom:0;'>{flag(f.team_a)} {f.team_a} vs {f.team_b} {flag(f.team_b)}</h4>", unsafe_allow_html=True)
        rnd = f"{f.round}" + (f" — Group {f.group}" if f.group else "")
        st.markdown(f"<span style='color:#8888bb;font-size:0.82rem;'>{rnd} · {f.date.strftime('%b %d')} · {f.venue}</span>", unsafe_allow_html=True)

        cols = st.columns([1, 0.3, 1])
        with cols[0]:
            st.markdown(f"<div style='text-align:center;font-size:1.3rem;font-weight:700;color:#1a1a2e;'>{p.win_prob_a:.0%}</div><div style='text-align:center;color:#8888bb;font-size:0.75rem;'>Win</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center;font-size:1.8rem;font-weight:800;color:#4361ee;'>{p.predicted_score[0]}–{p.predicted_score[1]}</div>", unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f"<div style='text-align:center;padding-top:0.8rem;'><div style='font-size:2rem;'>{flag(f.team_a)}</div><div style='font-size:0.8rem;color:#8888bb;'>vs</div><div style='font-size:2rem;'>{flag(f.team_b)}</div></div>", unsafe_allow_html=True)
        with cols[2]:
            st.markdown(f"<div style='text-align:center;font-size:1.3rem;font-weight:700;color:#1a1a2e;'>{p.win_prob_b:.0%}</div><div style='text-align:center;color:#8888bb;font-size:0.75rem;'>Win</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center;font-size:1.8rem;font-weight:800;color:#7b2cbf;'>{p.predicted_score[0]}–{p.predicted_score[1]}</div>", unsafe_allow_html=True)

        lambda_text = f"λ={p.lambda_a:.2f} / {p.lambda_b:.2f} (base)"
        if p.adjusted_lambda_a is not None:
            lambda_text += f" → adj={p.adjusted_lambda_a:.2f} / {p.adjusted_lambda_b:.2f}"
        st.markdown(f"<div style='text-align:center;color:#8888bb;font-size:0.85rem;'>Draw: {p.draw_prob:.0%} · {lambda_text}</div>", unsafe_allow_html=True)

        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Analysis", "🏥 Injuries", "📰 Team News", "⚔️ Key Battle", "🎯 Factor Breakdown"])
        with tab1:
            ca, cb = st.columns(2)
            for col, team_data, tm in [(ca, a, f.team_a), (cb, b, f.team_b)]:
                with col:
                    st.markdown(f"**{flag(tm)} {tm}**")
                    st.markdown(f"<span style='color:#6b6b8d;font-size:0.85rem;'>Style: {team_data['style']} · Attack: {team_data['attack_rating']:.2f} · Defense: {team_data['defense_rating']:.2f}</span>", unsafe_allow_html=True)
                    if team_data["strengths"]:
                        for s, d in team_data["strengths"]:
                            st.markdown(f"<span style='color:#2e7d32;font-size:0.85rem;'>✅ {s}: {d}</span>", unsafe_allow_html=True)
                    if team_data["weaknesses"]:
                        for s, d in team_data["weaknesses"]:
                            st.markdown(f"<span style='color:#c62828;font-size:0.85rem;'>⚠️ {s}: {d}</span>", unsafe_allow_html=True)

        with tab2:
            ca, cb = st.columns(2)
            with ca:
                st.markdown(f"**{flag(f.team_a)} {f.team_a}**")
                for inj in (injuries_a or ["✅ No reported injuries"]):
                    st.markdown(f"<span style='font-size:0.85rem;'>{'⚠️' if 'doubtful' in inj or 'recovering' in inj else '✅'} {inj}</span>", unsafe_allow_html=True)
            with cb:
                st.markdown(f"**{flag(f.team_b)} {f.team_b}**")
                for inj in (injuries_b or ["✅ No reported injuries"]):
                    st.markdown(f"<span style='font-size:0.85rem;'>{'⚠️' if 'doubtful' in inj or 'recovering' in inj else '✅'} {inj}</span>", unsafe_allow_html=True)

        with tab3:
            ca, cb = st.columns(2)
            with ca:
                st.markdown(f"**{flag(f.team_a)} {f.team_a} News**")
                if news_a:
                    for article in news_a[:4]:
                        st.markdown(f"<span style='font-size:0.83rem;'>📰 <a href='{article['link']}' target='_blank'>{article['title'][:90]}</a><br><span style='color:#8888bb;'>{article['source']}</span></span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span style='color:#8888bb;font-size:0.85rem;'>No recent articles found</span>", unsafe_allow_html=True)
            with cb:
                st.markdown(f"**{flag(f.team_b)} {f.team_b} News**")
                if news_b:
                    for article in news_b[:4]:
                        st.markdown(f"<span style='font-size:0.83rem;'>📰 <a href='{article['link']}' target='_blank'>{article['title'][:90]}</a><br><span style='color:#8888bb;'>{article['source']}</span></span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span style='color:#8888bb;font-size:0.85rem;'>No recent articles found</span>", unsafe_allow_html=True)

        with tab4:
            comp = compare_teams(f.team_a, f.team_b)
            st.markdown("**Advantage Matrix**")
            for cat, tm in comp["advantage"].items():
                st.markdown(f"<span style='font-size:0.85rem;'><strong>{cat}</strong>: {flag(tm)} {tm}</span>", unsafe_allow_html=True)
            if comp["key_battles"]:
                st.markdown("**Key Storylines**")
                for b in comp["key_battles"]:
                    st.markdown(f"<span style='font-size:0.85rem;color:#3d3d5c;'>⚡ {b}</span>", unsafe_allow_html=True)

        with tab5:
            if p.factor_breakdown:
                st.markdown("#### λ Adjustment Factors")
                st.markdown("<span style='color:#8888bb;font-size:0.82rem;'>Positive = advantage for team A, negative = advantage for team B</span>", unsafe_allow_html=True)
                factor_rows = []
                factor_labels = {
                    "form": "Recent Form",
                    "goal_diff": "Goal Differential",
                    "h2h": "Head-to-Head",
                    "squad_value": "Squad Value",
                    "experience": "Tournament Experience",
                    "confederation": "Confederation Strength",
                    "injuries": "Injury Impact",
                    "manager": "Manager Pedigree",
                    "wc_performance": "WC 2018/22 Performance",
                    "xG_differential": "xG Differential",
                    "opponent_quality": "Opponent Quality",
                }
                total = 0.0
                for k, v in p.factor_breakdown.items():
                    label = factor_labels.get(k, k.replace("_", " ").title())
                    total += v
                    color = "#2e7d32" if v > 0 else "#c62828" if v < 0 else "#8888bb"
                    sign = "+" if v > 0 else ""
                    factor_rows.append({"Factor": label, "Impact": f"{sign}{v:.3f}"})
                factor_rows.append({"Factor": "**Total Adjustment**", "Impact": f"{'+' if total > 0 else ''}{total:.3f}"})
                st.dataframe(pd.DataFrame(factor_rows), use_container_width=True, hide_index=True)

                ca, cb = st.columns(2)
                base_a = p.lambda_a
                base_b = p.lambda_b
                adj_a = p.adjusted_lambda_a
                adj_b = p.adjusted_lambda_b
                with ca:
                    st.markdown(f"**{flag(f.team_a)} {f.team_a}**")
                    st.markdown(f"Base λ: {base_a:.3f} → Adjusted: **{adj_a:.3f}**" if adj_a else f"Base λ: {base_a:.3f}")
                    st.markdown(f"Outcome: {p.win_prob_a:.1%} win, {p.draw_prob:.1%} draw")
                with cb:
                    st.markdown(f"**{flag(f.team_b)} {f.team_b}**")
                    st.markdown(f"Base λ: {base_b:.3f} → Adjusted: **{adj_b:.3f}**" if adj_b else f"Base λ: {base_b:.3f}")
                    st.markdown(f"Outcome: {p.win_prob_b:.1%} win, {p.draw_prob:.1%} draw")
            else:
                st.markdown("<span style='color:#8888bb;'>Factor analysis not available</span>", unsafe_allow_html=True)

        st.markdown("---")


def _render_news_feed():
    st.markdown("### 🌐 World Football News")
    items = scraper.get_global_news()
    if items:
        for article in items[:20]:
            st.markdown(f"""
            <div style='background:white;border-radius:10px;padding:0.6rem 1rem;margin:0.4rem 0;border:1px solid #e8ecf4;'>
                <a href="{article['link']}" target="_blank" style='font-weight:600;font-size:0.95rem;text-decoration:none;'>{article['title'][:120]}</a>
                <div style='color:#8888bb;font-size:0.78rem;margin-top:2px;'>{article['source']} · {article['published'][:16]}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("No news articles loaded. RSS feeds may be unavailable.")


def _run_mc():
    import json
    import os
    cache_path = os.path.join(os.path.dirname(__file__), ".mc_cache.json")
    if os.path.exists(cache_path):
        with open(cache_path) as f:
            return json.load(f)
    mc = TournamentSimulator().run_monte_carlo(25)
    try:
        with open(cache_path, "w") as f:
            json.dump(mc, f)
    except Exception:
        pass
    return mc


def render_overview():
    st.markdown("# 🏆 FIFA World Cup 2026 Predictor")
    st.markdown("<p style='color:#6b6b8d;font-size:1.05rem;margin-bottom:1.5rem;'>LLM-Enhanced Tournament Forecasting Engine</p>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Qualified Teams", "48")
    with col2: st.metric("Groups", "12")
    with col3: st.metric("Host Nations", "3  🇺🇸🇲🇽🇨🇦")
    with col4: st.metric("Knockout Teams", "32")

    if st.button("🏅 Run Championship Simulation"):
        with st.spinner("Running 25 Monte Carlo simulations…"):
            mc = _run_mc()
    else:
        mc = None

    if mc:
        st.markdown("### 🏅 Title Favorites")
        top10 = list(mc["winners"].items())[:10]
        cols = st.columns(5)
        for i, (team, wins) in enumerate(top10):
            pct = wins / mc["total_simulations"] * 100
            with cols[i % 5]:
                c = "#4361ee" if i == 0 else "#7b2cbf" if i < 3 else "#8888bb"
                st.markdown(f"""
                <div class='team-card' style='text-align:center;'>
                    <div style='font-size:2rem;'>{flag(team)}</div>
                    <div style='font-weight:700;color:#1a1a2e;'>{team}</div>
                    <div style='font-size:1.5rem;font-weight:800;color:{c};'>{pct:.1f}%</div>
                    <div style='color:#8888bb;font-size:0.78rem;'>win probability</div>
                </div>""", unsafe_allow_html=True)

        mcd = pd.DataFrame([
            {"Team": t, "Win %": round(w/mc["total_simulations"]*100, 1),
             "Semi %": round(mc["semi_finalists"].get(t,0)/mc["total_simulations"]*100, 1),
             "Quarter %": round(mc["quarter_finalists"].get(t,0)/mc["total_simulations"]*100, 1)}
            for t, w in mc["winners"].items()
        ]).head(15)

        fig = px.bar(mcd, x="Team", y="Win %", text="Win %",
                     color="Win %", color_continuous_scale="blues",
                     title="Championship Win Probability (Top 15)")
        fig.update_layout(xaxis_tickangle=-45, height=400,
                          plot_bgcolor="white", paper_bgcolor="white",
                          font_color="#3d3d5c", title_font_color="#1a1a2e")
        fig.update_traces(textfont_color="#1a1a2e", textposition="outside")
        st.plotly_chart(fig, width='stretch')

    st.markdown("### ⚡ Quick Match Predictor")
    ca, cb = st.columns(2)
    with ca:
        ta = st.selectbox("Team A", ALL_TEAMS, index=ALL_TEAMS.index("France"))
    with cb:
        tb = st.selectbox("Team B", ALL_TEAMS, index=ALL_TEAMS.index("Argentina"))
    if st.button("Predict Match", width='stretch'):
        p = predict_match_enhanced(ta, tb, scraper_instance=scraper)
        g = st.columns(3)
        with g[0]:
            st.markdown(f"<div style='text-align:center;'><div style='font-size:2.5rem;'>{flag(ta)}</div><div style='font-weight:700;color:#1a1a2e;font-size:1rem;'>{ta}</div><div style='font-size:1.8rem;font-weight:800;color:#4361ee;'>{p.win_prob_a:.0%}</div></div>", unsafe_allow_html=True)
        with g[1]:
            st.markdown(f"<div style='text-align:center;padding-top:1.5rem;'><div style='font-size:1.8rem;color:#8888bb;'>VS</div><div style='font-size:1.5rem;font-weight:700;color:#1a1a2e;'>{p.predicted_score[0]}–{p.predicted_score[1]}</div></div>", unsafe_allow_html=True)
        with g[2]:
            st.markdown(f"<div style='text-align:center;'><div style='font-size:2.5rem;'>{flag(tb)}</div><div style='font-weight:700;color:#1a1a2e;font-size:1rem;'>{tb}</div><div style='font-size:1.8rem;font-weight:800;color:#7b2cbf;'>{p.win_prob_b:.0%}</div></div>", unsafe_allow_html=True)
        lam_str = f"λ={p.lambda_a:.2f} / {p.lambda_b:.2f} (base)"
        if p.adjusted_lambda_a is not None:
            lam_str += f" → adj={p.adjusted_lambda_a:.2f} / {p.adjusted_lambda_b:.2f}"
        try:
            from llm_rag import rag_predictor
            ms = rag_predictor.model_source
            model_label = "Enhanced Poisson + Gemini" if ms == "gemini" else "Enhanced Poisson"
        except Exception:
            model_label = "Enhanced Poisson"
        st.markdown(f"<div style='text-align:center;color:#b0b8d0;margin-top:0.3rem;'>Draw: {p.draw_prob:.0%} · {lam_str}<br><span style='font-size:0.78rem;'>Model: {model_label}</span></div>", unsafe_allow_html=True)


def render_rankings():
    st.markdown("# 🌍 FIFA World Rankings (April 2026)")
    conf_filter = st.multiselect("Filter by Confederation", ["UEFA","CONMEBOL","CAF","AFC","CONCACAF","OFC"],
                                  default=["UEFA","CONMEBOL","CAF","AFC","CONCACAF","OFC"])
    rows = []
    for i, (name, pts) in enumerate(sorted(FIFA_RANKINGS_APRIL_2026.items(), key=lambda x: -x[1]), 1):
        td = get_team_data(name)
        if td.confederation in conf_filter:
            rows.append({"Rank": i, "Team": f"{flag(name)} {name}", "Confederation": td.confederation,
                         "Points": round(pts, 1), "Form": RECENT_FORM_MODIFIERS.get(name, 0),
                         "Attack": td.attack, "Defense": td.defense})
    df = pd.DataFrame(rows)
    st.dataframe(df, column_config={
        "Team": st.column_config.TextColumn("Team", width="large"),
        "Points": st.column_config.NumberColumn("Points", format="%.1f"),
        "Form": st.column_config.NumberColumn("Form", format="%+d"),
    }, hide_index=True, width='stretch')
    fig = px.bar(df, x="Team", y="Points", color="Confederation", text="Points",
                 title="FIFA Rankings by Confederation")
    fig.update_layout(xaxis_tickangle=-45, height=500,
                      plot_bgcolor="white", paper_bgcolor="white",
                      font_color="#3d3d5c", title_font_color="#1a1a2e")
    fig.update_traces(textfont_color="#1a1a2e", textposition="outside")
    st.plotly_chart(fig, width='stretch')


def render_groups():
    st.markdown("# 📋 World Cup 2026 Group Stage")
    for g_name in sorted(WORLD_CUP_GROUPS.keys()):
        teams = WORLD_CUP_GROUPS[g_name]
        standings = predict_group_poisson(g_name, teams)
        with st.expander(f"**Group {g_name}**", expanded=True):
            cols = st.columns(4)
            for i, s in enumerate(standings):
                td = get_team_data(s["team"])
                with cols[i]:
                    st.markdown(team_card(s["team"],
                        [f"Pts: {s['points']}", f"GD: {s['gd']:+d}", f"GF: {s['gf']}",
                         f"FIFA #{td.fifa_rank} · {td.confederation}"], i), unsafe_allow_html=True)
            st.markdown("**Predicted Match Results:**")
            mcols = st.columns(3)
            fixtures = [(teams[0], teams[1]), (teams[2], teams[3]),
                        (teams[0], teams[2]), (teams[1], teams[3]),
                        (teams[0], teams[3]), (teams[1], teams[2])]
            for idx, (ta, tb) in enumerate(fixtures):
                p = predict_match_poisson(ta, tb)
                with mcols[idx % 3]:
                    st.markdown(match_line(ta, tb, p.predicted_score[0], p.predicted_score[1],
                                          p.win_prob_a, p.draw_prob, p.win_prob_b), unsafe_allow_html=True)


def render_tournament():
    st.markdown("# 🎯 Live Tournament Simulation")
    if st.button("▶️ Run Full Simulation", type="primary", width='stretch'):
        with st.spinner("Simulating groups + knockout bracket…"):
            result = TournamentSimulator().run()

        gs = result["group_standings"]
        st.markdown("## Group Stage")
        gcols = st.columns(3)
        for gi, g_name in enumerate(sorted(gs.keys())):
            with gcols[gi % 3]:
                st.markdown(f"<h4>Group {g_name}</h4>", unsafe_allow_html=True)
                for i, s in enumerate(gs[g_name]):
                    bc = "#4361ee" if i == 0 else "#7b2cbf" if i == 1 else "#dce0ec"
                    star = " ⭐" if i < 2 else ""
                    st.markdown(f"<div class='group-team' style='border-left-color:{bc};'><span style='font-size:1.05rem;'>{flag(s.team)}</span> <strong style='color:#1a1a2e;'>{s.team}</strong> · {s.points}pts · GD {s.goal_diff:+d}{star}</div>", unsafe_allow_html=True)

        ko = result["knockout"]
        st.markdown("## 🏆 Knockout Stage")
        rcols = st.columns(4)
        for ri, (rname, rkey) in enumerate([
            ("R32", "round_of_32"), ("R16", "round_of_16"),
            ("QF", "quarter_finals"), ("SF", "semi_finals"),
        ]):
            with rcols[ri]:
                st.markdown(f"<h4>{rname}</h4>", unsafe_allow_html=True)
                for m in ko.get(rkey, []):
                    w = m.winner()
                    st.markdown(f"""<div class='match-row' style='font-size:0.85rem;'>{flag(m.team_a)} {m.team_a}<br><strong style='font-size:1.1rem;color:#1a1a2e;'>{m.goals_a}–{m.goals_b}</strong><br>{m.team_b} {flag(m.team_b)}{f"<br><span style='color:#4361ee;font-weight:600;'>✓ {w}</span>" if w else ""}</div>""", unsafe_allow_html=True)

        st.markdown("---")
        fcol1, fcol2 = st.columns(2)
        with fcol1:
            tp = ko.get("third_place")
            if tp:
                st.markdown(f"<h3>🥉 Third Place</h3><div style='text-align:center;font-size:1.2rem;color:#1a1a2e;'>{flag(tp.team_a)} {tp.team_a} <strong>{tp.goals_a}–{tp.goals_b}</strong> {tp.team_b} {flag(tp.team_b)}</div>", unsafe_allow_html=True)
        with fcol2:
            f = ko.get("final")
            if f:
                w = ko.get("winner")
                st.markdown(f"<h3 style='color:#4361ee;'>🏆 Final</h3><div style='text-align:center;font-size:1.2rem;color:#1a1a2e;'>{flag(f.team_a)} {f.team_a} <strong>{f.goals_a}–{f.goals_b}</strong> {f.team_b} {flag(f.team_b)}</div><div style='text-align:center;font-size:1.5rem;font-weight:800;color:#4361ee;margin-top:0.5rem;'>🏆 {w}</div>", unsafe_allow_html=True)


def render_monte_carlo():
    st.markdown("# 📊 Monte Carlo Simulation")
    n_sims = st.slider("Number of simulations", 50, 5000, 500, step=50)
    if st.button("▶️ Run Monte Carlo", type="primary", width='stretch'):
        with st.spinner(f"Running {n_sims} simulations…"):
            mc = TournamentSimulator().run_monte_carlo(n_sims)
        st.success(f"Completed {mc['total_simulations']} simulations!")
        mcd = pd.DataFrame([
            {"Team": t, "Win": round(w/mc["total_simulations"]*100, 1),
             "Semi": round(mc["semi_finalists"].get(t,0)/mc["total_simulations"]*100, 1),
             "Quarter": round(mc["quarter_finalists"].get(t,0)/mc["total_simulations"]*100, 1)}
            for t, w in mc["winners"].items()
        ]).head(20)
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Win Title", x=mcd["Team"], y=mcd["Win"], marker_color="#4361ee", text=mcd["Win"]))
        fig.add_trace(go.Bar(name="Reach Semi", x=mcd["Team"], y=mcd["Semi"], marker_color="#7b2cbf", text=mcd["Semi"]))
        fig.add_trace(go.Bar(name="Reach Quarter", x=mcd["Team"], y=mcd["Quarter"], marker_color="#4cc9f0", text=mcd["Quarter"]))
        fig.update_layout(barmode="group", xaxis_tickangle=-45, height=500,
                          plot_bgcolor="white", paper_bgcolor="white",
                          font_color="#3d3d5c", title_font_color="#1a1a2e",
                          title=f"Tournament Probabilities ({n_sims} simulations)")
        fig.update_traces(textfont_color="#1a1a2e")
        st.plotly_chart(fig, width='stretch')
        st.markdown("### Top 10 Favorites")
        for i, (team, wins) in enumerate(list(mc["winners"].items())[:10], 1):
            wp = wins / mc["total_simulations"] * 100
            sp = mc["semi_finalists"].get(team, 0) / mc["total_simulations"] * 100
            qp = mc["quarter_finalists"].get(team, 0) / mc["total_simulations"] * 100
            st.markdown(f"""
            <div class='team-card' style='display:flex;align-items:center;justify-content:space-between;'>
                <div><span style='font-weight:700;color:#8888bb;'>#{i}</span> <span style='font-size:1.3rem;'>{flag(team)}</span> <strong style='color:#1a1a2e;'>{team}</strong></div>
                <div style='display:flex;gap:1.5rem;'>
                    <div style='text-align:center;'><div style='color:#4361ee;font-size:1.2rem;font-weight:700;'>{wp:.1f}%</div><div style='color:#8888bb;font-size:0.7rem;'>Win</div></div>
                    <div style='text-align:center;'><div style='color:#7b2cbf;font-size:1.2rem;font-weight:700;'>{sp:.1f}%</div><div style='color:#8888bb;font-size:0.7rem;'>Semi</div></div>
                    <div style='text-align:center;'><div style='color:#4cc9f0;font-size:1.2rem;font-weight:700;'>{qp:.1f}%</div><div style='color:#8888bb;font-size:0.7rem;'>Quarter</div></div>
                </div>
            </div>""", unsafe_allow_html=True)


def render_h2h():
    st.markdown("# ⚔️ Head-to-Head Analysis")
    st.markdown("<p style='color:#6b6b8d;font-size:0.95rem;'>Compare any two teams — prediction, strengths, weaknesses, style, news & head-to-head history</p>", unsafe_allow_html=True)

    ca, cb = st.columns(2)
    with ca:
        ta = st.selectbox("Team A", ALL_TEAMS, index=ALL_TEAMS.index("France"), key="h2h_a")
    with cb:
        tb = st.selectbox("Team B", ALL_TEAMS, index=ALL_TEAMS.index("Germany"), key="h2h_b")

    if st.button("Analyze Matchup", type="primary", width='stretch'):
        p = predict_match_enhanced(ta, tb, scraper_instance=scraper)
        h2h = get_h2h(ta, tb)
        td_a, td_b = get_team_data(ta), get_team_data(tb)
        a_analysis = analyze_team(ta)
        b_analysis = analyze_team(tb)
        mgr_a = get_manager(ta)
        mgr_b = get_manager(tb)

        # Header
        st.markdown(f"""<div class='team-card' style='text-align:center;'><div style='display:flex;justify-content:space-around;align-items:center;padding:0.5rem 0;'>
            <div><div style='font-size:3rem;'>{flag(ta)}</div><div style='font-weight:700;font-size:1.1rem;color:#1a1a2e;'>{ta}</div></div>
            <div><div style='font-size:1.5rem;color:#8888bb;font-weight:600;'>VS</div><div style='font-size:2rem;font-weight:800;color:#1a1a2e;'>{p.predicted_score[0]}–{p.predicted_score[1]}</div></div>
            <div><div style='font-size:3rem;'>{flag(tb)}</div><div style='font-weight:700;font-size:1.1rem;color:#1a1a2e;'>{tb}</div></div>
        </div></div>""", unsafe_allow_html=True)

        # Win probabilities
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div style='text-align:center;padding:0.8rem;background:#f0f2ff;border-radius:10px;'><div style='font-size:1.8rem;font-weight:800;color:#4361ee;'>{p.win_prob_a:.0%}</div><div style='color:#6b6b8d;font-size:0.85rem;'>{ta} Win</div></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div style='text-align:center;padding:0.8rem;background:#f5f5fa;border-radius:10px;'><div style='font-size:1.8rem;font-weight:800;color:#1a1a2e;'>{p.draw_prob:.0%}</div><div style='color:#6b6b8d;font-size:0.85rem;'>Draw</div></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div style='text-align:center;padding:0.8rem;background:#f5f0ff;border-radius:10px;'><div style='font-size:1.8rem;font-weight:800;color:#7b2cbf;'>{p.win_prob_b:.0%}</div><div style='color:#6b6b8d;font-size:0.85rem;'>{tb} Win</div></div>", unsafe_allow_html=True)

        try:
            from llm_rag import rag_predictor
            model_src = rag_predictor.model_source
            rag_predictor.initialize()
            model_label = "Enhanced Poisson + Gemini" if model_src == "gemini" else \
                          "Enhanced Poisson + OpenAI" if model_src == "openai" else \
                          "Enhanced Poisson"
        except Exception:
            model_label = "Enhanced Poisson"
        st.markdown(f"<div style='text-align:center;color:#b0b8d0;font-size:0.78rem;margin-top:0.2rem;'>Model: {model_label}</div>", unsafe_allow_html=True)

        st.markdown("---")

        # Team profiles side by side
        st.markdown("### 📊 Team Profiles")
        sc1, sc2 = st.columns(2)
        for col, team_data, td, mgr, team in [
            (sc1, a_analysis, td_a, mgr_a, ta),
            (sc2, b_analysis, td_b, mgr_b, tb)
        ]:
            with col:
                form_color = "#2e7d32" if td.recent_form > 0 else "#c62828"
                st.markdown(f"<div style='background:white;border-radius:12px;padding:1rem;border:1px solid #e8ecf4;height:100%;'>"
                            f"<div style='font-size:1.2rem;font-weight:700;color:#1a1a2e;margin-bottom:0.5rem;'>{flag(team)} {team}</div>"
                            f"<div style='display:grid;grid-template-columns:1fr 1fr;gap:0.3rem;font-size:0.88rem;'>"
                            f"<span style='color:#8888bb;'>FIFA Rank</span><span style='font-weight:600;'>#{td.fifa_rank} ({td.fifa_points:.0f} pts)</span>"
                            f"<span style='color:#8888bb;'>Confederation</span><span>{td.confederation}</span>"
                            f"<span style='color:#8888bb;'>Style</span><span>{team_data['style']}</span>"
                            f"<span style='color:#8888bb;'>Manager</span><span>{mgr['name']}</span>"
                            f"<span style='color:#8888bb;'>WC Apps</span><span>{td.appearances} (best: {td.best_result})</span>"
                            f"<span style='color:#8888bb;'>Form</span><span style='color:{form_color};'>{td.recent_form:+d}</span>"
                            f"<span style='color:#8888bb;'>Attack</span><span>{td.attack:.2f}</span>"
                            f"<span style='color:#8888bb;'>Defense</span><span>{td.defense:.2f}</span>"
                            f"</div></div>", unsafe_allow_html=True)

        # Strengths & Weaknesses
        st.markdown("### ✅ Strengths & ⚠️ Weaknesses")
        ss1, ss2 = st.columns(2)
        for col, analysis in [(ss1, a_analysis), (ss2, b_analysis)]:
            with col:
                st.markdown(f"**{flag(analysis['team'])} {analysis['team']}**")
                if analysis["strengths"]:
                    for s, d in analysis["strengths"]:
                        st.markdown(f"<span style='color:#2e7d32;font-size:0.85rem;'>✅ <strong>{s}</strong>: {d}</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span style='color:#8888bb;font-size:0.85rem;'>No standout strengths identified</span>", unsafe_allow_html=True)
                if analysis["weaknesses"]:
                    st.markdown("<br>", unsafe_allow_html=True)
                    for s, d in analysis["weaknesses"]:
                        st.markdown(f"<span style='color:#c62828;font-size:0.85rem;'>⚠️ <strong>{s}</strong>: {d}</span>", unsafe_allow_html=True)

        # Head-to-head history
        st.markdown("---")
        st.markdown("### 📜 Head-to-Head History")
        if h2h["total"] > 0:
            key = tuple(sorted([ta, tb]))
            h2h_rows = []
            for m in h2h["matches"]:
                ga, gb, comp, year = m
                if ta == key[0]:
                    score = f"{ga}–{gb}"
                else:
                    score = f"{gb}–{ga}"
                h2h_rows.append({"Match": f"{flag(ta)} {ta} vs {tb} {flag(tb)}",
                                 "Score": score, "Competition": comp, "Year": year})
            h2h_df = pd.DataFrame(h2h_rows).sort_values("Year", ascending=False)
            st.dataframe(h2h_df, hide_index=True, use_container_width=True)
            tot = h2h["total"]
            aw = h2h[f"{ta}_wins"]
            bw = h2h[f"{tb}_wins"]
            dr = h2h["draws"]
            st.markdown(f"<span style='color:#6b6b8d;font-size:0.9rem;'>Overall: {ta} {aw} wins – {dr} draws – {tb} {bw} wins ({tot} meetings)</span>", unsafe_allow_html=True)
        else:
            st.info("No previous head-to-head meetings between these teams.")

        # Advantage matrix
        st.markdown("### ⚡ Advantage Matrix")
        comp = compare_teams(ta, tb)
        adv_cols = st.columns(4)
        adv_items = list(comp["advantage"].items())
        for i, (cat, tm) in enumerate(adv_items):
            with adv_cols[i % 4]:
                st.markdown(f"<div style='background:white;border-radius:8px;padding:0.5rem;text-align:center;border:1px solid #e8ecf4;'>"
                            f"<div style='color:#8888bb;font-size:0.75rem;'>{cat}</div>"
                            f"<div style='font-weight:700;font-size:0.95rem;color:#1a1a2e;'>{flag(tm)} {tm}</div></div>", unsafe_allow_html=True)

        # Key storylines
        if comp["key_battles"]:
            st.markdown("### 🔑 Key Storylines")
            for b in comp["key_battles"]:
                st.markdown(f"<span style='font-size:0.9rem;color:#3d3d5c;'>⚡ {b}</span>", unsafe_allow_html=True)

        # Factor breakdown
        if p.factor_breakdown:
            st.markdown("### 🎯 λ Adjustment Factors")
            st.markdown("<span style='color:#8888bb;font-size:0.82rem;'>Positive = advantage for team A, negative = advantage for team B</span>", unsafe_allow_html=True)
            factor_labels = {
                "form": "Recent Form", "goal_diff": "Goal Differential", "h2h": "Head-to-Head",
                "squad_value": "Squad Value", "experience": "Tournament Experience",
                "confederation": "Confederation Strength", "injuries": "Injury Impact",
                "manager": "Manager Pedigree", "wc_performance": "WC 2018/22 Performance",
                "xG_differential": "xG Differential", "opponent_quality": "Opponent Quality",
            }
            frows = []
            total = 0.0
            for k, v in p.factor_breakdown.items():
                label = factor_labels.get(k, k.replace("_", " ").title())
                total += v
                sign = "+" if v > 0 else ""
                frows.append({"Factor": label, "Impact": f"{sign}{v:.3f}"})
            frows.append({"Factor": "**Total Adjustment**", "Impact": f"{'+' if total > 0 else ''}{total:.3f}"})
            st.dataframe(pd.DataFrame(frows), use_container_width=True, hide_index=True)

            ca2, cb2 = st.columns(2)
            with ca2:
                st.markdown(f"**{flag(ta)} {ta}** — Base λ: {p.lambda_a:.3f} → Adjusted: **{p.adjusted_lambda_a:.3f}** ({p.win_prob_a:.1%} win)")
            with cb2:
                st.markdown(f"**{flag(tb)} {tb}** — Base λ: {p.lambda_b:.3f} → Adjusted: **{p.adjusted_lambda_b:.3f}** ({p.win_prob_b:.1%} win)")

        # News for both teams
        st.markdown("---")
        st.markdown("### 📰 Team News")
        news_ncol1, news_ncol2 = st.columns(2)
        for col, team, opp in [(news_ncol1, ta, tb), (news_ncol2, tb, ta)]:
            with col:
                st.markdown(f"**{flag(team)} {team}**")
                news_items = scraper.get_team_news_with_links(team)
                if news_items:
                    for article in news_items[:4]:
                        st.markdown(f"<span style='font-size:0.83rem;'>📰 <a href='{article['link']}' target='_blank'>{article['title'][:100]}</a><br><span style='color:#8888bb;font-size:0.78rem;'>{article['source']} · {article['published'][:12]}</span></span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span style='color:#8888bb;font-size:0.85rem;'>No recent news found</span>", unsafe_allow_html=True)

                injury_info = scraper.extract_team_news(team)
                if injury_info.injuries:
                    st.markdown(f"<span style='font-size:0.83rem;font-weight:600;color:#c62828;margin-top:0.4rem;display:block;'>🏥 Injuries & Fitness</span>", unsafe_allow_html=True)
                    for inj in injury_info.injuries[:3]:
                        icon = "⚠️" if any(k in inj.lower() for k in ["doubtful", "recovering", "muscle", "hamstring", "knee", "ankle"]) else "✅"
                        st.markdown(f"<span style='font-size:0.82rem;'>{icon} {inj[:90]}</span>", unsafe_allow_html=True)

        # Goal distribution comparison
        st.markdown("---")
        st.markdown("### 📈 Goal Distribution")
        st.markdown("<span style='color:#000000;font-size:1rem;'>Expected goals per team given this specific matchup</span>", unsafe_allow_html=True)
        dist_a = [poisson_prob(k, p.adjusted_lambda_a or p.lambda_a) for k in range(7)]
        dist_b = [poisson_prob(k, p.adjusted_lambda_b or p.lambda_b) for k in range(7)]
        fig = go.Figure()
        fig.add_trace(go.Bar(name=ta, x=[str(k) for k in range(7)], y=dist_a,
                             marker_color="#4361ee", text=[f"{v:.0%}" for v in dist_a], textposition="outside"))
        fig.add_trace(go.Bar(name=tb, x=[str(k) for k in range(7)], y=dist_b,
                             marker_color="#7b2cbf", text=[f"{v:.0%}" for v in dist_b], textposition="outside"))
        fig.update_layout(barmode="group", height=350, plot_bgcolor="white", paper_bgcolor="white",
                          font_color="#000000", title_font_color="#000000", font_size=14,
                          xaxis_title="Goals", yaxis_title="Probability",
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig.update_traces(textfont_color="#ffffff", textfont_size=13)
        st.plotly_chart(fig, width='stretch')


def render_team_profile():
    st.markdown("# 📋 Team Profile")
    team = st.selectbox("Select Team", ALL_TEAMS, index=ALL_TEAMS.index("France"))
    td = get_team_data(team)
    st.markdown(f"""<div class='team-card' style='text-align:center;'><div style='font-size:3.5rem;'>{flag(team)}</div><div style='font-size:1.8rem;font-weight:800;color:#1a1a2e;'>{team}</div><div style='color:#8888bb;'>{td.confederation} · WC #{td.appearances} appearances</div></div>""", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("FIFA Rank", f"#{td.fifa_rank}", f"{td.fifa_points:.0f} pts")
    with c2: st.metric("Best Result", td.best_result)
    with c3: st.metric("Attack", td.attack)
    with c4: st.metric("Defense", td.defense)

    st.markdown("### Head-to-Head vs Top Opponents")
    top_teams = ["France","Spain","Argentina","England","Portugal","Brazil","Netherlands","Germany"]
    opps = [t for t in ALL_TEAMS if t != team][:8] if team in top_teams else top_teams
    h2h_rows = []
    for opp in opps[:8]:
        if opp == team: continue
        p = predict_match_poisson(team, opp)
        h2h_rows.append({"Opponent": opp, "Win": f"{p.win_prob_a if p.team_a==team else p.win_prob_b:.0%}",
                         "Draw": f"{p.draw_prob:.0%}", "Score": f"{p.predicted_score[0]}–{p.predicted_score[1]}"})
    if h2h_rows:
        st.dataframe(pd.DataFrame(h2h_rows), hide_index=True, width='stretch')

    st.markdown("### Goal Distribution")
    dist = [poisson_prob(k, td.attack * 1.25) for k in range(7)]
    fig = px.bar(x=[str(k) for k in range(7)], y=dist, labels={"x": "Goals", "y": "Probability"},
                 title=f"Expected Goals ({team})", color=dist, color_continuous_scale="blues")
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                      font_color="#3d3d5c", title_font_color="#1a1a2e", height=350)
    fig.update_traces(textfont_color="#1a1a2e")
    st.plotly_chart(fig, width='stretch')

    st.markdown("### Group Projection")
    for g_name, teams in WORLD_CUP_GROUPS.items():
        if team in teams:
            st.dataframe(pd.DataFrame([
                {"Pos": i+1, **s} for i, s in enumerate(predict_group_poisson(g_name, teams))
            ]), hide_index=True, width='stretch')
            break


main()
