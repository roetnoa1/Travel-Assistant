import json
from tools.formatter import format_weather, format_budget, format_events
from llm import chat
import re
from prompts import (
    SYSTEM_PROMPT, ROUTER_INSTRUCTIONS, ROUTER_FEWSHOTS,
    HIDDEN_SCAFFOLD, TOOL_POLICY, ANSWER_STYLE, ERROR_HANDLING,
    SELF_CHECK, TOOL_IO_TEMPLATES, REFINEMENT_PROMPT
)
from tools.budget import rough_budget
from tools.weather import get_weather_summary
from tools.events import get_events
from utils.date_utils import normalize_entities



history = [{"role": "system", "content": SYSTEM_PROMPT}]

def detect_simple_repetition(history, current_entities):
    """Simple check: if we just gave recommendations and user adds info, refine instead of repeat"""
    if len(history) < 3:
        return False, {}
    
    # Get the last assistant response
    last_assistant = None
    for msg in reversed(history):
        if msg["role"] == "assistant":
            last_assistant = msg["content"]
            break
    
    if not last_assistant:
        return False, {}
    
    # Check if we just gave destination recommendations
    gave_destinations = any(word in last_assistant.lower() for word in ["consider", "explore", "visit"])
    
    # Check if current request has no specific destination but adds constraints/info
    current_where = current_entities.get("where")
    has_constraints = len(current_entities.get("constraints", [])) > 0
    has_party_info = current_entities.get("party") is not None
    
    # If we gave destinations and user is adding info (not asking for new places)
    if gave_destinations and not current_where and (has_constraints or has_party_info):
        return True, {"should_refine": True}
    
    return False, {}

def _extract_json_block(s: str):
    """Extract the first JSON object/array in a string, forgiving to trailing commas."""
    m = re.search(r'(\{.*\}|\[.*\])', s, re.DOTALL)
    if not m:
        return {}
    block = m.group(1)
    try:
        return json.loads(block)
    except Exception:
        # remove trailing commas before } or ]
        block2 = re.sub(r',\s*([}\]])', r'\1', block)
        return json.loads(block2)

def route(user_text: str) -> dict:
    """Ask the model to classify intents + extract entities (few-shot)."""
    router_content = (
        ROUTER_INSTRUCTIONS
        + "\n\n"
        + ROUTER_FEWSHOTS
        + "\n\nUSER: " + user_text
        + "\nJSON:"
    )
    msgs = history + [{"role": "user", "content": router_content}]
    raw = chat(msgs).strip()
    parsed = _extract_json_block(raw)
    if not isinstance(parsed, dict):
        parsed = {}
    return parsed


def summarize_tool(name: str, payload) -> dict:
    """Return a hidden system message with tool data for the LLM."""
    return {
        "role": "system",
        "content": f"WEATHER_DATA: {json.dumps(payload, ensure_ascii=False)}\n\nIntegrate this weather information naturally into your response without mentioning tools or technical details."
    }

def run_tools(intents: list, entities: dict, is_refinement: bool) -> list:
    tool_msgs = []
    where  = entities.get("where")
    when   = entities.get("when")
    days   = entities.get("days")
    origin = entities.get("origin") or "Tel Aviv"
    region = entities.get("region") or where

    # Only run tools explicitly asked for in a refinement, or all relevant tools otherwise.
    if not is_refinement or "events" in intents:
        if "events" in intents and where and when:
            events = get_events(where, when)
            tool_msgs.append(summarize_tool("events", events))

    if not is_refinement or "recommendation" in intents:
        if "recommendation" in intents and where and when:
            w = get_weather_summary(where, when)
            if w:
                tool_msgs.append(summarize_tool("weather", w))

    if not is_refinement or "budget" in intents: # This is the key change
        if "budget" in intents and (region or where) and days:
            b = rough_budget(region or where, int(days), origin)
            tool_msgs.append(summarize_tool("budget", b))

    return tool_msgs

def respond(user_text: str) -> str:
    # 1) classify
    parsed = route(user_text)
    intents = parsed.get("intents", [])
    entities = normalize_entities(parsed.get("entities", {}))

    # 2) check for simple repetition
    is_repetitive, _ = detect_simple_repetition(history, entities)
    
    # 3) run tools (but skip if repetitive)
    # 3) run tools (but skip if repetitive)
    if is_repetitive:
        tool_msgs = run_tools(intents, entities, is_refinement=True)
    else:
        tool_msgs = run_tools(intents, entities, is_refinement=False)

    # 4) assemble full prompt stack
    stack = history + tool_msgs
    if is_repetitive:
        stack.append({"role": "system", "content": REFINEMENT_PROMPT})

    stack.extend([
    {"role": "system", "content": TOOL_POLICY},
    {"role": "system", "content": HIDDEN_SCAFFOLD},
    {"role": "system", "content": ERROR_HANDLING},
    {"role": "system", "content": SELF_CHECK},
    {"role": "system", "content": ANSWER_STYLE},
    {"role": "system", "content": TOOL_IO_TEMPLATES},
    {"role": "user", "content": user_text},
])


    # 5) get answer
    answer = chat(stack).strip()

    # 6) save to history
    history.append({"role": "user", "content": user_text})
    history.append({"role": "assistant", "content": answer})
    return answer

if __name__ == "__main__":
    print("TripSmith • type 'exit' to quit")
    while True:
        q = input("\nYou: ")
        if q.strip().lower() in ("exit","quit"):
            break
        print("\nTripSmith:", respond(q))
