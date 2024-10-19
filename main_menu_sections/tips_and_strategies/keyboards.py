"""
Defines the keyboards used for bot interactions.

This file contains functions that create the various InlineKeyboardMarkup objects used in the bot, such as:
- Start menu keyboard.
- Main menu keyboard.
- General advice sheet selection keyboard.
- General advice question selection keyboard.
- Solution strategies sheet selection keyboard.
- Solution strategies question selection keyboard.
- Format selection keyboard.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
def _create_keyboard(buttons, back_callback_data=None):
    """Helper function to create a keyboard with an optional back button."""
    keyboard = [
        [InlineKeyboardButton(f"{text} {emoji}", callback_data=callback_data)]  # Add emoji here
        for text, callback_data, emoji in buttons  # Modify to include emoji
    ]
    if back_callback_data:
        keyboard.append(
            [InlineKeyboardButton("الرجوع للخلف 🔙", callback_data=back_callback_data)]  # Added back arrow
        )
    return InlineKeyboardMarkup(keyboard)

async def get_tips_and_strategies_keyboard():
    """Returns the keyboard for the main menu."""
    buttons = [
        ("نصائح عامة", "handle_general_tips", "💡"),
        ("استراتيجيات الحل", "handle_solving_strategies", "🧠"),
        ("طلب نصائح خاصة", "handle_request_specific_tips", "🙋‍♂️"),
    ]
    return _create_keyboard(buttons, back_callback_data="go_back")


def get_general_advice_keyboard(general_advice_model):
    """Returns the keyboard for general advice sheet selection."""
    buttons = [
        (sheet_name, f"sheet_name_{sheet_name}", "📄")
        for sheet_name in general_advice_model.get_sheet_names()
    ]
    return _create_keyboard(buttons, back_callback_data="tips_and_strategies")


def get_general_advice_questions_keyboard(questions, sheet_name):
    """Returns the keyboard for general advice question selection."""
    buttons = [
        (question, f"ga_q_{i}_{sheet_name}", "❓") for i, question in enumerate(questions)
    ]
    return _create_keyboard(buttons, back_callback_data="handle_general_tips")


def get_solution_strategies_keyboard(solution_strategies_model):
    """Returns the keyboard for solution strategies sheet selection."""
    buttons = [
        (sheet_name, f"ss_sheet_{sheet_name}", "📝")
        for sheet_name in solution_strategies_model.get_sheet_names()
    ]
    return _create_keyboard(buttons, back_callback_data="tips_and_strategies")


def get_solution_strategies_questions_keyboard(questions, sheet_name):
    """Returns the keyboard for solution strategies question selection."""
    buttons = [
        (question, f"ss_q_{i}_{sheet_name}", "❓") for i, question in enumerate(questions)
    ]
    return _create_keyboard(buttons, back_callback_data="handle_solving_strategies")


def get_format_selection_keyboard():
    """Returns the keyboard for format selection."""
    buttons = [
        ("فيديو", "format_video", "🎥"),
        ("صوت", "format_audio", "🎤"),
        ("نص", "format_text", "📝"),
        ("ملف PDF", "format_pdf", "📄"),
    ]
    return _create_keyboard(buttons, back_callback_data="tips_and_strategies")