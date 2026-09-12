"""Style DNA visualization page."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from styleiq.services.style_dna_service import style_dna_service


def _make_radar_chart(dna_dict: dict, title: str) -> go.Figure:
    """Create a radar chart for Style DNA visualization."""
    categories = list(dna_dict.keys())
    values = list(dna_dict.values())
    values_closed = values + [values[0]]
    categories_closed = categories + [categories[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(201, 168, 76, 0.2)',
        line=dict(color='#C9A84C', width=2),
        name='Style DNA',
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100],
                            gridcolor='#30363D', color='#8B949E'),
            angularaxis=dict(gridcolor='#30363D', color='#E6EDF3'),
            bgcolor='#0D1117',
        ),
        paper_bgcolor='#0D1117',
        plot_bgcolor='#0D1117',
        font=dict(color='#E6EDF3'),
        title=dict(text=title, font=dict(color='#C9A84C', size=14)),
        showlegend=False,
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig


def _make_bar_chart(dna_dict: dict) -> go.Figure:
    """Create a horizontal bar chart for Style DNA."""
    sorted_items = sorted(dna_dict.items(), key=lambda x: x[1], reverse=True)
    labels = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]
    colors = ['#C9A84C' if v >= 70 else '#3FB950' if v >= 50 else '#8B949E' for v in values]

    fig = go.Figure(go.Bar(
        x=values, y=labels,
        orientation='h',
        marker_color=colors,
        text=[f"{v:.0f}" for v in values],
        textposition='outside',
        textfont=dict(color='#E6EDF3'),
    ))
    fig.update_layout(
        paper_bgcolor='#0D1117',
        plot_bgcolor='#0D1117',
        font=dict(color='#E6EDF3'),
        xaxis=dict(range=[0, 110], gridcolor='#21262D', color='#8B949E'),
        yaxis=dict(gridcolor='#21262D', color='#E6EDF3'),
        margin=dict(l=20, r=60, t=20, b=20),
        height=350,
    )
    return fig


def render():
    st.title("🧬 My Style DNA")

    if not st.session_state.get("user_id"):
        st.warning("Complete the Style Onboarding first to see your Style DNA.")
        if st.button("✨ Go to Onboarding", type="primary"):
            st.session_state.current_page = "Onboarding"
            st.rerun()
        return

    user_id = st.session_state.user_id
    dna = style_dna_service.get_current_dna(user_id)

    if not dna:
        st.error("No Style DNA found. Please complete onboarding.")
        return

    archetype = style_dna_service.get_style_archetype(dna)

    # ── Header ─────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Style Archetype", archetype)
    with col2:
        st.metric("DNA Version", f"v{dna.version}")
    with col3:
        st.metric("Interactions", dna.interaction_count)
    with col4:
        st.metric("Modesty Score", f"{dna.modesty_score:.0f}/100")

    st.markdown("---")

    # ── Charts ─────────────────────────────────────────────────────────
    aesthetic_dna = {
        "Minimal": dna.minimal,
        "Feminine": dna.feminine,
        "Traditional": dna.traditional,
        "Contemporary": dna.contemporary,
        "Romantic": dna.romantic,
        "Classic": dna.classic,
        "Streetwear": dna.streetwear,
        "Bohemian": dna.bohemian,
        "Edgy": dna.edgy,
    }

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(_make_radar_chart(aesthetic_dna, "Style DNA Radar"), use_container_width=True)
    with col2:
        st.plotly_chart(_make_bar_chart(aesthetic_dna), use_container_width=True)

    st.markdown("---")

    # ── DNA breakdown ──────────────────────────────────────────────────
    st.subheader("📊 Full DNA Breakdown")
    col1, col2 = st.columns(2)

    all_dims = {
        "Minimal": dna.minimal, "Maximalist": dna.maximalist,
        "Feminine": dna.feminine, "Androgynous": dna.androgynous,
        "Traditional": dna.traditional, "Contemporary": dna.contemporary,
        "Romantic": dna.romantic, "Edgy": dna.edgy,
        "Streetwear": dna.streetwear, "Classic": dna.classic,
        "Bohemian": dna.bohemian,
    }
    items = list(all_dims.items())
    half = len(items) // 2

    for col, chunk in zip([col1, col2], [items[:half], items[half:]]):
        with col:
            for name, score in chunk:
                col.write(f"**{name}**")
                col.progress(int(score), text=f"{score:.0f}/100")

    st.markdown("---")

    # ── Eastern/Western & Modesty ──────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Eastern ↔ Western")
        eastern = dna.eastern_affinity
        western = 100 - eastern
        fig = go.Figure(go.Bar(
            x=[eastern, western],
            y=["Eastern", "Western"],
            orientation='h',
            marker_color=['#C9A84C', '#3FB950'],
        ))
        fig.update_layout(
            paper_bgcolor='#0D1117', plot_bgcolor='#0D1117',
            font=dict(color='#E6EDF3'), height=150,
            xaxis=dict(range=[0, 100], gridcolor='#21262D'),
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Modesty Profile")
        modesty_labels = {
            (0, 25): "Relaxed Coverage",
            (25, 50): "Moderate",
            (50, 75): "Conservative",
            (75, 100): "Modest / Full Coverage",
        }
        modesty_score = dna.modesty_score
        label = next((v for (lo, hi), v in modesty_labels.items()
                      if lo <= modesty_score < hi), "Full Modest")
        st.metric("Modesty Level", label)
        st.progress(int(modesty_score), text=f"{modesty_score:.0f}/100")

    st.markdown("---")

    # ── Simulate interaction ───────────────────────────────────────────
    st.subheader("🔄 Update Your DNA")
    st.caption("Simulate a like or dislike to see how your DNA evolves in real time.")

    col1, col2, col3 = st.columns(3)
    with col1:
        interaction_type = st.selectbox("Interaction", ["like", "save", "dislike", "skip"])
    with col2:
        tags = st.multiselect("Item Tags", ["minimal", "feminine", "contemporary",
                                             "traditional", "romantic", "streetwear",
                                             "bohemian", "maximalist", "ethnic",
                                             "classic", "clean_girl", "soft_girl"])
    with col3:
        family = st.selectbox("Garment Family", ["eastern", "western", "modest", "fusion"])

    if st.button("Apply Interaction", type="primary"):
        if tags:
            style_dna_service.update_from_interaction(
                user_id=user_id,
                interaction_type=interaction_type,
                item_aesthetic_tags=tags,
                item_garment_family=family,
            )
            st.success(f"DNA updated! Version {dna.version} → {dna.version + 1}")
            st.rerun()
        else:
            st.warning("Select at least one tag.")

    # ── Version history ────────────────────────────────────────────────
    history = style_dna_service.get_dna_history(user_id)
    if len(history) > 1:
        st.markdown("---")
        st.subheader(f"📜 DNA History — {len(history)} versions")
        versions = [f"v{h.version}" for h in history]
        minimal_scores = [h.minimal for h in history]
        feminine_scores = [h.feminine for h in history]
        contemporary_scores = [h.contemporary for h in history]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=versions, y=minimal_scores,
                                  mode='lines+markers', name='Minimal',
                                  line=dict(color='#C9A84C')))
        fig.add_trace(go.Scatter(x=versions, y=feminine_scores,
                                  mode='lines+markers', name='Feminine',
                                  line=dict(color='#3FB950')))
        fig.add_trace(go.Scatter(x=versions, y=contemporary_scores,
                                  mode='lines+markers', name='Contemporary',
                                  line=dict(color='#1F6FEB')))
        fig.update_layout(
            paper_bgcolor='#0D1117', plot_bgcolor='#0D1117',
            font=dict(color='#E6EDF3'),
            xaxis=dict(gridcolor='#21262D', color='#8B949E'),
            yaxis=dict(gridcolor='#21262D', range=[0, 100], color='#8B949E'),
            legend=dict(bgcolor='#161B22', bordercolor='#30363D'),
            margin=dict(l=20, r=20, t=20, b=20),
            height=300,
        )
        st.plotly_chart(fig, use_container_width=True)
