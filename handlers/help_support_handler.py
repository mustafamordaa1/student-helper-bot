from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from config import CONNECT_TELEGRAM_USERNAME
from utils.faq_management import get_faq_categories, get_faqs_by_category
from utils.subscription_management import check_subscription


async def help_support_handler(update: Update, context: CallbackContext):
    """Handles the 'المساعدة والدعم' command."""

    if not await check_subscription(update, context):
        return

    # Add the support account button
    support_button = InlineKeyboardButton(
        "تواصل مع الدعم", url=CONNECT_TELEGRAM_USERNAME
    )
    keyboard = InlineKeyboardMarkup([[support_button]])

    await update.message.reply_text(
        "سنعرض لك مجموعة من الأسئلة الشائعة, وإذا لم تجد إجابة لسؤالك، يمكنك التواصل مع الدعم عبر الرابط أدناه:",
        reply_markup=keyboard,
    )

    user_context = context.user_data.get("current_section")  # Get user context

    if user_context == "tests":
        initial_category = "أسئلة متعلقة بالاختبارات"
        await display_initial_message_and_support(update, context, initial_category)
    elif user_context == "level_determination":
        initial_category = "أسئلة بتحديد المستوى"
        await display_initial_message_and_support(update, context, initial_category)
    elif user_context == "settings":
        initial_category = "أسئلة متعلقة بالإعدادات"
        await display_initial_message_and_support(update, context, initial_category)
    elif user_context == "traditional_learning":
        initial_category = "أسئلة متعلقة بالطريقة التقليدية"
        await display_initial_message_and_support(update, context, initial_category)
    elif user_context == "conversation_learning":
        initial_category = "أسئلة متعلقة بالطريقة المحادثة"
        await display_initial_message_and_support(update, context, initial_category)
    elif user_context == "tips_and_strategies":
        initial_category = "أسئلة متعلقة بالنصائح والاستراتيجيات"
        await display_initial_message_and_support(update, context, initial_category)
    elif user_context == "statistics":
        initial_category = "أسئلة متعلقة بالإحصائيات"
        await display_initial_message_and_support(update, context, initial_category)
    elif user_context == "subscription":
        initial_category = "أسئلة متعلقة بالاشتراك"
        await display_initial_message_and_support(update, context, initial_category)
    elif user_context == "rewards":
        initial_category = "أسئلة متعلقة بالمكافآت"
        await display_initial_message_and_support(update, context, initial_category)
    else:
        # Default to general category selection
        await display_faq_categories(update, context)


async def display_initial_message_and_support(
    update: Update, context: CallbackContext, initial_category: str
):
    """Displays the initial FAQ message and support button."""

    await display_faqs_for_category(update, context, initial_category)


async def display_faq_categories(update: Update, context: CallbackContext):
    """Displays the main FAQ categories to the user."""
    categories = await get_faq_categories()
    keyboard = []
    for index, category in enumerate(categories):
        # Use the row index as callback_data
        keyboard.append(
            [InlineKeyboardButton(category, callback_data=f"faq_category_{index}")]
        )

    await update.message.reply_text(
        "اختر فئة من الأسئلة الشائعة:", reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def display_faqs_for_category(
    update: Update, context: CallbackContext, category: str
):
    """Displays the FAQs for a specific category."""
    try:
        faqs = await get_faqs_by_category(category)

        if not faqs:
            await update.message.reply_text(
                f"لا توجد أسئلة شائعة في فئة '{category}' حاليًا."
            )
            return

        keyboard = []
        for question, _, question_id in faqs:
            callback_data = f"faq_question_{question_id}"
            keyboard.append(
                [InlineKeyboardButton(question, callback_data=callback_data)]
            )

        keyboard.append(
            [InlineKeyboardButton("الرجوع للخلف", callback_data="handle_faq")]
        )  # Go back to category selection

        await update.message.reply_text(
            f"الأسئلة الشائعة في فئة '{category}':",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    except Exception as e:
        print(f"Error in display_faqs_for_category: {e}")  # Log the error
        await update.message.reply_text(
            "حدث خطأ أثناء جلب الأسئلة الشائعة. يرجى المحاولة مرة أخرى لاحقًا."
        )
