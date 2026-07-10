"""
Ementora Academy — EdTech Platform Prototype
A single-file Streamlit prototype with three portals: Student, Teacher, Admin.

Run with:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# ──────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Ementora Academy",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────
# DESIGN TOKENS
# ──────────────────────────────────────────────────────────────────────────
INK        = "#12203D"   # near-black navy, primary text on light surfaces
NAVY       = "#152A52"   # deep academic navy — chrome / sidebar
NAVY_SOFT  = "#1F3A6E"   # lighter navy for hover/active states
BRASS      = "#C69A3E"   # lantern-gold accent
BRASS_SOFT = "#E8CE8E"   # pale gold for tints
PARCHMENT  = "#FAF6ED"   # warm off-white surface
PARCHMENT2 = "#F1EADA"   # slightly deeper parchment for cards
SLATE      = "#5B6B85"   # muted secondary text
GOOD       = "#3E7A57"   # success green
WARN       = "#B4552F"   # warm terracotta-adjacent warning

FONT_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
"""

CUSTOM_CSS = f"""
<style>
    html, body, [class*="css"]  {{
        font-family: 'Inter', sans-serif;
    }}
    .stApp {{
        background: {PARCHMENT};
    }}
    h1, h2, h3, .em-display {{
        font-family: 'Fraunces', serif;
        color: {INK};
        letter-spacing: -0.01em;
    }}
    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {NAVY} 0%, {INK} 100%);
    }}
    section[data-testid="stSidebar"] * {{
        color: {PARCHMENT} !important;
    }}
    section[data-testid="stSidebar"] .stRadio label {{
        font-family: 'Inter', sans-serif;
    }}
    section[data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,0.15);
    }}

    /* Brand lockup */
    .em-brand {{
        display: flex; align-items: center; gap: 12px;
        padding: 6px 0 18px 0;
    }}
    .em-seal {{
        width: 42px; height: 42px; border-radius: 50%;
        background: radial-gradient(circle at 35% 30%, {BRASS_SOFT}, {BRASS} 60%, #8a6a22 100%);
        display: flex; align-items: center; justify-content: center;
        font-family: 'Fraunces', serif; font-weight: 700; font-size: 18px; color: {INK};
        box-shadow: 0 3px 10px rgba(0,0,0,0.35);
        flex-shrink: 0;
    }}
    .em-brand-text .em-name {{
        font-family: 'Fraunces', serif; font-weight: 700; font-size: 19px; line-height: 1.1;
        color: {PARCHMENT};
    }}
    .em-brand-text .em-tag {{
        font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase;
        color: {BRASS_SOFT}; opacity: 0.85;
    }}

    /* Cards */
    .em-card {{
        background: {PARCHMENT2};
        border: 1px solid rgba(18,32,61,0.08);
        border-radius: 14px;
        padding: 20px 22px;
        box-shadow: 0 1px 2px rgba(18,32,61,0.04);
    }}
    .em-card-navy {{
        background: linear-gradient(135deg, {NAVY} 0%, {NAVY_SOFT} 100%);
        border-radius: 14px;
        padding: 20px 22px;
        color: {PARCHMENT};
        box-shadow: 0 8px 20px rgba(21,42,82,0.25);
    }}
    .em-card-navy .em-metric-label {{ color: {BRASS_SOFT}; }}
    .em-card-navy .em-metric-value {{ color: {PARCHMENT}; }}

    .em-eyebrow {{
        font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase;
        color: {BRASS}; font-weight: 600; margin-bottom: 4px; display: block;
    }}
    .em-metric-label {{
        font-size: 12.5px; color: {SLATE}; text-transform: uppercase; letter-spacing: 0.06em;
    }}
    .em-metric-value {{
        font-family: 'Fraunces', serif; font-size: 30px; font-weight: 600; color: {INK};
        line-height: 1.2;
    }}
    .em-metric-delta-up {{ color: {GOOD}; font-size: 13px; font-weight: 600; }}
    .em-metric-delta-down {{ color: {WARN}; font-size: 13px; font-weight: 600; }}

    /* Pills / badges */
    .em-pill {{
        display: inline-block; padding: 3px 11px; border-radius: 999px;
        font-size: 11.5px; font-weight: 600; letter-spacing: 0.02em;
    }}
    .em-pill-live {{ background: #FBE3D9; color: {WARN}; }}
    .em-pill-done {{ background: #DCEBE1; color: {GOOD}; }}
    .em-pill-brass {{ background: {BRASS_SOFT}; color: #5c4413; }}

    /* Progress bar */
    .em-progress-track {{
        background: rgba(18,32,61,0.08); border-radius: 999px; height: 8px; width: 100%; overflow: hidden;
    }}
    .em-progress-fill {{
        background: linear-gradient(90deg, {BRASS} 0%, {BRASS_SOFT} 100%); height: 100%; border-radius: 999px;
    }}

    /* Divider with label */
    .em-rule {{
        display: flex; align-items: center; gap: 12px; margin: 6px 0 14px 0;
    }}
    .em-rule::before, .em-rule::after {{
        content: ""; flex: 1; height: 1px; background: rgba(18,32,61,0.14);
    }}
    .em-rule span {{
        font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase; color: {SLATE};
    }}

    /* Buttons */
    .stButton>button {{
        background: {NAVY}; color: {PARCHMENT}; border-radius: 9px; border: none;
        font-weight: 600; padding: 0.5em 1.2em;
    }}
    .stButton>button:hover {{
        background: {BRASS}; color: {INK};
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{ gap: 6px; }}
    .stTabs [data-baseweb="tab"] {{
        background: {PARCHMENT2}; border-radius: 8px 8px 0 0; padding: 8px 16px;
        font-weight: 600; color: {SLATE};
    }}
    .stTabs [aria-selected="true"] {{
        background: {NAVY}; color: {PARCHMENT} !important;
    }}

    #MainMenu, footer {{visibility: hidden;}}
</style>
"""

