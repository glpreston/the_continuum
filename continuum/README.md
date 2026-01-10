# The Continuum

**The Continuum** is a modular, multi‑actor orchestration system designed to blend
structured reasoning, expressive personas, and extensible tooling into a single,
coherent AI presence.

It is built around three core ideas:

1. **Multiple internal actors** (the Senate) generate diverse proposals.
2. **A Jury** evaluates those proposals and selects the strongest one.
3. **A unified meta‑persona** shapes the final response into a consistent voice.

The result is a system that feels deliberate, expressive, and architecturally clean.

---

## ✨ Features

- **Multi‑actor deliberation** (Senate + Jury model)
- **Unified persona layer** for consistent tone and style
- **Modular architecture** with clear boundaries:
  - `core/` – message types, context, routing
  - `actors/` – base actors, specialist actors, persona blending
  - `orchestrator/` – Senate, Jury, Controller
  - `memory/` – episodic, semantic, working memory
  - `tools/` – tool interface + registry
  - `cli/` – interactive command‑line runner
- **Future‑ready** for MySQL‑backed memory and tool integrations
- **Lightweight dependencies** and modern packaging (`pyproject.toml`)

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/glpreston/the_continuum.git
cd the_continuum