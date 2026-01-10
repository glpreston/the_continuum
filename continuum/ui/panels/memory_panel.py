import streamlit as st

def render_memory(controller):
    st.header("Memory Viewer")

    memory = controller.context.memory

    # Show all stored memories
    st.subheader("Stored Memories")
    if memory._store:
        for key, record in memory._store.items():
            with st.expander(f"{key}"):
                st.write("**Value:**", record.value)
                if record.metadata:
                    st.write("**Metadata:**", record.metadata)
    else:
        st.write("No memories stored yet.")

    st.divider()

    # Memory snapshot
    st.subheader("Snapshot")
    snapshot = memory.snapshot()
    if snapshot:
        st.json(snapshot)
    else:
        st.write("Snapshot is empty.")

    st.divider()

    # Memory search
    st.subheader("Search Memory")
    query = st.text_input("Search for…", key="memory_search_sidebar")
    if query:
        results = memory.search(query)
        if results:
            for r in results:
                with st.expander(f"Match: {r.key}"):
                    st.write("**Value:**", r.value)
                    if r.metadata:
                        st.write("**Metadata:**", r.metadata)
        else:
            st.write("No matches found.")