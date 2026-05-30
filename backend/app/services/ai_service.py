"""
AI Service for entry and goal analysis.
Supports OpenAI and Anthropic Claude.
Auto-detects provider by API key prefix:
  - OpenAI: sk-... (not starting with sk-ant-)
  - Anthropic: sk-ant-...
Falls back to placeholder if no key configured.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
from app.models import Entry, Goal
from app.config import settings

# Lazy imports to avoid errors if packages not installed
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncOpenAI = None

try:
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    AsyncAnthropic = None


class AIService:
    def __init__(self):
        self.api_key = settings.ai_api_key
        self.model = settings.ai_model or "gpt-4"
        self.provider = self._detect_provider()

    def _detect_provider(self) -> str:
        """Auto-detect AI provider from API key prefix."""
        if not self.api_key:
            return "none"
        # Anthropic keys start with sk-ant-
        if self.api_key.startswith("sk-ant-"):
            return "anthropic"
        # OpenAI keys start with sk- (and not sk-ant-)
        if self.api_key.startswith("sk-"):
            return "openai"
        return "unknown"

    async def analyze_entry(self, entry: Entry) -> str:
        """Generate gentle analysis of a daily entry."""
        if not self.api_key:
            return self._placeholder_entry_analysis(entry)

        # Real implementation would call OpenAI/Anthropic/etc
        # Placeholder for now
        return self._placeholder_entry_analysis(entry)

    def _placeholder_entry_analysis(self, entry: Entry) -> str:
        """Placeholder analysis when no AI key configured."""
        lines = []
        
        if entry.mood:
            if entry.mood >= 7:
                lines.append("Настроение на хорошем уровне.")
            elif entry.mood >= 4:
                lines.append("Настроение в средней зоне — это нормально.")
            else:
                lines.append("Настроение ниже обычного — обрати на это внимание с любопытством.")

        if entry.energy:
            if entry.energy >= 7:
                lines.append("Энергия позволяет двигаться к целям.")
            elif entry.energy <= 3:
                lines.append("Энергия ниже — может быть, стоит замедлиться сегодня?")

        if entry.anxiety and entry.anxiety >= 6:
            lines.append("Тревога присутствует — что если просто наблюдать за ней без оценки?")

        lines.append("Вопрос на завтра: Что одно может поддержать тебя?")
        
        return " ".join(lines)

    async def analyze_goals(self, goals: list[Goal]) -> str:
        """Generate gentle reflection across all goals."""
        if not self.api_key:
            return self._placeholder_goals_analysis(goals)

        return self._placeholder_goals_analysis(goals)

    def _placeholder_goals_analysis(self, goals: list[Goal]) -> str:
        """Placeholder goals analysis."""
        if not goals:
            return "Цели еще не созданы. Когда будут готовы, я помогу найти связи между ними."

        by_horizon = {}
        for g in goals:
            by_horizon.setdefault(g.horizon, []).append(g)

        lines = [f"У вас {len(goals)} целей на разных горизонтах."]
        
        if "dream_life" in by_horizon:
            lines.append("Жизнь мечты описана — это хороший ориентир для проверки более близких целей.")

        if "month" in by_horizon and "dream_life" in by_horizon:
            lines.append("Есть цели и на месяц, и на жизнь мечты — можно проверять, как шаги на месяц приближают к большой картинке.")

        lines.append("Вопрос: Какие цели сейчас просят больше внимания, а какие можно отпустить или отложить?")

        return " ".join(lines)

    async def generate_weekly_reflection(
        self,
        entries: List[Entry],
        goals: List[Goal],
    ) -> Dict[str, Any]:
        """Generate weekly reflection based on entries and goals.
        
        Returns structured output with:
        - patterns: what repeated
        - energy_insights: when energy was higher/lower
        - goal_connections: possible links to goals
        - next_week_question: gentle question
        - next_week_focus: small focus area
        """
        if len(entries) < 3:
            return {
                "patterns": "Недостаточно записей для выводов. Продолжай записывать — гипотезы появятся сами.",
                "energy_insights": "Пока рано говорить о динамике энергии.",
                "goal_connections": "Когда будет больше записей, здесь появятся связи с целями.",
                "next_week_question": "Что одно хочется попробовать на следующей неделе?",
                "next_week_focus": "Просто продолжать записывать Пульс — этого достаточно.",
                "is_placeholder": True,
            }

        if not self.api_key:
            return self._placeholder_weekly_reflection(entries, goals)

        # Real implementation would call AI provider
        return await self._real_weekly_reflection(entries, goals)

    def _placeholder_weekly_reflection(
        self,
        entries: List[Entry],
        goals: List[Goal],
    ) -> Dict[str, Any]:
        """Placeholder weekly reflection when no AI key is present."""
        # Calculate basic stats
        moods = [e.mood for e in entries if e.mood is not None]
        energies = [e.energy for e in entries if e.energy is not None]
        anxieties = [e.anxiety for e in entries if e.anxiety is not None]
        
        avg_mood = sum(moods) / len(moods) if moods else None
        avg_energy = sum(energies) / len(energies) if energies else None
        avg_anxiety = sum(anxieties) / len(anxieties) if anxieties else None

        # Find insights text
        patterns_text = f"За неделю {len(entries)} записей. "
        if avg_mood:
            patterns_text += f"Среднее настроение: {avg_mood:.1f}/10. "
        if avg_energy:
            patterns_text += f"Средняя энергия: {avg_energy:.1f}/10. "
        patterns_text += "Когда подключится AI, здесь появятся мягкие гипотезы о повторяющихся темах."

        energy_text = "Недельное отражение почти готово. Сейчас AI-ключ не подключен, поэтому я могу показать только базовую динамику. "
        if avg_energy:
            if avg_energy >= 7:
                energy_text += "Энергия на неделе была на хорошем уровне. "
            elif avg_energy <= 4:
                energy_text += "Энергия на неделе была ниже — это данность, не оценка. "
            else:
                energy_text += "Энергия колебалась в среднем диапазоне. "
        energy_text += "Когда ключ будет добавлен, здесь появится мягкое резюме недели: повторяющиеся темы, связь с энергией и один вопрос на следующую неделю."

        # Goals connection
        goal_text = ""
        if goals:
            month_goals = [g for g in goals if g.horizon == "month" and g.status == "active"]
            dream_goals = [g for g in goals if g.horizon == "dream_life" and g.status == "active"]
            if month_goals:
                goal_text += f"Активных целей на месяц: {len(month_goals)}. "
            if dream_goals:
                goal_text += "Жизнь мечты описана — хороший ориентир. "
            goal_text += "С AI появятся мягкие гипотезы о связи состояния и направления."
        else:
            goal_text = "Цели пока не созданы. Когда появятся, AI поможет найти связи с ежедневным состоянием."

        return {
            "patterns": patterns_text,
            "energy_insights": energy_text,
            "goal_connections": goal_text,
            "next_week_question": "Что одно хочется попробовать на следующей неделе?",
            "next_week_focus": "Продолжать записывать Пульс — этого достаточно.",
            "is_placeholder": True,
        }

    async def _real_weekly_reflection(
        self,
        entries: List[Entry],
        goals: List[Goal],
    ) -> Dict[str, Any]:
        """Real AI weekly reflection using configured provider."""
        try:
            prompt = self.build_weekly_prompt(entries, goals)
            system_prompt = "Ты мягкий помощник по самонаблюдению. Ты не психолог и не врач. Ты помогаешь пользователю заметить паттерны в своём состоянии без оценки и давления."

            if self.provider == "anthropic" and ANTHROPIC_AVAILABLE:
                content = await self._call_anthropic(system_prompt, prompt)
            elif self.provider == "openai" and OPENAI_AVAILABLE:
                content = await self._call_openai(system_prompt, prompt)
            else:
                return self._placeholder_weekly_reflection(entries, goals)

            if not content:
                raise ValueError("Empty AI response")

            # Parse structured response
            result = self._parse_ai_response(content)
            result["is_placeholder"] = False
            result["raw_output"] = content
            result["provider"] = self.provider
            return result

        except Exception as e:
            # Fallback to placeholder on any error
            print(f"AI error ({self.provider}): {e}")
            result = self._placeholder_weekly_reflection(entries, goals)
            result["is_placeholder"] = True
            result["error"] = str(e)
            result["provider"] = self.provider
            return result

    async def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Call OpenAI API."""
        client = AsyncOpenAI(api_key=self.api_key)
        response = await client.chat.completions.create(
            model=self.model or "gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=800,
        )
        return response.choices[0].message.content or ""

    async def _call_anthropic(self, system_prompt: str, user_prompt: str) -> str:
        """Call Anthropic Claude API."""
        client = AsyncAnthropic(api_key=self.api_key)
        # Claude uses different model naming
        model = self.model or "claude-3-haiku-20240307"
        if model.startswith("gpt-"):
            # User set OpenAI model but using Anthropic key, use default Claude model
            model = "claude-3-haiku-20240307"

        response = await client.messages.create(
            model=model,
            max_tokens=800,
            temperature=0.7,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        # Extract text from content blocks
        text_parts = []
        for block in response.content:
            if hasattr(block, 'text'):
                text_parts.append(block.text)
        return "\n".join(text_parts)

    def _parse_ai_response(self, content: str) -> Dict[str, Any]:
        """Parse AI response into structured fields."""
        # Default values
        result = {
            "patterns": "",
            "energy_insights": "",
            "goal_connections": "",
            "next_week_question": "",
            "next_week_focus": "",
        }

        # Try to extract sections by keywords
        lines = content.split('\n')
        current_key = None
        buffer = []

        for line in lines:
            line_lower = line.lower().strip()

            # Detect section headers
            if 'повторялось' in line_lower or 'patterns' in line_lower:
                if current_key and buffer:
                    result[current_key] = ' '.join(buffer).strip()
                current_key = "patterns"
                buffer = []
            elif 'энергия' in line_lower or 'energy' in line_lower:
                if current_key and buffer:
                    result[current_key] = ' '.join(buffer).strip()
                current_key = "energy_insights"
                buffer = []
            elif 'цел' in line_lower or 'goals' in line_lower or 'связь' in line_lower:
                if current_key and buffer:
                    result[current_key] = ' '.join(buffer).strip()
                current_key = "goal_connections"
                buffer = []
            elif 'вопрос' in line_lower or 'question' in line_lower:
                if current_key and buffer:
                    result[current_key] = ' '.join(buffer).strip()
                current_key = "next_week_question"
                buffer = []
            elif 'фокус' in line_lower or 'focus' in line_lower:
                if current_key and buffer:
                    result[current_key] = ' '.join(buffer).strip()
                current_key = "next_week_focus"
                buffer = []
            elif current_key:
                # Skip markdown headers and empty lines
                if line.strip() and not line.startswith('#'):
                    buffer.append(line.strip())

        # Save last section
        if current_key and buffer:
            result[current_key] = ' '.join(buffer).strip()

        # Fill empty fields with defaults
        if not result["patterns"]:
            result["patterns"] = "За неделю проявились интересные паттерны. Смотри детали ниже."
        if not result["energy_insights"]:
            result["energy_insights"] = "Энергия колебалась — это нормально. Важно замечать, когда она выше или ниже."
        if not result["goal_connections"]:
            result["goal_connections"] = "Записи и цели связаны более тонко, чем кажется. AI поможет увидеть это при следующих отражениях."
        if not result["next_week_question"]:
            result["next_week_question"] = "Что одно хочется попробовать на следующей неделе?"
        if not result["next_week_focus"]:
            result["next_week_focus"] = "Продолжать записывать Пульс — этого достаточно."

        return result

    def build_weekly_prompt(
        self,
        entries: List[Entry],
        goals: List[Goal],
    ) -> str:
        """Build the prompt for weekly reflection."""
        # Limit entries to avoid exceeding model context window
        MAX_ENTRIES = 50
        MAX_INSIGHT_LENGTH = 500

        entries_text = []
        for e in entries[:MAX_ENTRIES]:
            date_str = e.created_at.strftime("%Y-%m-%d") if e.created_at else "Unknown"
            parts = [f"{date_str}:"]
            if e.mood:
                parts.append(f"настроение {e.mood}/10")
            if e.energy:
                parts.append(f"энергия {e.energy}/10")
            if e.anxiety:
                parts.append(f"тревога {e.anxiety}/10")
            if e.insight:
                insight = e.insight
                if len(insight) > MAX_INSIGHT_LENGTH:
                    insight = insight[:MAX_INSIGHT_LENGTH] + "..."
                parts.append(f"инсайт: {insight}")
            entries_text.append(" | ".join(parts))

        goals_text = []
        for g in goals:
            if g.status == "active":
                goals_text.append(f"[{g.horizon}] {g.title}")

        return f"""Ты мягкий помощник по самонаблюдению. Ты не психолог, не врач и не ставишь диагнозы. Проанализируй записи пользователя за неделю как гипотезы, а не выводы.

Данные недели:
{chr(10).join(entries_text)}

Цели пользователя:
{chr(10).join(goals_text) if goals_text else "Цели пока не созданы."}

Верни структурированный ответ с:
1. patterns: Что повторялось на этой неделе (1-2 предложения).
2. energy_insights: Когда энергия была выше или ниже (1-2 предложения).
3. goal_connections: Возможную связь состояния с целями (1-2 предложения).
4. next_week_question: Один мягкий вопрос на следующую неделю.
5. next_week_focus: Один маленький фокус на ближайшие 7 дней.

Тон: спокойно, бережно, без давления. Не используй медицинские рекомендации."""

    async def analyze_all_entries(
        self,
        entries: List[Entry],
        goals: List[Goal],
    ) -> Dict[str, Any]:
        """Analyze all user entries to find deep patterns and insights using Claude AI.
        
        Returns structured analysis with:
        - key_patterns: recurring themes across all entries
        - emotional_dynamics: mood/energy trends over time
        - body_signals: physical sensations that repeat
        - insight_themes: common insights and realizations
        - goal_alignment: how entries relate to goals
        - recommendations: gentle suggestions based on data
        """
        if len(entries) < 5:
            return {
                "key_patterns": "Недостаточно записей для глубокого анализа. Продолжай записывать — анализ появится автоматически когда накопится больше данных.",
                "emotional_dynamics": "Пока рано выявлять динамику. Минимум 5 записей для базового анализа.",
                "body_signals": "Нет данных.",
                "insight_themes": "Нет данных.",
                "goal_alignment": "Нет данных.",
                "recommendations": "Продолжать регулярно записывать Пульс — этого достаточно.",
                "is_placeholder": True,
            }

        if not self.api_key:
            return self._placeholder_all_entries_analysis(entries, goals)

        return await self._real_all_entries_analysis(entries, goals)

    def _placeholder_all_entries_analysis(
        self,
        entries: List[Entry],
        goals: List[Goal],
    ) -> Dict[str, Any]:
        """Placeholder when no AI key configured."""
        moods = [e.mood for e in entries if e.mood is not None]
        energies = [e.energy for e in entries if e.energy is not None]
        
        avg_mood = sum(moods) / len(moods) if moods else None
        avg_energy = sum(energies) / len(energies) if energies else None
        
        patterns = f"За период {len(entries)} записей. "
        if avg_mood:
            patterns += f"Среднее настроение: {avg_mood:.1f}/10. "
        if avg_energy:
            patterns += f"Средняя энергия: {avg_energy:.1f}/10. "
        patterns += "Когда подключится AI-ключ, здесь появятся глубинные паттерны."
        
        return {
            "key_patterns": patterns,
            "emotional_dynamics": "Динамика будет видна при подключении Claude AI.",
            "body_signals": "Паттерны телесных ощущений появятся после AI-анализа.",
            "insight_themes": "Темы инсайтов будут извлечены при подключении AI.",
            "goal_alignment": f"Активных целей: {len([g for g in goals if g.status == 'active'])}. Связь с записями проявится после анализа." if goals else "Цели не созданы.",
            "recommendations": "Продолжать записывать Пульс — анализ появится автоматически.",
            "is_placeholder": True,
        }

    async def _real_all_entries_analysis(
        self,
        entries: List[Entry],
        goals: List[Goal],
    ) -> Dict[str, Any]:
        """Real AI analysis using Claude."""
        try:
            prompt = self.build_all_entries_prompt(entries, goals)
            system_prompt = "Ты мягкий аналитик самонаблюдений. Ты не психолог и не врач. Ты анализируешь долгосрочные паттерны в записях пользователя и даёшь мягкие гипотезы без давления и оценки."

            if self.provider == "anthropic" and ANTHROPIC_AVAILABLE:
                content = await self._call_anthropic(system_prompt, prompt)
            elif self.provider == "openai" and OPENAI_AVAILABLE:
                content = await self._call_openai(system_prompt, prompt)
            else:
                return self._placeholder_all_entries_analysis(entries, goals)

            if not content:
                raise ValueError("Empty AI response")

            result = self._parse_all_entries_response(content)
            result["is_placeholder"] = False
            result["raw_output"] = content
            result["provider"] = self.provider
            result["entry_count"] = len(entries)
            return result

        except Exception as e:
            print(f"AI all-entries error ({self.provider}): {e}")
            result = self._placeholder_all_entries_analysis(entries, goals)
            result["is_placeholder"] = True
            result["error"] = str(e)
            return result

    def build_all_entries_prompt(
        self,
        entries: List[Entry],
        goals: List[Goal],
    ) -> str:
        """Build prompt for analyzing all entries."""
        # Limit entries to avoid token overflow
        MAX_ENTRIES = 100
        MAX_TEXT_LENGTH = 300
        
        entries_text = []
        for e in entries[:MAX_ENTRIES]:
            date_str = e.created_at.strftime("%Y-%m-%d") if e.created_at else "Unknown"
            parts = [f"[{date_str}]"]
            if e.mood is not None:
                parts.append(f"Н:{e.mood}")
            if e.energy is not None:
                parts.append(f"Э:{e.energy}")
            if e.anxiety is not None:
                parts.append(f"Т:{e.anxiety}")
            if e.body_state:
                text = e.body_state[:MAX_TEXT_LENGTH] + "..." if len(e.body_state) > MAX_TEXT_LENGTH else e.body_state
                parts.append(f"Тело: {text}")
            if e.insight:
                text = e.insight[:MAX_TEXT_LENGTH] + "..." if len(e.insight) > MAX_TEXT_LENGTH else e.insight
                parts.append(f"Инсайт: {text}")
            if e.gratitude:
                parts.append(f"Благодарность: {e.gratitude}")
            if e.tomorrow_commitment:
                parts.append(f"Обязательство: {e.tomorrow_commitment}")
            entries_text.append(" | ".join(parts))
        
        goals_text = []
        for g in goals:
            if g.status == "active":
                goals_text.append(f"- [{g.horizon}] {g.current_title}")

        return f"""Проанализируй все записи пользователя за весь период. Найди глубинные паттерны и мягкие закономерности.

ЗАПИСИ ПОЛЬЗОВАТЕЛЯ ({len(entries)} записей):
{chr(10).join(entries_text)}

АКТИВНЫЕ ЦЕЛИ:
{chr(10).join(goals_text) if goals_text else "Цели не созданы."}

Верни структурированный анализ:

1. KEY_PATTERNS: Главные повторяющиеся темы (2-3 предложения)
2. EMOTIONAL_DYNAMICS: Как менялось настроение и энергия во времени (2-3 предложения)  
3. BODY_SIGNALS: Какие телесные ощущения повторялись (1-2 предложения)
4. INSIGHT_THEMES: Какие темы в инсайтах повторялись (2-3 предложения)
5. GOAL_ALIGNMENT: Насколько записи соответствуют целям (1-2 предложения)
6. RECOMMENDATIONS: Мягкие рекомендации на основе данных (2-3 предложения)

Тон: бережный, любопытный, без давления и диагностики."""

    def _parse_all_entries_response(self, content: str) -> Dict[str, Any]:
        """Parse AI response for all-entries analysis."""
        result = {
            "key_patterns": "",
            "emotional_dynamics": "",
            "body_signals": "",
            "insight_themes": "",
            "goal_alignment": "",
            "recommendations": "",
        }
        
        lines = content.split('\n')
        current_key = None
        buffer = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            if 'key_patterns' in line_lower or 'паттерн' in line_lower or 'повторяющиеся темы' in line_lower:
                if current_key and buffer:
                    result[current_key] = ' '.join(buffer).strip()
                current_key = "key_patterns"
                buffer = []
            elif 'emotional_dynamics' in line_lower or 'динамик' in line_lower or 'настроение' in line_lower:
                if current_key and buffer:
                    result[current_key] = ' '.join(buffer).strip()
                current_key = "emotional_dynamics"
                buffer = []
            elif 'body_signals' in line_lower or 'тел' in line_lower or 'ощущен' in line_lower:
                if current_key and buffer:
                    result[current_key] = ' '.join(buffer).strip()
                current_key = "body_signals"
                buffer = []
            elif 'insight_themes' in line_lower or 'инсайт' in line_lower or 'осознан' in line_lower:
                if current_key and buffer:
                    result[current_key] = ' '.join(buffer).strip()
                current_key = "insight_themes"
                buffer = []
            elif 'goal_alignment' in line_lower or 'цел' in line_lower or 'соответствие' in line_lower:
                if current_key and buffer:
                    result[current_key] = ' '.join(buffer).strip()
                current_key = "goal_alignment"
                buffer = []
            elif 'recommendations' in line_lower or 'рекомендац' in line_lower:
                if current_key and buffer:
                    result[current_key] = ' '.join(buffer).strip()
                current_key = "recommendations"
                buffer = []
            elif current_key:
                if line.strip() and not line.startswith('#') and not line.startswith('**'):
                    buffer.append(line.strip())
        
        if current_key and buffer:
            result[current_key] = ' '.join(buffer).strip()
        
        # Defaults
        for key in result:
            if not result[key]:
                result[key] = "Анализ этого аспекта появится при следующем обновлении."
        
        return result
