#!/usr/bin/env python3
"""
Repo‑Wide Legacy Persona/Rewrite Detector
-----------------------------------------
This script scans the entire repo for:

- legacy rewrite pipeline references
- deprecated persona fields
- old emotional modulation flags
- meta‑rewrite toggles
- Phase‑3/4 rewrite modules
- unused persona attributes
- any reference to enable_meta_llm or meta_rewrite_llm

It does NOT modify anything. It only reports findings.
"""

import os
import re

ROOT = os.getcwd()
TARGET_EXT = (".py", ".json", ".txt")

# ---------------------------------------------------------------------
# Patterns to search for
# ---------------------------------------------------------------------

PATTERNS = {
    "legacy_rewrite_hook": r"legacy_rewrite|rewrite_v2|rewrite_v1|old_rewrite",
    "meta_llm_toggle": r"enable_meta_llm|meta_rewrite_llm",
    "deprecated_persona_fields": r"(tone_prefix|style_prefix|emotion_map|persona_v1|persona_v2)",
    "old_emotion_engine": r"(emotion_v1|emotion_legacy|old_emotion_engine)",
    "old_style_rewrite": r"(style_rewrite|rewrite_style|persona_style_hook)",
    "phase3_rewrite": r"(rewrite_phase3|phase3_rewrite|rewrite_legacy)",
    "unused_persona_attrs": r"(persona_attributes|persona_config_old|persona_settings_v1)",
}

# ---------------------------------------------------------------------
# Search function
# ---------------------------------------------------------------------

def scan_file(path):
    results = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    for label, pattern in PATTERNS.items():
        if re.search(pattern, content):
            results.append(label)

    return results


def walk_repo():
    findings = {}
    for root, dirs, files in os.walk(ROOT):
        if "venv" in root or "__pycache__" in root or "logs" in root:
            continue

        for file in files:
            if file.endswith(TARGET_EXT):
                full = os.path.join(root, file)
                matches = scan_file(full)
                if matches:
                    findings[full] = matches
    return findings


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

if __name__ == "__main__":
    print("🔍 Scanning repo for legacy persona/rewrite references...\n")

    findings = walk_repo()

    if not findings:
        print("✔ No legacy references found. Repo is clean.")
    else:
        print("⚠ Legacy references detected:\n")
        for path, labels in findings.items():
            print(f"→ {path}")
            for label in labels:
                print(f"   - {label}")
            print()

    print("\nScan complete.")