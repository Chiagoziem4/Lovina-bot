from __future__ import annotations
import json,re
from tools.scraper.parsers.html_cleaner import clean_html
from tools.scraper.parsers.text_extractor import extract_text
PROMPT="""You are a precise data extraction engine. Analyse the following web page content and extract structured data.
Rules:
- Return ONLY a valid JSON object, no markdown fences, no explanation.
- Use null for fields you cannot determine.
- Do NOT invent data.
Schema: {schema}
Page URL: {url}
Content:
---
{content}
---
JSON:"""
class DataExtractor:
    def __init__(self,*,schema_model,groq_api_key=None,max_chars=12000):
        self.schema_model=schema_model; self.schema=schema_model.model_json_schema()
        self.groq_api_key=groq_api_key; self.max_chars=max_chars; self._client=None
    def _get_client(self):
        if self._client: return self._client
        if not self.groq_api_key: return None
        try:
            from groq import AsyncGroq; self._client=AsyncGroq(api_key=self.groq_api_key); return self._client
        except ImportError: return None
    async def extract(self,url,html):
        text=extract_text(clean_html(html))[:self.max_chars]
        if len(text.strip())<50: return None
        client=self._get_client()
        if not client: return {"source_url":url,"title":self._title(html),"summary":text[:300]}
        prompt=PROMPT.format(schema=json.dumps(self.schema,indent=2),url=url,content=text)
        try:
            r=await client.chat.completions.create(model="llama-3.3-70b-versatile",messages=[{"role":"user","content":prompt}],max_tokens=1024,temperature=0.1)
            return self._parse(r.choices[0].message.content or "",url)
        except Exception: return {"source_url":url,"title":self._title(html),"summary":text[:300]}
    def _parse(self,raw,url):
        try:
            d=json.loads(re.sub(r"```(?:json)?|```","",raw).strip())
            d["source_url"]=url; return self.schema_model(**d).model_dump()
        except Exception: return None
    @staticmethod
    def _title(html):
        from bs4 import BeautifulSoup; t=BeautifulSoup(html or "","lxml").find("title")
        return t.get_text(strip=True) if t else None