st.markdown(FONT_CSS, unsafe_allow_html=True)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

PLOTLY_TEMPLATE = dict(
    layout=go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=INK, size=13),
        colorway=[NAVY, BRASS, SLATE, GOOD, WARN, NAVY_SOFT],
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
)

# ──────────────────────────────────────────────────────────────────────────
# MOCK DATA
# ──────────────────────────────────────────────────────────────────────────
rng = np.random.default_rng(7)

COURSES = pd.DataFrame([
    {"course": "UPSC CSE — Foundation 2027", "mentor": "Dr. A. Sharma", "progress": 68, "next": "Modern History — Ch. 9", "when": "Today, 6:00 PM"},
    {"course": "SSC CGL Quant Mastery", "mentor": "R. Verma", "progress": 41, "next": "Time & Work — Live Problem Set", "when": "Tomorrow, 8:00 AM"},
    {"course": "Banking Awareness 2026", "mentor": "P. Iyer", "progress": 89, "next": "Monetary Policy Recap", "when": "Fri, 7:30 PM"},
    {"course": "English Grammar Sprint", "mentor": "S. Nair", "progress": 22, "next": "Tenses — Diagnostic Test", "when": "Sat, 10:00 AM"},
])

TEST_HISTORY = pd.DataFrame({
    "Test": [f"Mock {i}" for i in range(1, 11)],
    "Score": rng.integers(55, 96, 10),
    "Percentile": rng.integers(60, 99, 10),
})

STUDENTS = pd.DataFrame([
    {"name": "Ananya Roy", "batch": "UPSC Foundation 2027", "attendance": 94, "last_score": 82, "status": "Active"},
    {"name": "Kabir Malhotra", "batch": "SSC CGL Quant", "attendance": 61, "last_score": 54, "status": "At risk"},
    {"name": "Diya Sen", "batch": "Banking Awareness", "attendance": 88, "last_score": 91, "status": "Active"},
    {"name": "Rehan Qureshi", "batch": "UPSC Foundation 2027", "attendance": 76, "last_score": 69, "status": "Active"},
    {"name": "Meher Kaur", "batch": "English Sprint", "attendance": 45, "last_score": 40, "status": "At risk"},
    {"name": "Ojas Patil", "batch": "SSC CGL Quant", "attendance": 97, "last_score": 88, "status": "Active"},
])

