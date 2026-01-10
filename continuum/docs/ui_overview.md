# The Continuum — UI Overview

This document describes the structure, layout, and responsibilities of the Streamlit UI for The Continuum.  
It serves as a guide for contributors working on the interface, panels, or visualization components.

---

## 1. UI Philosophy

The UI is designed to:
- expose internal reasoning  
- visualize the Senate → Jury pipeline  
- provide debugging tools  
- present actor personalities (J12)  
- maintain a clean, readable layout  
- support rapid iteration during development  

---

## 2. Layout Structure

The UI is divided into two major regions:

### **A. Sidebar (Left Column)**
Contains:
- Continuum Traces  
- Senate Rankings  
- Jury Decision  
- Actor Reasoning  
- Senate Pipeline  
- Flow Diagram  
- Memory Viewer  
- Persona Controls  
- Actor Controls  
- Actor Profiles (J12)  
- Theme & Layout  

Panels are implemented in: continuum/ui/panels/


Each panel is a standalone module for clarity and modularity.

---

### **B. Main Area (Right Column)**
Contains:
- Title & caption  
- Chat interface  
- Chat history  
- User input field  

The chat panel is implemented in: continuum/ui/panels/chat_panel.py


---

## 3. Panel Responsibilities

### **Chat Panel**
- Displays conversation history  
- Accepts user input  
- Triggers Senate → Jury → Meta‑Persona pipeline  
- Updates context  

### **Senate Pipeline Panel**
- Shows raw proposals  
- Shows filtered proposals  
- Shows ranked proposals  
- Displays the winning actor  

### **Actor Reasoning Panel**
- Displays per‑actor reasoning traces  
- Useful for debugging and tuning  

### **Flow Diagram Panel**
- Visualizes the entire pipeline  
- Helps understand system flow at a glance  

### **Memory Viewer Panel**
- Shows stored memories  
- Shows snapshots  
- Supports memory search  

### **Actor Profiles Panel (J12)**
- Displays personality cards  
- Helps users understand each actor’s cognitive style  

---

## 4. Known UI Issues

### **Chat Panel Duplication / Blank Output**
Documented in: /docs/ui_issue_chat_duplication.md

This is a Streamlit rerun behavior issue and will be addressed in a future UI pass.

---

## 5. Future UI Enhancements

- Color‑coded actor proposals  
- Animated flow diagram  
- Actor “spotlight” mode  
- Memory timeline visualization  
- Multi‑tab layout for advanced debugging  

---

**Document Version:** J12  
**Last Updated:** January 2026


