from datetime import datetime, timedelta
import logging
from telegram import (
    Update,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    CallbackContext,
    CommandHandler,
    Application,
)

from handlers.main_menu_handler import main_menu_handler
from utils.database import execute_query
from utils.user_management import save_user_data, user_exists
from .keyboards import (
    create_gender_keyboard,
    create_class_keyboard,
    create_voice_written_keyboard,
    create_yes_no_keyboard,
    create_preference_keyboard,
)
from .material import send_material
from config import WELCOMING_FOLDER, WELCOMING_MESSAGE

# Conversation states
GENDER, NAME, CLASS, VOICE_WRITTEN, QIYAS, SCORE, PREFERENCE = range(7)

logger = logging.getLogger(__name__)


async def check_user_and_route(
    update: Update, context: CallbackContext, text_when_not_exist
) -> int:
    """Checks if the user exists and routes to main menu or onboarding."""
    user = update.effective_user
    if await user_exists(user.id):
        await main_menu_handler(update, context)
        return ConversationHandler.END
    else:
        await update.message.reply_text(text_when_not_exist)
        keyboard = InlineKeyboardMarkup(create_gender_keyboard())
        await update.message.reply_text(
            "يرجى اختيار جنسك:",
            reply_markup=keyboard,
        )
        return GENDER


async def start_conversation(update: Update, context: CallbackContext) -> int:
    """Handles the /start command and routes based on user existence."""
    return await check_user_and_route(update, context, WELCOMING_MESSAGE)


async def show_main_menu(update: Update, context: CallbackContext) -> int:
    """Handles the /main_menu command and routes based on user existence."""
    return await check_user_and_route(update, context, WELCOMING_MESSAGE)


async def gender_handler(update: Update, context: CallbackContext) -> int:
    """Handles gender selection."""
    query = update.callback_query
    await query.answer()
    context.user_data["gender"] = query.data
    if query.data == "Male":
        await query.edit_message_text(
            "أهلا بكم أيها الفارس المجتهد🤴🏻، ما الاسم الذي تحب أن أناديك به؟"
        )
    elif query.data == "Female":
        await query.edit_message_text(
            "أهلا بكم أيتها الأميرة المجتهدة👸🏻، ما الاسم الذي تحبين أن أناديك به؟"
        )
    return NAME


