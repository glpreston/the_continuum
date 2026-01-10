import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

def render_similarity(controller):
    st.header("Actor Similarity Heatmap")

    sim = controller.context.debug_flags.get("similarity_matrix")

    if not sim:
        st.write("No similarity data yet.")
        return

    actors = sim.get("actors", [])
    matrix = np.array(sim.get("matrix", []))

    if matrix.size == 0:
        st.write("Similarity matrix is empty.")
        return

    # Create heatmap figure
    fig, ax = plt.subplots(figsize=(6, 4))

    sns.heatmap(
        matrix,
        xticklabels=actors,
        yticklabels=actors,
        cmap="viridis",
        annot=True,
        fmt=".2f",
        linewidths=0.5,
        ax=ax,
    )

    ax.set_title("Actor Proposal Similarity (Cosine TF‑IDF)")

    st.pyplot(fig)