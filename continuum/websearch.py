import json
import requests
from typing import Any, Dict, List, Callable, Optional

OLLAMA_API = "http://localhost:11434/api/chat"

# ============================
# 1) TOOL IMPLEMENTATIONS
# ============================

def web_search(query: str) -> str:
    """
    Replace this with a stronger backend:
    - Bing Web Search API
    - SearXNG instance
    - Custom search microservice
    For now, still using DuckDuckGo as a demo.
    """
    resp = requests.get(
        "https://api.duckduckgo.com/",
        params={"q": query, "format": "json"}
    )
    data = resp.json()
    return data.get("AbstractText", "No results found.")


def echo_text(text: str) -> str:
    """Simple demo tool to show multiple tools wiring."""
    return f"[echo] {text}"


# Map tool names -> Python callables
TOOL_FUNCTIONS: Dict[str, Callable[..., str]] = {
    "web_search": web_search,
    "echo_text": echo_text,
}

# Tool schemas exposed to the model
TOOLS_SCHEMA: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for live information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "echo_text",
            "description": "Echo back the provided text",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                },
                "required": ["text"],
            },
        },
    },
]


# ============================
# 2) STREAM / MODEL HELPERS
# ============================

def read_stream(response):
    for line in response.iter_lines():
        if not line:
            continue
        yield json.loads(line.decode("utf-8"))


def call_model(messages: List[Dict[str, Any]], model: str = "qwen2.5-coder"):
    payload = {
        "model": model,
        "messages": messages,
        "tools": TOOLS_SCHEMA,
        "stream": True,
    }
    resp = requests.post(OLLAMA_API, json=payload, stream=True)
    resp.raise_for_status()
    return read_stream(resp)


# ============================
# 3) ROBUST JSON PARSING
# ============================

def try_parse_json(s: str) -> Optional[Any]:
    """
    Try to parse JSON from a string.
    Be forgiving: trim, try direct, then try to extract the first {...} block.
    """
    s = s.strip()
    if not s:
        return None

    # First attempt: direct parse
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass

    # Second attempt: find first '{' and last '}' and parse that slice
    start = s.find("{")
    end = s.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = s[start : end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            return None

    return None


# ============================
# 4) AGENT CLASS
# ============================

class ToolAgent:
    def __init__(self, model: str = "qwen2.5-coder"):
        self.model = model
        self.messages: List[Dict[str, Any]] = []

    def add_message(self, role: str, content: str, **extra):
        msg: Dict[str, Any] = {"role": role, "content": content}
        msg.update(extra)
        self.messages.append(msg)

    def _collect_stream_content(self) -> List[Dict[str, Any]]:
        """
        Call the model and collect all streamed chunks that contain 'message'.
        Returns a list of message dicts (possibly partial).
        """
        chunks: List[Dict[str, Any]] = []
        for chunk in call_model(self.messages, model=self.model):
            msg = chunk.get("message")
            if msg:
                chunks.append(msg)
        return chunks

    def _extract_tool_call_from_structured(self, msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle models that use proper `tool_calls` field.
        """
        tool_calls = msg.get("tool_calls")
        if not tool_calls:
            return None
        # For simplicity, just take the first tool call
        return tool_calls[0]

    def _extract_tool_call_from_content(self, msgs: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Handle models that emit JSON in `content` instead of `tool_calls`.
        Concatenate content and try to parse as JSON.
        """
        contents = [m.get("content", "") for m in msgs if m.get("content")]
        raw = "".join(contents).strip()
        if not raw:
            return None
        parsed = try_parse_json(raw)
        if isinstance(parsed, dict) and "name" in parsed and "arguments" in parsed:
            return parsed
        return None

    def _execute_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        func = TOOL_FUNCTIONS.get(name)
        if not func:
            return f"[tool error] Unknown tool: {name}"

        try:
            return func(**arguments)
        except TypeError as e:
            return f"[tool error] Bad arguments for {name}: {e}"
        except Exception as e:
            return f"[tool error] Exception in {name}: {e}"

    def run_once(self, user_query: str) -> None:
        # System prompt to strongly encourage tool use
        self.messages = [
            {
                "role": "system",
                "content": (
                    "You are a tool-using assistant. "
                    "When external or up-to-date information is needed, "
                    "you MUST call one of the provided tools instead of guessing."
                ),
            },
            {"role": "user", "content": user_query},
        ]

        # 1) First model call: try to get a tool call
        first_msgs = self._collect_stream_content()

        # Try structured tool_calls first
        tool_call = None
        for m in first_msgs:
            tool_call = self._extract_tool_call_from_structured(m)
            if tool_call:
                break

        # If no structured tool_calls, try JSON in content
        if not tool_call:
            tool_call = self._extract_tool_call_from_content(first_msgs)

        if not tool_call:
            # No tool call at all → just print whatever the model said
            print("\n[MODEL RESPONSE WITHOUT TOOL CALL]\n")
            for m in first_msgs:
                content = m.get("content", "")
                if content:
                    print(content, end="", flush=True)
            print()
            return

        # Normalize tool_call shape
        name = tool_call.get("name")
        arguments = tool_call.get("arguments", {})
        if not isinstance(arguments, dict):
            # Some models return arguments as JSON string
            if isinstance(arguments, str):
                parsed_args = try_parse_json(arguments)
                if isinstance(parsed_args, dict):
                    arguments = parsed_args
                else:
                    arguments = {}
            else:
                arguments = {}

        print("\n[TOOL CALL DETECTED]\n")
        print(json.dumps({"name": name, "arguments": arguments}, indent=2))

        # 2) Execute tool
        result = self._execute_tool(name, arguments)
        print(f"\n[TOOL RESULT FROM {name}]\n")
        print(result)

        # 3) Add tool result back into conversation and get final answer
        #    We also optionally add the raw tool_call as an assistant message for transparency.
        self.messages.append(
            {
                "role": "assistant",
                "content": json.dumps({"name": name, "arguments": arguments}),
            }
        )
        self.messages.append(
            {
                "role": "tool",
                "name": name,
                "content": result,
            }
        )

        print("\n[FINAL MODEL RESPONSE]\n")
        final_msgs = self._collect_stream_content()
        for m in final_msgs:
            content = m.get("content", "")
            if content:
                print(content, end="", flush=True)
        print()


# ============================
# 5) ENTRY POINT
# ============================

if __name__ == "__main__":
    agent = ToolAgent(model="qwen2.5-coder")  # swap to deepseek-r1 / mistral-nemo to experiment
    agent.run_once("give me a parts list to make a 4x4x6 3d printer.")
