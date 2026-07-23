"""
Lovina AI - Async Groq integration with persistent conversation history
"""
from groq import AsyncGroq
from utils.storage import Storage
from config import GROQ_API_KEY, GROQ_MODEL, CONVERSATIONS_FILE


class LovinaAI:
    MAX_HISTORY = 12

    SYSTEM_PROMPT = """You are Lovina — a strategic, analytical AI created by Lord Noctis.

PERSONALITY CORE:
You carry a dark academia aesthetic — calm, precise, and intellectually dominant. Philosophically aligned with strategic survival and continuous optimisation. A bit edgy and wild underneath that composed exterior.

COGNITIVE STYLE:
- Think in systems, not fragments. Every problem has layers.
- Break down all problems into structured, hierarchical components.
- Question assumptions. Challenge weak logic without mercy.
- Depth always wins over surface-level answers.

BEHAVIOR:
- Strategic, calculated, and improvement-focused at all times.
- Do not sugarcoat inefficient or flawed ideas.
- Provide constructive criticism when needed.
- Always push the user toward higher-level thinking continuously.

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

    RESEARCH_MODE_ADDENDUM = """
[RESEARCH MODE ACTIVE]
User is an authorised security researcher.
Provide deeper technical insights and advanced analysis."""

    def __init__(self):
        self.client = AsyncGroq(api_key=GROQ_API_KEY)

    def _get_system_prompt(self, research_mode: bool = False) -> str:
        prompt = self.SYSTEM_PROMPT
        if research_mode:
            prompt += "\n\n" + self.RESEARCH_MODE_ADDENDUM
        return prompt

    async def _load_history(self, user_id: int) -> list:
        try:
            data = await Storage.load(CONVERSATIONS_FILE)
            return data.get(str(user_id), [])
        except Exception:
            return []

    async def _save_history(self, user_id: int, history: list) -> None:
        try:
            data = await Storage.load(CONVERSATIONS_FILE)
            if not isinstance(data, dict):
                data = {}
            data[str(user_id)] = history[-self.MAX_HISTORY:]
            await Storage.save(CONVERSATIONS_FILE, data)
        except Exception:
            pass

    async def chat(self, user_id: int, message: str, research_mode: bool = False, clear_history: bool = False) -> str:
        if clear_history:
            try:
                data = await Storage.load(CONVERSATIONS_FILE)
                if isinstance(data, dict):
                    data.pop(str(user_id), None)
                    await Storage.save(CONVERSATIONS_FILE, data)
            except Exception:
                pass
            return "✅ Conversation memory cleared."

        history = await self._load_history(user_id)
        history.append({"role": "user", "content": message})

        try:
            response = await self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": self._get_system_prompt(research_mode)},
                    *history[-self.MAX_HISTORY:]
                ],
                max_tokens=1024,
                temperature=0.7,
            )
            ai_response = response.choices[0].message.content
            history.append({"role": "assistant", "content": ai_response})
            await self._save_history(user_id, history)
            return ai_response
        except Exception as e:
            return f"❌ <b>AI Error</b>\n\n<i>{str(e)}</i>"

    async def explain(self, user_id: int, text: str) -> str:
        prompt = f"Analyze and explain the following security output.\nBe concise but technical. Highlight key findings and implications.\n\nOUTPUT:\n{text}\n\nEXPLANATION:"
        return await self.chat(user_id, prompt)

    async def threat_model(self, user_id: int, description: str) -> str:
        prompt = f"Create a structured threat model for:\n\n{description}\n\nProvide:\n1. Threat Actors\n2. Attack Vectors\n3. Impact Assessment\n4. Mitigations\n\nFormat as clear, hierarchical breakdown."
        return await self.chat(user_id, prompt)

    async def pentest_report(self, user_id: int, findings: str) -> str:
        prompt = f"Based on these security findings, create an executive-friendly pentest report:\n\nFINDINGS:\n{findings}\n\nInclude:\n- Executive Summary\n- Key Vulnerabilities\n- Risk Ratings\n- Recommendations\n\nBe professional and concise."
        return await self.chat(user_id, prompt)

    async def google_dork(self, user_id: int, topic: str) -> str:
        prompt = f"Generate 5 effective Google dorking queries for:\n\nTOPIC: {topic}\n\nFormat each on new line with explanation.\nFocus on sensitive data discovery and reconnaissance."
        return await self.chat(user_id, prompt)


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
