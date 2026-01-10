import streamlit as st

def render_tools(controller):
    st.header("Tool Logs")

    if controller.tool_logs:
        for entry in reversed(controller.tool_logs[-20:]):
            with st.expander(f"{entry['tool']} — {entry['timestamp']:.0f}"):
                st.write("**Parameters:**", entry["params"])
                st.write("**Result:**", entry["result"])
                if entry["error"]:
                    st.error(f"Error: {entry['error']}")
                st.caption(f"Duration: {entry['duration']:.3f}s")
    else:
        st.write("No tool calls yet.")