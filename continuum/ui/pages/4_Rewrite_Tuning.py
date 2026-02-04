# continuum/ui/pages/4_Rewrite_Tuning.py

import streamlit as st
import pandas as pd

from sqlalchemy import text

from continuum.orchestrator.continuum_controller import ContinuumController
from continuum.aira.meta_rewrite import meta_rewrite_llm
from continuum.persona.style_rewrite import apply_style



#@st.cache_resource
#def get_controller():
#    return ContinuumController()

if "controller" not in st.session_state:
    st.session_state.controller = ContinuumController()

controller = st.session_state.controller


def run_rewrite(controller, text_input: str, depth: int, emotion_label: str):
    """
    Run the real meta_rewrite_llm in a loop to simulate multi-depth rewriting.
    Returns a list of (depth, base_output, styled_output_or_None).
    """
    outputs = []
    current = text_input

    for d in range(depth):
        rewritten = meta_rewrite_llm(
            controller=controller,
            core_text=current,
            emotion_label=emotion_label or "neutral",
        )
        outputs.append((d + 1, current, rewritten))
        current = rewritten

    return outputs


#def main():
#    st.set_page_config(page_title="Rewrite Tuning", layout="wide")
#    controller = get_controller()

def main():
    st.set_page_config(page_title="Cognitive Trace", layout="wide")

    # Use the shared controller from session_state
    #if "controller" not in st.session_state:
    #    st.session_state.controller = ContinuumController()

    #controller = st.session_state.controller

    st.title("🌀 Aira Rewrite Lab — Model, Persona, Depth, Style")

    # -------------------------------------------------------------------------
    # 1. REWRITE MODEL SELECTION (LOGICAL ONLY)
    # -------------------------------------------------------------------------
    st.subheader("🔧 Rewrite Model Selection")

    # registry.models is a list of ORM rows with .name
    available_models = [getattr(m, "name") for m in controller.registry.models]

    col1, col2 = st.columns([2, 1])

    with col1:
        selected_model = st.selectbox(
            "Preferred Rewrite Model (logical preference)",
            available_models,
            index=available_models.index(getattr(controller, "rewrite_model", available_models[0]))
            if getattr(controller, "rewrite_model", None) in available_models
            else 0,
        )

    with col2:
        custom_model = st.text_input(
            "Custom Model Name (optional)",
            value=getattr(controller, "rewrite_model", selected_model),
        )

    if st.button("Save Preferred Rewrite Model"):
        new_value = custom_model if custom_model else selected_model
        try:
            # This is a logical preference; meta_rewrite_llm still uses routing,
            # but we persist this for future use / display.
            controller.rewrite_model = new_value
            try:
                controller.db.execute(
                    text("UPDATE rewrite_config SET pinned_model = :m"),
                    {"m": new_value},
                )
                controller.db.commit()
            except Exception:
                # If rewrite_config table doesn't exist, we just keep it in memory.
                pass
            st.success(f"Preferred rewrite model set to {new_value}")
        except Exception as e:
            st.error(f"Failed: {e}")

    st.markdown("---")

    # -------------------------------------------------------------------------
    # 2. REWRITE PARAMETERS (TEMPERATURE + DEPTH)
    # -------------------------------------------------------------------------
    st.subheader("🌡️ Rewrite Parameters")

    colA, colB = st.columns(2)

    with colA:
        new_temp = st.slider(
            "Base Temperature (used by meta_rewrite_llm)",
            0.0, 2.0,
            getattr(controller, "temperature", 0.7),
            0.05,
        )

    with colB:
        new_depth = st.slider(
            "Max Rewrite Depth (used by meta_rewrite_llm)",
            1, 10,
            getattr(controller, "max_rewrite_depth", 3),
        )

    if st.button("Save Rewrite Parameters"):
        controller.temperature = new_temp
        controller.max_rewrite_depth = new_depth
        st.success("Rewrite parameters updated (controller.temperature, controller.max_rewrite_depth).")

    st.markdown("---")

    # -------------------------------------------------------------------------
    # 3. PERSONA STYLE CONTROLS (FOR apply_style)
    # -------------------------------------------------------------------------
    st.subheader("🎨 Persona Style Controls (Post-Processing)")

    # We’ll store persona style in controller.voiceprint["style_weights"]
    vp = getattr(controller, "voiceprint", {})
    style_weights = vp.get("style_weights", {
        "warmth": 1.0,
        "clarity": 1.0,
        "brevity": 1.0,
        "creativity": 1.0,
        "softness": 1.0,
    })

    col1, col2, col3 = st.columns(3)

    with col1:
        warmth = st.slider("Warmth", 0.5, 1.5, float(style_weights.get("warmth", 1.0)), 0.05)
        clarity = st.slider("Clarity", 0.5, 1.5, float(style_weights.get("clarity", 1.0)), 0.05)

    with col2:
        brevity = st.slider("Brevity", 0.5, 1.5, float(style_weights.get("brevity", 1.0)), 0.05)
        creativity = st.slider("Creativity", 0.5, 1.5, float(style_weights.get("creativity", 1.0)), 0.05)

    with col3:
        softness = st.slider("Softness", 0.5, 1.5, float(style_weights.get("softness", 1.0)), 0.05)
        emotion_label = st.selectbox(
            "Emotion Label (for meta_rewrite_llm)",
            ["neutral", "soft", "excited", "serious"],
            index=0,
        )

    if st.button("Save Persona Style"):
        style_weights = {
            "warmth": warmth,
            "clarity": clarity,
            "brevity": brevity,
            "creativity": creativity,
            "softness": softness,
        }
        vp["style_weights"] = style_weights
        controller.voiceprint = vp
        st.success("Persona style weights updated (controller.voiceprint['style_weights']).")

    st.markdown("---")

    # -------------------------------------------------------------------------
    # 4. REWRITE TEST BENCH (WITH OPTIONAL PERSONA STYLE PASS)
    # -------------------------------------------------------------------------
    st.subheader("🧪 Rewrite Test Bench")

    test_input = st.text_area(
        "Input Text",
        placeholder="Paste text here to test the rewrite pipeline...",
        height=150,
    )

    test_depth = st.slider(
        "Test Depth",
        1, getattr(controller, "max_rewrite_depth", 3),
        getattr(controller, "max_rewrite_depth", 3),
    )

    apply_persona_style = st.checkbox(
        "Apply Persona Style Pass (apply_style) to each depth output",
        value=True,
    )

    if st.button("Run Rewrite Test"):
        if not test_input.strip():
            st.error("Please enter text to rewrite.")
        else:
            results = run_rewrite(controller, test_input, test_depth, emotion_label)

            for depth, base_input, base_output in results:
                with st.expander(f"Depth {depth} Output"):
                    st.markdown("**Rewritten Text (meta_rewrite_llm):**")
                    st.write(base_output)

                    if apply_persona_style:
                        styled = apply_style(base_output, style_weights)
                        st.markdown("**After Persona Style (apply_style):**")
                        st.write(styled)

    st.markdown("---")

    # -------------------------------------------------------------------------
    # 5. REWRITE TRACE INSPECTOR (IF YOU LOG IT)
    # -------------------------------------------------------------------------
    st.subheader("🔍 Rewrite Trace Inspector (Last Turn)")

    if len(getattr(controller, "turn_logger", [])) == 0:
        st.info("No turns logged yet.")
    else:
        last_turn = controller.turn_logger[-1]
        trace = last_turn.get("rewrite_trace", {})

        if not trace:
            st.info("No rewrite trace recorded for the last turn.")
        else:
            # trace is expected to be a dict keyed by depth
            for depth, entry in trace.items():
                with st.expander(f"Depth {depth}"):
                    st.markdown("**Input:**")
                    st.write(entry.get("input", ""))

                    st.markdown("**Output:**")
                    st.write(entry.get("output", ""))

                    if "notes" in entry:
                        st.markdown("**Notes:**")
                        st.write(entry["notes"])


if __name__ == "__main__":
    main()