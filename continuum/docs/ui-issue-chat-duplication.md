# Continuum UI Issue Log — Chat Panel Duplication & Rerun Behavior
**Status:** Partially Resolved — Deferred for Later Fix  
**Component:** Streamlit Chat Panel (`render_chat`)  
**Impact:** Cosmetic UI duplication / blank chat area  
**Core System Impact:** None

---

## 1. Summary of the Issue
The Continuum’s Streamlit chat interface intermittently displays:

- **Duplicated messages** (each message appears twice), or  
- **No messages at all** (blank chat area)

depending on how rerun logic is handled.

This issue affects **only the chat display layer**.  
All core Continuum systems (Senate, Jury, Memory, Flow Diagram, Actor Reasoning) work correctly.

---

## 2. Root Cause
Streamlit re-runs the entire script **twice** when a chat message is submitted:

1. **Initial render** (before rerun)  
2. **Full rerun** (after rerun)

If the chat panel renders messages during both phases, duplication occurs.  
If the chat panel is skipped incorrectly during rerun, the chat area appears blank.

This behavior is tied to:

- `st.chat_input()` triggering reruns  
- `st.rerun()` forcing additional reruns  
- The order of layout blocks in `streamlit_app.py`

The issue is **not** caused by:

- Duplicate calls to `render_chat`  
- Duplicate layout blocks  
- Duplicate controller logic  
- Incorrect message storage  

The duplication is purely a **Streamlit rerun semantics** issue.

---

## 3. What We Tried

### A. Removing rendering inside the input handler
We removed:

```python
with st.chat_message("user"): ...
with st.chat_message("assistant"): ...