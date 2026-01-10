import streamlit as st

def render_theme_controls(controller):
    st.header("Theme & Layout")

    # Theme mode
    mode = st.selectbox(
        "Theme Mode",
        ["Light", "Dark", "Continuum"],
        index=["Light", "Dark", "Continuum"].index(controller.theme_settings["mode"]),
    )
    controller.theme_settings["mode"] = mode

    # Accent color
    accent = st.selectbox(
        "Accent Color",
        ["blue", "green", "purple", "orange", "pink"],
        index=["blue", "green", "purple", "orange", "pink"].index(
            controller.theme_settings["accent_color"]
        ),
    )
    controller.theme_settings["accent_color"] = accent

    # Font size
    font = st.selectbox(
        "Font Size",
        ["small", "medium", "large"],
        index=["small", "medium", "large"].index(controller.theme_settings["font_size"]),
    )
    controller.theme_settings["font_size"] = font

    # Layout density
    density = st.selectbox(
        "Layout Density",
        ["compact", "comfortable", "spacious"],
        index=["compact", "comfortable", "spacious"].index(
            controller.theme_settings["density"]
        ),
    )
    controller.theme_settings["density"] = density