async def name_handler(update: Update, context: CallbackContext) -> int:
    """Handles user name input."""
    context.user_data["name"] = update.message.text
    keyboard = create_class_keyboard()
    await update.message.reply_text(
        "ما هو الصف الذي تدرس فيه؟", reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CLASS


async def class_handler(update: Update, context: CallbackContext) -> int:
    """Handles class/grade selection."""
    query = update.callback_query
    await query.answer()
    context.user_data["class"] = query.data

    keyboard = create_voice_written_keyboard()
    await query.edit_message_text(
        "ما هو الأفضل بالنسبة لك، الإجابات الصوتية أو المكتوبة؟",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return VOICE_WRITTEN


async def voice_written_handler(update: Update, context: CallbackContext) -> int:
    """Handles preferred interaction mode selection."""
    query = update.callback_query
    await query.answer()
    context.user_data["voice_written"] = query.data

    keyboard = create_yes_no_keyboard()
    await query.edit_message_text(
        "هل سبق لك أن قمت بقياس قياس قبل ذلك؟",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return QIYAS


async def qiyas_handler(update: Update, context: CallbackContext) -> int:
    """Handles previous Qiyas experience."""
    query = update.callback_query
    await query.answer()
    context.user_data["qiyas"] = query.data

    if query.data == "Yes":
        gender = context.user_data.get("gender")  # Get the user's gender
        if gender == "Male":
            await query.edit_message_text(
                "حتى أرسم لك أفضل خطة للمذاكرة، أريد أن أعرف: ما هي أعلى درجة لك في اختبار القدرات؟ 🫣 (أدخل رقمًا، وإن كنت لا تريد الإفصاح، فاكتب 65 لأعاملك حسب متوسط درجات الطلاب☺️)"
            )
        elif gender == "Female":
            await query.edit_message_text(
                "حتى أرسم لكِ أفضل خطة للمذاكرة، أريد أن أعرف: ما هي أعلى درجة لكِ في اختبار القدرات؟ 🫣 (أدخلي رقمًا، وإن كنت لا تريدين الإفصاح، فاكتبي 65 لأعاملك حسب متوسط درجات الطالبات في الاختبار☺️)"
            )
        else:
            await query.edit_message_text(
                "حتى أرسم لك أفضل خطة للمذاكرة، أريد أن أعرف: ما هي أعلى درجة لك في اختبار القدرات؟ 🫣 (أدخل رقمًا، وإن كنت لا تريد الإفصاح، فاكتب 65 لأعاملك حسب متوسط درجات الطلاب☺️)"
            )
        return SCORE
    else:
        context.user_data["score"] = 65  # Default score
        return await preference_selection(query, context)


async def score_handler(update: Update, context: CallbackContext) -> int:
    """Handles user's Qiyas score input."""
    try:
        score = int(update.message.text)
        if not (40 <= score <= 100):  # Changed validation range
            raise ValueError
        context.user_data["score"] = score
    except ValueError:
        await update.message.reply_text("يرجى إدخال رقم صحيح بين 40 و 100 لدرجاتك.")
        return SCORE

    return await preference_selection(update, context)


async def preference_selection(update_or_query, context: CallbackContext) -> int:
    """Asks the user for their preferred explanation format."""
    keyboard = create_preference_keyboard()

    if isinstance(update_or_query, Update):
        await update_or_query.message.reply_text(
            "كيف تحب أن نشرح لك طريقة استعمال البوت؟😊",  # Changed the text
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    else:
        await update_or_query.edit_message_text(
            "كيف تحب أن نشرح لك طريقة استعمال البوت؟😊",  # Changed the text
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    return PREFERENCE


async def handle_preference_selection(update: Update, context: CallbackContext) -> int:
    user_data = update.effective_user
    if await user_exists(user_data.id):
        query = update.callback_query
        await query.answer()
        selected_preference = query.data.lower()

        try:
            await send_material(query, context, selected_preference, WELCOMING_FOLDER)
        except Exception as e:
            logger.error(f"Error sending material: {e}")
            await query.message.reply_text(
                "حدث خطأ أثناء إرسال المواد. يرجى المحاولة لاحقًا."
            )
    else:
        query = update.callback_query
        await save_user_data(user_data, context, user_data.id)
        # await update.effective_message.reply_text("قد تم حفظ بياناتك.")

        # Grant the user a free one-hour trial
        subscription_end_time = (datetime.now() + timedelta(hours=1)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        execute_query(
            "UPDATE users SET subscription_end_time = ? ,type_of_last_subscription = ? WHERE telegram_id = ?",
            (subscription_end_time, "تجربة مجانية الساعية", update.effective_user.id),
        )

        # await update.effective_message.reply_text(
        #     "تم اعطائك ساعة مجانا لتجربني مجانا. يمكنك التجريب كما تشاء.\n"
        #     "ويمكنك تمديد الاشتراك بتجربة مجانية من خلال زر الاشتراك في القائمة الرئيسية."
        # )

        await query.answer()
        selected_preference = query.data.lower()

        try:
            await send_material(query, context, selected_preference, WELCOMING_FOLDER)
        except Exception as e:
            logger.error(f"Error sending material: {e}")
            await query.message.reply_text(
                "حدث خطأ أثناء إرسال المواد. يرجى المحاولة لاحقًا."
            )

        # Provide main buttons after sending material
        await main_menu_handler(query, context)
        return ConversationHandler.END


def register_converstaion_handlers(application: Application):
    application.add_handler(
        ConversationHandler(
            entry_points=[
                CommandHandler("start", start_conversation),
                CommandHandler("main_menu", show_main_menu),
            ],
            states={
                GENDER: [CallbackQueryHandler(gender_handler)],
                NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_handler)],
                CLASS: [CallbackQueryHandler(class_handler)],
                VOICE_WRITTEN: [CallbackQueryHandler(voice_written_handler)],
                QIYAS: [CallbackQueryHandler(qiyas_handler)],
                SCORE: [MessageHandler(filters.TEXT & ~filters.COMMAND, score_handler)],
                PREFERENCE: [CallbackQueryHandler(handle_preference_selection)],
            },
            fallbacks=[],
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            handle_preference_selection, pattern="^(Text|Audio|Video)$"
        )
    )
