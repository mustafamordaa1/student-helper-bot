from telegram import (
    ReplyKeyboardMarkup,
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    CallbackContext,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    CommandHandler,
)

from AIModels.chatgpt import get_chatgpt_instance
from utils.question_management import (
    format_question_for_chatgpt,
    format_question_for_user,
    get_random_question,
    get_user_questions_for_review,
    update_learning_progress,
)
from utils.subscription_management import check_subscription


# Conversation states
ASK_QUESTION, PROVIDE_FEEDBACK, REVIEW_QUESTION = range(3)

chatgpt = get_chatgpt_instance()

# System message to set up the assistant's behavior
SYSTEM_MESSAGE = """
You are a helpful personal assistant for a Telegram bot. You have access to user statistics, 
frequently asked questions, and various documents. Your role is to assist users, provide advice, 
and answer questions about the bot and associated tests. Be proactive, ask clarifying questions 
when needed, and always strive to provide accurate and helpful information.
"""


async def handle_conversation_learning(update: Update, context: CallbackContext):
    
    if not await check_subscription(update, context):
        return
    context.user_data["current_section"] = "conversation_learning"
    keyboard = [
        [InlineKeyboardButton("ابدأ المحادثة 🗣️", callback_data="handle_conversation")],
        [InlineKeyboardButton("طرح الأسئلة ❔", callback_data="handle_ask_questions")],
        [InlineKeyboardButton("مراجعة الأسئلة 📝", callback_data="review_questions")],
        [InlineKeyboardButton("الرجوع للخلف 🔙", callback_data="go_back")],
    ]
    await update.callback_query.edit_message_text(
        "التعلم عبر المحادثة 📚", reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def ask_question(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    messages = await chatgpt.get_chat_history(user.id)
    context.user_data["messages"] = messages

    question_data = get_random_question()

    if not question_data:
        await update.callback_query.edit_message_text("لا توجد أسئلة متاحة حاليًا 😞.")
        return ConversationHandler.END
    await query.message.reply_text("حسنا هذا سؤال لك كيف تعتقد سيكون حله 🤔")

    context.user_data["current_question"] = question_data
    formatted_question = format_question_for_user(question_data)

    await query.edit_message_text(formatted_question)
    return PROVIDE_FEEDBACK


async def provide_feedback(update: Update, context: CallbackContext):
    user_answer = update.message.text.strip().upper()
    question_data = context.user_data["current_question"]
    correct_answer = question_data["correct_answer"].upper()

    chatgpt_prompt = (
        f"The user answered '{user_answer}' to the following question:\n"
        f"{format_question_for_chatgpt(question_data)}\n\n"
        f"The correct answer is '{correct_answer}'.\n"
        f"Please provide a clear and concise explanation of why the user's "
        f"answer is incorrect and why the correct answer is correct, using "
        f"the following explanation from the question's context:\n\n"
        f"{question_data['explanation']}\n"
        f"and also make the conversation fun and engage with the user and don't let the user know of the prompt, have a normal conversation"
    )

    await update.message.reply_text("جاري تحليل إجابتك... 🧐")  # Feedback during processing

    assistant_response = await chatgpt.chat_with_assistant(
        update.effective_user.id,
        user_message=chatgpt_prompt,
        update=update,
        context=context,
        system_message=SYSTEM_MESSAGE,
    )
    if assistant_response:
        await update.message.reply_text("هل لديك اي استفسارات لتسأل عنها؟ 🙋‍♂️")
        return PROVIDE_FEEDBACK
    else:
        await update.message.reply_text(
            "حدث خطأ أثناء معالجة طلبك. يرجى المحاولة مرة أخرى لاحقًا 😞."
        )
        return ConversationHandler.END


async def handle_ask_questions(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    await query.edit_message_text(
        f"مرحبا {user.first_name}! اسألني أي شيء تريده عن تعلم المحادثة 💬."
    )

    messages = await chatgpt.get_chat_history(user.id)
    context.user_data["messages"] = messages

    return ASK_QUESTION


async def ask_question_chatgpt(update: Update, context: CallbackContext):
    user_question = update.message.text
    await update.message.reply_text("جاري التفكير في إجابتك... 🤔")

    try:
        assistant_response = await chatgpt.chat_with_assistant(
            update.effective_user.id,
            user_question,
            update,
            context,
            system_message=SYSTEM_MESSAGE,
        )

        if assistant_response:
            await update.message.reply_text(assistant_response)
        else:
            await update.message.reply_text(
                "لم أتمكن من العثور على إجابة لسؤالك. هل يمكنك إعادة صياغته؟ 🔄"
            )
    except Exception as e:
        await update.message.reply_text(
            "حدث خطأ أثناء معالجة طلبك. يرجى المحاولة مرة أخرى لاحقًا 😞."
        )
        print(f"Error in ask_question_chatgpt: {e}")
    return ASK_QUESTION


async def review_questions(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    reviewed_questions = get_user_questions_for_review(user_id)

    if not reviewed_questions:
        await update.callback_query.edit_message_text(
            "لم تقم بمراجعة أي أسئلة حتى الآن 📝."
        )
        return

    review_text = "الأسئلة التي قمت بمراجعتها:\n"
    for i, question_data in enumerate(reviewed_questions):
        question, correct_answer, answered_correctly = question_data
        review_text += f"\nالسؤال {i+1}: {question}\n"
        review_text += f"الإجابة الصحيحة: {correct_answer}\n"
        review_text += (
            "أجبت بشكل صحيح ✅" if answered_correctly else "أجبت بشكل خاطئ ❌"
        )
        review_text += "\n"

    await update.callback_query.edit_message_text(review_text)


async def cancel_learning(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "تم إلغاء التعلم. إذا كنت بحاجة إلى أي شيء آخر، فأعلمني! 👋"
    )
    return ConversationHandler.END


conversation_learning_conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(ask_question, pattern="^handle_conversation$"),
        CallbackQueryHandler(handle_ask_questions, pattern="^handle_ask_questions$"),
    ],
    states={
        ASK_QUESTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, ask_question_chatgpt),
        ],
        PROVIDE_FEEDBACK: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, provide_feedback)
        ],
    },
    fallbacks=[CommandHandler("end_chat", cancel_learning)],
)

CONVERSATION_LEARNING_HANDLERS = {
    "conversation_learning": handle_conversation_learning,
    "review_questions": review_questions,
}