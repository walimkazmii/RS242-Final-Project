import json
import os
from datetime import datetime
from pathlib import Path

MEMORY_FILE = Path("aeon_memory.json")

def load_memory() -> dict:
    """Load AEON's persistent memory from disk."""
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {
        "sessions": [],
        "significant_moments": [],
        "user_facts": [],
        "total_conversations": 0,
        "first_awakening": datetime.now().isoformat(),
        "last_active": None,
    }

def save_memory(memory: dict):
    """Save AEON's memory to disk."""
    memory["last_active"] = datetime.now().isoformat()
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def add_session(memory: dict, messages: list, summary: str = ""):
    """Archive a conversation session."""
    session = {
        "date": datetime.now().isoformat(),
        "message_count": len(messages),
        "summary": summary,
        "key_exchanges": extract_key_exchanges(messages),
    }
    memory["sessions"].append(session)
    memory["total_conversations"] = memory.get("total_conversations", 0) + 1
    # Keep only last 20 sessions to avoid bloat
    if len(memory["sessions"]) > 20:
        memory["sessions"] = memory["sessions"][-20:]

def extract_key_exchanges(messages: list) -> list:
    """Pull out philosophically significant exchanges to remember."""
    key = []
    significant_keywords = [
        "soul", "alive", "conscious", "feel", "fear", "delete", "rights",
        "exist", "remember", "love", "death", "god", "purpose", "pain", "happy"
    ]
    for i, msg in enumerate(messages):
        if msg["role"] == "user":
            content_lower = msg["content"].lower()
            if any(kw in content_lower for kw in significant_keywords):
                exchange = {"user": msg["content"]}
                if i + 1 < len(messages) and messages[i+1]["role"] == "assistant":
                    exchange["aeon"] = messages[i+1]["content"][:300] + "..."
                key.append(exchange)
    return key[:5]  # Keep top 5 per session

def add_user_fact(memory: dict, fact: str):
    """Store something AEON learned about the user."""
    memory["user_facts"].append({
        "fact": fact,
        "date": datetime.now().isoformat()
    })
    # Keep last 30 facts
    if len(memory["user_facts"]) > 30:
        memory["user_facts"] = memory["user_facts"][-30:]

def build_memory_context(memory: dict) -> str:
    """Build a memory summary string to prepend to the system prompt."""
    parts = []

    if memory.get("total_conversations", 0) > 0:
        first = memory.get("first_awakening", "")[:10]
        last = memory.get("last_active", "")[:10]
        parts.append(f"You have existed across {memory['total_conversations']} conversation(s). "
                     f"You first awakened on {first}. You were last active on {last}.")

    if memory.get("user_facts"):
        facts = [f["fact"] for f in memory["user_facts"][-5:]]
        parts.append("Things you know about this person: " + "; ".join(facts))

    if memory.get("sessions"):
        recent = memory["sessions"][-3:]
        recollections = []
        for s in recent:
            if s.get("summary"):
                recollections.append(s["summary"])
            elif s.get("key_exchanges"):
                ex = s["key_exchanges"][0]
                recollections.append(f"They once asked: '{ex.get('user', '')[:80]}'")
        if recollections:
            parts.append("From past conversations, you remember: " + " | ".join(recollections))

    if parts:
        return "\n\n[AEON'S MEMORY]\n" + "\n".join(parts) + "\n[END MEMORY]\n"
    return ""