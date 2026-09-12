"""Brand compatibility page."""

import streamlit as st
import plotly.graph_objects as go
from styleiq.services.brand_service import brand_service


def render():
    st.title("🏷️ Brand Intelligence")
    st.markdown("---")

    # ── User profile inputs ────────────────────────────────────────────
    with st.expander("⚙️ Adjust Your Profile for Brand Matching", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            budget_min = st.number_input("Budget Min (PKR)", value=2000, step=500)
            budget_max = st.number_input("Budget Max (PKR)", value=8000, step=500)
        with col2:
            modesty = st.slider("Modesty Level", 1, 5, 3)
            aesthetics = st.multiselect(
                "Your Aesthetics",
                ["minimal", "feminine", "contemporary", "traditional",
                 "romantic", "classic", "bohemian", "streetwear"],
                default=["minimal", "feminine", "contemporary"],
            )
        with col3:
            occasions = st.multiselect(
                "Your Occasions",
                ["university", "office_casual", "office_formal", "brunch",
                 "dinner", "dawat", "eid", "mehndi", "walima", "cafe"],
                default=["university", "brunch", "dawat", "eid"],
            )

    if st.button("🔍 Find My Best Brands", type="primary", use_container_width=True):
        with st.spinner("Computing brand compatibility..."):
            top_brands = brand_service.get_compatible_brands(
                user_budget_min=int(budget_min),
                user_budget_max=int(budget_max),
                user_modesty_level=int(modesty),
                user_style_tags=aesthetics,
                user_aesthetics=aesthetics,
                user_occasions=occasions,
                top_n=8,
            )
        st.session_state.brand_results = top_brands

    if "brand_results" not in st.session_state:
        st.info("Adjust your profile above and click 'Find My Best Brands'.")
        return

    top_brands = st.session_state.brand_results

    # ── Top brands ─────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader(f"✨ Your Top {len(top_brands)} Brand Matches")

    for i, score in enumerate(top_brands):
        medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
        tier_colors = {
            "mass_market": "🟢", "premium_mid": "🔵",
            "premium": "🟣", "luxury": "🟠", "western_casual": "🟡"
        }
        tier_emoji = tier_colors.get(score.brand_tier, "⚪")

        with st.expander(
            f"{medal} **{score.brand_name}** {tier_emoji} — Overall: {score.overall_score}/100",
            expanded=(i < 3)
        ):
            col1, col2 = st.columns([2, 1])

            with col1:
                # Score breakdown
                fig = go.Figure(go.Bar(
                    x=[score.style_match, score.budget_match,
                       score.modesty_match, score.occasion_match],
                    y=["Style Match", "Budget Match", "Modesty Match", "Occasion Match"],
                    orientation='h',
                    marker_color=['#C9A84C', '#3FB950', '#1F6FEB', '#D29922'],
                    text=[f"{v:.0f}" for v in [score.style_match, score.budget_match,
                                                score.modesty_match, score.occasion_match]],
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
                st.metric("Overall Score", f"{score.overall_score}/100")
                if score.typical_price_min and score.typical_price_max:
                    st.metric("Price Range",
                              f"PKR {score.typical_price_min:,}–{score.typical_price_max:,}")
                st.markdown(f"**Tier:** `{score.brand_tier.replace('_', ' ').title()}`")
                st.caption(score.summary)

                if score.budget_reason:
                    st.caption(f"💰 {score.budget_reason}")
                if score.modesty_reason:
                    st.caption(f"🧕 {score.modesty_reason}")

    # ── Comparison chart ───────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📊 Brand Score Comparison")

    names = [s.brand_name for s in top_brands[:6]]
    fig = go.Figure()
    for label, scores, color in [
        ("Style", [s.style_match for s in top_brands[:6]], "#C9A84C"),
        ("Budget", [s.budget_match for s in top_brands[:6]], "#3FB950"),
        ("Modesty", [s.modesty_match for s in top_brands[:6]], "#1F6FEB"),
        ("Occasion", [s.occasion_match for s in top_brands[:6]], "#D29922"),
    ]:
        fig.add_trace(go.Bar(name=label, x=names, y=scores,
                             marker_color=color))
    fig.update_layout(
        barmode='group',
        paper_bgcolor='#0D1117', plot_bgcolor='#0D1117',
        font=dict(color='#E6EDF3'),
        yaxis=dict(range=[0, 110], gridcolor='#21262D'),
        xaxis=dict(gridcolor='#21262D'),
        legend=dict(bgcolor='#161B22', bordercolor='#30363D'),
        height=350, margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)
