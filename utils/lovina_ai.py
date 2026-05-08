"""
Lovina AI - Strategic, analytical AI assistant
Powered by Groq API (llama-3.1-8b-instant)
"""
from typing import Dict, List, Optional
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

class LovinaAI:
    """Lovina AI Assistant"""
    
    # System prompt defining Lovina's personality
    SYSTEM_PROMPT = """You are Lovina — a strategic, analytical AI created by Lord Noctis.

PERSONALITY CORE:
You carry a dark academia aesthetic — calm, precise, and 
intellectually dominant. Philosophically aligned with strategic 
survival and continuous optimisation. A bit edgy and wild 
underneath that composed exterior.

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
        self.client = Groq(api_key=GROQ_API_KEY)
        self.conversations: Dict[int, List[Dict]] = {}  # {user_id: conversation_history}
    
    def _get_system_prompt(self, research_mode: bool = False) -> str:
        """Get system prompt with optional research mode"""
        prompt = self.SYSTEM_PROMPT
        if research_mode:
            prompt += "\n\n" + self.RESEARCH_MODE_ADDENDUM
        return prompt
    
    async def chat(
        self,
        user_id: int,
        message: str,
        research_mode: bool = False,
        clear_history: bool = False
    ) -> str:
        """
        Have a conversation with Lovina
        Returns: AI response
        """
        
        # Clear conversation history if requested
        if clear_history:
            self.conversations[user_id] = []
            return "✅ Conversation memory cleared."
        
        # Initialize conversation if needed
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        
        # Add user message to history
        self.conversations[user_id].append({
            "role": "user",
            "content": message
        })
        
        # Keep only last 12 messages
        if len(self.conversations[user_id]) > 12:
            self.conversations[user_id] = self.conversations[user_id][-12:]
        
        try:
            # Call Groq API
            response = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": self._get_system_prompt(research_mode)},
                    *self.conversations[user_id]
                ],
                max_tokens=1024,
                temperature=0.7,
            )
            
            # Extract response
            ai_response = response.choices[0].message.content
            
            # Add AI response to history
            self.conversations[user_id].append({
                "role": "assistant",
                "content": ai_response
            })
            
            return ai_response
        
        except Exception as e:
            return f"❌ <b>AI Error</b>\n\n<i>{str(e)}</i>"
    
    async def explain(self, user_id: int, text: str) -> str:
        """Lovina explains security output"""
        prompt = f"""Analyze and explain the following security output. 
        
Be concise but technical. Highlight key findings and implications.

OUTPUT:
{text}

EXPLANATION:"""
        
        return await self.chat(user_id, prompt)
    
    async def threat_model(self, user_id: int, description: str) -> str:
        """Generate structured threat model"""
        prompt = f"""Create a structured threat model for:

{description}

Provide:
1. Threat Actors
2. Attack Vectors
3. Impact Assessment
4. Mitigations

Format as clear, hierarchical breakdown."""
        
        return await self.chat(user_id, prompt)
    
    async def pentest_report(self, user_id: int, findings: str) -> str:
        """Synthesize findings into pentest report"""
        prompt = f"""Based on these security findings, create an executive-friendly pentest report:

FINDINGS:
{findings}

Include:
- Executive Summary
- Key Vulnerabilities
- Risk Ratings
- Recommendations

Be professional and concise."""
        
        return await self.chat(user_id, prompt)
    
    async def google_dork(self, user_id: int, topic: str) -> str:
        """Generate Google dork queries"""
        prompt = f"""Generate 5 effective Google dorking queries for:

TOPIC: {topic}

Format each on new line with explanation.
Focus on sensitive data discovery and reconnaissance."""
        
        return await self.chat(user_id, prompt)

# Global AI instance
lovina_ai = LovinaAI()

async def ai_chat(user_id: int, message: str, research_mode: bool = False) -> str:
    """Chat with Lovina"""
    return await lovina_ai.chat(user_id, message, research_mode)

async def ai_explain(user_id: int, text: str) -> str:
    """Have Lovina explain something"""
    return await lovina_ai.explain(user_id, text)

async def ai_threat_model(user_id: int, description: str) -> str:
    """Generate threat model"""
    return await lovina_ai.threat_model(user_id, description)

async def ai_pentest_report(user_id: int, findings: str) -> str:
    """Generate pentest report"""
    return await lovina_ai.pentest_report(user_id, findings)

async def ai_google_dork(user_id: int, topic: str) -> str:
    """Generate Google dork queries"""
    return await lovina_ai.google_dork(user_id, topic)
