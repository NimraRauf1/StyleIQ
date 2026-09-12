"""
STYLEIQ — Streamlit Frontend
Main entry point. Handles navigation and session state.

Run with: streamlit run frontend/app.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="STYLEIQ — Pakistan Fashion Intelligence",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        color: #C9A84C;
        letter-spacing: -0.5px;
    }
    .sub-header {
        font-size: 1rem;
        color: #8B949E;
        margin-top: -10px;
    }
    .metric-card {
        background: #161B22;
        border: 1px solid #30363D;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    .trend-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .score-bar-container {
        background: #21262D;
        border-radius: 6px;
        height: 8px;
        margin: 4px 0;
    }
    .gold-divider {
        border: 1px solid #C9A84C;
        margin: 20px 0;
    }
    [data-testid="stSidebar"] {
        background-color: #0D1117;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state defaults ─────────────────────────────────────────────────
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "onboarded" not in st.session_state:
    st.session_state.onboarded = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# ── Sidebar navigation ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="main-header">STYLEIQ</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Pakistan Fashion Intelligence</p>', unsafe_allow_html=True)
    st.markdown("---")

    if st.session_state.user_name:
        st.success(f"👤 {st.session_state.user_name}")
        st.markdown("---")

    pages = {
        "🏠 Home":             "Home",
        "✨ Style Onboarding": "Onboarding",
        "🧬 My Style DNA":     "DNA",
        "📈 Trend Dashboard":  "Trends",
        "🏷️ Brand Match":      "Brands",
    }

    for label, page in pages.items():
        if st.button(label, use_container_width=True,
                     type="primary" if st.session_state.current_page == page else "secondary"):
            st.session_state.current_page = page
            st.rerun()

    st.markdown("---")
    st.caption("Milestone 7 — MVP Frontend")
    st.caption("Built with Python + Streamlit")

# ── Page routing ───────────────────────────────────────────────────────────
page = st.session_state.current_page

if page == "Home":
    st.markdown('<h1 class="main-header">STYLEIQ ✨</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Pakistan Fashion Intelligence & Personal Stylist Agent</p>',
                unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Pakistani Brands", "15", "Tracked")
    with col2:
        st.metric("Fashion Trends", "5", "Scored")
    with col3:
        st.metric("Garment Categories", "42", "Classified")
    with col4:
        st.metric("Cities Covered", "7", "Climate-aware")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("What STYLEIQ Does")
        st.markdown("""
        **STYLEIQ** is not a generic AI fashion recommender.
        It is a fashion intelligence system built for Pakistan.

        - 🧬 **Style DNA** — learns your aesthetic from interactions
        - 📈 **Trend Detection** — evidence-based, not guessed
        - 🏷️ **Brand Matching** — best brands *for you*, not best brands generally
        - 🌦️ **Weather-aware** — Islamabad ≠ Karachi ≠ Quetta
        - 🕌 **Occasion Intelligence** — Mehndi, Eid, university, dawat
        - 💰 **Budget-aware** — PKR ranges, not dollar prices
        """)

    with col2:
        st.subheader("Get Started")
        st.info("Complete the Style Onboarding to create your personal Style DNA.")
        if st.button("✨ Start Style Onboarding", type="primary", use_container_width=True):
            st.session_state.current_page = "Onboarding"
            st.rerun()

        st.subheader("Explore Without Profile")
        if st.button("📈 View Trend Dashboard", use_container_width=True):
            st.session_state.current_page = "Trends"
            st.rerun()
        if st.button("🏷️ View Brand Intelligence", use_container_width=True):
            st.session_state.current_page = "Brands"
            st.rerun()

elif page == "Onboarding":
    from frontend.pages.onboarding import render
    render()

elif page == "DNA":
    from frontend.pages.style_dna import render
    render()

elif page == "Trends":
    from frontend.pages.trends import render
    render()

elif page == "Brands":
    from frontend.pages.brands import render
    render()
