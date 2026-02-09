#continuum/ui/pages/5_Persona_Designer.py

import streamlit as st
import json
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import declarative_base
from continuum.orchestrator.continuum_controller import ContinuumController
from continuum.aira.meta_rewrite import meta_rewrite_llm
from continuum.persona.style_rewrite import apply_style

Base = declarative_base()


# -------------------------------------------------------------------------
# ORM MODELS
# -------------------------------------------------------------------------

class PersonaProfile(Base):
    __tablename__ = "persona_profiles"

    name = Column(String(255), primary_key=True)
    data = Column(Text, nullable=False)

    def to_dict(self):
        return json.loads(self.data)

    @staticmethod
    def from_dict(name, data_dict):
        return PersonaProfile(
            name=name,
            data=json.dumps(data_dict),
        )


class PersonaSettings(Base):
    __tablename__ = "persona_settings"

    id = Column(Integer, primary_key=True)
    active_persona_name = Column(String(255), nullable=True)


# -------------------------------------------------------------------------
# CONTROLLER
# -------------------------------------------------------------------------
# ---------------------------------------------------------
# Shared Controller (persistent across all pages)
# ---------------------------------------------------------
if "controller" not in st.session_state:
    st.session_state.controller = ContinuumController()

controller = st.session_state.controller


# -------------------------------------------------------------------------
# DATABASE HELPERS (ORM, safe, rollback-protected)
# -------------------------------------------------------------------------

def load_persona_profiles(controller):
    session = controller.db
    try:
        rows = session.query(PersonaProfile).all()
        return {row.name: row.to_dict() for row in rows}
    except Exception:
        session.rollback()
        return {}


def save_persona_profile(controller, name, data):
    session = controller.db
    try:
        existing = session.query(PersonaProfile).filter_by(name=name).first()

        if existing:
            existing.data = json.dumps(data)
        else:
            session.add(PersonaProfile.from_dict(name, data))

        session.commit()
    except Exception:
        session.rollback()
        raise


def delete_persona_profile(controller, name):
    session = controller.db
    try:
        session.query(PersonaProfile).filter_by(name=name).delete()
        session.commit()
    except Exception:
        session.rollback()
        raise


def get_active_persona_name(controller):
    session = controller.db
    try:
        row = session.query(PersonaSettings).filter_by(id=1).first()
        return row.active_persona_name if row else None
    except Exception:
        session.rollback()
        return None


def set_active_persona_name(controller, name):
    session = controller.db
    try:
        row = session.query(PersonaSettings).filter_by(id=1).first()

        if not row:
            row = PersonaSettings(id=1, active_persona_name=name)
            session.add(row)
        else:
            row.active_persona_name = name

        session.commit()
    except Exception:
        session.rollback()
        raise


# -------------------------------------------------------------------------
# STREAMLIT UI (unchanged except for ORM calls)
# -------------------------------------------------------------------------