DOUBTS = pd.DataFrame([
    {"student": "Kabir Malhotra", "topic": "Time & Work — Ch. 4", "asked": "2h ago", "status": "Open"},
    {"student": "Meher Kaur", "topic": "Present Perfect vs Past Perfect", "asked": "5h ago", "status": "Open"},
    {"student": "Diya Sen", "topic": "Repo Rate mechanics", "asked": "1d ago", "status": "Answered"},
])

ALL_USERS = pd.DataFrame([
    {"name": "Ananya Roy", "role": "Student", "plan": "Pro Annual", "joined": "2025-03-11", "status": "Active"},
    {"name": "Dr. A. Sharma", "role": "Educator", "plan": "—", "joined": "2023-07-02", "status": "Active"},
    {"name": "Kabir Malhotra", "role": "Student", "plan": "Basic", "joined": "2026-01-19", "status": "Active"},
    {"name": "R. Verma", "role": "Educator", "plan": "—", "joined": "2024-02-14", "status": "Active"},
    {"name": "Meher Kaur", "role": "Student", "plan": "Pro Monthly", "joined": "2026-04-02", "status": "Suspended"},
    {"name": "P. Iyer", "role": "Educator", "plan": "—", "joined": "2022-11-23", "status": "Active"},
])

TICKETS = pd.DataFrame([
    {"id": "#3021", "user": "Kabir Malhotra", "issue": "Video buffering during live class", "priority": "High", "status": "Open"},
    {"id": "#3018", "user": "Diya Sen", "issue": "Refund request — duplicate payment", "priority": "High", "status": "Open"},
    {"id": "#3011", "user": "Ojas Patil", "issue": "Certificate name spelling error", "priority": "Low", "status": "Resolved"},
    {"id": "#3005", "user": "Meher Kaur", "issue": "Unable to access downloaded notes", "priority": "Medium", "status": "In progress"},
])

months = pd.date_range(end=datetime.today(), periods=9, freq="ME").strftime("%b")
REVENUE = pd.DataFrame({
    "Month": months,
    "Revenue (₹L)": [12.4, 13.1, 14.8, 15.2, 16.9, 18.0, 17.4, 19.6, 21.2],
    "New Enrollments": [820, 890, 1010, 970, 1120, 1250, 1180, 1340, 1460],
})

