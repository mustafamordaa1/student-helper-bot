from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CallbackContext,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from AIModels.chatgpt import get_chatgpt_instance

# Conversation states
CHATTING = 0
CONFIRM_CLEAR = 1
CONTNUE_CHATTING = 2

# System message to set up the assistant's behavior
SYSTEM_MESSAGE = """
You are a helpful personal assistant for a Telegram bot. You have access to user statistics, 
frequently asked questions, and various documents. Your role is to assist users, provide advice, 
and answer questions about the bot and associated tests. Be proactive, ask clarifying questions 
when needed, and always strive to provide accurate and helpful information.
"""

chatgpt = get_chatgpt_instance()


async def start_chat(update: Update, context: CallbackContext) -> int:
    """Handles the '/personal_assistant_chat' command and loads chat history."""
    user = update.effective_user
    await update.message.reply_text(
        f"مرحبا {user.first_name}! أنا مساعدك الشخصي. كيف يمكنني مساعدتك اليوم؟"
    )
    messages = await chatgpt.get_chat_history(user.id)
    context.user_data["messages"] = messages
    return CHATTING


async def chat(update: Update, context: CallbackContext) -> int:
    user_message = update.message.text

    assistant_response = await chatgpt.chat_with_assistant(
        update.effective_user.id,
        user_message,
        update,
        context,
        system_message=SYSTEM_MESSAGE,
    )

    if assistant_response:
        return CHATTING
    else:
        await update.message.reply_text(
            "حدث خطأ أثناء معالجة طلبك. يرجى المحاولة مرة أخرى لاحقًا."
        )
        return ConversationHandler.END


async def end_chat(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "شكرا لك على الدردشة معي. إذا احتجت إلى مساعدة مرة أخرى، فقط ابدأ دردشة جديدة!"
    )
    return ConversationHandler.END


async def clear_chat_history(update: Update, context: CallbackContext) -> int:
    """Asks the user for confirmation before clearing the chat history."""
    await update.message.reply_text(
        "هل أنت متأكد أنك تريد مسح سجل الدردشة؟",
        reply_markup=ReplyKeyboardMarkup(
            [["نعم", "لا"]], resize_keyboard=True, one_time_keyboard=True
        ),
    )
    return CONFIRM_CLEAR


async def confirm_clear_history(update: Update, context: CallbackContext) -> int:
    """Handles the user's confirmation to clear the history."""
    user_response = update.message.text
    print(user_response)
    if user_response == "نعم":
        user_id = update.effective_user.id
        await chatgpt.clear_user_history(user_id)
        context.user_data["messages"] = [{"role": "system", "content": SYSTEM_MESSAGE}]
        await update.message.reply_text(
            "تم مسح سجل الدردشة الخاص بك."
        )
        await update.message.reply_text(
            "هل تريد بدء محادثة جديدة؟",
            reply_markup=ReplyKeyboardMarkup(
                [["نعم", "لا"]], resize_keyboard=True, one_time_keyboard=True
            ),
        )
        return CONTNUE_CHATTING
    else:
        await update.message.reply_text(
            "لم يتم مسح سجل الدردشة.", reply_markup=ReplyKeyboardRemove()
        )
        return CHATTING


async def continue_chatting(update: Update, context: CallbackContext) -> int:
    user_response = update.message.text
    if user_response.lower() == "نعم":
        await update.message.reply_text(
            "حسنا , كيف يمكنني مساعدتك؟", reply_markup=ReplyKeyboardRemove()
        )
        return CHATTING
    else:
        await update.message.reply_text(
            "حسنا, وداعا!", reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END


personal_assistant_handler = ConversationHandler(
    entry_points=[
        CommandHandler("personal_assistant_chat", start_chat),
        CommandHandler("clear_history", clear_chat_history),
    ],
    states={
        CHATTING: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, chat),
            CommandHandler("clear_history", clear_chat_history),
        ],
        CONFIRM_CLEAR: [
            MessageHandler(filters.TEXT, confirm_clear_history),
        ],
        CONTNUE_CHATTING: [
            MessageHandler(filters.TEXT, continue_chatting),
        ],
    },
    fallbacks=[CommandHandler("end_chat", end_chat)],
)
