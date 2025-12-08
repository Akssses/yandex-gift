import logging
import os
import django
from asgiref.sync import sync_to_async
from django.conf import settings
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# Инициализация Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from bot.models import TelegramUser

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния диалога
WAITING_FOR_STACK = 'waiting_for_stack'
WAITING_FOR_COUNTRY = 'waiting_for_country'
WAITING_FOR_CITY = 'waiting_for_city'


# Асинхронные обертки для работы с БД
@sync_to_async
def get_user_by_telegram_id(telegram_id):
    return TelegramUser.objects.filter(telegram_id=telegram_id).first()


@sync_to_async
def get_user_by_username(username):
    return TelegramUser.objects.filter(username=username).first()


@sync_to_async
def get_user_by_name(first_name, last_name):
    return TelegramUser.objects.filter(
        first_name=first_name,
        last_name=last_name
    ).first()


@sync_to_async
def get_user_by_id(user_id):
    try:
        return TelegramUser.objects.get(id=user_id)
    except TelegramUser.DoesNotExist:
        return None


@sync_to_async
def save_user(telegram_user):
    telegram_user.save()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    
    logger.info(f"User {user.id} (@{user.username}) started the bot")
    
    try:
        # Ищем пользователя по telegram_id или username
        telegram_user = await get_user_by_telegram_id(user.id)
        logger.info(f"Search by telegram_id {user.id}: {telegram_user}")
        
        if not telegram_user:
            # Пробуем найти по username (если есть)
            if user.username:
                telegram_user = await get_user_by_username(user.username)
                logger.info(f"Search by username @{user.username}: {telegram_user}")
                if telegram_user:
                    # Обновляем telegram_id если нашли по username
                    telegram_user.telegram_id = user.id
                    await save_user(telegram_user)
                    logger.info(f"Updated telegram_id for user {telegram_user.id}")
        
        # Если все еще не нашли, пробуем найти по имени и фамилии
        if not telegram_user and user.first_name and user.last_name:
            telegram_user = await get_user_by_name(user.first_name, user.last_name)
            logger.info(f"Search by name {user.first_name} {user.last_name}: {telegram_user}")
            if telegram_user and not telegram_user.telegram_id:
                # Обновляем telegram_id если нашли по имени и telegram_id еще не установлен
                telegram_user.telegram_id = user.id
                if user.username:
                    telegram_user.username = user.username
                await save_user(telegram_user)
                logger.info(f"Updated telegram_id and username for user {telegram_user.id}")
        
        if not telegram_user:
            # Пользователь не найден в базе
            logger.warning(f"User {user.id} (@{user.username}) not found in database")
            await update.message.reply_text(
                "К сожалению, вам недоступен этот бот. "
                "Обратитесь к администратору для получения доступа."
            )
            return
        
        # Пользователь найден - начинаем новый сценарий приветствия
        logger.info(f"User {telegram_user.id} found, starting new onboarding")

        welcome_text = (
            "Привет!\n\n"
            "Добро пожаловать в DevRel Thanks Advent — адвент-календарь для tech-амбассадоров 🎄\n\n"
            "Мы сделали этот календарь, чтобы сказать тебе большое спасибо! Спасибо, что делишься экспертизой, "
            "драйвишь инженерную культуру и поддерживаешь наши инициативы.\n\n"
            "Каждый день на протяжении 2 недель тебя ждут сюрпризы от нашей команды: от подборок и полезных материалов "
            "до классных подарков!\n\n"
            "Мы очень рады, что ты часть сообщества.\n\n"
            "DevRel-команда ❤️"
        )

        await update.message.reply_text(welcome_text)

        # ВТОРОЕ СООБЩЕНИЕ — вопрос про стек
        stack_keyboard = [
            [
                InlineKeyboardButton("backend", callback_data="stack_backend"),
                InlineKeyboardButton("frontend", callback_data="stack_frontend"),
                InlineKeyboardButton("mobile", callback_data="stack_mobile"),
            ],
            [
                InlineKeyboardButton("AI", callback_data="stack_ai"),
                InlineKeyboardButton("ML", callback_data="stack_ml"),
                InlineKeyboardButton("analytics", callback_data="stack_analytics"),
            ],
            [
                InlineKeyboardButton("product", callback_data="stack_product"),
                InlineKeyboardButton("teamlead", callback_data="stack_teamlead"),
                InlineKeyboardButton("security", callback_data="stack_security"),
            ],
            [
                InlineKeyboardButton("другое", callback_data="stack_other"),
            ],
        ]
        await update.message.reply_text(
            "1) С каким стеком ты работаешь?",
            reply_markup=InlineKeyboardMarkup(stack_keyboard),
        )

        # Устанавливаем состояние ожидания выбора стека
        context.user_data['state'] = WAITING_FOR_STACK
        context.user_data['user_id'] = telegram_user.id
        
    except Exception as e:
        logger.error(f"Error in start handler: {e}", exc_info=True)
        await update.message.reply_text(
            "Произошла ошибка. Попробуйте позже."
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    state = context.user_data.get('state')
    user_id = context.user_data.get('user_id')
    
    if state == WAITING_FOR_CITY:
        city = update.message.text.strip()
        try:
            telegram_user = await get_user_by_id(user_id)
            if not telegram_user:
                raise TelegramUser.DoesNotExist()

            # Логируем город (отдельного поля нет)
            logger.info(f"User {telegram_user.id} provided city: {city}")

            # Финальное сообщение с кнопкой открытия мини-аппы
            keyboard = [
                [
                    InlineKeyboardButton(
                        "Открыть", web_app=WebAppInfo(url=settings.MINI_APP_URL)
                    )
                ]
            ]
            await update.message.reply_text(
                "Настало время открыть первый подарок!\n\n"
                "Загляни и посмотри, что мы приготовили специально для тебя.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

            context.user_data.clear()

        except TelegramUser.DoesNotExist:
            await update.message.reply_text(
                "Произошла ошибка. Попробуйте начать заново с команды /start"
            )
            context.user_data.clear()
        except Exception as e:
            logger.error(f"Error saving city: {e}")
            await update.message.reply_text(
                "Произошла ошибка при сохранении данных. Попробуйте позже."
            )
    else:
        # Если состояние не определено, отправляем приветствие
        await start(update, context)


async def startapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /startapp для запуска мини-апп"""
    user = update.effective_user
    
    logger.info(f"User {user.id} (@{user.username}) requested startapp")
    
    try:
        # Проверяем, что пользователь есть в базе и имеет доступ
        telegram_user = await get_user_by_telegram_id(user.id)
        
        if not telegram_user:
            # Пробуем найти по username
            if user.username:
                telegram_user = await get_user_by_username(user.username)
                if telegram_user:
                    telegram_user.telegram_id = user.id
                    await save_user(telegram_user)
        
        if not telegram_user:
            await update.message.reply_text(
                "К сожалению, вам недоступен этот бот. "
                "Обратитесь к администратору для получения доступа."
            )
            return
        
        # Проверяем, что пользователь из РФ
        if not telegram_user.is_from_rf:
            await update.message.reply_text(
                "К сожалению, доступ к адвент-календарю "
                "доступен только для пользователей, работающих с территории РФ."
            )
            return
        
        # Создаем кнопку для открытия мини-аппки
        # Используем start_parameter для передачи telegram_id в мини-апп
        keyboard = [
            [
                InlineKeyboardButton(
                    "Открыть адвент-календарь",
                    web_app=WebAppInfo(
                        url=settings.MINI_APP_URL,
                        # start_parameter можно использовать для передачи данных
                        # но telegram_id уже доступен через initDataUnsafe
                    )
                )
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Нажмите кнопку ниже, чтобы открыть адвент-календарь. "
            "Заходите в него каждый день с 8 по 19 декабря и получайте подарки от Яндекса. "
            "В случае пропуска дня забрать подарок за этот день не получится :(",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error in startapp handler: {e}", exc_info=True)
        await update.message.reply_text(
            "Произошла ошибка. Попробуйте позже."
        )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик callback кнопок"""
    query = update.callback_query
    await query.answer()
    
    user_id = context.user_data.get('user_id')
    state = context.user_data.get('state')

    # Шаг 1: выбор стека
    if state == WAITING_FOR_STACK and query.data.startswith("stack_"):
        stack = query.data.replace("stack_", "")
        try:
            telegram_user = await get_user_by_id(user_id)
            if not telegram_user:
                raise TelegramUser.DoesNotExist()

            # Сохраняем стек в поле position (как ближайшее по смыслу)
            telegram_user.position = stack
            await save_user(telegram_user)

            # Переходим к вопросу о стране
            country_keyboard = [
                [
                    InlineKeyboardButton("Россия", callback_data="country_russia"),
                    InlineKeyboardButton("Сербия", callback_data="country_serbia"),
                ],
                [
                    InlineKeyboardButton("Беларусь", callback_data="country_belarus"),
                    InlineKeyboardButton("Казахстан", callback_data="country_kazakhstan"),
                ],
                [
                    InlineKeyboardButton("Узбекистан", callback_data="country_uzbekistan"),
                    InlineKeyboardButton("Другая страна", callback_data="country_other"),
                ],
            ]
            await query.edit_message_text(
                "2) В какой стране ты находишься?",
                reply_markup=InlineKeyboardMarkup(country_keyboard),
            )

            context.user_data['state'] = WAITING_FOR_COUNTRY
            context.user_data['stack'] = stack

        except TelegramUser.DoesNotExist:
            await query.edit_message_text(
                "Произошла ошибка. Попробуйте начать заново с команды /start"
            )
            context.user_data.clear()
        except Exception as e:
            logger.error(f"Error handling stack selection: {e}", exc_info=True)
            await query.edit_message_text(
                "Произошла ошибка. Попробуйте позже."
            )
        return

    # Шаг 2: выбор страны
    if state == WAITING_FOR_COUNTRY and query.data.startswith("country_"):
        country = query.data.replace("country_", "")
        try:
            telegram_user = await get_user_by_id(user_id)
            if not telegram_user:
                raise TelegramUser.DoesNotExist()

            # Сохраняем страну как is_from_rf (True только если Россия)
            telegram_user.is_from_rf = country.lower() == "russia"
            await save_user(telegram_user)

            # Переходим к вопросу о городе
            await query.edit_message_text(
                "3) Укажи город, в котором ты живёшь."
            )
            context.user_data['state'] = WAITING_FOR_CITY
            context.user_data['country'] = country

        except TelegramUser.DoesNotExist:
            await query.edit_message_text(
                "Произошла ошибка. Попробуйте начать заново с команды /start"
            )
            context.user_data.clear()
        except Exception as e:
            logger.error(f"Error handling country selection: {e}", exc_info=True)
            await query.edit_message_text(
                "Произошла ошибка. Попробуйте позже."
            )
        return

    # Если состояние не совпадает, запускаем заново
    await query.edit_message_text(
        "Давайте начнем заново. Наберите /start"
    )
    context.user_data.clear()


def setup_bot():
    """Настройка и запуск бота"""
    token = settings.TELEGRAM_BOT_TOKEN
    
    application = Application.builder().token(token).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("startapp", startapp))  # Обработчик для /startapp
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    return application
