# continuum/ts_bridge/selector_client.py

import json
import subprocess
from pathlib import Path

TS_SELECTOR_SCRIPT = (
    Path(__file__).parent
    / ".."
    / "ts"
    / "dist"
    / "selector"
    / "hybridSelector.cjs"
).resolve()

def select_model(actor: str, role: str, default_model: str, tags=None, complexity=None):
    payload = json.dumps({
        "actor": actor,
        "role": role,
        "default_model": default_model,
        "tags": tags or [],
        "complexity": complexity or "medium"
    })

    script_path = str(TS_SELECTOR_SCRIPT).replace("/", "\\")
    cmd = ["node", script_path]

    print("RUNNING:", cmd)

    result = subprocess.run(
        cmd,
        input=payload,          # <-- send JSON to stdin
        text=True,
        capture_output=True,
        check=False
    )

    if result.returncode != 0:
        print(
            "Selector error: process failed",
            {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            },
        )
        return default_model

    if not result.stdout.strip():
        print("Selector error: empty stdout", {"stderr": result.stderr})
        return default_model

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(
            "Selector error: invalid JSON",
            {"error": str(e), "stdout": result.stdout, "stderr": result.stderr},
        )
        return default_model

    return data.get("model", default_model)