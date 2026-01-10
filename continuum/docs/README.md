# The Continuum — Documentation Index

Welcome to the documentation hub for **The Continuum**, a unified meta‑presence orchestrating multiple internal actors through a Senate–Jury deliberation pipeline.

This index provides quick access to all major documents, specifications, and design notes.

---

## Core Architecture
- **Continuum Architecture Overview**  
  `/docs/continuum_architecture.md`

- **Senate & Jury Pipeline Specification**  
  (future: `/docs/senate_jury_pipeline.md`)

- **Memory System Overview**  
  (future: `/docs/memory_system.md`)

---

## Persona & Actors
- **J12 — Actor Personality Cards**  
  `/docs/actor_personality_cards.md`

- **Meta‑Persona Layer Specification**  
  (future: `/docs/meta_persona.md`)

---

## UI & Interaction
- **UI Overview & Layout Structure**  
  `/docs/ui_overview.md`

- **Chat Panel Issue Log (Streamlit Rerun Behavior)**  
  `/docs/ui_issue_chat_duplication.md`

---

## Development Notes
- **Project Setup & Folder Structure**  
  (future: `/docs/project_structure.md`)

- **Troubleshooting Notes**  
  (future: `/docs/troubleshooting.md`)

---

## Versioning
- **Current Version:** J12  
- **Last Updated:** January 2026

---

When you add new modules or features, update this index to keep the documentation cohesive and discoverable.

# The Continuum — Architecture Overview

The Continuum is a unified meta‑presence composed of multiple internal actors, a Senate–Jury deliberation engine, a meta‑persona layer, and a memory system.  
This document provides a high‑level overview of the architecture and how each subsystem interacts.

---

## 1. High‑Level Flow
User Message ↓ ContinuumContext (messages, memory, profile) ↓ Senate (multiple actors generate proposals) ↓ Filtering & Relevance Scoring ↓ Ranking ↓ Jury (selects the winning proposal) ↓ Meta‑Persona Layer (unifies tone & voice) ↓ Final Assistant Response

---

## 2. Core Components

### **ContinuumContext**
Tracks:
- conversation history  
- memory snapshot  
- user profile  
- debug flags  
- ContinuumMemory instance  

Acts as the shared state container for the entire system.

---

### **Senate (Actor Layer)**
A collection of specialized cognitive actors.  
Each actor:
- receives the user message  
- generates a proposal  
- includes metadata (confidence, domain, persona traits)  
- is scored for relevance  

Actors are defined in: continuum/actors/


Personality cards are defined in: continuum/persona/actor_cards.py

---

### **Jury**
Evaluates ranked proposals and selects the final winner.  
The Jury:
- considers confidence  
- considers relevance  
- may include tie‑breaking logic  
- produces a final decision object  

---

### **Meta‑Persona Layer**
Transforms the winning proposal into a unified, human‑readable response.  
Responsibilities:
- maintain consistent tone  
- integrate dissenting perspectives  
- smooth out actor‑specific quirks  
- produce the final assistant message  

---

### **Memory System**
Stores:
- durable facts  
- contextual snapshots  
- semantic embeddings (future)  

Supports:
- memory search  
- memory retrieval  
- memory‑aware reasoning  

---

## 3. UI Integration

The Streamlit UI exposes:
- chat interface  
- Senate pipeline visualization  
- actor reasoning  
- flow diagram  
- memory viewer  
- persona controls  
- actor profiles (J12)  

Panels live in: continuum/ui/panels/

---

## 4. Design Principles

- **Modularity** — each subsystem is isolated and replaceable  
- **Transparency** — internal reasoning is visible through UI panels  
- **Expressiveness** — actors have distinct cognitive styles  
- **Unification** — meta‑persona ensures a coherent final voice  
- **Extensibility** — new actors, memory types, or UI panels can be added easily  

---

## 5. Future Extensions

- Actor weighting & adaptive relevance  
- Long‑term memory embeddings  
- Multi‑turn actor specialization  
- Tool‑augmented actors  
- Multi‑persona blending  

---

**Document Version:** J12  
**Last Updated:** January 2026
