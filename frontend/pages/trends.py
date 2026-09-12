"""Trend dashboard page."""

import streamlit as st
import plotly.graph_objects as go
from styleiq.services.trend_service import trend_service


def render():
    st.title("📈 Trend Dashboard")
    st.markdown("Evidence-based Pakistani fashion trend intelligence. Every score is computed from real signals.")
    st.markdown("---")

    with st.spinner("Loading trend scores..."):
        top_trends = trend_service.get_trending_now(top_n=5)
        emerging = trend_service.get_emerging_trends()

    # ── Trending Now ───────────────────────────────────────────────────
    st.subheader("🔥 Trending Now — Pakistan Fashion")

    for i, t in enumerate(top_trends):
        status_colors = {
            "emerging": "🟡", "rising": "🟢",
            "peaking": "🟢", "declining": "🔴",
        }
        emoji = status_colors.get(t.status, "⚪")

        with st.expander(f"{emoji} **{t.trend_name}** [{t.category}] — Score: {t.total_score}/100",
                         expanded=(i == 0)):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**Status:** `{t.status.upper()}`")

                # Score breakdown bar chart
                fig = go.Figure(go.Bar(
                    x=[t.popularity_score, t.growth_score,
                       t.cross_brand_score, t.seasonal_score],
                    y=["Popularity", "Growth", "Cross-Brand", "Seasonal"],
                    orientation='h',
                    marker_color=['#C9A84C', '#3FB950', '#1F6FEB', '#D29922'],
                    text=[f"{v:.0f}" for v in [t.popularity_score, t.growth_score,
                                                t.cross_brand_score, t.seasonal_score]],
                    textposition='outside',
                ))
                fig.update_layout(
                    paper_bgcolor='#0D1117', plot_bgcolor='#0D1117',
                    font=dict(color='#E6EDF3'),
                    xaxis=dict(range=[0, 115], gridcolor='#21262D'),
                    yaxis=dict(gridcolor='#21262D'),
                    height=200, margin=dict(l=10, r=40, t=10, b=10),
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.metric("Total Score", f"{t.total_score}/100")
                if t.brand_count:
                    st.metric("Brands", f"{int(t.brand_count)}")
                if t.growth_rate_pct is not None:
                    st.metric("Search Growth", f"{t.growth_rate_pct:+.0f}%")
                if t.season:
                    st.metric("Season", t.season.title())

                st.markdown("**Evidence:**")
                for signal in t.supporting_signals:
                    st.caption(f"→ {signal}")

    st.markdown("---")

    # ── Emerging Trends ────────────────────────────────────────────────
    st.subheader("🌱 Emerging Trends — Watch These")
    if emerging:
        for t in emerging:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{t.trend_name}** [{t.category}]")
            with col2:
                st.markdown(f"Score: `{t.total_score}`")
            with col3:
                st.markdown(f"Growth: `{t.growth_score:.0f}`")
    else:
        st.info("No emerging trends detected yet.")

    st.markdown("---")

    # ── Score comparison ───────────────────────────────────────────────
    st.subheader("📊 All Trends Comparison")
    names = [t.trend_name for t in top_trends]
    total_scores = [t.total_score for t in top_trends]

    fig = go.Figure(go.Bar(
        x=names, y=total_scores,
        marker_color=['#C9A84C' if s >= 70 else '#3FB950' if s >= 50 else '#8B949E'
                      for s in total_scores],
        text=[f"{s:.0f}" for s in total_scores],
        textposition='outside',
    ))
    fig.update_layout(
        paper_bgcolor='#0D1117', plot_bgcolor='#0D1117',
        font=dict(color='#E6EDF3'),
        yaxis=dict(range=[0, 110], gridcolor='#21262D'),
        xaxis=dict(gridcolor='#21262D'),
        height=300, margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.caption("Trend scores are computed from brand appearances, search volume growth, cross-brand adoption, and seasonal relevance. No scores are invented.")
