"""
Voice processing service: transcribe audio and extract structured data.
Uses Groq for Whisper transcription and AI for parsing.
"""
from typing import Optional, Dict, Any, Literal
import io
from app.config import settings

# Lazy imports
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    Groq = None

from app.services.ai_service import AIService


class VoiceService:
    """Process voice recordings: transcribe + parse into Entry or Goal."""

    def __init__(self):
        self.groq_key = getattr(settings, 'groq_api_key', None) or getattr(settings, 'ai_api_key', None)
        self.ai_service = AIService()

    async def process_voice(
        self,
        audio_bytes: bytes,
        filename: str = "voice.ogg"
    ) -> Dict[str, Any]:
        """
        Process voice recording:
        1. Transcribe with Groq Whisper
        2. Parse with AI to determine Entry vs Goal
        3. Return structured data
        """
        # Step 1: Transcribe
        transcript = await self._transcribe(audio_bytes, filename)
        if not transcript:
            return {"error": "Failed to transcribe audio", "type": "unknown"}

        # Step 2: Parse with AI
        parsed = await self._parse_transcript(transcript)
        parsed["transcript"] = transcript
        parsed["original_text"] = transcript  # For compatibility

        return parsed

    async def _transcribe(self, audio_bytes: bytes, filename: str) -> Optional[str]:
        """Transcribe audio using Groq Whisper."""
        if not GROQ_AVAILABLE or not self.groq_key:
            print("Groq not available, returning empty transcript")
            return None

        try:
            client = Groq(api_key=self.groq_key)

            # Create file-like object from bytes
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = filename

            response = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3-turbo",
                language="ru",
                response_format="text"
            )

            # Response is string when response_format="text"
            return response.strip() if response else None

        except Exception as e:
            print(f"Transcription error: {e}")
            return None

    async def _parse_transcript(self, transcript: str) -> Dict[str, Any]:
        """
        Parse transcript with AI to determine Entry vs Goal and extract fields.
        """
        if not self.ai_service.api_key:
            # Fallback: treat as simple entry text
            return {
                "type": "entry",
                "data": {
                    "entry_type": "pulse",
                    "raw_text": transcript,
                },
                "parsed": False
            }

        try:
            # Use AI to classify and extract
            result = await self._ai_parse(transcript)
            return result
        except Exception as e:
            print(f"AI parsing error: {e}")
            # Fallback
            return {
                "type": "entry",
                "data": {
                    "entry_type": "pulse",
                    "raw_text": transcript,
                },
                "parsed": False,
                "error": str(e)
            }

    async def _ai_parse(self, transcript: str) -> Dict[str, Any]:
        """Use AI to parse transcript into structured Entry or Goal."""
        prompt = f"""Проанализируй голосовую запись пользователя. Определи, это:
A) Ежедневный отчет о состоянии (Entry) — содержит оценки настроения, энергии, описания тела, инсайты
B) Цель (Goal) — содержит намерения, планы, желаемый результат на месяц/год

Запись: "{transcript}"

Верни ТОЛЬКО JSON без markdown:
{{
  "type": "entry" | "goal",
  "confidence": 0.0-1.0,
  "data": {{}}
}}

Для type="entry" заполни:
{{
  "entry_type": "pulse",
  "mood": null | число 1-10,
  "energy": null | число 1-10,
  "anxiety": null | число 1-10,
  "body_state": "описание того, что в теле или пусто",
  "insight": "главный инсайт или пусто",
  "gratitude": "за что благодарен или пусто",
  "today_moment": "момент осознанности сегодня или пусто",
  "tomorrow_commitment": "одно обязательство на завтра или пусто",
  "raw_text": "полный текст записи"
}}

Для type="goal" заполни:
{{
  "horizon": "month" | "quarter" | "year" | "dream_life",
  "title": "краткое название цели",
  "description": "описание цели",
  "status": "active"
}}

Если не уверен, используй type="entry" с raw_text."""

        # Use AI service to generate
        if self.ai_service.provider == "anthropic":
            result = await self._call_claude_parse(prompt)
        else:
            result = await self._call_openai_parse(prompt)

        # Parse JSON from result
        import json
        try:
            # Clean up markdown if present
            text = result.strip()
            if text.startswith("```"):
                # Extract from markdown code block
                lines = text.split("\n")
                json_lines = []
                in_json = False
                for line in lines:
                    if line.startswith("```json") or line.startswith("```"):
                        in_json = not in_json
                        continue
                    if in_json or (not line.startswith("```") and json_lines):
                        json_lines.append(line)
                text = "\n".join(json_lines).strip()
                if text.endswith("```"):
                    text = text[:-3].strip()

            parsed = json.loads(text)
            return parsed
        except json.JSONDecodeError as e:
            print(f"Failed to parse AI response as JSON: {e}")
            print(f"Response was: {result}")
            # Return as raw entry
            return {
                "type": "entry",
                "confidence": 0.5,
                "data": {
                    "entry_type": "pulse",
                    "raw_text": transcript,
                },
                "parsed": False
            }

    async def _call_openai_parse(self, prompt: str) -> str:
        """Call OpenAI for parsing."""
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.ai_service.api_key)
            response = await client.chat.completions.create(
                model=self.ai_service.model or "gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Ты анализируешь голосовые записи пользователя. Отвечай только JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            print(f"OpenAI parse error: {e}")
            raise

    async def _call_claude_parse(self, prompt: str) -> str:
        """Call Claude for parsing."""
        try:
            from anthropic import AsyncAnthropic
            client = AsyncAnthropic(api_key=self.ai_service.api_key)
            model = self.ai_service.model or "claude-3-haiku-20240307"
            if model.startswith("gpt-"):
                model = "claude-3-haiku-20240307"

            response = await client.messages.create(
                model=model,
                max_tokens=500,
                temperature=0.3,
                system="Ты анализируешь голосовые записи пользователя. Отвечай только JSON.",
                messages=[{"role": "user", "content": prompt}]
            )

            text_parts = []
            for block in response.content:
                if hasattr(block, 'text'):
                    text_parts.append(block.text)
            return "\n".join(text_parts)
        except Exception as e:
            print(f"Claude parse error: {e}")
            raise
