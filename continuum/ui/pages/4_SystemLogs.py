import streamlit as st

def main():
    st.set_page_config(page_title="System Logs", layout="wide")

    st.title("System Logs")

    st.subheader("Recent Logs")
    st.write("Tail of log file or log viewer goes here.")

if __name__ == "__main__":
    main()