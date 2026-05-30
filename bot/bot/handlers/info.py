"""Information center handlers: help, about, privacy, updates, roadmap, changelog, feedback."""

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.config import settings

router = Router()


def get_mini_app_url(path: str = "") -> str:
    """Build Mini App URL with specific route."""
    base = settings.mini_app_url.rstrip('/')
    return f"{base}{path}"


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Show help and usage instructions."""
    help_text = (
        "📖 *Как пользоваться*\n\n"
        "Главный сценарий простой:\n\n"
        "1️⃣ *Пульс дня*\n"
        "Отмечаешь настроение, энергию, тревогу, короткий инсайт и один маленький фокус на завтра.\n\n"
        "2️⃣ *Динамика*\n"
        "Когда накопится несколько записей, можно смотреть, как меняется состояние.\n\n"
        "3️⃣ *Цели и жизнь мечты*\n"
        "Можно формулировать ориентиры на месяц, год, 3 года, 5 лет и описывать жизнь мечты.\n\n"
        "4️⃣ *Колесо баланса*\n"
        "Можно сделать срез текущей жизни по сферам и обновлять его раз в 2 недели.\n\n"
        "5️⃣ *Недельное отражение*\n"
        "Когда накопятся записи, приложение может мягко подсветить повторяющиеся темы.\n\n"
        "6️⃣ *Обратная связь*\n"
        "Если что-то непонятно, сломалось или хочется предложить идею — напиши через /feedback.\n\n"
        "Здесь нет оценок, наказаний и давления. Пропуски нормальны."
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📝 Открыть приложение",
            web_app=types.WebAppInfo(url=get_mini_app_url("/"))
        )],
        [InlineKeyboardButton(
            text="💬 Оставить обратную связь",
            callback_data="feedback_prompt"
        )]
    ])
    
    await message.answer(help_text, reply_markup=keyboard, parse_mode="Markdown")


@router.message(Command("about"))
async def cmd_about(message: types.Message):
    """Explain what this app is."""
    about_text = (
        "🌿 *Что это за приложение*\n\n"
        "Это пространство для самонаблюдения: коротких ежедневных записей, целей, динамики и мягкой рефлексии.\n\n"
        "Идея не в том, чтобы «стать дисциплинированнее» или каждый день идеально всё заполнять.\n\n"
        "Идея в том, чтобы постепенно лучше видеть:\n"
        "• что с тобой происходит\n"
        "• что влияет на состояние\n"
        "• какие цели действительно живые\n"
        "• куда хочется двигаться\n"
        "• что помогает возвращаться к себе без давления\n\n"
        "Приложение сейчас развивается в формате закрытой беты. "
        "Поэтому я постепенно добавляю функции, смотрю на обратную связь и улучшаю mini app."
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📖 Как пользоваться",
            callback_data="show_help"
        )],
        [InlineKeyboardButton(
            text="🔒 Приватность",
            callback_data="show_privacy"
        )],
        [InlineKeyboardButton(
            text="🆕 Что нового",
            callback_data="show_updates"
        )]
    ])
    
    await message.answer(about_text, reply_markup=keyboard, parse_mode="Markdown")


@router.message(Command("privacy"))
async def cmd_privacy(message: types.Message):
    """Explain privacy and data handling."""
    privacy_text = (
        "🔒 *Данные и приватность*\n\n"
        "По умолчанию твои записи, цели, Пульс, колесо баланса и недельные отражения *приватны*.\n\n"
        "Они нужны, чтобы работали:\n"
        "• история\n"
        "• динамика\n"
        "• цели\n"
        "• недельные отражения\n"
        "• личный кабинет\n\n"
        "⚠️ Приложение *не является медицинской или психологической помощью*, не ставит диагнозы и не заменяет специалиста.\n\n"
        "Если появится функция «Круг поддержки», публикация туда будет только вручную и только после твоего явного выбора. "
        "По умолчанию ничего не публикуется.\n\n"
        "Во время закрытой беты данные могут использоваться для улучшения продукта и исправления ошибок.\n\n"
        "Ты можешь попросить удалить свои данные через /feedback."
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📝 Открыть приложение",
            web_app=types.WebAppInfo(url=get_mini_app_url("/"))
        )]
    ])
    
    await message.answer(privacy_text, reply_markup=keyboard, parse_mode="Markdown")


@router.message(Command("updates"))
async def cmd_updates(message: types.Message):
    """Show latest updates."""
    updates_text = (
        "🆕 *Что нового*\n\n"
        "Здесь будет история обновлений mini app: новые функции, исправления, улучшения интерфейса и планы на ближайшие версии.\n\n"
        "*Последние изменения:*\n"
        "• добавлен Пульс дня с ползунками 0-10\n"
        "• добавлены текстовые поля для тела, инсайта, благодарности\n"
        "• добавлены цели и «жизнь мечты»\n"
        "• добавлена динамика недели\n"
        "• добавлено мягкое возвращение после паузы\n"
        "• добавлены недельные AI-отражения (тестовый режим)\n"
        "• добавлено колесо баланса жизни\n\n"
        "*В разработке:*\n"
        "• голосовой ввод (временно отключен)\n"
        "• Круг поддержки\n"
        "• улучшенная приватность и экспорт данных"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📋 История изменений",
            callback_data="show_changelog"
        )],
        [InlineKeyboardButton(
            text="🗺 Что планируется",
            callback_data="show_roadmap"
        )],
        [InlineKeyboardButton(
            text="💡 Предложить идею",
            callback_data="feedback_idea"
        )]
    ])
    
    await message.answer(updates_text, reply_markup=keyboard, parse_mode="Markdown")


@router.message(Command("roadmap"))
async def cmd_roadmap(message: types.Message):
    """Show planned features."""
    roadmap_text = (
        "🗺 *Что планируется дальше*\n\n"
        "*Ближайшие направления:*\n\n"
        "1️⃣ *Колесо баланса жизни* ✅ Готово\n"
        "Срез по сферам жизни и обновление раз в 2 недели.\n\n"
        "2️⃣ *Круг поддержки* 🔄 В разработке\n"
        "Возможность по желанию вынести мысль, цель или вопрос в общее пространство и получить поддержку.\n\n"
        "3️⃣ *Голосовой ввод* ⏸️ Приостановлен\n"
        "Можно будет надиктовать Пульс или дневниковую запись. Пока отладим стабильность.\n\n"
        "4️⃣ *Улучшение недельных отражений*\n"
        "Более точная связь между Пульсом, целями и состоянием.\n\n"
        "5️⃣ *Приватность и экспорт*\n"
        "Более удобное удаление и экспорт своих данных.\n\n"
        "Если тебе хочется предложить идею — напиши через /feedback."
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="💡 Предложить идею",
            callback_data="feedback_idea"
        )],
        [InlineKeyboardButton(
            text="📝 Открыть приложение",
            web_app=types.WebAppInfo(url=get_mini_app_url("/"))
        )]
    ])
    
    await message.answer(roadmap_text, reply_markup=keyboard, parse_mode="Markdown")


@router.message(Command("changelog"))
async def cmd_changelog(message: types.Message):
    """Show version history."""
    changelog_text = (
        "📋 *История изменений*\n\n"
        "*v0.6 — Информационный центр*\n"
        "• добавлены команды /help, /about, /privacy\n"
        "• добавлены команды /updates, /roadmap, /changelog\n"
        "• обновлено стартовое сообщение с кнопками\n"
        "• добавлена страница обратной связи в Mini App\n\n"
        "*v0.5 — Beta preparation*\n"
        "• добавлены beta-disclaimer\n"
        "• добавлена production конфигурация\n"
        "• добавлены ползунки вместо кнопок для оценок\n\n"
        "*v0.4 — Weekly Reflection*\n"
        "• добавлено недельное отражение\n"
        "• добавлен placeholder без AI-ключа\n"
        "• результат сохраняется в базу\n\n"
        "*v0.3 — Soft Return*\n"
        "• добавлены состояния возвращения\n"
        "• приложение мягко встречает после паузы\n\n"
        "*v0.2 — Goals*\n"
        "• добавлены цели на месяц, год, 3 года, 5 лет\n"
        "• добавлена «жизнь мечты»\n\n"
        "*v0.1 — Pulse*\n"
        "• добавлен Пульс дня\n"
        "• добавлена история\n"
        "• добавлена динамика недели"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🆕 Что нового",
            callback_data="show_updates"
        )],
        [InlineKeyboardButton(
            text="🗺 Что планируется",
            callback_data="show_roadmap"
        )]
    ])
    
    await message.answer(changelog_text, reply_markup=keyboard, parse_mode="Markdown")


@router.message(Command("feedback"))
async def cmd_feedback(message: types.Message):
    """Prompt user to send feedback."""
    feedback_text = (
        "💬 *Обратная связь*\n\n"
        "Напиши сюда любое сообщение:\n"
        "• что сломалось\n"
        "• что непонятно\n"
        "• чего не хватает\n"
        "• какую идею хочется предложить\n"
        "• что понравилось\n\n"
        "Можно коротко. Я сохраню это как обратную связь по бете.\n\n"
        "Или открой Mini App и нажми «💬 Оставить обратную связь» на главной."
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📝 Открыть приложение",
            web_app=types.WebAppInfo(url=get_mini_app_url("/"))
        )]
    ])
    
    await message.answer(feedback_text, reply_markup=keyboard, parse_mode="Markdown")


# Callback handlers for inline buttons
@router.callback_query(lambda c: c.data == "show_help")
async def on_show_help(callback: types.CallbackQuery):
    """Show help when callback button pressed."""
    await callback.message.answer(
        "📖 *Как пользоваться*\n\n"
        "Главный сценарий простой:\n\n"
        "1️⃣ *Пульс дня*\n"
        "Отмечаешь настроение, энергию, тревогу, короткий инсайт и один маленький фокус на завтра.\n\n"
        "2️⃣ *Динамика*\n"
        "Когда накопится несколько записей, можно смотреть, как меняется состояние.\n\n"
        "3️⃣ *Цели и жизнь мечты*\n"
        "Можно формулировать ориентиры на месяц, год, 3 года, 5 лет.\n\n"
        "4️⃣ *Колесо баланса*\n"
        "Срез текущей жизни по сферам.\n\n"
        "5️⃣ *Недельное отражение*\n"
        "Мягкое подсвечивание повторяющихся тем.\n\n"
        "Здесь нет оценок, наказаний и давления. Пропуски нормальны.",
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "show_updates")
async def on_show_updates(callback: types.CallbackQuery):
    """Show updates when callback button pressed."""
    await cmd_updates(callback.message)
    await callback.answer()


@router.callback_query(lambda c: c.data == "show_privacy")
async def on_show_privacy(callback: types.CallbackQuery):
    """Show privacy when callback button pressed."""
    await cmd_privacy(callback.message)
    await callback.answer()


@router.callback_query(lambda c: c.data == "show_changelog")
async def on_show_changelog(callback: types.CallbackQuery):
    """Show changelog when callback button pressed."""
    await cmd_changelog(callback.message)
    await callback.answer()


@router.callback_query(lambda c: c.data == "show_roadmap")
async def on_show_roadmap(callback: types.CallbackQuery):
    """Show roadmap when callback button pressed."""
    await cmd_roadmap(callback.message)
    await callback.answer()


@router.callback_query(lambda c: c.data == "show_feedback")
async def on_show_feedback(callback: types.CallbackQuery):
    """Show feedback prompt when callback button pressed."""
    await cmd_feedback(callback.message)
    await callback.answer()


@router.callback_query(lambda c: c.data in ["feedback_prompt", "feedback_idea"])
async def on_feedback_prompt(callback: types.CallbackQuery):
    """Show feedback prompt."""
    await cmd_feedback(callback.message)
    await callback.answer()
