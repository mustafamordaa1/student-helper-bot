import os
import logging
from telegram import Update
from telegram.ext import CallbackContext

from config import WELCOMING_FOLDER

logger = logging.getLogger(__name__)

async def handle_preference_selection(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    selected_preference = query.data.lower()

    try:
        await send_material(query, context, selected_preference, WELCOMING_FOLDER)
    except Exception as e:
        logger.error(f"Error sending material: {e}")
        await query.message.reply_text(
            "الرجاء انتظار الرسالة او حدث خطأ أثناء إرسال المواد."
        )

async def send_material(
    query: Update, context: CallbackContext, preference: str, folder_path: str
) -> None:
    """Sends the appropriate material based on user preference."""

    if preference == "text":
        await send_text_material(query, folder_path)
    elif preference == "audio":
        await send_audio_material(query, folder_path)
    elif preference == "video":
        await send_video_material(query, folder_path)
    else:
        logger.warning(f"Invalid preference received: {preference}")
        await query.message.reply_text(
            "حدث خطأ، لم يتم التعرف على تفضيلك. يرجى المحاولة لاحقًا."
        )


async def send_text_material(query: Update, folder_path: str) -> None:
    """Sends text material from the specified folder."""
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".txt"):
            with open(
                os.path.join(folder_path, file_name), "r", encoding="utf-8"
            ) as file:
                await query.message.reply_text(file.read())


async def send_audio_material(query: Update, folder_path: str) -> None:
    """Sends audio material from the specified folder."""
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".mp3"):
            await query.message.reply_audio(
                audio=open(os.path.join(folder_path, file_name), "rb")
            )


async def send_video_material(query: Update, folder_path: str) -> None:
    """Sends video material from the specified folder."""
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".mp4"):
            await query.message.reply_video(
                video=open(os.path.join(folder_path, file_name), "rb")
            )