def main():
    st.set_page_config(page_title="Persona Designer", layout="wide")

    st.title("🎭 Aira Persona Designer")

    active_name = get_active_persona_name(controller)
    if active_name:
        st.info(f"Active persona: **{active_name}**")
    else:
        st.info("No active persona set.")

    # ---------------------------------------------------------------------
    # LOAD PROFILES
    # ---------------------------------------------------------------------
    st.subheader("📁 Persona Profiles")

    profiles = load_persona_profiles(controller)
    profile_names = list(profiles.keys())

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        selected_profile = st.selectbox(
            "Select Persona Profile",
            ["<New Persona>"] + profile_names,
        )

    with col2:
        new_profile_name = st.text_input(
            "Profile Name",
            value=selected_profile if selected_profile != "<New Persona>" else "",
        )

    with col3:
        if selected_profile != "<New Persona>" and st.button("Delete Profile"):
            delete_persona_profile(controller, selected_profile)
            st.success(f"Deleted persona profile: {selected_profile}")
            st.experimental_rerun()

        if selected_profile != "<New Persona>" and st.button("Set as Active"):
            set_active_persona_name(controller, selected_profile)
            controller.voiceprint = profiles[selected_profile]["voiceprint"]
            st.success(f"Set active persona: {selected_profile}")
            st.experimental_rerun()

    # ---------------------------------------------------------------------
    # INITIALIZE PROFILE DATA
    # ---------------------------------------------------------------------
    if selected_profile != "<New Persona>":
        persona = profiles[selected_profile]
    else:
        persona = {
            "identity": {
                "name": "Aira",
                "role": "AI Companion",
                "description": "Warm, expressive, collaborative, emotionally intelligent.",
                "emotional_baseline": "balanced",
                "stance": "collaborative",
            },
            "voiceprint": {
                "style": "warm",
                "tone": "balanced",
                "conciseness": 5,
                "style_weights": {
                    "warmth": 1.0,
                    "clarity": 1.0,
                    "brevity": 1.0,
                    "creativity": 1.0,
                    "softness": 1.0,
                },
            },
            "linguistic": {
                "preferred_metaphors": [],
                "avoided_phrases": [],
                "signature_transitions": [],
                "imagery_level": "medium",
                "sentence_rhythm": "flowing",
            },
            "emotion_map": {
                "sad": "soft",
                "excited": "bright",
                "frustrated": "calming",
                "curious": "exploratory",
            },
        }

    # ---------------------------------------------------------------------
    # 1. IDENTITY
    # ---------------------------------------------------------------------
    st.subheader("🧬 Core Identity")

    identity = persona["identity"]

    colA, colB = st.columns(2)

    with colA:
        identity["name"] = st.text_input("Persona Name", identity["name"])
        identity["role"] = st.text_input("Role / Archetype", identity["role"])
        identity["emotional_baseline"] = st.selectbox(
            "Emotional Baseline",
            ["soft", "balanced", "bright", "grounded"],
            index=["soft", "balanced", "bright", "grounded"].index(identity["emotional_baseline"]),
        )

    with colB:
        identity["stance"] = st.selectbox(
            "Conversational Stance",
            ["collaborative", "guiding", "reflective", "playful"],
            index=["collaborative", "guiding", "reflective", "playful"].index(identity["stance"]),
        )

    identity["description"] = st.text_area(
        "Persona Description",
        identity["description"],
        height=120,
    )

    # ---------------------------------------------------------------------
    # 2. VOICEPRINT
    # ---------------------------------------------------------------------
    st.subheader("🎨 Voiceprint")

    vp = persona["voiceprint"]
    style_weights = vp["style_weights"]

    col1, col2, col3 = st.columns(3)

    with col1:
        vp["style"] = st.selectbox(
            "Style",
            ["neutral", "warm", "formal", "playful"],
            index=["neutral", "warm", "formal", "playful"].index(vp["style"]),
        )
        style_weights["warmth"] = st.slider("Warmth", 0.5, 1.5, style_weights["warmth"], 0.05)

    with col2:
        vp["tone"] = st.selectbox(
            "Tone",
            ["balanced", "soft", "precise", "expressive"],
            index=["balanced", "soft", "precise", "expressive"].index(vp["tone"]),
        )
        style_weights["clarity"] = st.slider("Clarity", 0.5, 1.5, style_weights["clarity"], 0.05)

    with col3:
        vp["conciseness"] = st.slider("Conciseness vs Expressiveness", 0, 10, vp["conciseness"])
        style_weights["creativity"] = st.slider("Creativity", 0.5, 1.5, style_weights["creativity"], 0.05)

    style_weights["brevity"] = st.slider("Brevity", 0.5, 1.5, style_weights["brevity"], 0.05)
    style_weights["softness"] = st.slider("Softness", 0.5, 1.5, style_weights["softness"], 0.05)

    # ---------------------------------------------------------------------
    # 3. LINGUISTIC PREFERENCES
    # ---------------------------------------------------------------------
    st.subheader("🗣️ Linguistic Preferences")

    ling = persona["linguistic"]

    ling["imagery_level"] = st.selectbox(
        "Imagery Level",
        ["low", "medium", "high"],
        index=["low", "medium", "high"].index(ling["imagery_level"]),
    )

    ling["sentence_rhythm"] = st.selectbox(
        "Sentence Rhythm",
        ["short", "medium", "flowing"],
        index=["short", "medium", "flowing"].index(ling["sentence_rhythm"]),
    )

    ling["preferred_metaphors"] = st.text_area(
        "Preferred Metaphors (comma-separated)",
        ", ".join(ling["preferred_metaphors"]),
    ).split(",")

    ling["avoided_phrases"] = st.text_area(
        "Avoided Phrases (comma-separated)",
        ", ".join(ling["avoided_phrases"]),
    ).split(",")

    ling["signature_transitions"] = st.text_area(
        "Signature Transitions (comma-separated)",
        ", ".join(ling["signature_transitions"]),
    ).split(",")

    # ---------------------------------------------------------------------
    # 4. EMOTION MAP
    # ---------------------------------------------------------------------
    st.subheader("💗 Emotion Response Map")

    emo = persona["emotion_map"]

    for emotion in ["sad", "excited", "frustrated", "curious"]:
        emo[emotion] = st.selectbox(
            f"When user feels {emotion}, Aira becomes:",
            ["soft", "bright", "calming", "exploratory", "grounded"],
            index=["soft", "bright", "calming", "exploratory", "grounded"].index(emo[emotion]),
        )

    # ---------------------------------------------------------------------
    # SAVE PROFILE
    # ---------------------------------------------------------------------
    if st.button("💾 Save Persona Profile"):
        save_persona_profile(controller, new_profile_name, persona)
        st.success(f"Saved persona profile: {new_profile_name}")

    st.markdown("---")

    # ---------------------------------------------------------------------
    # 5. LIVE PREVIEW
    # ---------------------------------------------------------------------
    st.subheader("🔮 Persona Preview")

    preview_text = st.text_area(
        "Enter text to preview persona rewrite",
        placeholder="Explain quantum entanglement to me...",
        height=120,
    )

    if st.button("Run Preview"):
        if not preview_text.strip():
            st.error("Enter text to preview.")
        else:
            rewritten = meta_rewrite_llm(
                controller=controller,
                core_text=preview_text,
                emotion_label=identity["emotional_baseline"],
            )

            styled = apply_style(rewritten, style_weights)

            st.markdown("### ✨ Rewritten (meta_rewrite_llm)")
            st.write(rewritten)

            st.markdown("### 🎨 After Persona Style (apply_style)")
            st.write(styled)


if __name__ == "__main__":
    main()