# ──────────────────────────────────────────────────────────────────────────
# SMALL UI HELPERS
# ──────────────────────────────────────────────────────────────────────────
def metric_card(label, value, delta=None, delta_positive=True, navy=False):
    delta_html = ""
    if delta:
        cls = "em-metric-delta-up" if delta_positive else "em-metric-delta-down"
        arrow = "▲" if delta_positive else "▼"
        delta_html = f'<div class="{cls}">{arrow} {delta}</div>'
    card_class = "em-card-navy" if navy else "em-card"
    st.markdown(f"""
        <div class="{card_class}">
            <div class="em-metric-label">{label}</div>
            <div class="em-metric-value">{value}</div>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)

def section_rule(label):
    st.markdown(f'<div class="em-rule"><span>{label}</span></div>', unsafe_allow_html=True)

def progress_bar(pct, width_pct=100):
    st.markdown(f"""
        <div class="em-progress-track" style="width:{width_pct}%;">
            <div class="em-progress-fill" style="width:{pct}%;"></div>
        </div>
    """, unsafe_allow_html=True)

def pill(text, kind="brass"):
    return f'<span class="em-pill em-pill-{kind}">{text}</span>'

# ──────────────────────────────────────────────────────────────────────────
# SIDEBAR — BRAND + NAVIGATION
# ──────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div class="em-brand">
            <div class="em-seal">EA</div>
            <div class="em-brand-text">
                <div class="em-name">Ementora Academy</div>
                <div class="em-tag">Learn with intent</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    portal = st.radio(
        "Portal",
        ["🎓 Student Portal", "🧑‍🏫 Teacher Portal", "🛠️ Admin Portal"],
        label_visibility="collapsed",
    )
    st.markdown("---")

    if "Student" in portal:
        page = st.radio("Go to", ["Dashboard", "My Courses", "Live Classes", "Test Series", "Certificates"], label_visibility="collapsed")
        st.markdown("---")
        st.caption("Signed in as")
        st.markdown("**Ananya Roy**  \nUPSC Foundation 2027")
    elif "Teacher" in portal:
        page = st.radio("Go to", ["Dashboard", "My Batches", "Create Content", "Doubt Queue", "Earnings"], label_visibility="collapsed")
        st.markdown("---")
        st.caption("Signed in as")
        st.markdown("**Dr. A. Sharma**  \nHistory & Polity Mentor")
    else:
        page = st.radio("Go to", ["Dashboard", "Users", "Courses", "Revenue", "Support Tickets"], label_visibility="collapsed")
        st.markdown("---")
        st.caption("Signed in as")
        st.markdown("**Admin — Ops Team**  \nSuper Admin")

# ══════════════════════════════════════════════════════════════════════════
# STUDENT PORTAL
# ══════════════════════════════════════════════════════════════════════════
if "Student" in portal:

    if page == "Dashboard":
        st.markdown('<span class="em-eyebrow">Student Portal</span>', unsafe_allow_html=True)
        st.markdown("## Welcome back, Ananya 👋")
        st.caption("You're 4 days into your longest study streak yet. Keep it going.")
        st.write("")

        c1, c2, c3, c4 = st.columns(4)
        with c1: metric_card("Active Courses", "4", navy=True)
        with c2: metric_card("Study Streak", "4 days", "+1 vs last week", True)
        with c3: metric_card("Avg. Mock Score", "78%", "+6% this month", True)
        with c4: metric_card("All-India Rank", "#1,204", "▲ 312 ranks", True)

        st.write("")
        left, right = st.columns([2, 1])

        with left:
            section_rule("Continue Learning")
            for _, row in COURSES.iterrows():
                st.markdown(f"""
                    <div class="em-card" style="margin-bottom:12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <div style="font-family:'Fraunces',serif; font-weight:600; font-size:16px; color:{INK};">{row['course']}</div>
                                <div style="color:{SLATE}; font-size:13px; margin-top:2px;">Mentor: {row['mentor']}  •  Next: {row['next']}  •  {row['when']}</div>
                            </div>
                            <div style="font-family:'Fraunces',serif; font-weight:600; color:{BRASS}; font-size:18px;">{row['progress']}%</div>
                        </div>
                        <div style="margin-top:10px;">
                """, unsafe_allow_html=True)
                progress_bar(row["progress"])
                st.markdown("</div></div>", unsafe_allow_html=True)

        with right:
            section_rule("Today's Schedule")
            st.markdown(f"""
                <div class="em-card">
                    <div style="margin-bottom:14px;">
                        {pill("LIVE IN 20 MIN", "live")}
                        <div style="font-weight:600; margin-top:6px;">Modern History — Ch. 9</div>
                        <div style="color:{SLATE}; font-size:13px;">6:00 PM • Dr. A. Sharma</div>
                    </div>
                    <div style="margin-bottom:14px;">
                        {pill("SCHEDULED", "brass")}
                        <div style="font-weight:600; margin-top:6px;">Weekly Vocabulary Quiz</div>
                        <div style="color:{SLATE}; font-size:13px;">8:30 PM • Self-paced</div>
                    </div>
                    <div>
                        {pill("COMPLETED", "done")}
                        <div style="font-weight:600; margin-top:6px; opacity:0.6;">Polity — Fundamental Rights</div>
                        <div style="color:{SLATE}; font-size:13px; opacity:0.6;">Yesterday</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    elif page == "My Courses":
        st.markdown('<span class="em-eyebrow">Student Portal</span>', unsafe_allow_html=True)
        st.markdown("## My Courses")
        st.write("")
        tabs = st.tabs(["In Progress", "Completed", "Saved for Later"])
        with tabs[0]:
            for _, row in COURSES.iterrows():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{row['course']}**")
                    st.caption(f"Mentor: {row['mentor']}")
                    progress_bar(row["progress"])
                with col2:
                    st.button("Resume", key=f"resume_{row['course']}")
                st.write("")
        with tabs[1]:
            st.info("Completed courses will appear here along with your certificate download link.")
        with tabs[2]:
            st.info("You haven't saved any courses yet. Browse the catalog to add some.")

    elif page == "Live Classes":
        st.markdown('<span class="em-eyebrow">Student Portal</span>', unsafe_allow_html=True)
        st.markdown("## Live Classes")
        st.write("")
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown(f"""
                <div class="em-card-navy">
                    <div>{pill("● LIVE NOW", "live")}</div>
                    <div style="font-family:'Fraunces',serif; font-size:22px; font-weight:600; margin-top:10px;">Modern History — Ch. 9: The 1857 Uprising</div>
                    <div style="color:{BRASS_SOFT}; margin-top:4px;">Dr. A. Sharma  •  2,341 watching</div>
                </div>
            """, unsafe_allow_html=True)
            st.write("")
            st.button("▶ Join Live Class", type="primary")
            st.write("")
            section_rule("Ask a Doubt")
            st.text_area("Type your question for the mentor", placeholder="e.g. Could you re-explain the causes of the revolt?", label_visibility="collapsed")
            st.button("Submit Question")
        with c2:
            section_rule("Up Next")
            upcoming = [
                ("SSC CGL — Time & Work", "Tomorrow, 8:00 AM"),
                ("Banking Awareness Recap", "Fri, 7:30 PM"),
                ("English Grammar Diagnostic", "Sat, 10:00 AM"),
            ]
            for title, when in upcoming:
                st.markdown(f"""
                    <div class="em-card" style="margin-bottom:10px;">
                        <div style="font-weight:600;">{title}</div>
                        <div style="color:{SLATE}; font-size:13px;">{when}</div>
                    </div>
                """, unsafe_allow_html=True)

    elif page == "Test Series":
        st.markdown('<span class="em-eyebrow">Student Portal</span>', unsafe_allow_html=True)
        st.markdown("## Test Series & Analytics")
        st.write("")
        c1, c2, c3 = st.columns(3)
        with c1: metric_card("Tests Attempted", "10")
        with c2: metric_card("Best Score", f"{TEST_HISTORY['Score'].max()}%")
        with c3: metric_card("Avg. Percentile", f"{int(TEST_HISTORY['Percentile'].mean())}th")

        st.write("")
        section_rule("Score Trend")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=TEST_HISTORY["Test"], y=TEST_HISTORY["Score"],
                                  mode="lines+markers", name="Your Score",
                                  line=dict(color=NAVY, width=3), marker=dict(size=7, color=BRASS)))
        fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=340, yaxis_title="Score (%)")
        st.plotly_chart(fig, use_container_width=True)

        section_rule("Topic-wise Accuracy")
        topics = pd.DataFrame({
            "Topic": ["Modern History", "Polity", "Quant — Arithmetic", "Reasoning", "English Grammar"],
            "Accuracy": [82, 74, 58, 69, 45],
        })
        fig2 = px.bar(topics, x="Accuracy", y="Topic", orientation="h",
                      color="Accuracy", color_continuous_scale=[SLATE, BRASS])
        fig2.update_layout(**PLOTLY_TEMPLATE["layout"], height=300, showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    elif page == "Certificates":
        st.markdown('<span class="em-eyebrow">Student Portal</span>', unsafe_allow_html=True)
        st.markdown("## Certificates")
        st.write("")
        st.markdown(f"""
            <div class="em-card" style="text-align:center; padding:40px;">
                <div style="font-family:'Fraunces',serif; font-size:20px; color:{SLATE};">
                    Complete a course to unlock your certificate of achievement.
                </div>
                <div style="margin-top:10px; color:{SLATE}; font-size:13px;">
                    Banking Awareness 2026 is 89% complete — almost there!
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.write("")
        progress_bar(89)

# ══════════════════════════════════════════════════════════════════════════
# TEACHER PORTAL
# ══════════════════════════════════════════════════════════════════════════
elif "Teacher" in portal:

    if page == "Dashboard":
        st.markdown('<span class="em-eyebrow">Teacher Portal</span>', unsafe_allow_html=True)
        st.markdown("## Good evening, Dr. Sharma")
        st.caption("Your 6:00 PM live class starts in 20 minutes.")
        st.write("")

        c1, c2, c3, c4 = st.columns(4)
        with c1: metric_card("Students Enrolled", "1,284", navy=True)
        with c2: metric_card("Avg. Watch Time", "38 min", "+3 min", True)
        with c3: metric_card("Rating", "4.8 / 5", "+0.1", True)
        with c4: metric_card("Open Doubts", str((DOUBTS["status"] == "Open").sum()), "2 new today", False)

        st.write("")
        left, right = st.columns([3, 2])
        with left:
            section_rule("Engagement — Last 8 Sessions")
            eng = pd.DataFrame({
                "Session": [f"S{i}" for i in range(1, 9)],
                "Attendance": rng.integers(800, 1300, 8),
            })
            fig = px.area(eng, x="Session", y="Attendance")
            fig.update_traces(line_color=NAVY, fillcolor="rgba(21,42,82,0.15)")
            fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=300)
            st.plotly_chart(fig, use_container_width=True)
        with right:
            section_rule("Recent Doubts")
            for _, row in DOUBTS.iterrows():
                kind = "live" if row["status"] == "Open" else "done"
                st.markdown(f"""
                    <div class="em-card" style="margin-bottom:10px;">
                        <div style="display:flex; justify-content:space-between;">
                            <div style="font-weight:600;">{row['student']}</div>
                            {pill(row['status'], kind)}
                        </div>
                        <div style="color:{SLATE}; font-size:13px; margin-top:4px;">{row['topic']} • {row['asked']}</div>
                    </div>
                """, unsafe_allow_html=True)

    elif page == "My Batches":
        st.markdown('<span class="em-eyebrow">Teacher Portal</span>', unsafe_allow_html=True)
        st.markdown("## My Batches")
        st.write("")
        my_students = STUDENTS.copy()
        st.dataframe(
            my_students.style.background_gradient(subset=["attendance", "last_score"], cmap="YlOrBr"),
            use_container_width=True, hide_index=True,
        )
        st.write("")
        section_rule("Take Attendance")
        cols = st.columns(3)
        for i, name in enumerate(STUDENTS["name"]):
            with cols[i % 3]:
                st.checkbox(name, value=True, key=f"att_{name}")
        st.button("Save Attendance", type="primary")

    elif page == "Create Content":
        st.markdown('<span class="em-eyebrow">Teacher Portal</span>', unsafe_allow_html=True)
        st.markdown("## Create Content")
        st.write("")
        tabs = st.tabs(["Schedule Live Class", "Upload Recording", "Build a Quiz"])
        with tabs[0]:
            c1, c2 = st.columns(2)
            with c1:
                st.text_input("Class title", placeholder="e.g. Modern History — Ch. 10")
                st.selectbox("Batch", STUDENTS["batch"].unique())
                st.date_input("Date")
            with c2:
                st.text_area("Description", placeholder="What will this class cover?", height=110)
                st.time_input("Start time")
            st.button("Schedule Class", type="primary")
        with tabs[1]:
            st.file_uploader("Upload lecture video", type=["mp4", "mov"])
            st.text_input("Title")
            st.multiselect("Tag topics", ["History", "Polity", "Quant", "Reasoning", "English"])
            st.button("Publish Recording", type="primary")
        with tabs[2]:
            st.text_input("Quiz title")
            n = st.slider("Number of questions", 1, 20, 5)
            st.caption(f"Add {n} question(s) below (prototype — expand as needed).")
            for i in range(min(n, 3)):
                with st.expander(f"Question {i+1}"):
                    st.text_input("Question text", key=f"q_{i}")
                    st.text_input("Correct answer", key=f"a_{i}")
            st.button("Publish Quiz", type="primary")

    elif page == "Doubt Queue":
        st.markdown('<span class="em-eyebrow">Teacher Portal</span>', unsafe_allow_html=True)
        st.markdown("## Doubt Queue")
        st.write("")
        for _, row in DOUBTS.iterrows():
            kind = "live" if row["status"] == "Open" else "done"
            with st.container():
                st.markdown(f"""
                    <div class="em-card" style="margin-bottom:12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <div style="font-weight:600;">{row['student']}</div>
                                <div style="color:{SLATE}; font-size:13px;">{row['topic']} • asked {row['asked']}</div>
                            </div>
                            {pill(row['status'], kind)}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                if row["status"] == "Open":
                    st.text_input("Reply", key=f"reply_{row['student']}", label_visibility="collapsed", placeholder="Type your answer…")

    elif page == "Earnings":
        st.markdown('<span class="em-eyebrow">Teacher Portal</span>', unsafe_allow_html=True)
        st.markdown("## Earnings")
        st.write("")
        c1, c2, c3 = st.columns(3)
        with c1: metric_card("This Month", "₹1,84,200", "+12%", True, navy=True)
        with c2: metric_card("Lifetime Payout", "₹22.6L")
        with c3: metric_card("Next Payout Date", "15 Jul")

        st.write("")
        section_rule("Monthly Payout Trend")
        payout = pd.DataFrame({"Month": months, "Payout (₹K)": [142, 151, 163, 158, 171, 179, 174, 182, 184]})
        fig = px.bar(payout, x="Month", y="Payout (₹K)", color_discrete_sequence=[BRASS])
        fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=300)
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# ADMIN PORTAL
# ══════════════════════════════════════════════════════════════════════════
else:

    if page == "Dashboard":
        st.markdown('<span class="em-eyebrow">Admin Portal</span>', unsafe_allow_html=True)
        st.markdown("## Platform Overview")
        st.caption("All systems operational • Last synced just now")
        st.write("")

        c1, c2, c3, c4 = st.columns(4)
        with c1: metric_card("Total Students", "48,920", "+2.4% MoM", True, navy=True)
        with c2: metric_card("Total Educators", "312", "+6 this month", True)
        with c3: metric_card("Monthly Revenue", "₹21.2L", "+8.2%", True)
        with c4: metric_card("Open Tickets", str((TICKETS["status"] == "Open").sum()), "2 high priority", False)

        st.write("")
        left, right = st.columns([3, 2])
        with left:
            section_rule("Revenue & Enrollment Trend")
            fig = go.Figure()
            fig.add_trace(go.Bar(x=REVENUE["Month"], y=REVENUE["Revenue (₹L)"], name="Revenue (₹L)", marker_color=NAVY, yaxis="y1"))
            fig.add_trace(go.Scatter(x=REVENUE["Month"], y=REVENUE["New Enrollments"], name="New Enrollments",
                                      mode="lines+markers", line=dict(color=BRASS, width=3), yaxis="y2"))
            fig.update_layout(
                **PLOTLY_TEMPLATE["layout"], height=340,
                yaxis=dict(title="Revenue (₹L)"),
                yaxis2=dict(title="Enrollments", overlaying="y", side="right", showgrid=False),
            )
            st.plotly_chart(fig, use_container_width=True)
        with right:
            section_rule("System Health")
            health = [
                ("Video CDN Uptime", "99.98%", GOOD),
                ("Avg. App Crash Rate", "0.02%", GOOD),
                ("Live Class Latency", "1.4s", GOOD),
                ("Payment Gateway", "Operational", GOOD),
            ]
            for label, val, color in health:
                st.markdown(f"""
                    <div class="em-card" style="margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;">
                        <span style="color:{SLATE}; font-size:13.5px;">{label}</span>
                        <span style="font-weight:700; color:{color};">{val}</span>
                    </div>
                """, unsafe_allow_html=True)

    elif page == "Users":
        st.markdown('<span class="em-eyebrow">Admin Portal</span>', unsafe_allow_html=True)
        st.markdown("## User Management")
        st.write("")
        c1, c2 = st.columns([1, 3])
        with c1:
            role_filter = st.selectbox("Filter by role", ["All", "Student", "Educator"])
        filtered = ALL_USERS if role_filter == "All" else ALL_USERS[ALL_USERS["role"] == role_filter]
        st.dataframe(filtered, use_container_width=True, hide_index=True)
        st.write("")
        section_rule("Add a New User")
        c1, c2, c3 = st.columns(3)
        with c1: st.text_input("Full name")
        with c2: st.selectbox("Role", ["Student", "Educator", "Support Staff"])
        with c3: st.selectbox("Plan", ["Basic", "Pro Monthly", "Pro Annual", "—"])
        st.button("Create User", type="primary")

    elif page == "Courses":
        st.markdown('<span class="em-eyebrow">Admin Portal</span>', unsafe_allow_html=True)
        st.markdown("## Course Management")
        st.write("")
        course_admin = COURSES.copy()
        course_admin["status"] = ["Published", "Published", "Published", "Under Review"]
        course_admin["enrolled"] = [12480, 8320, 15990, 210]
        st.dataframe(course_admin[["course", "mentor", "status", "enrolled"]], use_container_width=True, hide_index=True)
        st.write("")
        section_rule("Create / Approve Course")
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Course title")
            st.selectbox("Category", ["UPSC", "SSC", "Banking", "State PSC", "English & Aptitude"])
        with c2:
            st.selectbox("Assign Educator", ALL_USERS[ALL_USERS["role"] == "Educator"]["name"])
            st.number_input("Price (₹)", min_value=0, value=2999, step=100)
        st.button("Submit for Approval", type="primary")

    elif page == "Revenue":
        st.markdown('<span class="em-eyebrow">Admin Portal</span>', unsafe_allow_html=True)
        st.markdown("## Revenue & Business Metrics")
        st.write("")
        c1, c2, c3, c4 = st.columns(4)
        with c1: metric_card("MRR", "₹21.2L", "+8.2%", True, navy=True)
        with c2: metric_card("ARPU", "₹433", "+1.9%", True)
        with c3: metric_card("Churn Rate", "3.1%", "-0.4pt", True)
        with c4: metric_card("LTV : CAC", "4.2x")

        st.write("")
        section_rule("Revenue by Category")
        cat_rev = pd.DataFrame({
            "Category": ["UPSC", "SSC", "Banking", "State PSC", "English & Aptitude"],
            "Revenue (₹L)": [8.9, 5.4, 3.6, 2.1, 1.2],
        })
        fig = px.pie(cat_rev, names="Category", values="Revenue (₹L)", hole=0.55,
                     color_discrete_sequence=[NAVY, BRASS, SLATE, NAVY_SOFT, BRASS_SOFT])
        fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=340)
        st.plotly_chart(fig, use_container_width=True)

    elif page == "Support Tickets":
        st.markdown('<span class="em-eyebrow">Admin Portal</span>', unsafe_allow_html=True)
        st.markdown("## Support Tickets")
        st.write("")
        status_filter = st.multiselect("Filter by status", TICKETS["status"].unique().tolist(), default=TICKETS["status"].unique().tolist())
        view = TICKETS[TICKETS["status"].isin(status_filter)]
        st.dataframe(view, use_container_width=True, hide_index=True)
