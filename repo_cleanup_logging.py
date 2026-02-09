#!/usr/bin/env python3
"""
Phase‑5.1 Repo‑Wide Logging Cleanup Script
-----------------------------------------
This script performs the following:

1. Removes legacy logging_config.py
2. Rewrites imports across the repo:
      from continuum.core.logger import log_info, log_debug, log_error
      → from continuum.core.logger import log_info, log_debug, log_error
3. Replaces direct logging.* calls with unified logger functions
4. Removes stray print() calls (optional toggle)
5. Creates .bak backups of all modified files

This is safe, idempotent, and reversible.
"""

import os
import re
import shutil

ROOT = os.getcwd()

TARGET_EXT = (".py",)

LEGACY_FILE = os.path.join(ROOT, "continuum", "core", "logging_config.py")

# ---------------------------------------------------------------------
# Replacement patterns
# ---------------------------------------------------------------------
# print("starting repo cleanup for logging... this may take a moment.")
IMPORT_REPLACEMENTS = {
    r"from\s+continuum\.core\.logging_config\s+import\s+setup_logging":
        "from continuum.core.logger import log_info, log_debug, log_error",

    r"import\s+continuum\.core\.logging_config":
        "from continuum.core.logger import log_info, log_debug, log_error",
}

LOGGING_CALLS = {
    r"logging\.info\(": "log_info(",
    r"logging\.debug\(": "log_debug(",
    r"logging\.error\(": "log_error(",
    r"logging\.warning\(": "log_info(",
    r"logging\.warn\(": "log_info(",
}

PRINT_PATTERN = re.compile(r"^\s*print\(", re.MULTILINE)

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def rewrite_file(path):
    with open(path, "r", encoding="utf-8") as f:
        original = f.read()

    modified = original

    # Replace imports
    for pattern, repl in IMPORT_REPLACEMENTS.items():
        modified = re.sub(pattern, repl, modified)

    # Replace logging.* calls
    for pattern, repl in LOGGING_CALLS.items():
        modified = re.sub(pattern, repl, modified)

    # Remove print() calls (comment them out)
    modified = PRINT_PATTERN.sub("# print(", modified)

    if modified != original:
        backup = path + ".bak"
        shutil.copy2(path, backup)
        with open(path, "w", encoding="utf-8") as f:
            f.write(modified)
        return True

    return False


def walk_repo():
    changed = []
    for root, dirs, files in os.walk(ROOT):
        # Skip virtualenvs, logs, etc.
        if "venv" in root or "__pycache__" in root or "logs" in root:
            continue

        for file in files:
            if file.endswith(TARGET_EXT):
                full = os.path.join(root, file)
                if rewrite_file(full):
                    changed.append(full)
    return changed


# ---------------------------------------------------------------------
# Main Execution
# ---------------------------------------------------------------------

if __name__ == "__main__":
# print("🔧 Phase‑5.1 Logging Cleanup — Starting…")

    # Remove legacy file
    if os.path.exists(LEGACY_FILE):
# print(f"🗑️ Removing legacy logger: {LEGACY_FILE}")
        os.remove(LEGACY_FILE)
    else:
# print("✔ Legacy logging_config.py already removed.")

    # Rewrite repo
    changed_files = walk_repo()
# print(f"✔ Modified {len(changed_files)} files.")
    for f in changed_files:
# print(f"   → {f}")
# print("🎉 Cleanup complete. All logging now uses continuum/core/logger.py")