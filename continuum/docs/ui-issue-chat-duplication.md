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


Absolutely, George — I can package this cleanly so you can drop it straight into **ui-issue-chat-duplication.md** without touching anything else right now.  
No fixes, no refactors — just a well‑formed issue entry you can paste into the existing file.

Here’s the issue text, ready to insert:

---

## **ISSUE: Preview Voice Button Throws HiFiGAN `NoneType` Error**

### **Summary**  
Using the **Preview Voice (Audio)** button in the Actor Panel triggers a runtime error inside the TTS library (`hifigan_generator.py`). The error originates from the vocoder’s conditioning layer receiving `None` as input (`g = None`), causing `conv1d()` to fail.

### **Observed Error**  
```
TypeError: conv1d() received an invalid combination of arguments - got (NoneType, Parameter, Parameter, ...)
```

### **Context**  
- The main actor audio paths (`actor.speak()` and `speak_proposal`) work correctly.  
- Only the **Preview Voice** button in the UI triggers this failure.  
- This path appears to call `tts_engine.synthesize()` in a way that leads to `g = None` inside the HiFiGAN vocoder.  
- This is a known upstream issue in certain TTS configurations.

### **Impact**  
- Preview Voice is currently non-functional.  
- No impact on live actor audio during Senate or Meta‑Persona responses.  
- No impact on Phase 3 reasoning or UI panels.

### **Status**  
- **Deferred**.  
- Will be addressed after Phase 3 core milestones.  
- Workaround: rely on actor-generated audio (which works) instead of Preview Voice.
