from __future__ import annotations

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class LLMService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY missing in .env")

        self.client = Groq(api_key=api_key)

    def extract_api_structure(self, text: str) -> str:
        prompt = f"""
Extract API structure from documentation.

Return ONLY VALID JSON.

DO NOT:
- Explain anything
- Add extra text
- Use markdown
- Include wildcard endpoints like "/agent/*"

FORMAT:
{{
  "base_url": "",
  "auth": "",
  "endpoints": [
    {{
      "path": "",
      "method": "",
      "description": "",
      "params": []
    }}
  ]
}}

Documentation:
{text[:5000]}
"""

        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

        content = response.choices[0].message.content

        # 🔥 CLEAN OUTPUT
        content = content.replace("```json", "").replace("```", "").strip()

        return content