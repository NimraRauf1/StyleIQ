"""Onboarding page — collects user profile and seeds Style DNA."""

import streamlit as st
from styleiq.services.style_dna_service import style_dna_service


def render():
    st.title("✨ Style Onboarding")
    st.markdown("Tell us about yourself. All body-related fields are optional — always.")
    st.markdown("---")

    with st.form("onboarding_form"):
        # ── Identity ───────────────────────────────────────────────────
        st.subheader("👤 About You")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Your name", placeholder="Nimra")
            email = st.text_input("Email", placeholder="nimra@example.com")
            age = st.number_input("Age", min_value=13, max_value=80, value=22)
        with col2:
            city = st.selectbox("City", [
                "islamabad", "rawalpindi", "lahore", "karachi",
                "peshawar", "multan", "quetta", "faisalabad", "other"
            ])
            occupation = st.text_input("Occupation / Status",
                                       placeholder="University student, Teacher, etc.")

        st.markdown("---")

        # ── Style preferences ──────────────────────────────────────────
        st.subheader("🎨 Your Style")
        col1, col2 = st.columns(2)
        with col1:
            modesty = st.select_slider(
                "Modesty Preference",
                options=[1, 2, 3, 4, 5],
                value=3,
                format_func=lambda x: {
                    1: "1 — Minimal", 2: "2 — Relaxed",
                    3: "3 — Moderate", 4: "4 — Modest", 5: "5 — Full Modest"
                }[x]
            )
        with col2:
            eastern_western = st.slider(
                "Eastern ↔ Western Preference",
                min_value=0.0, max_value=1.0, value=0.5, step=0.1,
                help="0 = Fully Eastern | 0.5 = Mixed | 1 = Fully Western"
            )

        aesthetics = st.multiselect(
            "Preferred Aesthetics (choose all that feel like you)",
            options=["minimal", "feminine", "contemporary", "traditional",
                     "romantic", "classic", "bohemian", "streetwear",
                     "edgy", "maximalist", "soft_girl", "clean_girl"],
            default=["minimal", "feminine"],
        )

        col1, col2 = st.columns(2)
        with col1:
            liked_colors = st.text_input(
                "Favourite Colors",
                placeholder="beige, white, olive, blush pink",
                help="Comma-separated"
            )
        with col2:
            disliked_colors = st.text_input(
                "Colors You Avoid",
                placeholder="neon yellow, orange",
                help="Comma-separated"
            )

        st.markdown("---")

        # ── Occasions ──────────────────────────────────────────────────
        st.subheader("📅 Your Occasions")
        occasions = st.multiselect(
            "What do you usually dress for?",
            options=["university", "office_casual", "office_formal", "home",
                     "brunch", "dinner", "dawat", "cafe", "friend_gathering",
                     "eid", "eid_milan", "mehndi", "dholki", "nikkah",
                     "baraat", "walima", "airport", "travel_local"],
            default=["university", "brunch", "dawat", "eid"],
        )

        st.markdown("---")

        # ── Budget ─────────────────────────────────────────────────────
        st.subheader("💰 Budget")
        col1, col2 = st.columns(2)
        with col1:
            budget_min = st.number_input("Minimum Budget (PKR)", value=2000, step=500)
        with col2:
            budget_max = st.number_input("Maximum Budget (PKR)", value=8000, step=500)

        st.markdown("---")

        # ── Submit ─────────────────────────────────────────────────────
        submitted = st.form_submit_button("✨ Create My Style Profile", type="primary",
                                          use_container_width=True)

    if submitted:
        if not name or not email:
            st.error("Please enter your name and email.")
            return

        if budget_min >= budget_max:
            st.error("Maximum budget must be greater than minimum budget.")
            return

        with st.spinner("Creating your Style DNA..."):
            try:
                # Create user
                user_id = style_dna_service.create_user(
                    email=email,
                    username=name.lower().replace(" ", "_"),
                )

                # Parse colors
                preferred_colors = [c.strip() for c in liked_colors.split(",") if c.strip()]
                disliked_colors_list = [c.strip() for c in disliked_colors.split(",") if c.strip()]

                # Seed DNA
                style_dna_service.seed_from_onboarding(
                    user_id=user_id,
                    age=int(age),
                    city=city,
                    modesty_level=int(modesty),
                    eastern_western_pref=float(eastern_western),
                    preferred_aesthetics=aesthetics,
                    preferred_silhouettes=[],
                    preferred_colors=preferred_colors,
                    usual_occasions=occasions,
                    budget_min=int(budget_min),
                    budget_max=int(budget_max),
                )

                # Save to session
                st.session_state.user_id = user_id
                st.session_state.user_name = name
                st.session_state.onboarded = True

                st.success(f"✨ Welcome, {name}! Your Style DNA has been created.")
                st.balloons()

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🧬 View My Style DNA", type="primary", use_container_width=True):
                        st.session_state.current_page = "DNA"
                        st.rerun()
                with col2:
                    if st.button("📈 View Trends", use_container_width=True):
                        st.session_state.current_page = "Trends"
                        st.rerun()

            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")
