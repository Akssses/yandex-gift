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
WAITING_FOR_POSITION = 'waiting_for_position'
WAITING_FOR_RF = 'waiting_for_rf'


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
        
        # Пользователь найден - начинаем диалог
        logger.info(f"User {telegram_user.id} found, starting dialog")
        await update.message.reply_text(
            "Привет! Это новогодний адвент-календарь для амбассадоров Яндекса."
        )
        
        # Запрашиваем должность
        await update.message.reply_text(
            "Пожалуйста, введите вашу текущую должность (senior backend developer – в таком формате):"
        )
        
        # Устанавливаем состояние ожидания должности
        context.user_data['state'] = WAITING_FOR_POSITION
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
    
    if state == WAITING_FOR_POSITION:
        # Сохраняем должность
        position = update.message.text
        
        try:
            telegram_user = await get_user_by_id(user_id)
            if not telegram_user:
                raise TelegramUser.DoesNotExist()
            telegram_user.position = position
            await save_user(telegram_user)
            
            # Создаем клавиатуру с кнопками для выбора территории
            keyboard = [
                [
                    InlineKeyboardButton("Из РФ", callback_data='rf_yes'),
                    InlineKeyboardButton("Не из РФ", callback_data='rf_no')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "Спасибо! Скажите, вы сейчас работаете с территории РФ?",
                reply_markup=reply_markup
            )
            
            # Меняем состояние на ожидание выбора территории
            context.user_data['state'] = WAITING_FOR_RF
            
        except TelegramUser.DoesNotExist:
            await update.message.reply_text(
                "Произошла ошибка. Попробуйте начать заново с команды /start"
            )
            context.user_data.clear()
        except Exception as e:
            logger.error(f"Error saving position: {e}")
            await update.message.reply_text(
                "Произошла ошибка при сохранении данных. Попробуйте позже."
            )
    
    else:
        # Если состояние не определено, отправляем приветствие
        await start(update, context)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик callback кнопок"""
    query = update.callback_query
    await query.answer()
    
    user_id = context.user_data.get('user_id')
    
    if query.data in ['rf_yes', 'rf_no']:
        try:
            telegram_user = await get_user_by_id(user_id)
            if not telegram_user:
                raise TelegramUser.DoesNotExist()
            
            if query.data == 'rf_yes':
                telegram_user.is_from_rf = True
                await save_user(telegram_user)
                
                # Создаем кнопку для открытия мини-аппки
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Открыть",
                            web_app=WebAppInfo(url=settings.MINI_APP_URL)
                        )
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    "Спасибо! Нажмите кнопку ниже, чтобы открыть адвент-календарь. "
                    "Заходите в него каждый день с 8 по 19 декабря и получайте подарки от Яндекса. "
                    "В случае пропуска дня забрать подарок за этот день не получится :(",
                    reply_markup=reply_markup
                )
                
            else:  # rf_no
                telegram_user.is_from_rf = False
                await save_user(telegram_user)
                
                await query.edit_message_text(
                    "Спасибо за информацию! К сожалению, доступ к адвент-календарю "
                    "доступен только для пользователей, работающих с территории РФ."
                )
            
            # Очищаем состояние
            context.user_data.clear()
            
        except TelegramUser.DoesNotExist:
            await query.edit_message_text(
                "Произошла ошибка. Попробуйте начать заново с команды /start"
            )
            context.user_data.clear()
        except Exception as e:
            logger.error(f"Error handling callback: {e}")
            await query.edit_message_text(
                "Произошла ошибка. Попробуйте позже."
            )


def setup_bot():
    """Настройка и запуск бота"""
    token = settings.TELEGRAM_BOT_TOKEN
    
    application = Application.builder().token(token).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    return application
