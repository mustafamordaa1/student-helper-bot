"""
Defines the handlers for various bot interactions.

This file contains functions that handle different user interactions with the bot, including:
- Responding to the `/start` command.
- Managing the main menu.
- Handling general advice interactions.
- Handling solution strategies interactions.
- Handling specific advice requests (not fully implemented).
- Handling back buttons to navigate between menus.
"""

from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TimedOut

from excel_handler import ExcelHandler
from general_advice_model import GeneralAdviceModel
from solution_strategies_model import SolutionStrategiesModel
from keyboards import (
    get_start_keyboard,
    get_main_menu_keyboard,
    get_general_advice_keyboard,
    get_general_advice_questions_keyboard,
    get_solution_strategies_keyboard,
    get_solution_strategies_questions_keyboard,
    get_format_selection_keyboard,
)
from constants import (
    GENERAL_ADVICE_FILE,
    SOLUTION_STRATEGIES_FILE,
    STATE_START,
    STATE_MAIN_MENU,
    STATE_GENERAL_ADVICE,
    STATE_SOLUTION_STRATEGIES,
    STATE_SPECIFIC_ADVICE,
)

# --- Global Variables ---
user_states = {}


# --- Handlers ---
async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command."""
    user_states[update.effective_user.id] = STATE_START
    await update.message.reply_text(
        "أهلا بك في هذا البوت. قم باختيار الخيار الذي تريده",
        reply_markup=get_start_keyboard(),
    )

async def handle_back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles going back to the start menu."""
    query = update.callback_query
    await query.answer()
    user_states[update.effective_user.id] = STATE_START
    await query.edit_message_text(
        text="أهلا بك في هذا البوت. قم باختيار الخيار الذي تريده",
        reply_markup=get_start_keyboard(),
    )

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the main menu options."""
    query = update.callback_query
    await query.answer()
    user_states[update.effective_user.id] = STATE_MAIN_MENU
    await query.edit_message_text(
        text="هذا هو قسم النصائح والاستراتيجيات. بماذا يمكنني أن أساعدك؟",
        reply_markup=get_main_menu_keyboard(),
    )


async def handle_general_advice(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handles general advice selection and displays sheet names."""
    query = update.callback_query
    await query.answer()
    user_states[update.effective_user.id] = STATE_GENERAL_ADVICE

    general_advice_excel = ExcelHandler(GENERAL_ADVICE_FILE)
    general_advice_model = GeneralAdviceModel(general_advice_excel)

    await query.edit_message_text(
        text="هنا ستجد مجموعة من النصائح الهامة لمساعدتك في التحضير لاختبار القدرات. تأكد من قراءتها بعناية للحصول على أفضل النتائج.",
        reply_markup=get_general_advice_keyboard(general_advice_model),
    )


