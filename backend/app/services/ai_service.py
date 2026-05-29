"""
AI Service for entry and goal analysis.
Currently returns placeholder responses - requires AI_API_KEY for real implementation.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models import Entry, Goal
from app.config import settings


class AIService:
    def __init__(self):
        self.api_key = settings.ai_api_key
        self.model = settings.ai_model or "gpt-4"

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
        """Real AI weekly reflection - to be implemented when AI key is present."""
        # This will be implemented when connecting to OpenAI/Anthropic
        # For now, return placeholder with flag
        result = self._placeholder_weekly_reflection(entries, goals)
        result["is_placeholder"] = False
        result["note"] = "Real AI implementation pending - provider abstraction ready"
        return result

    def build_weekly_prompt(
        self,
        entries: List[Entry],
        goals: List[Goal],
    ) -> str:
        """Build the prompt for weekly reflection."""
        entries_text = []
        for e in entries:
            date_str = e.created_at.strftime("%Y-%m-%d") if e.created_at else "Unknown"
            parts = [f"{date_str}:"]
            if e.mood:
                parts.append(f"настроение {e.mood}/10")
            if e.energy:
                parts.append(f"энергия {e.energy}/10")
            if e.anxiety:
                parts.append(f"тревога {e.anxiety}/10")
            if e.insight:
                parts.append(f"инсайт: {e.insight}")
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
