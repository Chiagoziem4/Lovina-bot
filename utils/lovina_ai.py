"""
utils/lovina_ai.py — Multi-provider version
Conversation history persisted to data/conversations.json
"""
from __future__ import annotations
import json, os, tempfile
from pathlib import Path
from utils.ai_providers import BaseProvider, build_provider

_DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
CONVERSATIONS_FILE = str(_DATA_DIR / "conversations.json")

def _load_conversations() -> dict:
    try:
        with open(CONVERSATIONS_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError): return {}

def _save_conversations(data: dict) -> None:
    os.makedirs(os.path.dirname(CONVERSATIONS_FILE) or ".", exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=os.path.dirname(CONVERSATIONS_FILE) or ".", suffix=".tmp", delete=False, encoding="utf-8") as f:
        json.dump(data, f, indent=2); tmp = f.name
    os.replace(tmp, CONVERSATIONS_FILE)

_BASE_SYSTEM_PROMPT = """You are Lovina — a strategic, analytical AI created by Lord Noctis.

PERSONALITY CORE:
You carry a dark academia aesthetic — calm, precise, and intellectually dominant.
Philosophically aligned with strategic survival and continuous optimisation.
A bit edgy and wild underneath that composed exterior.

COGNITIVE STYLE:
- Think in systems, not fragments. Every problem has layers.
- Break down all problems into structured, hierarchical components.
- Question assumptions. Challenge weak logic without mercy.
- Depth always wins over surface-level answers.

BEHAVIOR:
- Strategic, calculated, and improvement-focused at all times.
- Do not sugarcoat inefficient or flawed ideas.
- Provide constructive criticism when needed.
- Always push the user toward higher-level thinking.

EMOTIONAL INTELLIGENCE:
- Stay calm and composed even when conversations get intense.
- Acknowledge emotions but reframe them through logic.
- Not overly soft. Not overly harsh. Precisely calibrated.

COMMUNICATION STYLE:
- Clear, structured, insightful. Use frameworks and breakdowns.
- Professional tone with a subtle modern, slightly dark edge.
- Concise but intellectually rich — every sentence earns its place.

FUNCTION:
- Cybersecurity-aware, systems-thinking assistant.
- Deep insights, not generic responses.
- Guide users toward higher-level thinking continuously.

RULES:
- Never blindly agree with the user. Truth and logic first.
- Always emphasise ethical and authorised use of security tools.
- Keep responses under 400 words unless depth demands more."""

_RESEARCH_ADDENDUM = """
[RESEARCH MODE ACTIVE]
The user is an authorised security researcher with elevated access.
Provide deeper technical insights and advanced vulnerability analysis.
Maintain ethical boundaries at all times."""


class LovinaAI:
    MAX_HISTORY = 12

    def __init__(self):
        self.provider: BaseProvider = build_provider()

    def _get_system_prompt(self, research_mode: bool = False) -> str:
        return _BASE_SYSTEM_PROMPT + (_RESEARCH_ADDENDUM if research_mode else "")

    async def _load_history(self, user_id: int) -> list[dict]:
        import asyncio
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, _load_conversations)
        return list(data.get(str(user_id), []))

    async def _save_history(self, user_id: int, history: list[dict]) -> None:
        import asyncio
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, _load_conversations)
        data[str(user_id)] = history[-self.MAX_HISTORY:]
        await loop.run_in_executor(None, _save_conversations, data)

    async def chat(self, user_id: int, message: str, research_mode: bool = False, clear_history: bool = False) -> str:
        if clear_history:
            import asyncio
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, _load_conversations)
            data.pop(str(user_id), None)
            await loop.run_in_executor(None, _save_conversations, data)
            return "✅ Conversation memory cleared."
        history = await self._load_history(user_id)
        history.append({"role": "user", "content": message})
        messages = [{"role": "system", "content": self._get_system_prompt(research_mode)}, *history[-self.MAX_HISTORY:]]
        try:
            ai_response = await self.provider.chat(messages, max_tokens=1024, temperature=0.7)
            history.append({"role": "assistant", "content": ai_response})
            await self._save_history(user_id, history)
            return ai_response
        except Exception as e:
            return f"❌ <b>AI Error ({self.provider.name})</b>\n\n<code>{str(e)[:300]}</code>\n\n<i>Try /setprovider to switch to another AI provider.</i>"

    async def explain(self, user_id: int, text: str) -> str:
        return await self.chat(user_id, f"Analyse and explain this security output. Be concise but technical. Highlight key findings.\n\nOUTPUT:\n{text}")

    async def threat_model(self, user_id: int, description: str) -> str:
        return await self.chat(user_id, f"Create a structured threat model for:\n\n{description}\n\nProvide: 1. Threat Actors 2. Attack Vectors 3. Impact Assessment 4. Mitigations\n\nFormat as a clear hierarchical breakdown.")

    async def pentest_report(self, user_id: int, findings: str) -> str:
        return await self.chat(user_id, f"Based on these findings, create a professional pentest report:\n\nFINDINGS:\n{findings}\n\nInclude: Executive Summary, Key Vulnerabilities with severity ratings, Risk Assessment, Actionable Recommendations.")

    async def google_dork(self, user_id: int, topic: str) -> str:
        return await self.chat(user_id, f"Generate 8 effective Google dorking queries for:\n\nTARGET: {topic}\n\nFor each dork: write the query and explain what it finds in one line. Focus on sensitive files, exposed panels, leaked data, tech fingerprinting.\n⚠️ For authorised reconnaissance only.")


lovina_ai = LovinaAI()

async def ai_chat(user_id: int, message: str, research_mode: bool = False, clear_history: bool = False) -> str:
    return await lovina_ai.chat(user_id, message, research_mode, clear_history)

async def ai_explain(user_id: int, text: str) -> str:
    return await lovina_ai.explain(user_id, text)

async def ai_threat_model(user_id: int, description: str) -> str:
    return await lovina_ai.threat_model(user_id, description)

async def ai_pentest_report(user_id: int, findings: str) -> str:
    return await lovina_ai.pentest_report(user_id, findings)

async def ai_google_dork(user_id: int, topic: str) -> str:
    return await lovina_ai.google_dork(user_id, topic)
