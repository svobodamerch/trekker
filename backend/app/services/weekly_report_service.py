"""Service for generating weekly AI reports for users and community."""
import json
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import User, Entry, WeeklyReport, CommunityWeeklyReport, CommunityPost
from app.services.ai_service import AIService


class WeeklyReportService:
    """Generate and manage weekly AI reports."""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()
    
    def get_week_boundaries(self, target_date: date = None) -> tuple[date, date]:
        """Get Monday and Sunday for the week containing target_date."""
        if target_date is None:
            target_date = date.today()
        
        # Find Monday (weekday() returns 0 for Monday)
        monday = target_date - timedelta(days=target_date.weekday())
        sunday = monday + timedelta(days=6)
        return monday, sunday
    
    def get_user_entries_for_week(self, user_id: int, week_start: date, week_end: date) -> List[Entry]:
        """Get all user entries for a specific week."""
        return self.db.query(Entry).filter(
            Entry.user_id == user_id,
            Entry.created_at >= datetime.combine(week_start, datetime.min.time()),
            Entry.created_at <= datetime.combine(week_end, datetime.max.time()),
        ).order_by(Entry.created_at.asc()).all()
    
    def calculate_user_stats(self, entries: List[Entry]) -> Dict:
        """Calculate statistics from user entries."""
        if not entries:
            return {
                "count": 0,
                "days_with_entries": 0,
                "avg_mood": None,
                "avg_anxiety": None,
                "avg_energy": None,
                "insights": [],
                "body_states": [],
                "gratitudes": [],
                "commitments": [],
            }
        
        # Count unique days
        days = set()
        moods = []
        anxieties = []
        energies = []
        insights = []
        body_states = []
        gratitudes = []
        commitments = []
        
        for entry in entries:
            entry_date = entry.created_at.date()
            days.add(entry_date)
            
            if entry.mood is not None:
                moods.append(entry.mood)
            if entry.anxiety is not None:
                anxieties.append(entry.anxiety)
            if entry.energy is not None:
                energies.append(entry.energy)
            if entry.insight:
                insights.append(entry.insight)
            if entry.body_state:
                body_states.append(entry.body_state)
            if entry.gratitude:
                gratitudes.append(entry.gratitude)
            if entry.tomorrow_commitment:
                commitments.append(entry.tomorrow_commitment)
        
        return {
            "count": len(entries),
            "days_with_entries": len(days),
            "avg_mood": sum(moods) / len(moods) if moods else None,
            "avg_anxiety": sum(anxieties) / len(anxieties) if anxieties else None,
            "avg_energy": sum(energies) / len(energies) if energies else None,
            "insights": insights,
            "body_states": body_states,
            "gratitudes": gratitudes,
            "commitments": commitments,
        }
    
    def build_user_prompt(self, user: User, week_start: date, week_end: date, stats: Dict) -> str:
        """Build AI prompt for individual user report."""
        days_missed = 7 - stats["days_with_entries"]
        
        prompt = f"""Ты — мягкий, поддерживающий AI-ассистент в приложении для самонаблюдения. 
Напиши персональный еженедельный отчет для пользователя на основе его записей.

ДАННЫЕ ПОЛЬЗОВАТЕЛЯ:
Имя: {user.first_name or 'друг'}
Период: {week_start.strftime('%d.%m')} — {week_end.strftime('%d.%m.%Y')}

СТАТИСТИКА НЕДЕЛИ:
- Всего записей: {stats['count']}
- Дней с записями: {stats['days_with_entries']} из 7
- Пропущено дней: {days_missed}
{f"- Среднее настроение: {stats['avg_mood']:.1f}/10" if stats['avg_mood'] else ''}
{f"- Средняя тревога: {stats['avg_anxiety']:.1f}/10" if stats['avg_anxiety'] else ''}
{f"- Средняя энергия: {stats['avg_energy']:.1f}/10" if stats['avg_energy'] else ''}

ИНСАЙТЫ ПОЛЬЗОВАТЕЛЯ ({len(stats['insights'])}):
"""
        
        for i, insight in enumerate(stats['insights'][:5], 1):
            prompt += f"{i}. {insight}\n"
        
        if stats['body_states']:
            prompt += f"\nТЕЛЕСНЫЕ ОЩУЩЕНИЯ ({len(stats['body_states'])}):\n"
            for state in stats['body_states'][:3]:
                prompt += f"- {state}\n"
        
        if stats['gratitudes']:
            prompt += f"\nБЛАГОДАРНОСТИ ({len(stats['gratitudes'])}):\n"
            for gratitude in stats['gratitudes'][:3]:
                prompt += f"- {gratitude}\n"
        
        prompt += """
НАПИШИ ОТЧЕТ В СЛЕДУЮЩЕЙ СТРУКТУРЕ (JSON):
{
  "summary": "2-3 предложения о том, как прошла неделя",
  "highlights": "Главные достижения/наблюдения (1-2 предложения)",
  "patterns": "Замеченные паттерны (1-2 предложения)",
  "encouragement": "Тёплые слова поддержки, учитывая активность пользователя",
  "suggestions": "1-2 мягкие рекомендации на следующую неделю"
}

ТРЕБОВАНИЯ:
1. Тон: мягкий, поддерживающий, без давления
2. Если пользователь писал каждый день — похвали и отмети это
3. Если были пропуски — не упрекай, просто отметь факт
4. Ссылки на конкретные инсайты пользователя
5. Длина каждого поля: максимум 150 символов
"""
        return prompt
    
    def parse_user_report(self, ai_response: str) -> Dict:
        """Parse AI response for individual report."""
        try:
            # Try to find JSON in the response
            start = ai_response.find('{')
            end = ai_response.rfind('}')
            if start != -1 and end != -1:
                json_str = ai_response[start:end+1]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback parsing
        return {
            "summary": "Эта неделя была наполнена самонаблюдением.",
            "highlights": "Ты уделял время рефлексии и записывал свои состояния.",
            "patterns": "Продолжай в том же духе — регулярность важнее идеальности.",
            "encouragement": "Молодец, что приходишь сюда и фиксируешь своё состояние.",
            "suggestions": "На следующей неделе можно попробовать обратить внимание на связь между сном и энергией.",
        }
    
    async def generate_user_report(self, user: User, week_start: date, week_end: date) -> WeeklyReport:
        """Generate AI report for a single user."""
        # Get entries for the week
        entries = self.get_user_entries_for_week(user.id, week_start, week_end)
        stats = self.calculate_user_stats(entries)
        
        # Build and send prompt to AI
        prompt = self.build_user_prompt(user, week_start, week_end, stats)
        
        ai_response = await self.ai_service._call_anthropic(prompt)
        report_data = self.parse_user_report(ai_response)
        
        # Create report record
        report = WeeklyReport(
            user_id=user.id,
            week_start=week_start,
            week_end=week_end,
            entries_count=stats["count"],
            days_with_entries=stats["days_with_entries"],
            days_missed=7 - stats["days_with_entries"],
            avg_mood=stats["avg_mood"],
            avg_anxiety=stats["avg_anxiety"],
            avg_energy=stats["avg_energy"],
            summary=report_data.get("summary", ""),
            highlights=report_data.get("highlights", ""),
            patterns=report_data.get("patterns", ""),
            encouragement=report_data.get("encouragement", ""),
            suggestions=report_data.get("suggestions", ""),
            raw_ai_output=ai_response,
        )
        
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    def get_community_stats(self, week_start: date, week_end: date) -> Dict:
        """Get aggregated stats for the entire community."""
        # Get all entries for the week
        entries = self.db.query(Entry).filter(
            Entry.created_at >= datetime.combine(week_start, datetime.min.time()),
            Entry.created_at <= datetime.combine(week_end, datetime.max.time()),
        ).all()
        
        # Get unique active users
        active_user_ids = set(e.user_id for e in entries)
        total_users = self.db.query(User).count()
        
        # Calculate averages
        moods = [e.mood for e in entries if e.mood is not None]
        anxieties = [e.anxiety for e in entries if e.anxiety is not None]
        energies = [e.energy for e in entries if e.energy is not None]
        
        pulse_count = len([e for e in entries if e.entry_type == 'pulse'])
        diary_count = len([e for e in entries if e.entry_type == 'diary'])
        
        return {
            "total_users": total_users,
            "active_users": len(active_user_ids),
            "total_entries": len(entries),
            "pulse_entries": pulse_count,
            "diary_entries": diary_count,
            "avg_mood": sum(moods) / len(moods) if moods else None,
            "avg_anxiety": sum(anxieties) / len(anxieties) if anxieties else None,
            "avg_energy": sum(energies) / len(energies) if energies else None,
        }
    
    async def generate_community_report(self, week_start: date, week_end: date) -> CommunityWeeklyReport:
        """Generate AI report for the entire community."""
        stats = self.get_community_stats(week_start, week_end)
        
        prompt = f"""Ты — мягкий, поддерживающий AI-ассистент в приложении для самонаблюдения.
Напиши общий еженедельный отчет для сообщества на основе агрегированных данных.

ПЕРИОД: {week_start.strftime('%d.%m')} — {week_end.strftime('%d.%m.%Y')}

СТАТИСТИКА СООБЩЕСТВА:
- Всего пользователей: {stats['total_users']}
- Активных пользователей: {stats['active_users']}
- Всего записей: {stats['total_entries']}
- Пульсов дня: {stats['pulse_entries']}
- Дневниковых записей: {stats['diary_entries']}
{f"- Среднее настроение сообщества: {stats['avg_mood']:.1f}/10" if stats['avg_mood'] else ''}
{f"- Средняя тревога: {stats['avg_anxiety']:.1f}/10" if stats['avg_anxiety'] else ''}
{f"- Средняя энергия: {stats['avg_energy']:.1f}/10" if stats['avg_energy'] else ''}

НАПИШИ ОТЧЕТ В СЛЕДУЮЩЕЙ СТРУКТУРЕ (JSON):
{
  "community_summary": "2-3 предложения о том, как прошла неделя у сообщества",
  "trends": "Общие тенденции и паттерны (1-2 предложения)",
  "encouragement": "Ободряющие слова для всего сообщества",
  "collective_challenge": "Мягкий челлендж/приглашение на следующую неделю"
}

ТРЕБОВАНИЯ:
1. Тон: мягкий, объединяющий, вдохновляющий
2. Отмечай достижения сообщества как целого
3. Если активность низкая — не критикуй, просто отметь
4. Челлендж должен быть лёгким и приятным
5. Длина каждого поля: максимум 200 символов
"""
        
        ai_response = await self.ai_service._call_anthropic(prompt)
        
        try:
            start = ai_response.find('{')
            end = ai_response.rfind('}')
            if start != -1 and end != -1:
                report_data = json.loads(ai_response[start:end+1])
            else:
                raise ValueError("No JSON found")
        except:
            report_data = {
                "community_summary": f"На этой неделе сообщество сделало {stats['total_entries']} записей.",
                "trends": "Люди продолжают уделять время себе и своему состоянию.",
                "encouragement": "Вместе мы создаём пространство для искренности и поддержки.",
                "collective_challenge": "На следующей неделе попробуйте записывать одну маленькую благодарность каждый день.",
            }
        
        report = CommunityWeeklyReport(
            week_start=week_start,
            week_end=week_end,
            total_users=stats["total_users"],
            active_users=stats["active_users"],
            total_entries=stats["total_entries"],
            total_pulse_entries=stats["pulse_entries"],
            total_diary_entries=stats["diary_entries"],
            community_avg_mood=stats["avg_mood"],
            community_avg_anxiety=stats["avg_anxiety"],
            community_avg_energy=stats["avg_energy"],
            community_summary=report_data.get("community_summary", ""),
            trends=report_data.get("trends", ""),
            encouragement=report_data.get("encouragement", ""),
            collective_challenge=report_data.get("collective_challenge", ""),
            raw_ai_output=ai_response,
        )
        
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    async def generate_all_reports(self, target_date: date = None, send_via_telegram: bool = True):
        """Generate reports for all users and community for the given week."""
        from app.config import settings
        import httpx
        from datetime import datetime

        week_start, week_end = self.get_week_boundaries(target_date)

        # Check if already generated
        existing = self.db.query(CommunityWeeklyReport).filter(
            CommunityWeeklyReport.week_start == week_start
        ).first()

        if existing:
            return existing

        # Generate community report first
        community_report = await self.generate_community_report(week_start, week_end)

        # Post community report to feed
        await self._post_community_report(community_report)

        # Get all users
        users = self.db.query(User).all()

        # Generate and optionally send individual reports
        for user in users:
            # Check if user already has report for this week
            existing_user_report = self.db.query(WeeklyReport).filter(
                WeeklyReport.user_id == user.id,
                WeeklyReport.week_start == week_start,
            ).first()

            if not existing_user_report:
                try:
                    report = await self.generate_user_report(user, week_start, week_end)

                    # Send via Telegram if configured
                    if send_via_telegram and settings.bot_token and user.telegram_user_id:
                        try:
                            await self._send_report_via_telegram(
                                settings.bot_token,
                                user.telegram_user_id,
                                report
                            )
                            report.sent_at = datetime.utcnow()
                            self.db.commit()
                        except Exception as e:
                            print(f"Failed to send report to user {user.id}: {e}")

                except Exception as e:
                    print(f"Failed to generate report for user {user.id}: {e}")

        return community_report

    async def _send_report_via_telegram(self, bot_token: str, chat_id: str, report: WeeklyReport):
        """Send user report via Telegram Bot API."""
        import httpx

        text = self.format_user_report_for_bot(report)

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "Markdown",
                },
                timeout=30.0
            )
            resp.raise_for_status()
            return resp.json()

    async def _post_community_report(self, report: CommunityWeeklyReport):
        """Post community report as system post in community feed."""
        from app.models.community import CommunityPost

        title, body = self.format_community_report_for_post(report)

        try:
            post = CommunityPost(
                user_id=None,  # System post
                title=title,
                body=body,
                visibility="named",
                is_weekly_report=True,
                source_type="weekly_report",
            )
            self.db.add(post)
            self.db.commit()
            self.db.refresh(post)

            report.community_post_id = post.id
            self.db.commit()

            print(f"Posted community weekly report as post {post.id}")

        except Exception as e:
            print(f"Failed to post community report: {e}")
    
    def format_user_report_for_bot(self, report: WeeklyReport) -> str:
        """Format report for Telegram bot message."""
        lines = [
            f"📊 *Отчёт за неделю* ({report.week_start.strftime('%d.%m')} — {report.week_end.strftime('%d.%m')})",
            "",
            f"📝 Записей: {report.entries_count} | Дней: {report.days_with_entries}/7",
        ]
        
        if report.avg_mood:
            lines.append(f"😊 Настроение: {report.avg_mood:.1f}/10")
        if report.avg_energy:
            lines.append(f"⚡ Энергия: {report.avg_energy:.1f}/10")
        if report.avg_anxiety:
            lines.append(f"🌊 Тревога: {report.avg_anxiety:.1f}/10")
        
        lines.extend([
            "",
            f"*{report.summary}*",
            "",
            f"🌟 {report.highlights}",
            "",
            f"💡 {report.patterns}",
            "",
            f"🤗 {report.encouragement}",
            "",
            f"✨ На следующую неделю:\n{report.suggestions}",
        ])
        
        return "\n".join(lines)
    
    def format_community_report_for_post(self, report: CommunityWeeklyReport) -> tuple[str, str]:
        """Format community report for community post (title, body)."""
        title = f"📊 Отчёт сообщества за неделю {report.week_start.strftime('%d.%m')} — {report.week_end.strftime('%d.%m')}"
        
        body_lines = [
            f"*{report.community_summary}*",
            "",
            f"📈 Статистика:",
            f"• Активных участников: {report.active_users} из {report.total_users}",
            f"• Всего записей: {report.total_entries}",
            f"• Пульсов дня: {report.total_pulse_entries}",
            f"• Дневников: {report.total_diary_entries}",
        ]
        
        if report.community_avg_mood:
            body_lines.append(f"• Среднее настроение: {report.community_avg_mood:.1f}/10")
        
        body_lines.extend([
            "",
            f"🔄 {report.trends}",
            "",
            f"💪 {report.encouragement}",
            "",
            f"🎯 Челлендж на следующую неделю:\n{report.collective_challenge}",
        ])
        
        return title, "\n".join(body_lines)
