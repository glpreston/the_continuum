# continuum/ui/panels/actor_profiles_panel.py

import streamlit as st
from continuum.persona.actor_cards import ACTOR_CARDS, ActorCard


def render_actor_profiles():
    """Render the J12 Actor Personality Cards in the sidebar."""

    st.subheader("Actor Profiles")

    for actor_id, card in ACTOR_CARDS.items():
        with st.expander(f"{card.ui['icon']}  {card.role_name}", expanded=False):

            # Essence
            st.markdown(f"**Essence:** {card.essence}")

            # Cognitive Style
            st.markdown("**Cognitive Style**")
            for item in card.cognitive_style:
                st.markdown(f"- {item}")

            # Strengths
            st.markdown("**Strengths**")
            for item in card.strengths:
                st.markdown(f"- {item}")

            # Blind Spots
            st.markdown("**Blind Spots**")
            for item in card.blind_spots:
                st.markdown(f"- {item}")

            # Preferred Domains
            st.markdown("**Preferred Domains**")
            st.markdown(", ".join(card.preferred_domains))

            # Example Snippet
            st.markdown("**Example Reasoning Snippet**")
            st.markdown(f"> {card.example_snippet}")

            # UI Metadata (optional)
            st.caption(f"Label: {card.ui['label']} • Color: {card.ui['color']}")