async def handle_general_advice_sheet(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handles sheet selection in general advice and displays questions."""
    query = update.callback_query
    await query.answer()
    sheet_name = query.data

    general_advice_excel = ExcelHandler(GENERAL_ADVICE_FILE)
    general_advice_model = GeneralAdviceModel(general_advice_excel)
    questions = general_advice_model.get_sheet_questions(sheet_name)

    user_states[update.effective_user.id] = f"{STATE_GENERAL_ADVICE}_sheet_{sheet_name}"

    await query.edit_message_text(
        text="اختر سؤالًا:",
        reply_markup=get_general_advice_questions_keyboard(questions, sheet_name),
    )


async def handle_general_advice_question(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handles question selection in general advice and sends the answer."""
    query = update.callback_query
    await query.answer()
    _, _, question_index, sheet_name = query.data.split("_", 3)
    question_index = int(question_index)

    general_advice_excel = ExcelHandler(GENERAL_ADVICE_FILE)
    general_advice_model = GeneralAdviceModel(general_advice_excel)
    answer = general_advice_model.get_answer(sheet_name, question_index)

    await query.message.reply_text(text=answer)


# --- Solution Strategies Handlers ---
async def handle_solution_strategies(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handles solution strategies selection and displays sheet names."""
    query = update.callback_query
    await query.answer()
    user_states[update.effective_user.id] = STATE_SOLUTION_STRATEGIES

    solution_strategies_excel = ExcelHandler(SOLUTION_STRATEGIES_FILE)
    solution_strategies_model = SolutionStrategiesModel(solution_strategies_excel)

    await query.edit_message_text(
        text="تعرف على استراتيجيات الحل المختلفة لكل أنواع الأقسام والأسئلة. سأقدم لك تقنيات تساعدك على التعامل مع مختلف التحديات في الاختبار.",
        reply_markup=get_solution_strategies_keyboard(solution_strategies_model),
    )


async def handle_solution_strategies_sheet(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handles sheet selection in solution strategies and displays questions."""
    query = update.callback_query
    await query.answer()
    _, _, sheet_name = query.data.split("_", 2)

    solution_strategies_excel = ExcelHandler(SOLUTION_STRATEGIES_FILE)
    solution_strategies_model = SolutionStrategiesModel(solution_strategies_excel)
    questions = solution_strategies_model.get_sheet_questions(sheet_name)

    user_states[update.effective_user.id] = (
        f"{STATE_SOLUTION_STRATEGIES}_sheet_{sheet_name}"
    )

    await query.edit_message_text(
        text="اختر سؤالًا:",
        reply_markup=get_solution_strategies_questions_keyboard(questions, sheet_name),
    )


async def handle_solution_strategies_question(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handles question selection and asks for the preferred format."""
    query = update.callback_query
    await query.answer()
    _, _, question_index, sheet_name = query.data.split("_", 3)
    question_index = int(question_index)

    # Store the question index and sheet name in the user's context
    context.user_data["question_index"] = question_index
    context.user_data["sheet_name"] = sheet_name

    user_states[update.effective_user.id] = (
        f"{STATE_SOLUTION_STRATEGIES}_questions_{sheet_name}"
    )

    await query.edit_message_text(
        text="كيف تريد التوضيح؟", reply_markup=get_format_selection_keyboard()
    )

async def handle_solution_format(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handles the format selection and sends the appropriate file."""
    query = update.callback_query
    await query.answer()
    file_format = query.data.split("_")[1]
    question_index = context.user_data.get("question_index")
    sheet_name = context.user_data.get("sheet_name")

    solution_strategies_excel = ExcelHandler(SOLUTION_STRATEGIES_FILE)
    solution_strategies_model = SolutionStrategiesModel(solution_strategies_excel)
    file_path = solution_strategies_model.get_file_path(
        sheet_name, question_index, file_format
    )

    if file_path:
        try:
            if file_format == "video":
                await context.bot.send_video(
                    chat_id=query.message.chat_id, video=open(file_path, "rb")
                )
            elif file_format == "audio":
                await context.bot.send_audio(
                    chat_id=query.message.chat_id, audio=open(file_path, "rb")
                )
            elif file_format == "text":
                with open(file_path, "r", encoding="utf-8") as f:
                    text_content = f.read()
                await context.bot.send_message(
                    chat_id=query.message.chat_id, text=text_content
                )
            elif file_format == "pdf":
                await context.bot.send_document(
                    chat_id=query.message.chat_id, document=open(file_path, "rb")
                )

            # Optionally, you can send a confirmation message after the file is sent
            await query.message.reply_text(text=f"✅ تم إرسال {file_format} بنجاح!")
        except TimedOut as e:
            await query.message.reply_text(text="⏳ ...سيجهز  الملف في اي لحظة, يرجى الانتظار")
        except Exception as e:
            await query.edit_message_text(text=f"❌ حدث خطأ أثناء إرسال الملف: {e}")
    else:
        await query.edit_message_text(text="❌ لم يتم العثور على الملف.")

async def handle_specific_advice(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handles the request for specific advice (not fully implemented)."""
    query = update.callback_query
    await query.answer()
    user_states[update.effective_user.id] = STATE_SPECIFIC_ADVICE
    await query.edit_message_text(text="هذه الخاصية قيد التطوير. يرجى المحاولة لاحقاً.")


async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles going back to the previous menu."""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    current_state = user_states.get(user_id)

    if current_state == STATE_MAIN_MENU:
        await handle_start(update, context)
    elif current_state == STATE_GENERAL_ADVICE:
        await handle_main_menu(update, context)
    elif current_state == STATE_SOLUTION_STRATEGIES:
        await handle_main_menu(update, context)
    elif current_state == STATE_SPECIFIC_ADVICE:
        await handle_main_menu(update, context)
    elif "sheet" in current_state:
        if "advice" in current_state:
            await handle_general_advice(update, context)
        elif "strategies" in current_state:
            await handle_solution_strategies(update, context)
    elif "questions" in current_state:
        if "advice" in current_state:
            sheet_name = current_state.split("_")[-1]
            await handle_general_advice_sheet(update, context)
        elif "strategies" in current_state:
            sheet_name = current_state.split("_")[-1]
            await handle_solution_strategies_sheet(update, context)
    else:
        await handle_start(update, context)
