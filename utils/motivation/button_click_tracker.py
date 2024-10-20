import os
import random
from openpyxl import load_workbook
from telegram import Update
from telegram.ext import CallbackContext
from utils.database import get_data

# Constants for paths and message frequency
MOTIVATIONAL_MESSAGES_PATH = os.path.dirname(os.path.abspath(__file__))
MALE_MAIN_MENU_MESSAGES_FILE = "main_menu/Male Sructure.xlsx"
FEMALE_MAIN_MENUMESSAGES_FILE = "main_menu/Female Sructure.xlsx"

MALE_GO_BACK__MESSAGES_FILE = "go_back/Male Sructure.xlsx"
FEMALE_GO_BACK_MESSAGES_FILE = "go_back/Female Sructure.xlsx"
MESSAGES_TRIGGER_THRESHOLD = 2

# Global dictionary to store messages (loaded on bot startup)
motivational_messages = {
    "main_menu": {"male": [], "female": []},
    "go_back": {"male": [], "female": []},
}


def load_motivational_messages():
    """Loads motivational messages from Excel files into the global dictionary."""

    def load_messages_from_file(filepath):
        messages = []
        workbook = load_workbook(filepath)
        sheet = workbook.active
        for row in sheet.iter_rows(values_only=True):  # Header row
            messages.append(row[0])  # Messages are in the first column
        return messages

    male_main_filepath = os.path.join(
        MOTIVATIONAL_MESSAGES_PATH, MALE_MAIN_MENU_MESSAGES_FILE
    )
    female_main_filepath = os.path.join(
        MOTIVATIONAL_MESSAGES_PATH, FEMALE_MAIN_MENUMESSAGES_FILE
    )

    male_back_filepath = os.path.join(
        MOTIVATIONAL_MESSAGES_PATH, MALE_GO_BACK__MESSAGES_FILE
    )
    female_back_filepath = os.path.join(
        MOTIVATIONAL_MESSAGES_PATH, FEMALE_GO_BACK_MESSAGES_FILE
    )

    motivational_messages["main_menu"]["male"] = load_messages_from_file(
        male_main_filepath
    )
    motivational_messages["main_menu"]["female"] = load_messages_from_file(
        female_main_filepath
    )

    motivational_messages["go_back"]["male"] = load_messages_from_file(
        male_back_filepath
    )
    motivational_messages["go_back"]["female"] = load_messages_from_file(
        female_back_filepath
    )


def get_random_motivational_message(gender: str, called_from):
    """Returns a random motivational message based on gender."""
    if gender.lower() == "male":
        return random.choice(motivational_messages[called_from]["male"])
    elif gender.lower() == "female":
        return random.choice(motivational_messages[called_from]["female"])
    else:
        return None


async def send_motivational_message(
    update: Update, context: CallbackContext, called_from
):
    """Sends a motivational message to the user and resets the click counter."""
    # user_id = update.effective_user.id

    if isinstance(update, Update):
        user = update.effective_user
    else:  # Assuming it's a CallbackQuery
        user = update.from_user
    user_id = user.id
    user_data = context.user_data

    gender = get_data("SELECT gender FROM users WHERE telegram_id = ?", (user_id,))[0][
        0
    ]

    message = get_random_motivational_message(gender, called_from)
    if message:
        username = user.username
        message = message.replace("(اسم المستخدم)", username)
        if isinstance(update, Update):
            await update.message.reply_text(message)
        else:
            await update.message.reply_text(message)
    user_data["button_clicks"] = 0


async def track_button_clicks(update: Update, context: CallbackContext, called_from):
    """Tracks button clicks and sends a motivational message when the threshold is reached."""
    user_data = context.user_data

    if "button_clicks" not in user_data:
        user_data["button_clicks"] = 0

    user_data["button_clicks"] += 1

    if user_data["button_clicks"] >= MESSAGES_TRIGGER_THRESHOLD:
        await send_motivational_message(update, context, called_from)
