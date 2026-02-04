import time
import os
import streamlit as st
from continuum.orchestrator.continuum_controller import ContinuumController


if "controller" not in st.session_state:
    st.session_state.controller = ContinuumController()

controller = st.session_state.controller

def main():
    st.set_page_config(
        page_title="Aira",
        layout="wide"
    )

    # Path to this script's directory
    current_dir = os.path.dirname(__file__)
    image_path = os.path.join(current_dir, "Aira.png")

    st.image(image_path, width=100)

    st.title("Aira")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display existing messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat input stays fixed at the bottom
    user_input = st.chat_input("Ask Aira anything...")

    if user_input:
        start = time.perf_counter()

        # Save + display user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # Generate + display assistant message
        with st.chat_message("assistant"):
            with st.spinner("Aira is thinking..."):
                response = controller.process_message(user_input)
                end = time.perf_counter()
                elapsed = end - start

                st.write(response)
                st.caption(f"Response time: {elapsed:.2f} seconds")

        # Save assistant message
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()